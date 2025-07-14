"""
用户登录界面语言

用于统一管理界面组件的语言翻译
"""

import json
import os

from PySide6.QtCore import Signal, QObject

class LocaleManager(QObject):
    """
    语言管理器单例
    """

    _instance = None

    updated = Signal()

    def __new__(cls):
        if cls._instance is None:
            # 创建单例对象
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "initialized", False):
            return
        super().__init__()
        self.initialized = True
        self._translations = {}
        # 默认使用中文
        self._locale = "zh_CN"
        self.set_locale(self._locale)

    def set_locale(self, locale_code):
        path = os.path.join("locales", f"{locale_code}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self._translations = json.load(f)
                self._locale = locale_code

        self.updated.emit()

    def get_text(self, key):
        return self._translations.get(key, key)

    # 提供简化接口，等同于 get_text
    def get(self, key):
        return self.get_text(key)

    def current_locale(self):
        return self._locale
