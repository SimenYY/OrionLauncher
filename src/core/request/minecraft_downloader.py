"""Minecraft专用优化下载器。

专门针对Minecraft大量小文件下载场景优化的下载器，
整合了连接池、内存优化、批量处理等优化功能。
利用Minecraft文件本身的复用机制，跳过已存在的文件。
"""

import asyncio
import logging
import os
import time
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

from src.utils.callbacks import IDownloadMultiThread, Callbacks
from src.utils.types import DownloadFile
from src.utils.Exceptions import DownloadException, NetworkException
from src.utils.Exceptions.code import CoreErrorCodes

from .downloader import get_connection_pool_manager, FileDownloader

logger = logging.getLogger(__name__)


class MinecraftDownloadManager:
    """Minecraft专用下载管理器

    专门针对Minecraft下载场景优化的下载管理器：
    1. 智能连接池管理
    2. 文件存在性检查（利用Minecraft自身复用机制）
    3. 内存优化
    4. 智能并发控制
    """

    def __init__(self,
                 callback_group: IDownloadMultiThread,
                 tasks: List[DownloadFile],
                 minecraft_directory: str,
                 concurrent_count: Optional[int] = None,
                 max_retries: int = 3):
        """初始化Minecraft下载管理器

        Args:
            callback_group: 回调组接口
            tasks: 下载任务列表
            minecraft_directory: Minecraft安装目录
            concurrent_count: 并发数量，None表示自动计算
            max_retries: 最大重试次数
        """
        self._callback_group = callback_group
        self._tasks = tasks
        self._minecraft_directory = minecraft_directory
        self._max_retries = max_retries

        # 智能计算并发数
        if concurrent_count is None:
            self._concurrent_count = self._calculate_minecraft_concurrency()
        else:
            self._concurrent_count = concurrent_count

        # 状态跟踪
        self._is_cancelled = False
        self._task_progress: Dict[str, int] = {}
        self._task_downloaded: Dict[str, int] = {}
        self._task_total: Dict[str, int] = {}
        self._task_speeds: Dict[str, int] = {}
        self._completed_tasks = 0
        self._failed_tasks = 0
        self._skipped_tasks = 0

        logger.info(f"Minecraft下载管理器初始化完成 - 任务数: {len(tasks)}, "
                   f"并发数: {self._concurrent_count}")
    
    def _calculate_minecraft_concurrency(self) -> int:
        """计算Minecraft下载的最优并发数
        
        Returns:
            最优并发数
        """
        task_count = len(self._tasks)
        
        # 分析Minecraft文件类型
        assets_count = 0  # 资源文件
        libraries_count = 0  # 库文件
        other_count = 0  # 其他文件
        
        for task in self._tasks:
            path = task.get("path", "")
            if "assets" in path:
                assets_count += 1
            elif "libraries" in path:
                libraries_count += 1
            else:
                other_count += 1
        
        # 根据文件类型分布计算并发数
        if assets_count > task_count * 0.7:  # 主要是资源文件
            # 资源文件通常很小，可以使用较高并发
            concurrency = min(25, max(10, task_count // 4))
        elif libraries_count > task_count * 0.5:  # 主要是库文件
            # 库文件较大，使用中等并发
            concurrency = min(15, max(5, task_count // 6))
        else:
            # 混合文件，使用保守并发
            concurrency = min(10, max(3, task_count // 8))
        
        # 确保在合理范围内
        concurrency = max(1, min(concurrency, 30))
        
        logger.info(f"Minecraft并发数计算: {concurrency} "
                   f"(资源文件: {assets_count}, 库文件: {libraries_count}, 其他: {other_count})")
        
        return concurrency
    
    async def download_minecraft_files(self) -> bool:
        """下载Minecraft文件

        Returns:
            下载是否成功
        """
        logger.info(f"开始下载Minecraft文件，共 {len(self._tasks)} 个文件")
        self._callback_group.start()

        try:
            # 预处理任务：检查文件是否已存在
            await self._preprocess_tasks()

            # 如果所有文件都已存在
            if self._skipped_tasks == len(self._tasks):
                logger.info("所有文件都已存在，跳过下载")
                self._callback_group.progress(100)
                self._callback_group.finished()
                return True

            # 执行下载
            success = await self._execute_downloads()

            if success:
                total_original_tasks = self._skipped_tasks + len(self._tasks)
                logger.info(f"Minecraft文件下载完成 - 总数: {total_original_tasks}, "
                           f"跳过: {self._skipped_tasks}, 新下载: {self._completed_tasks}")
                self._callback_group.finished()
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Minecraft文件下载失败: {e}")
            self._callback_group.error(e)
            return False
    
    async def _preprocess_tasks(self):
        """预处理任务：检查文件是否已存在"""
        logger.info("检查文件是否已存在...")

        tasks_to_download = []

        for task in self._tasks:
            file_path = task.get("path", "")
            size = task.get("size", 0)
            sha1 = task.get("sha1", "")

            # 确保路径是绝对路径
            if not os.path.isabs(file_path):
                file_path = os.path.join(self._minecraft_directory, file_path)
                task["path"] = file_path

            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 检查文件是否已存在且有效
            if await self._is_file_valid(file_path, size, sha1):
                self._skipped_tasks += 1
                logger.debug(f"文件已存在且有效: {file_path}")

                # 模拟完成状态
                task_id = f"skipped_{self._skipped_tasks}"
                self._task_progress[task_id] = 100
                self._task_downloaded[task_id] = size
                self._task_total[task_id] = size
            else:
                tasks_to_download.append(task)

        # 更新任务列表
        self._tasks = tasks_to_download

        logger.info(f"文件检查完成 - 跳过: {self._skipped_tasks}, 需要下载: {len(self._tasks)}")

        # 更新进度
        if self._skipped_tasks > 0:
            total_tasks = self._skipped_tasks + len(self._tasks)
            skip_progress = int((self._skipped_tasks / total_tasks) * 100)
            self._callback_group.progress(skip_progress)

    async def _is_file_valid(self, file_path: str, expected_size: int = 0, expected_sha1: str = "") -> bool:
        """检查文件是否已存在且有效

        Args:
            file_path: 文件路径
            expected_size: 期望文件大小
            expected_sha1: 期望SHA1值

        Returns:
            文件是否有效
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False

        # 检查文件大小
        if expected_size > 0:
            actual_size = os.path.getsize(file_path)
            if actual_size != expected_size:
                logger.debug(f"文件大小不匹配: {file_path} (期望: {expected_size}, 实际: {actual_size})")
                return False

        # 检查SHA1校验（如果提供）
        if expected_sha1:
            if not await self._verify_file_sha1(file_path, expected_sha1):
                logger.debug(f"文件SHA1校验失败: {file_path}")
                return False

        return True

    async def _verify_file_sha1(self, file_path: str, expected_sha1: str) -> bool:
        """验证文件SHA1校验和

        Args:
            file_path: 文件路径
            expected_sha1: 期望的SHA1值

        Returns:
            校验是否通过
        """
        try:
            import hashlib
            sha1_hash = hashlib.sha1()

            # 异步读取文件计算SHA1
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(8192)  # 8KB分块读取
                    if not chunk:
                        break
                    sha1_hash.update(chunk)

                    # 让出控制权，避免阻塞事件循环
                    await asyncio.sleep(0)

            actual_sha1 = sha1_hash.hexdigest()
            return actual_sha1.lower() == expected_sha1.lower()

        except Exception as e:
            logger.error(f"计算文件SHA1时发生错误: {file_path} - {e}")
            return False
    
    async def _execute_downloads(self) -> bool:
        """执行下载任务"""
        if not self._tasks:
            logger.info("没有需要下载的任务")
            return True
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(self._concurrent_count)
        
        # 创建下载任务
        download_tasks = []
        for i, task in enumerate(self._tasks):
            task_id = f"download_{i}"
            download_task = asyncio.create_task(
                self._download_single_file(semaphore, task_id, task)
            )
            download_tasks.append(download_task)
        
        # 启动监控
        monitor_task = asyncio.create_task(self._monitor_progress())
        
        try:
            # 等待所有下载完成
            results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # 检查结果
            success_count = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"任务 {i} 失败: {result}")
                else:
                    success_count += 1
            
            return success_count == len(self._tasks)
            
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _download_single_file(self, semaphore: asyncio.Semaphore, 
                                   task_id: str, task: DownloadFile) -> bool:
        """下载单个文件"""
        async with semaphore:
            if self._is_cancelled:
                return False
            
            try:
                # 创建单文件下载器
                downloader = FileDownloader(
                    self._create_file_callback(task_id)
                )

                # 执行下载
                await downloader.download_file(task)

                self._completed_tasks += 1
                return True
                
            except Exception as e:
                logger.error(f"下载文件失败 {task_id}: {e}")
                self._failed_tasks += 1
                return False
    
    def _create_file_callback(self, task_id: str) -> Callbacks:
        """创建单文件回调，符合IDownloadSingle接口"""
        def on_start():
            logger.debug(f"任务 {task_id} 开始下载")

        def on_progress(progress: int):
            self._task_progress[task_id] = progress

        def on_bytes_downloaded(downloaded: int, total: int):
            self._task_downloaded[task_id] = downloaded
            self._task_total[task_id] = total

        def on_speed(speed: int):
            self._task_speeds[task_id] = speed

        def on_finished():
            logger.debug(f"任务 {task_id} 下载完成")

        def on_error(error: Exception):
            logger.error(f"任务 {task_id} 下载失败: {error}")

        return Callbacks(
            start=on_start,
            progress=on_progress,
            bytes_downloaded=on_bytes_downloaded,
            speed=on_speed,
            finished=on_finished,
            error=on_error
        )
    
    async def _monitor_progress(self):
        """监控下载进度"""
        while not self._is_cancelled:
            try:
                # 计算总体进度
                total_original_tasks = self._skipped_tasks + len(self._tasks)
                completed = self._skipped_tasks + self._completed_tasks

                if total_original_tasks > 0:
                    progress = int((completed / total_original_tasks) * 100)
                    self._callback_group.progress(progress)

                # 计算总体速度
                total_speed = sum(self._task_speeds.values())
                self._callback_group.speed(total_speed)

                # 报告任务进度
                self._callback_group.tasks_progress(self._task_progress.copy())

                await asyncio.sleep(1.0)

            except asyncio.CancelledError:
                break
    
    def cancel(self):
        """取消下载"""
        logger.info("取消Minecraft文件下载")
        self._is_cancelled = True
