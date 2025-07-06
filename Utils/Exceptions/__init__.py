from typing import Optional
from .code import get_error_code_for_exception, format_error_code, decode_error_code


class OrionException(Exception):
    """
    OrionLauncher异常基类
    
    所有自定义异常都应继承此类，以便于统一处理和识别。
    
    Attributes:
        message (str): 异常消息
        code (int): 错误代码
        details (dict): 附加的错误详情
    """
    def __init__(self, message: str, code: int = None, details: Optional[dict] = None):
        """
        初始化OrionException实例
        
        Args:
            message (str): 异常消息
            code (int, optional): 错误代码，如果为None则自动获取
            details (dict, optional): 附加的错误详情，默认为None
        """
        self.message = message
        # 如果没有提供code，则根据异常类名自动获取
        if code is None:
            code = get_error_code_for_exception(self.__class__.__name__)
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """返回异常的字符串表示"""
        if self.code:
            formatted_code = format_error_code(self.code)
            return f"[{formatted_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> dict:
        """将异常转换为字典格式"""
        return {
            'message': self.message,
            'code': self.code,
            'formatted_code': format_error_code(self.code),
            'exception_type': self.__class__.__name__,
            'details': self.details
        }


# ===== 核心异常 =====

class CoreException(OrionException):
    """核心模块异常基类"""
    pass


# ----- 网络相关异常 -----

class NetworkException(CoreException):
    """网络相关异常基类"""
    pass


class DownloadException(NetworkException):
    """下载异常"""
    pass


class ApiException(NetworkException):
    """API调用异常"""
    pass


class AuthenticationException(NetworkException):
    """认证异常"""
    pass


# ----- 文件系统相关异常 -----

class FileSystemException(CoreException):
    """文件系统相关异常基类"""
    pass


class FileNotFoundException(FileSystemException):
    """文件未找到异常"""
    pass


class FilePermissionException(FileSystemException):
    """文件权限异常"""
    pass


class FileOperationException(FileSystemException):
    """文件操作异常"""
    pass


# ----- 配置相关异常 -----

class ConfigException(CoreException):
    """配置相关异常基类"""
    pass


class InvalidConfigException(ConfigException):
    """无效配置异常"""
    pass


class ConfigNotFoundException(ConfigException):
    """配置未找到异常"""
    pass


# ----- 游戏相关异常 -----

class GameException(CoreException):
    """游戏相关异常基类"""
    pass


class GameLaunchException(GameException):
    """游戏启动异常"""
    pass


class GameInstallException(GameException):
    """游戏安装异常"""
    pass


# ===== 控制器异常 =====

class ControllerException(OrionException):
    """控制器异常基类"""
    pass


class InitializationException(ControllerException):
    """初始化异常"""
    pass


class AsyncTaskException(ControllerException):
    """异步任务异常"""
    pass


# ===== 视图异常 =====

class ViewException(OrionException):
    """视图异常基类"""
    pass


class UIException(ViewException):
    """UI相关异常"""
    pass


# ===== 工具异常 =====

class UtilsException(OrionException):
    """工具异常基类"""
    pass


class RepositoryException(UtilsException):
    """仓库异常"""
    pass


# ===== 系统异常包装器 =====

class WrappedSystemException(OrionException):
    """
    系统异常包装器
    
    用于包装系统异常，将其转换为OrionException
    
    Attributes:
        original_exception (Exception): 原始系统异常
    """
    def __init__(self, original_exception: Exception, message: Optional[str] = None):
        """
        初始化WrappedSystemException实例
        
        Args:
            original_exception (Exception): 原始系统异常
            message (str, optional): 自定义消息，如果为None则使用原始异常消息
        """
        self.original_exception = original_exception
        message = message or str(original_exception)
        details = {"exception_type": type(original_exception).__name__}
        super().__init__(message, details=details)


# 导出工具函数
__all__ = [
    # 基础异常类
    'OrionException',
    
    # Core层异常
    'CoreException', 'NetworkException', 'DownloadException', 'ApiException', 
    'AuthenticationException', 'FileSystemException', 'FileNotFoundException',
    'FilePermissionException', 'FileOperationException', 'ConfigException',
    'InvalidConfigException', 'ConfigNotFoundException', 'GameException',
    'GameLaunchException', 'GameInstallException',
    
    # Controller层异常
    'ControllerException', 'InitializationException', 'AsyncTaskException',
    
    # View层异常
    'ViewException', 'UIException',
    
    # Utils层异常
    'UtilsException', 'RepositoryException',
    
    # 系统异常包装器
    'WrappedSystemException',
    
    # 工具函数
    'decode_error_code', 'get_error_code_for_exception', 'format_error_code'
] 