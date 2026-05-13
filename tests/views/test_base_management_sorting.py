"""
BaseManagementView 排序功能测试。
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget

from app.views.base_management_view import BaseManagementView


class MockManager:
    """模拟数据管理器。"""

    def __init__(self) -> None:
        self.items = []

    def get_items(self) -> list[dict]:
        return self.items


class TestableManagementView(BaseManagementView):
    """可测试的管理视图。"""

    def _get_table_headers(self) -> list[str]:
        return ['名称', '价格', '操作']

    def _configure_table_columns(self, header) -> None:
        pass

    def _get_stat_cards_config(self):
        return []

    def _create_input_group(self):
        from PySide6.QtWidgets import QGroupBox
        return QGroupBox()

    def _populate_table_row(self, row: int, item: dict, original_index: int) -> None:
        from PySide6.QtWidgets import QTableWidgetItem
        self.table.setItem(row, 0, QTableWidgetItem(item['name']))
        price_item = QTableWidgetItem(str(item['price']))
        price_item.setData(Qt.ItemDataRole.UserRole, item['price'])
        self.table.setItem(row, 1, price_item)

    def _update_stats(self) -> None:
        pass

    def _add_item(self) -> None:
        pass

    def _edit_item(self, row: int) -> None:
        pass

    def _get_item_type_name(self) -> str:
        return '测试项目'

    def _get_sortable_columns(self) -> list[int]:
        return [1]


class TestSorting:
    """排序功能测试。"""

    def test_initial_sort_state(self, qtbot) -> None:
        """测试初始排序状态。"""
        manager = MockManager()
        view = TestableManagementView(manager)
        qtbot.addWidget(view)

        assert view._sort_column == -1
        assert view._sort_order == 0

    def test_sortable_columns(self, qtbot) -> None:
        """测试可排序列配置。"""
        manager = MockManager()
        view = TestableManagementView(manager)
        qtbot.addWidget(view)

        assert view._get_sortable_columns() == [1]

    def test_header_click_first_time_ascending(self, qtbot) -> None:
        """测试第一次点击表头触发升序排序。"""
        manager = MockManager()
        manager.items = [
            {'name': '物品A', 'price': 100.0},
            {'name': '物品B', 'price': 50.0},
            {'name': '物品C', 'price': 200.0},
        ]
        view = TestableManagementView(manager)
        qtbot.addWidget(view)
        view.refresh_table()

        view._on_header_clicked(1)

        assert view._sort_column == 1
        assert view._sort_order == 1

        header_item = view.table.horizontalHeaderItem(1)
        assert '↑' in header_item.text()

    def test_header_click_second_time_descending(self, qtbot) -> None:
        """测试第二次点击表头触发降序排序。"""
        manager = MockManager()
        manager.items = [
            {'name': '物品A', 'price': 100.0},
            {'name': '物品B', 'price': 50.0},
        ]
        view = TestableManagementView(manager)
        qtbot.addWidget(view)
        view.refresh_table()

        view._on_header_clicked(1)
        view._on_header_clicked(1)

        assert view._sort_column == 1
        assert view._sort_order == 2

        header_item = view.table.horizontalHeaderItem(1)
        assert '↓' in header_item.text()

    def test_header_click_third_time_no_sort(self, qtbot) -> None:
        """测试第三次点击表头取消排序。"""
        manager = MockManager()
        manager.items = [
            {'name': '物品A', 'price': 100.0},
            {'name': '物品B', 'price': 50.0},
        ]
        view = TestableManagementView(manager)
        qtbot.addWidget(view)
        view.refresh_table()

        view._on_header_clicked(1)
        view._on_header_clicked(1)
        view._on_header_clicked(1)

        assert view._sort_column == -1
        assert view._sort_order == 0

        header_item = view.table.horizontalHeaderItem(1)
        assert '↑' not in header_item.text()
        assert '↓' not in header_item.text()

    def test_click_different_column_resets_sort(self, qtbot) -> None:
        """测试点击不同列重置排序状态。"""
        manager = MockManager()
        manager.items = [
            {'name': '物品A', 'price': 100.0},
        ]
        view = TestableManagementView(manager)
        qtbot.addWidget(view)
        view.refresh_table()

        view._on_header_clicked(1)
        view._on_header_clicked(0)

        assert view._sort_column == 0
        assert view._sort_order == 1

    def test_click_non_sortable_column_ignored(self, qtbot) -> None:
        """测试点击不可排序列被忽略。"""
        manager = MockManager()
        manager.items = [
            {'name': '物品A', 'price': 100.0},
        ]
        view = TestableManagementView(manager)
        qtbot.addWidget(view)
        view.refresh_table()

        view._on_header_clicked(2)

        assert view._sort_column == -1
        assert view._sort_order == 0

    def test_sort_order_correctness(self, qtbot) -> None:
        """测试排序顺序正确性。"""
        manager = MockManager()
        manager.items = [
            {'name': '物品A', 'price': 100.0},
            {'name': '物品B', 'price': 50.0},
            {'name': '物品C', 'price': 200.0},
        ]
        view = TestableManagementView(manager)
        qtbot.addWidget(view)
        view.refresh_table()

        view._on_header_clicked(1)

        item0 = view.table.item(0, 1)
        item1 = view.table.item(1, 1)
        item2 = view.table.item(2, 1)

        assert item0.data(Qt.ItemDataRole.UserRole) <= item1.data(Qt.ItemDataRole.UserRole)
        assert item1.data(Qt.ItemDataRole.UserRole) <= item2.data(Qt.ItemDataRole.UserRole)

        view._on_header_clicked(1)

        item0 = view.table.item(0, 1)
        item1 = view.table.item(1, 1)
        item2 = view.table.item(2, 1)

        assert item0.data(Qt.ItemDataRole.UserRole) >= item1.data(Qt.ItemDataRole.UserRole)
        assert item1.data(Qt.ItemDataRole.UserRole) >= item2.data(Qt.ItemDataRole.UserRole)
