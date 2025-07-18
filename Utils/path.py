import os
import sys

import appdirs

if getattr(sys, "frozen", False):
    if hasattr(sys, "_MEIPASS"):
        base_path: str = sys._MEIPASS
elif "__compiled__" in globals():
    base_path: str = os.path.dirname(os.path.abspath(__file__))     # Nuitka单文件打包
else:
    base_path: str = os.path.dirname(os.path.abspath(sys.argv[0]))  # 非打包，源码运行

# 可执行文件在计算机中的固定目录
exe_path: str = os.path.dirname(os.path.abspath(sys.argv[0]))
cwd_path: str = os.getcwd()

# 用户数据目录
data_path: str = appdirs.user_data_dir("OrionLauncher")
# 创建数据目录
if not os.path.exists(data_path):
    os.makedirs(data_path)

