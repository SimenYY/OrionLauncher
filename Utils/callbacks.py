from typing import Dict, Any, Callable, Protocol, Literal, overload
import logging
import traceback

logger = logging.getLogger(__name__)

class Callbacks:
    def __init__(self,
                 **kwargs: Callable[[Any], Any],
                 ):
        self._callbacks: Dict[str, Callable[[Any], Any]] = kwargs

    def _noop(*args, **kwargs) -> None:
        if logger.getEffectiveLevel() <= logging.DEBUG:
            # 除非 Debug 级别以下，否则不耗费资源用于打印堆栈信息
            stack: traceback.StackSummary = traceback.extract_stack()
            caller: traceback.FrameSummary = stack[-3]      # 跳过 _noop 和 __getitem__
            logger.debug(
                f"Default callback 'empty' was called by {caller.name} in {caller.filename}:{caller.lineno}:\n"
                f"    with {caller.line}"
            )
        return None
    
    def __getitem__(self, key: str) -> Callable[[Any], Any]:
        return self._callbacks.get(key, self._noop)
    
    def __getattr__(self, name: str) -> Callable[[Any], Any]:
        return self._callbacks.get(name, self._noop)
    
class CallbackGroup():
    _EMPTY_CALLBACKS = Callbacks()

    def __init__(self,
                 **kwargs: Callbacks,
                 ):
        self._callbacks: Dict[str, Callbacks] = kwargs

    def __getitem__(self, key: str) -> Callbacks:
        return self._callbacks.get(key, self._default())
    
    def __getattr__(self, name: str) -> Callbacks:
        return self._callbacks.get(name, self._default())
    
    def _default(self) -> Callbacks:
        logger.warning(f"A method requested an empty callback group!")
        if logger.getEffectiveLevel() <= logging.DEBUG:
            stack: traceback.StackSummary = traceback.extract_stack()
            caller: traceback.FrameSummary = stack[-3]
            logger.warning(
                f"Default callback group was called by {caller.name} in {caller.filename}:{caller.lineno}:\n"
                f"    with {caller.line}"
            )
        return self._EMPTY_CALLBACKS

class IDownloadSingle(Protocol):
    """单一下载任务信号"""
    def start(self):
        """任务开始信号"""
    def progress(self, progress: int):
        """任务进度；0-100"""
    def bytes_downloaded(self, downloaded: int, total: int):
        """字节级进度；已下载字节数和总字节数"""
    def speed(self, speed: int):
        """任务下载速度；单位：字节/秒"""
    def finished(self):
        """任务完成信号"""
    def error(self, error: Exception):
        """任务错误信号，传递错误"""

class IDownloadMultiThread(Protocol):
    """
    多线程任务调度
    """
    def start(self):
        """任务开始信号"""
    def tasks_progress(self, progress: Dict[str, int]):
        """任务进度；0-100"""
    def size(self, size: int):
        """任务数据大小；单位：字节"""
    def downloaded_size(self, size: int):
        """任务已下载的总大小；单位：字节"""
    def speed(self, speed: int):
        """任务下载速度；单位：字节/秒"""
    def progress(self, progress: int):
        """任务总进度；0-100"""
    def finished(self):
        """整个下载任务完成信号"""
    def error(self, error: Exception):
        """整个下载任务错误信号，传递错误"""

class IInstallGame(Protocol):
    """
    安装游戏信号
    """
    def start(self):
        """任务开始信号"""
    def finished(self):
        """任务完成信号"""
    def error(self, error: Exception):
        """任务错误信号，传递错误"""

class IVerifyGameFile(Protocol):
    """
    验证游戏文件信号
    """
    def start(self):
        """任务开始信号"""
    def finished(self):
        """任务完成信号"""
    def error(self, error: Exception):
        """任务错误信号，传递错误"""

class IInstallAddon(Protocol):
    """
    附加组件安装（Fabric/Forge/NeoForge/Quilt）
    """
    def start(self):
        """任务开始信号"""
    def finished(self):
        """任务完成信号"""
    def error(self, error: Exception):
        """任务错误信号，传递错误"""


class IAccountLogin(Protocol):
    """
    账号登录信号
    """
    def start(self):
        """登录开始信号"""
    def authenticating(self):
        """正在进行身份验证"""
    def device_code(self, code: str):
        """设备代码，等待用户输入"""
    def progress(self, step: str, current: int, total: int):
        """登录进度，step为当前步骤描述"""
    def success(self, username: str, uuid: str, access_token: str):
        """登录成功，返回用户名、UUID和访问令牌"""
    def finished(self):
        """登录流程完成信号"""
    def error(self, error: Exception):
        """登录错误信号，传递错误"""


class IOfflineAccountAdd(Protocol):
    """
    离线账号添加信号
    """
    def start(self):
        """添加开始信号"""
    def finished(self):
        """添加完成信号"""
    def error(self, error: Exception):
        """添加错误信号，传递错误"""


class IAccountRefresh(Protocol):
    """
    账号令牌刷新信号
    """
    def start(self):
        """刷新开始信号"""
    def validating(self):
        """正在验证当前令牌"""
    def refreshing(self):
        """正在刷新令牌"""
    def success(self, access_token: str, expires_in: int):
        """刷新成功，返回新令牌和过期时间"""
    def finished(self):
        """刷新完成信号"""
    def error(self, error: Exception):
        """刷新错误信号，传递错误"""


class IAccountLogout(Protocol):
    """
    账号登出信号
    """
    def start(self):
        """登出开始信号"""
    def revoking_token(self):
        """正在撤销令牌"""
    def clearing_cache(self):
        """正在清理缓存"""
    def finished(self):
        """登出完成信号"""
    def error(self, error: Exception):
        """登出错误信号，传递错误"""


class IAccountValidation(Protocol):
    """
    账号验证信号
    """
    def start(self):
        """验证开始信号"""
    def checking_token(self):
        """正在检查令牌有效性"""
    def checking_profile(self):
        """正在检查用户档案"""
    def valid(self, username: str, uuid: str):
        """验证通过，返回用户信息"""
    def invalid(self, reason: str):
        """验证失败，返回失败原因"""
    def finished(self):
        """验证完成信号"""
    def error(self, error: Exception):
        """验证错误信号，传递错误"""


class InstallationCallbackGroup(CallbackGroup):
    """
    类型化的安装器回调组
    """
    @overload
    def __getattr__(self, name: Literal["download"]) -> IDownloadMultiThread:
        ...

    @overload
    def __getattr__(self, name: Literal["install_game"]) -> IInstallGame:
        ...

    @overload
    def __getattr__(self, name: Literal["install_forge"]) -> IInstallAddon:
        ...

    @overload
    def __getattr__(self, name: Literal["install_neoforge"]) -> IInstallAddon:
        ...

    @overload
    def __getattr__(self, name: Literal["install_fabric"]) -> IInstallAddon:
        ...

    @overload
    def __getattr__(self, name: Literal["install_quilt"]) -> IInstallAddon:
        ...

    @overload
    def __getattr__(self, name: Literal["install_liteloader"]) -> IInstallAddon:
        ...

    @overload
    def __getattr__(self, name: Literal["verify"]) -> IVerifyGameFile:
        ...

    def __getattr__(self, name: str) -> Any:
        return super().__getattr__(name)


class AccountCallbackGroup(CallbackGroup):
    """
    类型化的账号管理回调组

    支持多种账号操作的回调管理：
    - login: 账号登录流程
    - refresh: 令牌刷新流程
    - logout: 账号登出流程
    - validation: 账号验证流程

    使用示例:
        callbacks = AccountCallbackGroup(
            login=Callbacks(
                start=lambda: print("开始登录"),
                success=lambda username, uuid, token: print(f"登录成功: {username}"),
                error=lambda e: print(f"登录失败: {e}")
            ),
            refresh=Callbacks(
                start=lambda: print("开始刷新令牌"),
                success=lambda token, expires: print("令牌刷新成功")
            )
        )
    """
    @overload
    def __getattr__(self, name: Literal["login"]) -> IAccountLogin:
        ...

    @overload
    def __getattr__(self, name: Literal["refresh"]) -> IAccountRefresh:
        ...

    @overload
    def __getattr__(self, name: Literal["logout"]) -> IAccountLogout:
        ...

    @overload
    def __getattr__(self, name: Literal["validation"]) -> IAccountValidation:
        ...

    def __getattr__(self, name: str) -> Any:
        return super().__getattr__(name)
