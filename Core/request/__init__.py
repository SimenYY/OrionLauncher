"""请求处理模块。

该模块包含网络请求相关的功能，包括文件下载、API调用等。
"""

from .downloader import FileDownloader

__all__ = ['FileDownloader']
