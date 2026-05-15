"""
models模块的测试fixtures
"""
from pathlib import Path

import pytest
from PySide6.QtCore import QDate


@pytest.fixture(name='sample_item')
def sample_item_fixture():
    """提供示例物品数据"""
    return {
        'name': '测试手机',
        'price': 1000.0,
        'purchase_date': '2024-01-01',
        'status': 'active',
        'discontinued_date': None,
        'discontinued_reason': None,
    }


@pytest.fixture(name='sample_clothing')
def sample_clothing_fixture():
    """提供示例衣物数据"""
    return {
        'name': '测试T恤',
        'clothing_type': '上衣',
        'price': 100.0,
        'purchase_date': '2024-01-01',
        'status': 'active',
        'discontinued_date': None,
        'discontinued_reason': None,
    }


@pytest.fixture(name='mock_qdate_current')
def mock_qdate_current_fixture(mocker):
    """统一mock QDate.currentDate()"""
    fixed_date = QDate(2024, 1, 15)
    mocker.patch.object(QDate, 'currentDate', return_value=fixed_date)
    return fixed_date


@pytest.fixture(name='temp_items_file')
def temp_items_file_fixture(tmp_path: Path):
    """提供临时物品数据文件路径"""
    return tmp_path / "items.json"


@pytest.fixture(name='temp_clothing_file')
def temp_clothing_file_fixture(tmp_path: Path):
    """提供临时衣物数据文件路径"""
    return tmp_path / "clothing.json"


@pytest.fixture(name='active_item')
def active_item_fixture():
    """提供活跃状态的物品数据"""
    return {
        'name': '测试手机',
        'price': 1000.0,
        'purchase_date': '2024-01-01',
        'status': 'active',
        'discontinued_date': None,
        'discontinued_reason': None,
    }


@pytest.fixture(name='discontinued_item')
def discontinued_item_fixture():
    """提供停用状态的物品数据"""
    return {
        'name': '测试手机',
        'price': 1000.0,
        'purchase_date': '2024-01-01',
        'status': 'discontinued',
        'discontinued_date': '2024-03-01',
        'discontinued_reason': '转卖',
    }


@pytest.fixture(name='multiple_items')
def multiple_items_fixture():
    """提供多个物品的列表"""
    return [
        {
            'name': '手机1',
            'price': 1000.0,
            'purchase_date': '2024-01-01',
            'status': 'active',
            'discontinued_date': None,
            'discontinued_reason': None,
        },
        {
            'name': '手机2',
            'price': 2000.0,
            'purchase_date': '2024-01-02',
            'status': 'active',
            'discontinued_date': None,
            'discontinued_reason': None,
        },
    ]


@pytest.fixture(name='item_manager_factory')
def item_manager_factory_fixture(tmp_path: Path, mocker):
    """提供ItemManager工厂函数"""
    def create_manager(items=None, file_path=None):
        from app.models.item_manager import ItemManager
        
        if file_path is None:
            file_path = tmp_path / "items.json"
        
        mocker.patch('app.models.item_manager.get_items_file_path', return_value=file_path)
        
        manager = ItemManager.__new__(ItemManager)
        manager.save_path = file_path
        manager.items = items if items is not None else []
        
        return manager
    
    return create_manager


@pytest.fixture(name='clothing_manager_factory')
def clothing_manager_factory_fixture(tmp_path: Path, mocker):
    """提供ClothingManager工厂函数"""
    def create_manager(items=None, file_path=None):
        from app.models.clothing_manager import ClothingManager
        
        if file_path is None:
            file_path = tmp_path / "clothing.json"
        
        mocker.patch('app.models.clothing_manager.get_clothing_file_path', return_value=file_path)
        
        manager = ClothingManager.__new__(ClothingManager)
        manager.save_path = file_path
        manager.items = items if items is not None else []
        
        return manager
    
    return create_manager
