from setuptools import setup, find_packages

setup(
    name="item-record-manager",
    version="1.0.0",
    description="物品记录管理器",
    packages=find_packages(),
    install_requires=[
        "PySide6==6.6.0"
    ],
    entry_points={
        "console_scripts": [
            "item-record-manager=app.main:main"
        ]
    }
)