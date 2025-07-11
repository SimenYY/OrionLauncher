"""文件下载器模块。

该模块提供异步文件下载功能，支持进度跟踪、速度监控和下载取消。
"""

import asyncio
import time
from typing import Callable, Optional

import httpx


class FileDownloader:
    """异步文件下载器。

    提供异步文件下载功能，支持进度跟踪和下载取消。
    适用于需要长时间下载大文件的场景。

    Attributes:
        _is_cancelled (bool): 标记当前下载是否被取消

    Example:
        下载文件并显示进度::

            downloader = FileDownloader()

            def on_progress(percentage):
                print(f"下载进度: {percentage}%")

            def on_speed(speed):
                print(f"下载速度: {speed/1024:.1f} KB/s")

            await downloader.download_file(
                "https://example.com/file.zip",
                "/path/to/save/file.zip",
                progress_callback=on_progress,
                speed_callback=on_speed
            )
    """

    def __init__(self):
        """初始化下载器实例。

        设置初始取消状态为False，准备开始下载任务。
        """
        self._is_cancelled = False

    async def download_file(
        self,
        url: str,
        save_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
        speed_callback: Optional[Callable[[int], None]] = None,
        size: int = 0,
    ) -> str:
        """异步下载文件。

        从指定URL下载文件并保存到本地路径，同时通过回调函数报告下载进度和速度。
        支持大文件分块下载，避免内存占用过多。

        Args:
            url: 要下载的文件URL
            save_path: 文件保存的本地路径
            progress_callback: 进度回调函数，接收一个0-100的整数表示下载百分比
            speed_callback: 速度回调函数，接收一个整数表示当前下载速度(字节/秒)
            size: 文件大小(字节)，默认为0。如果提供，将优先使用此值而非从响应头获取

        Returns:
            下载成功的消息字符串

        Raises:
            httpx.HTTPStatusError: 当HTTP请求失败时（如404, 500等状态码）
            asyncio.CancelledError: 当下载被用户取消时
            IOError: 当文件写入失败时（如磁盘空间不足、权限不够等）
            httpx.TimeoutException: 当请求超时时

        Note:
            * 下载过程中会定期检查取消状态
            * 使用512KB的分块大小进行下载
            * 每秒更新一次下载速度
            * 如果无法获取文件大小，进度回调不会被调用

        Example:
            下载文件::

                try:
                    result = await downloader.download_file(
                        "https://example.com/large_file.zip",
                        "/downloads/large_file.zip"
                    )
                    print(result)
                except asyncio.CancelledError:
                    print("下载被取消")
                except httpx.HTTPStatusError as e:
                    print(f"HTTP错误: {e.response.status_code}")
        """
        self._is_cancelled = False
        # 大文件分片大小 (512KB)
        chunk_size = 512 * 1024
        # 用于计算下载速度
        last_time = time.time()
        last_size = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()  # 如果请求失败则抛出异常

                # 优先使用传入的size参数，如未提供则从响应头获取
                total_size = (
                    size if size > 0 else int(response.headers.get("Content-Length", 0))
                )
                downloaded_size = 0

                with open(save_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size):
                        if self._is_cancelled:
                            raise asyncio.CancelledError("下载被用户取消")

                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 计算并回调下载进度
                        if total_size > 0 and progress_callback:
                            percentage = int((downloaded_size / total_size) * 100)
                            progress_callback(percentage)

                        # 计算并回调下载速度
                        if speed_callback:
                            current_time = time.time()
                            time_diff = current_time - last_time

                            # 每秒更新一次下载速度
                            if time_diff >= 1.0:
                                speed = int((downloaded_size - last_size) / time_diff)
                                speed_callback(speed)
                                last_time = current_time
                                last_size = downloaded_size

        if progress_callback:
            progress_callback(100)  # 确保最后是100%

        if speed_callback:
            speed_callback(0)  # 下载完成，速度为0

        return f"文件下载完成: {save_path}"

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
