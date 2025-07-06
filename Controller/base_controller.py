import abc
from typing import Optional, Dict, List, Any, Callable

from PySide6.QtCore import QObject, Signal, Slot, QThread


class BaseController(QObject):
    """
    控制器基类，作为GUI与Core功能模块交互的桥梁
    
    所有控制器应继承此类，并实现相应的抽象方法
    控制器应遵循单线程异步模式，对于IO密集型任务使用信号槽机制
    """
    
    # 通用信号
    error_occurred = Signal(str)  # 错误信号
    task_progress = Signal(str, int)  # 任务进度信号 (任务名, 进度百分比)
    task_completed = Signal(str)  # 任务完成信号 (任务名)
    
    def __init__(self, parent: Optional[QObject] = None):
        """初始化控制器"""
        super().__init__(parent)
        self._threads = {}  # 存储线程对象
        self._workers = {}  # 存储工作对象
    
    def initialize(self) -> bool:
        """
        初始化控制器
        
        Returns:
            bool: 初始化是否成功
        """
        # 子类应该重写此方法
        raise NotImplementedError("子类必须实现initialize方法")
    
    def run_async_task(self, task_name: str, task_func: Callable, *args, **kwargs) -> None:
        """
        在单独的线程中运行异步任务
        
        Args:
            task_name: 任务名称
            task_func: 任务函数
            *args, **kwargs: 传递给任务函数的参数
        """
        # 如果已经有同名任务在运行，先停止它
        if task_name in self._threads and self._threads[task_name].isRunning():
            self._threads[task_name].quit()
            self._threads[task_name].wait()
        
        # 创建工作线程
        thread = QThread()
        # 创建工作对象
        worker = AsyncTaskWorker(task_func, *args, **kwargs)
        # 将工作对象移动到线程
        worker.moveToThread(thread)
        # 连接信号
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.progress.connect(lambda p: self.task_progress.emit(task_name, p))
        worker.error.connect(self.error_occurred.emit)
        worker.result.connect(lambda: self.task_completed.emit(task_name))
        
        # 存储线程和工作对象
        self._threads[task_name] = thread
        self._workers[task_name] = worker
        
        # 启动线程
        thread.start()
    
    def cleanup(self) -> None:
        """清理资源，关闭所有线程"""
        # 停止所有线程
        try:
            for name in list(self._threads.keys()):
                thread = self._threads.get(name)
                if thread and thread.isRunning():
                    thread.quit()
                    thread.wait(1000)  # 等待最多1秒
                
                # 从字典中移除
                self._threads.pop(name, None)
                self._workers.pop(name, None)
        except RuntimeError:
            # 忽略已删除对象的错误
            pass


class AsyncTaskWorker(QObject):
    """异步任务工作器"""
    finished = Signal()
    error = Signal(str)
    progress = Signal(int)
    result = Signal(object)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    @Slot()
    def run(self):
        """执行任务"""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()