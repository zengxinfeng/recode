"""
物品记录管理器安装配置。

使用 setuptools 进行包的安装配置。
"""

from setuptools import find_packages, setup

setup(
    name="item-record-manager",
    version="1.0.0",
    description="物品记录管理器",
    author="",
    packages=find_packages(),
    install_requires=[
        "PySide6==6.6.0",
    ],
    entry_points={
        "console_scripts": [
            "item-record-manager=app.main:main",
        ],
    },
    python_requires=">=3.10",
)
