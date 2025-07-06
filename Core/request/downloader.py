import asyncio
import httpx
import time
from typing import Callable, Optional

class FileDownloader:
    """
    该类提供异步文件下载功能，支持进度跟踪和下载取消。
    
    Attributes:
        _is_cancelled (bool): 标记当前下载是否被取消
    """
    def __init__(self):
        """
        初始化下载器实例。
        
        设置初始取消状态为False。
        """
        self._is_cancelled = False

    async def download_file(
        self,
        url: str,
        save_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
        speed_callback: Optional[Callable[[int], None]] = None,
        size: int = 0
    ) -> str:
        """
        异步下载文件。
        
        此方法从指定URL下载文件并保存到本地路径，同时通过回调函数报告下载进度和速度。
        
        Parameters:
            url (str): 要下载的文件URL
            save_path (str): 文件保存的本地路径
            progress_callback (Optional[Callable[[int], None]]): 
                进度回调函数，接收一个0-100的整数表示下载百分比
            speed_callback (Optional[Callable[[int], None]]):
                速度回调函数，接收一个整数表示当前下载速度(B/s)
            size (int): 文件大小(字节)，默认为0。如果提供，将优先使用此值而非从响应头获取
        
        Returns:
            str: 下载成功的消息
            
        Raises:
            httpx.HTTPStatusError: 当HTTP请求失败时
            asyncio.CancelledError: 当下载被用户取消时
            IOError: 当文件写入失败时
        """
        self._is_cancelled = False
        # 大文件分片大小 (512KB)
        chunk_size = 512 * 1024
        # 用于计算下载速度
        last_time = time.time()
        last_size = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status() # 如果请求失败则抛出异常

                # 优先使用传入的size参数，如未提供则从响应头获取
                total_size = size if size > 0 else int(response.headers.get('Content-Length', 0))
                downloaded_size = 0
                
                with open(save_path, 'wb') as f:
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
            progress_callback(100) # 确保最后是100%
            
        if speed_callback:
            speed_callback(0) # 下载完成，速度为0

        return f"文件下载完成: {save_path}"

    def cancel(self) -> None:
        """
        取消当前正在进行的下载。
        
        设置取消标志，使下载循环在下一次迭代时抛出CancelledError异常。
        """
        self._is_cancelled = True
