from typing import TypedDict, NotRequired


class DownloadFile(TypedDict):
    path: NotRequired[str]
    sha1: NotRequired[str]
    size: NotRequired[int]
    url: str
