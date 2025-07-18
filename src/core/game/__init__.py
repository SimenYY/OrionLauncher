"""游戏管理模块。

该模块提供Minecraft游戏相关的管理功能，包括本地版本检测、
游戏配置管理等功能。

主要功能:
    - 本地已安装版本的检测和管理
    - 版本配置文件的解析
    - 游戏目录结构的管理

子模块:
    local_versions: 本地版本管理模块

Classes:
    LocalVersionInfo: 本地版本信息类

Functions:
    get_local_minecraft_versions: 获取本地版本列表
    get_local_minecraft_versions_dict: 获取本地版本列表（字典格式）
    find_version_by_id: 根据ID查找版本
    get_version_types_summary: 获取版本类型统计
"""

from .local_versions import (
    LocalVersionInfo,
    get_local_minecraft_versions,
    get_local_minecraft_versions_dict,
    find_version_by_id,
    get_version_types_summary
)

__all__ = [
    "LocalVersionInfo",
    "get_local_minecraft_versions",
    "get_local_minecraft_versions_dict", 
    "find_version_by_id",
    "get_version_types_summary"
]
