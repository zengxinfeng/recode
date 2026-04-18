"""
衣物管理视图模块。

提供衣物记录的添加、编辑、删除、搜索、统计和类型筛选功能。
"""

from typing import Any, Optional

from PySide6.QtCore import QDate, QPoint, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
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
from app.views.widgets.filter_header import FilterHeader
from app.views.widgets.filter_popup import FilterPopup


class ClothingManagementView(BaseManagementView):
    """
    衣物管理视图。

    继承自 BaseManagementView，实现衣物特有的表格列配置、
    类型筛选、输入表单和业务逻辑。
    """

    def __init__(
        self,
        manager: Any,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        初始化衣物管理视图。

        Args:
            manager: 衣物数据管理器实例。
            parent: 父窗口部件。
        """
        self.clothing_type_filter_selected: Optional[list[str]] = None
        self.clothing_filter_header: Optional[FilterHeader] = None
        super().__init__(manager, parent)
        
    def show_view(self) -> None:
        """显示视图并刷新数据。"""
        self.show()
        self._refresh_clothing_type_options()
        self._apply_filters()
        self._update_stats()


    def _get_table_headers(self) -> list[str]:
        """获取表格列标题。"""
        return [
            '衣物名称', '衣物类型', '购买价格', '购买日期',
            '已使用天数', '状态', '操作'
        ]

    def _configure_table_columns(self, header: QHeaderView) -> None:
        """
        配置表格列属性。

        Args:
            header: 表格头部实例。
        """
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 120)
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
            (
                "clothingTotalAssetsCard", "总资产",
                "clothingTotalAssetsValue", "¥0.00"
            ),
            (
                "clothingCountCard", "衣物数量",
                "clothingCountValue", "0"
            ),
        ]

    def _get_search_placeholder(self) -> str:
        """获取搜索框占位文本。"""
        return '输入衣物名称进行搜索...'

    def _get_table_group_title(self) -> str:
        """获取表格分组标题。"""
        return '📋 衣物列表'

    def _get_item_type_name(self) -> str:
        """获取项目类型名称。"""
        return '衣物'

    def _create_input_group(self) -> QGroupBox:
        """创建输入区域。"""
        input_group = QGroupBox('👕 添加衣物')
        input_group.setObjectName("clothingInputGroup")
        input_layout = QHBoxLayout()
        input_layout.setSpacing(16)
        input_layout.setContentsMargins(24, 16, 24, 16)

        name_label = QLabel('名称:')
        name_label.setObjectName("inputLabel")
        self.clothing_name_input = QLineEdit()
        self.clothing_name_input.setPlaceholderText('衣物名称')
        self.clothing_name_input.setMinimumWidth(120)
        input_layout.addWidget(name_label)
        input_layout.addWidget(self.clothing_name_input)

        type_label = QLabel('类型:')
        type_label.setObjectName("inputLabel")
        self.clothing_type_input = QComboBox()
        self.clothing_type_input.setEditable(True)
        self.clothing_type_input.lineEdit().setPlaceholderText('选择或输入类型')
        self.clothing_type_input.setMinimumWidth(120)
        input_layout.addWidget(type_label)
        input_layout.addWidget(self.clothing_type_input)

        price_label = QLabel('价格:')
        price_label.setObjectName("inputLabel")
        self.clothing_price_input = QLineEdit()
        self.clothing_price_input.setPlaceholderText('购买价格')
        self.clothing_price_input.setMinimumWidth(80)
        input_layout.addWidget(price_label)
        input_layout.addWidget(self.clothing_price_input)

        date_label = QLabel('日期:')
        date_label.setObjectName("inputLabel")
        self.clothing_date_input = DateInput()
        input_layout.addWidget(date_label)
        input_layout.addWidget(self.clothing_date_input)

        input_layout.addSpacing(8)

        self.add_clothing_button = QPushButton('➕ 添加')
        self.add_clothing_button.setObjectName("addButton")
        self.add_clothing_button.clicked.connect(self._add_item)
        input_layout.addWidget(self.add_clothing_button)

        input_group.setLayout(input_layout)
        return input_group

    def _create_search_group(self) -> QGroupBox:
        """创建搜索区域分组。"""
        search_group = super()._create_search_group()
        search_group.setObjectName("clothingSearchGroup")
        return search_group

    def _create_table(self) -> None:
        """创建表格部件并配置筛选头部。"""
        super()._create_table()
        self.table.setObjectName("clothingTable")
        self.clothing_filter_header = FilterHeader(self.table)
        self.table.setHorizontalHeader(self.clothing_filter_header)
        self.clothing_filter_header.filter_clicked.connect(
            self._show_type_filter
        )
        self._configure_table_columns(self.clothing_filter_header)

    def _create_table_group(self) -> QGroupBox:
        """创建表格分组。"""
        table_group = super()._create_table_group()
        table_group.setObjectName("clothingTableGroup")
        return table_group

    def _apply_filters(self) -> None:
        """应用搜索和类型筛选。"""
        search_text = self.search_input.text().lower()
        selected_types = self.clothing_type_filter_selected

        items = self.manager.get_items()

        filtered_items = [
            item for item in items
            if (not search_text or search_text in item.get('name', '').lower())
            and (selected_types is None
                 or item.get('clothing_type') in selected_types)
        ]

        self._populate_filtered_table(filtered_items, items)

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
            item: 衣物数据字典。
            original_index: 原始数据索引。
        """
        is_discontinued = item.get('status') == STATUS_DISCONTINUED

        self.table.setItem(row, 0, self._create_styled_item(
            item.get('name', ''), is_discontinued,
            tooltip=f"衣物名称：{item.get('name', '')}",
        ))

        self.table.setItem(row, 1, self._create_styled_item(
            item.get('clothing_type', ''), is_discontinued,
        ))

        self.table.setItem(row, 2, self._create_styled_item(
            f"¥{item['price']:.2f}", is_discontinued,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            user_role_data=item['price'],
        ))

        self.table.setItem(row, 3, self._create_styled_item(
            item['purchase_date'], is_discontinued,
        ))

        days_used = self.manager.calculate_days_used(item)
        self.table.setItem(row, 4, self._create_styled_item(
            str(days_used), is_discontinued,
            alignment=Qt.AlignmentFlag.AlignCenter,
            user_role_data=days_used,
        ))

        status_text = '已停用' if is_discontinued else '使用中'
        self.table.setItem(row, 5, self._create_styled_item(
            status_text, is_discontinued,
            alignment=Qt.AlignmentFlag.AlignCenter,
        ))

        button_widget = self._create_action_buttons(original_index, item)
        self.table.setCellWidget(row, 6, button_widget)

    def _update_stats(self) -> None:
        """更新统计信息显示。"""
        total_assets = self.manager.get_total_assets()
        item_count = len(self.manager.get_items())

        self._get_stat_label("clothingTotalAssetsValue").setText(
            f'¥{total_assets:.2f}'
        )
        self._get_stat_label("clothingCountValue").setText(f'{item_count}')

    def _add_item(self) -> None:
        """添加衣物。"""
        name = self.clothing_name_input.text().strip()
        clothing_type = self.clothing_type_input.text().strip()
        price_text = self.clothing_price_input.text().strip()

        if not name:
            QMessageBox.warning(self, '警告', '请输入衣物名称')
            return

        if not clothing_type:
            QMessageBox.warning(self, '警告', '请输入衣物类型')
            return

        price, error = self._validate_price(price_text)
        if error:
            QMessageBox.warning(self, '警告', error)
            return

        self.manager.add_item(
            name, clothing_type, price, self.clothing_date_input.date()
        )

        self._refresh_clothing_type_options()
        self._refresh_after_change()
        self._show_status_message('衣物添加成功')

        self.clothing_name_input.clear()
        self.clothing_type_input.setCurrentText('')
        self.clothing_price_input.clear()
        self.clothing_date_input.setDate(QDate.currentDate())

    def _edit_item(self, row: int) -> None:
        """
        编辑衣物。

        Args:
            row: 衣物索引。
        """
        item = self.manager.items[row]

        dialog = QDialog(self)
        dialog.setWindowTitle('修改衣物')
        dialog.setGeometry(200, 200, 400, 250)

        layout = QFormLayout(dialog)

        name_edit = QLineEdit(item.get('name', ''))
        type_edit = QLineEdit(item['clothing_type'])
        price_edit = QLineEdit(str(item['price']))
        date_edit = DateInput()
        date_edit.setDate(
            QDate.fromString(item['purchase_date'], 'yyyy-MM-dd')
        )

        layout.addRow('衣物名称:', name_edit)
        layout.addRow('衣物类型:', type_edit)
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
            clothing_type = type_edit.text().strip()
            price_text = price_edit.text().strip()

            if not name:
                QMessageBox.warning(self, '警告', '请输入衣物名称')
                return

            if not clothing_type:
                QMessageBox.warning(self, '警告', '请输入衣物类型')
                return

            price, error = self._validate_price(price_text)
            if error:
                QMessageBox.warning(self, '警告', error)
                return

            self.manager.update_item(
                row, name, clothing_type, price, date_edit.date()
            )
            self._refresh_after_change()
            self._show_status_message('衣物修改成功')

    def _refresh_clothing_type_options(self) -> None:
        """刷新衣物类型下拉选项列表。"""
        all_types = self.manager.get_all_clothing_types()
        current_text = self.clothing_type_input.currentText()

        self.clothing_type_input.blockSignals(True)
        self.clothing_type_input.clear()
        self.clothing_type_input.addItems(all_types)
        self.clothing_type_input.setCurrentText(current_text)
        self.clothing_type_input.blockSignals(False)

    def _show_type_filter(self, column: int) -> None:
        """
        显示类型筛选弹窗。

        Args:
            column: 点击的列索引。
        """
        all_types = self.manager.get_all_clothing_types()
        if not all_types:
            return

        if self.clothing_type_filter_selected is None:
            selected = all_types
        else:
            selected = self.clothing_type_filter_selected

        popup = FilterPopup(all_types, selected, self)

        header = self.clothing_filter_header
        x = header.sectionViewportPosition(column)
        height = header.height()

        global_pos = self.table.mapToGlobal(QPoint(x, height))
        popup.move(global_pos.x(), global_pos.y() + 2)
        popup.filter_applied.connect(self._on_type_filter_applied)
        popup.show()

    def _on_type_filter_applied(self, selected: list[str]) -> None:
        """
        处理类型筛选结果。

        Args:
            selected: 选中的类型列表。
        """
        all_types = self.manager.get_all_clothing_types()

        if set(selected) == set(all_types):
            self.clothing_type_filter_selected = None
            has_filter = False
        else:
            self.clothing_type_filter_selected = selected
            has_filter = True

        self.clothing_filter_header.set_filter_active(has_filter)
        self._apply_filters()
