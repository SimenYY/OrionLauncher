"""
自动化构建脚本，用于Workflow
"""
import os
import sys
import codecs
import argparse
import subprocess

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())     # 设置stdout编码为UTF-8
assert sys.version_info >= (3, 12), "Python 3.12+ required"     # 检查Python版本

parser = argparse.ArgumentParser(description="Build Orion Launcher")
parser.add_argument("-n", "--name", help="Output file name", default="Orion Launcher")
args = parser.parse_args()

build_command = [
    "pyinstaller",
    "orion.py",
    "--noconfirm",         # 覆盖输出目录时不需确认
    "-F",                  # 单文件
    # "-i", "logo.png",      # 图标
    "--add-data", f"src{os.pathsep}src", # 添加数据文件
    "-n", args.name        # 输出文件名
]
subprocess.run(build_command)