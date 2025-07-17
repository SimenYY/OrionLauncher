"""
设置控制器模块

负责应用设置的管理、保存、加载等功能
"""

import os
import platform
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Any

from PySide6.QtCore import Signal

from .base_controller import BaseController


class SettingsController(BaseController):
    """
    设置控制器

    负责应用设置的管理、保存、加载等功能
    """

    # 设置相关信号
    settings_loaded = Signal(dict)  # 设置数据
    settings_saved = Signal()
    settings_changed = Signal(str, object)  # 设置项名称, 新值

    # 配置文件位置
    APP_NAME = "OrionLauncher"
    FILE_NAME = "settings.pkl"

    def __init__(self, parent=None):
        """初始化设置控制器"""
        super().__init__(parent)
        self._settings = {
            "game": {
                "minecraft_directory": "",
                "java_path": "",
                "max_memory": 2048,
                "jvm_args": "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200",
                "resolution_width": 854,
                "resolution_height": 480,
                "fullscreen": False,
            },
            "launcher": {
                "language": "zh_CN",
                "theme": "dark",
                "theme_colors": {},
                "background_path": "",
                "check_updates": True,
                "close_launcher_when_game_starts": True,
            },
            "download": {
                "download_source": "official",
                "concurrent_downloads": 3,
                "download_assets": True,
                "download_libraries": True,
            },
        }

    def initialize(self) -> bool:
        """
        初始化控制器

        Returns:
            bool: 初始化是否成功
        """
        # 加载设置
        self.load_settings()
        return True

    @staticmethod
    def _get_user_config_path() -> Path:
        """获取用户配置文件的完整路径（跨平台）"""
        system = platform.system()
        if system == "Windows":
            base_dir = os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
        elif system == "Darwin":  # macOS
            base_dir = Path.home() / "Library" / "Application Support"
        else:  # Linux 或其他系统
            base_dir = Path.home() / ".config"

        config_dir = Path(base_dir) / SettingsController.APP_NAME
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / SettingsController.FILE_NAME

    @staticmethod
    def hash_data(data: bytes) -> str:
        """使用 SHA-256 计算字节数据的哈希值"""
        return hashlib.sha256(data).hexdigest()

    def load_settings(self) -> None:
        """加载设置"""
        # 异步加载设置
        self.run_async_task("load_settings", self._async_load_settings)

    def _async_load_settings(self) -> Dict[str, Any]:
        """
        异步加载设置

        Returns:
            Dict[str, Any]: 设置数据
        """
        # 加载配置，并验证哈希值是否匹配
        config_path = SettingsController._get_user_config_path()
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    payload = pickle.load(f)  # 读取已保存的内容（包含 data 和 hash）

                data = payload.get("data")
                expected_hash = payload.get("hash")

                # 校验哈希是否匹配
                if SettingsController.hash_data(data) == expected_hash:
                    # 返回反序列化后的配置对象
                    self._settings = pickle.loads(data)
                else:
                    print("配置文件已损坏")

            except Exception as e:
                print("加载配置失败:", e)

        # 发送设置加载信号
        self.settings_loaded.emit(self._settings)
        return self._settings

    def save_settings(self) -> None:
        """保存设置"""
        # 异步保存设置
        self.run_async_task("save_settings", self._async_save_settings)

    def _async_save_settings(self) -> bool:
        """
        异步保存设置

        Returns:
            bool: 保存是否成功
        """
        # 保存配置，并写入哈希值用于验证
        config_path = SettingsController._get_user_config_path()
        data = pickle.dumps(self._settings)
        digest = self.hash_data(data)

        # 构建保存的内容：包含原始数据和哈希值
        payload = {
            "data": data,
            "hash": digest,
        }

        # 保存文件，会自动覆盖旧文件（"wb" 写入二进制模式）
        with open(config_path, "wb") as f:
            pickle.dump(payload, f)

        # 发送设置保存信号
        self.settings_saved.emit()
        return True

    def get_setting(self, section: str, key: str, default=None) -> Any:
        """
        获取设置项

        Args:
            section: 设置分区
            key: 设置项键名
            default: 默认值

        Returns:
            Any: 设置项值
        """
        if section in self._settings and key in self._settings[section]:
            return self._settings[section][key]
        return default

    def set_setting(self, section: str, key: str, value: Any) -> None:
        """
        设置设置项

        Args:
            section: 设置分区
            key: 设置项键名
            value: 设置项值
        """
        if section not in self._settings:
            self._settings[section] = {}

        # 检查值是否变化
        old_value = self._settings[section].get(key)
        if old_value != value:
            self._settings[section][key] = value
            self.settings_changed.emit(f"{section}.{key}", value)

    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有设置

        Returns:
            Dict[str, Dict[str, Any]]: 所有设置
        """
        return self._settings
