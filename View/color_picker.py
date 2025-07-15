from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QColorDialog,
    QLabel,
    QFrame,
    QSizePolicy,
    QSpacerItem,
    QComboBox,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal

from Utils.locale_manager import LocaleManager

from .theme_manager import ThemeManager


class ColorPicker(QWidget):
    """
    自定义颜色选择器组件
    """

    saved = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(LocaleManager().get("color_picker"))
        self.base_theme = None

        # 初始化UI
        self._init_ui()

        # 添加UI样式
        self._set_style_sheet()

        # 设置UI文字语言
        self._set_text()

    def _init_ui(self):
        # 主垂直布局
        main_layout = QVBoxLayout(self)
        # 水平内容布局，包含左侧颜色选择器和右侧颜色槽布局
        content_layout = QHBoxLayout()

        # 左侧颜色选择器
        self.color_dialog = QColorDialog(self)
        self.color_dialog.setOptions(
            QColorDialog.NoButtons | QColorDialog.DontUseNativeDialog
        )
        self.color_dialog.setWindowFlags(Qt.Widget)
        self.color_dialog.currentColorChanged.connect(self._update_current_selection)
        content_layout.addWidget(self.color_dialog, 3)
        self.colors = [
            ThemeManager().get("selection-background"),
            ThemeManager().get("selection-hover"),
            ThemeManager().get("theme-text"),
        ]
        self.color_labels = []
        self.selected_index = 0

        # 右侧颜色槽布局
        self.slot_layout = QVBoxLayout()

        # 主题色
        self.primary_color_label = QLabel(LocaleManager().get("primary_color"))
        self.primary_color_frame = QFrame()
        self.primary_color_frame.setFixedSize(120, 50)
        self.primary_color_frame.setFrameShape(QFrame.StyledPanel)
        self.primary_color_frame.setCursor(Qt.PointingHandCursor)
        self.primary_color_frame.mousePressEvent = lambda _: self._select_slot(0)
        self.color_labels.append(self.primary_color_frame)
        self.slot_layout.addWidget(self.primary_color_label)
        self.slot_layout.addWidget(self.primary_color_frame)

        # 悬浮状态的主题色
        self.secondary_color_label = QLabel(LocaleManager().get("secondary_color"))
        self.secondary_color_frame = QFrame()
        self.secondary_color_frame.setFixedSize(120, 50)
        self.secondary_color_frame.setFrameShape(QFrame.StyledPanel)
        self.secondary_color_frame.setCursor(Qt.PointingHandCursor)
        self.secondary_color_frame.mousePressEvent = lambda _: self._select_slot(1)
        self.color_labels.append(self.secondary_color_frame)
        self.slot_layout.addWidget(self.secondary_color_label)
        self.slot_layout.addWidget(self.secondary_color_frame)

        # 主题色上的文字
        self.text_color_label = QLabel(LocaleManager().get("text_color"))
        self.text_color_frame = QFrame()
        self.text_color_frame.setFixedSize(120, 50)
        self.text_color_frame.setFrameShape(QFrame.StyledPanel)
        self.text_color_frame.setCursor(Qt.PointingHandCursor)
        self.text_color_frame.mousePressEvent = lambda _: self._select_slot(2)
        self.color_labels.append(self.text_color_frame)
        self.slot_layout.addWidget(self.text_color_label)
        self.slot_layout.addWidget(self.text_color_frame)

        # 基础主题切换
        self.base_theme_label = QLabel(LocaleManager().get("base_theme"))
        self.base_theme_label.setAlignment(Qt.AlignLeft)
        self.slot_layout.addWidget(self.base_theme_label)
        self.theme_combo = QComboBox()
        # 置顶当前主题选择
        if ThemeManager().get_base_theme() == "light":
            self.theme_combo.addItem(LocaleManager().get("light"), "light")
            self.theme_combo.addItem(LocaleManager().get("dark"), "dark")
        else:
            self.theme_combo.addItem(LocaleManager().get("dark"), "dark")
            self.theme_combo.addItem(LocaleManager().get("light"), "light")
        self.slot_layout.addWidget(self.theme_combo)

        # 保存按钮
        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.slot_layout.addItem(spacer)
        self.save_button = QPushButton(LocaleManager().get("save"))
        self.save_button.setFixedSize(120, 50)
        self.save_button.clicked.connect(self.saved.emit)
        self.slot_layout.addWidget(self.save_button)

        content_layout.addLayout(self.slot_layout, 1)
        main_layout.addLayout(content_layout)

        # 默认选中第一个颜色框
        self.selected_index = 0

    def _select_slot(self, index):
        """选择当前正在编辑的颜色槽，并高亮显示边框"""
        self.selected_index = index
        self._set_style_sheet()

    def _update_current_selection(self, color: QColor):
        """实时更新当前选中的颜色槽背景以及保存键颜色"""
        if not color.isValid():
            return
        self.colors[self.selected_index] = color.name()
        self._set_style_sheet()

    def _set_style_sheet(self):
        """设置/刷新所有UI组件样式"""
        theme_color, theme_color_alt, theme_text = self.colors
        self.save_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {theme_color};
                color: {theme_text};
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {theme_color_alt};
            }}
        """
        )
        self.primary_color_frame.setStyleSheet(
            f"""
                background-color: {theme_color};
                border: {'2px solid gray' if self.selected_index != 0 else
                         f'4px solid {ThemeManager().get('negative-selection-background')}'};
            """
        )
        self.secondary_color_frame.setStyleSheet(
            f"""
                background-color: {theme_color_alt};
                border: {'2px solid gray' if self.selected_index != 1 else
                         f'4px solid {ThemeManager().get('negative-selection-background')}'};
            """
        )
        self.text_color_frame.setStyleSheet(
            f"""
                background-color: {theme_text};
                border: {'2px solid gray' if self.selected_index != 2 else
                         f'4px solid {ThemeManager().get('negative-selection-background')}'};
            """
        )

    def _set_text(self):
        """设置/刷新所有UI组件的文字"""
        self.setWindowTitle(LocaleManager().get("color_picker"))
        self.primary_color_label.setText(LocaleManager().get("primary_color"))
        self.secondary_color_label.setText(LocaleManager().get("secondary_color"))
        self.text_color_label.setText(LocaleManager().get("text_color"))
        self.base_theme_label.setText(LocaleManager().get("base_theme"))
        for i in range(self.theme_combo.count()):
            self.theme_combo.setItemText(
                i, LocaleManager().get(self.theme_combo.itemData(i))
            )
        self.save_button.setText(LocaleManager().get("save"))
