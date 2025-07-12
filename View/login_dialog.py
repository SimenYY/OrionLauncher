"""
登录对话框模块

提供用户登录界面
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFrame,
)
from PySide6.QtCore import Qt, Slot

from Controller import AccountController
from .theme_manager import ThemeManager


class LoginDialog(QDialog):
    """
    登录对话框

    提供用户登录界面
    """

    def __init__(self, account_controller: AccountController, parent=None):
        """
        初始化登录对话框

        Args:
            account_controller: 账户控制器
            parent: 父部件
        """
        super().__init__(parent)

        self.account_controller = account_controller

        # 设置窗口属性
        self.setWindowTitle("用户登录")
        self.setMinimumSize(400, 300)
        self.setModal(True)

        # 设置窗口样式
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {ThemeManager().get("qdialog-background")};
                border-radius: 10px;
            }}
        """
        )

        # 初始化UI
        self._init_ui()

        # 连接信号槽
        self._connect_signals()

    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 创建标题
        title_label = QLabel("登录您的账户")
        title_label.setStyleSheet(
            f"color: {ThemeManager().get("title")}; font-size: 20px; font-weight: bold; background: transparent;"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # 创建表单
        form_frame = QFrame()
        form_frame.setStyleSheet(
            f"""
            background-color: {ThemeManager().get("qframe-background")};
            border-radius: 8px;
        """
        )
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # 用户名输入
        username_label = QLabel("用户名:")
        username_label.setStyleSheet(
            f"color: {ThemeManager().get("label")}; font-size: 14px; background: transparent;"
        )
        self.username_edit = QLineEdit()
        self.username_edit.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {ThemeManager().get("text-box-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ThemeManager().get("focus-border")};
            }}
        """
        )
        self.username_edit.setPlaceholderText("输入您的用户名")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_edit)

        # 密码输入
        password_label = QLabel("密码:")
        password_label.setStyleSheet(
            f"color: {ThemeManager().get("label")}; font-size: 14px; background: transparent;"
        )
        self.password_edit = QLineEdit()
        self.password_edit.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {ThemeManager().get("text-box-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ThemeManager().get("focus-border")};
            }}
        """
        )
        self.password_edit.setPlaceholderText("输入您的密码")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_edit)

        # 添加表单到主布局
        main_layout.addWidget(form_frame)

        # 创建错误信息标签（默认隐藏）
        self.error_label = QLabel()
        self.error_label.setStyleSheet(
            f"color: {ThemeManager().get("negative-selection-background")}; font-size: 14px; background: transparent;"
        )
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        main_layout.addWidget(self.error_label)

        # 添加弹性空间
        main_layout.addStretch(1)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("neutral-selection-background")};
                color: {ThemeManager().get("text")};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("neutral-selection-hover")};
            }}
        """
        )

        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("selection-background")};
                color: {ThemeManager().get("text")};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("selection-hover")};
            }}
            QPushButton:disabled {{
                background-color: {ThemeManager().get("disabled-selection")};
                color: {ThemeManager().get("disabled-selection-text")};
            }}
        """
        )

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)

        main_layout.addLayout(button_layout)

    def _connect_signals(self):
        """连接信号槽"""
        # 按钮信号
        self.cancel_button.clicked.connect(self.reject)
        self.login_button.clicked.connect(self._handle_login_clicked)

        # 账户控制器信号
        self.account_controller.login_success.connect(self._handle_login_success)
        self.account_controller.login_failed.connect(self._handle_login_failed)

        # 输入框信号
        self.username_edit.textChanged.connect(self._validate_inputs)
        self.password_edit.textChanged.connect(self._validate_inputs)

    def _validate_inputs(self):
        """验证输入"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        # 验证输入是否有效
        self.login_button.setEnabled(bool(username and password))

    @Slot()
    def _handle_login_clicked(self):
        """处理登录按钮点击事件"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        # 禁用登录按钮
        self.login_button.setEnabled(False)
        self.login_button.setText("正在登录...")

        # 隐藏错误信息
        self.error_label.setVisible(False)

        # 执行登录
        self.account_controller.login(username, password)

    @Slot(dict)
    def _handle_login_success(self, account_info):
        """
        处理登录成功事件

        Args:
            account_info: 账户信息
        """
        self.accept()

    @Slot(str)
    def _handle_login_failed(self, error_msg: str):
        """
        处理登录失败事件

        Args:
            error_msg: 错误信息
        """
        # 显示错误信息
        self.error_label.setText(error_msg)
        self.error_label.setVisible(True)

        # 恢复登录按钮
        self.login_button.setEnabled(True)
        self.login_button.setText("登录")
