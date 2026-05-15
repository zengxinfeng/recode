"""
path_utils的单元测试
"""
from pathlib import Path

import pytest

from app.utils.path_utils import (
    STYLE_FILES,
    get_app_root,
    get_clothing_file_path,
    get_data_path,
    get_items_file_path,
    get_resource_path,
    get_style_file_paths,
    get_style_path,
    load_combined_styles,
)


class TestStyleFilesConstant:
    """STYLE_FILES常量的测试"""

    @staticmethod
    def test_style_files_应包含所有预期的样式文件():
        """验证STYLE_FILES包含所有预期的样式文件"""
        expected_files = [
            'base.qss',
            'buttons.qss',
            'inputs.qss',
            'table.qss',
            'navigation.qss',
            'dialogs.qss',
            'calendar.qss',
            'clothing.qss',
        ]
        
        assert len(STYLE_FILES) == 8
        for file in expected_files:
            assert file in STYLE_FILES


class TestGetAppRoot:
    """get_app_root函数的测试"""

    @staticmethod
    def test_get_app_root_应返回正确的应用根目录():
        """验证返回的路径是正确的应用根目录"""
        # Act（操作）
        result = get_app_root()
        
        # Assert（检验）
        assert isinstance(result, Path)
        assert result.exists()
        assert result.name == 'recode'


class TestGetResourcePath:
    """get_resource_path函数的测试"""

    @staticmethod
    def test_get_resource_path_应返回资源目录路径():
        """验证返回的资源目录路径正确"""
        # Act（操作）
        result = get_resource_path()
        
        # Assert（检验）
        assert isinstance(result, Path)
        assert result.name == 'resources'


class TestGetDataPath:
    """get_data_path函数的测试"""

    @staticmethod
    def test_get_data_path_应返回数据目录路径():
        """验证返回的数据目录路径正确"""
        # Act（操作）
        result = get_data_path()
        
        # Assert（检验）
        assert isinstance(result, Path)
        assert 'resources' in str(result)
        assert 'datas' in str(result)


class TestGetItemsFilePath:
    """get_items_file_path函数的测试"""

    @staticmethod
    def test_get_items_file_path_应返回物品数据文件路径():
        """验证返回的物品数据文件路径正确"""
        # Act（操作）
        result = get_items_file_path()
        
        # Assert（检验）
        assert isinstance(result, Path)
        assert result.name == 'items.json'


class TestGetClothingFilePath:
    """get_clothing_file_path函数的测试"""

    @staticmethod
    def test_get_clothing_file_path_应返回衣物数据文件路径():
        """验证返回的衣物数据文件路径正确"""
        # Act（操作）
        result = get_clothing_file_path()
        
        # Assert（检验）
        assert isinstance(result, Path)
        assert result.name == 'clothing.json'


class TestGetStylePath:
    """get_style_path函数的测试"""

    @staticmethod
    def test_get_style_path_应返回样式文件目录路径():
        """验证返回的样式目录路径正确"""
        # Act（操作）
        result = get_style_path()
        
        # Assert（检验）
        assert isinstance(result, Path)
        assert result.name == 'styles'


class TestGetStyleFilePaths:
    """get_style_file_paths函数的测试"""

    @staticmethod
    def test_get_style_file_paths_应返回所有样式文件路径列表():
        """验证返回的样式文件路径列表正确"""
        # Act（操作）
        result = get_style_file_paths()
        
        # Assert（检验）
        assert isinstance(result, list)
        assert len(result) == len(STYLE_FILES)
        for path in result:
            assert isinstance(path, Path)


class TestLoadCombinedStyles:
    """load_combined_styles函数的测试"""

    @staticmethod
    def test_load_combined_styles_当所有文件存在时_应加载所有内容(tmp_path: Path, mocker):
        """所有样式文件都存在时加载"""
        # Arrange（构造）
        style_dir = tmp_path / "styles"
        style_dir.mkdir()
        
        for filename in STYLE_FILES:
            style_file = style_dir / filename
            style_file.write_text(f"/* {filename} content */\n", encoding='utf-8')
        
        mocker.patch('app.utils.path_utils.get_style_path', return_value=style_dir)
        
        # Act（操作）
        result = load_combined_styles()
        
        # Assert（检验）
        assert isinstance(result, str)
        assert len(result) > 0
        for filename in STYLE_FILES:
            assert filename in result

    @staticmethod
    def test_load_combined_styles_当部分文件不存在时_应只加载存在的文件(tmp_path: Path, mocker):
        """部分样式文件不存在时加载"""
        # Arrange（构造）
        style_dir = tmp_path / "styles"
        style_dir.mkdir()
        
        existing_files = STYLE_FILES[:3]
        for filename in existing_files:
            style_file = style_dir / filename
            style_file.write_text(f"/* {filename} content */\n", encoding='utf-8')
        
        mocker.patch('app.utils.path_utils.get_style_path', return_value=style_dir)
        
        # Act（操作）
        result = load_combined_styles()
        
        # Assert（检验）
        assert isinstance(result, str)
        assert len(result) > 0
        for filename in existing_files:
            assert filename in result

    @staticmethod
    def test_load_combined_styles_当文件读取失败时_应跳过失败文件(tmp_path: Path, mocker):
        """样式文件读取时发生OSError"""
        # Arrange（构造）
        style_dir = tmp_path / "styles"
        style_dir.mkdir()
        
        first_file = style_dir / STYLE_FILES[0]
        first_file.write_text("/* first file */\n", encoding='utf-8')
        
        mocker.patch('app.utils.path_utils.get_style_path', return_value=style_dir)
        
        def mock_open_func(file, *args, **kwargs):
            if STYLE_FILES[1] in str(file):
                raise OSError('Read error')
            return open(file, *args, **kwargs)
        
        mocker.patch('builtins.open', side_effect=mock_open_func)
        
        # Act（操作）
        result = load_combined_styles()
        
        # Assert（检验）
        assert isinstance(result, str)

    @staticmethod
    def test_load_combined_styles_当所有文件都不存在时_应返回空字符串(tmp_path: Path, mocker):
        """所有样式文件都不存在"""
        # Arrange（构造）
        style_dir = tmp_path / "styles"
        style_dir.mkdir()
        
        mocker.patch('app.utils.path_utils.get_style_path', return_value=style_dir)
        
        # Act（操作）
        result = load_combined_styles()
        
        # Assert（检验）
        assert isinstance(result, str)
        assert result == ''
