"""
启动 Minecraft JVM，管理游戏进程的全生命周期
"""
import subprocess
import logging
import re
import time
import threading

from typing import List, Optional
from Utils.types import ProcessLog
from Utils.callbacks import ClientProcess

logger = logging.getLogger(__name__)


class GameProcess:
    """游戏进程管理类"""
    def __init__(
            self,
            command: list[str],     # 启动命令
            directory: str,         # 启动目录
            callback: ClientProcess
    ):
        self.command = command
        self.directory = directory
        self.process: Optional[subprocess.Popen] = None
        self.process_logs: List[ProcessLog] = []
        self.pid: Optional[int] = None
        self._stop_event = threading.Event()
        self._log_thread: Optional[threading.Thread] = None

        self.callback = callback

    def start(self):
        """启动游戏进程"""
        try:
            logger.info(f"启动游戏进程，命令: {' '.join(self.command)}")
            logger.info(f"工作目录: {self.directory}")

            # 发送启动信号
            self.callback.start()

            # 启动进程
            self.process = subprocess.Popen(
                self.command,
                cwd=self.directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 将stderr重定向到stdout
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True,
                encoding='utf-8',  # 明确指定UTF-8编码
                errors='replace'   # 遇到编码错误时替换为占位符
            )

            self.pid = self.process.pid
            logger.info(f"游戏进程已启动，PID: {self.pid}")

            # 启动日志监控线程
            self._start_log_monitoring()

            # 启动进程监控线程
            self._start_process_monitoring()

        except Exception as e:
            logger.error(f"启动游戏进程失败: {e}")
            self.callback.error(e)
            raise

    def _start_log_monitoring(self):
        """启动日志监控线程"""
        self._log_thread = threading.Thread(
            target=self._monitor_logs,
            name=f"GameProcess-Log-{self.pid}",
            daemon=True
        )
        self._log_thread.start()
        logger.debug(f"日志监控线程已启动: {self._log_thread.name}")

    def _start_process_monitoring(self):
        """启动进程监控线程"""
        monitor_thread = threading.Thread(
            target=self._monitor_process,
            name=f"GameProcess-Monitor-{self.pid}",
            daemon=True
        )
        monitor_thread.start()
        logger.debug(f"进程监控线程已启动: {monitor_thread.name}")

    def _monitor_logs(self):
        """监控游戏进程的输出日志"""
        if not self.process or not self.process.stdout:
            return

        try:
            while not self._stop_event.is_set() and self.process.poll() is None:
                try:
                    # 读取一行输出
                    line = self.process.stdout.readline()
                    if line:
                        line = line.strip()
                        if line:  # 忽略空行
                            # 解析日志并添加到列表
                            log_entry = self._parse_log(line)
                            self.process_logs.append(log_entry)

                            # 记录到Python日志系统
                            log_level = getattr(logging, log_entry['level'], logging.INFO)
                            logger.log(log_level, f"[Minecraft] {log_entry['message']}")
                    else:
                        # 如果没有更多输出且进程已结束，退出循环
                        if self.process.poll() is not None:
                            break
                        time.sleep(0.1)  # 短暂等待
                except Exception as e:
                    logger.error(f"读取游戏进程输出时出错: {e}")
                    break

        except Exception as e:
            logger.error(f"日志监控线程异常: {e}")
        finally:
            logger.debug(f"日志监控线程结束: {threading.current_thread().name}")

    def _monitor_process(self):
        """监控游戏进程状态"""
        if not self.process:
            return

        try:
            # 等待进程结束
            exit_code = self.process.wait()
            logger.info(f"游戏进程已结束，退出码: {exit_code}")

            # 停止日志监控
            self._stop_event.set()

            # 等待日志线程结束
            if self._log_thread and self._log_thread.is_alive():
                self._log_thread.join(timeout=5.0)

            # 发送进程结束信号
            self.callback.finished(exit_code, self.process_logs)

        except Exception as e:
            logger.error(f"进程监控线程异常: {e}")
            self.callback.error(e)

    def _parse_log(self, log: str) -> ProcessLog:
        """解析Minecraft日志"""
        timestamp = time.time()
        level = 'INFO'
        message = log

        # 匹配 [时间] [线程/级别]: 消息
        match1 = re.match(r'^\[(\d{2}:\d{2}:\d{2})\]\s*\[([^/]+)/([A-Z]+)\]:\s*(.+)$', log, re.IGNORECASE)
        if match1:
            level = match1.group(3).upper()
            message = match1.group(4)
        else:
            # 匹配 [时间] [级别]: 消息
            match2 = re.match(r'^\[(\d{2}:\d{2}:\d{2})\]\s*\[([A-Z]+)\]:\s*(.+)$', log, re.IGNORECASE)
            if match2:
                level = match2.group(2).upper()
                message = match2.group(3)
            else:
                # 匹配 [级别]: 消息
                match3 = re.match(r'^\[([A-Z]+)\]:\s*(.+)$', log, re.IGNORECASE)
                if match3:
                    level = match3.group(1).upper()
                    message = match3.group(2)

        # 级别标准化
        if level in ['WARNING', 'SEVERE']:
            level = 'WARN' if level == 'WARNING' else 'ERROR'

        return ProcessLog(
            level=level,
            message=message,
            timestamp=timestamp
        )

    def std_input(self, data: str):
        """向游戏进程发送输入"""
        if not self.process or not self.process.stdin:
            logger.warning("游戏进程未运行或stdin不可用")
            return False

        try:
            self.process.stdin.write(data + '\n')
            self.process.stdin.flush()
            logger.debug(f"向游戏进程发送输入: {data}")
            return True
        except Exception as e:
            logger.error(f"向游戏进程发送输入失败: {e}")
            return False

    def is_running(self) -> bool:
        """检查游戏进程是否正在运行"""
        return self.process is not None and self.process.poll() is None

    def terminate(self):
        """终止游戏进程"""
        if not self.process:
            return

        try:
            logger.info(f"正在终止游戏进程 PID: {self.pid}")

            # 设置停止事件
            self._stop_event.set()

            # 尝试优雅地终止进程
            self.process.terminate()

            # 等待进程结束，最多等待10秒
            try:
                self.process.wait(timeout=10.0)
                logger.info("游戏进程已优雅终止")
            except subprocess.TimeoutExpired:
                # 如果进程没有在10秒内结束，强制杀死
                logger.warning("游戏进程未在10秒内结束，强制杀死")
                self.process.kill()
                self.process.wait()
                logger.info("游戏进程已被强制杀死")

        except Exception as e:
            logger.error(f"终止游戏进程时出错: {e}")

    def get_logs(self, level_filter: Optional[str] = None, limit: Optional[int] = None) -> List[ProcessLog]:
        """获取进程日志

        Args:
            level_filter: 日志级别过滤器，如 'ERROR', 'WARN', 'INFO', 'DEBUG'
            limit: 返回的日志条数限制

        Returns:
            过滤后的日志列表
        """
        logs = self.process_logs.copy()

        if level_filter:
            logs = [log for log in logs if log['level'] == level_filter.upper()]

        if limit:
            logs = logs[-limit:]  # 返回最新的N条日志

        return logs

