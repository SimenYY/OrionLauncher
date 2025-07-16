Core 模块
===========

Core层包含OrionLauncher的核心业务逻辑和功能实现，采用模块化设计，包括：

- **仓库模块**: 配置管理、路径管理和常量定义
- **请求模块**: 网络请求和文件下载功能
- **版本模块**: Minecraft版本信息管理
- **用户模块**: 用户账户管理和认证
- **游戏模块**: 本地游戏版本管理和进程控制
- **安装模块**: Minecraft安装调度和管理
- **启动器库**: 内置的minecraft_launcher_lib

核心模块概述
------------

.. automodule:: Core
   :members:
   :undoc-members:
   :show-inheritance:

仓库模块 (Repository)
---------------------

仓库模块提供配置管理、路径管理等基础设施功能。

配置管理
~~~~~~~~

.. automodule:: Core.Repository.Config
   :members:
   :undoc-members:
   :show-inheritance:

仓库基础
~~~~~~~~

.. automodule:: Core.Repository
   :members:
   :undoc-members:
   :show-inheritance:

请求模块 (request)
------------------

请求模块提供网络请求和文件下载功能，包含多种优化的下载器实现。

该模块针对Minecraft的下载场景进行了特别优化，包括：

- **基础下载器**: 提供通用的异步文件下载功能
- **Minecraft专用下载器**: 针对Minecraft大量小文件下载场景优化
- **优化下载器**: 包含内存优化、连接池复用等高级功能
- **下载缓存**: 智能缓存机制，避免重复下载

基础下载器
~~~~~~~~~~

.. automodule:: Core.request.downloader
   :members:
   :undoc-members:
   :show-inheritance:

Minecraft专用下载器
~~~~~~~~~~~~~~~~~~~

.. automodule:: Core.request.minecraft_downloader
   :members:
   :undoc-members:
   :show-inheritance:

优化下载器
~~~~~~~~~~

.. automodule:: Core.request.optimized_downloader
   :members:
   :undoc-members:
   :show-inheritance:

下载缓存
~~~~~~~~

.. automodule:: Core.request.download_cache
   :members:
   :undoc-members:
   :show-inheritance:

请求模块基础
~~~~~~~~~~~~

.. automodule:: Core.request
   :members:
   :undoc-members:
   :show-inheritance:

版本模块 (version)
------------------

版本模块提供Minecraft版本信息的获取、解析和缓存功能。

Minecraft版本管理
~~~~~~~~~~~~~~~~~

.. automodule:: Core.version.minecraft_version
   :members:
   :undoc-members:
   :show-inheritance:

版本模块基础
~~~~~~~~~~~~

.. automodule:: Core.version
   :members:
   :undoc-members:
   :show-inheritance:

用户模块 (user)
---------------

用户模块提供用户账户管理和认证功能。

.. automodule:: Core.user
   :members:
   :undoc-members:
   :show-inheritance:

游戏模块 (game)
---------------

游戏模块提供本地游戏版本管理和游戏进程控制功能。

该模块负责管理已安装的Minecraft版本和游戏运行时的进程控制：

- **本地版本管理**: 扫描和管理本地已安装的Minecraft版本
- **游戏进程管理**: 启动和监控Minecraft游戏进程

本地版本管理
~~~~~~~~~~~~

.. automodule:: Core.game.local_versions
   :members:
   :undoc-members:
   :show-inheritance:

游戏进程管理
~~~~~~~~~~~~

.. automodule:: Core.game.daemon
   :members:
   :undoc-members:
   :show-inheritance:

游戏模块基础
~~~~~~~~~~~~

.. automodule:: Core.game
   :members:
   :undoc-members:
   :show-inheritance:

安装模块 (Installation)
-----------------------

Core.Installation 模块提供了一个兼容 InstallationCallbackGroup 的 Model 层安装调度工具，
实现了与 minecraft_launcher_lib 的解耦，支持多种安装任务的调度和管理。

该模块采用适配器模式和任务调度模式，提供了灵活的安装架构：

- **安装调度器**: 核心调度器，负责任务调度和状态管理
- **安装适配器**: 适配器接口，实现与底层库的解耦
- **安装任务**: 安装任务抽象类和具体实现
- **回调转换器**: 处理不同回调接口的转换

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

安装模块基础
~~~~~~~~~~~~

.. automodule:: Core.Installation
   :members:
   :undoc-members:
   :show-inheritance:

Minecraft启动器库 (minecraft_launcher_lib)
------------------------------------------

内置的minecraft_launcher_lib库，提供Minecraft启动和管理的底层功能。

.. note::
   这是一个内置的第三方库，提供Minecraft的安装、启动等底层功能。
   详细文档请参考 `minecraft-launcher-lib官方文档 <https://minecraft-launcher-lib.readthedocs.io/>`_。

.. automodule:: Core.minecraft_launcher_lib
   :members:
   :undoc-members:
   :show-inheritance: