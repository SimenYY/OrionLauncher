"""用户管理模块。

该模块包含用户账户管理、认证等功能。
"""
from src.utils.types import UserInfo
from src.utils.tools import uuid_generate


class OfflineUser:
    @staticmethod
    def create(name: str) -> UserInfo:
        user_uuid: str = uuid_generate(name)
        return UserInfo(
            id=user_uuid,
            name=name,
            type="offline"
        )
