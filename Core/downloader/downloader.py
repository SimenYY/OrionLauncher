import asyncio
import httpx
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
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> str:
        """
        异步下载文件。
        
        此方法从指定URL下载文件并保存到本地路径，同时通过回调函数报告下载进度。
        
        Parameters:
            url (str): 要下载的文件URL
            save_path (str): 文件保存的本地路径
            progress_callback (Optional[Callable[[int], None]]): 
                进度回调函数，接收一个0-100的整数表示下载百分比
        
        Returns:
            str: 下载成功的消息
            
        Raises:
            httpx.HTTPStatusError: 当HTTP请求失败时
            asyncio.CancelledError: 当下载被用户取消时
            IOError: 当文件写入失败时
        """
        self._is_cancelled = False
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status() # 如果请求失败则抛出异常

                total_size = int(response.headers.get('Content-Length', 0))
                downloaded_size = 0
                
                with open(save_path, 'wb') as f:
                    async for chunk in response.aiter_bytes():
                        if self._is_cancelled:
                            raise asyncio.CancelledError("下载被用户取消")
                        
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0 and progress_callback:
                            percentage = int((downloaded_size / total_size) * 100)
                            progress_callback(percentage)
        
        if progress_callback:
            progress_callback(100) # 确保最后是100%

        return f"文件下载完成: {save_path}"

    def cancel(self) -> None:
        """
        取消当前正在进行的下载。
        
        设置取消标志，使下载循环在下一次迭代时抛出CancelledError异常。
        """
        self._is_cancelled = True
