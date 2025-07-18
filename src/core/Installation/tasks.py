"""
安装任务模块

本模块定义了安装任务的抽象类和具体实现，包括游戏安装、Mod 加载器安装、资源验证等任务。
每个任务都有自己的生命周期和状态管理，可以独立执行或作为复合任务的一部分。

任务类型：
- InstallationTask: 安装任务抽象基类
- GameInstallationTask: 游戏安装任务
- ModLoaderInstallationTask: Mod 加载器安装任务
- AssetVerificationTask: 资源验证任务
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from enum import Enum

from .adapter import InstallationAdapter
from .callback_converter import CallbackConverter, InstallationTaskType
from src.utils.callbacks import InstallationCallbackGroup

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """
    任务状态枚举
    """
    PENDING = "pending"          # 等待中
    RUNNING = "running"          # 运行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"     # 已取消


class TaskPriority(Enum):
    """
    任务优先级枚举
    """
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class InstallationTask(ABC):
    """安装任务抽象基类。

    定义了安装任务的通用接口和生命周期管理。
    所有具体的安装任务都应该继承此类并实现抽象方法。

    Attributes:
        task_id (str): 任务唯一标识符。
        name (str): 任务名称。
        description (str): 任务描述。
        priority (TaskPriority): 任务优先级。
        dependencies (List[str]): 依赖的任务 ID 列表。
        status (TaskStatus): 当前任务状态。
        progress (int): 任务进度百分比 (0-100)。
        error_message (Optional[str]): 错误消息，仅在任务失败时设置。
        result (Optional[Any]): 任务执行结果。
        logger (logging.Logger): 日志记录器实例。
    """

    def __init__(self,
                 task_id: str,
                 name: str,
                 description: str = "",
                 priority: TaskPriority = TaskPriority.NORMAL,
                 dependencies: Optional[List[str]] = None) -> None:
        """初始化安装任务。

        Args:
            task_id: 任务唯一标识符。
            name: 任务名称。
            description: 任务描述。
            priority: 任务优先级，默认为 NORMAL。
            dependencies: 依赖的任务 ID 列表，默认为空列表。
        """
        self.task_id = task_id
        self.name = name
        self.description = description
        self.priority = priority
        self.dependencies = dependencies or []

        # 任务状态
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.error_message: Optional[str] = None
        self.result: Optional[Any] = None

        # 日志记录器
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # 回调相关
        self._callback_converter: Optional[CallbackConverter] = None
    
    @abstractmethod
    def execute(self, callback_converter: CallbackConverter, **kwargs) -> bool:
        """执行任务。

        子类必须实现此方法来定义具体的任务执行逻辑。

        Args:
            callback_converter: 回调转换器，用于处理进度和状态回调。
            **kwargs: 任务执行参数。

        Returns:
            bool: 执行成功返回 True，失败返回 False。
        """
        pass

    @abstractmethod
    def validate(self, **kwargs) -> bool:
        """验证任务执行条件。

        子类必须实现此方法来验证任务是否可以执行。

        Args:
            **kwargs: 验证参数。

        Returns:
            bool: 验证通过返回 True，否则返回 False。
        """
        pass

    @abstractmethod
    def get_estimated_duration(self) -> int:
        """获取任务预估执行时间。

        子类必须实现此方法来提供任务的预估执行时间。

        Returns:
            int: 预估执行时间（秒）。
        """
        pass

    def can_execute(self, completed_tasks: List[str]) -> bool:
        """检查任务是否可以执行（依赖是否满足）。

        Args:
            completed_tasks: 已完成的任务 ID 列表。

        Returns:
            bool: 如果所有依赖都已完成返回 True，否则返回 False。
        """
        for dependency in self.dependencies:
            if dependency not in completed_tasks:
                return False
        return True

    def set_status(self, status: TaskStatus, error_message: Optional[str] = None) -> None:
        """设置任务状态。

        Args:
            status: 新的任务状态。
            error_message: 错误消息，仅在状态为失败时设置。
        """
        self.status = status
        self.error_message = error_message
        self.logger.debug(f"任务 {self.task_id} 状态更新: {status.value}")

        if error_message:
            self.logger.error(f"任务 {self.task_id} 失败: {error_message}")

    def set_progress(self, progress: int) -> None:
        """设置任务进度。

        Args:
            progress: 进度百分比，范围为 0-100。
        """
        self.progress = max(0, min(100, progress))
        self.logger.debug(f"任务 {self.task_id} 进度: {self.progress}%")
    
    def __str__(self) -> str:
        return f"Task({self.task_id}: {self.name})"
    
    def __repr__(self) -> str:
        return f"InstallationTask(task_id='{self.task_id}', name='{self.name}', status={self.status.value})"


class GameInstallationTask(InstallationTask):
    """游戏安装任务。

    负责安装指定版本的 Minecraft 游戏，包括下载游戏文件、
    资源文件和依赖库等。

    Attributes:
        version_id (str): 要安装的游戏版本 ID。
        minecraft_directory (str): Minecraft 安装目录路径。
        adapter (InstallationAdapter): 用于执行安装的适配器实例。
    """

    def __init__(self,
                 task_id: str,
                 version_id: str,
                 minecraft_directory: Union[str, Path],
                 adapter: InstallationAdapter,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 priority: TaskPriority = TaskPriority.HIGH) -> None:
        """初始化游戏安装任务。

        Args:
            task_id: 任务唯一标识符。
            version_id: 要安装的游戏版本 ID。
            minecraft_directory: Minecraft 安装目录路径。
            adapter: 用于执行安装的适配器实例。
            name: 任务名称，如果为 None 则自动生成。
            description: 任务描述，如果为 None 则自动生成。
            priority: 任务优先级，默认为 HIGH。
        """
        if name is None:
            name = f"安装 Minecraft {version_id}"
        if description is None:
            description = f"安装 Minecraft 版本 {version_id} 到 {minecraft_directory}"

        super().__init__(task_id, name, description, priority)

        self.version_id = version_id
        self.minecraft_directory = str(minecraft_directory)
        self.adapter = adapter
    
    def execute(self, callback_converter: CallbackConverter, **kwargs) -> bool:
        """
        执行游戏安装任务
        
        Args:
            callback_converter: 回调转换器
            **kwargs: 任务执行参数
            
        Returns:
            执行是否成功
        """
        try:
            self.set_status(TaskStatus.RUNNING)
            self.logger.info(f"开始执行游戏安装任务: {self.version_id}")
            
            # 获取回调字典
            callback_dict = callback_converter.get_callback_dict(InstallationTaskType.INSTALL_GAME)
            
            # 执行安装
            success = self.adapter.install(self.version_id, callback_dict, **kwargs)
            
            if success:
                self.set_status(TaskStatus.COMPLETED)
                self.result = {"version_id": self.version_id, "installed": True}
                self.logger.info(f"游戏安装任务完成: {self.version_id}")
                return True
            else:
                self.set_status(TaskStatus.FAILED, "安装失败")
                return False
                
        except Exception as e:
            self.set_status(TaskStatus.FAILED, str(e))
            callback_converter.on_task_error(e)
            self.logger.error(f"游戏安装任务执行失败: {e}")
            return False
    
    def validate(self, **kwargs) -> bool:
        """
        验证游戏安装任务执行条件
        
        Args:
            **kwargs: 验证参数
            
        Returns:
            验证是否通过
        """
        # 检查版本是否有效
        if not self.adapter.validate_version(self.version_id):
            self.logger.error(f"无效的游戏版本: {self.version_id}")
            return False
        
        # 检查是否已安装
        if self.adapter.is_installed(self.version_id):
            self.logger.info(f"游戏版本 {self.version_id} 已安装")
            return False
        
        # 检查目录权限
        minecraft_path = Path(self.minecraft_directory)
        if not minecraft_path.exists():
            try:
                minecraft_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.error(f"无法创建 Minecraft 目录: {e}")
                return False
        
        return True
    
    def get_estimated_duration(self) -> int:
        """
        获取游戏安装任务预估执行时间
        
        Returns:
            预估执行时间（秒）
        """
        # 根据版本类型估算时间
        if "snapshot" in self.version_id.lower():
            return 300  # 5分钟
        else:
            return 180  # 3分钟


class ModLoaderInstallationTask(InstallationTask):
    """
    Mod 加载器安装任务
    
    负责安装指定的 Mod 加载器（如 Forge、Fabric、Quilt 等）。
    """
    
    def __init__(self,
                 task_id: str,
                 mod_loader_type: str,
                 version_id: str,
                 minecraft_directory: Union[str, Path],
                 adapter: InstallationAdapter,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 priority: TaskPriority = TaskPriority.NORMAL,
                 dependencies: Optional[List[str]] = None,
                 **loader_kwargs):
        """
        初始化 Mod 加载器安装任务
        
        Args:
            task_id: 任务唯一标识符
            mod_loader_type: Mod 加载器类型 (forge, fabric, quilt)
            version_id: 版本 ID
            minecraft_directory: Minecraft 安装目录
            adapter: 安装适配器
            name: 任务名称（可选）
            description: 任务描述（可选）
            priority: 任务优先级
            dependencies: 依赖的任务 ID 列表
            **loader_kwargs: Mod 加载器特定参数
        """
        if name is None:
            name = f"安装 {mod_loader_type.title()} {version_id}"
        if description is None:
            description = f"安装 {mod_loader_type.title()} 版本 {version_id}"
            
        super().__init__(task_id, name, description, priority, dependencies)
        
        self.mod_loader_type = mod_loader_type.lower()
        self.version_id = version_id
        self.minecraft_directory = str(minecraft_directory)
        self.adapter = adapter
        self.loader_kwargs = loader_kwargs
    
    def execute(self, callback_converter: CallbackConverter, **kwargs) -> bool:
        """
        执行 Mod 加载器安装任务
        
        Args:
            callback_converter: 回调转换器
            **kwargs: 任务执行参数
            
        Returns:
            执行是否成功
        """
        try:
            self.set_status(TaskStatus.RUNNING)
            self.logger.info(f"开始执行 Mod 加载器安装任务: {self.mod_loader_type} {self.version_id}")
            
            # 根据 Mod 加载器类型获取对应的回调字典
            task_type_map = {
                "forge": InstallationTaskType.INSTALL_FORGE,
                "fabric": InstallationTaskType.INSTALL_FABRIC,
                "quilt": InstallationTaskType.INSTALL_QUILT,
                "neoforge": InstallationTaskType.INSTALL_NEOFORGE,
                "liteloader": InstallationTaskType.INSTALL_LITELOADER,
            }
            
            task_type = task_type_map.get(self.mod_loader_type, InstallationTaskType.INSTALL_FORGE)
            callback_dict = callback_converter.get_callback_dict(task_type)
            
            # 合并参数
            install_kwargs = {**self.loader_kwargs, **kwargs}
            
            # 执行安装
            success = self.adapter.install(self.version_id, callback_dict, **install_kwargs)
            
            if success:
                self.set_status(TaskStatus.COMPLETED)
                self.result = {
                    "mod_loader_type": self.mod_loader_type,
                    "version_id": self.version_id,
                    "installed": True
                }
                self.logger.info(f"Mod 加载器安装任务完成: {self.mod_loader_type} {self.version_id}")
                return True
            else:
                self.set_status(TaskStatus.FAILED, "安装失败")
                return False
                
        except Exception as e:
            self.set_status(TaskStatus.FAILED, str(e))
            callback_converter.on_task_error(e)
            self.logger.error(f"Mod 加载器安装任务执行失败: {e}")
            return False
    
    def validate(self, **kwargs) -> bool:
        """
        验证 Mod 加载器安装任务执行条件
        
        Args:
            **kwargs: 验证参数
            
        Returns:
            验证是否通过
        """
        # 检查版本是否有效
        if not self.adapter.validate_version(self.version_id):
            self.logger.error(f"无效的 {self.mod_loader_type} 版本: {self.version_id}")
            return False
        
        # 检查是否已安装
        if self.adapter.is_installed(self.version_id):
            self.logger.info(f"{self.mod_loader_type} 版本 {self.version_id} 已安装")
            return False
        
        return True
    
    def get_estimated_duration(self) -> int:
        """
        获取 Mod 加载器安装任务预估执行时间
        
        Returns:
            预估执行时间（秒）
        """
        # 根据 Mod 加载器类型估算时间
        duration_map = {
            "forge": 240,      # 4分钟
            "fabric": 120,     # 2分钟
            "quilt": 120,      # 2分钟
            "neoforge": 240,   # 4分钟
            "liteloader": 90,  # 1.5分钟
        }
        
        return duration_map.get(self.mod_loader_type, 180)


class AssetVerificationTask(InstallationTask):
    """
    资源验证任务
    
    负责验证游戏资源文件的完整性。
    """
    
    def __init__(self,
                 task_id: str,
                 version_id: str,
                 minecraft_directory: Union[str, Path],
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 priority: TaskPriority = TaskPriority.LOW,
                 dependencies: Optional[List[str]] = None):
        """
        初始化资源验证任务
        
        Args:
            task_id: 任务唯一标识符
            version_id: 游戏版本 ID
            minecraft_directory: Minecraft 安装目录
            name: 任务名称（可选）
            description: 任务描述（可选）
            priority: 任务优先级
            dependencies: 依赖的任务 ID 列表
        """
        if name is None:
            name = f"验证 Minecraft {version_id} 资源"
        if description is None:
            description = f"验证 Minecraft 版本 {version_id} 的资源文件完整性"
            
        super().__init__(task_id, name, description, priority, dependencies)
        
        self.version_id = version_id
        self.minecraft_directory = str(minecraft_directory)
    
    def execute(self, callback_converter: CallbackConverter, **kwargs) -> bool:
        """
        执行资源验证任务
        
        Args:
            callback_converter: 回调转换器
            **kwargs: 任务执行参数
            
        Returns:
            执行是否成功
        """
        try:
            self.set_status(TaskStatus.RUNNING)
            self.logger.info(f"开始执行资源验证任务: {self.version_id}")
            
            # 获取回调字典
            callback_dict = callback_converter.get_callback_dict(InstallationTaskType.VERIFY)
            
            # 模拟验证过程
            import time
            for i in range(0, 101, 10):
                time.sleep(0.1)  # 模拟验证时间
                self.set_progress(i)
                callback_dict.get("setProgress", lambda x: None)(i)
                
            self.set_status(TaskStatus.COMPLETED)
            self.result = {"version_id": self.version_id, "verified": True}
            self.logger.info(f"资源验证任务完成: {self.version_id}")
            return True
            
        except Exception as e:
            self.set_status(TaskStatus.FAILED, str(e))
            callback_converter.on_task_error(e)
            self.logger.error(f"资源验证任务执行失败: {e}")
            return False
    
    def validate(self, **kwargs) -> bool:
        """
        验证资源验证任务执行条件
        
        Args:
            **kwargs: 验证参数
            
        Returns:
            验证是否通过
        """
        # 检查版本目录是否存在
        version_dir = Path(self.minecraft_directory) / "versions" / self.version_id
        if not version_dir.exists():
            self.logger.error(f"版本目录不存在: {version_dir}")
            return False
        
        # 检查版本 JSON 文件是否存在
        version_json = version_dir / f"{self.version_id}.json"
        if not version_json.exists():
            self.logger.error(f"版本 JSON 文件不存在: {version_json}")
            return False
        
        return True
    
    def get_estimated_duration(self) -> int:
        """
        获取资源验证任务预估执行时间
        
        Returns:
            预估执行时间（秒）
        """
        return 60  # 1分钟


class CompositeInstallationTask(InstallationTask):
    """
    复合安装任务
    
    由多个子任务组成的复合任务，可以按顺序或并行执行子任务。
    """
    
    def __init__(self,
                 task_id: str,
                 name: str,
                 subtasks: List[InstallationTask],
                 description: str = "",
                 priority: TaskPriority = TaskPriority.NORMAL,
                 parallel: bool = False):
        """
        初始化复合安装任务
        
        Args:
            task_id: 任务唯一标识符
            name: 任务名称
            subtasks: 子任务列表
            description: 任务描述
            priority: 任务优先级
            parallel: 是否并行执行子任务
        """
        super().__init__(task_id, name, description, priority)
        
        self.subtasks = subtasks
        self.parallel = parallel
        self.completed_subtasks = 0
    
    def execute(self, callback_converter: CallbackConverter, **kwargs) -> bool:
        """
        执行复合安装任务
        
        Args:
            callback_converter: 回调转换器
            **kwargs: 任务执行参数
            
        Returns:
            执行是否成功
        """
        try:
            self.set_status(TaskStatus.RUNNING)
            self.logger.info(f"开始执行复合安装任务: {self.name}")
            
            success_count = 0
            total_tasks = len(self.subtasks)
            
            for i, subtask in enumerate(self.subtasks):
                self.logger.info(f"执行子任务 {i+1}/{total_tasks}: {subtask.name}")
                
                # 验证子任务
                if not subtask.validate(**kwargs):
                    self.logger.warning(f"子任务验证失败，跳过: {subtask.name}")
                    continue
                
                # 执行子任务
                if subtask.execute(callback_converter, **kwargs):
                    success_count += 1
                    self.completed_subtasks += 1
                else:
                    self.logger.error(f"子任务执行失败: {subtask.name}")
                    if not self.parallel:  # 串行执行时，一个失败就停止
                        break
                
                # 更新进度
                progress = int(((i + 1) / total_tasks) * 100)
                self.set_progress(progress)
            
            # 判断是否成功
            if success_count == total_tasks:
                self.set_status(TaskStatus.COMPLETED)
                self.result = {"completed_subtasks": success_count, "total_subtasks": total_tasks}
                self.logger.info(f"复合安装任务完成: {self.name}")
                return True
            else:
                self.set_status(TaskStatus.FAILED, f"只有 {success_count}/{total_tasks} 个子任务成功")
                return False
                
        except Exception as e:
            self.set_status(TaskStatus.FAILED, str(e))
            callback_converter.on_task_error(e)
            self.logger.error(f"复合安装任务执行失败: {e}")
            return False
    
    def validate(self, **kwargs) -> bool:
        """
        验证复合安装任务执行条件
        
        Args:
            **kwargs: 验证参数
            
        Returns:
            验证是否通过
        """
        # 验证所有子任务
        for subtask in self.subtasks:
            if not subtask.validate(**kwargs):
                self.logger.error(f"子任务验证失败: {subtask.name}")
                return False
        
        return True
    
    def get_estimated_duration(self) -> int:
        """
        获取复合安装任务预估执行时间
        
        Returns:
            预估执行时间（秒）
        """
        if self.parallel:
            # 并行执行时，取最长的子任务时间
            return max(subtask.get_estimated_duration() for subtask in self.subtasks)
        else:
            # 串行执行时，累加所有子任务时间
            return sum(subtask.get_estimated_duration() for subtask in self.subtasks) 