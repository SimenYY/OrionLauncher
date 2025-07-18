"""
账户控制器模块

负责用户账户的管理、登录、验证等功能
"""

from typing import Dict, List, Optional, Any
from PySide6.QtCore import Signal

from .base_controller import BaseController
from src.utils.locale_manager import LocaleManager


class AccountController(BaseController):
    """
    账户控制器

    负责用户账户的管理、登录、验证等功能
    """

    # 账户相关信号
    login_success = Signal(dict)  # 用户信息
    login_failed = Signal(str)  # 错误信息
    logout_completed = Signal()
    account_list_updated = Signal(list)  # 账户列表

    def __init__(self, parent=None):
        """初始化账户控制器"""
        super().__init__(parent)
        self._current_account = None
        self._accounts = []

    def initialize(self) -> bool:
        """
        初始化控制器

        Returns:
            bool: 初始化是否成功
        """
        # TODO: 初始化账户控制器，连接Core层相关功能
        return True

    def login(self, username: str, password: str) -> None:
        """
        登录账户

        Args:
            username: 用户名
            password: 密码
        """
        # 异步登录
        self.run_async_task("login", self._async_login, username, password)

    def _async_login(self, username: str, password: str) -> Dict[str, Any]:
        """
        异步登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            Dict[str, Any]: 用户信息
        """
        # TODO: 调用Core层登录功能
        # 模拟登录过程
        import time

        time.sleep(1)

        # 模拟登录成功
        if username and password:
            account_info = {
                "username": username,
                "uuid": "12345678-1234-5678-1234-567812345678",
                "accessToken": "token123456",
                "type": "Microsoft",
            }
            self._current_account = account_info
            self.login_success.emit(account_info)
            return account_info
        else:
            error_msg = LocaleManager().get("username_password_empty_error")
            self.login_failed.emit(error_msg)
            return {"error": error_msg}

    def logout(self) -> None:
        """登出当前账户"""
        # 异步登出
        self.run_async_task("logout", self._async_logout)

    def _async_logout(self) -> None:
        """异步登出"""
        # TODO: 调用Core层登出功能
        self._current_account = None
        self.logout_completed.emit()
        return True

    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        获取已保存的账户列表

        Returns:
            List[Dict[str, Any]]: 账户列表
        """
        # TODO: 从Core层获取账户列表
        return self._accounts

    def refresh_account_list(self) -> None:
        """刷新账户列表"""
        # 异步获取账户列表
        self.run_async_task("refresh_accounts", self._async_refresh_accounts)

    def _async_refresh_accounts(self) -> None:
        """异步刷新账户列表"""
        # TODO: 从Core层获取账户列表
        # 模拟获取账户列表
        accounts = self.get_accounts()
        self.account_list_updated.emit(accounts)
        return accounts

    def get_current_account(self) -> Optional[Dict[str, Any]]:
        """
        获取当前登录的账户

        Returns:
            Optional[Dict[str, Any]]: 当前账户信息，如果未登录则返回None
        """
        return self._current_account
