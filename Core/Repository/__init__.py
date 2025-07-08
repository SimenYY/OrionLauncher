"""仓库管理模块。

该模块包含路径管理、文件仓库等功能。
"""

from .Path import Path
from .Config import Config
from Utils.abc import Repository

class Persistence(Repository):
    def __init__(self):
        super().__init__()

path = Path()
persistence = Persistence()
config = Config()

__all__ = ['path', 'persistence', 'config'] 