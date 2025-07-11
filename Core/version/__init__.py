"""版本管理模块。

该模块提供Minecraft版本信息的获取、解析和缓存功能。

主要功能:
    - Minecraft版本信息的获取和解析
    - 多镜像源支持（官方源、BMCLAPI）
    - 版本过滤和查询
    - 缓存机制

Classes:
    VersionRequestOfficial: 官方API请求器
    VersionRequestBMCLAPI: BMCLAPI镜像请求器
    MinecraftVersion: 版本信息解析器

Functions:
    load_versions: 加载版本信息
    get_versions: 获取指定类型的版本信息

Variables:
    mirror: 镜像源映射字典
"""

from .minecraft_version import (MinecraftVersion, VersionRequestBMCLAPI,
                                VersionRequestOfficial, get_versions,
                                load_versions, mirror)

__all__ = [
    "VersionRequestOfficial",
    "VersionRequestBMCLAPI",
    "MinecraftVersion",
    "load_versions",
    "get_versions",
    "mirror",
]
