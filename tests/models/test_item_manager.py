"""
ItemManager的单元测试
"""
import json
from pathlib import Path

import pytest
from PySide6.QtCore import QDate

from app.models.item_manager import ItemManager, DISCONTINUE_REASONS


class TestDiscontinueReasonsConstant:
    """DISCONTINUE_REASONS常量的测试"""

    @staticmethod
    def test_discontinue_reasons_应包含所有预期的停用原因():
        """验证DISCONTINUE_REASONS包含所有预期的停用原因"""
        # Assert（检验）
        assert '报废' in DISCONTINUE_REASONS
        assert '转卖' in DISCONTINUE_REASONS
        assert '闲置' in DISCONTINUE_REASONS
        assert '其他' in DISCONTINUE_REASONS
        assert len(DISCONTINUE_REASONS) == 4


class TestItemManagerInit:
    """ItemManager初始化的测试"""

    @staticmethod
    def test_init_当文件不存在时_应初始化空列表(temp_items_file: Path, mocker):
        """测试初始化时文件不存在，应初始化为空列表"""
        # Arrange（构造）
        mocker.patch('app.models.item_manager.get_items_file_path', return_value=temp_items_file)
        
        # Act（操作）
        manager = ItemManager()
        
        # Assert（检验）
        assert manager.items == []

    @staticmethod
    def test_init_当文件存在且有有效数据时_应加载数据(temp_items_file: Path, mocker):
        """测试初始化时文件存在且有有效数据，应正确加载"""
        # Arrange（构造）
        test_data = [
            {'name': '手机', 'price': 1000.0, 'purchase_date': '2024-01-01'}
        ]
        temp_items_file.write_text(json.dumps(test_data), encoding='utf-8')
        mocker.patch('app.models.item_manager.get_items_file_path', return_value=temp_items_file)
        
        # Act（操作）
        manager = ItemManager()
        
        # Assert（检验）
        assert manager.items == test_data


class TestItemManagerLoadData:
    """ItemManager加载数据的测试"""

    @staticmethod
    def test_load_data_当文件不存在时_应设置为空列表(temp_items_file: Path):
        """测试加载不存在的文件时，应设置为空列表"""
        # Arrange（构造）
        manager = ItemManager.__new__(ItemManager)
        manager.save_path = temp_items_file
        
        # Act（操作）
        manager.load_data()
        
        # Assert（检验）
        assert manager.items == []

    @staticmethod
    def test_load_data_当文件内容无效JSON时_应设置为空列表(temp_items_file: Path):
        """测试加载无效JSON文件时，应设置为空列表"""
        # Arrange（构造）
        temp_items_file.write_text('invalid json', encoding='utf-8')
        manager = ItemManager.__new__(ItemManager)
        manager.save_path = temp_items_file
        
        # Act（操作）
        manager.load_data()
        
        # Assert（检验）
        assert manager.items == []

    @staticmethod
    def test_load_data_当文件读取失败时_应设置为空列表(temp_items_file: Path, mocker):
        """测试文件读取失败时，应设置为空列表"""
        # Arrange（构造）
        manager = ItemManager.__new__(ItemManager)
        manager.save_path = temp_items_file
        mocker.patch('builtins.open', side_effect=OSError('Read error'))
        
        # Act（操作）
        manager.load_data()
        
        # Assert（检验）
        assert manager.items == []


class TestItemManagerSaveData:
    """ItemManager保存数据的测试"""

    @staticmethod
    def test_save_data_应正确保存数据到_file(item_manager_factory, active_item):
        """测试保存数据应正确写入文件"""
        # Arrange（构造）
        manager = item_manager_factory(items=[active_item])
        
        # Act（操作）
        manager.save_data()
        
        # Assert（检验）
        assert manager.save_path.exists()
        saved_data = json.loads(manager.save_path.read_text(encoding='utf-8'))
        assert saved_data == manager.items


class TestItemManagerAddItem:
    """ItemManager添加物品的测试"""

    @staticmethod
    def test_add_item_当给定有效数据时_应添加到列表(item_manager_factory):
        """测试添加有效物品数据"""
        # Arrange（构造）
        manager = item_manager_factory(items=[])
        
        name = '手机'
        price = 1000.0
        purchase_date = QDate(2024, 1, 1)
        
        # Act（操作）
        manager.add_item(name, price, purchase_date)
        
        # Assert（检验）
        assert len(manager.items) == 1
        assert manager.items[0]['name'] == name
        assert manager.items[0]['price'] == price
        assert manager.items[0]['purchase_date'] == '2024-01-01'
        assert manager.items[0]['status'] == 'active'
        assert manager.items[0]['discontinued_date'] is None
        assert manager.items[0]['discontinued_reason'] is None

    @staticmethod
    def test_add_item_当价格为整数时_应转换为浮点数(item_manager_factory):
        """测试添加价格为整数时，应转换为浮点数"""
        # Arrange（构造）
        manager = item_manager_factory(items=[])
        
        # Act（操作）
        manager.add_item('手机', 1000, QDate(2024, 1, 1))
        
        # Assert（检验）
        assert isinstance(manager.items[0]['price'], float)
        assert manager.items[0]['price'] == 1000.0


class TestItemManagerRemoveItem:
    """ItemManager删除物品的测试"""

    @staticmethod
    def test_remove_item_当索引有效时_应删除对应项(item_manager_factory, multiple_items):
        """测试删除有效索引的物品"""
        # Arrange（构造）
        manager = item_manager_factory(items=multiple_items.copy())
        
        # Act（操作）
        manager.remove_item(0)
        
        # Assert（检验）
        assert len(manager.items) == 1
        assert manager.items[0]['name'] == '手机2'

    @staticmethod
    def test_remove_item_当索引无效时_应不执行操作(item_manager_factory, active_item):
        """测试删除无效索引时，应不执行任何操作"""
        # Arrange（构造）
        manager = item_manager_factory(items=[active_item])
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.remove_item(10)
        
        # Assert（检验）
        assert manager.items == original_items

    @staticmethod
    def test_remove_item_当索引为负数时_应不执行操作(item_manager_factory, active_item):
        """测试删除负数索引时，应不执行任何操作"""
        # Arrange（构造）
        manager = item_manager_factory(items=[active_item])
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.remove_item(-1)
        
        # Assert（检验）
        assert manager.items == original_items


class TestItemManagerUpdateItem:
    """ItemManager更新物品的测试"""

    @staticmethod
    def test_update_item_当索引有效时_应更新对应项(item_manager_factory, active_item):
        """测试更新有效索引的物品"""
        # Arrange（构造）
        manager = item_manager_factory(items=[active_item])
        
        new_name = '平板'
        new_price = 1500.0
        new_date = QDate(2024, 2, 1)
        
        # Act（操作）
        manager.update_item(0, new_name, new_price, new_date)
        
        # Assert（检验）
        assert manager.items[0]['name'] == new_name
        assert manager.items[0]['price'] == new_price
        assert manager.items[0]['purchase_date'] == '2024-02-01'

    @staticmethod
    def test_update_item_应保留原有的状态信息(item_manager_factory, discontinued_item):
        """测试更新时应保留原有的状态信息"""
        # Arrange（构造）
        manager = item_manager_factory(items=[discontinued_item])
        
        # Act（操作）
        manager.update_item(0, '平板', 1500.0, QDate(2024, 2, 1))
        
        # Assert（检验）
        assert manager.items[0]['status'] == 'discontinued'
        assert manager.items[0]['discontinued_date'] == '2024-03-01'
        assert manager.items[0]['discontinued_reason'] == '转卖'

    @staticmethod
    def test_update_item_当索引无效时_应不执行操作(item_manager_factory, active_item):
        """测试更新无效索引时，应不执行任何操作"""
        # Arrange（构造）
        manager = item_manager_factory(items=[active_item])
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.update_item(10, '平板', 1500.0, QDate(2024, 2, 1))
        
        # Assert（检验）
        assert manager.items == original_items


class TestItemManagerDiscontinueItem:
    """ItemManager停用物品的测试"""

    @staticmethod
    def test_discontinue_item_当索引有效时_应标记为停用(item_manager_factory, active_item):
        """测试停用有效索引的物品"""
        # Arrange（构造）
        manager = item_manager_factory(items=[active_item])
        
        discontinued_date = QDate(2024, 3, 1)
        discontinued_reason = '转卖'
        
        # Act（操作）
        manager.discontinue_item(0, discontinued_date, discontinued_reason)
        
        # Assert（检验）
        assert manager.items[0]['status'] == 'discontinued'
        assert manager.items[0]['discontinued_date'] == '2024-03-01'
        assert manager.items[0]['discontinued_reason'] == '转卖'

    @staticmethod
    def test_discontinue_item_当索引无效时_应不执行操作(item_manager_factory, active_item):
        """测试停用无效索引时，应不执行任何操作"""
        # Arrange（构造）
        manager = item_manager_factory(items=[active_item])
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.discontinue_item(10, QDate(2024, 3, 1), '转卖')
        
        # Assert（检验）
        assert manager.items == original_items


class TestItemManagerReactivateItem:
    """ItemManager重新启用物品的测试"""

    @staticmethod
    def test_reactivate_item_当索引有效时_应标记为活跃(item_manager_factory, discontinued_item):
        """测试重新启用有效索引的物品"""
        # Arrange（构造）
        manager = item_manager_factory(items=[discontinued_item])
        
        # Act（操作）
        manager.reactivate_item(0)
        
        # Assert（检验）
        assert manager.items[0]['status'] == 'active'
        assert manager.items[0]['discontinued_date'] is None
        assert manager.items[0]['discontinued_reason'] is None

    @staticmethod
    def test_reactivate_item_当索引无效时_应不执行操作(item_manager_factory, discontinued_item):
        """测试重新启用无效索引时，应不执行任何操作"""
        # Arrange（构造）
        manager = item_manager_factory(items=[discontinued_item])
        original_items = manager.items.copy()
        
        # Act（操作）
        manager.reactivate_item(10)
        
        # Assert（检验）
        assert manager.items == original_items


class TestItemManagerGetItems:
    """ItemManager获取物品列表的测试"""

    @staticmethod
    def test_get_items_应返回所有物品列表(item_manager_factory, multiple_items):
        """测试获取所有物品列表"""
        # Arrange（构造）
        manager = item_manager_factory(items=multiple_items)
        
        # Act（操作）
        result = manager.get_items()
        
        # Assert（检验）
        assert result == manager.items
        assert len(result) == 2


class TestItemManagerCalculateDaysUsed:
    """ItemManager计算使用天数的测试"""

    @staticmethod
    def test_calculate_days_used_当物品为活跃状态时_应计算到当前日期(item_manager_factory, active_item, mocker):
        """测试活跃状态物品应计算到当前日期的使用天数"""
        # Arrange（构造）
        manager = item_manager_factory()
        current_date = QDate(2024, 1, 10)
        
        # Act（操作）
        mocker.patch.object(QDate, 'currentDate', return_value=current_date)
        result = manager.calculate_days_used(active_item)
        
        # Assert（检验）
        assert result == 10

    @staticmethod
    def test_calculate_days_used_当物品为停用状态时_应计算到停用日期(item_manager_factory, discontinued_item):
        """测试停用状态物品应计算到停用日期的使用天数"""
        # Arrange（构造）
        manager = item_manager_factory()
        
        # Act（操作）
        result = manager.calculate_days_used(discontinued_item)
        
        # Assert（检验）
        assert result == 60

    @staticmethod
    def test_calculate_days_used_当计算结果为负数时_应返回最小值1(item_manager_factory, mocker):
        """测试当计算结果为负数时，应返回最小值1"""
        # Arrange（构造）
        manager = item_manager_factory()
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


class TestItemManagerCalculateDailyCost:
    """ItemManager计算日均成本的测试"""

    @staticmethod
    def test_calculate_daily_cost_应正确计算日均成本(item_manager_factory, active_item, mocker):
        """测试计算日均成本"""
        # Arrange（构造）
        manager = item_manager_factory()
        current_date = QDate(2024, 1, 11)
        
        # Act（操作）
        mocker.patch.object(QDate, 'currentDate', return_value=current_date)
        result = manager.calculate_daily_cost(active_item)
        
        # Assert（检验）
        # 使用天数：11天（从2024-01-01到2024-01-11，包含购买当天）
        # 日均成本：1000.0 / 11 ≈ 90.91
        assert abs(result - 90.9090909090909) < 0.01

    @staticmethod
    def test_calculate_daily_cost_当使用天数为0时_应返回原价(item_manager_factory, active_item, mocker):
        """测试当使用天数为0时，应返回原价"""
        # Arrange（构造）
        manager = item_manager_factory()
        
        # Act（操作）
        mocker.patch.object(manager, 'calculate_days_used', return_value=0)
        result = manager.calculate_daily_cost(active_item)
        
        # Assert（检验）
        assert result == 1000.0


class TestItemManagerGetTotalAssets:
    """ItemManager计算总资产的测试"""

    @staticmethod
    def test_get_total_assets_应返回所有物品的总价格(item_manager_factory, multiple_items):
        """测试计算所有物品的总资产"""
        # Arrange（构造）
        manager = item_manager_factory(items=multiple_items)
        
        # Act（操作）
        result = manager.get_total_assets()
        
        # Assert（检验）
        assert result == 3000.0

    @staticmethod
    def test_get_total_assets_当列表为空时_应返回0(item_manager_factory):
        """测试当物品列表为空时，应返回0"""
        # Arrange（构造）
        manager = item_manager_factory(items=[])
        
        # Act（操作）
        result = manager.get_total_assets()
        
        # Assert（检验）
        assert result == 0.0


class TestItemManagerGetAverageDailyCost:
    """ItemManager计算平均日均成本的测试"""

    @staticmethod
    def test_get_average_daily_cost_应返回所有物品的日均成本总和(item_manager_factory, multiple_items, mocker):
        """测试计算所有物品的日均成本总和"""
        # Arrange（构造）
        manager = item_manager_factory(items=multiple_items)
        current_date = QDate(2024, 1, 11)
        
        # Act（操作）
        mocker.patch.object(QDate, 'currentDate', return_value=current_date)
        result = manager.get_average_daily_cost()
        
        # Assert（检验）
        # 使用天数：11天（从2024-01-01到2024-01-11，包含购买当天）
        # 手机日均成本：1000.0 / 11 ≈ 90.91
        # 平板日均成本：2000.0 / 11 ≈ 181.82
        # 总计：90.91 + 181.82 ≈ 272.73
        assert abs(result - 272.72727272727275) < 0.01

    @staticmethod
    def test_get_average_daily_cost_当列表为空时_应返回0(item_manager_factory):
        """测试当物品列表为空时，应返回0"""
        # Arrange（构造）
        manager = item_manager_factory(items=[])
        
        # Act（操作）
        result = manager.get_average_daily_cost()
        
        # Assert（检验）
        assert result == 0.0
