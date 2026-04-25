"""
路径管理工具模块。

提供应用程序中各类路径的获取功能，确保跨平台兼容性。
"""

from pathlib import Path
from typing import List


STYLE_FILES: List[str] = [
    "base.qss",
    "buttons.qss",
    "inputs.qss",
    "table.qss",
    "navigation.qss",
    "dialogs.qss",
    "calendar.qss",
    "clothing.qss",
]


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


def get_style_file_paths() -> List[Path]:
    """
    获取所有样式文件路径列表。

    Returns:
        样式文件路径的列表。
    """
    style_path = get_style_path()
    return [style_path / filename for filename in STYLE_FILES]


def load_combined_styles() -> str:
    """
    加载并合并所有样式文件内容。

    Returns:
        合并后的样式字符串。
    """
    combined_styles: List[str] = []
    style_path = get_style_path()

    for filename in STYLE_FILES:
        file_path = style_path / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    combined_styles.append(f.read())
            except OSError as e:
                print(f"加载样式文件 {filename} 失败: {e}")

    return "\n\n".join(combined_styles)


def get_clothing_file_path() -> Path:
    """
    获取衣物数据文件路径。

    Returns:
        衣物数据文件的 Path 对象。
    """
    return get_data_path() / "clothing.json"
