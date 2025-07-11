"""
OrionLauncher异常状态码定义

异常状态码采用5位数字格式：XYZAB
│││││
│││└┴─ 具体异常类型 (01-99)
││└─── 子模块类型 (0-9)
│└──── 主模块类型 (0-9)
└───── 应用层级 (1-9)

应用层级分配：
1 - Core层异常
2 - Controller层异常
3 - View层异常
4 - Utils层异常
9 - 系统异常包装器
"""

# ===== Core层异常 (1xxxx) =====


class CoreErrorCodes:
    """Core层异常状态码"""

    # 通用Core异常 (10xxx)
    CORE_GENERAL_ERROR = 10001
    CORE_INITIALIZATION_ERROR = 10002
    CORE_UNKNOWN_ERROR = 10099

    # 网络相关异常 (11xxx)
    # 通用网络异常 (110xx)
    NETWORK_GENERAL_ERROR = 11001
    NETWORK_CONNECTION_ERROR = 11002
    NETWORK_TIMEOUT_ERROR = 11003
    NETWORK_DNS_ERROR = 11004
    NETWORK_SSL_ERROR = 11005

    # 下载相关异常 (111xx)
    DOWNLOAD_GENERAL_ERROR = 11101
    DOWNLOAD_FILE_NOT_FOUND = 11102
    DOWNLOAD_PERMISSION_DENIED = 11103
    DOWNLOAD_DISK_FULL = 11104
    DOWNLOAD_CHECKSUM_MISMATCH = 11105
    DOWNLOAD_INTERRUPTED = 11106
    DOWNLOAD_SPEED_TOO_SLOW = 11107

    # API调用异常 (112xx)
    API_GENERAL_ERROR = 11201
    API_INVALID_REQUEST = 11202
    API_UNAUTHORIZED = 11203
    API_FORBIDDEN = 11204
    API_NOT_FOUND = 11205
    API_SERVER_ERROR = 11206
    API_RATE_LIMITED = 11207
    API_INVALID_RESPONSE = 11208

    # 认证相关异常 (113xx)
    AUTH_GENERAL_ERROR = 11301
    AUTH_INVALID_CREDENTIALS = 11302
    AUTH_TOKEN_EXPIRED = 11303
    AUTH_TOKEN_INVALID = 11304
    AUTH_PERMISSION_DENIED = 11305
    AUTH_ACCOUNT_LOCKED = 11306
    AUTH_MFA_REQUIRED = 11307

    # 文件系统异常 (12xxx)
    # 通用文件系统异常 (120xx)
    FILESYSTEM_GENERAL_ERROR = 12001

    # 文件操作异常 (121xx)
    FILE_NOT_FOUND = 12101
    FILE_PERMISSION_DENIED = 12102
    FILE_ALREADY_EXISTS = 12103
    FILE_IN_USE = 12104
    FILE_CORRUPTED = 12105
    FILE_TOO_LARGE = 12106

    # 目录操作异常 (122xx)
    DIRECTORY_NOT_FOUND = 12201
    DIRECTORY_PERMISSION_DENIED = 12202
    DIRECTORY_NOT_EMPTY = 12203
    DIRECTORY_CREATION_FAILED = 12204

    # 配置相关异常 (13xxx)
    CONFIG_GENERAL_ERROR = 13001
    CONFIG_NOT_FOUND = 13002
    CONFIG_INVALID_FORMAT = 13003
    CONFIG_VALIDATION_FAILED = 13004
    CONFIG_SAVE_FAILED = 13005
    CONFIG_LOAD_FAILED = 13006

    # 游戏相关异常 (14xxx)
    # 通用游戏异常 (140xx)
    GAME_GENERAL_ERROR = 14001

    # 游戏启动异常 (141xx)
    GAME_LAUNCH_FAILED = 14101
    GAME_EXECUTABLE_NOT_FOUND = 14102
    GAME_INCOMPATIBLE_SYSTEM = 14103
    GAME_MISSING_DEPENDENCIES = 14104
    GAME_ALREADY_RUNNING = 14105

    # 游戏安装异常 (142xx)
    GAME_INSTALL_FAILED = 14201
    GAME_INSTALL_SPACE_INSUFFICIENT = 14202
    GAME_INSTALL_CORRUPTED = 14203
    GAME_UNINSTALL_FAILED = 14204


# ===== Controller层异常 (2xxxx) =====


class ControllerErrorCodes:
    """Controller层异常状态码"""

    # 通用Controller异常 (20xxx)
    CONTROLLER_GENERAL_ERROR = 20001
    CONTROLLER_INITIALIZATION_FAILED = 20002

    # 异步任务异常 (21xxx)
    ASYNC_TASK_FAILED = 21001
    ASYNC_TASK_TIMEOUT = 21002
    ASYNC_TASK_CANCELLED = 21003
    ASYNC_TASK_QUEUE_FULL = 21004

    # 账户控制器异常 (22xxx)
    ACCOUNT_CONTROLLER_ERROR = 22001
    ACCOUNT_LOGIN_FAILED = 22002
    ACCOUNT_LOGOUT_FAILED = 22003
    ACCOUNT_REFRESH_FAILED = 22004

    # 游戏控制器异常 (23xxx)
    GAME_CONTROLLER_ERROR = 23001
    GAME_LIST_LOAD_FAILED = 23002
    GAME_INFO_FETCH_FAILED = 23003

    # 设置控制器异常 (24xxx)
    SETTINGS_CONTROLLER_ERROR = 24001
    SETTINGS_LOAD_FAILED = 24002
    SETTINGS_SAVE_FAILED = 24003


# ===== View层异常 (3xxxx) =====


class ViewErrorCodes:
    """View层异常状态码"""

    # 通用View异常 (30xxx)
    VIEW_GENERAL_ERROR = 30001
    VIEW_INITIALIZATION_FAILED = 30002

    # UI异常 (31xxx)
    UI_COMPONENT_ERROR = 31001
    UI_RENDER_ERROR = 31002
    UI_EVENT_HANDLER_ERROR = 31003
    UI_RESOURCE_LOAD_ERROR = 31004

    # 窗口相关异常 (32xxx)
    WINDOW_CREATION_FAILED = 32001
    WINDOW_SHOW_FAILED = 32002
    WINDOW_CLOSE_FAILED = 32003

    # 对话框异常 (33xxx)
    DIALOG_CREATION_FAILED = 33001
    DIALOG_MODAL_ERROR = 33002


# ===== Utils层异常 (4xxxx) =====


class UtilsErrorCodes:
    """Utils层异常状态码"""

    # 通用Utils异常 (40xxx)
    UTILS_GENERAL_ERROR = 40001

    # 仓库异常 (41xxx)
    REPOSITORY_ERROR = 41001
    REPOSITORY_PATH_ERROR = 41002
    REPOSITORY_ACCESS_ERROR = 41003


# ===== 系统异常包装器 (9xxxx) =====


class SystemErrorCodes:
    """系统异常包装器状态码"""

    SYSTEM_EXCEPTION_WRAPPER = 90001
    UNKNOWN_SYSTEM_ERROR = 90099


# ===== 异常状态码映射表 =====

# 异常类到状态码的映射
EXCEPTION_CODE_MAPPING = {
    # Core层异常
    "CoreException": CoreErrorCodes.CORE_GENERAL_ERROR,
    "NetworkException": CoreErrorCodes.NETWORK_GENERAL_ERROR,
    "DownloadException": CoreErrorCodes.DOWNLOAD_GENERAL_ERROR,
    "ApiException": CoreErrorCodes.API_GENERAL_ERROR,
    "AuthenticationException": CoreErrorCodes.AUTH_GENERAL_ERROR,
    "FileSystemException": CoreErrorCodes.FILESYSTEM_GENERAL_ERROR,
    "FileNotFoundException": CoreErrorCodes.FILE_NOT_FOUND,
    "FilePermissionException": CoreErrorCodes.FILE_PERMISSION_DENIED,
    "FileOperationException": CoreErrorCodes.FILESYSTEM_GENERAL_ERROR,
    "ConfigException": CoreErrorCodes.CONFIG_GENERAL_ERROR,
    "InvalidConfigException": CoreErrorCodes.CONFIG_INVALID_FORMAT,
    "ConfigNotFoundException": CoreErrorCodes.CONFIG_NOT_FOUND,
    "GameException": CoreErrorCodes.GAME_GENERAL_ERROR,
    "GameLaunchException": CoreErrorCodes.GAME_LAUNCH_FAILED,
    "GameInstallException": CoreErrorCodes.GAME_INSTALL_FAILED,
    # Controller层异常
    "ControllerException": ControllerErrorCodes.CONTROLLER_GENERAL_ERROR,
    "InitializationException": ControllerErrorCodes.CONTROLLER_INITIALIZATION_FAILED,
    "AsyncTaskException": ControllerErrorCodes.ASYNC_TASK_FAILED,
    # View层异常
    "ViewException": ViewErrorCodes.VIEW_GENERAL_ERROR,
    "UIException": ViewErrorCodes.UI_COMPONENT_ERROR,
    # Utils层异常
    "UtilsException": UtilsErrorCodes.UTILS_GENERAL_ERROR,
    "RepositoryException": UtilsErrorCodes.REPOSITORY_ERROR,
    # 系统异常包装器
    "WrappedSystemException": SystemErrorCodes.SYSTEM_EXCEPTION_WRAPPER,
}


def get_error_code_for_exception(exception_class_name: str) -> int:
    """
    根据异常类名获取对应的错误状态码

    Args:
        exception_class_name (str): 异常类名

    Returns:
        int: 对应的错误状态码，如果未找到则返回通用错误码
    """
    return EXCEPTION_CODE_MAPPING.get(exception_class_name, 99999)


def format_error_code(code: int) -> str:
    """
    格式化错误状态码为可读形式

    Args:
        code (int): 错误状态码

    Returns:
        str: 格式化后的错误状态码字符串
    """
    if code < 10000:
        return f"E{code:04d}"
    else:
        return f"E{code:05d}"


def decode_error_code(code: int) -> dict:
    """
    解析错误状态码的层级信息

    Args:
        code (int): 错误状态码

    Returns:
        dict: 包含层级信息的字典
    """
    if code < 10000:
        # 4位数字格式，转换为5位
        code = code * 10

    code_str = str(code).zfill(5)

    layer_map = {
        "1": "Core层",
        "2": "Controller层",
        "3": "View层",
        "4": "Utils层",
        "9": "系统层",
    }

    module_map = {
        "1": {
            "0": "通用Core",
            "1": "网络相关",
            "2": "文件系统",
            "3": "配置相关",
            "4": "游戏相关",
        },
        "2": {
            "0": "通用Controller",
            "1": "异步任务",
            "2": "账户控制器",
            "3": "游戏控制器",
            "4": "设置控制器",
        },
        "3": {"0": "通用View", "1": "UI组件", "2": "窗口管理", "3": "对话框"},
        "4": {"0": "通用Utils", "1": "仓库管理"},
        "9": {"0": "系统异常"},
    }

    layer = code_str[0]
    module = code_str[1]
    submodule = code_str[2]
    error_type = code_str[3:5]

    return {
        "layer": layer_map.get(layer, "未知层级"),
        "module": module_map.get(layer, {}).get(module, "未知模块"),
        "submodule": submodule,
        "error_type": error_type,
        "full_code": code,
    }
