"""
安装调度器模块

本模块实现了安装调度器的核心逻辑，负责管理安装任务的队列、调度和执行。
调度器兼容 InstallationCallbackGroup 接口，提供统一的回调管理。

主要功能：
- 任务队列管理
- 任务依赖解析
- 任务调度和执行
- 状态跟踪和进度报告
- 错误处理和重试机制
"""

import asyncio
import logging
import threading
from typing import Dict, List, Optional, Set, Callable, Any, Union
from pathlib import Path
from enum import Enum
from queue import PriorityQueue, Empty
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future

from .tasks import InstallationTask, TaskStatus, TaskPriority, CompositeInstallationTask
from .callback_converter import CallbackConverter, MultiTaskCallbackConverter
from .adapter import InstallationAdapter
from src.utils.callbacks import InstallationCallbackGroup

logger = logging.getLogger(__name__)


class SchedulerStatus(Enum):
    """调度器状态枚举。

    定义了调度器可能的运行状态。
    """
    IDLE = "idle"               # 空闲状态，没有任务在执行
    RUNNING = "running"         # 运行中，正在执行任务
    PAUSED = "paused"           # 暂停状态，暂时停止调度新任务
    STOPPING = "stopping"      # 停止中，正在停止调度器
    STOPPED = "stopped"         # 已停止，调度器完全停止
    ERROR = "error"             # 错误状态，调度器遇到错误


@dataclass
class TaskExecutionResult:
    """任务执行结果数据类。

    包含任务执行的详细结果信息。

    Attributes:
        task_id (str): 任务 ID。
        success (bool): 执行是否成功。
        error_message (Optional[str]): 错误消息，仅在失败时设置。
        result (Optional[Any]): 任务执行结果。
        execution_time (float): 执行耗时（秒）。
    """
    task_id: str
    success: bool
    error_message: Optional[str] = None
    result: Optional[Any] = None
    execution_time: float = 0.0


@dataclass
class SchedulerConfig:
    """调度器配置数据类。

    包含调度器的各种配置参数。

    Attributes:
        max_concurrent_tasks (int): 最大并发任务数，默认为 3。
        max_retries (int): 任务失败时的最大重试次数，默认为 3。
        retry_delay (float): 重试延迟时间（秒），默认为 5.0。
        task_timeout (float): 任务超时时间（秒），默认为 3600.0（1小时）。
        enable_dependency_check (bool): 是否启用依赖检查，默认为 True。
        enable_task_validation (bool): 是否启用任务验证，默认为 True。
    """
    max_concurrent_tasks: int = 3
    max_retries: int = 3
    retry_delay: float = 5.0
    task_timeout: float = 3600.0  # 1小时
    enable_dependency_check: bool = True
    enable_task_validation: bool = True


class InstallationScheduler:
    """安装调度器。

    负责管理和调度安装任务，兼容 InstallationCallbackGroup 接口。
    支持任务队列、依赖解析、并发执行和状态管理。

    调度器采用生产者-消费者模式，使用优先级队列管理任务，
    支持任务依赖检查、失败重试和并发控制。

    Attributes:
        callback_group (InstallationCallbackGroup): 回调组实例。
        config (SchedulerConfig): 调度器配置。
        status (SchedulerStatus): 当前调度器状态。
        logger (logging.Logger): 日志记录器实例。
    """

    def __init__(self,
                 callback_group: InstallationCallbackGroup,
                 config: Optional[SchedulerConfig] = None) -> None:
        """初始化安装调度器。

        Args:
            callback_group: 回调组实例，用于处理安装过程中的回调。
            config: 调度器配置，如果为 None 则使用默认配置。
        """
        self.callback_group = callback_group
        self.config = config or SchedulerConfig()

        # 调度器状态
        self.status = SchedulerStatus.IDLE
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # 任务管理
        self._tasks: Dict[str, InstallationTask] = {}
        self._task_queue: PriorityQueue = PriorityQueue()
        self._running_tasks: Dict[str, Future] = {}
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Set[str] = set()
        self._retry_counts: Dict[str, int] = {}

        # 线程池
        self._executor: Optional[ThreadPoolExecutor] = None
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # 回调转换器
        self._callback_converter: Optional[CallbackConverter] = None

        # 统计信息
        self._total_tasks = 0
        self._completed_count = 0
        self._failed_count = 0
        self._start_time: Optional[float] = None

        # 锁
        self._lock = threading.RLock()
    
    def add_task(self, task: InstallationTask) -> None:
        """
        添加任务到调度器
        
        Args:
            task: 安装任务实例
        """
        with self._lock:
            if task.task_id in self._tasks:
                self.logger.warning(f"任务 {task.task_id} 已存在，将被替换")
            
            self._tasks[task.task_id] = task
            self._retry_counts[task.task_id] = 0
            self._total_tasks += 1
            
            # 添加到优先级队列
            priority = -task.priority.value  # 负数使优先级高的任务先执行
            self._task_queue.put((priority, task.task_id))
            
            self.logger.info(f"添加任务: {task.task_id} ({task.name})")
    
    def add_tasks(self, tasks: List[InstallationTask]) -> None:
        """
        批量添加任务
        
        Args:
            tasks: 任务列表
        """
        for task in tasks:
            self.add_task(task)
    
    def remove_task(self, task_id: str) -> bool:
        """
        移除任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功移除
        """
        with self._lock:
            if task_id not in self._tasks:
                self.logger.warning(f"任务 {task_id} 不存在")
                return False
            
            # 检查任务是否正在运行
            if task_id in self._running_tasks:
                self.logger.warning(f"任务 {task_id} 正在运行，无法移除")
                return False
            
            del self._tasks[task_id]
            if task_id in self._retry_counts:
                del self._retry_counts[task_id]
            
            self._total_tasks -= 1
            self.logger.info(f"移除任务: {task_id}")
            return True
    
    def get_task(self, task_id: str) -> Optional[InstallationTask]:
        """
        获取任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务实例或 None
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[InstallationTask]:
        """
        获取所有任务
        
        Returns:
            任务列表
        """
        with self._lock:
            return list(self._tasks.values())
    
    def get_pending_tasks(self) -> List[InstallationTask]:
        """
        获取待执行任务
        
        Returns:
            待执行任务列表
        """
        with self._lock:
            return [task for task in self._tasks.values() if task.status == TaskStatus.PENDING]
    
    def get_running_tasks(self) -> List[InstallationTask]:
        """
        获取正在运行的任务
        
        Returns:
            正在运行的任务列表
        """
        with self._lock:
            return [task for task in self._tasks.values() if task.status == TaskStatus.RUNNING]
    
    def get_completed_tasks(self) -> List[InstallationTask]:
        """
        获取已完成任务
        
        Returns:
            已完成任务列表
        """
        with self._lock:
            return [task for task in self._tasks.values() if task.status == TaskStatus.COMPLETED]
    
    def get_failed_tasks(self) -> List[InstallationTask]:
        """
        获取失败任务
        
        Returns:
            失败任务列表
        """
        with self._lock:
            return [task for task in self._tasks.values() if task.status == TaskStatus.FAILED]
    
    def start(self) -> None:
        """
        启动调度器
        """
        with self._lock:
            if self.status == SchedulerStatus.RUNNING:
                self.logger.warning("调度器已在运行中")
                return
            
            self.logger.info("启动安装调度器")
            self.status = SchedulerStatus.RUNNING
            import time
            self._start_time = time.time()
            
            # 创建线程池
            self._executor = ThreadPoolExecutor(
                max_workers=self.config.max_concurrent_tasks,
                thread_name_prefix="InstallationScheduler"
            )
            
            # 创建回调转换器
            self._callback_converter = MultiTaskCallbackConverter(self.callback_group)
            
            # 启动调度器线程
            self._stop_event.clear()
            self._scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                name="InstallationScheduler-Main",
                daemon=True
            )
            self._scheduler_thread.start()
            
            self.logger.info("安装调度器启动完成")
    
    def stop(self, wait: bool = True) -> None:
        """
        停止调度器
        
        Args:
            wait: 是否等待所有任务完成
        """
        with self._lock:
            if self.status == SchedulerStatus.STOPPED:
                self.logger.warning("调度器已停止")
                return
            
            self.logger.info("停止安装调度器")
            self.status = SchedulerStatus.STOPPING
            
            # 设置停止事件
            self._stop_event.set()
            
            # 等待正在运行的任务完成
            if wait and self._running_tasks:
                self.logger.info(f"等待 {len(self._running_tasks)} 个任务完成...")
                for future in self._running_tasks.values():
                    try:
                        future.result(timeout=10.0)  # 最多等待10秒
                    except Exception as e:
                        self.logger.error(f"等待任务完成时发生错误: {e}")
            
            # 关闭线程池
            if self._executor:
                self._executor.shutdown(wait=wait)
                self._executor = None
            
            # 等待调度器线程结束
            if self._scheduler_thread and self._scheduler_thread.is_alive():
                self._scheduler_thread.join(timeout=5.0)
                self._scheduler_thread = None
            
            self.status = SchedulerStatus.STOPPED
            self.logger.info("安装调度器已停止")
    
    def pause(self) -> None:
        """
        暂停调度器
        """
        with self._lock:
            if self.status == SchedulerStatus.RUNNING:
                self.status = SchedulerStatus.PAUSED
                self.logger.info("调度器已暂停")
    
    def resume(self) -> None:
        """
        恢复调度器
        """
        with self._lock:
            if self.status == SchedulerStatus.PAUSED:
                self.status = SchedulerStatus.RUNNING
                self.logger.info("调度器已恢复")
    
    def get_progress(self) -> Dict[str, Any]:
        """
        获取调度器进度信息
        
        Returns:
            进度信息字典
        """
        with self._lock:
            if self._total_tasks == 0:
                progress_percentage = 0
            else:
                progress_percentage = int((self._completed_count / self._total_tasks) * 100)
            
            return {
                "status": self.status.value,
                "total_tasks": self._total_tasks,
                "completed_tasks": self._completed_count,
                "failed_tasks": self._failed_count,
                "running_tasks": len(self._running_tasks),
                "pending_tasks": len(self.get_pending_tasks()),
                "progress_percentage": progress_percentage,
                "start_time": self._start_time,
            }
    
    def _scheduler_loop(self) -> None:
        """
        调度器主循环
        """
        self.logger.info("调度器主循环开始")
        
        try:
            while not self._stop_event.is_set():
                # 检查调度器状态
                if self.status == SchedulerStatus.PAUSED:
                    self._stop_event.wait(1.0)
                    continue
                
                # 尝试获取下一个任务
                try:
                    priority, task_id = self._task_queue.get(timeout=1.0)
                except Empty:
                    # 检查是否所有任务都完成
                    if self._is_all_tasks_finished():
                        self.logger.info("所有任务已完成，调度器退出")
                        break
                    continue
                
                # 获取任务
                task = self._tasks.get(task_id)
                if not task:
                    self.logger.warning(f"任务 {task_id} 不存在")
                    continue
                
                # 检查任务状态
                if task.status != TaskStatus.PENDING:
                    continue
                
                # 检查依赖
                if self.config.enable_dependency_check and not self._check_dependencies(task):
                    # 重新加入队列
                    self._task_queue.put((priority, task_id))
                    self._stop_event.wait(1.0)
                    continue
                
                # 检查并发限制
                if len(self._running_tasks) >= self.config.max_concurrent_tasks:
                    # 重新加入队列
                    self._task_queue.put((priority, task_id))
                    self._stop_event.wait(1.0)
                    continue
                
                # 执行任务
                self._execute_task(task)
                
        except Exception as e:
            self.logger.error(f"调度器主循环发生错误: {e}")
            self.status = SchedulerStatus.ERROR
        finally:
            self.logger.info("调度器主循环结束")
    
    def _execute_task(self, task: InstallationTask) -> None:
        """
        执行任务
        
        Args:
            task: 要执行的任务
        """
        self.logger.info(f"开始执行任务: {task.task_id}")
        
        # 任务验证
        if self.config.enable_task_validation:
            try:
                if not task.validate():
                    self.logger.warning(f"任务验证失败: {task.task_id}")
                    self._handle_task_failure(task, "任务验证失败")
                    return
            except Exception as e:
                self.logger.error(f"任务验证时发生错误: {e}")
                self._handle_task_failure(task, f"任务验证错误: {e}")
                return
        
        # 提交任务到线程池
        future = self._executor.submit(self._run_task, task)
        self._running_tasks[task.task_id] = future
        
        # 添加完成回调
        future.add_done_callback(lambda f: self._on_task_completed(task.task_id, f))
    
    def _run_task(self, task: InstallationTask) -> TaskExecutionResult:
        """
        运行任务
        
        Args:
            task: 要运行的任务
            
        Returns:
            任务执行结果
        """
        import time
        start_time = time.time()
        
        try:
            # 设置任务状态
            task.set_status(TaskStatus.RUNNING)
            
            # 执行任务
            success = task.execute(self._callback_converter)
            
            execution_time = time.time() - start_time
            
            return TaskExecutionResult(
                task_id=task.task_id,
                success=success,
                result=task.result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"任务 {task.task_id} 执行时发生异常: {e}")
            
            return TaskExecutionResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _on_task_completed(self, task_id: str, future: Future) -> None:
        """
        任务完成回调
        
        Args:
            task_id: 任务 ID
            future: 任务 Future 对象
        """
        with self._lock:
            # 从运行任务列表中移除
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
            
            task = self._tasks.get(task_id)
            if not task:
                return
            
            try:
                result = future.result()
                
                if result.success:
                    self._handle_task_success(task, result)
                else:
                    self._handle_task_failure(task, result.error_message)
                    
            except Exception as e:
                self.logger.error(f"获取任务 {task_id} 结果时发生错误: {e}")
                self._handle_task_failure(task, str(e))
    
    def _handle_task_success(self, task: InstallationTask, result: TaskExecutionResult) -> None:
        """
        处理任务成功
        
        Args:
            task: 任务实例
            result: 执行结果
        """
        task.set_status(TaskStatus.COMPLETED)
        self._completed_tasks.add(task.task_id)
        self._completed_count += 1
        
        self.logger.info(f"任务 {task.task_id} 执行成功，耗时: {result.execution_time:.2f}s")
        
        # 检查是否所有任务都完成
        if self._is_all_tasks_finished():
            self.logger.info("所有任务已完成")
            self.callback_group.download.finished()
    
    def _handle_task_failure(self, task: InstallationTask, error_message: Optional[str] = None) -> None:
        """
        处理任务失败
        
        Args:
            task: 任务实例
            error_message: 错误消息
        """
        retry_count = self._retry_counts.get(task.task_id, 0)
        
        if retry_count < self.config.max_retries:
            # 重试任务
            self._retry_counts[task.task_id] = retry_count + 1
            task.set_status(TaskStatus.PENDING)
            
            self.logger.warning(f"任务 {task.task_id} 失败，准备重试 ({retry_count + 1}/{self.config.max_retries})")
            
            # 延迟后重新加入队列
            import time
            time.sleep(self.config.retry_delay)
            
            priority = -task.priority.value
            self._task_queue.put((priority, task.task_id))
        else:
            # 标记为失败
            task.set_status(TaskStatus.FAILED, error_message)
            self._failed_tasks.add(task.task_id)
            self._failed_count += 1
            
            self.logger.error(f"任务 {task.task_id} 最终失败: {error_message}")
            
            # 通知回调
            if error_message:
                error = Exception(error_message)
                self.callback_group.download.error(error)
    
    def _check_dependencies(self, task: InstallationTask) -> bool:
        """
        检查任务依赖
        
        Args:
            task: 任务实例
            
        Returns:
            依赖是否满足
        """
        return task.can_execute(list(self._completed_tasks))
    
    def _is_all_tasks_finished(self) -> bool:
        """
        检查是否所有任务都已完成
        
        Returns:
            是否所有任务都已完成
        """
        with self._lock:
            # 检查是否还有待执行或正在运行的任务
            for task in self._tasks.values():
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    return False
            
            # 检查队列是否为空
            return self._task_queue.empty() and len(self._running_tasks) == 0
    
    def clear(self) -> None:
        """
        清空调度器
        """
        with self._lock:
            if self.status == SchedulerStatus.RUNNING:
                self.logger.warning("调度器正在运行，无法清空")
                return
            
            self._tasks.clear()
            self._completed_tasks.clear()
            self._failed_tasks.clear()
            self._retry_counts.clear()
            self._running_tasks.clear()
            
            # 清空队列
            while not self._task_queue.empty():
                try:
                    self._task_queue.get_nowait()
                except Empty:
                    break
            
            # 重置统计信息
            self._total_tasks = 0
            self._completed_count = 0
            self._failed_count = 0
            self._start_time = None
            
            self.logger.info("调度器已清空")
    
    def __enter__(self):
        """
        上下文管理器入口
        """
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        """
        self.stop(wait=True) 