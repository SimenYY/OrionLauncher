"""
回调转换器模块

本模块提供了回调转换器，用于将 InstallationCallbackGroup 转换为 minecraft_launcher_lib 
所需的 CallbackDict 格式，实现不同回调接口之间的适配。

主要功能：
- 将 InstallationCallbackGroup 的回调接口转换为 minecraft_launcher_lib 的回调格式
- 支持多种安装任务类型的回调转换
- 提供统一的回调管理和转换机制
"""

import logging
from typing import Dict, Any, Optional, Callable
from enum import Enum

from Utils.callbacks import InstallationCallbackGroup
from Core.minecraft_launcher_lib.types import CallbackDict

logger = logging.getLogger(__name__)


class InstallationTaskType(Enum):
    """安装任务类型枚举。

    定义了支持的各种安装任务类型，用于回调转换器识别不同的任务。
    """
    DOWNLOAD = "download"                       # 下载任务
    INSTALL_GAME = "install_game"               # 游戏安装任务
    INSTALL_FORGE = "install_forge"             # Forge 安装任务
    INSTALL_NEOFORGE = "install_neoforge"       # NeoForge 安装任务
    INSTALL_FABRIC = "install_fabric"           # Fabric 安装任务
    INSTALL_QUILT = "install_quilt"             # Quilt 安装任务
    INSTALL_LITELOADER = "install_liteloader"   # LiteLoader 安装任务
    VERIFY = "verify"                           # 验证任务


class CallbackConverter:
    """回调转换器。

    将 InstallationCallbackGroup 的回调接口转换为 minecraft_launcher_lib
    所需的 CallbackDict 格式，实现不同回调系统之间的适配。

    该转换器负责将底层库的回调事件转换为上层应用可以理解的回调格式，
    支持多种安装任务类型的回调处理。

    Attributes:
        callback_group (InstallationCallbackGroup): 回调组实例。
        logger (logging.Logger): 日志记录器实例。
    """

    def __init__(self, callback_group: InstallationCallbackGroup) -> None:
        """初始化回调转换器。

        Args:
            callback_group: InstallationCallbackGroup 实例，用于处理转换后的回调。
        """
        self.callback_group = callback_group
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # 当前任务状态
        self._current_task_type: Optional[InstallationTaskType] = None
        self._current_max_progress: int = 100
        self._current_progress: int = 0
        
    def get_callback_dict(self, task_type: InstallationTaskType) -> CallbackDict:
        """获取指定任务类型的 CallbackDict。

        根据任务类型创建相应的回调字典，用于与 minecraft_launcher_lib 交互。

        Args:
            task_type: 安装任务类型。

        Returns:
            CallbackDict: 转换后的回调字典，包含 setStatus、setProgress 和 setMax 回调。
        """
        self._current_task_type = task_type

        callback_dict: CallbackDict = {
            "setStatus": self._on_set_status,
            "setProgress": self._on_set_progress,
            "setMax": self._on_set_max,
        }

        return callback_dict
    
    def _on_set_status(self, status: str) -> None:
        """
        处理状态设置回调
        
        Args:
            status: 状态信息
        """
        self.logger.debug(f"任务状态更新: {status}")
        
        if self._current_task_type == InstallationTaskType.DOWNLOAD:
            # 下载任务开始
            self.callback_group.download.start()
        elif self._current_task_type == InstallationTaskType.INSTALL_GAME:
            # 游戏安装任务开始
            self.callback_group.install_game.start()
        elif self._current_task_type == InstallationTaskType.INSTALL_FORGE:
            # Forge 安装任务开始
            self.callback_group.install_forge.start()
        elif self._current_task_type == InstallationTaskType.INSTALL_NEOFORGE:
            # NeoForge 安装任务开始
            self.callback_group.install_neoforge.start()
        elif self._current_task_type == InstallationTaskType.INSTALL_FABRIC:
            # Fabric 安装任务开始
            self.callback_group.install_fabric.start()
        elif self._current_task_type == InstallationTaskType.INSTALL_QUILT:
            # Quilt 安装任务开始
            self.callback_group.install_quilt.start()
        elif self._current_task_type == InstallationTaskType.INSTALL_LITELOADER:
            # LiteLoader 安装任务开始
            self.callback_group.install_liteloader.start()
        elif self._current_task_type == InstallationTaskType.VERIFY:
            # 验证任务开始
            self.callback_group.verify.start()
    
    def _on_set_progress(self, progress: int) -> None:
        """
        处理进度设置回调
        
        Args:
            progress: 当前进度值
        """
        self._current_progress = progress
        
        # 计算百分比进度
        if self._current_max_progress > 0:
            progress_percentage = int((progress / self._current_max_progress) * 100)
        else:
            progress_percentage = 0
            
        self.logger.debug(f"任务进度更新: {progress}/{self._current_max_progress} ({progress_percentage}%)")
        
        if self._current_task_type == InstallationTaskType.DOWNLOAD:
            # 下载进度更新
            self.callback_group.download.progress(progress_percentage)
        elif self._current_task_type == InstallationTaskType.INSTALL_GAME:
            # 游戏安装进度更新 - 暂时不需要特殊处理
            pass
        elif self._current_task_type == InstallationTaskType.INSTALL_FORGE:
            # Forge 安装进度更新 - 暂时不需要特殊处理
            pass
        elif self._current_task_type == InstallationTaskType.INSTALL_NEOFORGE:
            # NeoForge 安装进度更新 - 暂时不需要特殊处理
            pass
        elif self._current_task_type == InstallationTaskType.INSTALL_FABRIC:
            # Fabric 安装进度更新 - 暂时不需要特殊处理
            pass
        elif self._current_task_type == InstallationTaskType.INSTALL_QUILT:
            # Quilt 安装进度更新 - 暂时不需要特殊处理
            pass
        elif self._current_task_type == InstallationTaskType.INSTALL_LITELOADER:
            # LiteLoader 安装进度更新 - 暂时不需要特殊处理
            pass
        elif self._current_task_type == InstallationTaskType.VERIFY:
            # 验证进度更新 - 暂时不需要特殊处理
            pass
            
        # 检查是否完成
        if progress >= self._current_max_progress:
            self._on_task_finished()
    
    def _on_set_max(self, max_value: int) -> None:
        """
        处理最大值设置回调
        
        Args:
            max_value: 最大进度值
        """
        self._current_max_progress = max_value
        self.logger.debug(f"任务最大进度设置: {max_value}")
        
        if self._current_task_type == InstallationTaskType.DOWNLOAD:
            # 下载任务设置大小信息
            self.callback_group.download.size(max_value)
    
    def _on_task_finished(self) -> None:
        """
        处理任务完成回调
        """
        self.logger.debug(f"任务完成: {self._current_task_type}")
        
        if self._current_task_type == InstallationTaskType.DOWNLOAD:
            # 下载任务完成
            self.callback_group.download.finished()
        elif self._current_task_type == InstallationTaskType.INSTALL_GAME:
            # 游戏安装任务完成
            self.callback_group.install_game.finished()
        elif self._current_task_type == InstallationTaskType.INSTALL_FORGE:
            # Forge 安装任务完成
            self.callback_group.install_forge.finished()
        elif self._current_task_type == InstallationTaskType.INSTALL_NEOFORGE:
            # NeoForge 安装任务完成
            self.callback_group.install_neoforge.finished()
        elif self._current_task_type == InstallationTaskType.INSTALL_FABRIC:
            # Fabric 安装任务完成
            self.callback_group.install_fabric.finished()
        elif self._current_task_type == InstallationTaskType.INSTALL_QUILT:
            # Quilt 安装任务完成
            self.callback_group.install_quilt.finished()
        elif self._current_task_type == InstallationTaskType.INSTALL_LITELOADER:
            # LiteLoader 安装任务完成
            self.callback_group.install_liteloader.finished()
        elif self._current_task_type == InstallationTaskType.VERIFY:
            # 验证任务完成
            self.callback_group.verify.finished()
    
    def on_task_error(self, error: Exception) -> None:
        """
        处理任务错误回调
        
        Args:
            error: 发生的错误
        """
        self.logger.error(f"任务错误: {self._current_task_type}, 错误: {error}")
        
        if self._current_task_type == InstallationTaskType.DOWNLOAD:
            # 下载任务错误
            self.callback_group.download.error(error)
        elif self._current_task_type == InstallationTaskType.INSTALL_GAME:
            # 游戏安装任务错误
            self.callback_group.install_game.error(error)
        elif self._current_task_type == InstallationTaskType.INSTALL_FORGE:
            # Forge 安装任务错误
            self.callback_group.install_forge.error(error)
        elif self._current_task_type == InstallationTaskType.INSTALL_NEOFORGE:
            # NeoForge 安装任务错误
            self.callback_group.install_neoforge.error(error)
        elif self._current_task_type == InstallationTaskType.INSTALL_FABRIC:
            # Fabric 安装任务错误
            self.callback_group.install_fabric.error(error)
        elif self._current_task_type == InstallationTaskType.INSTALL_QUILT:
            # Quilt 安装任务错误
            self.callback_group.install_quilt.error(error)
        elif self._current_task_type == InstallationTaskType.INSTALL_LITELOADER:
            # LiteLoader 安装任务错误
            self.callback_group.install_liteloader.error(error)
        elif self._current_task_type == InstallationTaskType.VERIFY:
            # 验证任务错误
            self.callback_group.verify.error(error)
    
    def reset(self) -> None:
        """
        重置转换器状态
        """
        self._current_task_type = None
        self._current_max_progress = 100
        self._current_progress = 0
        self.logger.debug("回调转换器状态已重置")


class MultiTaskCallbackConverter(CallbackConverter):
    """多任务回调转换器。

    支持多个任务的回调转换，可以跟踪多个任务的状态并提供统一的回调接口。
    该转换器能够计算多个任务的总体进度，并在所有任务完成时触发完成回调。

    Attributes:
        _task_states (Dict[InstallationTaskType, Dict[str, Any]]): 任务状态跟踪字典。
        _total_tasks (int): 总任务数。
        _completed_tasks (int): 已完成任务数。
    """

    def __init__(self, callback_group: InstallationCallbackGroup) -> None:
        """初始化多任务回调转换器。

        Args:
            callback_group: InstallationCallbackGroup 实例，用于处理转换后的回调。
        """
        super().__init__(callback_group)

        # 任务状态跟踪
        self._task_states: Dict[InstallationTaskType, Dict[str, Any]] = {}
        self._total_tasks = 0
        self._completed_tasks = 0
    
    def add_task(self, task_type: InstallationTaskType, weight: float = 1.0) -> None:
        """添加任务到多任务转换器。

        Args:
            task_type: 要添加的任务类型。
            weight: 任务权重，用于计算总体进度，默认为 1.0。
        """
        self._task_states[task_type] = {
            "weight": weight,
            "progress": 0,
            "max_progress": 100,
            "completed": False
        }
        self._total_tasks += 1
        self.logger.debug(f"添加任务: {task_type}, 权重: {weight}")
    
    def get_callback_dict(self, task_type: InstallationTaskType) -> CallbackDict:
        """
        获取指定任务类型的 CallbackDict
        
        Args:
            task_type: 安装任务类型
            
        Returns:
            转换后的 CallbackDict
        """
        if task_type not in self._task_states:
            self.add_task(task_type)
            
        self._current_task_type = task_type
        
        callback_dict: CallbackDict = {
            "setStatus": self._on_multi_task_set_status,
            "setProgress": self._on_multi_task_set_progress,
            "setMax": self._on_multi_task_set_max,
        }
        
        return callback_dict
    
    def _on_multi_task_set_status(self, status: str) -> None:
        """
        处理多任务状态设置回调
        
        Args:
            status: 状态信息
        """
        self.logger.debug(f"多任务状态更新: {self._current_task_type} - {status}")
        
        # 调用父类方法处理单个任务的状态
        self._on_set_status(status)
    
    def _on_multi_task_set_progress(self, progress: int) -> None:
        """
        处理多任务进度设置回调
        
        Args:
            progress: 当前进度值
        """
        if self._current_task_type and self._current_task_type in self._task_states:
            task_state = self._task_states[self._current_task_type]
            task_state["progress"] = progress
            
            # 计算总体进度
            total_weighted_progress = 0
            total_weight = 0
            
            for _, state in self._task_states.items():
                if state["max_progress"] > 0:
                    task_progress = (state["progress"] / state["max_progress"]) * 100
                else:
                    task_progress = 0

                total_weighted_progress += task_progress * state["weight"]
                total_weight += state["weight"]
            
            if total_weight > 0:
                overall_progress = int(total_weighted_progress / total_weight)
            else:
                overall_progress = 0
            
            self.logger.debug(f"多任务进度更新: {self._current_task_type} {progress}/{task_state['max_progress']}, 总体进度: {overall_progress}%")
            
            # 更新下载进度
            self.callback_group.download.progress(overall_progress)
            
            # 检查任务是否完成
            if progress >= task_state["max_progress"] and not task_state["completed"]:
                task_state["completed"] = True
                self._completed_tasks += 1
                self.logger.debug(f"任务完成: {self._current_task_type}, 已完成: {self._completed_tasks}/{self._total_tasks}")
                
                # 调用单个任务完成回调
                self._on_task_finished()
                
                # 检查是否所有任务都完成
                if self._completed_tasks >= self._total_tasks:
                    self.logger.debug("所有任务完成")
                    self.callback_group.download.finished()
    
    def _on_multi_task_set_max(self, max_value: int) -> None:
        """
        处理多任务最大值设置回调
        
        Args:
            max_value: 最大进度值
        """
        if self._current_task_type and self._current_task_type in self._task_states:
            self._task_states[self._current_task_type]["max_progress"] = max_value
            self.logger.debug(f"多任务最大进度设置: {self._current_task_type} - {max_value}")
    
    def reset(self) -> None:
        """
        重置多任务转换器状态
        """
        super().reset()
        self._task_states.clear()
        self._total_tasks = 0
        self._completed_tasks = 0
        self.logger.debug("多任务回调转换器状态已重置") 