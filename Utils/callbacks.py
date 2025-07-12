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
        
