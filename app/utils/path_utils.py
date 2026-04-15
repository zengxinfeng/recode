"""
路径管理工具模块。

提供应用程序中各类路径的获取功能，确保跨平台兼容性。
"""

from pathlib import Path


def get_app_root() -> Path:
    """
    获取应用程序根目录。

    Returns:
        应用程序根目录的 Path 对象。
    """
    return Path(__file__).parent.parent


def get_resource_path() -> Path:
    """
    获取资源目录。

    Returns:
        资源目录的 Path 对象。
    """
    return get_app_root() / "resources"


def get_data_path() -> Path:
    """
    获取数据目录。

    Returns:
        数据目录的 Path 对象。
    """
    return get_resource_path() / "datas"


def get_items_file_path() -> Path:
    """
    获取物品数据文件路径。

    Returns:
        物品数据文件的 Path 对象。
    """
    return get_data_path() / "items.json"


def get_style_path() -> Path:
    """
    获取样式文件目录路径。

    Returns:
        样式文件目录的 Path 对象。
    """
    return get_resource_path() / "styles"


def get_main_style_path() -> Path:
    """
    获取主样式文件路径。

    Returns:
        主样式文件的 Path 对象。
    """
    return get_style_path() / "main.qss"


def get_dark_style_path() -> Path:
    """
    获取暗黑主题样式文件路径。

    Returns:
        暗黑主题样式文件的 Path 对象。
    """
    return get_style_path() / "dark.qss"


def get_clothing_file_path() -> Path:
    """
    获取衣物数据文件路径。

    Returns:
        衣物数据文件的 Path 对象。
    """
    return get_data_path() / "clothing.json"
