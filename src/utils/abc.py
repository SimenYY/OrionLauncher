from abc import ABC
from typing import Any, Dict


class Repository(Dict[str, Any], ABC):
    """提供键值存储功能的抽象基类。

    继承自 ``Dict`` 实现字典的全部功能，同时作为抽象基类(ABC)提供接口规范。
    重写 ``__getitem__`` 方法使其在访问不存在的键时返回None而不是抛出KeyError。

    该类可作为配置文件、设置存储等键值对存储机制的基类。
    """

    def __init__(self) -> None:
        """初始化Repository实例。"""
        super().__init__()

    def get(self, key: str, default: Any = None) -> Any:
        """获取指定键的值，如果键不存在则返回默认值。

        Args:
            key (str): 要获取值的键
            default (Any, optional): 键不存在时返回的默认值。默认为None

        Returns:
            Any: 键对应的值或默认值
        """
        return super().get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置指定键的值。

        Args:
            key (str): 要设置的键
            value (Any): 要设置的值
        """
        self[key] = value

    def __getitem__(self, key: str) -> Any:
        """重写字典的键访问方法，当键不存在时返回None而不是抛出KeyError。

        此方法通过调用 ``get`` 方法实现安全访问。

        Args:
            key (str): 要访问的键

        Returns:
            Any: 键对应的值，如果键不存在则返回None
        """
        return self.get(key)
