from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTableWidget, QTableWidgetItem, 
                               QPushButton, QLabel, QLineEdit, QDateEdit, 
                               QMessageBox, QHeaderView, QStatusBar, QGroupBox, QListWidget)
from PySide6.QtCore import Qt, QDate
from app.models.item_manager import ItemManager
from app.utils.path_utils import get_main_style_path

class MainWindow(QMainWindow):
    """
    主应用程序窗口类，继承自QMainWindow
    """
    def __init__(self):
        super().__init__()
        # 加载和应用样式
        self.load_styles()
        # 创建物品管理器实例
        self.item_manager = ItemManager()
        # 初始化用户界面
        self.init_ui()
        # 刷新表格显示
        self.refresh_table()
    
    def load_styles(self):
        """
        加载和应用 QSS 样式
        """
        style_path = get_main_style_path()
        if style_path.exists():
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    style = f.read()
                self.setStyleSheet(style)
            except Exception as e:
                print(f"加载样式文件失败: {e}")
    
    def init_ui(self):
        """
        初始化用户界面
        """
        self.setWindowTitle('记录管理器')
        self.setGeometry(100, 100, 1000, 750)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建导航侧边栏
        nav_widget = QWidget()
        nav_widget.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        
        # 导航标题
        nav_title = QLabel('记录管理')
        nav_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;")
        nav_layout.addWidget(nav_title)
        
        # 导航列表
        self.nav_list = QListWidget()
        self.nav_list.addItem('物品记录管理')
        # 预留其他记录管理功能的入口
        # self.nav_list.addItem('其他记录管理1')
        # self.nav_list.addItem('其他记录管理2')
        self.nav_list.setCurrentRow(0)
        self.nav_list.itemClicked.connect(self.switch_view)
        nav_layout.addWidget(self.nav_list)
        
        # 内容区域
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('就绪')
        
        # 创建物品记录管理视图
        self.create_item_management_view()
        
        # 将导航和内容添加到主布局
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(content_widget)
        
        # 初始更新统计数据
        self.update_stats()
    
    def create_item_management_view(self):
        """
        创建物品记录管理视图
        """
        # 清空内容布局
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 创建统计信息区域
        stats_group = QGroupBox('统计信息')
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # 总资产标签
        self.total_assets_label = QLabel('总资产: ¥0.00')
        self.total_assets_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        
        # 日均总成本标签
        self.daily_cost_label = QLabel('日均总成本: ¥0.00')
        self.daily_cost_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        
        # 物品数量标签
        self.item_count_label = QLabel('物品数量: 0')
        self.item_count_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        
        stats_layout.addWidget(self.total_assets_label)
        stats_layout.addWidget(self.daily_cost_label)
        stats_layout.addWidget(self.item_count_label)
        stats_group.setLayout(stats_layout)
        
        # 创建输入区域
        input_group = QGroupBox('添加物品')
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)
        
        # 物品名称输入
        name_label = QLabel('物品名称:')
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入物品名称')
        input_layout.addWidget(name_label)
        input_layout.addWidget(self.name_input)
        
        # 购买价格输入
        price_label = QLabel('购买价格:')
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText('请输入购买价格')
        input_layout.addWidget(price_label)
        input_layout.addWidget(self.price_input)
        
        # 购买日期输入（使用日期选择器）
        date_label = QLabel('购买日期:')
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())  # 默认为当前日期
        self.date_input.setDisplayFormat('yyyy-MM-dd')  # 设置日期显示格式
        input_layout.addWidget(date_label)
        input_layout.addWidget(self.date_input)
        
        # 添加按钮
        self.add_button = QPushButton('添加物品')
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.add_item)  # 连接添加物品函数
        input_layout.addWidget(self.add_button)
        
        input_group.setLayout(input_layout)
        
        # 创建搜索区域
        search_group = QGroupBox('搜索')
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        search_label = QLabel('搜索:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入物品名称进行搜索')
        self.search_input.textChanged.connect(self.search_items)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_group.setLayout(search_layout)
        
        # 创建表格用于显示物品列表
        table_group = QGroupBox('物品列表')
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 设置列数
        # 设置列标题
        self.table.setHorizontalHeaderLabels(['物品名称', '购买价格', '购买日期', '已使用天数', '日均使用价格', '操作'])
        # 设置表头自适应列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 物品名称列拉伸填充
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 价格列根据内容调整
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 日期列根据内容调整
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 使用天数列根据内容调整
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 日均价格列根据内容调整
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 操作列根据内容调整
        
        # 表格样式已在 QSS 文件中定义
        
        # 启用排序
        self.table.setSortingEnabled(True)
        # 禁用编辑功能
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 连接单元格点击信号
        self.table.cellClicked.connect(self.handle_cell_click)
        
        # 连接表头点击信号，实现点击第三下取消排序
        header.sectionClicked.connect(self.handle_header_click)
        # 存储排序状态
        self.sort_states = {}
        for i in range(6):
            self.sort_states[i] = 0  # 0: 未排序, 1: 升序, 2: 降序
        
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        
        # 将各组件添加到内容布局
        self.content_layout.addWidget(stats_group)
        self.content_layout.addWidget(input_group)
        self.content_layout.addWidget(search_group)
        self.content_layout.addWidget(table_group)
    
    def switch_view(self, item):
        """
        切换不同的记录管理视图
        :param item: 点击的导航项
        """
        view_name = item.text()
        if view_name == '物品记录管理':
            self.create_item_management_view()
            self.refresh_table()
            self.update_stats()
        # 可以在这里添加其他记录管理视图的切换逻辑
        # elif view_name == '其他记录管理1':
        #     self.create_other_view1()
        # elif view_name == '其他记录管理2':
        #     self.create_other_view2()
    
    def handle_header_click(self, logical_index):
        """
        处理表头点击事件，实现点击第三下取消排序
        :param logical_index: 点击的列索引
        """
        # 临时禁用排序以避免默认行为干扰
        self.table.setSortingEnabled(False)
        
        # 更新排序状态
        self.sort_states[logical_index] = (self.sort_states[logical_index] + 1) % 3
        
        if self.sort_states[logical_index] == 0:
            # 取消排序
            self.table.setSortingEnabled(True)
            # 重置排序指示器
            self.table.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            # 刷新表格以显示原始顺序
            if self.search_input.text():
                self.search_items()
            else:
                self.refresh_table()
        elif self.sort_states[logical_index] == 1:
            # 升序排序
            self.table.sortByColumn(logical_index, Qt.AscendingOrder)
            self.table.setSortingEnabled(True)
        else:
            # 降序排序
            self.table.sortByColumn(logical_index, Qt.DescendingOrder)
            self.table.setSortingEnabled(True)
    
    def add_item(self):
        """
        添加物品功能函数
        """
        # 获取输入框内容并去除首尾空白
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        
        # 验证物品名称是否为空
        if not name:
            QMessageBox.warning(self, '警告', '请输入物品名称')
            return
        
        # 验证价格是否为有效数字
        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, '警告', '请输入有效的购买价格')
            return
        
        # 添加物品到管理器
        self.item_manager.add_item(
            name, 
            price, 
            self.date_input.date()
        )
        
        # 刷新表格和统计数据
        if self.search_input.text():
            self.search_items()
        else:
            self.refresh_table()
        self.update_stats()
        # 更新状态栏
        self.statusBar.showMessage('物品添加成功', 3000)
        
        # 清空输入框
        self.name_input.clear()
        self.price_input.clear()
        self.date_input.setDate(QDate.currentDate())
    
    def refresh_table(self):
        """
        刷新表格显示
        """
        items = self.item_manager.get_items()
        
        # 保存当前排序状态
        current_sort_column = self.table.horizontalHeader().sortIndicatorSection()
        current_sort_order = self.table.horizontalHeader().sortIndicatorOrder()
        
        # 临时禁用排序以提高性能
        self.table.setSortingEnabled(False)
        
        # 设置表格行数为物品数量
        self.table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # 第0列：物品名称
            name_item = QTableWidgetItem(item['name'])
            name_item.setToolTip(f"物品：{item['name']}")
            self.table.setItem(row, 0, name_item)
            
            # 第1列：购买价格（右对齐）
            price_item = QTableWidgetItem(f"¥{item['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_item.setData(Qt.UserRole, item['price'])  # 存储原始价格用于排序
            self.table.setItem(row, 1, price_item)
            
            # 第2列：购买日期
            date_item = QTableWidgetItem(item['purchase_date'])
            self.table.setItem(row, 2, date_item)
            
            # 第3列：已使用天数（居中对齐，自动计算）
            days_used = self.item_manager.calculate_days_used(item)
            days_item = QTableWidgetItem(str(days_used))
            days_item.setTextAlignment(Qt.AlignCenter)
            days_item.setData(Qt.UserRole, days_used)  # 存储原始天数用于排序
            self.table.setItem(row, 3, days_item)
            
            # 第4列：日均使用价格（右对齐）
            daily_cost = self.item_manager.calculate_daily_cost(item)
            daily_cost_item = QTableWidgetItem(f"¥{daily_cost:.2f}")
            daily_cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            daily_cost_item.setData(Qt.UserRole, daily_cost)  # 存储原始日均价格用于排序
            self.table.setItem(row, 4, daily_cost_item)
            
            # 第5列：操作按钮
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(5, 2, 5, 2)
            
            # 修改按钮
            edit_btn = QPushButton('修改')
            edit_btn.setObjectName("editButton")
            edit_btn.setFixedWidth(70)
            edit_btn.clicked.connect(lambda _, r=row: self.edit_item(r))
            button_layout.addWidget(edit_btn)
            
            # 删除按钮
            delete_btn = QPushButton('删除')
            delete_btn.setObjectName("deleteButton")
            delete_btn.setFixedWidth(70)
            delete_btn.clicked.connect(lambda _, r=row: self.delete_item(r))
            button_layout.addWidget(delete_btn)
            
            # 创建容器部件来容纳按钮布局
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            self.table.setCellWidget(row, 5, button_widget)
        
        # 重新启用排序
        self.table.setSortingEnabled(True)
        
        # 恢复之前的排序状态
        if current_sort_column != -1:
            self.table.sortByColumn(current_sort_column, current_sort_order)
    
    def delete_item(self, row):
        """
        删除物品功能函数
        :param row: 要删除的行号
        """
        # 显示确认对话框
        reply = QMessageBox.question(
            self, 
            '确认删除', 
            f'确定要删除物品 "{self.item_manager.items[row]["name"]}" 吗？',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        # 如果用户确认删除
        if reply == QMessageBox.Yes:
            # 从管理器中删除物品
            self.item_manager.remove_item(row)
            # 刷新表格和统计数据
            if self.search_input.text():
                self.search_items()
            else:
                self.refresh_table()
            self.update_stats()
            # 更新状态栏
            self.statusBar.showMessage('物品删除成功', 3000)
    
    def update_stats(self):
        """
        更新统计信息显示
        """
        # 计算总资产和日均总成本
        total_assets = self.item_manager.get_total_assets()
        average_daily_cost = self.item_manager.get_average_daily_cost()
        item_count = len(self.item_manager.get_items())
        
        # 更新标签显示
        self.total_assets_label.setText(f'总资产: ¥{total_assets:.2f}')
        self.daily_cost_label.setText(f'日均总成本: ¥{average_daily_cost:.2f}')
        self.item_count_label.setText(f'物品数量: {item_count}')
    
    def search_items(self):
        """
        搜索物品功能
        """
        search_text = self.search_input.text().lower()
        items = self.item_manager.get_items()
        
        # 过滤物品
        filtered_items = [item for item in items if search_text in item['name'].lower()]
        
        # 保存当前排序状态
        current_sort_column = self.table.horizontalHeader().sortIndicatorSection()
        current_sort_order = self.table.horizontalHeader().sortIndicatorOrder()
        
        # 临时禁用排序以提高性能
        self.table.setSortingEnabled(False)
        
        # 更新表格显示
        self.table.setRowCount(len(filtered_items))
        
        for row, item in enumerate(filtered_items):
            # 第0列：物品名称
            name_item = QTableWidgetItem(item['name'])
            name_item.setToolTip(f"物品：{item['name']}")
            self.table.setItem(row, 0, name_item)
            
            # 第1列：购买价格（右对齐）
            price_item = QTableWidgetItem(f"¥{item['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_item.setData(Qt.UserRole, item['price'])  # 存储原始价格用于排序
            self.table.setItem(row, 1, price_item)
            
            # 第2列：购买日期
            date_item = QTableWidgetItem(item['purchase_date'])
            self.table.setItem(row, 2, date_item)
            
            # 第3列：已使用天数（居中对齐，自动计算）
            days_used = self.item_manager.calculate_days_used(item)
            days_item = QTableWidgetItem(str(days_used))
            days_item.setTextAlignment(Qt.AlignCenter)
            days_item.setData(Qt.UserRole, days_used)  # 存储原始天数用于排序
            self.table.setItem(row, 3, days_item)
            
            # 第4列：日均使用价格（右对齐）
            daily_cost = self.item_manager.calculate_daily_cost(item)
            daily_cost_item = QTableWidgetItem(f"¥{daily_cost:.2f}")
            daily_cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            daily_cost_item.setData(Qt.UserRole, daily_cost)  # 存储原始日均价格用于排序
            self.table.setItem(row, 4, daily_cost_item)
            
            # 第5列：操作按钮
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(5, 2, 5, 2)
            
            # 修改按钮
            edit_btn = QPushButton('修改')
            edit_btn.setObjectName("editButton")
            edit_btn.setFixedWidth(70)
            # 查找原索引
            original_index = items.index(item)
            edit_btn.clicked.connect(lambda _, r=original_index: self.edit_item(r))
            button_layout.addWidget(edit_btn)
            
            # 删除按钮
            delete_btn = QPushButton('删除')
            delete_btn.setObjectName("deleteButton")
            delete_btn.setFixedWidth(70)
            delete_btn.clicked.connect(lambda _, r=original_index: self.delete_item(r))
            button_layout.addWidget(delete_btn)
            
            # 创建容器部件来容纳按钮布局
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            self.table.setCellWidget(row, 5, button_widget)
        
        # 重新启用排序
        self.table.setSortingEnabled(True)
        
        # 恢复之前的排序状态
        if current_sort_column != -1:
            self.table.sortByColumn(current_sort_column, current_sort_order)
    
    def handle_cell_click(self, row, column):
        """
        处理表格单元格点击事件
        :param row: 行号
        :param column: 列号
        """
        # 当前不执行特殊操作，保留接口供后续扩展
        pass
    
    def edit_item(self, row):
        """
        修改物品功能函数
        :param row: 要修改的行号
        """
        # 获取要修改的物品
        item = self.item_manager.items[row]
        
        # 创建修改对话框
        from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle('修改物品')
        dialog.setGeometry(200, 200, 400, 200)
        
        layout = QFormLayout(dialog)
        
        # 创建输入控件
        name_edit = QLineEdit(item['name'])
        price_edit = QLineEdit(str(item['price']))
        date_edit = QDateEdit()
        date_edit.setDate(QDate.fromString(item['purchase_date'], 'yyyy-MM-dd'))
        date_edit.setDisplayFormat('yyyy-MM-dd')
        
        # 添加到布局
        layout.addRow('物品名称:', name_edit)
        layout.addRow('购买价格:', price_edit)
        layout.addRow('购买日期:', date_edit)
        
        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(button_box)
        
        # 连接按钮信号
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # 显示对话框
        if dialog.exec() == QDialog.Accepted:
            # 获取输入值
            name = name_edit.text().strip()
            price_text = price_edit.text().strip()
            
            # 验证输入
            if not name:
                QMessageBox.warning(self, '警告', '请输入物品名称')
                return
            
            try:
                price = float(price_text)
                if price <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, '警告', '请输入有效的购买价格')
                return
            
            # 更新物品
            self.item_manager.update_item(
                row, 
                name, 
                price, 
                date_edit.date()
            )
            
            # 刷新表格和统计数据
            if self.search_input.text():
                self.search_items()
            else:
                self.refresh_table()
            self.update_stats()
            # 更新状态栏
            self.statusBar.showMessage('物品修改成功', 3000)

