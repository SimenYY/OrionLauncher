import abc
from typing import Optional, Dict, Any, Callable

from PySide6.QtCore import QObject, Signal, Slot, QThread


class BaseController(QObject):
    """控制器基类，作为GUI与Core功能模块交互的桥梁。

    所有控制器应继承此类，并实现相应的抽象方法。
    控制器遵循单线程异步模式，对于IO密集型任务使用信号槽机制。

    Note:
        这是一个抽象基类，子类必须实现 :meth:`initialize` 方法。

    Attributes:
        error_occurred (Signal): 错误信号，携带错误消息字符串
        task_progress (Signal): 任务进度信号，携带任务名和进度百分比
        task_completed (Signal): 任务完成信号，携带任务名

    Example:
        创建一个自定义控制器::

            class MyController(BaseController):
                def initialize(self) -> bool:
                    # 初始化逻辑
                    return True
    """

    # 通用信号
    error_occurred = Signal(str)
    """Signal[str]: 当发生错误时发出，携带错误消息。"""

    task_progress = Signal(str, int)
    """Signal[str, int]: 报告任务进度，参数为(任务名, 进度百分比)。"""

    task_completed = Signal(str)
    """Signal[str]: 任务完成时发出，携带任务名。"""

    def __init__(self, parent: Optional[QObject] = None):
        """初始化控制器基类。

        Args:
            parent: 父QObject对象，用于Qt对象树管理
        """
        super().__init__(parent)
        self._threads: Dict[str, QThread] = {}  # 存储线程对象
        self._workers: Dict[str, "AsyncTaskWorker"] = {}  # 存储工作对象

    @abc.abstractmethod
    def initialize(self) -> bool:
        """初始化控制器。

        子类必须实现此方法来执行具体的初始化逻辑。

        Returns:
            初始化是否成功

        Raises:
            NotImplementedError: 如果子类未实现此方法
        """
        raise NotImplementedError("子类必须实现initialize方法")

    def run_async_task(
        self, task_name: str, task_func: Callable[..., Any], *args, **kwargs
    ) -> None:
        """在单独的线程中运行异步任务。

        这个方法创建一个新的工作线程来执行任务函数，避免阻塞主线程。
        如果已经有同名任务在运行，会先停止旧任务再启动新任务。

        Args:
            task_name: 任务的唯一标识符
            task_func: 要执行的任务函数
            *args: 传递给任务函数的位置参数
            **kwargs: 传递给任务函数的关键字参数

        Note:
            任务执行过程中的进度通过 :attr:`task_progress` 信号报告。
            任务完成时通过 :attr:`task_completed` 信号通知。
            任务出错时通过 :attr:`error_occurred` 信号报告。

        Example:
            运行一个下载任务::

                controller.run_async_task(
                    "download_file",
                    self.download_function,
                    "http://example.com/file.zip",
                    "/path/to/save"
                )
        """
        # 如果已经有同名任务在运行，先停止它
        try:
            if task_name in self._threads and self._threads[task_name].isRunning():
                self._threads[task_name].quit()
                self._threads[task_name].wait()
        except RuntimeError:
            del self._threads[task_name]

        # 创建工作线程
        thread = QThread()
        # 创建工作对象
        worker = AsyncTaskWorker(task_func, *args, **kwargs)
        # 将工作对象移动到线程
        worker.moveToThread(thread)
        # 连接信号
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.progress.connect(lambda p: self.task_progress.emit(task_name, p))
        worker.error.connect(self.error_occurred.emit)
        worker.result.connect(lambda: self.task_completed.emit(task_name))

        # 存储线程和工作对象
        self._threads[task_name] = thread
        self._workers[task_name] = worker

        # 启动线程
        thread.start()

    def cleanup(self) -> None:
        """清理资源，关闭所有线程。

        这个方法应该在控制器销毁前调用，确保所有后台线程正确关闭。

        Note:
            会等待每个线程最多1秒钟，超时则强制退出。
        """
        # 停止所有线程
        try:
            for name in list(self._threads.keys()):
                thread = self._threads.get(name)
                if thread and thread.isRunning():
                    thread.quit()
                    thread.wait(1000)  # 等待最多1秒

                # 从字典中移除
                self._threads.pop(name, None)
                self._workers.pop(name, None)
        except RuntimeError:
            # 忽略已删除对象的错误
            pass


class AsyncTaskWorker(QObject):
    """异步任务工作器。

    在独立线程中执行任务函数，并通过信号报告结果。

    Attributes:
        finished (Signal): 任务完成信号
        error (Signal): 错误信号，携带错误消息
        progress (Signal): 进度信号，携带进度值
        result (Signal): 结果信号，携带任务返回值
    """

    finished = Signal()
    """Signal: 任务完成时发出。"""

    error = Signal(str)
    """Signal[str]: 任务出错时发出，携带错误消息。"""

    progress = Signal(int)
    """Signal[int]: 报告任务进度，参数为进度百分比(0-100)。"""

    result = Signal(object)
    """Signal[object]: 任务成功完成时发出，携带返回值。"""

    def __init__(self, func: Callable[..., Any], *args, **kwargs):
        """初始化工作器。

        Args:
            func: 要执行的任务函数
            *args: 传递给任务函数的位置参数
            **kwargs: 传递给任务函数的关键字参数
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self) -> None:
        """执行任务。

        这个方法在工作线程中被调用，执行任务函数并发出相应信号。

        Note:
            任务成功时发出 :attr:`result` 信号。
            任务失败时发出 :attr:`error` 信号。
            无论成功失败都会发出 :attr:`finished` 信号。
        """
        try:
            result = self.func(*self.args, **self.kwargs)
            self.result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
