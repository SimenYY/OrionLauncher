"""
安装调度器使用示例

本文件展示了如何使用 InstallationScheduler 和相关组件来管理 Minecraft 安装任务。
包括游戏安装、Mod 加载器安装和资源验证等场景。
"""

import logging
import time
from pathlib import Path

from src.utils.callbacks import InstallationCallbackGroup, Callbacks
from .scheduler import InstallationScheduler, SchedulerConfig
from .adapter import VanillaInstallationAdapter, ForgeInstallationAdapter, FabricInstallationAdapter
from .tasks import GameInstallationTask, ModLoaderInstallationTask, AssetVerificationTask, TaskPriority
from .callback_converter import InstallationTaskType

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)


def create_callback_group() -> InstallationCallbackGroup:
    """
    创建回调组实例
    
    Returns:
        配置好的回调组
    """
    
    # 下载回调
    download_callbacks = Callbacks(
        start=lambda: logger.info("🚀 开始下载"),
        progress=lambda p: logger.info(f"📥 下载进度: {p}%"),
        tasks_progress=lambda tp: logger.info(f"📊 任务进度: {tp}"),
        size=lambda s: logger.info(f"📦 总大小: {s} 字节"),
        downloaded_size=lambda ds: logger.info(f"⬇️ 已下载: {ds} 字节"),
        speed=lambda sp: logger.info(f"🚀 下载速度: {sp} 字节/秒"),
        finished=lambda: logger.info("✅ 下载完成"),
        error=lambda e: logger.error(f"❌ 下载错误: {e}")
    )
    
    # 游戏安装回调
    install_game_callbacks = Callbacks(
        start=lambda: logger.info("🎮 开始安装游戏"),
        finished=lambda: logger.info("✅ 游戏安装完成"),
        error=lambda e: logger.error(f"❌ 游戏安装错误: {e}")
    )
    
    # Forge 安装回调
    install_forge_callbacks = Callbacks(
        start=lambda: logger.info("🔨 开始安装 Forge"),
        finished=lambda: logger.info("✅ Forge 安装完成"),
        error=lambda e: logger.error(f"❌ Forge 安装错误: {e}")
    )
    
    # Fabric 安装回调
    install_fabric_callbacks = Callbacks(
        start=lambda: logger.info("🧵 开始安装 Fabric"),
        finished=lambda: logger.info("✅ Fabric 安装完成"),
        error=lambda e: logger.error(f"❌ Fabric 安装错误: {e}")
    )
    
    # 验证回调
    verify_callbacks = Callbacks(
        start=lambda: logger.info("🔍 开始验证文件"),
        finished=lambda: logger.info("✅ 文件验证完成"),
        error=lambda e: logger.error(f"❌ 文件验证错误: {e}")
    )
    
    # 创建回调组
    callback_group = InstallationCallbackGroup(
        download=download_callbacks,
        install_game=install_game_callbacks,
        install_forge=install_forge_callbacks,
        install_fabric=install_fabric_callbacks,
        verify=verify_callbacks
    )
    
    return callback_group


def example_simple_game_installation():
    """
    示例：简单的游戏安装
    """
    logger.info("=" * 60)
    logger.info("示例：简单的游戏安装")
    logger.info("=" * 60)
    
    # 创建回调组
    callback_group = create_callback_group()
    
    # 创建调度器配置
    config = SchedulerConfig(
        max_concurrent_tasks=2,
        max_retries=2,
        retry_delay=3.0
    )
    
    # 创建调度器
    scheduler = InstallationScheduler(callback_group, config)
    
    # 创建适配器
    minecraft_directory = Path.home() / ".minecraft"
    adapter = VanillaInstallationAdapter(minecraft_directory)
    
    # 创建游戏安装任务
    game_task = GameInstallationTask(
        task_id="install_minecraft_1.20.4",
        version_id="1.20.4",
        minecraft_directory=minecraft_directory,
        adapter=adapter,
        priority=TaskPriority.HIGH
    )
    
    # 添加任务到调度器
    scheduler.add_task(game_task)
    
    # 使用上下文管理器运行调度器
    with scheduler:
        # 等待任务完成
        while not scheduler._is_all_tasks_finished():
            time.sleep(1)
            progress = scheduler.get_progress()
            logger.info(f"总体进度: {progress['progress_percentage']}%")
    
    logger.info("游戏安装示例完成")


def example_modded_installation():
    """
    示例：带 Mod 加载器的完整安装
    """
    logger.info("=" * 60)
    logger.info("示例：带 Mod 加载器的完整安装")
    logger.info("=" * 60)
    
    # 创建回调组
    callback_group = create_callback_group()
    
    # 创建调度器配置
    config = SchedulerConfig(
        max_concurrent_tasks=3,
        max_retries=3,
        retry_delay=5.0,
        enable_dependency_check=True
    )
    
    # 创建调度器
    scheduler = InstallationScheduler(callback_group, config)
    
    # 创建适配器
    minecraft_directory = Path.home() / ".minecraft"
    vanilla_adapter = VanillaInstallationAdapter(minecraft_directory)
    forge_adapter = ForgeInstallationAdapter(minecraft_directory)
    fabric_adapter = FabricInstallationAdapter(minecraft_directory)
    
    # 创建任务
    # 1. 游戏安装任务
    game_task = GameInstallationTask(
        task_id="install_minecraft_1.20.1",
        version_id="1.20.1",
        minecraft_directory=minecraft_directory,
        adapter=vanilla_adapter,
        priority=TaskPriority.CRITICAL
    )
    
    # 2. Forge 安装任务（依赖游戏安装）
    forge_task = ModLoaderInstallationTask(
        task_id="install_forge_1.20.1",
        mod_loader_type="forge",
        version_id="1.20.1-47.2.0",
        minecraft_directory=minecraft_directory,
        adapter=forge_adapter,
        priority=TaskPriority.HIGH,
        dependencies=["install_minecraft_1.20.1"]
    )
    
    # 3. 资源验证任务（依赖所有安装完成）
    verify_task = AssetVerificationTask(
        task_id="verify_minecraft_1.20.1",
        version_id="1.20.1",
        minecraft_directory=minecraft_directory,
        priority=TaskPriority.LOW,
        dependencies=["install_minecraft_1.20.1", "install_forge_1.20.1"]
    )
    
    # 添加任务到调度器
    scheduler.add_tasks([game_task, forge_task, verify_task])
    
    # 运行调度器
    with scheduler:
        # 监控进度
        while not scheduler._is_all_tasks_finished():
            time.sleep(2)
            progress = scheduler.get_progress()
            logger.info(f"总体进度: {progress['progress_percentage']}% - "
                       f"完成: {progress['completed_tasks']}, "
                       f"运行中: {progress['running_tasks']}, "
                       f"待处理: {progress['pending_tasks']}")
    
    # 显示最终结果
    completed_tasks = scheduler.get_completed_tasks()
    failed_tasks = scheduler.get_failed_tasks()
    
    logger.info(f"✅ 完成任务: {len(completed_tasks)}")
    for task in completed_tasks:
        logger.info(f"  - {task.name}")
    
    if failed_tasks:
        logger.error(f"❌ 失败任务: {len(failed_tasks)}")
        for task in failed_tasks:
            logger.error(f"  - {task.name}: {task.error_message}")
    
    logger.info("带 Mod 加载器的完整安装示例完成")


def example_fabric_installation():
    """
    示例：Fabric 安装
    """
    logger.info("=" * 60)
    logger.info("示例：Fabric 安装")
    logger.info("=" * 60)
    
    # 创建回调组
    callback_group = create_callback_group()
    
    # 创建调度器
    scheduler = InstallationScheduler(callback_group)
    
    # 创建适配器
    minecraft_directory = Path.home() / ".minecraft"
    vanilla_adapter = VanillaInstallationAdapter(minecraft_directory)
    fabric_adapter = FabricInstallationAdapter(minecraft_directory)
    
    # 创建任务
    game_task = GameInstallationTask(
        task_id="install_minecraft_1.20.4",
        version_id="1.20.4",
        minecraft_directory=minecraft_directory,
        adapter=vanilla_adapter
    )
    
    fabric_task = ModLoaderInstallationTask(
        task_id="install_fabric_1.20.4",
        mod_loader_type="fabric",
        version_id="1.20.4",
        minecraft_directory=minecraft_directory,
        adapter=fabric_adapter,
        dependencies=["install_minecraft_1.20.4"],
        loader_version="0.15.0"  # 指定 Fabric 加载器版本
    )
    
    # 添加任务
    scheduler.add_tasks([game_task, fabric_task])
    
    # 运行调度器
    with scheduler:
        while not scheduler._is_all_tasks_finished():
            time.sleep(1)
            progress = scheduler.get_progress()
            logger.info(f"进度: {progress['progress_percentage']}%")
    
    logger.info("Fabric 安装示例完成")


def example_scheduler_control():
    """
    示例：调度器控制（暂停、恢复、停止）
    """
    logger.info("=" * 60)
    logger.info("示例：调度器控制")
    logger.info("=" * 60)
    
    # 创建回调组
    callback_group = create_callback_group()
    
    # 创建调度器
    scheduler = InstallationScheduler(callback_group)
    
    # 创建适配器
    minecraft_directory = Path.home() / ".minecraft"
    adapter = VanillaInstallationAdapter(minecraft_directory)
    
    # 创建多个任务
    tasks = []
    for i, version in enumerate(["1.20.4", "1.20.3", "1.20.2"]):
        task = GameInstallationTask(
            task_id=f"install_minecraft_{version}",
            version_id=version,
            minecraft_directory=minecraft_directory,
            adapter=adapter
        )
        tasks.append(task)
    
    # 添加任务
    scheduler.add_tasks(tasks)
    
    # 启动调度器
    scheduler.start()
    
    try:
        # 运行一段时间
        time.sleep(5)
        logger.info("⏸️ 暂停调度器")
        scheduler.pause()
        
        # 暂停期间
        time.sleep(3)
        logger.info("▶️ 恢复调度器")
        scheduler.resume()
        
        # 继续运行
        while not scheduler._is_all_tasks_finished():
            time.sleep(1)
            progress = scheduler.get_progress()
            logger.info(f"状态: {progress['status']}, 进度: {progress['progress_percentage']}%")
            
    finally:
        # 停止调度器
        logger.info("🛑 停止调度器")
        scheduler.stop()
    
    logger.info("调度器控制示例完成")


if __name__ == "__main__":
    """
    运行所有示例
    """
    logger.info("🚀 开始运行安装调度器示例")
    
    try:
        # 运行示例（注意：这些示例需要网络连接和适当的权限）
        # example_simple_game_installation()
        # example_modded_installation()
        # example_fabric_installation()
        # example_scheduler_control()
        
        logger.info("ℹ️ 示例代码已准备就绪，取消注释以运行具体示例")
        
    except Exception as e:
        logger.error(f"❌ 运行示例时发生错误: {e}")
    
    logger.info("✅ 安装调度器示例运行完成") 