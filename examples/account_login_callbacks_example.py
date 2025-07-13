"""Minecraft账号登录回调使用示例。

展示如何使用新定义的账号登录回调组，包括不同登录方式的处理。
"""

import logging
from typing import Dict, Any

from Utils.callbacks import Callbacks, AccountCallbackGroup

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccountLoginExample:
    """账号登录示例类"""
    
    def __init__(self):
        self.login_state = "idle"
        self.user_info = {}
        self.tokens = {}
    
    def create_login_callbacks(self) -> Callbacks:
        """创建登录回调"""
        def on_start():
            self.login_state = "starting"
            print("🚀 开始登录...")
            logger.info("账号登录开始")
        
        def on_authenticating():
            self.login_state = "authenticating"
            print("🔐 正在进行身份验证...")
            logger.info("正在进行身份验证")
        
        def on_waiting_user_input(message: str):
            self.login_state = "waiting_input"
            print(f"⏳ 等待用户操作: {message}")
            logger.info(f"等待用户输入: {message}")
        
        def on_progress(step: str, current: int, total: int):
            progress = int((current / total) * 100) if total > 0 else 0
            print(f"📊 登录进度: {step} ({current}/{total}) - {progress}%")
            logger.info(f"登录进度: {step} - {progress}%")
        
        def on_success(username: str, uuid: str, access_token: str):
            self.login_state = "success"
            self.user_info = {
                "username": username,
                "uuid": uuid,
                "access_token": access_token
            }
            print(f"✅ 登录成功!")
            print(f"   用户名: {username}")
            print(f"   UUID: {uuid}")
            print(f"   令牌: {access_token[:20]}...")
            logger.info(f"登录成功: {username} ({uuid})")
        
        def on_finished():
            print("🎉 登录流程完成")
            logger.info("登录流程完成")
        
        def on_error(error: Exception):
            self.login_state = "error"
            print(f"❌ 登录失败: {error}")
            logger.error(f"登录失败: {error}")
        
        return Callbacks(
            start=on_start,
            authenticating=on_authenticating,
            waiting_user_input=on_waiting_user_input,
            progress=on_progress,
            success=on_success,
            finished=on_finished,
            error=on_error
        )
    
    def create_refresh_callbacks(self) -> Callbacks:
        """创建令牌刷新回调"""
        def on_start():
            print("🔄 开始刷新令牌...")
            logger.info("令牌刷新开始")
        
        def on_validating():
            print("🔍 正在验证当前令牌...")
            logger.info("正在验证当前令牌")
        
        def on_refreshing():
            print("⚡ 正在刷新令牌...")
            logger.info("正在刷新令牌")
        
        def on_success(access_token: str, expires_in: int):
            self.tokens["access_token"] = access_token
            self.tokens["expires_in"] = expires_in
            print(f"✅ 令牌刷新成功!")
            print(f"   新令牌: {access_token[:20]}...")
            print(f"   有效期: {expires_in}秒")
            logger.info(f"令牌刷新成功，有效期: {expires_in}秒")
        
        def on_finished():
            print("🎉 令牌刷新完成")
            logger.info("令牌刷新完成")
        
        def on_error(error: Exception):
            print(f"❌ 令牌刷新失败: {error}")
            logger.error(f"令牌刷新失败: {error}")
        
        return Callbacks(
            start=on_start,
            validating=on_validating,
            refreshing=on_refreshing,
            success=on_success,
            finished=on_finished,
            error=on_error
        )
    
    def create_logout_callbacks(self) -> Callbacks:
        """创建登出回调"""
        def on_start():
            print("👋 开始登出...")
            logger.info("账号登出开始")
        
        def on_revoking_token():
            print("🔒 正在撤销令牌...")
            logger.info("正在撤销令牌")
        
        def on_clearing_cache():
            print("🧹 正在清理缓存...")
            logger.info("正在清理缓存")
        
        def on_finished():
            self.login_state = "logged_out"
            self.user_info.clear()
            self.tokens.clear()
            print("✅ 登出完成")
            logger.info("账号登出完成")
        
        def on_error(error: Exception):
            print(f"❌ 登出失败: {error}")
            logger.error(f"登出失败: {error}")
        
        return Callbacks(
            start=on_start,
            revoking_token=on_revoking_token,
            clearing_cache=on_clearing_cache,
            finished=on_finished,
            error=on_error
        )
    
    def create_validation_callbacks(self) -> Callbacks:
        """创建验证回调"""
        def on_start():
            print("🔍 开始验证账号...")
            logger.info("账号验证开始")
        
        def on_checking_token():
            print("🔑 正在检查令牌有效性...")
            logger.info("正在检查令牌有效性")
        
        def on_checking_profile():
            print("👤 正在检查用户档案...")
            logger.info("正在检查用户档案")
        
        def on_valid(username: str, uuid: str):
            print(f"✅ 账号验证通过!")
            print(f"   用户名: {username}")
            print(f"   UUID: {uuid}")
            logger.info(f"账号验证通过: {username} ({uuid})")
        
        def on_invalid(reason: str):
            print(f"❌ 账号验证失败: {reason}")
            logger.warning(f"账号验证失败: {reason}")
        
        def on_finished():
            print("🎉 账号验证完成")
            logger.info("账号验证完成")
        
        def on_error(error: Exception):
            print(f"❌ 验证过程出错: {error}")
            logger.error(f"验证过程出错: {error}")
        
        return Callbacks(
            start=on_start,
            checking_token=on_checking_token,
            checking_profile=on_checking_profile,
            valid=on_valid,
            invalid=on_invalid,
            finished=on_finished,
            error=on_error
        )
    
    def create_account_callback_group(self) -> AccountCallbackGroup:
        """创建完整的账号回调组"""
        return AccountCallbackGroup(
            login=self.create_login_callbacks(),
            refresh=self.create_refresh_callbacks(),
            logout=self.create_logout_callbacks(),
            validation=self.create_validation_callbacks()
        )


def demonstrate_microsoft_login():
    """演示微软账号登录流程"""
    print("\n=== 微软账号登录演示 ===")
    
    example = AccountLoginExample()
    callbacks = example.create_account_callback_group()
    
    # 模拟微软账号登录流程
    callbacks.login.start()
    callbacks.login.progress("获取设备代码", 1, 4)
    callbacks.login.waiting_user_input("请在浏览器中完成授权")
    callbacks.login.progress("等待用户授权", 2, 4)
    callbacks.login.authenticating()
    callbacks.login.progress("获取访问令牌", 3, 4)
    callbacks.login.progress("获取用户信息", 4, 4)
    callbacks.login.success("Steve", "550e8400-e29b-41d4-a716-446655440000", "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...")
    callbacks.login.finished()


def demonstrate_offline_login():
    """演示离线登录流程"""
    print("\n=== 离线登录演示 ===")
    
    example = AccountLoginExample()
    callbacks = example.create_account_callback_group()
    
    # 模拟离线登录流程
    callbacks.login.start()
    callbacks.login.progress("验证用户名", 1, 2)
    callbacks.login.progress("生成离线UUID", 2, 2)
    callbacks.login.success("Alex", "offline-uuid-12345", "offline-token")
    callbacks.login.finished()


def demonstrate_token_refresh():
    """演示令牌刷新流程"""
    print("\n=== 令牌刷新演示 ===")
    
    example = AccountLoginExample()
    callbacks = example.create_account_callback_group()
    
    # 模拟令牌刷新流程
    callbacks.refresh.start()
    callbacks.refresh.validating()
    callbacks.refresh.refreshing()
    callbacks.refresh.success("new_access_token_here", 3600)
    callbacks.refresh.finished()


def demonstrate_account_validation():
    """演示账号验证流程"""
    print("\n=== 账号验证演示 ===")
    
    example = AccountLoginExample()
    callbacks = example.create_account_callback_group()
    
    # 模拟账号验证流程
    callbacks.validation.start()
    callbacks.validation.checking_token()
    callbacks.validation.checking_profile()
    callbacks.validation.valid("Steve", "550e8400-e29b-41d4-a716-446655440000")
    callbacks.validation.finished()


def demonstrate_logout():
    """演示登出流程"""
    print("\n=== 账号登出演示 ===")
    
    example = AccountLoginExample()
    callbacks = example.create_account_callback_group()
    
    # 模拟登出流程
    callbacks.logout.start()
    callbacks.logout.revoking_token()
    callbacks.logout.clearing_cache()
    callbacks.logout.finished()


def main():
    """主函数"""
    print("🎮 Minecraft账号登录回调示例")
    print("=" * 50)
    
    # 演示各种登录场景
    demonstrate_microsoft_login()
    demonstrate_offline_login()
    demonstrate_token_refresh()
    demonstrate_account_validation()
    demonstrate_logout()
    
    print("\n🎉 所有演示完成!")


if __name__ == "__main__":
    main()
