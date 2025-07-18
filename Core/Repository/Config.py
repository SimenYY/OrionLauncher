import os
from Utils.abc import Repository
from Utils.path import data_path
from Utils.database import Database

from abc import ABC 
from typing import Any, Dict

import _version


class Config(Repository):
    def __init__(self):
        super().__init__()
        self.db_file = os.path.join(data_path, "config.db")
        self.database = Database(self.db_file)  # 创建数据库实例，用于存储配置数据
        self.update({
            "api.mirror": "Official",
            "api.proxy": "",
            "api.proxy.username": "",
            "api.proxy.password": ""
        })
        self._load()  # 加载数据库中的配置

    def _load(self):
        self.update(self.database.item_get_all())

    def _save(self):
        self.database.item_sync(self)

    def __getitem__(self, key: str) -> Any:
        return super().get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(key, value)
        self.database.item_set(key, value)

    def __delitem__(self, key: str) -> None:
        super().__delitem__(key)
        self.database.item_delete(key)


class Constant(Repository):
    """只读配置，用于存储一些固定不变的配置项"""
    name: str = "OrionLauncher"
    organization: str = "OrionLauncher"
    repository: str = "https://github.com/OrionLauncher/OrionLauncher"
    license: str = "GNU LGPL-2.1 license"
    license_url: str = "https://github.com/OrionLauncher/OrionLauncher/blob/main/LICENSE"
    version: str = _version.__version__

config = Config()
