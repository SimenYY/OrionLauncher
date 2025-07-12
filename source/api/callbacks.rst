回调系统 (Utils.callbacks)
===============================

.. currentmodule:: Utils.callbacks

回调系统模块提供了一套灵活的回调机制，用于处理异步操作的事件通知和状态更新。

模块概述
--------

该模块包含以下主要组件：

- :class:`Callbacks` - 基础回调容器类
- :class:`CallbackGroup` - 回调组管理类  
- :class:`InstallationCallbackGroup` - 类型化的安装器回调组
- 多个协议接口定义不同场景下的回调签名

基础回调类
----------

.. autoclass:: Callbacks
   :members:
   :undoc-members:
   :show-inheritance:

   基础回调容器类，用于存储和管理一组回调函数。

   .. method:: __init__(**kwargs)

      初始化回调容器。

      :param kwargs: 命名回调函数，键为回调名称，值为可调用对象

   .. method:: __getitem__(key: str) -> Callable[[Any], Any]

      通过键获取回调函数。

      :param key: 回调函数名称
      :return: 对应的回调函数，如果不存在则返回空操作函数

   .. method:: __getattr__(name: str) -> Callable[[Any], Any]

      通过属性访问回调函数。

      :param name: 回调函数名称  
      :return: 对应的回调函数，如果不存在则返回空操作函数

回调组管理
----------

.. autoclass:: CallbackGroup
   :members:
   :undoc-members:
   :show-inheritance:

   回调组管理类，用于组织多个相关的回调容器。

   .. method:: __init__(**kwargs)

      初始化回调组。

      :param kwargs: 命名的回调容器，键为组名，值为Callbacks实例

   .. method:: __getitem__(key: str) -> Callbacks

      通过键获取回调容器。

      :param key: 回调组名称
      :return: 对应的回调容器，如果不存在则返回空回调容器

   .. method:: __getattr__(name: str) -> Callbacks

      通过属性访问回调容器。

      :param name: 回调组名称
      :return: 对应的回调容器，如果不存在则返回空回调容器

类型化回调组
------------

.. autoclass:: InstallationCallbackGroup
   :members:
   :undoc-members:
   :show-inheritance:

   专门用于安装过程的类型化回调组，提供类型提示支持。

协议接口
--------

下载相关协议
~~~~~~~~~~~~

.. autoclass:: IDownloadSingle
   :members:
   :undoc-members:

   单一下载任务的回调协议接口。

   .. method:: start()

      任务开始信号。

   .. method:: progress(progress: int)

      任务进度更新。

      :param progress: 进度百分比 (0-100)

   .. method:: bytes_downloaded(downloaded: int, total: int)

      字节级进度更新。

      :param downloaded: 已下载字节数
      :param total: 总字节数

   .. method:: speed(speed: int)

      下载速度更新。

      :param speed: 下载速度，单位：字节/秒

   .. method:: finished()

      任务完成信号。

   .. method:: error(error: Exception)

      任务错误信号。

      :param error: 发生的异常

.. autoclass:: IDownloadMultiThread
   :members:
   :undoc-members:

   多线程下载任务的回调协议接口。

   .. method:: start()

      任务开始信号。

   .. method:: tasks_progress(progress: Dict[str, int])

      各任务进度更新。

      :param progress: 任务名称到进度百分比的映射

   .. method:: size(size: int)

      任务数据大小。

      :param size: 数据大小，单位：字节

   .. method:: downloaded_size(task: str, size: int)

      任务已下载大小。

      :param task: 任务名称
      :param size: 已下载大小，单位：字节

   .. method:: speed(speed: int)

      下载速度更新。

      :param speed: 下载速度，单位：字节/秒

   .. method:: progress(progress: int)

      总体进度更新。

      :param progress: 总进度百分比 (0-100)

   .. method:: finished(task: str)

      单个任务完成信号。

      :param task: 完成的任务名称

   .. method:: error(task: str, error: Exception)

      任务错误信号。

      :param task: 出错的任务名称
      :param error: 发生的异常

安装相关协议
~~~~~~~~~~~~

.. autoclass:: IInstallGame
   :members:
   :undoc-members:

   游戏安装任务的回调协议接口。

   .. method:: start()

      安装开始信号。

   .. method:: finished()

      安装完成信号。

   .. method:: error(error: Exception)

      安装错误信号。

      :param error: 发生的异常

.. autoclass:: IVerifyGameFile
   :members:
   :undoc-members:

   游戏文件验证任务的回调协议接口。

   .. method:: start()

      验证开始信号。

   .. method:: finished()

      验证完成信号。

   .. method:: error(error: Exception)

      验证错误信号。

      :param error: 发生的异常

使用示例
--------

基础使用::

    from Utils.callbacks import Callbacks, CallbackGroup

    # 创建回调函数
    def on_start():
        print("任务开始")

    def on_progress(progress):
        print(f"进度: {progress}%")

    # 创建回调容器
    callbacks = Callbacks(
        start=on_start,
        progress=on_progress
    )

    # 调用回调
    callbacks.start()  # 输出: 任务开始
    callbacks.progress(50)  # 输出: 进度: 50%

回调组使用::

    # 创建回调组
    download_callbacks = Callbacks(
        start=lambda: print("下载开始"),
        progress=lambda p: print(f"下载进度: {p}%")
    )

    install_callbacks = Callbacks(
        start=lambda: print("安装开始"),
        finished=lambda: print("安装完成")
    )

    callback_group = CallbackGroup(
        download=download_callbacks,
        install=install_callbacks
    )

    # 使用回调组
    callback_group.download.start()  # 输出: 下载开始
    callback_group.install.finished()  # 输出: 安装完成

注意事项
--------

- 当访问不存在的回调时，会返回一个空操作函数而不是抛出异常
- 在DEBUG日志级别下，调用空回调时会记录调用堆栈信息，便于调试
- 协议接口使用了Python的Protocol类型，提供静态类型检查支持
- InstallationCallbackGroup提供了类型化的回调访问，增强IDE支持 