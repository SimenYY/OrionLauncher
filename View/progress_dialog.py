"""
进度对话框模块

显示任务进度的对话框
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QProgressBar,
)
from PySide6.QtCore import Slot

from Utils.locale_manager import LocaleManager
from .theme_manager import ThemeManager


class ProgressDialog(QDialog):
    """
    进度对话框

    显示任务进度的对话框
    """

    def __init__(self, title: str, parent=None):
        """
        初始化进度对话框

        Args:
            title: 对话框标题
            parent: 父部件
        """
        super().__init__(parent)

        # 设置窗口属性
        self.setWindowTitle(title)
        self.setMinimumSize(400, 150)
        self.setModal(True)

        # 初始化UI
        self._init_ui()

        # 设置UI文字语言
        self._set_text()

    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 创建任务标签
        self.task_label = QLabel("正在处理...")
        main_layout.addWidget(self.task_label)

        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # 创建详细信息标签
        self.detail_label = QLabel()
        self.detail_label.setWordWrap(True)
        main_layout.addWidget(self.detail_label)

        # 添加弹性空间
        main_layout.addStretch(1)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 添加弹性空间
        button_layout.addStretch(1)

        # 创建取消按钮
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # 添加UI样式
        self._set_style_sheet()

    def _set_style_sheet(self):
        """设置/刷新所有UI组件样式"""
        self.task_label.setStyleSheet(
            f"color: {ThemeManager().get("text")}; font-size: 16px; background: transparent;"
        )

        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {ThemeManager().get("progress-bar-background")};
                color: {ThemeManager().get("text")};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {ThemeManager().get("progress-bar")};
                border-radius: 4px;
            }}
        """
        )

        self.detail_label.setStyleSheet(
            f"color: {ThemeManager().get("label")}; font-size: 12px; background: transparent;"
        )

        self.cancel_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("neutral-selection-background")};
                color: {ThemeManager().get("text")};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("neutral-selection-hover")};
            }}
        """
        )

    def _set_text(self):
        """设置/刷新所有UI组件的文字"""
        self.task_label.setText(LocaleManager().get("processing"))
        self.cancel_button.setText(LocaleManager().get("cancel"))

    def set_task(self, task_name: str):
        """
        设置任务名称

        Args:
            task_name: 任务名称
        """
        self.task_label.setText(task_name)

    def set_progress(self, value: int, maximum: int = 100):
        """
        设置进度

        Args:
            value: 当前进度值
            maximum: 最大进度值
        """
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def set_detail(self, detail: str):
        """
        设置详细信息

        Args:
            detail: 详细信息
        """
        self.detail_label.setText(detail)

    @Slot()
    def on_cancel_clicked(self):
        """处理取消按钮点击事件"""
        self.reject()

    def connect_cancel_button(self, slot):
        """
        连接取消按钮的点击事件

        Args:
            slot: 槽函数
        """
        self.cancel_button.clicked.disconnect(self.on_cancel_clicked)
        self.cancel_button.clicked.connect(slot)
