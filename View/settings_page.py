"""
设置页面模块

提供应用程序设置界面
"""

import sys
from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QTabWidget,
    QFormLayout,
    QGroupBox,
)
from PySide6.QtCore import Slot

from Controller import SettingsController

from Utils.locale_manager import LocaleManager
from .theme_manager import ThemeManager


class SettingsPage(QWidget):
    """
    设置页面

    提供应用程序设置界面
    """

    def __init__(self, settings_controller: SettingsController, parent=None):
        """
        初始化设置页面

        Args:
            settings_controller: 设置控制器
            parent: 父部件
        """
        super().__init__(parent)

        self.settings_controller = settings_controller

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
        self.title_label = QLabel("设置")
        main_layout.addWidget(self.title_label)

        # 创建选项卡
        self.tab_widget = QTabWidget()

        # 创建游戏选项卡
        self.game_tab = self._create_game_tab()
        self.tab_widget.addTab(self.game_tab, "游戏")

        # 创建启动器选项卡
        self.launcher_tab = self._create_launcher_tab()
        self.tab_widget.addTab(self.launcher_tab, "启动器")

        # 创建下载选项卡
        self.download_tab = self._create_download_tab()
        self.tab_widget.addTab(self.download_tab, "下载")

        main_layout.addWidget(self.tab_widget)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 添加弹性空间
        button_layout.addStretch(1)

        # 创建保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._on_save_button_click)
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)

        # 添加UI样式
        self._set_style_sheet()

        # 添加UI文字
        self._set_text()

    def _on_save_button_click(self):
        # 处理主题切换
        ThemeManager().setTheme(self.theme_combo.currentData())
        LocaleManager().set_locale(self.language_combo.currentData())

    def _create_game_tab(self) -> QWidget:
        """
        创建游戏选项卡

        Returns:
            QWidget: 游戏选项卡部件
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 创建游戏路径设置
        self.path_group = QGroupBox("游戏路径")
        self.path_layout = QFormLayout(self.path_group)
        self.path_layout.setSpacing(10)

        # Minecraft 目录
        minecraft_layout = QHBoxLayout()
        self.minecraft_dir_edit = QLineEdit()
        self.minecraft_dir_button = QPushButton("浏览...")
        minecraft_layout.addWidget(self.minecraft_dir_edit)
        minecraft_layout.addWidget(self.minecraft_dir_button)
        self.path_layout.addRow("Minecraft 目录:", minecraft_layout)

        # Java 路径
        java_layout = QHBoxLayout()
        self.java_path_edit = QLineEdit()
        self.java_path_button = QPushButton("浏览...")
        java_layout.addWidget(self.java_path_edit)
        java_layout.addWidget(self.java_path_button)
        self.path_layout.addRow("Java 路径:", java_layout)

        layout.addWidget(self.path_group)

        # 创建游戏设置
        self.game_group = QGroupBox("游戏设置")
        self.game_layout = QFormLayout(self.game_group)
        self.game_layout.setSpacing(10)

        # 最大内存
        self.max_memory_spin = QSpinBox()
        self.max_memory_spin.setMinimum(1024)
        self.max_memory_spin.setMaximum(16384)
        self.max_memory_spin.setSingleStep(512)
        self.max_memory_spin.setValue(2048)
        self.max_memory_spin.setSuffix(" MB")
        self.game_layout.addRow("最大内存:", self.max_memory_spin)

        # JVM 参数
        self.jvm_args_edit = QLineEdit()
        self.game_layout.addRow("JVM 参数:", self.jvm_args_edit)

        # 分辨率
        resolution_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(640)
        self.width_spin.setMaximum(3840)
        self.width_spin.setValue(854)

        resolution_layout.addWidget(self.width_spin)

        resolution_layout.addWidget(QLabel("×"))

        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(480)
        self.height_spin.setMaximum(2160)
        self.height_spin.setValue(480)

        resolution_layout.addWidget(self.height_spin)

        self.fullscreen_check = QCheckBox("全屏")

        resolution_layout.addWidget(self.fullscreen_check)
        resolution_layout.addStretch(1)

        self.game_layout.addRow("分辨率:", resolution_layout)

        layout.addWidget(self.game_group)

        # 添加弹性空间
        layout.addStretch(1)

        return tab

    def _create_launcher_tab(self) -> QWidget:
        """
        创建启动器选项卡

        Returns:
            QWidget: 启动器选项卡部件
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 创建启动器设置
        self.launcher_group = QGroupBox("启动器设置")
        self.launcher_layout = QFormLayout(self.launcher_group)
        self.launcher_layout.setSpacing(10)

        # 语言
        self.language_combo = QComboBox()
        self.language_combo.addItem("简体中文", "zh_CN")
        self.language_combo.addItem("繁體中文", "zh_TW")
        self.language_combo.addItem("English", "en_US")
        self.launcher_layout.addRow("语言:", self.language_combo)

        # 主题
        self.theme_combo = QComboBox()

        # 当前主题色放置于最顶端
        match ThemeManager().get_base_theme():
            case "dark":
                self.theme_combo.addItem("深色", "dark")
                self.theme_combo.addItem("浅色", "light")
            case "light":
                self.theme_combo.addItem("浅色", "light")
                self.theme_combo.addItem("深色", "dark")
            case _:
                self.theme_combo.addItem("深色", "dark")
                self.theme_combo.addItem("浅色", "light")
        self.launcher_layout.addRow("主题:", self.theme_combo)

        # 检查更新
        self.check_updates_check = QCheckBox()
        self.check_updates_check.setChecked(True)
        self.launcher_layout.addRow("检查更新:", self.check_updates_check)

        # 游戏启动时关闭启动器
        self.close_launcher_check = QCheckBox()
        self.close_launcher_check.setChecked(True)
        self.launcher_layout.addRow("游戏启动时关闭启动器:", self.close_launcher_check)

        layout.addWidget(self.launcher_group)

        # 添加弹性空间
        layout.addStretch(1)

        return tab

    def _create_download_tab(self) -> QWidget:
        """
        创建下载选项卡

        Returns:
            QWidget: 下载选项卡部件
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 创建下载设置
        self.download_group = QGroupBox("下载设置")
        self.download_layout = QFormLayout(self.download_group)
        self.download_layout.setSpacing(10)

        # 下载源
        self.download_source_combo = QComboBox()
        self.download_source_combo.addItem("官方", "official")
        self.download_source_combo.addItem("BMCLAPI", "bmclapi")
        self.download_source_combo.addItem("MCBBS", "mcbbs")
        self.download_layout.addRow("下载源:", self.download_source_combo)

        # 并发下载数
        self.concurrent_downloads_spin = QSpinBox()
        self.concurrent_downloads_spin.setMinimum(1)
        self.concurrent_downloads_spin.setMaximum(16)
        self.concurrent_downloads_spin.setValue(3)
        self.download_layout.addRow("并发下载数:", self.concurrent_downloads_spin)

        # 下载资源
        self.download_assets_check = QCheckBox()
        self.download_assets_check.setChecked(True)
        self.download_layout.addRow("下载游戏资源:", self.download_assets_check)

        # 下载库文件
        self.download_libraries_check = QCheckBox()
        self.download_libraries_check.setChecked(True)
        self.download_layout.addRow("下载库文件:", self.download_libraries_check)

        layout.addWidget(self.download_group)

        # 添加弹性空间
        layout.addStretch(1)

        return tab

    def _set_style_sheet(self):
        """设置/刷新所有UI组件样式"""

        self.title_label.setStyleSheet(
            f"color: {ThemeManager().get('title')}; font-size: 24px; font-weight: bold; background: transparent;"
        )

        self.tab_widget.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {ThemeManager().get("border")};
                background-color: {ThemeManager().get("tab-selection-background")};
                border-radius: 4px;
            }}
            QTabBar {{
                background-color: {ThemeManager().get("tab-bar-background")};
            }}
            QTabBar::tab {{
                background-color: {ThemeManager().get("tab-background")};
                color: {ThemeManager().get("label")};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {ThemeManager().get("tab-selection-background")};
                color: {ThemeManager().get("selection-background")};
                border-bottom: 2px solid {ThemeManager().get("focus-border")};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {ThemeManager().get("neutral-selection-background")};
            }}
        """
        )

        self.save_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("selection-background")};
                color: {ThemeManager().get("theme-text")};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("selection-hover")};
            }}
        """
        )

        self.game_tab.setStyleSheet(
            f"background-color: {ThemeManager().get('home-window-background')}; color: {ThemeManager().get('text')}"
        )

        self.path_group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {ThemeManager().get('home-window-background')};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {ThemeManager().get("title")};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        )

        self.minecraft_dir_edit.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.minecraft_dir_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("neutral-selection-background")};
                color: {ThemeManager().get("text")};
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("neutral-selection-hover")};
            }}
        """
        )

        self.java_path_edit.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.java_path_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeManager().get("neutral-selection-background")};
                color: {ThemeManager().get("text")};
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager().get("neutral-selection-hover")};
            }}
        """
        )

        self.game_group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {ThemeManager().get('home-window-background')};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {ThemeManager().get("title")};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        )

        self.max_memory_spin.setStyleSheet(
            f"""
            QSpinBox {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.jvm_args_edit.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.width_spin.setStyleSheet(
            f"""
            QSpinBox {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.height_spin.setStyleSheet(
            f"""
            QSpinBox {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.fullscreen_check.setStyleSheet(
            f"""
            QCheckBox {{
                color: {ThemeManager().get("text")};
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 2px;
                background-color: {ThemeManager().get("indicator-background")};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ThemeManager().get("focus-border")};
            }}
        """
        )

        self.launcher_tab.setStyleSheet(
            f"background-color: {ThemeManager().get('home-window-background')}; color: {ThemeManager().get('text')}"
        )

        self.launcher_group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {ThemeManager().get('home-window-background')};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {ThemeManager().get("title")};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        )

        self.language_combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.theme_combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.check_updates_check.setStyleSheet(
            f"""
            QCheckBox {{
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 2px;
                background-color: {ThemeManager().get("indicator-background")};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ThemeManager().get("focus-border")};
            }}
        """
        )

        self.close_launcher_check.setStyleSheet(
            f"""
            QCheckBox {{
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 2px;
                background-color: {ThemeManager().get("indicator-background")};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ThemeManager().get("focus-border")};
            }}
        """
        )

        self.download_tab.setStyleSheet(
            f"background-color: {ThemeManager().get('home-window-background')}; color: {ThemeManager().get('text')}"
        )

        self.download_group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {ThemeManager().get('home-window-background')};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                color: {ThemeManager().get("title")};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        )

        self.download_source_combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.concurrent_downloads_spin.setStyleSheet(
            f"""
            QSpinBox {{
                background-color: {ThemeManager().get("indicator-background")};
                color: {ThemeManager().get("text")};
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 4px;
                padding: 8px;
            }}
        """
        )

        self.download_assets_check.setStyleSheet(
            f"""
            QCheckBox {{
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 2px;
                background-color: {ThemeManager().get("indicator-background")};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ThemeManager().get("focus-border")};
            }}
        """
        )

        self.download_libraries_check.setStyleSheet(
            f"""
            QCheckBox {{
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {ThemeManager().get("border")};
                border-radius: 2px;
                background-color: {ThemeManager().get("indicator-background")};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ThemeManager().get("focus-border")};
            }}
        """
        )

    def _set_text(self):
        """设置/刷新所有UI组件的文字"""
        self.title_label.setText(LocaleManager().get("settings"))
        self.tab_widget.setTabText(0, LocaleManager().get("game"))
        self.tab_widget.setTabText(1, LocaleManager().get("launcher"))
        self.tab_widget.setTabText(2, LocaleManager().get("download"))
        self.save_button.setText(LocaleManager().get("save"))

        # game_tab
        self.path_group.setTitle(LocaleManager().get("game_path"))
        self.minecraft_dir_button.setText(LocaleManager().get("browse"))
        self.path_layout.itemAt(0).widget().setText(
            f"Minecraft {LocaleManager().get("folder")}:"
        )
        self.java_path_button.setText(LocaleManager().get("browse"))
        self.path_layout.itemAt(2).widget().setText(
            f"Java {LocaleManager().get("path")}:"
        )
        self.game_group.setTitle(LocaleManager().get("game_settings"))
        self.game_layout.itemAt(0).widget().setText(LocaleManager().get("max_memory"))
        self.game_layout.itemAt(2).widget().setText(
            f"JVM {LocaleManager().get("parameter")}:"
        )
        self.fullscreen_check.setText(LocaleManager().get("fullscreen"))
        self.game_layout.itemAt(4).widget().setText(LocaleManager().get("resolution"))
        self.launcher_group.setTitle(LocaleManager().get("launcher_settings"))

        # launcher_tab
        self.launcher_layout.itemAt(0).widget().setText(LocaleManager().get("language"))
        for i in range(self.theme_combo.count()):
            self.theme_combo.setItemText(
                i, LocaleManager().get(self.theme_combo.itemData(i))
            )
        self.launcher_layout.itemAt(2).widget().setText(LocaleManager().get("theme"))
        self.launcher_layout.itemAt(4).widget().setText(
            LocaleManager().get("check_for_updates")
        )
        self.launcher_layout.itemAt(6).widget().setText(
            LocaleManager().get("close_launcher_when_game_starts")
        )

        # download_tab
        self.download_group.setTitle(LocaleManager().get("download_settings"))
        self.download_layout.itemAt(0).widget().setText(
            LocaleManager().get("download_source")
        )
        for i in range(self.download_source_combo.count()):
            self.download_source_combo.setItemText(
                i, LocaleManager().get(self.download_source_combo.itemData(i))
            )
        self.download_layout.itemAt(2).widget().setText(
            LocaleManager().get("parallel_download_count")
        )
        self.download_layout.itemAt(4).widget().setText(
            LocaleManager().get("download_game_resources")
        )
        self.download_layout.itemAt(6).widget().setText(
            LocaleManager().get("download_library_files")
        )

    def _connect_signals(self):
        """连接信号槽"""
        # 设置控制器信号
        self.settings_controller.settings_loaded.connect(self._handle_settings_loaded)
        self.settings_controller.settings_saved.connect(self._handle_settings_saved)

        # 按钮信号
        self.save_button.clicked.connect(self._handle_save_clicked)
        self.minecraft_dir_button.clicked.connect(self._handle_minecraft_dir_clicked)
        self.java_path_button.clicked.connect(self._handle_java_path_clicked)

        # 加载设置
        self.settings_controller.load_settings()

        # UI刷新信号
        ThemeManager().updated.connect(self._set_style_sheet)

        # 语言刷新信号
        LocaleManager().updated.connect(self._set_text)

    @Slot(dict)
    def _handle_settings_loaded(self, settings: Dict[str, Any]):
        """
        处理设置加载事件

        Args:
            settings: 设置数据
        """
        # 游戏设置
        game_settings = settings.get("game", {})
        self.minecraft_dir_edit.setText(game_settings.get("minecraft_directory", ""))
        self.java_path_edit.setText(game_settings.get("java_path", ""))
        self.max_memory_spin.setValue(game_settings.get("max_memory", 2048))
        self.jvm_args_edit.setText(game_settings.get("jvm_args", ""))
        self.width_spin.setValue(game_settings.get("resolution_width", 854))
        self.height_spin.setValue(game_settings.get("resolution_height", 480))
        self.fullscreen_check.setChecked(game_settings.get("fullscreen", False))

        # 启动器设置
        launcher_settings = settings.get("launcher", {})
        language = launcher_settings.get("language", "zh_CN")
        index = self.language_combo.findData(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        theme = launcher_settings.get("theme", "dark")
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.check_updates_check.setChecked(
            launcher_settings.get("check_updates", True)
        )
        self.close_launcher_check.setChecked(
            launcher_settings.get("close_launcher_when_game_starts", True)
        )

        # 下载设置
        download_settings = settings.get("download", {})
        download_source = download_settings.get("download_source", "official")
        index = self.download_source_combo.findData(download_source)
        if index >= 0:
            self.download_source_combo.setCurrentIndex(index)

        self.concurrent_downloads_spin.setValue(
            download_settings.get("concurrent_downloads", 3)
        )
        self.download_assets_check.setChecked(
            download_settings.get("download_assets", True)
        )
        self.download_libraries_check.setChecked(
            download_settings.get("download_libraries", True)
        )

    @Slot()
    def _handle_save_clicked(self):
        """处理保存按钮点击事件"""
        # 游戏设置
        self.settings_controller.set_setting(
            "game", "minecraft_directory", self.minecraft_dir_edit.text()
        )
        self.settings_controller.set_setting(
            "game", "java_path", self.java_path_edit.text()
        )
        self.settings_controller.set_setting(
            "game", "max_memory", self.max_memory_spin.value()
        )
        self.settings_controller.set_setting(
            "game", "jvm_args", self.jvm_args_edit.text()
        )
        self.settings_controller.set_setting(
            "game", "resolution_width", self.width_spin.value()
        )
        self.settings_controller.set_setting(
            "game", "resolution_height", self.height_spin.value()
        )
        self.settings_controller.set_setting(
            "game", "fullscreen", self.fullscreen_check.isChecked()
        )

        # 启动器设置
        self.settings_controller.set_setting(
            "launcher", "language", self.language_combo.currentData()
        )
        self.settings_controller.set_setting(
            "launcher", "theme", self.theme_combo.currentData()
        )
        self.settings_controller.set_setting(
            "launcher", "check_updates", self.check_updates_check.isChecked()
        )
        self.settings_controller.set_setting(
            "launcher",
            "close_launcher_when_game_starts",
            self.close_launcher_check.isChecked(),
        )

        # 下载设置
        self.settings_controller.set_setting(
            "download", "download_source", self.download_source_combo.currentData()
        )
        self.settings_controller.set_setting(
            "download", "concurrent_downloads", self.concurrent_downloads_spin.value()
        )
        self.settings_controller.set_setting(
            "download", "download_assets", self.download_assets_check.isChecked()
        )
        self.settings_controller.set_setting(
            "download", "download_libraries", self.download_libraries_check.isChecked()
        )

        # 保存设置
        self.settings_controller.save_settings()

    @Slot()
    def _handle_settings_saved(self):
        """处理设置保存完成事件"""
        # TODO: 显示保存成功提示
        pass

    @Slot()
    def _handle_minecraft_dir_clicked(self):
        """处理Minecraft目录按钮点击事件"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择Minecraft目录", self.minecraft_dir_edit.text()
        )
        if directory:
            self.minecraft_dir_edit.setText(directory)

    @Slot()
    def _handle_java_path_clicked(self):
        """处理Java路径按钮点击事件"""
        file_filter = (
            "Java可执行文件 (java.exe)"
            if "win" in sys.platform
            else "Java可执行文件 (java)"
        )
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Java可执行文件", self.java_path_edit.text(), file_filter
        )
        if file_path:
            self.java_path_edit.setText(file_path)
