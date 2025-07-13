"""
启动 Minecraft JVM，管理游戏进程的全生命周期
"""
import subprocess
import logging
from typing import List

from Utils.types import ProcessLog

logger = logging.getLogger(__name__)


class GameProcess:
    """游戏进程管理类"""
    def __init__(
            self,
            command: list[str],     # 启动命令
            directory: str,         # 启动目录
    ):
        self.command = command
        self.directory = directory
        self.process = None
        self.process_logs = List[ProcessLog]

