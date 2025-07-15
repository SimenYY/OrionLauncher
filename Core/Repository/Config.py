from Utils.abc import Repository


class Config(Repository):
    def __init__(self):
        super().__init__()
        self["api.mirror"] = "Official"
        self["api.proxy"] = ""
        self["api.proxy.username"] = ""
        self["api.proxy.password"] = ""

    def _load(self):
        """
        TODO: 加载配置文件
        """
        pass

    def _save(self):
        """
        TODO:保存配置文件
        """
        pass

class Constant(Repository):
    """只读配置，用于存储一些固定不变的配置项"""
    name: str = "OrionLauncher"
    organization: str = "OrionLauncher"
    repository: str = "https://github.com/OrionLauncher/OrionLauncher"
    license: str = "GNU LGPL-2.1 license"
    license_url: str = "https://github.com/OrionLauncher/OrionLauncher/blob/main/LICENSE"


class Path(Repository):
    def __init__(self):
        super().__init__()

path = Path()
config = Config()
