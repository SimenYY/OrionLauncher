"""
用户登录界面主题

用于统一管理界面组件的颜色配置
"""


class ColorPalette:
    """
    基础颜色配置
    """

    def __init__(self, theme_color, theme_color_dark):
        self.theme_color = theme_color
        self.theme_color_dark = theme_color_dark
        self.colors = {
            "selection-background": self.theme_color,
            "selection-hover": self.theme_color_dark,
            "focus-border": self.theme_color,
            "progress-bar": self.theme_color,
            "title": self.theme_color,
            "indicator-background": "#444444",
            "neutral-selection-background": "#555555",
            "neutral-selection-hover": "#666666",
            "negative-selection-background": "#FF5555",
            "negative-selection-hover": "#FF3333",
            "disabled-selection": "rgba(85, 85, 85, 200)",
            "disabled-selection-text": "#888888",
            "border": "#555555",
            "tab-background": "#444444",
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

    def get_color(self, component):
        return self.colors.get(component, None)


class GreenThemePalette(ColorPalette):
    """
    绿色主题色
    """

    def __init__(self):
        super().__init__(theme_color="#4CAF50", theme_color_dark="#45a049")


class BlueThemePalette(ColorPalette):
    """
    蓝色主题色
    """

    def __init__(self):
        super().__init__()
        super().__init__(theme_color="#66ccff", theme_color_dark="#26aaec")


class ThemeManager:
    """
    主题管理器单例
    """

    _instance = None  # 单例实例

    def __new__(cls):
        if cls._instance is None:
            # 创建单例对象
            cls._instance = super(ThemeManager, cls).__new__(cls)
            # 默认使用绿色主题
            cls._instance.current_color_palette = GreenThemePalette()
        return cls._instance

    def set_palette(self, palette):
        if not isinstance(palette, ColorPalette):
            raise TypeError("Expected a ColorPalette instance.")
        self.current_color_palette = palette

    def get_palette(self):
        return self.current_color_palette

    def get_color(self, component):
        return self.current_color_palette.get_color(component)

    # 提供简化接口，等同于 get_color
    def get(self, component):
        return self.get_color(component)
