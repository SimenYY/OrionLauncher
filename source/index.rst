.. OrionLauncher documentation master file, created by
   sphinx-quickstart on Sat Jul  5 23:55:43 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

OrionLauncher 文档
==================

OrionLauncher 是一个现代化的 Minecraft 启动器，采用分层架构设计。

架构概述
========

项目采用三层架构：

* **View层** - 基于PySide6的用户界面
* **Controller层** - 抽象化前后端接口的控制器
* **Core层** - 核心业务逻辑和功能模块

设计原则
========

1. **分层清晰**: View层（PySide6），Controller层（抽象化前后端接口），Core层（主要功能与逻辑模块）
2. **单一职责**: Controller层作为GUI与功能模块交互的唯一桥梁
3. **异步优先**: 所有接口采用单线程异步设计，适应IO密集型任务
4. **模块化**: Core层细分为Model和Service等子层，便于维护和扩展

文档内容
========

.. toctree::
   :maxdepth: 2
   :caption: 内容目录:

   api/index

索引和表格
==========

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

