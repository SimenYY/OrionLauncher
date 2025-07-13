from typing import TypedDict, NotRequired, List, Dict


class DownloadFile(TypedDict):
    path: NotRequired[str]
    sha1: NotRequired[str]
    size: NotRequired[int]
    url: str

class UserInfo(TypedDict):
    id: str
    name: str
    type: str     # 账号的登录形式 Offline / Microsoft / ...
    access_token: NotRequired[str]
    refresh_token: NotRequired[str]
    skins: NotRequired[List[Dict[str, str]]]
    capes: NotRequired[List]

class ProcessLog(TypedDict):
    level: str
    message: str
    timestamp: int
    
