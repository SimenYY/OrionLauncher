"""
安装适配器模块

本模块定义了安装适配器接口和具体实现，用于与底层安装库（如 minecraft_launcher_lib）解耦。
通过适配器模式，可以轻松切换不同的底层实现，便于后期重构。

适配器接口：
- InstallationAdapter: 安装适配器基类
- VanillaInstallationAdapter: 原版游戏安装适配器
- ForgeInstallationAdapter: Forge 安装适配器
- FabricInstallationAdapter: Fabric 安装适配器
- QuiltInstallationAdapter: Quilt 安装适配器
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

from Core.minecraft_launcher_lib.types import CallbackDict
from Core.minecraft_launcher_lib import install as mll_install
from Core.minecraft_launcher_lib import forge as mll_forge
from Core.minecraft_launcher_lib import fabric as mll_fabric
from Core.minecraft_launcher_lib import quilt as mll_quilt
from Core.minecraft_launcher_lib import runtime as mll_runtime
from Core.minecraft_launcher_lib import utils as mll_utils
from Core.minecraft_launcher_lib.exceptions import VersionNotFound, UnsupportedVersion

logger = logging.getLogger(__name__)


class InstallationAdapter(ABC):
    """安装适配器基类。

    定义了安装适配器的通用接口，所有具体的安装适配器都应该继承此类。
    通过适配器模式，实现与底层安装库的解耦，便于后期重构和扩展。

    Attributes:
        minecraft_directory (str): Minecraft 安装目录路径。
        logger (logging.Logger): 日志记录器实例。
    """

    def __init__(self, minecraft_directory: Union[str, Path]) -> None:
        """初始化安装适配器。

        Args:
            minecraft_directory: Minecraft 安装目录路径。
        """
        self.minecraft_directory = str(minecraft_directory)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def install(self, version_id: str, callback: CallbackDict, **kwargs) -> bool:
        """执行安装操作。

        Args:
            version_id: 要安装的版本 ID。
            callback: 回调函数字典，用于报告安装进度和状态。
            **kwargs: 其他安装参数。

        Returns:
            bool: 安装是否成功。

        Raises:
            VersionNotFound: 当指定版本不存在时抛出。
            UnsupportedVersion: 当版本不受支持时抛出。
        """
        pass

    @abstractmethod
    def is_installed(self, version_id: str) -> bool:
        """检查指定版本是否已安装。

        Args:
            version_id: 要检查的版本 ID。

        Returns:
            bool: 如果版本已安装返回 True，否则返回 False。
        """
        pass

    @abstractmethod
    def get_available_versions(self) -> List[str]:
        """获取可用版本列表。

        Returns:
            List[str]: 可用版本 ID 列表。
        """
        pass

    def validate_version(self, version_id: str) -> bool:
        """验证版本 ID 是否有效。

        Args:
            version_id: 要验证的版本 ID。

        Returns:
            bool: 如果版本有效返回 True，否则返回 False。
        """
        return version_id in self.get_available_versions()


class VanillaInstallationAdapter(InstallationAdapter):
    """原版 Minecraft 安装适配器。

    负责原版 Minecraft 的安装，包括游戏文件、资源文件、库文件等。
    使用 minecraft_launcher_lib 库进行实际的安装操作。
    """

    def install(self, version_id: str, callback: CallbackDict, **kwargs) -> bool:
        """安装原版 Minecraft。

        Args:
            version_id: 要安装的 Minecraft 版本 ID。
            callback: 回调函数字典，用于报告安装进度。
            **kwargs: 其他安装参数。

        Returns:
            bool: 安装成功返回 True，失败返回 False。

        Raises:
            VersionNotFound: 当指定版本不存在时抛出。
        """
        try:
            self.logger.info(f"开始安装 Minecraft {version_id}")

            # 调用 minecraft_launcher_lib 进行安装
            mll_install.install_minecraft_version(
                versionid=version_id,
                minecraft_directory=self.minecraft_directory,
                callback=callback
            )

            self.logger.info(f"Minecraft {version_id} 安装完成")
            return True

        except VersionNotFound as e:
            self.logger.error(f"版本 {version_id} 不存在: {e}")
            raise
        except Exception as e:
            self.logger.error(f"安装 Minecraft {version_id} 时发生错误: {e}")
            return False

    def is_installed(self, version_id: str) -> bool:
        """检查 Minecraft 版本是否已安装。

        通过检查版本目录中的 JSON 文件和 JAR 文件是否存在来判断。

        Args:
            version_id: 要检查的 Minecraft 版本 ID。

        Returns:
            bool: 如果版本已安装返回 True，否则返回 False。
        """
        version_json_path = os.path.join(
            self.minecraft_directory, "versions", version_id, f"{version_id}.json"
        )
        version_jar_path = os.path.join(
            self.minecraft_directory, "versions", version_id, f"{version_id}.jar"
        )

        return os.path.exists(version_json_path) and os.path.exists(version_jar_path)

    def get_available_versions(self) -> List[str]:
        """获取可用的 Minecraft 版本列表。

        从 Mojang 官方 API 获取版本清单。

        Returns:
            List[str]: 可用版本 ID 列表，如果获取失败返回空列表。
        """
        try:
            # 使用 minecraft_launcher_lib 获取版本列表
            import requests
            response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json")
            if response.status_code == 200:
                data = response.json()
                return [v["id"] for v in data["versions"]]
            else:
                self.logger.error(f"获取版本列表失败，状态码: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"获取可用版本列表时发生错误: {e}")
            return []


class ForgeInstallationAdapter(InstallationAdapter):
    """Forge 安装适配器。

    负责 Forge 模组加载器的安装。Forge 是最流行的 Minecraft 模组加载器之一，
    支持大量的模组和插件。
    """

    def install(self, version_id: str, callback: CallbackDict, **kwargs) -> bool:
        """安装 Forge 模组加载器。

        Args:
            version_id: 要安装的 Forge 版本 ID。
            callback: 回调函数字典，用于报告安装进度。
            **kwargs: 其他安装参数。可选参数包括：
                - java_path (str): Java 可执行文件路径。

        Returns:
            bool: 安装成功返回 True，失败返回 False。

        Raises:
            VersionNotFound: 当指定 Forge 版本不存在时抛出。
        """
        try:
            self.logger.info(f"开始安装 Forge {version_id}")

            # 获取 Java 路径
            java_path = kwargs.get("java_path", None)

            # 调用 minecraft_launcher_lib 进行 Forge 安装
            mll_forge.install_forge_version(
                versionid=version_id,
                path=self.minecraft_directory,
                callback=callback,
                java=java_path
            )

            self.logger.info(f"Forge {version_id} 安装完成")
            return True

        except VersionNotFound as e:
            self.logger.error(f"Forge 版本 {version_id} 不存在: {e}")
            raise
        except Exception as e:
            self.logger.error(f"安装 Forge {version_id} 时发生错误: {e}")
            return False

    def is_installed(self, version_id: str) -> bool:
        """检查 Forge 版本是否已安装。

        通过检查 Forge 安装后创建的版本目录来判断是否已安装。

        Args:
            version_id: 要检查的 Forge 版本 ID。

        Returns:
            bool: 如果 Forge 版本已安装返回 True，否则返回 False。
        """
        # Forge 安装后会创建对应的版本目录
        forge_version_id = mll_forge.forge_to_installed_version(version_id)
        version_json_path = os.path.join(
            self.minecraft_directory, "versions", forge_version_id, f"{forge_version_id}.json"
        )

        return os.path.exists(version_json_path)

    def get_available_versions(self) -> List[str]:
        """获取可用的 Forge 版本列表。

        从 Forge 官方源获取可用版本列表。

        Returns:
            List[str]: 可用 Forge 版本 ID 列表，如果获取失败返回空列表。
        """
        try:
            versions = mll_forge.list_forge_versions()
            return versions
        except Exception as e:
            self.logger.error(f"获取可用 Forge 版本列表时发生错误: {e}")
            return []


class FabricInstallationAdapter(InstallationAdapter):
    """Fabric 安装适配器。

    负责 Fabric 模组加载器的安装。Fabric 是一个轻量级的模组加载器，
    专注于快速更新和现代化的模组开发体验。
    """

    def install(self, version_id: str, callback: CallbackDict, **kwargs) -> bool:
        """安装 Fabric 模组加载器。

        Args:
            version_id: 要安装 Fabric 的 Minecraft 版本 ID。
            callback: 回调函数字典，用于报告安装进度。
            **kwargs: 其他安装参数。可选参数包括：
                - loader_version (str): Fabric Loader 版本。
                - java_path (str): Java 可执行文件路径。

        Returns:
            bool: 安装成功返回 True，失败返回 False。

        Raises:
            VersionNotFound: 当指定 Minecraft 版本不存在时抛出。
            UnsupportedVersion: 当 Minecraft 版本不支持 Fabric 时抛出。
        """
        try:
            self.logger.info(f"开始安装 Fabric for Minecraft {version_id}")

            # 获取参数
            loader_version = kwargs.get("loader_version", None)
            java_path = kwargs.get("java_path", None)

            # 调用 minecraft_launcher_lib 进行 Fabric 安装
            mll_fabric.install_fabric(
                minecraft_version=version_id,
                minecraft_directory=self.minecraft_directory,
                loader_version=loader_version,
                callback=callback,
                java=java_path
            )

            self.logger.info(f"Fabric for Minecraft {version_id} 安装完成")
            return True

        except (VersionNotFound, UnsupportedVersion) as e:
            self.logger.error(f"Fabric 安装失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"安装 Fabric for Minecraft {version_id} 时发生错误: {e}")
            return False

    def is_installed(self, version_id: str) -> bool:
        """检查 Fabric 版本是否已安装。

        通过检查是否存在以 fabric-loader 开头且包含指定 Minecraft 版本的目录来判断。

        Args:
            version_id: 要检查的 Minecraft 版本 ID。

        Returns:
            bool: 如果 Fabric 已安装返回 True，否则返回 False。
        """
        # Fabric 安装后会创建 fabric-loader-{loader_version}-{minecraft_version} 目录
        # 这里简化检查，查看是否存在以 fabric-loader 开头且包含指定 minecraft 版本的目录
        versions_dir = os.path.join(self.minecraft_directory, "versions")
        if not os.path.exists(versions_dir):
            return False

        for version_dir in os.listdir(versions_dir):
            if version_dir.startswith("fabric-loader") and version_id in version_dir:
                version_json_path = os.path.join(versions_dir, version_dir, f"{version_dir}.json")
                if os.path.exists(version_json_path):
                    return True

        return False

    def get_available_versions(self) -> List[str]:
        """获取支持 Fabric 的 Minecraft 版本列表。

        从 Fabric 官方 API 获取支持的 Minecraft 版本列表。

        Returns:
            List[str]: 支持 Fabric 的 Minecraft 版本 ID 列表，如果获取失败返回空列表。
        """
        try:
            versions = mll_fabric.get_all_minecraft_versions()
            return [v["version"] for v in versions]
        except Exception as e:
            self.logger.error(f"获取支持 Fabric 的 Minecraft 版本列表时发生错误: {e}")
            return []


class QuiltInstallationAdapter(InstallationAdapter):
    """Quilt 安装适配器。

    负责 Quilt 模组加载器的安装。Quilt 是 Fabric 的一个分支，
    提供了更多的功能和改进，同时保持与 Fabric 模组的兼容性。
    """

    def install(self, version_id: str, callback: CallbackDict, **kwargs) -> bool:
        """安装 Quilt 模组加载器。

        Args:
            version_id: 要安装 Quilt 的 Minecraft 版本 ID。
            callback: 回调函数字典，用于报告安装进度。
            **kwargs: 其他安装参数。可选参数包括：
                - loader_version (str): Quilt Loader 版本。
                - java_path (str): Java 可执行文件路径。

        Returns:
            bool: 安装成功返回 True，失败返回 False。

        Raises:
            VersionNotFound: 当指定 Minecraft 版本不存在时抛出。
            UnsupportedVersion: 当 Minecraft 版本不支持 Quilt 时抛出。
        """
        try:
            self.logger.info(f"开始安装 Quilt for Minecraft {version_id}")

            # 获取参数
            loader_version = kwargs.get("loader_version", None)
            java_path = kwargs.get("java_path", None)

            # 调用 minecraft_launcher_lib 进行 Quilt 安装
            mll_quilt.install_quilt(
                minecraft_version=version_id,
                minecraft_directory=self.minecraft_directory,
                loader_version=loader_version,
                callback=callback,
                java=java_path
            )

            self.logger.info(f"Quilt for Minecraft {version_id} 安装完成")
            return True

        except (VersionNotFound, UnsupportedVersion) as e:
            self.logger.error(f"Quilt 安装失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"安装 Quilt for Minecraft {version_id} 时发生错误: {e}")
            return False

    def is_installed(self, version_id: str) -> bool:
        """检查 Quilt 版本是否已安装。

        通过检查是否存在以 quilt-loader 开头且包含指定 Minecraft 版本的目录来判断。

        Args:
            version_id: 要检查的 Minecraft 版本 ID。

        Returns:
            bool: 如果 Quilt 已安装返回 True，否则返回 False。
        """
        # Quilt 安装后会创建 quilt-loader-{loader_version}-{minecraft_version} 目录
        versions_dir = os.path.join(self.minecraft_directory, "versions")
        if not os.path.exists(versions_dir):
            return False

        for version_dir in os.listdir(versions_dir):
            if version_dir.startswith("quilt-loader") and version_id in version_dir:
                version_json_path = os.path.join(versions_dir, version_dir, f"{version_dir}.json")
                if os.path.exists(version_json_path):
                    return True

        return False

    def get_available_versions(self) -> List[str]:
        """获取支持 Quilt 的 Minecraft 版本列表。

        从 Quilt 官方 API 获取支持的 Minecraft 版本列表。

        Returns:
            List[str]: 支持 Quilt 的 Minecraft 版本 ID 列表，如果获取失败返回空列表。
        """
        try:
            versions = mll_quilt.get_all_minecraft_versions()
            return [v["version"] for v in versions]
        except Exception as e:
            self.logger.error(f"获取支持 Quilt 的 Minecraft 版本列表时发生错误: {e}")
            return []