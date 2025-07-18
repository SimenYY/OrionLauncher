"""仓库管理模块。

该模块包含路径管理、文件仓库等功能。
"""

from src.utils.abc import Repository

from .Config import config, path


class Persistence(Repository):
    def __init__(self):
        super().__init__()

persistence = Persistence()

__all__ = ["path", "persistence", "config"]
