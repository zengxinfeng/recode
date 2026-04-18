"""
基础管理视图模块。

提供物品和衣物管理视图的基类，封装通用的 UI 组件和业务逻辑。
"""

from typing import Any, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.views.widgets.discontinue_dialog import DiscontinueDialog

TABLE_ROW_HEIGHT = 50
STATUS_MESSAGE_DURATION = 3000
STATUS_ACTIVE = 'active'
STATUS_DISCONTINUED = 'discontinued'


class BaseManagementView(QWidget):
    """
    管理视图基类。

    提供统计卡片、搜索、表格、CRUD 操作等通用功能。
    子类需实现抽象方法以定义特定行为。
    """

    def __init__(self, manager: Any, parent: Optional[QWidget] = None) -> None:
        """
        初始化基础管理视图。

        Args:
            manager: 数据管理器实例。
            parent: 父窗口部件。
        """
        super().__init__(parent)
        self.manager = manager
        self.status_bar: Optional[QStatusBar] = None
        self.search_input: Optional[QLineEdit] = None
        self.table: Optional[QTableWidget] = None
        self._stat_labels: dict[str, QLabel] = {}
        self._setup_ui()

    def set_status_bar(self, status_bar: QStatusBar) -> None:
        """
        设置状态栏引用。

        Args:
            status_bar: 状态栏实例。
        """
        self.status_bar = status_bar

    def refresh_table(self) -> None:
        """刷新表格显示全部数据。"""
        items = self.manager.get_items()
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self._populate_table_row(row, item, row)

    def show_view(self) -> None:
        """显示视图并刷新数据。"""
        self.show()
        self._apply_filters()
        self._update_stats()

    def hide_view(self) -> None:
        """隐藏视图。"""
        self.hide()

    def _setup_ui(self) -> None:
        """初始化 UI 布局。"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._create_stats_group())
        layout.addLayout(self._create_input_search_layout())
        layout.addWidget(self._create_table_group(), 1)

    def _get_table_headers(self) -> list[str]:
        """获取表格列标题。子类必须实现。"""
        raise NotImplementedError

    def _configure_table_columns(self, header: Any) -> None:
        """配置表格列属性。子类必须实现。"""
        raise NotImplementedError

    def _get_stat_cards_config(
        self,
    ) -> list[Tuple[str, str, str, str]]:
        """获取统计卡片配置。子类必须实现。"""
        raise NotImplementedError

    def _create_input_group(self) -> QGroupBox:
        """创建输入区域。子类必须实现。"""
        raise NotImplementedError

    def _populate_table_row(
        self, row: int, item: dict[str, Any], original_index: int
    ) -> None:
        """填充表格行数据。子类必须实现。"""
        raise NotImplementedError

    def _update_stats(self) -> None:
        """更新统计信息。子类必须实现。"""
        raise NotImplementedError

    def _add_item(self) -> None:
        """添加项目。子类必须实现。"""
        raise NotImplementedError

    def _edit_item(self, row: int) -> None:
        """编辑项目。子类必须实现。"""
        raise NotImplementedError

    def _get_item_type_name(self) -> str:
        """获取项目类型名称。子类必须实现。"""
        raise NotImplementedError

    def _get_search_placeholder(self) -> str:
        """获取搜索框占位文本。"""
        return '输入名称进行搜索...'

    def _get_table_group_title(self) -> str:
        """获取表格分组标题。"""
        return '📋 列表'

    def _create_stats_group(self) -> QGroupBox:
        """创建统计信息分组。"""
        stats_group = QGroupBox('📊 统计信息')
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(18, 18, 18, 18)

        for card_name, title, value_name, initial_value in (
            self._get_stat_cards_config()
        ):
            card = self._create_stat_card(
                card_name, title, value_name, initial_value
            )
            self._stat_labels[value_name] = card.findChild(QLabel, value_name)
            stats_layout.addWidget(card, 1)

        stats_group.setLayout(stats_layout)
        return stats_group

    def _get_stat_label(self, value_name: str) -> Optional[QLabel]:
        """
        获取统计标签。

        Args:
            value_name: 标签对象名称。

        Returns:
            标签实例，若不存在则返回 None。
        """
        return self._stat_labels.get(value_name)

    def _create_stat_card(
        self,
        card_name: str,
        title: str,
        value_name: str,
        initial_value: str,
    ) -> QWidget:
        """
        创建单个统计卡片。

        Args:
            card_name: 卡片对象名称。
            title: 卡片标题。
            value_name: 数值标签对象名称。
            initial_value: 初始显示值。

        Returns:
            配置好的卡片部件。
        """
        card = QWidget()
        card.setObjectName(card_name)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        icon_map = {
            "totalAssetsCard": "💰",
            "dailyCostCard": "📊",
            "itemCountCard": "📦",
            "clothingTotalAssetsCard": "👗",
            "clothingCountCard": "👕",
        }
        icon_text = icon_map.get(card_name, "📈")
        icon_label = QLabel(icon_text)
        icon_label.setObjectName("statsCardIcon")
        icon_label.setStyleSheet("font-size: 28px;")
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("statsCardTitle")

        value_label = QLabel(initial_value)
        value_label.setObjectName(value_name)

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        layout.addLayout(text_layout)
        layout.addStretch(1)

        return card

    def _create_input_search_layout(self) -> QHBoxLayout:
        """创建输入和搜索区域的水平布局。"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.addWidget(self._create_input_group(), 3)
        layout.addWidget(self._create_search_group(), 1)
        return layout

    def _create_search_group(self) -> QGroupBox:
        """创建搜索区域分组。"""
        search_group = QGroupBox('🔍 搜索')
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        search_layout.setContentsMargins(20, 18, 20, 18)

        search_label = QLabel('🔍')
        search_label.setStyleSheet("font-size: 16px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self._get_search_placeholder())
        self.search_input.textChanged.connect(self._on_search_text_changed)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_group.setLayout(search_layout)
        return search_group

    def _on_search_text_changed(self) -> None:
        """搜索文本变化时触发过滤。"""
        self._apply_filters()

    def _apply_filters(self) -> None:
        """应用搜索过滤。"""
        search_text = self.search_input.text().lower()
        items = self.manager.get_items()
        filtered = [
            item for item in items
            if search_text in item.get('name', '').lower()
        ]
        self._populate_filtered_table(filtered, items)

    def _populate_filtered_table(
        self,
        filtered_items: list[dict[str, Any]],
        all_items: list[dict[str, Any]],
    ) -> None:
        """
        填充过滤后的表格数据。

        Args:
            filtered_items: 过滤后的项目列表。
            all_items: 完整项目列表。
        """
        self.table.setRowCount(len(filtered_items))
        for row, item in enumerate(filtered_items):
            original_index = all_items.index(item)
            self._populate_table_row(row, item, original_index)

    def _create_table_group(self) -> QGroupBox:
        """创建表格分组。"""
        table_group = QGroupBox(self._get_table_group_title())
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(12, 12, 12, 12)

        self._create_table()
        self._setup_table()

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        return table_group

    def _create_table(self) -> None:
        """创建表格部件。"""
        self.table = QTableWidget()
        self.table.setColumnCount(len(self._get_table_headers()))
        self.table.setHorizontalHeaderLabels(self._get_table_headers())
        self._configure_table_columns(self.table.horizontalHeader())

    def _setup_table(self) -> None:
        """配置表格属性。"""
        self.table.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.cellClicked.connect(self._handle_cell_click)

    def _handle_cell_click(self, row: int, column: int) -> None:
        """
        处理单元格点击事件。

        Args:
            row: 行索引。
            column: 列索引。
        """

    def _create_action_buttons(
        self, row: int, item: dict[str, Any]
    ) -> QWidget:
        """
        创建操作按钮部件。

        Args:
            row: 表格行索引。
            item: 项目数据字典。

        Returns:
            包含操作按钮的部件。
        """
        is_discontinued = item.get('status') == STATUS_DISCONTINUED

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(6)

        edit_btn = QPushButton('✏️ 修改')
        edit_btn.setObjectName("editButton")
        edit_btn.clicked.connect(lambda _, r=row: self._edit_item(r))
        button_layout.addWidget(edit_btn)

        if is_discontinued:
            reactivate_btn = QPushButton('🔄 启用')
            reactivate_btn.setObjectName("reactivateButton")
            reactivate_btn.clicked.connect(
                lambda _, r=row: self._reactivate_item(r)
            )
            button_layout.addWidget(reactivate_btn)
        else:
            discontinue_btn = QPushButton('⏹️ 停用')
            discontinue_btn.setObjectName("discontinueButton")
            discontinue_btn.clicked.connect(
                lambda _, r=row: self._discontinue_item(r)
            )
            button_layout.addWidget(discontinue_btn)

        delete_btn = QPushButton('🗑️ 删除')
        delete_btn.setObjectName("deleteButton")
        delete_btn.clicked.connect(lambda _, r=row: self._delete_item(r))
        button_layout.addWidget(delete_btn)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        return button_widget

    def _create_styled_item(
        self,
        text: str,
        is_discontinued: bool,
        alignment: Optional[int] = None,
        user_role_data: Optional[Any] = None,
        tooltip: Optional[str] = None,
    ) -> QTableWidgetItem:
        """
        创建带样式的表格项。

        Args:
            text: 显示文本。
            is_discontinued: 是否已停用。
            alignment: 文本对齐方式。
            user_role_data: 用户角色数据。
            tooltip: 工具提示文本。

        Returns:
            配置好的表格项。
        """
        table_item = QTableWidgetItem(text)
        if alignment is not None:
            table_item.setTextAlignment(alignment)
        if user_role_data is not None:
            table_item.setData(Qt.ItemDataRole.UserRole, user_role_data)
        if tooltip:
            table_item.setToolTip(tooltip)
        if is_discontinued:
            table_item.setForeground(Qt.GlobalColor.gray)
        return table_item

    def _validate_price(
        self, price_text: str
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        验证价格输入。

        Args:
            price_text: 价格文本。

        Returns:
            元组：(价格, 错误信息)，验证成功时错误信息为 None。
        """
        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError("价格必须大于0")
            return price, None
        except ValueError:
            return None, '请输入有效的购买价格'

    def _delete_item(self, row: int) -> None:
        """
        删除项目。

        Args:
            row: 项目索引。
        """
        item_name = self.manager.items[row].get('name', '未命名')
        type_name = self._get_item_type_name()
        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除{type_name} "{item_name}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.remove_item(row)
            self._refresh_after_change()
            self._show_status_message(f'{type_name}删除成功')

    def _discontinue_item(self, row: int) -> None:
        """
        停用项目。

        Args:
            row: 项目索引。
        """
        item = self.manager.items[row]
        type_name = self._get_item_type_name()
        dialog = DiscontinueDialog(self, item.get('name', '未命名'))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            discontinue_date = dialog.get_discontinue_date()
            discontinue_reason = dialog.get_discontinue_reason()
            self.manager.discontinue_item(
                row, discontinue_date, discontinue_reason
            )
            self._refresh_after_change()
            self._show_status_message(
                f'{type_name}已停用，原因：{discontinue_reason}'
            )

    def _reactivate_item(self, row: int) -> None:
        """
        重新启用项目。

        Args:
            row: 项目索引。
        """
        item = self.manager.items[row]
        type_name = self._get_item_type_name()
        reply = QMessageBox.question(
            self,
            '确认重新启用',
            f'确定要重新启用{type_name} "{item.get("name", "未命名")}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.reactivate_item(row)
            self._refresh_after_change()
            self._show_status_message(f'{type_name}已重新启用')

    def _refresh_after_change(self) -> None:
        """数据变更后刷新界面。"""
        self._apply_filters()
        self._update_stats()

    def _show_status_message(self, message: str) -> None:
        """
        显示状态栏消息。

        Args:
            message: 消息内容。
        """
        if self.status_bar:
            self.status_bar.showMessage(message, STATUS_MESSAGE_DURATION)
