"""
设置页面模块

提供应用程序设置界面
"""

import sys
from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QSpacerItem, QSizePolicy, 
    QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QFileDialog, QTabWidget, QFormLayout, QGroupBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont

from Controller import SettingsController


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
        title_label = QLabel("设置")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #333333;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #444444;
                color: #BBBBBB;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #333333;
                color: #4CAF50;
                border-bottom: 2px solid #4CAF50;
            }
            QTabBar::tab:hover:!selected {
                background-color: #555555;
            }
        """)
        
        # 创建游戏选项卡
        game_tab = self._create_game_tab()
        self.tab_widget.addTab(game_tab, "游戏")
        
        # 创建启动器选项卡
        launcher_tab = self._create_launcher_tab()
        self.tab_widget.addTab(launcher_tab, "启动器")
        
        # 创建下载选项卡
        download_tab = self._create_download_tab()
        self.tab_widget.addTab(download_tab, "下载")
        
        main_layout.addWidget(self.tab_widget)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 添加弹性空间
        button_layout.addStretch(1)
        
        # 创建保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
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
        path_group = QGroupBox("游戏路径")
        path_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #4CAF50;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        path_layout = QFormLayout(path_group)
        path_layout.setSpacing(10)
        
        # Minecraft 目录
        minecraft_layout = QHBoxLayout()
        self.minecraft_dir_edit = QLineEdit()
        self.minecraft_dir_edit.setStyleSheet("""
            QLineEdit {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.minecraft_dir_button = QPushButton("浏览...")
        self.minecraft_dir_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        minecraft_layout.addWidget(self.minecraft_dir_edit)
        minecraft_layout.addWidget(self.minecraft_dir_button)
        path_layout.addRow("Minecraft 目录:", minecraft_layout)
        
        # Java 路径
        java_layout = QHBoxLayout()
        self.java_path_edit = QLineEdit()
        self.java_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.java_path_button = QPushButton("浏览...")
        self.java_path_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        java_layout.addWidget(self.java_path_edit)
        java_layout.addWidget(self.java_path_button)
        path_layout.addRow("Java 路径:", java_layout)
        
        layout.addWidget(path_group)
        
        # 创建游戏设置
        game_group = QGroupBox("游戏设置")
        game_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #4CAF50;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        game_layout = QFormLayout(game_group)
        game_layout.setSpacing(10)
        
        # 最大内存
        self.max_memory_spin = QSpinBox()
        self.max_memory_spin.setStyleSheet("""
            QSpinBox {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.max_memory_spin.setMinimum(1024)
        self.max_memory_spin.setMaximum(16384)
        self.max_memory_spin.setSingleStep(512)
        self.max_memory_spin.setValue(2048)
        self.max_memory_spin.setSuffix(" MB")
        game_layout.addRow("最大内存:", self.max_memory_spin)
        
        # JVM 参数
        self.jvm_args_edit = QLineEdit()
        self.jvm_args_edit.setStyleSheet("""
            QLineEdit {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        game_layout.addRow("JVM 参数:", self.jvm_args_edit)
        
        # 分辨率
        resolution_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setStyleSheet("""
            QSpinBox {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.width_spin.setMinimum(640)
        self.width_spin.setMaximum(3840)
        self.width_spin.setValue(854)
        
        resolution_layout.addWidget(self.width_spin)
        
        resolution_layout.addWidget(QLabel("×"))
        
        self.height_spin = QSpinBox()
        self.height_spin.setStyleSheet("""
            QSpinBox {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.height_spin.setMinimum(480)
        self.height_spin.setMaximum(2160)
        self.height_spin.setValue(480)
        
        resolution_layout.addWidget(self.height_spin)
        
        self.fullscreen_check = QCheckBox("全屏")
        self.fullscreen_check.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555555;
                border-radius: 2px;
                background-color: #444444;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
        """)
        
        resolution_layout.addWidget(self.fullscreen_check)
        resolution_layout.addStretch(1)
        
        game_layout.addRow("分辨率:", resolution_layout)
        
        layout.addWidget(game_group)
        
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
        launcher_group = QGroupBox("启动器设置")
        launcher_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #4CAF50;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        launcher_layout = QFormLayout(launcher_group)
        launcher_layout.setSpacing(10)
        
        # 语言
        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.language_combo.addItem("简体中文", "zh_CN")
        self.language_combo.addItem("English", "en_US")
        launcher_layout.addRow("语言:", self.language_combo)
        
        # 主题
        self.theme_combo = QComboBox()
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.theme_combo.addItem("深色", "dark")
        self.theme_combo.addItem("浅色", "light")
        launcher_layout.addRow("主题:", self.theme_combo)
        
        # 检查更新
        self.check_updates_check = QCheckBox()
        self.check_updates_check.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555555;
                border-radius: 2px;
                background-color: #444444;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
        """)
        self.check_updates_check.setChecked(True)
        launcher_layout.addRow("检查更新:", self.check_updates_check)
        
        # 游戏启动时关闭启动器
        self.close_launcher_check = QCheckBox()
        self.close_launcher_check.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555555;
                border-radius: 2px;
                background-color: #444444;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
        """)
        self.close_launcher_check.setChecked(True)
        launcher_layout.addRow("游戏启动时关闭启动器:", self.close_launcher_check)
        
        layout.addWidget(launcher_group)
        
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
        download_group = QGroupBox("下载设置")
        download_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #4CAF50;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        download_layout = QFormLayout(download_group)
        download_layout.setSpacing(10)
        
        # 下载源
        self.download_source_combo = QComboBox()
        self.download_source_combo.setStyleSheet("""
            QComboBox {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.download_source_combo.addItem("官方", "official")
        self.download_source_combo.addItem("BMCLAPI", "bmclapi")
        self.download_source_combo.addItem("MCBBS", "mcbbs")
        download_layout.addRow("下载源:", self.download_source_combo)
        
        # 并发下载数
        self.concurrent_downloads_spin = QSpinBox()
        self.concurrent_downloads_spin.setStyleSheet("""
            QSpinBox {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.concurrent_downloads_spin.setMinimum(1)
        self.concurrent_downloads_spin.setMaximum(16)
        self.concurrent_downloads_spin.setValue(3)
        download_layout.addRow("并发下载数:", self.concurrent_downloads_spin)
        
        # 下载资源
        self.download_assets_check = QCheckBox()
        self.download_assets_check.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555555;
                border-radius: 2px;
                background-color: #444444;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
        """)
        self.download_assets_check.setChecked(True)
        download_layout.addRow("下载游戏资源:", self.download_assets_check)
        
        # 下载库文件
        self.download_libraries_check = QCheckBox()
        self.download_libraries_check.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555555;
                border-radius: 2px;
                background-color: #444444;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
        """)
        self.download_libraries_check.setChecked(True)
        download_layout.addRow("下载库文件:", self.download_libraries_check)
        
        layout.addWidget(download_group)
        
        # 添加弹性空间
        layout.addStretch(1)
        
        return tab
    
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
        
        self.check_updates_check.setChecked(launcher_settings.get("check_updates", True))
        self.close_launcher_check.setChecked(launcher_settings.get("close_launcher_when_game_starts", True))
        
        # 下载设置
        download_settings = settings.get("download", {})
        download_source = download_settings.get("download_source", "official")
        index = self.download_source_combo.findData(download_source)
        if index >= 0:
            self.download_source_combo.setCurrentIndex(index)
        
        self.concurrent_downloads_spin.setValue(download_settings.get("concurrent_downloads", 3))
        self.download_assets_check.setChecked(download_settings.get("download_assets", True))
        self.download_libraries_check.setChecked(download_settings.get("download_libraries", True))
    
    @Slot()
    def _handle_save_clicked(self):
        """处理保存按钮点击事件"""
        # 游戏设置
        self.settings_controller.set_setting("game", "minecraft_directory", self.minecraft_dir_edit.text())
        self.settings_controller.set_setting("game", "java_path", self.java_path_edit.text())
        self.settings_controller.set_setting("game", "max_memory", self.max_memory_spin.value())
        self.settings_controller.set_setting("game", "jvm_args", self.jvm_args_edit.text())
        self.settings_controller.set_setting("game", "resolution_width", self.width_spin.value())
        self.settings_controller.set_setting("game", "resolution_height", self.height_spin.value())
        self.settings_controller.set_setting("game", "fullscreen", self.fullscreen_check.isChecked())
        
        # 启动器设置
        self.settings_controller.set_setting("launcher", "language", self.language_combo.currentData())
        self.settings_controller.set_setting("launcher", "theme", self.theme_combo.currentData())
        self.settings_controller.set_setting("launcher", "check_updates", self.check_updates_check.isChecked())
        self.settings_controller.set_setting("launcher", "close_launcher_when_game_starts", self.close_launcher_check.isChecked())
        
        # 下载设置
        self.settings_controller.set_setting("download", "download_source", self.download_source_combo.currentData())
        self.settings_controller.set_setting("download", "concurrent_downloads", self.concurrent_downloads_spin.value())
        self.settings_controller.set_setting("download", "download_assets", self.download_assets_check.isChecked())
        self.settings_controller.set_setting("download", "download_libraries", self.download_libraries_check.isChecked())
        
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
        directory = QFileDialog.getExistingDirectory(self, "选择Minecraft目录", self.minecraft_dir_edit.text())
        if directory:
            self.minecraft_dir_edit.setText(directory)
    
    @Slot()
    def _handle_java_path_clicked(self):
        """处理Java路径按钮点击事件"""
        file_filter = "Java可执行文件 (java.exe)" if "win" in sys.platform else "Java可执行文件 (java)"
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Java可执行文件", self.java_path_edit.text(), file_filter)
        if file_path:
            self.java_path_edit.setText(file_path) 