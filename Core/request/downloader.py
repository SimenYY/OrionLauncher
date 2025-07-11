"""文件下载器模块。

该模块提供异步文件下载功能，支持进度跟踪、速度监控和下载取消。
"""

import asyncio
import time
from typing import List, Dict

from Utils.callbacks import IDownloadSingle, IDownloadMultiThread, Callbacks
from Utils.types import DownloadFile

import httpx


class FileDownloader:
    """异步文件下载器。

    提供异步文件下载功能，支持进度跟踪和下载取消。
    使用回调组模式统一管理下载事件（开始、进度、速度、完成、错误）。
    适用于需要长时间下载大文件的场景。

    Attributes:
        _is_cancelled (bool): 标记当前下载是否被取消
        _callback_group (IDownloadSingle): 回调组，用于处理下载事件

    Args:
        callback_group: 实现 IDownloadSingle 接口的回调组对象，用于处理下载过程中的各种事件

    Example:
        基本使用方法::

            # 创建实现 IDownloadSingle 的回调组
            callback_group = MyDownloadCallbacks()
            
            # 创建下载器
            downloader = FileDownloader(callback_group)

            # 开始下载
            await downloader.download_file(
                "https://example.com/file.zip",
                "/path/to/save/file.zip"
            )

    Note:
        * 回调组必须实现 IDownloadSingle 接口的所有方法
        * 下载过程中会自动调用相应的回调方法
        * 支持下载取消和错误处理
    """

    def __init__(self,
                 callback_group: IDownloadSingle,
                 ):
        """初始化下载器实例。

        Args:
            callback_group: 实现 IDownloadSingle 接口的回调组对象
        """
        self._is_cancelled = False
        self._callback_group: IDownloadSingle = callback_group

    async def download_file(
        self,
        file: DownloadFile,
    ) -> str:
        """异步下载文件。

        从 DownloadFile 对象中获取下载信息并下载文件到指定路径，
        通过回调组报告下载状态、进度和速度。
        支持大文件分块下载，避免内存占用过多。

        Args:
            file: DownloadFile 对象，包含以下字段：
                - url (str): 要下载的文件URL（必需）
                - path (str): 文件保存的本地路径（可选）
                - size (int): 文件大小(字节)（可选）
                - sha1 (str): 文件SHA1校验和（可选）

        Returns:
            下载成功的消息字符串

        Raises:
            httpx.HTTPStatusError: 当HTTP请求失败时（如404, 500等状态码）
            asyncio.CancelledError: 当下载被用户取消时
            IOError: 当文件写入失败时（如磁盘空间不足、权限不够等）
            httpx.TimeoutException: 当请求超时时
            KeyError: 当 DownloadFile 对象缺少必需字段时

        Note:
            * 下载过程中会定期检查取消状态
            * 使用512KB的分块大小进行下载
            * 每秒更新一次下载速度
            * 如果无法获取文件大小，进度回调不会被调用
            * 使用回调组统一管理所有下载事件
            * 如果 file 对象中未提供 size，将尝试从响应头获取

        Example:
            下载文件::

                file_info = {
                    "url": "https://example.com/large_file.zip",
                    "path": "/downloads/large_file.zip",
                    "size": 1024000
                }
                
                try:
                    result = await downloader.download_file(file_info)
                    print(result)
                except asyncio.CancelledError:
                    print("下载被取消")
                except httpx.HTTPStatusError as e:
                    print(f"HTTP错误: {e.response.status_code}")
        """
        self._is_cancelled = False
        
        try:
            # 通知开始下载
            self._callback_group.start()
            
            # 大文件分片大小 (512KB)
            chunk_size = 512 * 1024
            # 用于计算下载速度
            last_time = time.time()
            last_size = 0

            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("GET", file["url"]) as response:
                    response.raise_for_status()  # 如果请求失败则抛出异常

                    # 优先使用传入的size参数，如未提供则从响应头获取
                    total_size = (
                        file["size"] if file["size"] > 0 else int(response.headers.get("Content-Length", 0))
                    )
                    downloaded_size = 0

                    with open(file["path"], "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size):
                            if self._is_cancelled:
                                raise asyncio.CancelledError("下载被用户取消")

                            f.write(chunk)
                            downloaded_size += len(chunk)

                            # 报告字节级进度
                            self._callback_group.bytes_downloaded(downloaded_size, total_size)

                            # 计算并回调下载进度
                            if total_size > 0:
                                percentage = int((downloaded_size / total_size) * 100)
                                self._callback_group.progress(percentage)

                            # 计算并回调下载速度
                            current_time = time.time()
                            time_diff = current_time - last_time

                            # 每秒更新一次下载速度
                            if time_diff >= 1.0:
                                speed = int((downloaded_size - last_size) / time_diff)
                                self._callback_group.speed(speed)
                                last_time = current_time
                                last_size = downloaded_size

            # 确保最后进度为100%
            self._callback_group.progress(100)
            # 下载完成，速度为0
            self._callback_group.speed(0)
            # 通知下载完成
            self._callback_group.finished()

            return f"文件下载完成: {file['path']}"

        except Exception as e:
            # 通知下载错误
            self._callback_group.error(e)
            raise

    def cancel(self) -> None:
        """取消当前正在进行的下载。

        设置取消标志，使下载循环在下一次迭代时抛出CancelledError异常。

        Note:
            * 取消操作是异步的，不会立即停止下载
            * 下载器会在下一个数据块处理时检查取消状态
            * 已下载的部分文件会保留在磁盘上

        Example:
            在另一个协程中取消下载::

                # 启动下载
                download_task = asyncio.create_task(
                    downloader.download_file(url, path)
                )

                # 3秒后取消
                await asyncio.sleep(3)
                downloader.cancel()

                try:
                    await download_task
                except asyncio.CancelledError:
                    print("下载已取消")
        """
        self._is_cancelled = True

class DownloadManager:
    """
    并发下载管理器
    
    支持多个文件的并发下载，提供任务调度、进度跟踪和速度监控功能。
    使用回调组模式统一管理多线程下载过程中的所有事件。
    
    **进度计算机制**：
    - 基于字节数计算总体进度，而不是简单的任务进度平均值
    - 总体进度 = (所有任务已下载字节数之和) / (所有任务总字节数之和) * 100
    - 这样可以准确反映不同大小文件的下载贡献度
    
    Attributes:
        _callback_group (IDownloadMultiThread): 多线程下载回调组
        _tasks (List[DownloadFile]): 下载任务列表
        _concurrent_count (int): 并发下载数量
        _task_progress (Dict[str, int]): 各任务的下载进度 (0-100)
        _task_speeds (Dict[str, int]): 各任务的下载速度 (字节/秒)
        _task_downloaded_bytes (Dict[str, int]): 各任务已下载字节数
        _task_total_bytes (Dict[str, int]): 各任务总字节数
        _is_cancelled (bool): 是否已取消下载
        _downloaders (Dict[str, FileDownloader]): 任务ID到下载器的映射
    """
    
    def __init__(self,
                 callback_group: IDownloadMultiThread,
                 tasks: List[DownloadFile],
                 concurrent_count: int = 5,
                 ):
        """
        Args:
            callback_group: 实现 IDownloadMultiThread 接口的回调组对象，用于处理多线程下载过程中的各种事件和状态更新
            tasks: 下载任务列表，每个任务是一个 DownloadFile 对象
            concurrent_count: 并发下载任务数，默认为5
        """
        self._callback_group: IDownloadMultiThread = callback_group
        self._tasks: List[DownloadFile] = tasks
        self._concurrent_count: int = concurrent_count
        
        # 任务状态跟踪
        self._task_progress: Dict[str, int] = {}
        self._task_speeds: Dict[str, int] = {}
        self._task_downloaded_bytes: Dict[str, int] = {}  # 各任务已下载字节数
        self._task_total_bytes: Dict[str, int] = {}       # 各任务总字节数
        self._is_cancelled: bool = False
        self._downloaders: Dict[str, FileDownloader] = {}
        
        # 初始化任务状态
        for i, task in enumerate(tasks):
            task_id = f"task_{i}"
            self._task_progress[task_id] = 0
            self._task_speeds[task_id] = 0
            self._task_downloaded_bytes[task_id] = 0
            self._task_total_bytes[task_id] = task.get("size", 0)

    async def schedule(self) -> None:
        """
        调度并执行所有下载任务
        
        使用 asyncio.Semaphore 控制并发数量，确保不会同时启动过多下载任务。
        监控所有任务的进度和速度，定期更新总体状态。
        """
        self._callback_group.start()
        
        # 计算总文件大小
        total_size = sum(task.get("size", 0) for task in self._tasks)
        if total_size > 0:
            self._callback_group.size(total_size)
        
        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(self._concurrent_count)
        
        # 创建所有下载任务
        download_tasks = []
        for i, task in enumerate(self._tasks):
            task_id = f"task_{i}"
            download_task = asyncio.create_task(
                self._download_with_semaphore(semaphore, task_id, task)
            )
            download_tasks.append(download_task)
        
        # 启动速度监控任务
        speed_monitor_task = asyncio.create_task(self._monitor_speed())
        
        try:
            # 等待所有下载任务完成
            await asyncio.gather(*download_tasks, return_exceptions=True)
        finally:
            # 停止速度监控
            speed_monitor_task.cancel()
            try:
                await speed_monitor_task
            except asyncio.CancelledError:
                pass

    async def _download_with_semaphore(self, semaphore: asyncio.Semaphore, task_id: str, task: DownloadFile) -> None:
        """
        使用信号量控制的下载任务
        
        Args:
            semaphore: 用于控制并发数量的信号量
            task_id: 任务ID
            task: 下载任务对象
        """
        async with semaphore:
            if self._is_cancelled:
                return
            
            try:
                # 创建任务专用的下载器
                downloader = self._create_task_downloader(task_id)
                self._downloaders[task_id] = downloader
                
                # 开始下载
                await downloader.download_file(task)
                
            except Exception as e:
                self._callback_group.error(task_id, e)

    def _create_task_downloader(self, task_id: str) -> FileDownloader:
        """
        为特定任务创建下载器实例（闭包）
        
        Args:
            task_id: 任务ID
            
        Returns:
            配置了任务专用回调的 FileDownloader 实例
        """
        def on_start() -> None:
            """任务开始回调"""
            pass  # 多线程下载器在整体开始时已调用 start()
        
        def on_progress(progress: int) -> None:
            """任务进度回调"""
            self._update_task_progress(task_id, progress)
        
        def on_bytes_downloaded(downloaded: int, total: int) -> None:
            """字节级进度回调"""
            self._update_task_bytes(task_id, downloaded, total)
        
        def on_speed(speed: int) -> None:
            """任务速度回调"""
            self._update_task_speed(task_id, speed)
        
        def on_finished() -> None:
            """任务完成回调"""
            self._task_finished(task_id)
        
        def on_error(error: Exception) -> None:
            """任务错误回调"""
            self._callback_group.error(task_id, error)
        
        # 创建任务专用的回调组
        task_callbacks = Callbacks(
            start=on_start,
            progress=on_progress,
            bytes_downloaded=on_bytes_downloaded,
            speed=on_speed,
            finished=on_finished,
            error=on_error
        )
        
        return FileDownloader(callback_group=task_callbacks)

    def _update_task_progress(self, task_id: str, progress: int) -> None:
        """
        更新任务进度并计算基于字节数的总体进度
        
        Args:
            task_id: 任务ID
            progress: 任务进度 (0-100)
        """
        self._task_progress[task_id] = progress
        
        # 更新各任务进度
        self._callback_group.tasks_progress(self._task_progress.copy())
        
        # 基于字节数计算总体进度
        self._calculate_overall_progress()

    def _calculate_overall_progress(self) -> None:
        """
        基于字节数计算总体下载进度
        """
        total_bytes = sum(self._task_total_bytes.values())
        downloaded_bytes = sum(self._task_downloaded_bytes.values())
        
        if total_bytes > 0:
            overall_progress = int((downloaded_bytes / total_bytes) * 100)
            self._callback_group.progress(overall_progress)
            
            # 报告已下载大小
            for task_id, downloaded in self._task_downloaded_bytes.items():
                self._callback_group.downloaded_size(task_id, downloaded)

    def _update_task_speed(self, task_id: str, speed: int) -> None:
        """
        更新任务下载速度
        
        Args:
            task_id: 任务ID
            speed: 下载速度 (字节/秒)
        """
        self._task_speeds[task_id] = speed

    def _update_task_bytes(self, task_id: str, downloaded: int, total: int) -> None:
        """
        更新任务已下载字节数并计算总体进度
        
        Args:
            task_id: 任务ID
            downloaded: 已下载字节数
            total: 总字节数
        """
        self._task_downloaded_bytes[task_id] = downloaded
        self._task_total_bytes[task_id] = total
        
        # 基于字节数计算总体进度
        self._calculate_overall_progress()

    def _task_finished(self, task_id: str) -> None:
        """
        处理任务完成事件
        
        Args:
            task_id: 完成的任务ID
        """
        self._callback_group.finished(task_id)
        
        # 检查是否所有任务都已完成（基于字节数）
        all_completed = True
        for task_id in self._task_total_bytes:
            downloaded = self._task_downloaded_bytes.get(task_id, 0)
            total = self._task_total_bytes.get(task_id, 0)
            if total > 0 and downloaded < total:
                all_completed = False
                break
        
        if all_completed:
            # 所有任务完成，设置总进度为100%
            self._callback_group.progress(100)
            # 停止速度监控
            for task_id in self._task_speeds:
                self._task_speeds[task_id] = 0
            self._callback_group.speed(0)

    async def _monitor_speed(self) -> None:
        """
        监控总体下载速度
        
        定期计算并报告所有任务的总下载速度
        """
        while not self._is_cancelled:
            try:
                # 计算总速度
                total_speed = sum(self._task_speeds.values())
                self._callback_group.speed(total_speed)
                
                # 每秒更新一次
                await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                break

    def cancel(self) -> None:
        """
        取消所有下载任务
        
        设置取消标志并通知所有活跃的下载器停止下载
        """
        self._is_cancelled = True
        
        # 取消所有活跃的下载器
        for downloader in self._downloaders.values():
            downloader.cancel()

    @property
    def task_count(self) -> int:
        """获取任务总数"""
        return len(self._tasks)
    
    @property
    def completed_tasks(self) -> int:
        """获取已完成任务数（基于字节数判断）"""
        completed = 0
        for task_id in self._task_total_bytes:
            downloaded = self._task_downloaded_bytes.get(task_id, 0)
            total = self._task_total_bytes.get(task_id, 0)
            if total > 0 and downloaded >= total:
                completed += 1
            elif total == 0 and self._task_progress.get(task_id, 0) == 100:
                # 对于无法获取大小的文件，回退到百分比判断
                completed += 1
        return completed
    
    @property
    def is_completed(self) -> bool:
        """检查是否所有任务都已完成"""
        return self.completed_tasks == self.task_count
