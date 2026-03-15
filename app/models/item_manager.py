from PySide6.QtCore import QDate
import json
from app.utils.path_utils import get_items_file_path

class ItemManager:
    """
    物品管理类，负责数据的存储、加载、添加、删除和计算
    """
    def __init__(self):
        # 初始化物品列表
        self.items = []
        # 使用路径管理工具获取保存路径，确保跨平台兼容性
        self.save_path = get_items_file_path()
        # 确保资源目录存在
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        # 加载已保存的数据
        self.load_data()
    
    def load_data(self):
        """
        从本地文件加载物品数据
        """
        if self.save_path.exists():
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
            except:
                # 如果读取失败，初始化为空列表
                self.items = []
        else:
            # 如果文件不存在，初始化为空列表
            self.items = []
    
    def save_data(self):
        """
        将物品数据保存到本地文件
        """
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
    
    def add_item(self, name, price, purchase_date):
        """
        添加新物品到列表
        :param name: 物品名称
        :param price: 购买价格
        :param purchase_date: 购买日期（QDate对象）
        """
        item = {
            'name': name,
            'price': float(price),  # 价格转换为浮点数
            'purchase_date': purchase_date.toString('yyyy-MM-dd')  # 日期转字符串格式
        }
        self.items.append(item)
        self.save_data()  # 添加后立即保存到文件
    
    def remove_item(self, index):
        """
        根据索引删除物品
        :param index: 要删除的物品索引
        """
        if 0 <= index < len(self.items):
            del self.items[index]
            self.save_data()  # 删除后保存数据
    
    def update_item(self, index, name, price, purchase_date):
        """
        根据索引更新物品信息
        :param index: 要更新的物品索引
        :param name: 新的物品名称
        :param price: 新的购买价格
        :param purchase_date: 新的购买日期（QDate对象）
        """
        if 0 <= index < len(self.items):
            self.items[index] = {
                'name': name,
                'price': float(price),  # 价格转换为浮点数
                'purchase_date': purchase_date.toString('yyyy-MM-dd')  # 日期转字符串格式
            }
            self.save_data()  # 更新后保存数据
    
    def get_items(self):
        """
        获取所有物品列表
        :return: 物品列表
        """
        return self.items
    
    def calculate_days_used(self, item):
        """
        计算物品已使用天数
        :param item: 物品字典
        :return: 已使用天数
        """
        # 将字符串日期转换为QDate对象
        purchase_date = QDate.fromString(item['purchase_date'], 'yyyy-MM-dd')
        today = QDate.currentDate()  # 获取当前日期
        # 计算从购买日期到今天的天数（包含购买当天）
        days_used = purchase_date.daysTo(today) + 1
        return days_used
    
    def calculate_daily_cost(self, item):
        """
        计算单个物品的日均使用价格
        :param item: 物品字典
        :return: 日均使用价格
        """
        days_used = self.calculate_days_used(item)
        
        if days_used > 0:
            daily_cost = item['price'] / days_used
        else:
            daily_cost = item['price']
        
        return daily_cost
    
    def get_total_assets(self):
        """
        计算所有物品的总资产
        :return: 总资产金额
        """
        # 对所有物品的价格求和
        total = sum(item['price'] for item in self.items)
        return total
    
    def get_average_daily_cost(self):
        """
        计算所有物品的日均总成本
        :return: 日均总成本
        """
        if not self.items:
            return 0
        
        # 计算所有物品的日均使用价格总和
        total_daily_cost = sum(self.calculate_daily_cost(item) for item in self.items)
        return total_daily_cost