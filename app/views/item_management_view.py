"""
物品管理视图模块。

提供物品记录的添加、编辑、删除、搜索和统计功能。
"""

from typing import Any, Callable, Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.views.base_management_view import (
    STATUS_DISCONTINUED,
    BaseManagementView,
)
from app.views.widgets.date_input import DateInput


class ItemManagementView(BaseManagementView):
    """
    物品管理视图。

    继承自 BaseManagementView，实现物品特有的表格列配置、
    统计卡片、输入表单和业务逻辑。
    """

    def __init__(
        self,
        manager: Any,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        初始化物品管理视图。

        Args:
            manager: 物品数据管理器实例。
            parent: 父窗口部件。
        """
        self._on_stats_updated: Optional[Callable[[int], None]] = None
        super().__init__(manager, parent)

    def _get_table_headers(self) -> list[str]:
        """获取表格列标题。"""
        return [
            '物品名称', '购买价格', '购买日期', '状态',
            '已使用天数', '日均使用价格', '操作'
        ]

    def _configure_table_columns(self, header: QHeaderView) -> None:
        """
        配置表格列属性。

        Args:
            header: 表格头部实例。
        """
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.resizeSection(6, 300)

    def _get_stat_cards_config(
        self,
    ) -> list[tuple[str, str, str, str]]:
        """获取统计卡片配置。"""
        return [
            ("totalAssetsCard", "总资产", "totalAssetsValue", "¥0.00"),
            ("dailyCostCard", "日均总成本", "dailyCostValue", "¥0.00"),
            ("itemCountCard", "物品数量", "itemCountValue", "0"),
        ]

    def _get_search_placeholder(self) -> str:
        """获取搜索框占位文本。"""
        return '输入物品名称进行搜索...'

    def _get_table_group_title(self) -> str:
        """获取表格分组标题。"""
        return '📋 物品列表'

    def _get_item_type_name(self) -> str:
        """获取项目类型名称。"""
        return '物品'

    def _create_input_group(self) -> QGroupBox:
        """创建输入区域。"""
        input_group = QGroupBox('添加物品')
        input_layout = QGridLayout()
        input_layout.setSpacing(12)
        input_layout.setContentsMargins(20, 18, 20, 18)

        name_label = QLabel('物品名称:')
        name_label.setObjectName("inputLabel")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入物品名称')
        input_layout.addWidget(name_label, 0, 0, 1, 1)
        input_layout.addWidget(self.name_input, 0, 1, 1, 2)

        price_label = QLabel('购买价格:')
        price_label.setObjectName("inputLabel")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText('请输入购买价格')
        input_layout.addWidget(price_label, 0, 3, 1, 1)
        input_layout.addWidget(self.price_input, 0, 4, 1, 1)

        date_label = QLabel('购买日期:')
        date_label.setObjectName("inputLabel")
        self.date_input = DateInput()
        input_layout.addWidget(date_label, 0, 5, 1, 1)
        input_layout.addWidget(self.date_input, 0, 6, 1, 1)

        self.add_button = QPushButton('➕ 添加物品')
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self._add_item)
        input_layout.addWidget(self.add_button, 0, 7, 1, 1)

        input_group.setLayout(input_layout)
        return input_group

    def _populate_table_row(
        self,
        row: int,
        item: dict[str, Any],
        original_index: int,
    ) -> None:
        """
        填充表格行数据。

        Args:
            row: 表格行索引。
            item: 物品数据字典。
            original_index: 原始数据索引。
        """
        is_discontinued = item.get('status') == STATUS_DISCONTINUED

        self.table.setItem(row, 0, self._create_styled_item(
            item['name'], is_discontinued, tooltip=f"物品：{item['name']}"
        ))

        self.table.setItem(row, 1, self._create_styled_item(
            f"¥{item['price']:.2f}", is_discontinued,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            user_role_data=item['price'],
        ))

        self.table.setItem(row, 2, self._create_styled_item(
            item['purchase_date'], is_discontinued
        ))

        status_text = '已停用' if is_discontinued else '使用中'
        self.table.setItem(row, 3, self._create_styled_item(
            status_text, is_discontinued,
            alignment=Qt.AlignmentFlag.AlignCenter,
        ))

        days_used = self.manager.calculate_days_used(item)
        self.table.setItem(row, 4, self._create_styled_item(
            str(days_used), is_discontinued,
            alignment=Qt.AlignmentFlag.AlignCenter,
            user_role_data=days_used,
        ))

        daily_cost = self.manager.calculate_daily_cost(item)
        self.table.setItem(row, 5, self._create_styled_item(
            f"¥{daily_cost:.2f}", is_discontinued,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            user_role_data=daily_cost,
        ))

        button_widget = self._create_action_buttons(original_index, item)
        self.table.setCellWidget(row, 6, button_widget)

    def _update_stats(self) -> None:
        """更新统计信息显示。"""
        total_assets = self.manager.get_total_assets()
        average_daily_cost = self.manager.get_average_daily_cost()
        item_count = len(self.manager.get_items())

        self._get_stat_label("totalAssetsValue").setText(
            f'¥{total_assets:.2f}'
        )
        self._get_stat_label("dailyCostValue").setText(
            f'¥{average_daily_cost:.2f}'
        )
        self._get_stat_label("itemCountValue").setText(f'{item_count}')

        if self._on_stats_updated:
            self._on_stats_updated(item_count)

    def _add_item(self) -> None:
        """添加物品。"""
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()

        if not name:
            QMessageBox.warning(self, '警告', '请输入物品名称')
            return

        price, error = self._validate_price(price_text)
        if error:
            QMessageBox.warning(self, '警告', error)
            return

        self.manager.add_item(name, price, self.date_input.date())
        self._refresh_after_change()
        self._show_status_message('物品添加成功')

        self.name_input.clear()
        self.price_input.clear()
        self.date_input.setDate(QDate.currentDate())

    def _edit_item(self, row: int) -> None:
        """
        编辑物品。

        Args:
            row: 物品索引。
        """
        item = self.manager.items[row]

        dialog = QDialog(self)
        dialog.setWindowTitle('修改物品')
        dialog.setGeometry(200, 200, 400, 200)

        layout = QFormLayout(dialog)

        name_edit = QLineEdit(item['name'])
        price_edit = QLineEdit(str(item['price']))
        date_edit = DateInput()
        date_edit.setDate(
            QDate.fromString(item['purchase_date'], 'yyyy-MM-dd')
        )

        layout.addRow('物品名称:', name_edit)
        layout.addRow('购买价格:', price_edit)
        layout.addRow('购买日期:', date_edit)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addRow(button_box)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_edit.text().strip()
            price_text = price_edit.text().strip()

            if not name:
                QMessageBox.warning(self, '警告', '请输入物品名称')
                return

            price, error = self._validate_price(price_text)
            if error:
                QMessageBox.warning(self, '警告', error)
                return

            self.manager.update_item(row, name, price, date_edit.date())
            self._refresh_after_change()
            self._show_status_message('物品修改成功')
