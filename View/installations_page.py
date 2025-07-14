"""
安装管理页面模块

提供游戏版本安装和管理功能
"""

from typing import Any, Dict, List

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from Controller import GameController

from Utils.locale_manager import LocaleManager
from .theme_manager import ThemeManager


class InstallationsPage(QWidget):
    """
    安装管理页面

    提供游戏版本安装和管理功能
    """

    def __init__(self, game_controller: GameController, parent=None):
        """
        初始化安装管理页面

        Args:
            game_controller: 游戏控制器
            parent: 父部件
        """
        super().__init__(parent)

        self.game_controller = game_controller

        # 设置透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 初始化UI
        self._init_ui()

        # 设置UI文字语言
        self._set_text()

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

        # 创建标题
        self.title_label = QLabel("安装管理")
        main_layout.addWidget(self.title_label)

        # 创建已安装版本列表
        self.installed_frame = QFrame()
        installed_layout = QVBoxLayout(self.installed_frame)
        installed_layout.setContentsMargins(20, 20, 20, 20)

        # 创建已安装版本标题
        self.installed_title = QLabel("已安装版本")

        installed_layout.addWidget(self.installed_title)

        # 创建已安装版本列表
        self.installed_list = QListWidget()
        installed_layout.addWidget(self.installed_list)

        # 创建按钮布局
        installed_buttons_layout = QHBoxLayout()

        # 创建删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.setEnabled(False)

        # 创建启动按钮
        self.launch_button = QPushButton("启动")
        self.launch_button.setEnabled(False)

        installed_buttons_layout.addWidget(self.delete_button)
        installed_buttons_layout.addStretch(1)
        installed_buttons_layout.addWidget(self.launch_button)

        installed_layout.addLayout(installed_buttons_layout)

        main_layout.addWidget(self.installed_frame)

        # 创建安装新版本区域
        self.install_frame = QFrame()
        install_layout = QVBoxLayout(self.install_frame)
        install_layout.setContentsMargins(20, 20, 20, 20)

        # 创建安装新版本标题
        self.install_title = QLabel("安装新版本")
        install_layout.addWidget(self.install_title)

        # 创建版本选择区域
        version_layout = QHBoxLayout()
        self.version_label = QLabel("选择版本:")
        self.version_combo = QComboBox()

        version_layout.addWidget(self.version_label)
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch(1)

        # 创建安装按钮
        self.install_button = QPushButton("安装")
        version_layout.addWidget(self.install_button)

        install_layout.addLayout(version_layout)

        # 创建进度条（默认隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        install_layout.addWidget(self.progress_bar)

        main_layout.addWidget(self.install_frame)

        # 添加UI样式
        self._set_style_sheet()

    def _set_style_sheet(self):
        """设置/刷新所有UI组件样式"""
        self.title_label.setStyleSheet(
            f"color: {ThemeManager().get("title")}; font-size: 24px; font-weight: bold; background: transparent;"
        )

        self.installed_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {ThemeManager().get("qframe-background")};
                border-radius: 8px;
            }}
        """
        )

        self.installed_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: {ThemeManager().get("text-box-background")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 5px;
            }}
            QListWidget::item {{
                color: {ThemeManager().get("text")};
                padding: 8px;
                margin: 2px 0px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {ThemeManager().get("disabled-selection")};
            }}
            QListWidget::item:selected {{
                background-color: {ThemeManager().get("selection-background")};
                color: {ThemeManager().get("theme-text")};
            }}
        """
        )

        self.delete_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("negative-selection-background")};
                color: {ThemeManager().get("theme-text")};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("negative-selection-hover")};
            }}
            QPushButton:disabled {{
                background-color: {ThemeManager().get("disabled-selection")};
                color: {ThemeManager().get("disabled-selection-text")};
            }}
        """
        )

        self.launch_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("selection-background")};
                color: {ThemeManager().get("theme_text")};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("selection-hover")};
            }}
            QPushButton:disabled {{
                background-color: {ThemeManager().get("disabled-selection")};;
                color: {ThemeManager().get("disabled-selection-text")};
            }}
        """
        )

        self.install_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {ThemeManager().get("qframe-background")};
                border-radius: 8px;
            }}
        """
        )

        self.install_title.setStyleSheet(
            f"color: {ThemeManager().get("title")}; font-size: 18px; font-weight: bold; background: transparent;"
        )

        self.installed_title.setStyleSheet(
            f"color: {ThemeManager().get("title")}; font-size: 18px; font-weight: bold; background: transparent;"
        )

        self.version_label.setStyleSheet(
            f"color: {ThemeManager().get("label")}; font-size: 14px; background: transparent;"
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

        self.install_button.setStyleSheet(
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
            QPushButton:disabled {{
                background-color: {ThemeManager().get("disabled-selection")};;
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
                background-color: {ThemeManager().get("selection-background")};
                border-radius: 4px;
            }}
        """
        )

    def _set_text(self):
        """设置/刷新所有UI组件的文字"""
        self.title_label.setText(LocaleManager().get("installation"))
        self.installed_title.setText(LocaleManager().get("installed_version"))
        self.delete_button.setText(LocaleManager().get("delete"))
        self.launch_button.setText(LocaleManager().get("launch"))
        self.install_title.setText(LocaleManager().get("install_new_version"))
        self.version_label.setText(LocaleManager().get("select_version"))
        self.install_button.setText(LocaleManager().get("install"))

    def _connect_signals(self):
        """连接信号槽"""
        # 游戏控制器信号
        self.game_controller.version_list_updated.connect(
            self._handle_version_list_updated
        )
        self.game_controller.task_progress.connect(self._handle_task_progress)
        self.game_controller.task_completed.connect(self._handle_task_completed)

        # 按钮信号
        self.install_button.clicked.connect(self._handle_install_clicked)
        self.delete_button.clicked.connect(self._handle_delete_clicked)
        self.launch_button.clicked.connect(self._handle_launch_clicked)

        # 列表信号
        self.installed_list.itemSelectionChanged.connect(self._handle_selection_changed)

        # UI刷新信号
        ThemeManager().updated.connect(self._set_style_sheet)

        # 语言刷新信号
        LocaleManager().updated.connect(self._set_text)

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

        # 模拟已安装版本列表
        self.installed_list.clear()
        self.installed_list.addItem("1.20.4")

    @Slot()
    def _handle_selection_changed(self):
        """处理版本选择变化事件"""
        # 启用/禁用按钮
        has_selection = len(self.installed_list.selectedItems()) > 0
        self.delete_button.setEnabled(has_selection)
        self.launch_button.setEnabled(has_selection)

    @Slot()
    def _handle_install_clicked(self):
        """处理安装按钮点击事件"""
        version_id = self.version_combo.currentText()
        if not version_id:
            return

        # 禁用安装按钮
        self.install_button.setEnabled(False)
        self.install_button.setText(LocaleManager().get("installing"))
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 安装游戏
        self.game_controller.install_game(version_id)

    @Slot()
    def _handle_delete_clicked(self):
        """处理删除按钮点击事件"""
        selected_items = self.installed_list.selectedItems()
        if not selected_items:
            return

        # TODO: 实现删除功能
        version_id = selected_items[0].text()
        # 模拟删除
        self.installed_list.takeItem(self.installed_list.row(selected_items[0]))

    @Slot()
    def _handle_launch_clicked(self):
        """处理启动按钮点击事件"""
        selected_items = self.installed_list.selectedItems()
        if not selected_items:
            return

        version_id = selected_items[0].text()
        # TODO: 启动游戏
        self.game_controller.launch_game(version_id, "Player123")

    @Slot(str, int)
    def _handle_task_progress(self, task_name: str, progress: int):
        """
        处理任务进度事件

        Args:
            task_name: 任务名称
            progress: 进度百分比
        """
        if task_name == "install_game":
            self.progress_bar.setValue(progress)

    @Slot(str)
    def _handle_task_completed(self, task_name: str):
        """
        处理任务完成事件

        Args:
            task_name: 任务名称
        """
        if task_name == "install_game":
            # 恢复安装按钮
            self.install_button.setEnabled(True)
            self.install_button.setText(LocaleManager().get("install"))
            self.progress_bar.setVisible(False)

            # 添加到已安装列表
            version_id = self.version_combo.currentText()
            if version_id:
                self.installed_list.addItem(version_id)
