import logging
import os
import sys

import appdirs

from src.core.Repository import path
from src.core.Repository.Config import Constant


# 随 Nuitka/Pyinstaller 静态打包进可执行文件的资源文件释放的临时目录
if getattr(sys, "frozen", False):
    if hasattr(sys, "_MEIPASS"):
        path.set("base_path", sys._MEIPASS)  # Pyinstaller 单文件打包
else:
    path.set(
        "base_path", os.path.dirname(os.path.abspath(__file__))
    )  # 非打包 & Nuitka单文件打包
# 可执行文件在计算机中的固定目录
path.set("exe_path", os.path.dirname(os.path.abspath(sys.argv[0])))
# 当前工作目录
path.set("cwd_path", os.getcwd())

# 用户数据目录
path.set("data_path", appdirs.user_data_dir(Constant.name))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")