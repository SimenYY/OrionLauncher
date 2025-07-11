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
