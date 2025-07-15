"""
主窗口模块

应用程序的主窗口，包含侧边栏导航和内容区域
"""

import os
from typing import Dict, Any
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QFrame,
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QCloseEvent, QPainter, QColor

from Core.Repository import path
from Controller import GameController, AccountController, SettingsController
from .home_page import HomePage
from .installations_page import InstallationsPage
from .settings_page import SettingsPage
from .login_dialog import LoginDialog
from Utils.locale_manager import LocaleManager
from .theme_manager import ThemeManager


class MainWindow(QMainWindow):
    """
    应用程序主窗口

    包含侧边栏导航和内容区域
    """

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 设置窗口属性
        self.setWindowTitle("Orion Launcher")
        self.setMinimumSize(1000, 600)

        # 设置背景图片
        self._set_background()

        # 初始化控制器
        self.game_controller = GameController(self)
        self.account_controller = AccountController(self)
        self.settings_controller = SettingsController(self)

        # 初始化UI
        self._init_ui()

        # 初始化控制器
        self._init_controllers()

        # 连接信号槽
        self._connect_signals()

    def _set_background(self):
        """设置背景图片"""
        # 获取背景图片路径
        bg_path = os.path.join(path.get("base_path"), "src", "image", "background.png")
        bg_path = bg_path.replace("\\", "/")  # 转换路径分隔符

        if os.path.exists(bg_path):
            # 创建背景标签
            self.bg_label = QLabel(self)
            self.bg_label.setObjectName("bg_label")

            # 加载背景图片
            self.bg_pixmap = QPixmap(bg_path)
            if not self.bg_pixmap.isNull():
                # 设置初始大小
                self._update_background_size()
                # 设置背景图透明度
                self._set_background_overlay()

                # 将背景标签置于底层
                self.bg_label.lower()
            else:
                print("背景图片加载失败")

                # 使用CSS设置纯色背景作为备选
                self.setStyleSheet("QMainWindow { background-color: #1E1E1E; }")

    def _update_background_size(self):
        """更新背景图片大小"""
        if hasattr(self, "bg_pixmap") and hasattr(self, "bg_label"):
            # 获取窗口大小
            window_size = self.size()

            # 计算缩放比例，确保图片覆盖整个窗口
            pixmap_ratio = self.bg_pixmap.width() / self.bg_pixmap.height()
            window_ratio = window_size.width() / window_size.height()

            # 根据比例决定如何缩放
            if window_ratio > pixmap_ratio:
                # 窗口更宽，按宽度缩放
                scaled_pixmap = self.bg_pixmap.scaledToWidth(
                    window_size.width(), Qt.TransformationMode.SmoothTransformation
                )
            else:
                # 窗口更高，按高度缩放
                scaled_pixmap = self.bg_pixmap.scaledToHeight(
                    window_size.height(), Qt.TransformationMode.SmoothTransformation
                )

            # 设置背景标签大小和图片
            self.bg_label.setPixmap(scaled_pixmap)
            self.bg_label.setFixedSize(window_size)

            # 设置对齐方式为居中
            self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _set_background_overlay(self):
        """设置背景图片透明度"""
        self.bg_mask_label = QLabel(self)
        self.bg_mask_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )  # Allows clicks to pass through
        self.bg_mask_label.setGeometry(
            self.bg_label.geometry()
        )  # Overlay same position
        self.bg_mask_label.show()

    def _init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        # 设置中央部件为透明
        central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建侧边栏
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # 创建内容区域
        self.content_stack = QStackedWidget()
        # 设置内容区域为透明
        self.content_stack.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        main_layout.addWidget(self.content_stack)

        # 设置布局比例
        main_layout.setStretch(0, 1)  # 侧边栏
        main_layout.setStretch(1, 4)  # 内容区域

        # 创建页面
        self._create_pages()

        # 添加UI样式
        self._set_style_sheet()

        # 添加UI文字
        self._set_text()

    def _create_sidebar(self) -> QWidget:
        """
        创建侧边栏

        Returns:
            QWidget: 侧边栏部件
        """
        # 创建侧边栏容器
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")

        # 创建侧边栏布局
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)

        # 创建标题
        self.logo_label = QLabel("Orion Launcher")
        sidebar_layout.addWidget(self.logo_label)

        # 添加间隔
        sidebar_layout.addSpacing(20)

        # 创建导航按钮
        self.home_btn = self._create_nav_button("首页", "home")
        self.installations_btn = self._create_nav_button("安装管理", "installations")
        self.settings_btn = self._create_nav_button("设置", "settings")

        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.installations_btn)
        sidebar_layout.addWidget(self.settings_btn)

        # 添加弹性空间
        sidebar_layout.addStretch(1)

        # 创建用户信息区域
        self.user_info = QLabel("未登录")
        sidebar_layout.addWidget(self.user_info)

        # 创建登录/登出按钮
        self.login_btn = QPushButton("登录")
        sidebar_layout.addWidget(self.login_btn)

        return sidebar

    def _create_nav_button(self, text: str, name: str) -> QPushButton:
        """
        创建导航按钮

        Args:
            text: 按钮文本
            name: 按钮名称

        Returns:
            QPushButton: 导航按钮
        """
        btn = QPushButton(text)
        btn.setObjectName(f"nav_{name}")
        btn.setCheckable(True)
        return btn

    def _create_pages(self):
        """创建页面"""
        # 首页
        if getattr(self, "home_page", None) is None:
            self.home_page = HomePage(self.game_controller, self.account_controller)
        self.content_stack.addWidget(self.home_page)

        # 安装管理页
        if getattr(self, "installations_page", None) is None:
            self.installations_page = InstallationsPage(self.game_controller)
        self.content_stack.addWidget(self.installations_page)

        # 设置页
        if getattr(self, "settings_page", None) is None:
            self.settings_page = SettingsPage(self.settings_controller)
        self.content_stack.addWidget(self.settings_page)

    def _set_style_sheet(self):
        """设置/刷新所有UI组件样式"""
        self.sidebar.setStyleSheet(
            f"""
            #sidebar {{
                background-color: {ThemeManager().get("sidebar-background")};
                border-right: 1px solid {ThemeManager().get("sidebar-border")};
            }}
        """
        )

        self.logo_label.setStyleSheet(
            f"color: {ThemeManager().get('title')}; font-size: 24px; font-weight: bold; background: transparent;"
        )

        self.user_info.setStyleSheet(
            f"color: {ThemeManager().get('label')}; font-size: 14px; background: transparent;"
        )

        self.login_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("selection-background")};
                color: {ThemeManager().get("theme-text")};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("selection-hover")};
            }}
        """
        )

        nav_btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {ThemeManager().get("label")};
                border: none;
                text-align: left;
                padding: 10px;
                font-size: 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("label-hover")};
                color: {ThemeManager().get("text")};
            }}
            QPushButton:checked {{
                background-color: {ThemeManager().get("label-hover")};
                color: {ThemeManager().get("selection-background")};
                font-weight: bold;
            }}
        """
        self.home_btn.setStyleSheet(nav_btn_style)
        self.installations_btn.setStyleSheet(nav_btn_style)
        self.settings_btn.setStyleSheet(nav_btn_style)

        self.bg_mask_label.setStyleSheet(
            f"background-color: rgba(255, 255, 255, {int(255 * ThemeManager().get_background_opacity())})"
        )

    def _set_text(self):
        """设置/刷新所有UI组件的文字"""
        self.home_btn.setText(LocaleManager().get("home"))
        self.installations_btn.setText(LocaleManager().get("installation"))
        self.settings_btn.setText(LocaleManager().get("settings"))
        self.user_info.setText(LocaleManager().get("not_logged_in"))
        self.login_btn.setText(LocaleManager().get("login"))

    def _init_controllers(self):
        """初始化控制器"""
        self.game_controller.initialize()
        self.account_controller.initialize()
        self.settings_controller.initialize()

    def _connect_signals(self):
        """连接信号槽"""
        # 导航按钮信号
        self.home_btn.clicked.connect(lambda: self._switch_page(0))
        self.installations_btn.clicked.connect(lambda: self._switch_page(1))
        self.settings_btn.clicked.connect(lambda: self._switch_page(2))

        # 登录按钮信号
        self.login_btn.clicked.connect(self._handle_login_clicked)

        # 账户控制器信号
        self.account_controller.login_success.connect(self._handle_login_success)
        self.account_controller.logout_completed.connect(self._handle_logout_completed)

        # UI刷新信号
        ThemeManager().updated.connect(self._set_style_sheet)

        # 语言刷新信号
        LocaleManager().updated.connect(self._set_text)

    def resizeEvent(self, event):
        """
        窗口大小改变事件

        Args:
            event: 大小改变事件
        """
        # 更新背景图片大小
        self._update_background_size()

        super().resizeEvent(event)

    @Slot(int)
    def _switch_page(self, index: int):
        """
        切换页面

        Args:
            index: 页面索引
        """
        # 取消所有导航按钮的选中状态
        for btn in [self.home_btn, self.installations_btn, self.settings_btn]:
            btn.setChecked(False)

        # 设置当前页面
        self.content_stack.setCurrentIndex(index)

        # 设置当前按钮的选中状态
        if index == 0:
            self.home_btn.setChecked(True)
        elif index == 1:
            self.installations_btn.setChecked(True)
        elif index == 2:
            self.settings_btn.setChecked(True)

    @Slot()
    def _handle_login_clicked(self):
        """处理登录按钮点击事件"""
        current_account = self.account_controller.get_current_account()

        if current_account:
            # 已登录，执行登出
            self.account_controller.logout()
        else:
            # 未登录，显示登录对话框
            dialog = LoginDialog(self.account_controller, self)
            dialog.exec()

    @Slot(dict)
    def _handle_login_success(self, account_info: Dict[str, Any]):
        """
        处理登录成功事件

        Args:
            account_info: 账户信息
        """
        self.user_info.setText(
            f"{account_info['username']} ({LocaleManager().get("logged_in")})"
        )
        self.login_btn.setText(LocaleManager().get("log_out"))

    @Slot()
    def _handle_logout_completed(self):
        """处理登出完成事件"""
        self.user_info.setText(LocaleManager().get("not_logged_in"))
        self.login_btn.setText(LocaleManager().get("login"))

    def closeEvent(self, event: QCloseEvent):
        """
        关闭事件处理

        Args:
            event: 关闭事件
        """
        # 清理控制器资源
        self.game_controller.cleanup()
        self.account_controller.cleanup()
        self.settings_controller.cleanup()

        # 接受关闭事件
        event.accept()
