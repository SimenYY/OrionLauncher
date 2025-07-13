"""文件下载器模块。

该模块提供异步文件下载功能，支持进度跟踪、速度监控和下载取消。
"""

import asyncio
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse

from Utils.callbacks import IDownloadSingle, IDownloadMultiThread, Callbacks
from Utils.types import DownloadFile
from Utils.Exceptions import DownloadException, NetworkException, WrappedSystemException
from Utils.Exceptions.code import CoreErrorCodes

import httpx

logger = logging.getLogger(__name__)


class ConnectionPoolManager:
    """HTTP连接池管理器

    为不同的域名维护独立的连接池，优化大量小文件下载的性能。
    """

    def __init__(self, max_connections_per_host: int = 20, max_keepalive_connections: int = 10):
        """初始化连接池管理器

        Args:
            max_connections_per_host: 每个主机的最大连接数
            max_keepalive_connections: 最大保持活跃的连接数
        """
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self._max_connections_per_host = max_connections_per_host
        self._max_keepalive_connections = max_keepalive_connections
        self._lock = asyncio.Lock()

    async def get_client(self, url: str) -> httpx.AsyncClient:
        """获取指定URL对应的HTTP客户端

        Args:
            url: 目标URL

        Returns:
            HTTP客户端实例
        """
        parsed = urlparse(url)
        host_key = f"{parsed.scheme}://{parsed.netloc}"

        async with self._lock:
            if host_key not in self._clients:
                # 创建针对该主机优化的HTTP客户端
                limits = httpx.Limits(
                    max_connections=self._max_connections_per_host,
                    max_keepalive_connections=self._max_keepalive_connections
                )

                self._clients[host_key] = httpx.AsyncClient(
                    limits=limits,
                    timeout=httpx.Timeout(30.0, connect=10.0),
                    http2=True,  # 启用HTTP/2支持
                    follow_redirects=True
                )

                logger.debug(f"为主机 {host_key} 创建新的HTTP客户端")

            return self._clients[host_key]

    async def close_all(self):
        """关闭所有HTTP客户端"""
        async with self._lock:
            for client in self._clients.values():
                await client.aclose()
            self._clients.clear()
            logger.debug("已关闭所有HTTP客户端")


# 全局连接池管理器实例
_connection_pool_manager: Optional[ConnectionPoolManager] = None


async def get_connection_pool_manager() -> ConnectionPoolManager:
    """获取全局连接池管理器实例"""
    global _connection_pool_manager
    if _connection_pool_manager is None:
        _connection_pool_manager = ConnectionPoolManager()
    return _connection_pool_manager


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
            DownloadException: 下载相关错误
            NetworkException: 网络连接错误
            FileSystemException: 文件系统错误

        Note:
            * 下载过程中会定期检查取消状态
            * 根据文件大小动态调整分块大小
            * 每秒更新一次下载速度
            * 如果无法获取文件大小，进度回调不会被调用
            * 使用回调组统一管理所有下载事件
            * 如果 file 对象中未提供 size，将尝试从响应头获取
            * 使用连接池优化网络连接复用
        """
        self._is_cancelled = False

        try:
            # 验证必需字段
            if "url" not in file:
                raise DownloadException("下载文件缺少必需的URL字段", CoreErrorCodes.DOWNLOAD_GENERAL_ERROR)
            if "path" not in file:
                raise DownloadException("下载文件缺少必需的路径字段", CoreErrorCodes.DOWNLOAD_GENERAL_ERROR)

            logger.info(f"开始下载文件: {file['url']} -> {file['path']}")

            # 通知开始下载
            self._callback_group.start()

            # 用于计算下载速度
            last_time = time.time()
            last_size = 0

            try:
                # 使用连接池管理器获取HTTP客户端
                pool_manager = await get_connection_pool_manager()
                client = await pool_manager.get_client(file["url"])

                async with client.stream("GET", file["url"]) as response:
                    response.raise_for_status()  # 如果请求失败则抛出异常

                    # 优先使用传入的size参数，如未提供则从响应头获取
                    total_size = (
                        file.get("size", 0) if file.get("size", 0) > 0
                        else int(response.headers.get("Content-Length", 0))
                    )
                    downloaded_size = 0

                    # 根据文件大小动态调整分块大小
                    if total_size > 0:
                        if total_size < 1024 * 1024:  # 小于1MB的文件
                            chunk_size = min(8 * 1024, total_size)  # 8KB或文件大小
                        elif total_size < 10 * 1024 * 1024:  # 小于10MB的文件
                            chunk_size = 64 * 1024  # 64KB
                        else:  # 大文件
                            chunk_size = 512 * 1024  # 512KB
                    else:
                        chunk_size = 64 * 1024  # 默认64KB

                    logger.debug(f"文件大小: {total_size} 字节，分块大小: {chunk_size} 字节")

                    try:
                        with open(file["path"], "wb") as f:
                            async for chunk in response.aiter_bytes(chunk_size):
                                if self._is_cancelled:
                                    logger.info(f"下载被用户取消: {file['path']}")
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

                    except (IOError, OSError) as e:
                        logger.error(f"文件写入失败: {file['path']} - {e}")
                        raise DownloadException(
                            f"文件写入失败: {e}",
                            CoreErrorCodes.FILE_PERMISSION_DENIED if "permission" in str(e).lower()
                            else CoreErrorCodes.FILESYSTEM_GENERAL_ERROR
                        ) from e
                            
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP请求失败 [{e.response.status_code}]: {file['url']}"
                logger.error(error_msg)
                
                if e.response.status_code == 404:
                    raise DownloadException(error_msg, CoreErrorCodes.DOWNLOAD_FILE_NOT_FOUND) from e
                elif e.response.status_code == 403:
                    raise DownloadException(error_msg, CoreErrorCodes.DOWNLOAD_PERMISSION_DENIED) from e
                else:
                    raise DownloadException(error_msg, CoreErrorCodes.API_SERVER_ERROR) from e
                    
            except (httpx.TimeoutException, httpx.ConnectTimeout) as e:
                error_msg = f"网络连接超时: {file['url']}"
                logger.error(error_msg)
                raise NetworkException(error_msg, CoreErrorCodes.NETWORK_TIMEOUT_ERROR) from e
                
            except (httpx.ConnectError, httpx.NetworkError) as e:
                error_msg = f"网络连接失败: {file['url']} - {e}"
                logger.error(error_msg)
                raise NetworkException(error_msg, CoreErrorCodes.NETWORK_CONNECTION_ERROR) from e

            # 确保最后进度为100%
            self._callback_group.progress(100)
            # 下载完成，速度为0
            self._callback_group.speed(0)
            # 通知下载完成
            self._callback_group.finished()

            success_msg = f"文件下载完成: {file['path']} ({downloaded_size} 字节)"
            logger.info(success_msg)
            return success_msg

        except (DownloadException, NetworkException) as e:
            # 项目标准异常，直接传递
            self._callback_group.error(e)
            raise
            
        except asyncio.CancelledError as e:
            # 取消操作，使用特定错误码
            cancel_error = DownloadException("下载被取消", CoreErrorCodes.DOWNLOAD_INTERRUPTED)
            self._callback_group.error(cancel_error)
            raise cancel_error from e
            
        except Exception as e:
            # 其他未预期异常，包装为系统异常
            logger.error(f"下载过程中发生未预期错误: {file.get('url', 'unknown')} - {e}")
            wrapped_error = WrappedSystemException(e, f"下载文件时发生系统错误: {e}")
            self._callback_group.error(wrapped_error)
            raise wrapped_error

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
    
    作为多个 FileDownloader 的聚合器，将单个文件下载的回调信号
    重新封装为整体并发下载的回调信号，提供给上层使用。
    
    支持自动重试机制：当单个任务失败时，会自动重试指定次数，
    重试时会清零该任务的进度并重新开始下载。
    
    主要职责：
    1. 管理多个文件的并发下载
    2. 聚合各个文件的下载状态
    3. 计算总体进度和速度
    4. 向上层提供统一的并发下载回调
    5. 处理下载失败的自动重试
    """
    
    def __init__(self,
                 callback_group: IDownloadMultiThread,
                 tasks: List[DownloadFile],
                 concurrent_count: Optional[int] = None,
                 max_retries: int = 3,
                 ):
        """
        Args:
            callback_group: 上层回调组，接收聚合后的并发下载事件
            tasks: 下载任务列表
            concurrent_count: 并发数量，如果为None则自动计算最优值
            max_retries: 单个任务的最大重试次数，默认为3次
        """
        self._callback_group = callback_group
        self._tasks = tasks
        self._max_retries = max_retries

        # 智能计算并发数量
        if concurrent_count is None:
            self._concurrent_count = self._calculate_optimal_concurrency()
        else:
            self._concurrent_count = concurrent_count
        
        # 任务状态跟踪 - 简单明了
        self._task_progress: Dict[str, int] = {}        # 各任务进度 0-100
        self._task_downloaded: Dict[str, int] = {}      # 各任务已下载字节
        self._task_total: Dict[str, int] = {}           # 各任务总字节数
        self._task_speeds: Dict[str, int] = {}          # 各任务下载速度
        
        # 重试机制状态跟踪
        self._task_retry_count: Dict[str, int] = {}     # 各任务已重试次数
        self._task_failed_permanently: Dict[str, bool] = {}  # 各任务是否永久失败
        
        self._is_cancelled = False
        self._completed_tasks = 0
        self._failed_tasks = 0

    def _calculate_optimal_concurrency(self) -> int:
        """计算最优并发数量

        根据任务数量、文件大小等因素智能计算最优的并发数量。

        Returns:
            最优并发数量
        """
        task_count = len(self._tasks)

        # 分析文件大小分布
        total_size = 0
        small_files = 0  # 小于1MB的文件
        large_files = 0  # 大于10MB的文件

        for task in self._tasks:
            size = task.get("size", 0)
            total_size += size

            if size > 0:
                if size < 1024 * 1024:  # 小于1MB
                    small_files += 1
                elif size > 10 * 1024 * 1024:  # 大于10MB
                    large_files += 1

        # 计算平均文件大小
        avg_size = total_size / task_count if task_count > 0 else 0

        # 根据文件特征计算并发数
        if small_files > task_count * 0.8:  # 80%以上是小文件
            # 小文件场景：可以使用更高的并发数
            base_concurrency = min(20, task_count)
            # 但要考虑总任务数，避免过度并发
            if task_count > 100:
                concurrency = min(30, task_count // 3)
            else:
                concurrency = base_concurrency
        elif large_files > task_count * 0.5:  # 50%以上是大文件
            # 大文件场景：使用较低的并发数避免带宽竞争
            concurrency = min(5, task_count)
        else:
            # 混合场景：使用中等并发数
            concurrency = min(10, task_count)

        # 确保并发数在合理范围内
        concurrency = max(1, min(concurrency, 50))

        logger.info(f"智能计算并发数: {concurrency} (任务总数: {task_count}, "
                   f"小文件: {small_files}, 大文件: {large_files}, 平均大小: {avg_size/1024:.1f}KB)")

        return concurrency

    async def schedule(self) -> None:
        """
        调度执行所有下载任务
        """
        logger.info(f"开始并发下载任务，共 {len(self._tasks)} 个文件，并发数: {self._concurrent_count}")
        self._callback_group.start()
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(self._concurrent_count)
        
        # 创建下载任务
        download_tasks = []
        for i, task in enumerate(self._tasks):
            task_id = self._get_task_display_name(i, task)
            logger.debug(f"创建下载任务: {task_id}")
            download_task = asyncio.create_task(
                self._download_single_task(semaphore, task_id, task)
            )
            download_tasks.append(download_task)
        
        # 启动速度监控
        speed_monitor = asyncio.create_task(self._monitor_speed())
        
        try:
            # 等待所有任务完成
            results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # 检查是否有任务抛出了异常
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    task_id = self._get_task_display_name(i, self._tasks[i])
                    logger.warning(f"任务 {task_id} 执行时发生异常: {result}")
            
            # 检查最终状态 - 考虑重试机制
            permanently_failed_count = sum(1 for failed in self._task_failed_permanently.values() if failed)
            
            if permanently_failed_count > 0:
                failed_tasks = [task_id for task_id, failed in self._task_failed_permanently.items() if failed]
                error_msg = f"有 {permanently_failed_count} 个任务在重试{self._max_retries}次后仍然失败: {', '.join(failed_tasks)}"
                logger.error(f"并发下载失败: {error_msg}")
                
                # 创建聚合错误
                aggregate_error = DownloadException(error_msg, CoreErrorCodes.DOWNLOAD_GENERAL_ERROR)
                self._callback_group.error(aggregate_error)
            else:
                logger.info(f"所有下载任务完成，共 {len(self._tasks)} 个文件")
                self._callback_group.finished()
                
        except Exception as e:
            logger.error(f"下载调度过程中发生未预期错误: {e}")
            wrapped_error = WrappedSystemException(e, f"下载任务调度失败: {e}")
            self._callback_group.error(wrapped_error)
            raise wrapped_error
                
        finally:
            speed_monitor.cancel()
            try:
                await speed_monitor
            except asyncio.CancelledError:
                pass

            # 清理连接池（可选，在长时间不使用时）
            # 注意：这里不主动关闭连接池，因为可能还有其他下载任务在使用
            # 连接池会在程序退出时自动清理

    def _get_task_display_name(self, index: int, task: DownloadFile) -> str:
        """生成任务显示名称：task_id + 文件名"""
        filename = task.get("path", task["url"]).split("/")[-1]
        return f"task_{index}_{filename}"

    async def _download_single_task(self, semaphore: asyncio.Semaphore, 
                                   task_id: str, task: DownloadFile) -> None:
        """下载单个任务（支持重试）"""
        async with semaphore:
            if self._is_cancelled:
                logger.debug(f"任务 {task_id} 被取消，跳过执行")
                return
            
            # 初始化重试计数
            if task_id not in self._task_retry_count:
                self._task_retry_count[task_id] = 0
                self._task_failed_permanently[task_id] = False
            
            logger.debug(f"开始执行任务: {task_id} ({task.get('url', 'unknown url')})")
            
            while self._task_retry_count[task_id] <= self._max_retries:
                if self._is_cancelled:
                    logger.debug(f"任务 {task_id} 在重试过程中被取消")
                    return
                    
                try:
                    # 如果是重试，清零进度数据
                    if self._task_retry_count[task_id] > 0:
                        logger.info(f"重置任务 {task_id} 的进度数据")
                        self._clear_task_progress(task_id)
                    
                    # 创建单任务下载器
                    downloader = self._create_task_downloader(task_id)
                    await downloader.download_file(task)
                    
                    # 下载成功
                    if self._task_retry_count[task_id] > 0:
                        logger.info(f"任务 {task_id} 重试后成功完成")
                    else:
                        logger.debug(f"任务 {task_id} 首次尝试成功完成")
                    return
                    
                except (DownloadException, NetworkException) as e:
                    self._task_retry_count[task_id] += 1
                    
                    if self._task_retry_count[task_id] <= self._max_retries:
                        # 还有重试机会，等待一段时间后重试
                        retry_delay = min(2 ** (self._task_retry_count[task_id] - 1), 10)  # 指数退避，最大10秒
                        logger.warning(
                            f"任务 {task_id} 失败 ({e.code}): {e.message}，"
                            f"第{self._task_retry_count[task_id]}次重试 (共{self._max_retries}次)，"
                            f"{retry_delay}秒后重试"
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        # 重试次数用完，标记为永久失败
                        self._task_failed_permanently[task_id] = True
                        self._failed_tasks += 1
                        logger.error(
                            f"任务 {task_id} 永久失败 ({e.code}): {e.message}，"
                            f"已重试{self._max_retries}次"
                        )
                        
                        # 如果是第一个永久失败的任务，通知上层
                        if self._failed_tasks == 1:
                            first_failure_error = DownloadException(
                                f"首个下载任务失败: {task_id} - {e.message}",
                                e.code
                            )
                            self._callback_group.error(first_failure_error)
                        break
                        
                except Exception as e:
                    # 非预期异常，也进行重试
                    self._task_retry_count[task_id] += 1
                    
                    if self._task_retry_count[task_id] <= self._max_retries:
                        retry_delay = min(2 ** (self._task_retry_count[task_id] - 1), 10)
                        logger.warning(
                            f"任务 {task_id} 发生未预期错误: {e}，"
                            f"第{self._task_retry_count[task_id]}次重试 (共{self._max_retries}次)，"
                            f"{retry_delay}秒后重试"
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        # 重试次数用完
                        self._task_failed_permanently[task_id] = True
                        self._failed_tasks += 1
                        
                        wrapped_error = WrappedSystemException(e, f"任务 {task_id} 发生系统错误")
                        logger.error(f"任务 {task_id} 永久失败: {wrapped_error.message}，已重试{self._max_retries}次")
                        
                        if self._failed_tasks == 1:
                            self._callback_group.error(wrapped_error)
                        break

    def _clear_task_progress(self, task_id: str) -> None:
        """清零任务进度数据（用于重试）"""
        old_progress = self._task_progress.get(task_id, 0)
        old_downloaded = self._task_downloaded.get(task_id, 0)
        
        self._task_progress[task_id] = 0
        self._task_downloaded[task_id] = 0
        self._task_speeds[task_id] = 0
        # 注意：不清零 _task_total，因为文件大小不会变
        
        logger.debug(f"清零任务 {task_id} 进度: {old_progress}% -> 0%, {old_downloaded} bytes -> 0 bytes")
        
        # 更新回调状态
        self._callback_group.tasks_progress(self._task_progress.copy())
        self._update_size_info()
        self._update_overall_progress()

    def _create_task_downloader(self, task_id: str) -> FileDownloader:
        """为单个任务创建下载器"""
        
        def on_start():
            logger.debug(f"任务 {task_id} 下载器启动")
            
        def on_progress(progress: int):
            self._task_progress[task_id] = progress
            self._callback_group.tasks_progress(self._task_progress.copy())
            self._update_overall_progress()
            
        def on_bytes_downloaded(downloaded: int, total: int):
            self._task_downloaded[task_id] = downloaded
            self._task_total[task_id] = total
            
            # 更新总体状态
            self._update_size_info()
            self._update_overall_progress()
            
        def on_speed(speed: int):
            self._task_speeds[task_id] = speed
            
        def on_finished():
            self._completed_tasks += 1
            logger.debug(f"任务 {task_id} 下载器完成，总完成数: {self._completed_tasks}")
            
        def on_error(error: Exception):
            logger.debug(f"任务 {task_id} 下载器报告错误: {error}")
            
        return FileDownloader(Callbacks(
            start=on_start,
            progress=on_progress,
            bytes_downloaded=on_bytes_downloaded,
            speed=on_speed,
            finished=on_finished,
            error=on_error
        ))

    def _update_size_info(self):
        """更新大小信息 - 只计算已获取到大小的任务"""
        total_size = sum(size for size in self._task_total.values() if size > 0)
        total_downloaded = sum(
            self._task_downloaded.get(task_id, 0) 
            for task_id, total in self._task_total.items() 
            if total > 0
        )
        
        if total_size > 0:
            self._callback_group.size(total_size)
            self._callback_group.downloaded_size(total_downloaded)

    def _update_overall_progress(self):
        """更新总体进度 - 基于已获取大小的任务计算"""
        # 只计算已知大小的任务
        known_size_tasks = {k: v for k, v in self._task_total.items() if v > 0}
        
        if not known_size_tasks:
            return
            
        total_bytes = sum(known_size_tasks.values())
        downloaded_bytes = sum(
            self._task_downloaded.get(task_id, 0) 
            for task_id in known_size_tasks.keys()
        )
        
        if total_bytes > 0:
            progress = int((downloaded_bytes / total_bytes) * 100)
            self._callback_group.progress(progress)

    async def _monitor_speed(self):
        """监控总体下载速度"""
        logger.debug("启动下载速度监控")
        while not self._is_cancelled:
            try:
                total_speed = sum(self._task_speeds.values())
                self._callback_group.speed(total_speed)
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                logger.debug("下载速度监控被取消")
                break
        logger.debug("下载速度监控结束")

    def cancel(self):
        """取消所有下载"""
        logger.info("收到取消信号，正在停止所有下载任务")
        self._is_cancelled = True


class BatchDownloadManager(DownloadManager):
    """批量下载管理器

    专门针对大量小文件下载场景优化的下载管理器。
    通过批量处理、连接复用等技术提升下载性能。
    """

    def __init__(self,
                 callback_group: IDownloadMultiThread,
                 tasks: List[DownloadFile],
                 concurrent_count: Optional[int] = None,
                 max_retries: int = 3,
                 batch_size: int = 10):
        """
        Args:
            callback_group: 上层回调组，接收聚合后的并发下载事件
            tasks: 下载任务列表
            concurrent_count: 并发数量，如果为None则自动计算最优值
            max_retries: 单个任务的最大重试次数，默认为3次
            batch_size: 批处理大小，每批处理的文件数量
        """
        super().__init__(callback_group, tasks, concurrent_count, max_retries)
        self.batch_size = batch_size

        # 按主机分组任务，优化连接复用
        self._tasks_by_host = self._group_tasks_by_host()

    def _group_tasks_by_host(self) -> Dict[str, List[DownloadFile]]:
        """按主机分组任务

        将下载任务按目标主机分组，便于连接复用。

        Returns:
            按主机分组的任务字典
        """
        tasks_by_host = {}

        for task in self._tasks:
            url = task.get("url", "")
            if url:
                parsed = urlparse(url)
                host_key = f"{parsed.scheme}://{parsed.netloc}"

                if host_key not in tasks_by_host:
                    tasks_by_host[host_key] = []
                tasks_by_host[host_key].append(task)

        logger.info(f"任务按主机分组完成，共 {len(tasks_by_host)} 个主机")
        for host, host_tasks in tasks_by_host.items():
            logger.debug(f"主机 {host}: {len(host_tasks)} 个任务")

        return tasks_by_host

    async def schedule(self) -> None:
        """
        调度执行所有下载任务（批量优化版本）
        """
        logger.info(f"开始批量下载任务，共 {len(self._tasks)} 个文件，并发数: {self._concurrent_count}")
        self._callback_group.start()

        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(self._concurrent_count)

        # 按主机分批创建下载任务
        download_tasks = []
        task_index = 0

        for host, host_tasks in self._tasks_by_host.items():
            logger.debug(f"为主机 {host} 创建 {len(host_tasks)} 个下载任务")

            # 将同一主机的任务分批处理
            for i in range(0, len(host_tasks), self.batch_size):
                batch = host_tasks[i:i + self.batch_size]

                for task in batch:
                    task_id = self._get_task_display_name(task_index, task)
                    logger.debug(f"创建下载任务: {task_id}")
                    download_task = asyncio.create_task(
                        self._download_single_task(semaphore, task_id, task)
                    )
                    download_tasks.append(download_task)
                    task_index += 1

        # 启动速度监控
        speed_monitor = asyncio.create_task(self._monitor_speed())

        try:
            # 等待所有任务完成
            results = await asyncio.gather(*download_tasks, return_exceptions=True)

            # 检查是否有任务抛出了异常
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    task_id = self._get_task_display_name(i, self._tasks[i])
                    logger.warning(f"任务 {task_id} 执行时发生异常: {result}")

            # 检查最终状态 - 考虑重试机制
            permanently_failed_count = sum(1 for failed in self._task_failed_permanently.values() if failed)

            if permanently_failed_count > 0:
                failed_tasks = [task_id for task_id, failed in self._task_failed_permanently.items() if failed]
                error_msg = f"有 {permanently_failed_count} 个任务在重试{self._max_retries}次后仍然失败: {', '.join(failed_tasks)}"
                logger.error(f"批量下载失败: {error_msg}")

                # 创建聚合错误
                aggregate_error = DownloadException(error_msg, CoreErrorCodes.DOWNLOAD_GENERAL_ERROR)
                self._callback_group.error(aggregate_error)
            else:
                logger.info(f"所有批量下载任务完成，共 {len(self._tasks)} 个文件")
                self._callback_group.finished()

        except Exception as e:
            logger.error(f"批量下载调度过程中发生未预期错误: {e}")
            wrapped_error = WrappedSystemException(e, f"批量下载任务调度失败: {e}")
            self._callback_group.error(wrapped_error)
            raise wrapped_error

        finally:
            speed_monitor.cancel()
            try:
                await speed_monitor
            except asyncio.CancelledError:
                pass
