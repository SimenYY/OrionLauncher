"""优化的文件下载器模块。

专门针对Minecraft大量小文件下载场景优化的下载器实现。
包含内存优化、连接池复用、智能缓存等功能。
"""

import asyncio
import logging
import os
import hashlib
import time
from typing import List, Dict, Optional, Set
from pathlib import Path

from src.utils.callbacks import IDownloadSingle, IDownloadMultiThread, Callbacks
from src.utils.types import DownloadFile
from src.utils.Exceptions import DownloadException, NetworkException, WrappedSystemException
from src.utils.Exceptions.code import CoreErrorCodes

from .downloader import ConnectionPoolManager, get_connection_pool_manager

logger = logging.getLogger(__name__)


class MemoryOptimizedDownloader:
    """内存优化的文件下载器
    
    专门针对大量小文件下载场景优化，包含以下特性：
    1. 智能内存管理
    2. 文件校验缓存
    3. 连接池复用
    4. 动态分块大小
    """
    
    def __init__(self, callback_group: IDownloadSingle):
        """初始化内存优化下载器
        
        Args:
            callback_group: 回调组接口
        """
        self._callback_group = callback_group
        self._is_cancelled = False
        
        # 内存使用监控
        self._max_memory_usage = 50 * 1024 * 1024  # 50MB最大内存使用
        self._current_memory_usage = 0
        
        # 文件校验缓存
        self._sha1_cache: Dict[str, str] = {}
    
    async def download_file(self, file: DownloadFile) -> str:
        """下载单个文件（内存优化版本）
        
        Args:
            file: 下载文件信息
            
        Returns:
            下载成功消息
        """
        self._is_cancelled = False
        
        try:
            # 验证必需字段
            if "url" not in file:
                raise DownloadException("下载文件缺少必需的URL字段", CoreErrorCodes.DOWNLOAD_GENERAL_ERROR)
            if "path" not in file:
                raise DownloadException("下载文件缺少必需的路径字段", CoreErrorCodes.DOWNLOAD_GENERAL_ERROR)
            
            # 检查文件是否已存在且校验正确
            if await self._is_file_valid(file):
                logger.debug(f"文件已存在且校验正确，跳过下载: {file['path']}")
                self._callback_group.start()
                self._callback_group.progress(100)
                self._callback_group.finished()
                return f"文件已存在: {file['path']}"
            
            logger.info(f"开始下载文件: {file['url']} -> {file['path']}")
            
            # 通知开始下载
            self._callback_group.start()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file["path"]), exist_ok=True)
            
            # 获取文件大小并计算最优分块大小
            file_size = file.get("size", 0)
            chunk_size = self._calculate_optimal_chunk_size(file_size)
            
            # 使用连接池下载
            pool_manager = await get_connection_pool_manager()
            client = await pool_manager.get_client(file["url"])
            
            downloaded_size = 0
            last_time = time.time()
            last_size = 0
            
            async with client.stream("GET", file["url"]) as response:
                response.raise_for_status()
                
                # 获取实际文件大小
                if file_size == 0:
                    file_size = int(response.headers.get("Content-Length", 0))
                
                logger.debug(f"文件大小: {file_size} 字节，分块大小: {chunk_size} 字节")
                
                # 内存优化的文件写入
                with open(file["path"], "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size):
                        if self._is_cancelled:
                            logger.info(f"下载被用户取消: {file['path']}")
                            raise asyncio.CancelledError("下载被用户取消")
                        
                        # 写入数据
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 更新内存使用统计
                        self._current_memory_usage += len(chunk)
                        
                        # 报告进度
                        self._callback_group.bytes_downloaded(downloaded_size, file_size)
                        
                        if file_size > 0:
                            percentage = int((downloaded_size / file_size) * 100)
                            self._callback_group.progress(percentage)
                        
                        # 计算下载速度
                        current_time = time.time()
                        time_diff = current_time - last_time
                        
                        if time_diff >= 1.0:
                            speed = int((downloaded_size - last_size) / time_diff)
                            self._callback_group.speed(speed)
                            last_time = current_time
                            last_size = downloaded_size
                        
                        # 内存压力检查
                        if self._current_memory_usage > self._max_memory_usage:
                            # 强制垃圾回收
                            import gc
                            gc.collect()
                            self._current_memory_usage = 0
            
            # 验证下载的文件
            if "sha1" in file:
                if not await self._verify_file_sha1(file["path"], file["sha1"]):
                    raise DownloadException(
                        f"文件校验失败: {file['path']}", 
                        CoreErrorCodes.DOWNLOAD_GENERAL_ERROR
                    )
                
                # 缓存校验结果
                self._sha1_cache[file["path"]] = file["sha1"]
            
            # 完成下载
            self._callback_group.progress(100)
            self._callback_group.speed(0)
            self._callback_group.finished()
            
            success_msg = f"文件下载完成: {file['path']} ({downloaded_size} 字节)"
            logger.info(success_msg)
            return success_msg
            
        except Exception as e:
            self._callback_group.error(e)
            raise
    
    def _calculate_optimal_chunk_size(self, file_size: int) -> int:
        """计算最优分块大小
        
        Args:
            file_size: 文件大小
            
        Returns:
            最优分块大小
        """
        if file_size == 0:
            return 8 * 1024  # 8KB默认
        elif file_size < 64 * 1024:  # 小于64KB
            return min(4 * 1024, file_size)  # 4KB或文件大小
        elif file_size < 1024 * 1024:  # 小于1MB
            return 16 * 1024  # 16KB
        elif file_size < 10 * 1024 * 1024:  # 小于10MB
            return 64 * 1024  # 64KB
        else:
            return 256 * 1024  # 256KB
    
    async def _is_file_valid(self, file: DownloadFile) -> bool:
        """检查文件是否已存在且有效
        
        Args:
            file: 文件信息
            
        Returns:
            文件是否有效
        """
        file_path = file["path"]
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False
        
        # 检查文件大小
        if "size" in file:
            actual_size = os.path.getsize(file_path)
            if actual_size != file["size"]:
                logger.debug(f"文件大小不匹配: {file_path} (期望: {file['size']}, 实际: {actual_size})")
                return False
        
        # 检查SHA1校验
        if "sha1" in file:
            # 先检查缓存
            if file_path in self._sha1_cache and self._sha1_cache[file_path] == file["sha1"]:
                return True
            
            # 计算SHA1
            if await self._verify_file_sha1(file_path, file["sha1"]):
                self._sha1_cache[file_path] = file["sha1"]
                return True
            else:
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
    
    def cancel(self):
        """取消下载"""
        self._is_cancelled = True
