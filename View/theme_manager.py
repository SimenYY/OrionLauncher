"""
用户登录界面主题

用于统一管理界面组件的颜色配置
"""

from PySide6.QtCore import Signal, QObject


class ColorPalette:
    """
    基础颜色配置
    """

    def __init__(
        self,
        theme_color,
        theme_color_alt,
        theme_text,
        background_opacity=0,
        base_theme="dark",
    ):
        self.theme_color = theme_color
        self.theme_color_alt = theme_color_alt
        self.background_opacity = background_opacity
        self.base_theme = base_theme
        self.colors = {
            "selection-background": self.theme_color,
            "selection-hover": self.theme_color_alt,
            "focus-border": self.theme_color,
            "progress-bar": self.theme_color,
            "title": self.theme_color,
            "theme_text": theme_text,
        }
        if base_theme == "dark":
            self.colors.update(
                {
                    "indicator-background": "#444444",
                    "neutral-selection-background": "#555555",
                    "neutral-selection-hover": "#666666",
                    "negative-selection-background": "#FF5555",
                    "negative-selection-hover": "#FF3333",
                    "disabled-selection": "rgba(85, 85, 85, 200)",
                    "disabled-selection-text": "#888888",
                    "border": "#555555",
                    "tab-background": "#444444",
                    "tab-bar-background": "#242424",
                    "tab-selection-background": "#333333",
                    "qframe-background": "rgba(51, 51, 51, 200)",
                    "qdialog-background": "rgba(46, 46, 46, 240)",
                    "sidebar-background": "rgba(46, 46, 46, 180)",
                    "sidebar-border": "#3E3E3E",
                    "label": "#BBBBBB",
                    "label-hover": "rgba(62, 62, 62, 150)",
                    "text": "white",
                    "progress-bar-background": "rgba(68, 68, 68, 150)",
                    "home-window-background": "rgba(51, 51, 51, 150)",
                    "text-box-background": "rgba(68, 68, 68, 200)",
                }
            )
        else:
            self.colors.update(
                {
                    "selection-background": self.theme_color,
                    "selection-hover": self.theme_color_alt,
                    "focus-border": self.theme_color,
                    "progress-bar": self.theme_color,
                    "title": self.theme_color,
                    "indicator-background": "#CCCCCC",
                    "neutral-selection-background": "#DDDDDD",
                    "neutral-selection-hover": "#EEEEEE",
                    "negative-selection-background": "#A00000",
                    "negative-selection-hover": "#DF0000",
                    "disabled-selection": "rgba(200, 200, 200, 200)",
                    "disabled-selection-text": "#777777",
                    "border": "#DDDDDD",
                    "tab-background": "#EEEEEE",
                    "tab-bar-background": "#C2C2C2",
                    "tab-selection-background": "#F0F0F0",
                    "qframe-background": "rgba(230, 230, 230, 200)",
                    "qdialog-background": "rgba(235, 235, 235, 240)",
                    "sidebar-background": "rgba(235, 235, 235, 180)",
                    "sidebar-border": "#C1C1C1",
                    "label": "#444444",
                    "label-hover": "rgba(193, 193, 193, 150)",
                    "text": "black",
                    "progress-bar-background": "rgba(204, 204, 204, 150)",
                    "home-window-background": "rgba(230, 230, 230, 240)",
                    "text-box-background": "rgba(204, 204, 204, 200)",
                }
            )

    def get_color(self, component):
        return self.colors.get(component, None)

    def get_background_opacity(self):
        return self.background_opacity

    def get_base_theme(self):
        return self.base_theme


class GreenThemePalette(ColorPalette):
    """
    绿色主题色, 适用于深色主题
    """

    def __init__(self):
        super().__init__(
            theme_color="#4CAF50", theme_color_alt="#45a049", theme_text="white"
        )


class BlueThemePalette(ColorPalette):
    """
    蓝色主题色, 适用于深色主题
    """

    def __init__(self):
        super().__init__(
            theme_color="#66ccff", theme_color_alt="#26aaec", theme_text="white"
        )


class DarkGreenThemePalette(ColorPalette):
    """
    深绿色主题色, 适用于浅色主题
    """

    def __init__(self):
        super().__init__(
            theme_color="#0A410C",
            theme_color_alt="#18721B",
            theme_text="white",
            background_opacity=0.5,
            base_theme="light",
        )


class ThemeManager(QObject):
    """
    主题管理器单例
    """

    _instance = None  # 单例实例

    updated = Signal()

    def __new__(cls):
        if cls._instance is None:
            # 创建单例对象
            cls._instance = super(ThemeManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "initialized", False):
            return
        super().__init__()
        self.initialized = True
        # 默认使用绿色主题
        self.current_color_palette = GreenThemePalette()

    def set_palette(self, palette):
        if not isinstance(palette, ColorPalette):
            raise TypeError("Expected a ColorPalette instance.")
        self.current_color_palette = palette

    def setTheme(self, theme):
        match theme:
            case "light":
                self.set_palette(DarkGreenThemePalette())
            case "dark":
                self.set_palette(GreenThemePalette())
            case _:
                self.set_palette(BlueThemePalette())
        self.updated.emit()

    def get_palette(self):
        return self.current_color_palette

    def get_color(self, component):
        return self.current_color_palette.get_color(component)

    # 提供简化接口，等同于 get_color
    def get(self, component):
        return self.get_color(component)

    def get_background_opacity(self):
        return self.current_color_palette.get_background_opacity()

    def get_base_theme(self):
        return self.current_color_palette.get_base_theme()
