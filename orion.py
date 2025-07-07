#!/usr/bin/env python3
"""
Orion Launcher - Minecraft 启动器

主程序入口
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale, QTranslator

from View import MainWindow
from Core.Repository import path

# 随 Nuitka/Pyinstaller 静态打包进可执行文件的资源文件释放的临时目录
if getattr(sys, 'frozen', False):
    if hasattr(sys, '_MEIPASS'):
        path.set("base_path", sys._MEIPASS)     # Pyinstaller 单文件打包
else:
    path.set("base_path", os.path.dirname(os.path.abspath(__file__))) # 非打包 & Nuitka单文件打包
# 可执行文件在计算机中的固定目录
path.set("exe_path", os.path.dirname(os.path.abspath(sys.argv[0])))
# 当前工作目录
path.set("cwd_path", os.getcwd())



def main():
    """主程序入口"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("Orion Launcher")
    app.setApplicationDisplayName("Orion Launcher")
    
    # 设置中文本地化
    locale = QLocale(QLocale.Chinese, QLocale.China)
    translator = QTranslator()
    if translator.load(locale, "orion", "_", os.path.join(os.path.dirname(__file__), "translations")):
        app.installTranslator(translator)
    
    # 设置样式表
    app.setStyleSheet("""
        QWidget {
            background-color: #2E2E2E;
            color: #EEEEEE;
            font-family: "Microsoft YaHei", "SimHei", sans-serif;
        }
        QLabel {
            background: transparent;
        }
        QCheckBox {
            background: transparent;
        }
    """)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
