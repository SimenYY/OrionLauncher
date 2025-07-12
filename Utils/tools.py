"""
通用工具模块

本模块提供各种通用的工具函数和辅助功能，包括：

- 空回调函数
- 调试工具
- 其他通用辅助函数

这些工具函数旨在提高代码的可重用性和开发效率。
"""

import logging
import traceback

logger = logging.getLogger(__name__)


def empty(*args, **kwargs) -> None:
    """
    空回调函数，接受任意参数但不执行任何操作。

    这是一个通用的空操作函数，通常用作默认回调函数。在DEBUG日志级别下，
    会记录调用此函数的详细信息，帮助开发者了解何时何地使用了默认回调。

    Args:
        *args: 任意位置参数，将被忽略
        **kwargs: 任意关键字参数，将被忽略

    Returns:
        None: 总是返回 None

    Example:
        >>> # 作为默认回调使用
        >>> callback = empty
        >>> callback("some", "args", key="value")  # 不会有任何输出

        >>> # 在需要回调但不想执行任何操作时使用
        >>> process_data(data, on_complete=empty)

    Note:
        在DEBUG日志级别下，此函数会记录调用堆栈信息。
        在生产环境中，为了性能考虑，建议将日志级别设置为INFO或更高。
    """
    if logger.getEffectiveLevel() <= logging.DEBUG:
        # 除非 Debug 级别以下，否则不耗费资源用于打印堆栈信息
        stack: traceback.StackSummary = traceback.extract_stack()
        caller: traceback.FrameSummary = stack[-2]
        logger.debug(
            f"Default callback 'empty' was called by {caller.name} in {caller.filename}:{caller.lineno}:\n"
            f"    with {caller.line}"
        )
    return None


def delete_layout(layout):
    """删除所有UI组件及其所有子组件"""
    try:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
            elif child_layout:
                delete_layout(layout)
    except RuntimeError:
        pass
