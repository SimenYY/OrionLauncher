下载器模块 (Core.request.downloader)
=========================================

.. currentmodule:: Core.request.downloader

概述
----

下载器模块提供了强大的异步文件下载功能，支持并发下载、进度跟踪、错误重试和完整的回调机制。该模块遵循项目的标准异常处理体系，提供企业级的可靠性和可维护性。

主要特性
~~~~~~~~

* **异步下载**: 基于 `asyncio` 和 `httpx` 的高性能异步下载
* **并发控制**: 支持配置并发下载数量，充分利用网络带宽
* **进度跟踪**: 基于字节数的精确进度计算和实时速度监控
* **错误重试**: 指数退避重试机制，提高下载成功率
* **回调机制**: 完整的事件回调系统，支持灵活的状态处理
* **标准异常**: 使用项目统一的异常体系和错误代码
* **详细日志**: 分层日志记录，便于调试和监控

核心类
------

FileDownloader
~~~~~~~~~~~~~~

.. autoclass:: FileDownloader
   :members:
   :undoc-members:
   :show-inheritance:

   单文件异步下载器，负责下载单个文件并通过回调机制报告状态。

   **特性:**

   * 支持大文件分块下载 (512KB 块大小)
   * 实时进度和速度监控
   * 可取消的下载操作
   * 完整的错误处理和异常转换

   **使用示例:**

   .. code-block:: python

      from Core.request.downloader import FileDownloader
      from Utils.callbacks import Callbacks

      # 创建回调函数
      def on_progress(progress):
          print(f"下载进度: {progress}%")

      def on_speed(speed):
          print(f"下载速度: {speed/1024:.1f} KB/s")

      # 创建回调组
      callbacks = Callbacks(
          start=lambda: print("开始下载"),
          progress=on_progress,
          speed=on_speed,
          finished=lambda: print("下载完成"),
          error=lambda e: print(f"下载错误: {e}")
      )

      # 创建下载器
      downloader = FileDownloader(callbacks)

      # 执行下载
      file_info = {
          "url": "https://example.com/file.zip",
          "path": "./downloads/file.zip",
          "size": 1024000  # 可选
      }

      await downloader.download_file(file_info)

DownloadManager
~~~~~~~~~~~~~~~

.. autoclass:: DownloadManager
   :members:
   :undoc-members:
   :show-inheritance:

   并发下载管理器，负责调度和管理多个文件的并发下载。

   **特性:**

   * 可配置的并发下载数量
   * 基于字节数的精确总体进度计算
   * 自动重试机制，支持指数退避
   * 任务状态聚合和统一回调
   * 完整的错误处理和分类

   **使用示例:**

   .. code-block:: python

      from Core.request.downloader import DownloadManager
      from Utils.callbacks import Callbacks

      # 定义下载任务
      tasks = [
          {
              "url": "https://example.com/file1.zip",
              "path": "./downloads/file1.zip"
          },
          {
              "url": "https://example.com/file2.zip", 
              "path": "./downloads/file2.zip"
          }
      ]

      # 创建回调组
      callbacks = Callbacks(
          start=lambda: print("开始并发下载"),
          tasks_progress=lambda p: print(f"任务进度: {p}"),
          progress=lambda p: print(f"总进度: {p}%"),
          finished=lambda: print("全部下载完成"),
          error=lambda e: print(f"下载失败: {e}")
      )

      # 创建下载管理器
      manager = DownloadManager(
          callback_group=callbacks,
          tasks=tasks,
          concurrent_count=3,  # 并发数
          max_retries=2        # 重试次数
      )

      # 执行下载
      await manager.schedule()

回调接口
--------

IDownloadSingle
~~~~~~~~~~~~~~~

.. autoclass:: Utils.callbacks.IDownloadSingle
   :members:
   :undoc-members:

   单文件下载回调接口，定义了单个下载任务的事件回调方法。

   **回调方法:**

   * ``start()``: 下载开始时调用
   * ``progress(progress: int)``: 进度更新时调用 (0-100)
   * ``bytes_downloaded(downloaded: int, total: int)``: 字节级进度更新
   * ``speed(speed: int)``: 速度更新时调用 (字节/秒)
   * ``finished()``: 下载完成时调用
   * ``error(error: Exception)``: 发生错误时调用

IDownloadMultiThread  
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Utils.callbacks.IDownloadMultiThread
   :members:
   :undoc-members:

   多线程下载回调接口，定义了并发下载任务的事件回调方法。

   **回调方法:**

   * ``start()``: 并发下载开始时调用
   * ``tasks_progress(progress: Dict[str, int])``: 各任务进度更新
   * ``size(size: int)``: 总文件大小确定时调用
   * ``downloaded_size(size: int)``: 总已下载字节数更新
   * ``speed(speed: int)``: 总下载速度更新 (字节/秒)
   * ``progress(progress: int)``: 总体进度更新 (0-100)
   * ``finished()``: 全部下载完成时调用
   * ``error(error: Exception)``: 发生错误时调用

异常处理
--------

下载器模块使用项目标准的异常体系，所有异常都包含明确的错误代码：

常见异常类型
~~~~~~~~~~~~

.. list-table:: 下载相关异常
   :widths: 20 15 65
   :header-rows: 1

   * - 异常类型
     - 错误代码
     - 描述
   * - ``DownloadException``
     - E11101
     - 通用下载错误
   * - ``DownloadException``
     - E11102
     - 文件未找到 (404)
   * - ``DownloadException``
     - E11103
     - 权限被拒绝 (403)
   * - ``DownloadException``
     - E11106
     - 下载被中断/取消
   * - ``NetworkException``
     - E11002
     - 网络连接错误
   * - ``NetworkException``
     - E11003
     - 网络超时
   * - ``FileSystemException``
     - E12102
     - 文件权限错误
   * - ``WrappedSystemException``
     - E90001
     - 系统级异常包装

异常处理示例
~~~~~~~~~~~~

.. code-block:: python

   from Utils.Exceptions import DownloadException, NetworkException
   from Utils.Exceptions.code import CoreErrorCodes

   try:
       await downloader.download_file(file_info)
   except DownloadException as e:
       if e.code == CoreErrorCodes.DOWNLOAD_FILE_NOT_FOUND:
           print("文件不存在，请检查 URL")
       elif e.code == CoreErrorCodes.DOWNLOAD_PERMISSION_DENIED:
           print("访问被拒绝，请检查权限")
       else:
           print(f"下载失败: {e}")
   except NetworkException as e:
       print(f"网络错误: {e}")

配置选项
--------

FileDownloader 配置
~~~~~~~~~~~~~~~~~~~

.. list-table:: FileDownloader 配置参数
   :widths: 20 15 15 50
   :header-rows: 1

   * - 参数
     - 类型
     - 默认值
     - 说明
   * - ``callback_group``
     - ``IDownloadSingle``
     - 必需
     - 回调接口实现
   * - 分块大小
     - ``int``
     - 512KB
     - 下载时的数据块大小 (固定)
   * - 超时时间
     - ``float``
     - 30.0秒
     - HTTP 请求超时 (固定)

DownloadManager 配置
~~~~~~~~~~~~~~~~~~~

.. list-table:: DownloadManager 配置参数
   :widths: 20 15 15 50
   :header-rows: 1

   * - 参数
     - 类型
     - 默认值
     - 说明
   * - ``callback_group``
     - ``IDownloadMultiThread``
     - 必需
     - 回调接口实现
   * - ``tasks``
     - ``List[DownloadFile]``
     - 必需
     - 下载任务列表
   * - ``concurrent_count``
     - ``int``
     - 5
     - 并发下载数量
   * - ``max_retries``
     - ``int``
     - 3
     - 单个任务最大重试次数

最佳实践
--------

性能优化
~~~~~~~~

1. **合理设置并发数**: 根据网络带宽和服务器能力调整 ``concurrent_count``
2. **文件大小预知**: 在 ``DownloadFile`` 中提供 ``size`` 字段以获得准确进度
3. **回调频率控制**: 在回调函数中控制 UI 更新频率，避免界面卡顿

错误处理
~~~~~~~~

1. **分类处理异常**: 根据错误代码采取不同的处理策略
2. **合理设置重试**: 根据网络环境调整 ``max_retries`` 参数
3. **监控日志**: 开启适当的日志级别以便调试

代码组织
~~~~~~~~

.. code-block:: python

   # 推荐的代码组织方式
   class MyDownloadHandler:
       def __init__(self):
           self.callbacks = self._create_callbacks()
           self.manager = DownloadManager(
               callback_group=self.callbacks,
               tasks=self.get_download_tasks(),
               concurrent_count=3,
               max_retries=2
           )
       
       def _create_callbacks(self):
           return Callbacks(
               start=self.on_start,
               progress=self.on_progress,
               finished=self.on_finished,
               error=self.on_error
           )
       
       def on_start(self):
           self.logger.info("开始下载")
       
       def on_progress(self, progress):
           self.update_progress_bar(progress)
       
       def on_finished(self):
           self.logger.info("下载完成")
           self.notify_user()
       
       def on_error(self, error):
           self.logger.error(f"下载失败: {error}")
           self.handle_download_error(error)

数据类型
--------

DownloadFile
~~~~~~~~~~~~

.. code-block:: python

   from typing import TypedDict, NotRequired

   class DownloadFile(TypedDict):
       url: str                    # 必需: 下载 URL
       path: NotRequired[str]      # 可选: 保存路径
       size: NotRequired[int]      # 可选: 文件大小 (字节)
       sha1: NotRequired[str]      # 可选: SHA1 校验和

日志配置
--------

推荐的日志配置：

.. code-block:: python

   import logging

   # 开发环境
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
   )

   # 生产环境
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
       handlers=[
           logging.FileHandler('downloader.log'),
           logging.StreamHandler()
       ]
   )

版本历史
--------

.. versionadded:: 1.0.0
   初始版本，包含基本的单文件下载功能

.. versionadded:: 1.1.0
   添加并发下载管理器和重试机制

.. versionadded:: 1.2.0
   集成项目标准异常体系和错误代码

.. versionadded:: 1.3.0
   完善回调接口和字节级进度跟踪

另请参阅
--------

* :doc:`../exceptions/index` - 异常处理系统
* :doc:`../callbacks/index` - 回调机制
* :doc:`../utils/types` - 数据类型定义
* :doc:`../../user_guide/downloading` - 下载功能用户指南 