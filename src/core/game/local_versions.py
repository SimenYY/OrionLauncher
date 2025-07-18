"""本地Minecraft版本管理模块。

该模块提供本地已安装Minecraft版本的检测、解析和管理功能。

主要功能:
    - 扫描指定目录下的已安装Minecraft版本
    - 解析版本配置文件获取详细信息
    - 提供版本信息的结构化访问接口
    - 支持多种版本类型（原版、Forge、Fabric等）

Example:
    获取本地已安装版本::

        from src.core.game.local_versions import get_local_minecraft_versions
        
        minecraft_dir = "/path/to/.minecraft"
        versions = get_local_minecraft_versions(minecraft_dir)
        
        for version in versions:
            print(f"版本: {version['id']}")
            print(f"类型: {version['type']}")
            print(f"发布时间: {version['releaseTime']}")
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


class LocalVersionInfo:
    """本地Minecraft版本信息类。
    
    封装本地已安装版本的详细信息，包括版本ID、类型、配置等。
    
    Attributes:
        id (str): 版本ID
        type (str): 版本类型（release、snapshot、old_beta、old_alpha等）
        releaseTime (datetime): 发布时间
        complianceLevel (int): 合规级别
        mainClass (str): 主类名
        minecraftArguments (str): Minecraft启动参数（旧格式）
        arguments (Dict): 启动参数（新格式）
        libraries (List): 依赖库列表
        assets (str): 资源版本
        javaVersion (Dict): Java版本要求
        inheritsFrom (Optional[str]): 继承的版本ID
        jar (Optional[str]): JAR文件名
        custom_data (Dict): 自定义数据
    """
    
    def __init__(self, version_data: Dict[str, Any], version_path: Path):
        """初始化版本信息。
        
        Args:
            version_data: 从版本JSON文件解析的数据
            version_path: 版本目录路径
        """
        self.id: str = version_data.get("id", "")
        self.type: str = version_data.get("type", "unknown")
        self.releaseTime: datetime = self._parse_time(version_data.get("releaseTime", ""))
        self.complianceLevel: int = version_data.get("complianceLevel", 0)
        self.mainClass: str = version_data.get("mainClass", "")
        self.minecraftArguments: str = version_data.get("minecraftArguments", "")
        self.arguments: Dict = version_data.get("arguments", {})
        self.libraries: List = version_data.get("libraries", [])
        self.assets: str = version_data.get("assets", "")
        self.javaVersion: Dict = version_data.get("javaVersion", {})
        self.inheritsFrom: Optional[str] = version_data.get("inheritsFrom")
        self.jar: Optional[str] = version_data.get("jar")
        self.custom_data: Dict = version_data
        self.version_path: Path = version_path
        
    def _parse_time(self, time_str: str) -> datetime:
        """解析时间字符串。
        
        Args:
            time_str: 时间字符串
            
        Returns:
            解析后的datetime对象，解析失败时返回epoch时间
        """
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return datetime.fromtimestamp(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。
        
        Returns:
            包含版本信息的字典
        """
        return {
            "id": self.id,
            "type": self.type,
            "releaseTime": self.releaseTime,
            "complianceLevel": self.complianceLevel,
            "mainClass": self.mainClass,
            "minecraftArguments": self.minecraftArguments,
            "arguments": self.arguments,
            "libraries": self.libraries,
            "assets": self.assets,
            "javaVersion": self.javaVersion,
            "inheritsFrom": self.inheritsFrom,
            "jar": self.jar,
            "version_path": str(self.version_path),
            "is_modded": self.is_modded(),
            "mod_loader": self.get_mod_loader()
        }
    
    def is_modded(self) -> bool:
        """检查是否为模组版本。
        
        Returns:
            是否为模组版本
        """
        return self.inheritsFrom is not None or "forge" in self.id.lower() or "fabric" in self.id.lower() or "quilt" in self.id.lower()
    
    def get_mod_loader(self) -> Optional[str]:
        """获取模组加载器类型。
        
        Returns:
            模组加载器类型（forge、fabric、quilt等），如果不是模组版本则返回None
        """
        if "forge" in self.id.lower():
            return "forge"
        elif "fabric" in self.id.lower():
            return "fabric"
        elif "quilt" in self.id.lower():
            return "quilt"
        elif self.inheritsFrom:
            return "unknown_modded"
        return None


def get_local_minecraft_versions(minecraft_directory: Union[str, Path]) -> List[LocalVersionInfo]:
    """获取指定目录下的本地Minecraft版本列表。
    
    扫描Minecraft目录下的versions文件夹，解析每个版本的配置文件，
    返回包含详细信息的版本列表。
    
    Args:
        minecraft_directory: Minecraft目录路径
        
    Returns:
        本地版本信息列表，按发布时间倒序排列
        
    Raises:
        FileNotFoundError: 指定目录不存在
        PermissionError: 没有读取权限
        
    Example:
        获取本地版本::
        
            versions = get_local_minecraft_versions("/path/to/.minecraft")
            for version in versions:
                print(f"版本: {version.id}, 类型: {version.type}")
    """
    minecraft_path = Path(minecraft_directory)
    versions_path = minecraft_path / "versions"
    
    if not versions_path.exists():
        return []
    
    if not versions_path.is_dir():
        return []
    
    versions: List[LocalVersionInfo] = []
    
    try:
        for version_dir in versions_path.iterdir():
            if not version_dir.is_dir():
                continue
                
            version_json_path = version_dir / f"{version_dir.name}.json"
            
            if not version_json_path.exists():
                continue
                
            try:
                with open(version_json_path, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    
                version_info = LocalVersionInfo(version_data, version_dir)
                versions.append(version_info)
                
            except (json.JSONDecodeError, IOError, KeyError) as e:
                # 跳过无法解析的版本文件
                continue
                
    except PermissionError:
        raise PermissionError(f"没有读取目录的权限: {versions_path}")
    
    # 按发布时间倒序排列
    versions.sort(key=lambda v: v.releaseTime, reverse=True)
    
    return versions


def get_local_minecraft_versions_dict(minecraft_directory: Union[str, Path]) -> List[Dict[str, Any]]:
    """获取本地Minecraft版本列表（字典格式）。
    
    这是get_local_minecraft_versions的便捷版本，直接返回字典列表。
    
    Args:
        minecraft_directory: Minecraft目录路径
        
    Returns:
        版本信息字典列表
    """
    versions = get_local_minecraft_versions(minecraft_directory)
    return [version.to_dict() for version in versions]


def find_version_by_id(minecraft_directory: Union[str, Path], version_id: str) -> Optional[LocalVersionInfo]:
    """根据版本ID查找本地版本。
    
    Args:
        minecraft_directory: Minecraft目录路径
        version_id: 要查找的版本ID
        
    Returns:
        找到的版本信息，未找到时返回None
    """
    versions = get_local_minecraft_versions(minecraft_directory)
    for version in versions:
        if version.id == version_id:
            return version
    return None


def get_version_types_summary(minecraft_directory: Union[str, Path]) -> Dict[str, int]:
    """获取版本类型统计。
    
    Args:
        minecraft_directory: Minecraft目录路径
        
    Returns:
        版本类型统计字典，键为版本类型，值为数量
    """
    versions = get_local_minecraft_versions(minecraft_directory)
    summary = {}
    
    for version in versions:
        version_type = version.type
        summary[version_type] = summary.get(version_type, 0) + 1
    
    return summary
