"""
安装管理页面模块

提供游戏版本安装和管理功能
"""

from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QListWidgetItem, QFrame, 
    QSizePolicy, QSpacerItem, QProgressBar, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont

from Controller import GameController


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
        title_label = QLabel("安装管理")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: transparent;")
        main_layout.addWidget(title_label)
        
        # 创建已安装版本列表
        installed_frame = QFrame()
        installed_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(51, 51, 51, 200);
                border-radius: 8px;
            }
        """)
        installed_layout = QVBoxLayout(installed_frame)
        installed_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建已安装版本标题
        installed_title = QLabel("已安装版本")
        installed_title.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold; background: transparent;")
        installed_layout.addWidget(installed_title)
        
        # 创建已安装版本列表
        self.installed_list = QListWidget()
        self.installed_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(68, 68, 68, 200);
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                color: white;
                padding: 8px;
                margin: 2px 0px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: rgba(85, 85, 85, 200);
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        installed_layout.addWidget(self.installed_list)
        
        # 创建按钮布局
        installed_buttons_layout = QHBoxLayout()
        
        # 创建删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5555;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF3333;
            }
            QPushButton:disabled {
                background-color: rgba(85, 85, 85, 200);
                color: #888888;
            }
        """)
        self.delete_button.setEnabled(False)
        
        # 创建启动按钮
        self.launch_button = QPushButton("启动")
        self.launch_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: rgba(85, 85, 85, 200);
                color: #888888;
            }
        """)
        self.launch_button.setEnabled(False)
        
        installed_buttons_layout.addWidget(self.delete_button)
        installed_buttons_layout.addStretch(1)
        installed_buttons_layout.addWidget(self.launch_button)
        
        installed_layout.addLayout(installed_buttons_layout)
        
        main_layout.addWidget(installed_frame)
        
        # 创建安装新版本区域
        install_frame = QFrame()
        install_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(51, 51, 51, 200);
                border-radius: 8px;
            }
        """)
        install_layout = QVBoxLayout(install_frame)
        install_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建安装新版本标题
        install_title = QLabel("安装新版本")
        install_title.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold; background: transparent;")
        install_layout.addWidget(install_title)
        
        # 创建版本选择区域
        version_layout = QHBoxLayout()
        version_label = QLabel("选择版本:")
        version_label.setStyleSheet("color: #BBBBBB; font-size: 14px; background: transparent;")
        self.version_combo = QComboBox()
        self.version_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(68, 68, 68, 200);
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(68, 68, 68, 200);
                color: white;
                border: 1px solid #555555;
                selection-background-color: #4CAF50;
            }
        """)
        
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch(1)
        
        # 创建安装按钮
        self.install_button = QPushButton("安装")
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: rgba(85, 85, 85, 200);
                color: #888888;
            }
        """)
        version_layout.addWidget(self.install_button)
        
        install_layout.addLayout(version_layout)
        
        # 创建进度条（默认隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(68, 68, 68, 200);
                color: white;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setVisible(False)
        install_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(install_frame)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 游戏控制器信号
        self.game_controller.version_list_updated.connect(self._handle_version_list_updated)
        self.game_controller.task_progress.connect(self._handle_task_progress)
        self.game_controller.task_completed.connect(self._handle_task_completed)
        
        # 按钮信号
        self.install_button.clicked.connect(self._handle_install_clicked)
        self.delete_button.clicked.connect(self._handle_delete_clicked)
        self.launch_button.clicked.connect(self._handle_launch_clicked)
        
        # 列表信号
        self.installed_list.itemSelectionChanged.connect(self._handle_selection_changed)
    
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
        self.install_button.setText("正在安装...")
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
            self.install_button.setText("安装")
            self.progress_bar.setVisible(False)
            
            # 添加到已安装列表
            version_id = self.version_combo.currentText()
            if version_id:
                self.installed_list.addItem(version_id) 