"""
ClothingManager的单元测试
"""
import json
from pathlib import Path

import pytest
from PySide6.QtCore import QDate

from app.models.clothing_manager import ClothingManager, DISCONTINUE_REASONS


class TestClothingManagerInit:
    """ClothingManager初始化的测试"""

    @staticmethod
    def test_init_当文件不存在时_应初始化空列表(tmp_path: Path, mocker):
        """测试初始化时文件不存在，应初始化为空列表"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        mocker.patch('app.models.clothing_manager.get_clothing_file_path', return_value=test_file)
        
        # Act（操作）
        manager = ClothingManager()
        
        # Assert（检验）
        assert manager.items == []

    @staticmethod
    def test_init_当文件存在且有有效数据时_应加载数据(tmp_path: Path, mocker):
        """测试初始化时文件存在且有有效数据，应正确加载"""
        # Arrange（构造）
        test_data = [
            {'name': 'T恤', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'}
        ]
        test_file = tmp_path / "clothing.json"
        test_file.write_text(json.dumps(test_data), encoding='utf-8')
        mocker.patch('app.models.clothing_manager.get_clothing_file_path', return_value=test_file)
        
        # Act（操作）
        manager = ClothingManager()
        
        # Assert（检验）
        assert manager.items == test_data


class TestClothingManagerLoadData:
    """ClothingManager加载数据的测试"""

    @staticmethod
    def test_load_data_当文件不存在时_应设置为空列表(tmp_path: Path):
        """测试加载不存在的文件时，应设置为空列表"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.save_path = test_file
        
        # Act（操作）
        manager.load_data()
        
        # Assert（检验）
        assert manager.items == []

    @staticmethod
    def test_load_data_当文件内容无效JSON时_应设置为空列表(tmp_path: Path):
        """测试加载无效JSON文件时，应设置为空列表"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        test_file.write_text('invalid json', encoding='utf-8')
        manager = ClothingManager.__new__(ClothingManager)
        manager.save_path = test_file
        
        # Act（操作）
        manager.load_data()
        
        # Assert（检验）
        assert manager.items == []

    @staticmethod
    def test_load_data_当文件读取失败时_应设置为空列表(tmp_path: Path, mocker):
        """测试文件读取失败时，应设置为空列表"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.save_path = test_file
        mocker.patch('builtins.open', side_effect=OSError('Read error'))
        
        # Act（操作）
        manager.load_data()
        
        # Assert（检验）
        assert manager.items == []


class TestClothingManagerSaveData:
    """ClothingManager保存数据的测试"""

    @staticmethod
    def test_save_data_应正确保存数据到文件(tmp_path: Path):
        """测试保存数据应正确写入文件"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.save_path = test_file
        manager.items = [
            {'name': 'T恤', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'}
        ]
        
        # Act（操作）
        manager.save_data()
        
        # Assert（检验）
        assert test_file.exists()
        saved_data = json.loads(test_file.read_text(encoding='utf-8'))
        assert saved_data == manager.items


class TestClothingManagerAddItem:
    """ClothingManager添加衣物的测试"""

    @staticmethod
    def test_add_item_当给定有效数据时_应添加到列表(tmp_path: Path):
        """测试添加有效衣物数据"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = []
        manager.save_path = test_file
        
        name = 'T恤'
        clothing_type = '上衣'
        price = 100.0
        purchase_date = QDate(2024, 1, 1)
        
        # Act（操作）
        manager.add_item(name, clothing_type, price, purchase_date)
        
        # Assert（检验）
        assert len(manager.items) == 1
        assert manager.items[0]['name'] == name
        assert manager.items[0]['clothing_type'] == clothing_type
        assert manager.items[0]['price'] == price
        assert manager.items[0]['purchase_date'] == '2024-01-01'
        assert manager.items[0]['status'] == 'active'
        assert manager.items[0]['discontinued_date'] is None
        assert manager.items[0]['discontinued_reason'] is None

    @staticmethod
    def test_add_item_当价格为整数时_应转换为浮点数(tmp_path: Path):
        """测试添加价格为整数时，应转换为浮点数"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = []
        manager.save_path = test_file
        
        # Act（操作）
        manager.add_item('T恤', '上衣', 100, QDate(2024, 1, 1))
        
        # Assert（检验）
        assert isinstance(manager.items[0]['price'], float)
        assert manager.items[0]['price'] == 100.0


class TestClothingManagerRemoveItem:
    """ClothingManager删除衣物的测试"""

    @staticmethod
    def test_remove_item_当索引有效时_应删除对应项(tmp_path: Path):
        """测试删除有效索引的衣物"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {'name': 'T恤1', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'},
            {'name': 'T恤2', 'clothing_type': '上衣', 'price': 200.0, 'purchase_date': '2024-01-02'},
        ]
        manager.save_path = test_file
        
        # Act（操作）
        manager.remove_item(0)
        
        # Assert（检验）
        assert len(manager.items) == 1
        assert manager.items[0]['name'] == 'T恤2'

    @staticmethod
    def test_remove_item_当索引无效时_应不执行操作(tmp_path: Path):
        """测试删除无效索引时，应不执行任何操作"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {'name': 'T恤', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'}
        ]
        manager.save_path = test_file
        
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.remove_item(10)
        
        # Assert（检验）
        assert manager.items == original_items

    @staticmethod
    def test_remove_item_当索引为负数时_应不执行操作(tmp_path: Path):
        """测试删除负数索引时，应不执行任何操作"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {'name': 'T恤', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'}
        ]
        manager.save_path = test_file
        
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.remove_item(-1)
        
        # Assert（检验）
        assert manager.items == original_items


class TestClothingManagerUpdateItem:
    """ClothingManager更新衣物的测试"""

    @staticmethod
    def test_update_item_当索引有效时_应更新对应项(tmp_path: Path):
        """测试更新有效索引的衣物"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {
                'name': 'T恤',
                'clothing_type': '上衣',
                'price': 100.0,
                'purchase_date': '2024-01-01',
                'status': 'active',
                'discontinued_date': None,
                'discontinued_reason': None,
            }
        ]
        manager.save_path = test_file
        
        new_name = '衬衫'
        new_type = '上衣'
        new_price = 150.0
        new_date = QDate(2024, 2, 1)
        
        # Act（操作）
        manager.update_item(0, new_name, new_type, new_price, new_date)
        
        # Assert（检验）
        assert manager.items[0]['name'] == new_name
        assert manager.items[0]['clothing_type'] == new_type
        assert manager.items[0]['price'] == new_price
        assert manager.items[0]['purchase_date'] == '2024-02-01'

    @staticmethod
    def test_update_item_应保留原有的状态信息(tmp_path: Path):
        """测试更新时应保留原有的状态信息"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {
                'name': 'T恤',
                'clothing_type': '上衣',
                'price': 100.0,
                'purchase_date': '2024-01-01',
                'status': 'discontinued',
                'discontinued_date': '2024-03-01',
                'discontinued_reason': '报废',
            }
        ]
        manager.save_path = test_file
        
        # Act（操作）
        manager.update_item(0, '衬衫', '上衣', 150.0, QDate(2024, 2, 1))
        
        # Assert（检验）
        assert manager.items[0]['status'] == 'discontinued'
        assert manager.items[0]['discontinued_date'] == '2024-03-01'
        assert manager.items[0]['discontinued_reason'] == '报废'

    @staticmethod
    def test_update_item_当索引无效时_应不执行操作(tmp_path: Path):
        """测试更新无效索引时，应不执行任何操作"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {'name': 'T恤', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'}
        ]
        manager.save_path = test_file
        
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.update_item(10, '衬衫', '上衣', 150.0, QDate(2024, 2, 1))
        
        # Assert（检验）
        assert manager.items == original_items


class TestClothingManagerDiscontinueItem:
    """ClothingManager停用衣物的测试"""

    @staticmethod
    def test_discontinue_item_当索引有效时_应标记为停用(tmp_path: Path):
        """测试停用有效索引的衣物"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {
                'name': 'T恤',
                'clothing_type': '上衣',
                'price': 100.0,
                'purchase_date': '2024-01-01',
                'status': 'active',
                'discontinued_date': None,
                'discontinued_reason': None,
            }
        ]
        manager.save_path = test_file
        
        discontinued_date = QDate(2024, 3, 1)
        discontinued_reason = '报废'
        
        # Act（操作）
        manager.discontinue_item(0, discontinued_date, discontinued_reason)
        
        # Assert（检验）
        assert manager.items[0]['status'] == 'discontinued'
        assert manager.items[0]['discontinued_date'] == '2024-03-01'
        assert manager.items[0]['discontinued_reason'] == '报废'

    @staticmethod
    def test_discontinue_item_当索引无效时_应不执行操作(tmp_path: Path):
        """测试停用无效索引时，应不执行任何操作"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {
                'name': 'T恤',
                'clothing_type': '上衣',
                'price': 100.0,
                'purchase_date': '2024-01-01',
                'status': 'active',
                'discontinued_date': None,
                'discontinued_reason': None,
            }
        ]
        manager.save_path = test_file
        
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.discontinue_item(10, QDate(2024, 3, 1), '报废')
        
        # Assert（检验）
        assert manager.items == original_items


class TestClothingManagerReactivateItem:
    """ClothingManager重新启用衣物的测试"""

    @staticmethod
    def test_reactivate_item_当索引有效时_应标记为活跃(tmp_path: Path):
        """测试重新启用有效索引的衣物"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {
                'name': 'T恤',
                'clothing_type': '上衣',
                'price': 100.0,
                'purchase_date': '2024-01-01',
                'status': 'discontinued',
                'discontinued_date': '2024-03-01',
                'discontinued_reason': '报废',
            }
        ]
        manager.save_path = test_file
        
        # Act（操作）
        manager.reactivate_item(0)
        
        # Assert（检验）
        assert manager.items[0]['status'] == 'active'
        assert manager.items[0]['discontinued_date'] is None
        assert manager.items[0]['discontinued_reason'] is None

    @staticmethod
    def test_reactivate_item_当索引无效时_应不执行操作(tmp_path: Path):
        """测试重新启用无效索引时，应不执行任何操作"""
        # Arrange（构造）
        test_file = tmp_path / "clothing.json"
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {
                'name': 'T恤',
                'clothing_type': '上衣',
                'price': 100.0,
                'purchase_date': '2024-01-01',
                'status': 'discontinued',
                'discontinued_date': '2024-03-01',
                'discontinued_reason': '报废',
            }
        ]
        manager.save_path = test_file
        
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.reactivate_item(10)
        
        # Assert（检验）
        assert manager.items == original_items


class TestClothingManagerGetItems:
    """ClothingManager获取衣物列表的测试"""

    @staticmethod
    def test_get_items_应返回所有衣物列表():
        """测试获取所有衣物列表"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {'name': 'T恤1', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'},
            {'name': 'T恤2', 'clothing_type': '上衣', 'price': 200.0, 'purchase_date': '2024-01-02'},
        ]
        
        # Act（操作）
        result = manager.get_items()
        
        # Assert（检验）
        assert result == manager.items
        assert len(result) == 2


class TestClothingManagerGetAllClothingTypes:
    """ClothingManager获取所有衣物类型的测试"""

    @staticmethod
    def test_get_all_clothing_types_应返回不重复的类型列表():
        """测试获取所有不重复的衣物类型"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {'name': 'T恤1', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'},
            {'name': '牛仔裤', 'clothing_type': '裤子', 'price': 200.0, 'purchase_date': '2024-01-02'},
            {'name': 'T恤2', 'clothing_type': '上衣', 'price': 150.0, 'purchase_date': '2024-01-03'},
        ]
        
        # Act（操作）
        result = manager.get_all_clothing_types()
        
        # Assert（检验）
        assert result == ['上衣', '裤子']

    @staticmethod
    def test_get_all_clothing_types_当列表为空时_应返回空列表():
        """测试当衣物列表为空时，应返回空列表"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = []
        
        # Act（操作）
        result = manager.get_all_clothing_types()
        
        # Assert（检验）
        assert result == []

    @staticmethod
    def test_get_all_clothing_types_当类型为空时_应忽略该项():
        """测试当衣物类型为空时，应忽略该项"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {'name': 'T恤', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'},
            {'name': '未知', 'clothing_type': '', 'price': 50.0, 'purchase_date': '2024-01-02'},
        ]
        
        # Act（操作）
        result = manager.get_all_clothing_types()
        
        # Assert（检验）
        assert result == ['上衣']


class TestClothingManagerCalculateDaysUsed:
    """ClothingManager计算使用天数的测试"""

    @staticmethod
    def test_calculate_days_used_当衣物为活跃状态时_应计算到当前日期(mocker):
        """测试活跃状态衣物应计算到当前日期的使用天数"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        
        purchase_date = QDate(2024, 1, 1)
        current_date = QDate(2024, 1, 10)
        
        item = {
            'purchase_date': '2024-01-01',
            'status': 'active',
            'discontinued_date': None,
        }
        
        # Act（操作）
        mocker.patch.object(QDate, 'currentDate', return_value=current_date)
        result = manager.calculate_days_used(item)
        
        # Assert（检验）
        assert result == 10

    @staticmethod
    def test_calculate_days_used_当衣物为停用状态时_应计算到停用日期():
        """测试停用状态衣物应计算到停用日期的使用天数"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        
        item = {
            'purchase_date': '2024-01-01',
            'status': 'discontinued',
            'discontinued_date': '2024-01-10',
        }
        
        # Act（操作）
        result = manager.calculate_days_used(item)
        
        # Assert（检验）
        assert result == 10

    @staticmethod
    def test_calculate_days_used_当计算结果为负数时_应返回最小值1(mocker):
        """测试当计算结果为负数时，应返回最小值1"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        
        future_date = QDate(2025, 1, 1)
        current_date = QDate(2024, 1, 1)
        
        item = {
            'purchase_date': '2025-01-01',
            'status': 'active',
            'discontinued_date': None,
        }
        
        # Act（操作）
        mocker.patch.object(QDate, 'currentDate', return_value=current_date)
        result = manager.calculate_days_used(item)
        
        # Assert（检验）
        assert result == 1


class TestClothingManagerGetTotalAssets:
    """ClothingManager计算总资产的测试"""

    @staticmethod
    def test_get_total_assets_应返回所有衣物的总价格():
        """测试计算所有衣物的总资产"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = [
            {'name': 'T恤', 'clothing_type': '上衣', 'price': 100.0, 'purchase_date': '2024-01-01'},
            {'name': '牛仔裤', 'clothing_type': '裤子', 'price': 200.0, 'purchase_date': '2024-01-02'},
        ]
        
        # Act（操作）
        result = manager.get_total_assets()
        
        # Assert（检验）
        assert result == 300.0

    @staticmethod
    def test_get_total_assets_当列表为空时_应返回0():
        """测试当衣物列表为空时，应返回0"""
        # Arrange（构造）
        manager = ClothingManager.__new__(ClothingManager)
        manager.items = []
        
        # Act（操作）
        result = manager.get_total_assets()
        
        # Assert（检验）
        assert result == 0.0


class TestDiscontinueReasons:
    """停用原因常量的测试"""

    @staticmethod
    def test_discontinue_reasons_应包含所有预定义原因():
        """测试停用原因列表应包含所有预定义原因"""
        # Assert（检验）
        assert '报废' in DISCONTINUE_REASONS
        assert '转卖' in DISCONTINUE_REASONS
        assert '闲置' in DISCONTINUE_REASONS
        assert '其他' in DISCONTINUE_REASONS
        assert len(DISCONTINUE_REASONS) == 4
