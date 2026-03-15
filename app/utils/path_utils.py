from pathlib import Path

# 获取应用程序根目录
def get_app_root():
    """
    获取应用程序根目录
    :return: 应用程序根目录的 Path 对象
    """
    return Path(__file__).parent.parent

# 获取资源目录
def get_resource_path():
    """
    获取资源目录
    :return: 资源目录的 Path 对象
    """
    return get_app_root() / "resources"

# 获取数据目录
def get_data_path():
    """
    获取数据目录
    :return: 数据目录的 Path 对象
    """
    return get_resource_path() / "datas"

# 获取物品数据文件路径
def get_items_file_path():
    """
    获取物品数据文件路径
    :return: 物品数据文件的 Path 对象
    """
    return get_data_path() / "items.json"

# 获取样式文件路径
def get_style_path():
    """
    获取样式文件目录路径
    :return: 样式文件目录的 Path 对象
    """
    return get_resource_path() / "styles"

# 获取主样式文件路径
def get_main_style_path():
    """
    获取主样式文件路径
    :return: 主样式文件的 Path 对象
    """
    return get_style_path() / "main.qss"
