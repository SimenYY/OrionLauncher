"""
首页模块

显示游戏启动界面，包括版本选择、启动按钮等
"""

from typing import Any, Dict, List

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from Controller import AccountController, GameController

from .theme_manager import ThemeManager


class HomePage(QWidget):
    """
    首页

    显示游戏启动界面，包括版本选择、启动按钮等
    """

    def __init__(
        self,
        game_controller: GameController,
        account_controller: AccountController,
        parent=None,
    ):
        """
        初始化首页

        Args:
            game_controller: 游戏控制器
            account_controller: 账户控制器
            parent: 父部件
        """
        super().__init__(parent)

        self.game_controller = game_controller
        self.account_controller = account_controller

        # 设置透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 初始化UI
        self._init_ui()

        # 连接信号槽
        self._connect_signals()

        # 刷新版本列表
        self.game_controller.refresh_version_list()

    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 创建顶部区域
        self.top_frame = QFrame()
        top_layout = QVBoxLayout(self.top_frame)
        top_layout.setContentsMargins(20, 20, 20, 20)

        # 创建标题
        self.title_label = QLabel("Orion's Tip of the Day")
        top_layout.addWidget(self.title_label)

        # 创建提示内容
        self.tip_label = QLabel("Getting a fresh tip for you...")
        self.tip_label.setWordWrap(True)
        top_layout.addWidget(self.tip_label)

        # 添加顶部区域到主布局
        main_layout.addWidget(self.top_frame)

        # 添加弹性空间
        main_layout.addStretch(1)

        # 创建底部控制区域
        self.bottom_frame = QFrame()
        bottom_layout = QVBoxLayout(self.bottom_frame)
        bottom_layout.setContentsMargins(20, 20, 20, 20)
        bottom_layout.setSpacing(15)

        # 创建版本选择区域
        version_layout = QHBoxLayout()
        self.version_label = QLabel("游戏版本:")
        self.version_combo = QComboBox()

        version_layout.addWidget(self.version_label)
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch(1)

        # 创建版本信息标签
        self.version_info = QLabel("Latest Release - 1.21")
        version_layout.addWidget(self.version_info)

        bottom_layout.addLayout(version_layout)

        # 创建启动按钮
        self.play_button = QPushButton("PLAY")
        self.play_button.setMinimumHeight(50)
        bottom_layout.addWidget(self.play_button)

        # 创建进度条（默认隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(50)
        self.progress_bar.setVisible(False)
        bottom_layout.addWidget(self.progress_bar)

        main_layout.addWidget(self.bottom_frame)

        # 添加UI样式
        self._set_style_sheet()

    def _set_style_sheet(self):
        """设置/刷新所有UI组件样式"""
        self.top_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {ThemeManager().get("home-window-background")};
                border-radius: 8px;
            }}
        """
        )

        self.title_label.setStyleSheet(
            f"color: {ThemeManager().get('title')}; font-size: 18px; font-weight: bold; background: transparent;"
        )

        self.bottom_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {ThemeManager().get("home-window-background")};
                border-radius: 8px;
            }}
        """
        )

        self.version_label.setStyleSheet(
            f"color: {ThemeManager().get('label')}; font-size: 14px; background: transparent;"
        )

        self.version_combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {ThemeManager().get("text-box-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
                min-width: 200px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {ThemeManager().get("text-box-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                selection-background-color: {ThemeManager().get("selection-background")};
            }}
        """
        )

        self.version_info.setStyleSheet(
            f"color: {ThemeManager().get('label')}; font-size: 14px; background: transparent;"
        )

        self.play_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("selection-background")};
                color: {ThemeManager().get("theme_text")};
                border-radius: 4px;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
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

        self.tip_label.setStyleSheet(
            f"color: {ThemeManager().get('label')}; font-size: 14px; background: transparent;"
        )

    def _connect_signals(self):
        """连接信号槽"""
        # 游戏控制器信号
        self.game_controller.version_list_updated.connect(
            self._handle_version_list_updated
        )
        self.game_controller.game_launch_started.connect(
            self._handle_game_launch_started
        )
        self.game_controller.game_launched.connect(self._handle_game_launched)
        self.game_controller.task_progress.connect(self._handle_task_progress)

        # 按钮信号
        self.play_button.clicked.connect(self._handle_play_clicked)

        # 版本选择信号
        self.version_combo.currentIndexChanged.connect(self._handle_version_changed)

        # UI刷新信号
        ThemeManager().updated.connect(self._set_style_sheet)

    @Slot(list)
    def _handle_version_list_updated(self, versions: List[Dict[str, Any]]):
        """
        处理版本列表更新事件

        Args:
            versions: 版本列表
        """
        self.version_combo.clear()

        for version in versions:
            self.version_combo.addItem(version["id"], version)

    @Slot(int)
    def _handle_version_changed(self, index: int):
        """
        处理版本选择变化事件

        Args:
            index: 选中的索引
        """
        if index >= 0:
            version_data = self.version_combo.itemData(index)
            self.version_info.setText(
                f"{version_data['type'].capitalize()} - {version_data['id']}"
            )

    @Slot()
    def _handle_play_clicked(self):
        """处理启动按钮点击事件"""
        # 获取当前账户
        account = self.account_controller.get_current_account()

        if not account:
            # TODO: 显示登录对话框
            self.account_controller.login("Player123", "password")
            return

        # 获取选中的版本
        version_id = self.version_combo.currentText()
        if not version_id:
            return

        # 启动游戏
        self.game_controller.launch_game(version_id, account["username"])

    @Slot()
    def _handle_game_launch_started(self):
        """处理游戏启动开始事件"""
        self.play_button.setEnabled(False)
        self.play_button.setText("正在启动...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

    @Slot()
    def _handle_game_launched(self):
        """处理游戏启动完成事件"""
        self.play_button.setEnabled(True)
        self.play_button.setText("PLAY")
        self.progress_bar.setVisible(False)

    @Slot(str, int)
    def _handle_task_progress(self, task_name: str, progress: int):
        """
        处理任务进度事件

        Args:
            task_name: 任务名称
            progress: 进度百分比
        """
        if task_name == "launch_game":
            self.progress_bar.setValue(progress)
