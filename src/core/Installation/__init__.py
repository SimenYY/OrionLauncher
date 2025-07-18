"""
安装调度模块

本模块提供了一个兼容 InstallationCallbackGroup 的 Model 层安装调度工具，
实现了与 minecraft_launcher_lib 的解耦，支持多种安装任务的调度和管理。

主要组件：
- InstallationScheduler: 核心调度器，负责任务调度和状态管理
- InstallationAdapter: 适配器接口，实现与底层库的解耦
- InstallationTask: 安装任务抽象类和具体实现
- CallbackConverter: 回调转换器，处理不同回调接口的转换
"""

from .scheduler import InstallationScheduler
from .adapter import InstallationAdapter, VanillaInstallationAdapter, ForgeInstallationAdapter, FabricInstallationAdapter, QuiltInstallationAdapter
from .tasks import InstallationTask, GameInstallationTask, ModLoaderInstallationTask, AssetVerificationTask
from .callback_converter import CallbackConverter

__all__ = [
    "InstallationScheduler",
    "InstallationAdapter",
    "VanillaInstallationAdapter", 
    "ForgeInstallationAdapter",
    "FabricInstallationAdapter",
    "QuiltInstallationAdapter",
    "InstallationTask",
    "GameInstallationTask",
    "ModLoaderInstallationTask", 
    "AssetVerificationTask",
    "CallbackConverter"
] 