"""Core核心模块。

该模块包含OrionLauncher的核心业务逻辑和功能实现，包括：

- 请求模块：网络请求和下载功能
- 仓库模块：配置和路径管理
- 版本模块：Minecraft版本管理
- 用户模块：用户账户管理
- 安装模块：Minecraft安装调度和管理
- 游戏模块：本地游戏版本管理

子模块:
    Repository: 仓库管理模块
    request: 网络请求模块
    version: 版本管理模块
    user: 用户管理模块
    Installation: 安装调度模块
    game: 游戏管理模块
"""

from . import Repository, request, user, version, Installation, game

__all__ = ["Repository", "request", "version", "user", "Installation", "game"]
