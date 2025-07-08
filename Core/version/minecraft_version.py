"""Minecraft版本管理模块。

该模块提供Minecraft版本信息的获取、解析和缓存功能，支持多镜像源。

主要功能:
    - 从官方API或BMCLAPI获取版本清单
    - 解析和存储版本信息
    - 提供版本过滤和查询功能
    - 内置缓存机制提升性能

Example:
    获取最新的正式版本::

        import asyncio
        from Core.version.minecraft_version import get_versions

        async def main():
            versions = await get_versions(["release"])
            print(f"最新正式版: {versions['latest']}")

        asyncio.run(main())
"""
from typing import Callable, Dict, List, Union, Any, Optional
from Utils.request import request_json
from Utils.tools import empty
from Core.Repository import config, persistence

import time

class VersionRequestOfficial:
    """Minecraft官方版本API请求器。
    
    用于从Mojang官方API获取Minecraft版本清单信息。
    
    Attributes:
        host (str): API主机地址
        path (str): API路径
    """
    
    def __init__(self) -> None:
        """初始化官方API请求器。"""
        self.host: str = "https://launchermeta.mojang.com"
        self.path: str = "/mc/game/version_manifest.json"
    
    async def request(self, finnished: Optional[Callable[[Dict[str, Any]], None]] = empty, 
                     error: Optional[Callable[[str], None]] = empty) -> Union[Dict[str, Any], List[Any], None]:
        """发送版本清单请求。
        
        Args:
            finnished: 请求成功时的回调函数，接收响应数据作为参数
            error: 请求失败时的回调函数，接收错误信息作为参数
            
        Returns:
            从API获取的版本清单数据，通常为包含版本信息的字典
            
        Raises:
            ApiException: API调用失败时抛出
            NetworkException: 网络请求失败时抛出
            WrappedSystemException: 其他系统异常时抛出
        """
        return await request_json(self.host + self.path, finnished=finnished, error=error)

class VersionRequestBMCLAPI(VersionRequestOfficial):
    """BMCLAPI版本请求器。
    
    继承自VersionRequestOfficial，使用BMCLAPI镜像源获取版本信息。
    BMCLAPI提供了Mojang官方API的国内镜像，可以提高访问速度。
    """
    
    def __init__(self) -> None:
        """初始化BMCLAPI请求器。"""
        super().__init__()
        self.host: str = "https://bmclapi2.bangbang93.com"

#: 镜像源映射字典，包含所有可用的版本API镜像源
mirror: Dict[str, VersionRequestOfficial] = {
    "Official": VersionRequestOfficial(),
    "BMCLAPI": VersionRequestBMCLAPI(),
}

class MinecraftVersion:
    """Minecraft版本信息解析器。
    
    解析从API获取的版本清单数据，提供结构化的版本信息访问接口。
    
    Attributes:
        source (Dict[str, Any]): 原始版本清单数据
        latest (Dict[str, str]): 最新版本信息，包含release和snapshot
        versions (Dict[str, Dict[str, Union[str, int]]]): 所有版本的详细信息字典
    
    Example:
        解析版本数据::
        
            data = {"latest": {"release": "1.21", "snapshot": "24w44a"}, "versions": [...]}
            version = MinecraftVersion(data)
            print(f"最新正式版: {version.latest['release']}")
            print(f"版本总数: {len(version.versions)}")
    """
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """初始化版本解析器。
        
        Args:
            data: 从API获取的原始版本清单数据，应包含latest和versions字段
        """
        self.source: Dict[str, Any] = data
        self.latest: Dict[str, str] = {
            "release": "",
            "snapshot": "",
        }
        self.versions: Dict[str, Dict[str, Union[str, int]]] = {}
        self.load()

    def load(self) -> None:
        """解析版本信息。
        
        从原始数据中提取最新版本信息和所有版本详情，
        构建便于访问的数据结构。
        """
        self.latest["release"] = self.source["latest"]["release"]
        self.latest["snapshot"] = self.source["latest"]["snapshot"]
        for version in self.source["versions"]:
            self.versions[version["id"]] = version

async def load_versions(finnished: Optional[Callable[[Dict[str, Any]], None]] = empty, 
                       error: Optional[Callable[[str], None]] = empty) -> MinecraftVersion:
    """加载Minecraft版本信息。
    
    从配置的镜像源获取最新的版本清单数据，解析后存储到持久化缓存中。
    该函数会自动选择配置的镜像源，如果镜像源不存在则回退到官方源。
    
    Args:
        finnished: 请求成功时的回调函数，接收响应数据作为参数
        error: 请求失败时的回调函数，接收错误信息作为参数
        
    Returns:
        解析后的MinecraftVersion实例，包含完整的版本信息
        
    Raises:
        ApiException: API调用失败时抛出
        NetworkException: 网络请求失败时抛出
        WrappedSystemException: 其他系统异常时抛出
        
    Note:
        该函数会更新persistence中的版本缓存和更新时间戳。
    """
    _mirror_config: str = config.get("api.mirror", "Official")
    API: VersionRequestOfficial = mirror.get(_mirror_config, mirror["Official"])
    result: Union[Dict[str, Any], List[Any], None] = await API.request(finnished=finnished, error=error)
    version_manifest: MinecraftVersion = MinecraftVersion(result)
    persistence["minecraft.version_manifest"] = version_manifest
    persistence["minecraft.version_manifest.update_time"] = time.time()
    return version_manifest

async def get_versions(types: List[str] = None, 
                      finnished: Optional[Callable[[Dict[str, Any]], None]] = empty, 
                      error: Optional[Callable[[str], None]] = empty) -> Dict[str, Union[str, Dict[str, Dict[str, Union[str, int]]]]]:
    """获取指定类型的Minecraft版本信息。
    
    根据指定的版本类型过滤版本列表，支持缓存机制以提高性能。
    如果缓存过期（超过600秒）或不存在，会自动重新加载版本数据。
    
    Args:
        types: 要获取的版本类型列表，默认为["release", "snapshot", "old_beta", "old_alpha"]。
               可选值包括:
               - "release": 正式版
               - "snapshot": 快照版
               - "old_beta": 旧Beta版
               - "old_alpha": 旧Alpha版
        finnished: 请求成功时的回调函数，接收响应数据作为参数
        error: 请求失败时的回调函数，接收错误信息作为参数
        
    Returns:
        包含版本信息的字典，结构如下:
        
        - "latest" (str): 最新版本ID，优先返回release，其次snapshot
        - "versions" (Dict[str, Dict[str, Union[str, int]]]): 过滤后的版本详情字典
        
    Raises:
        ApiException: API调用失败时抛出
        NetworkException: 网络请求失败时抛出
        WrappedSystemException: 其他系统异常时抛出
        
    Example:
        获取正式版本::
        
            versions = await get_versions(["release"])
            print(f"最新正式版: {versions['latest']}")
            for version_id, version_info in versions['versions'].items():
                print(f"版本: {version_id}, 类型: {version_info['type']}")
                
    Note:
        - 缓存有效期为600秒（10分钟）
        - 版本数据存储在persistence["minecraft.version_manifest"]中
        - latest字段优先级：release > snapshot
    """
    if types is None:
        types = ["release", "snapshot", "old_beta", "old_alpha"]
        
    # 检查缓存，过期时间 600 秒
    if not persistence["minecraft.version_manifest"] or (time.time() - persistence.get("minecraft.version_manifest.update_time", 0) > 600):
        await load_versions(finnished=finnished, error=error)
    
    result: Dict[str, Union[str, Dict[str, Dict[str, Union[str, int]]]]] = {
        "latest": "",
        "versions": {}
    }
    
    for _id, _data in persistence["minecraft.version_manifest"].versions.items():
        if _data.get("type") in types:
            result["versions"][_id] = _data
            
    if "release" in types:
        result["latest"] = persistence["minecraft.version_manifest"].latest["release"]
    elif "snapshot" in types:
        result["latest"] = persistence["minecraft.version_manifest"].latest["snapshot"]
    
    return result
