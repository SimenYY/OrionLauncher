# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# 添加项目根目录到Python路径，以便导入模块
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "OrionLauncher"
copyright = "2025, Hisatri"
author = "Hisatri"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # 自动生成API文档
    "sphinx.ext.autosummary",  # 自动生成摘要
    "sphinx.ext.viewcode",  # 查看源码链接
    "sphinx.ext.napoleon",  # 支持Google/NumPy风格的docstring
    "sphinx.ext.intersphinx",  # 交叉引用其他项目文档
    "sphinx.ext.todo",  # Todo标记支持
    "sphinx.ext.coverage",  # 文档覆盖率
]

# 自动文档配置
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# 自动摘要配置
autosummary_generate = True
autosummary_imported_members = True

# Napoleon配置（Google风格docstring）
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# 交叉引用配置
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pyside6": ("https://doc.qt.io/qtforpython/", None),
}

# Todo扩展配置
todo_include_todos = True

templates_path = ["_templates"]
exclude_patterns = []

language = "zh_CN"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"  # 使用Read the Docs主题
html_static_path = ["_static"]

# HTML主题配置
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
}
