import ctypes
import sys
from typing import Any, Optional

from PySide6.QtCore import QDate, QPoint, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialog,
    QDialogButtonBox,
)

from app.models.clothing_manager import ClothingManager
from app.models.item_manager import ItemManager
from app.utils.path_utils import get_dark_style_path, get_main_style_path
from app.views.widgets.date_input import DateInput
from app.views.widgets.discontinue_dialog import DiscontinueDialog
from app.views.widgets.filter_header import FilterHeader
from app.views.widgets.filter_popup import FilterPopup


WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1000
WINDOW_DEFAULT_HEIGHT = 750
NAV_WIDTH = 220
TABLE_ROW_HEIGHT = 50
STATUS_MESSAGE_DURATION = 3000


class MainWindow(QMainWindow):
    """
    主应用程序窗口类，继承自 QMainWindow。

    负责管理物品记录的用户界面，包括添加、编辑、删除和搜索物品功能。
    """

    def __init__(self) -> None:
        super().__init__()
        self.current_theme: str = 'dark'
        self.item_manager: ItemManager = ItemManager()
        self.clothing_manager: ClothingManager = ClothingManager()
        self.item_management_widget: QWidget | None = None
        self.clothing_management_widget: QWidget | None = None
        self.sort_states: dict[int, int] = {}
        self.clothing_sort_states: dict[int, int] = {}
        self.clothing_type_filter_selected: list[str] | None = None

        self.load_styles()
        self.init_ui()
        self.refresh_table()

    def showEvent(self, event: Any) -> None:
        """
        窗口显示事件，确保标题栏颜色正确设置。

        Args:
            event: Qt 显示事件对象。
        """
        super().showEvent(event)
        self.update_title_bar_color()

    def load_styles(self) -> None:
        """
        加载和应用 QSS 样式。

        根据当前主题加载对应的样式文件并应用到窗口。
        """
        style_path = (
            get_main_style_path()
            if self.current_theme == 'light'
            else get_dark_style_path()
        )

        if style_path.exists():
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    style = f.read()
                self.setStyleSheet(style)
            except OSError as e:
                print(f"加载样式文件失败: {e}")

        self.update_title_bar_color()

    def update_title_bar_color(self) -> None:
        """
        更新窗口标题栏颜色（仅 Windows 系统）。

        使用 Windows DWM API 设置标题栏为暗色或亮色模式。
        """
        if sys.platform != 'win32':
            return

        try:
            hwnd = int(self.winId())
            dwmwa_use_immersive_dark_mode = 20
            value = 1 if self.current_theme == 'dark' else 0

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                dwmwa_use_immersive_dark_mode,
                ctypes.byref(ctypes.c_int(value)),
                ctypes.sizeof(ctypes.c_int),
            )
        except (AttributeError, OSError) as e:
            print(f"设置标题栏颜色失败: {e}")

    def toggle_theme(self) -> None:
        """
        切换主题。

        在明亮和暗黑主题之间切换，并更新状态栏提示。
        """
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.load_styles()
        theme_name = "暗黑" if self.current_theme == "dark" else "明亮"
        self.statusBar.showMessage(f'已切换到{theme_name}主题', STATUS_MESSAGE_DURATION)

    def init_ui(self) -> None:
        """
        初始化用户界面。

        创建并布局所有界面组件，包括导航栏、内容区域和状态栏。
        """
        self.setWindowTitle('记录管理器')
        self.setGeometry(100, 100, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        nav_widget = self._create_nav_widget()
        content_widget = self._create_content_widget()

        self._create_status_bar()

        self.create_item_management_view()

        main_layout.addWidget(nav_widget)
        main_layout.addWidget(content_widget)

        self.update_stats()

    def _create_nav_widget(self) -> QWidget:
        """
        创建导航侧边栏部件。

        Returns:
            配置好的导航栏部件。
        """
        nav_widget = QWidget()
        nav_widget.setFixedWidth(NAV_WIDTH)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(0)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        nav_header = QWidget()
        nav_header.setObjectName("navHeader")
        nav_header_layout = QVBoxLayout(nav_header)
        nav_header_layout.setContentsMargins(24, 24, 24, 24)

        nav_title = QLabel('💎 记录管理')
        nav_title.setObjectName("navTitle")
        nav_header_layout.addWidget(nav_title)

        nav_subtitle = QLabel('资产管理系统')
        nav_subtitle.setObjectName("navSubtitle")
        nav_header_layout.addWidget(nav_subtitle)

        nav_layout.addWidget(nav_header)

        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("QListWidget { border-radius: 0 0 12px 12px; }")

        item1 = QListWidgetItem('📦 物品记录管理')
        self.nav_list.addItem(item1)

        item2 = QListWidgetItem('👕 衣物记录管理')
        self.nav_list.addItem(item2)

        self.nav_list.setCurrentRow(0)
        self.nav_list.itemClicked.connect(self.switch_view)
        nav_layout.addWidget(self.nav_list)

        theme_button = QPushButton('🌓 切换主题')
        theme_button.setObjectName("themeButton")
        theme_button.clicked.connect(self.toggle_theme)
        nav_layout.addWidget(theme_button)

        return nav_widget

    def _create_content_widget(self) -> QWidget:
        """
        创建内容区域部件。

        Returns:
            配置好的内容区域部件。
        """
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(20, 0, 20, 0)
        return content_widget

    def _create_status_bar(self) -> None:
        """
        创建状态栏。

        初始化状态栏及其标签组件。
        """
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.status_label = QLabel('✅ 就绪')
        self.status_label.setObjectName("statusLabel")

        self.item_count_status = QLabel('📦 物品数量: 0')
        self.item_count_status.setObjectName("itemCountStatus")

        self.statusBar.addWidget(self.status_label)
        self.statusBar.addPermanentWidget(self.item_count_status)

    def create_item_management_view(self) -> None:
        """
        创建物品记录管理视图（只创建一次）。

        构建包含统计信息、输入区域、搜索区域和物品列表的完整视图。
        """
        if self.item_management_widget is not None:
            return

        self.item_management_widget = QWidget()
        item_layout = QVBoxLayout(self.item_management_widget)
        item_layout.setSpacing(10)
        item_layout.setContentsMargins(0, 0, 0, 0)

        stats_group = self._create_stats_group()
        input_search_layout = self._create_input_search_layout()
        table_group = self._create_table_group()

        item_layout.addWidget(stats_group)
        item_layout.addLayout(input_search_layout)
        item_layout.addWidget(table_group, 1)

        self.content_layout.addWidget(self.item_management_widget)

    def _create_stats_group(self) -> QGroupBox:
        """
        创建统计信息区域。

        Returns:
            包含统计卡件的分组框。
        """
        stats_group = QGroupBox('📊 统计信息')
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(18, 18, 18, 18)

        total_assets_card = self._create_stat_card(
            "totalAssetsCard", "总资产", "totalAssetsValue", "¥0.00"
        )
        self.total_assets_label = total_assets_card.findChild(QLabel, "totalAssetsValue")

        daily_cost_card = self._create_stat_card(
            "dailyCostCard", "日均总成本", "dailyCostValue", "¥0.00"
        )
        self.daily_cost_label = daily_cost_card.findChild(QLabel, "dailyCostValue")

        item_count_card = self._create_stat_card(
            "itemCountCard", "物品数量", "itemCountValue", "0"
        )
        self.item_count_label = item_count_card.findChild(QLabel, "itemCountValue")

        stats_layout.addWidget(total_assets_card, 1)
        stats_layout.addWidget(daily_cost_card, 1)
        stats_layout.addWidget(item_count_card, 1)
        stats_group.setLayout(stats_layout)

        return stats_group

    def _create_stat_card(
        self, card_name: str, title: str, value_name: str, initial_value: str
    ) -> QWidget:
        """
        创建单个统计卡片。

        Args:
            card_name: 卡片对象名称。
            title: 卡片标题。
            value_name: 数值标签对象名称。
            initial_value: 初始显示值。

        Returns:
            配置好的统计卡片部件。
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
        """
        创建输入和搜索区域的水平布局。

        Returns:
            包含输入区域和搜索区域的水平布局。
        """
        input_search_layout = QHBoxLayout()
        input_search_layout.setSpacing(15)

        input_group = self._create_input_group()
        search_group = self._create_search_group()

        input_search_layout.addWidget(input_group, 3)
        input_search_layout.addWidget(search_group, 1)

        return input_search_layout

    def _create_input_group(self) -> QGroupBox:
        """
        创建输入区域。

        Returns:
            包含物品输入控件的分组框。
        """
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
        self.add_button.clicked.connect(self.add_item)
        input_layout.addWidget(self.add_button, 0, 7, 1, 1)

        input_group.setLayout(input_layout)
        return input_group

    def _create_search_group(self) -> QGroupBox:
        """
        创建搜索区域。

        Returns:
            包含搜索控件的分组框。
        """
        search_group = QGroupBox('搜索')
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        search_layout.setContentsMargins(20, 18, 20, 18)

        search_label = QLabel('🔍')
        search_label.setStyleSheet("font-size: 16px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入物品名称进行搜索...')
        self.search_input.textChanged.connect(self.search_items)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_group.setLayout(search_layout)

        return search_group

    def _create_table_group(self) -> QGroupBox:
        """
        创建物品列表表格区域。

        Returns:
            包含表格控件的分组框。
        """
        table_group = QGroupBox('📋 物品列表')
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ['物品名称', '购买价格', '购买日期', '状态', '已使用天数', '日均使用价格', '操作']
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.resizeSection(6, 300)

        self.table.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        self.table.verticalHeader().setVisible(False)

        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        self.table.cellClicked.connect(self.handle_cell_click)
        header.sectionClicked.connect(self.handle_header_click)

        for i in range(7):
            self.sort_states[i] = 0

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)

        return table_group

    def switch_view(self, item: QListWidgetItem) -> None:
        """
        切换不同的记录管理视图。

        Args:
            item: 点击的导航项。
        """
        view_name = item.text()
        if '物品记录管理' in view_name:
            if self.clothing_management_widget:
                self.clothing_management_widget.hide()
            if self.item_management_widget:
                self.item_management_widget.show()
            self.refresh_table()
            self.update_stats()
        elif '衣物记录管理' in view_name:
            if self.item_management_widget:
                self.item_management_widget.hide()
            self.create_clothing_management_view()
            self.clothing_management_widget.show()
            self._apply_clothing_filters()
            self.update_clothing_stats()

    def handle_header_click(self, logical_index: int) -> None:
        """
        处理表头点击事件，实现点击第三下取消排序。

        Args:
            logical_index: 点击的列索引。
        """
        self.table.setSortingEnabled(False)

        self.sort_states[logical_index] = (self.sort_states[logical_index] + 1) % 3

        if self.sort_states[logical_index] == 0:
            self.table.setSortingEnabled(True)
            self.table.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            if self.search_input.text():
                self.search_items()
            else:
                self.refresh_table()
        elif self.sort_states[logical_index] == 1:
            self.table.sortByColumn(logical_index, Qt.AscendingOrder)
            self.table.setSortingEnabled(True)
        else:
            self.table.sortByColumn(logical_index, Qt.DescendingOrder)
            self.table.setSortingEnabled(True)

    def add_item(self) -> None:
        """
        添加物品功能函数。

        验证输入并添加新物品到管理器。
        """
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()

        if not name:
            QMessageBox.warning(self, '警告', '请输入物品名称')
            return

        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError("价格必须大于0")
        except ValueError:
            QMessageBox.warning(self, '警告', '请输入有效的购买价格')
            return

        self.item_manager.add_item(name, price, self.date_input.date())

        if self.search_input.text():
            self.search_items()
        else:
            self.refresh_table()
        self.update_stats()
        self.statusBar.showMessage('物品添加成功', STATUS_MESSAGE_DURATION)

        self.name_input.clear()
        self.price_input.clear()
        self.date_input.setDate(QDate.currentDate())

    def refresh_table(self) -> None:
        """
        刷新表格显示。

        从物品管理器加载所有物品并更新表格。
        """
        items = self.item_manager.get_items()

        current_sort_column = self.table.horizontalHeader().sortIndicatorSection()
        current_sort_order = self.table.horizontalHeader().sortIndicatorOrder()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            self._populate_table_row(row, item)

        self.table.setSortingEnabled(True)

        if current_sort_column != -1:
            self.table.sortByColumn(current_sort_column, current_sort_order)

    def _populate_table_row(self, row: int, item: dict[str, Any]) -> None:
        """
        填充表格单行数据。

        Args:
            row: 行索引。
            item: 物品数据字典。
        """
        is_discontinued = item.get('status') == 'discontinued'
        
        name_item = QTableWidgetItem(item['name'])
        name_item.setToolTip(f"物品：{item['name']}")
        if is_discontinued:
            name_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 0, name_item)

        price_item = QTableWidgetItem(f"¥{item['price']:.2f}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_item.setData(Qt.ItemDataRole.UserRole, item['price'])
        if is_discontinued:
            price_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 1, price_item)

        date_item = QTableWidgetItem(item['purchase_date'])
        if is_discontinued:
            date_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 2, date_item)

        status_text = '已停用' if is_discontinued else '使用中'
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if is_discontinued:
            status_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 3, status_item)

        days_used = self.item_manager.calculate_days_used(item)
        days_item = QTableWidgetItem(str(days_used))
        days_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        days_item.setData(Qt.ItemDataRole.UserRole, days_used)
        if is_discontinued:
            days_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 4, days_item)

        daily_cost = self.item_manager.calculate_daily_cost(item)
        daily_cost_item = QTableWidgetItem(f"¥{daily_cost:.2f}")
        daily_cost_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        daily_cost_item.setData(Qt.ItemDataRole.UserRole, daily_cost)
        if is_discontinued:
            daily_cost_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 5, daily_cost_item)

        button_widget = self._create_action_buttons(row, item)
        self.table.setCellWidget(row, 6, button_widget)

    def _create_action_buttons(self, row: int, item: Optional[dict[str, Any]] = None) -> QWidget:
        """
        创建操作按钮部件。

        Args:
            row: 对应的表格行索引。
            item: 物品数据字典，用于判断状态。

        Returns:
            包含编辑、停用/重新启用和删除按钮的部件。
        """
        is_discontinued = item.get('status') == 'discontinued' if item else False
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(6)

        edit_btn = QPushButton('✏️ 修改')
        edit_btn.setObjectName("editButton")
        edit_btn.clicked.connect(lambda _, r=row: self.edit_item(r))
        button_layout.addWidget(edit_btn)

        if is_discontinued:
            reactivate_btn = QPushButton('🔄 启用')
            reactivate_btn.setObjectName("reactivateButton")
            reactivate_btn.clicked.connect(lambda _, r=row: self.reactivate_item(r))
            button_layout.addWidget(reactivate_btn)
        else:
            discontinue_btn = QPushButton('⏹️ 停用')
            discontinue_btn.setObjectName("discontinueButton")
            discontinue_btn.clicked.connect(lambda _, r=row: self.discontinue_item(r))
            button_layout.addWidget(discontinue_btn)

        delete_btn = QPushButton('🗑️ 删除')
        delete_btn.setObjectName("deleteButton")
        delete_btn.clicked.connect(lambda _, r=row: self.delete_item(r))
        button_layout.addWidget(delete_btn)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        return button_widget

    def delete_item(self, row: int) -> None:
        """
        删除物品功能函数。

        Args:
            row: 要删除的行号。
        """
        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除物品 "{self.item_manager.items[row]["name"]}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.item_manager.remove_item(row)
            if self.search_input.text():
                self.search_items()
            else:
                self.refresh_table()
            self.update_stats()
            self.statusBar.showMessage('物品删除成功', STATUS_MESSAGE_DURATION)

    def discontinue_item(self, row: int) -> None:
        """
        停用物品功能函数。

        Args:
            row: 要停用的行号。
        """
        item = self.item_manager.items[row]
        dialog = DiscontinueDialog(self, item['name'])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            discontinue_date = dialog.get_discontinue_date()
            discontinue_reason = dialog.get_discontinue_reason()
            
            self.item_manager.discontinue_item(row, discontinue_date, discontinue_reason)
            
            if self.search_input.text():
                self.search_items()
            else:
                self.refresh_table()
            self.update_stats()
            self.statusBar.showMessage(
                f'物品已停用，原因：{discontinue_reason}',
                STATUS_MESSAGE_DURATION
            )

    def reactivate_item(self, row: int) -> None:
        """
        重新启用物品功能函数。

        Args:
            row: 要重新启用的行号。
        """
        item = self.item_manager.items[row]
        reply = QMessageBox.question(
            self,
            '确认重新启用',
            f'确定要重新启用物品 "{item["name"]}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.item_manager.reactivate_item(row)
            if self.search_input.text():
                self.search_items()
            else:
                self.refresh_table()
            self.update_stats()
            self.statusBar.showMessage('物品已重新启用', STATUS_MESSAGE_DURATION)

    def update_stats(self) -> None:
        """
        更新统计信息显示。

        计算并更新总资产、日均总成本和物品数量。
        """
        total_assets = self.item_manager.get_total_assets()
        average_daily_cost = self.item_manager.get_average_daily_cost()
        item_count = len(self.item_manager.get_items())

        self.total_assets_label.setText(f'¥{total_assets:.2f}')
        self.daily_cost_label.setText(f'¥{average_daily_cost:.2f}')
        self.item_count_label.setText(f'{item_count}')

        self.item_count_status.setText(f'📦 物品数量: {item_count}')

    def search_items(self) -> None:
        """
        搜索物品功能。

        根据搜索文本过滤并显示匹配的物品。
        """
        search_text = self.search_input.text().lower()
        items = self.item_manager.get_items()

        filtered_items = [
            item for item in items if search_text in item['name'].lower()
        ]

        current_sort_column = self.table.horizontalHeader().sortIndicatorSection()
        current_sort_order = self.table.horizontalHeader().sortIndicatorOrder()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(filtered_items))

        for row, item in enumerate(filtered_items):
            self._populate_search_table_row(row, item, items)

        self.table.setSortingEnabled(True)

        if current_sort_column != -1:
            self.table.sortByColumn(current_sort_column, current_sort_order)

    def _populate_search_table_row(
        self, row: int, item: dict[str, Any], all_items: list[dict[str, Any]]
    ) -> None:
        """
        填充搜索结果表格单行数据。

        Args:
            row: 行索引。
            item: 物品数据字典。
            all_items: 完整物品列表，用于查找原始索引。
        """
        is_discontinued = item.get('status') == 'discontinued'
        
        name_item = QTableWidgetItem(item['name'])
        name_item.setToolTip(f"物品：{item['name']}")
        if is_discontinued:
            name_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 0, name_item)

        price_item = QTableWidgetItem(f"¥{item['price']:.2f}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_item.setData(Qt.ItemDataRole.UserRole, item['price'])
        if is_discontinued:
            price_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 1, price_item)

        date_item = QTableWidgetItem(item['purchase_date'])
        if is_discontinued:
            date_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 2, date_item)

        status_text = '已停用' if is_discontinued else '使用中'
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if is_discontinued:
            status_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 3, status_item)

        days_used = self.item_manager.calculate_days_used(item)
        days_item = QTableWidgetItem(str(days_used))
        days_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        days_item.setData(Qt.ItemDataRole.UserRole, days_used)
        if is_discontinued:
            days_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 4, days_item)

        daily_cost = self.item_manager.calculate_daily_cost(item)
        daily_cost_item = QTableWidgetItem(f"¥{daily_cost:.2f}")
        daily_cost_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        daily_cost_item.setData(Qt.ItemDataRole.UserRole, daily_cost)
        if is_discontinued:
            daily_cost_item.setForeground(Qt.GlobalColor.gray)
        self.table.setItem(row, 5, daily_cost_item)

        original_index = all_items.index(item)
        button_widget = self._create_action_buttons(original_index, item)
        self.table.setCellWidget(row, 6, button_widget)

    def handle_cell_click(self, row: int, column: int) -> None:
        """
        处理表格单元格点击事件。

        Args:
            row: 行号。
            column: 列号。
        """

    def edit_item(self, row: int) -> None:
        """
        修改物品功能函数。

        Args:
            row: 要修改的行号。
        """
        item = self.item_manager.items[row]

        dialog = QDialog(self)
        dialog.setWindowTitle('修改物品')
        dialog.setGeometry(200, 200, 400, 200)

        layout = QFormLayout(dialog)

        name_edit = QLineEdit(item['name'])
        price_edit = QLineEdit(str(item['price']))
        date_edit = DateInput()
        date_edit.setDate(QDate.fromString(item['purchase_date'], 'yyyy-MM-dd'))

        layout.addRow('物品名称:', name_edit)
        layout.addRow('购买价格:', price_edit)
        layout.addRow('购买日期:', date_edit)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
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

            try:
                price = float(price_text)
                if price <= 0:
                    raise ValueError("价格必须大于0")
            except ValueError:
                QMessageBox.warning(self, '警告', '请输入有效的购买价格')
                return

            self.item_manager.update_item(row, name, price, date_edit.date())

            if self.search_input.text():
                self.search_items()
            else:
                self.refresh_table()
            self.update_stats()
            self.statusBar.showMessage('物品修改成功', STATUS_MESSAGE_DURATION)

    def create_clothing_management_view(self) -> None:
        """
        创建衣物记录管理视图（只创建一次）。

        构建包含统计信息、输入区域、搜索区域和衣物列表的完整视图。
        """
        if self.clothing_management_widget is not None:
            return

        self.clothing_management_widget = QWidget()
        clothing_layout = QVBoxLayout(self.clothing_management_widget)
        clothing_layout.setSpacing(10)
        clothing_layout.setContentsMargins(0, 0, 0, 0)

        stats_group = self._create_clothing_stats_group()
        input_search_layout = self._create_clothing_input_search_layout()
        table_group = self._create_clothing_table_group()

        clothing_layout.addWidget(stats_group)
        clothing_layout.addLayout(input_search_layout)
        clothing_layout.addWidget(table_group, 1)

        self.content_layout.addWidget(self.clothing_management_widget)
        self.clothing_management_widget.hide()

    def _create_clothing_stats_group(self) -> QGroupBox:
        """
        创建衣物统计信息区域。

        Returns:
            包含统计卡件的分组框。
        """
        stats_group = QGroupBox('📊 统计信息')
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(18, 18, 18, 18)

        total_assets_card = self._create_stat_card(
            "clothingTotalAssetsCard", "总资产", "clothingTotalAssetsValue", "¥0.00"
        )
        self.clothing_total_assets_label = total_assets_card.findChild(
            QLabel, "clothingTotalAssetsValue"
        )

        item_count_card = self._create_stat_card(
            "clothingCountCard", "衣物数量", "clothingCountValue", "0"
        )
        self.clothing_count_label = item_count_card.findChild(
            QLabel, "clothingCountValue"
        )

        stats_layout.addWidget(total_assets_card, 1)
        stats_layout.addWidget(item_count_card, 1)
        stats_group.setLayout(stats_layout)

        return stats_group

    def _create_clothing_input_search_layout(self) -> QHBoxLayout:
        """
        创建衣物输入和搜索区域的水平布局。

        Returns:
            包含输入区域和搜索区域的水平布局。
        """
        input_search_layout = QHBoxLayout()
        input_search_layout.setSpacing(15)

        input_group = self._create_clothing_input_group()
        search_group = self._create_clothing_search_group()

        input_search_layout.addWidget(input_group, 3)
        input_search_layout.addWidget(search_group, 1)

        return input_search_layout

    def _create_clothing_input_group(self) -> QGroupBox:
        """
        创建衣物输入区域。

        Returns:
            包含衣物输入控件的分组框。
        """
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
        self.clothing_type_input = QLineEdit()
        self.clothing_type_input.setPlaceholderText('如：T恤、裤子、外套')
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
        self.add_clothing_button.clicked.connect(self.add_clothing)
        input_layout.addWidget(self.add_clothing_button)

        input_group.setLayout(input_layout)
        return input_group

    def _create_clothing_search_group(self) -> QGroupBox:
        """
        创建衣物搜索区域。

        Returns:
            包含搜索控件的分组框。
        """
        search_group = QGroupBox('🔍 搜索')
        search_group.setObjectName("clothingSearchGroup")
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        search_layout.setContentsMargins(20, 14, 20, 14)

        search_label = QLabel('🔍')
        search_label.setStyleSheet("font-size: 16px;")
        self.clothing_search_input = QLineEdit()
        self.clothing_search_input.setPlaceholderText('输入衣物名称进行搜索...')
        self.clothing_search_input.textChanged.connect(self.search_clothing)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.clothing_search_input)

        search_group.setLayout(search_layout)

        return search_group

    def _create_clothing_table_group(self) -> QGroupBox:
        """
        创建衣物列表表格区域。

        Returns:
            包含表格控件的分组框。
        """
        table_group = QGroupBox('📋 衣物列表')
        table_group.setObjectName("clothingTableGroup")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.clothing_table = QTableWidget()
        self.clothing_table.setObjectName("clothingTable")
        self.clothing_table.setColumnCount(6)
        self.clothing_table.setHorizontalHeaderLabels(
            ['衣物名称', '衣物类型', '购买价格', '购买日期', '状态', '操作']
        )

        self.clothing_filter_header = FilterHeader(self.clothing_table)
        self.clothing_table.setHorizontalHeader(self.clothing_filter_header)
        self.clothing_filter_header.filter_clicked.connect(self._show_type_filter)

        header = self.clothing_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 120)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.resizeSection(5, 300)

        self.clothing_table.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        self.clothing_table.verticalHeader().setVisible(False)

        self.clothing_table.setSortingEnabled(True)
        self.clothing_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.clothing_table.setAlternatingRowColors(True)

        self.clothing_table.cellClicked.connect(self.handle_clothing_cell_click)
        header.sectionClicked.connect(self.handle_clothing_header_click)

        for i in range(6):
            self.clothing_sort_states[i] = 0

        table_layout.addWidget(self.clothing_table)
        table_group.setLayout(table_layout)

        return table_group

    def handle_clothing_header_click(self, logical_index: int) -> None:
        """
        处理衣物表头点击事件，实现点击第三下取消排序。

        Args:
            logical_index: 点击的列索引。
        """
        self.clothing_table.setSortingEnabled(False)

        self.clothing_sort_states[logical_index] = (
            self.clothing_sort_states[logical_index] + 1
        ) % 3

        if self.clothing_sort_states[logical_index] == 0:
            self.clothing_table.setSortingEnabled(True)
            self.clothing_table.horizontalHeader().setSortIndicator(
                -1, Qt.AscendingOrder
            )
            if self.clothing_search_input.text():
                self.search_clothing()
            else:
                self.refresh_clothing_table()
        elif self.clothing_sort_states[logical_index] == 1:
            self.clothing_table.sortByColumn(logical_index, Qt.AscendingOrder)
            self.clothing_table.setSortingEnabled(True)
        else:
            self.clothing_table.sortByColumn(logical_index, Qt.DescendingOrder)
            self.clothing_table.setSortingEnabled(True)

    def add_clothing(self) -> None:
        """
        添加衣物功能函数。

        验证输入并添加新衣物到管理器。
        """
        name = self.clothing_name_input.text().strip()
        clothing_type = self.clothing_type_input.text().strip()
        price_text = self.clothing_price_input.text().strip()

        if not name:
            QMessageBox.warning(self, '警告', '请输入衣物名称')
            return

        if not clothing_type:
            QMessageBox.warning(self, '警告', '请输入衣物类型')
            return

        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError("价格必须大于0")
        except ValueError:
            QMessageBox.warning(self, '警告', '请输入有效的购买价格')
            return

        self.clothing_manager.add_item(
            name, clothing_type, price, self.clothing_date_input.date()
        )

        self._apply_clothing_filters()
        self.update_clothing_stats()
        self.statusBar.showMessage('衣物添加成功', STATUS_MESSAGE_DURATION)

        self.clothing_name_input.clear()
        self.clothing_type_input.clear()
        self.clothing_price_input.clear()
        self.clothing_date_input.setDate(QDate.currentDate())

    def refresh_clothing_table(self) -> None:
        """
        刷新衣物表格显示。

        从衣物管理器加载所有衣物并更新表格。
        """
        items = self.clothing_manager.get_items()

        current_sort_column = (
            self.clothing_table.horizontalHeader().sortIndicatorSection()
        )
        current_sort_order = self.clothing_table.horizontalHeader().sortIndicatorOrder()

        self.clothing_table.setSortingEnabled(False)
        self.clothing_table.setRowCount(len(items))

        for row, item in enumerate(items):
            self._populate_clothing_table_row(row, item)

        self.clothing_table.setSortingEnabled(True)

        if current_sort_column != -1:
            self.clothing_table.sortByColumn(current_sort_column, current_sort_order)

    def _populate_clothing_table_row(self, row: int, item: dict[str, Any]) -> None:
        """
        填充衣物表格单行数据。

        Args:
            row: 行索引。
            item: 衣物数据字典。
        """
        is_discontinued = item.get('status') == 'discontinued'
        
        name_item = QTableWidgetItem(item.get('name', ''))
        name_item.setToolTip(f"衣物名称：{item.get('name', '')}")
        if is_discontinued:
            name_item.setForeground(Qt.GlobalColor.gray)
        self.clothing_table.setItem(row, 0, name_item)

        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setContentsMargins(4, 2, 4, 2)
        type_label = QLabel(item['clothing_type'])
        type_label.setObjectName("clothingTypeTag")
        if is_discontinued:
            type_label.setStyleSheet("color: gray;")
        type_layout.addWidget(type_label)
        type_layout.addStretch()
        self.clothing_table.setCellWidget(row, 1, type_widget)

        price_item = QTableWidgetItem(f"¥{item['price']:.2f}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_item.setData(Qt.ItemDataRole.UserRole, item['price'])
        if is_discontinued:
            price_item.setForeground(Qt.GlobalColor.gray)
        self.clothing_table.setItem(row, 2, price_item)

        date_item = QTableWidgetItem(item['purchase_date'])
        if is_discontinued:
            date_item.setForeground(Qt.GlobalColor.gray)
        self.clothing_table.setItem(row, 3, date_item)

        status_text = '已停用' if is_discontinued else '使用中'
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if is_discontinued:
            status_item.setForeground(Qt.GlobalColor.gray)
        self.clothing_table.setItem(row, 4, status_item)

        button_widget = self._create_clothing_action_buttons(row, item)
        self.clothing_table.setCellWidget(row, 5, button_widget)

    def _create_clothing_action_buttons(self, row: int, item: Optional[dict[str, Any]] = None) -> QWidget:
        """
        创建衣物操作按钮部件。

        Args:
            row: 对应的表格行索引。
            item: 衣物数据字典，用于判断状态。

        Returns:
            包含编辑、停用/重新启用和删除按钮的部件。
        """
        is_discontinued = item.get('status') == 'discontinued' if item else False
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(6)

        edit_btn = QPushButton('✏️ 修改')
        edit_btn.setObjectName("editButton")
        edit_btn.clicked.connect(lambda _, r=row: self.edit_clothing(r))
        button_layout.addWidget(edit_btn)

        if is_discontinued:
            reactivate_btn = QPushButton('🔄 启用')
            reactivate_btn.setObjectName("reactivateButton")
            reactivate_btn.clicked.connect(lambda _, r=row: self.reactivate_clothing(r))
            button_layout.addWidget(reactivate_btn)
        else:
            discontinue_btn = QPushButton('⏹️ 停用')
            discontinue_btn.setObjectName("discontinueButton")
            discontinue_btn.clicked.connect(lambda _, r=row: self.discontinue_clothing(r))
            button_layout.addWidget(discontinue_btn)

        delete_btn = QPushButton('🗑️ 删除')
        delete_btn.setObjectName("deleteButton")
        delete_btn.clicked.connect(lambda _, r=row: self.delete_clothing(r))
        button_layout.addWidget(delete_btn)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        return button_widget

    def delete_clothing(self, row: int) -> None:
        """
        删除衣物功能函数。

        Args:
            row: 要删除的行号。
        """
        item_name = self.clothing_manager.items[row].get('name', '未命名')
        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除衣物 "{item_name}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.clothing_manager.remove_item(row)
            self._apply_clothing_filters()
            self.update_clothing_stats()
            self.statusBar.showMessage('衣物删除成功', STATUS_MESSAGE_DURATION)

    def discontinue_clothing(self, row: int) -> None:
        """
        停用衣物功能函数。

        Args:
            row: 要停用的行号。
        """
        item = self.clothing_manager.items[row]
        dialog = DiscontinueDialog(self, item.get('name', '未命名'))
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            discontinue_date = dialog.get_discontinue_date()
            discontinue_reason = dialog.get_discontinue_reason()
            
            self.clothing_manager.discontinue_item(row, discontinue_date, discontinue_reason)
            self._apply_clothing_filters()
            self.update_clothing_stats()
            self.statusBar.showMessage(
                f'衣物已停用，原因：{discontinue_reason}',
                STATUS_MESSAGE_DURATION
            )

    def reactivate_clothing(self, row: int) -> None:
        """
        重新启用衣物功能函数。

        Args:
            row: 要重新启用的行号。
        """
        item = self.clothing_manager.items[row]
        reply = QMessageBox.question(
            self,
            '确认重新启用',
            f'确定要重新启用衣物 "{item.get("name", "未命名")}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.clothing_manager.reactivate_item(row)
            self._apply_clothing_filters()
            self.update_clothing_stats()
            self.statusBar.showMessage('衣物已重新启用', STATUS_MESSAGE_DURATION)

    def update_clothing_stats(self) -> None:
        """
        更新衣物统计信息显示。

        计算并更新总资产和衣物数量。
        """
        total_assets = self.clothing_manager.get_total_assets()
        item_count = len(self.clothing_manager.get_items())

        self.clothing_total_assets_label.setText(f'¥{total_assets:.2f}')
        self.clothing_count_label.setText(f'{item_count}')

    def _apply_clothing_filters(self) -> None:
        """
        应用搜索和类型筛选。
        """
        search_text = self.clothing_search_input.text().lower()
        selected_types = self.clothing_type_filter_selected

        items = self.clothing_manager.get_items()

        filtered_items = [
            item for item in items
            if (not search_text or search_text in item.get('name', '').lower())
            and (selected_types is None or item.get('clothing_type') in selected_types)
        ]

        current_sort_column = (
            self.clothing_table.horizontalHeader().sortIndicatorSection()
        )
        current_sort_order = self.clothing_table.horizontalHeader().sortIndicatorOrder()

        self.clothing_table.setSortingEnabled(False)
        self.clothing_table.setRowCount(len(filtered_items))

        for row, item in enumerate(filtered_items):
            self._populate_filtered_clothing_table_row(row, item, items)

        self.clothing_table.setSortingEnabled(True)

        if current_sort_column != -1:
            self.clothing_table.sortByColumn(current_sort_column, current_sort_order)

    def _show_type_filter(self, column: int) -> None:
        """
        显示类型过滤弹窗。

        Args:
            column: 点击的列索引。
        """
        all_types = self.clothing_manager.get_all_clothing_types()
        if not all_types:
            return

        if self.clothing_type_filter_selected is None:
            selected = all_types
        else:
            selected = self.clothing_type_filter_selected

        popup = FilterPopup(all_types, selected, self)

        header = self.clothing_filter_header
        x = header.sectionViewportPosition(column)
        width = header.sectionSize(column)
        height = header.height()

        global_pos = self.clothing_table.mapToGlobal(QPoint(x, height))
        popup.move(global_pos.x(), global_pos.y() + 2)
        popup.filter_applied.connect(self._on_type_filter_applied)
        popup.show()

    def _on_type_filter_applied(self, selected: list[str]) -> None:
        """
        处理类型筛选结果。

        Args:
            selected: 选中的类型列表。
        """
        all_types = self.clothing_manager.get_all_clothing_types()

        if set(selected) == set(all_types):
            self.clothing_type_filter_selected = None
            has_filter = False
        else:
            self.clothing_type_filter_selected = selected
            has_filter = True

        self.clothing_filter_header.set_filter_active(has_filter)

        self._apply_clothing_filters()

    def search_clothing(self) -> None:
        """
        搜索衣物功能。

        根据搜索文本过滤并显示匹配的衣物。
        """
        self._apply_clothing_filters()

    def _populate_filtered_clothing_table_row(
        self, row: int, item: dict[str, Any], all_items: list[dict[str, Any]]
    ) -> None:
        """
        填充过滤结果衣物表格单行数据。

        Args:
            row: 行索引。
            item: 衣物数据字典。
            all_items: 完整衣物列表，用于查找原始索引。
        """
        is_discontinued = item.get('status') == 'discontinued'
        
        name_item = QTableWidgetItem(item.get('name', ''))
        name_item.setToolTip(f"衣物名称：{item.get('name', '')}")
        if is_discontinued:
            name_item.setForeground(Qt.GlobalColor.gray)
        self.clothing_table.setItem(row, 0, name_item)

        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setContentsMargins(4, 2, 4, 2)
        type_label = QLabel(item['clothing_type'])
        type_label.setObjectName("clothingTypeTag")
        if is_discontinued:
            type_label.setStyleSheet("color: gray;")
        type_layout.addWidget(type_label)
        type_layout.addStretch()
        self.clothing_table.setCellWidget(row, 1, type_widget)

        price_item = QTableWidgetItem(f"¥{item['price']:.2f}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_item.setData(Qt.ItemDataRole.UserRole, item['price'])
        if is_discontinued:
            price_item.setForeground(Qt.GlobalColor.gray)
        self.clothing_table.setItem(row, 2, price_item)

        date_item = QTableWidgetItem(item['purchase_date'])
        if is_discontinued:
            date_item.setForeground(Qt.GlobalColor.gray)
        self.clothing_table.setItem(row, 3, date_item)

        status_text = '已停用' if is_discontinued else '使用中'
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if is_discontinued:
            status_item.setForeground(Qt.GlobalColor.gray)
        self.clothing_table.setItem(row, 4, status_item)

        original_index = all_items.index(item)
        button_widget = self._create_clothing_action_buttons(original_index, item)
        self.clothing_table.setCellWidget(row, 5, button_widget)

    def handle_clothing_cell_click(self, row: int, column: int) -> None:
        """
        处理衣物表格单元格点击事件。

        Args:
            row: 行号。
            column: 列号。
        """

    def edit_clothing(self, row: int) -> None:
        """
        修改衣物功能函数。

        Args:
            row: 要修改的行号。
        """
        item = self.clothing_manager.items[row]

        dialog = QDialog(self)
        dialog.setWindowTitle('修改衣物')
        dialog.setGeometry(200, 200, 400, 250)

        layout = QFormLayout(dialog)

        name_edit = QLineEdit(item.get('name', ''))
        type_edit = QLineEdit(item['clothing_type'])
        price_edit = QLineEdit(str(item['price']))
        date_edit = DateInput()
        date_edit.setDate(QDate.fromString(item['purchase_date'], 'yyyy-MM-dd'))

        layout.addRow('衣物名称:', name_edit)
        layout.addRow('衣物类型:', type_edit)
        layout.addRow('购买价格:', price_edit)
        layout.addRow('购买日期:', date_edit)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
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

            try:
                price = float(price_text)
                if price <= 0:
                    raise ValueError("价格必须大于0")
            except ValueError:
                QMessageBox.warning(self, '警告', '请输入有效的购买价格')
                return

            self.clothing_manager.update_item(
                row, name, clothing_type, price, date_edit.date()
            )

            self._apply_clothing_filters()
            self.update_clothing_stats()
            self.statusBar.showMessage('衣物修改成功', STATUS_MESSAGE_DURATION)
