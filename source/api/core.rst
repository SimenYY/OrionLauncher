Core 模块
===========

Core层包含主要的业务逻辑和功能实现，包括网络请求、文件管理、用户管理、版本管理等核心功能。

请求模块
--------

下载器
~~~~~~

.. automodule:: Core.request.downloader
   :members:
   :undoc-members:
   :show-inheritance:

仓库模块
--------

路径管理
~~~~~~~~

.. automodule:: Core.Repository.Path
   :members:
   :undoc-members:
   :show-inheritance:

版本模块
--------

Minecraft版本管理
~~~~~~~~~~~~~~~~~

.. automodule:: Core.version.minecraft_version
   :members:
   :undoc-members:
   :show-inheritance:

用户模块
--------

.. automodule:: Core.user
   :members:
   :undoc-members:
   :show-inheritance:

安装模块
--------

Core.Installation 模块提供了一个兼容 InstallationCallbackGroup 的 Model 层安装调度工具，
实现了与 minecraft_launcher_lib 的解耦，支持多种安装任务的调度和管理。

安装调度器
~~~~~~~~~~

.. automodule:: Core.Installation.scheduler
   :members:
   :undoc-members:
   :show-inheritance:

安装适配器
~~~~~~~~~~

.. automodule:: Core.Installation.adapter
   :members:
   :undoc-members:
   :show-inheritance:

安装任务
~~~~~~~~

.. automodule:: Core.Installation.tasks
   :members:
   :undoc-members:
   :show-inheritance:

回调转换器
~~~~~~~~~~

.. automodule:: Core.Installation.callback_converter
   :members:
   :undoc-members:
   :show-inheritance: