"""
物品管理模块。

负责物品数据的存储、加载、添加、删除和计算功能。
"""

import json
from pathlib import Path
from typing import Any, Literal

from PySide6.QtCore import QDate

from app.utils.path_utils import get_items_file_path

ItemStatus = Literal['active', 'discontinued']
DiscontinueReason = Literal['报废', '转卖', '闲置', '其他']

DISCONTINUE_REASONS: list[DiscontinueReason] = ['报废', '转卖', '闲置', '其他']


class ItemManager:
    """
    物品管理类，负责数据的存储、加载、添加、删除和计算。

    Attributes:
        items: 物品列表，每个物品为包含名称、价格和购买日期的字典。
        save_path: 数据文件的保存路径。
    """

    def __init__(self) -> None:
        """
        初始化物品管理器。

        设置保存路径，确保目录存在，并加载已保存的数据。
        """
        self.items: list[dict[str, Any]] = []
        self.save_path: Path = get_items_file_path()
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        self.load_data()

    def load_data(self) -> None:
        """
        从本地文件加载物品数据。

        如果文件不存在或读取失败，初始化为空列表。
        """
        if not self.save_path.exists():
            self.items = []
            return

        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                self.items = json.load(f)
        except (json.JSONDecodeError, OSError):
            self.items = []

    def save_data(self) -> None:
        """
        将物品数据保存到本地文件。
        """
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

    def add_item(self, name: str, price: float, purchase_date: QDate) -> None:
        """
        添加新物品到列表。

        Args:
            name: 物品名称。
            price: 购买价格。
            purchase_date: 购买日期（QDate 对象）。
        """
        item = {
            'name': name,
            'price': float(price),
            'purchase_date': purchase_date.toString('yyyy-MM-dd'),
            'status': 'active',
            'discontinued_date': None,
            'discontinued_reason': None,
        }
        self.items.append(item)
        self.save_data()

    def remove_item(self, index: int) -> None:
        """
        根据索引删除物品。

        Args:
            index: 要删除的物品索引。
        """
        if 0 <= index < len(self.items):
            del self.items[index]
            self.save_data()

    def update_item(
        self, index: int, name: str, price: float, purchase_date: QDate
    ) -> None:
        """
        根据索引更新物品信息。

        Args:
            index: 要更新的物品索引。
            name: 新的物品名称。
            price: 新的购买价格。
            purchase_date: 新的购买日期（QDate 对象）。
        """
        if 0 <= index < len(self.items):
            existing_item = self.items[index]
            self.items[index] = {
                'name': name,
                'price': float(price),
                'purchase_date': purchase_date.toString('yyyy-MM-dd'),
                'status': existing_item.get('status', 'active'),
                'discontinued_date': existing_item.get('discontinued_date'),
                'discontinued_reason': existing_item.get('discontinued_reason'),
            }
            self.save_data()

    def discontinue_item(
        self,
        index: int,
        discontinued_date: QDate,
        discontinued_reason: str,
    ) -> None:
        """
        将物品标记为已停用。

        Args:
            index: 要停用的物品索引。
            discontinued_date: 停用日期（QDate 对象）。
            discontinued_reason: 停用原因。
        """
        if 0 <= index < len(self.items):
            self.items[index]['status'] = 'discontinued'
            self.items[index]['discontinued_date'] = discontinued_date.toString(
                'yyyy-MM-dd'
            )
            self.items[index]['discontinued_reason'] = discontinued_reason
            self.save_data()

    def reactivate_item(self, index: int) -> None:
        """
        将已停用的物品重新启用。

        Args:
            index: 要重新启用的物品索引。
        """
        if 0 <= index < len(self.items):
            self.items[index]['status'] = 'active'
            self.items[index]['discontinued_date'] = None
            self.items[index]['discontinued_reason'] = None
            self.save_data()

    def get_items(self) -> list[dict[str, Any]]:
        """
        获取所有物品列表。

        Returns:
            物品列表。
        """
        return self.items

    def calculate_days_used(self, item: dict[str, Any]) -> int:
        """
        计算物品已使用天数。

        Args:
            item: 物品字典。

        Returns:
            已使用天数（包含购买当天）。
        """
        purchase_date = QDate.fromString(item['purchase_date'], 'yyyy-MM-dd')
        
        if item.get('status') == 'discontinued' and item.get('discontinued_date'):
            end_date = QDate.fromString(item['discontinued_date'], 'yyyy-MM-dd')
        else:
            end_date = QDate.currentDate()
        
        days_used = purchase_date.daysTo(end_date) + 1
        return max(days_used, 1)

    def calculate_daily_cost(self, item: dict[str, Any]) -> float:
        """
        计算单个物品的日均使用价格。

        Args:
            item: 物品字典。

        Returns:
            日均使用价格。
        """
        days_used = self.calculate_days_used(item)

        if days_used > 0:
            daily_cost = item['price'] / days_used
        else:
            daily_cost = item['price']

        return daily_cost

    def get_total_assets(self) -> float:
        """
        计算所有物品的总资产。

        Returns:
            总资产金额。
        """
        total = sum(item['price'] for item in self.items)
        return total

    def get_average_daily_cost(self) -> float:
        """
        计算所有物品的日均总成本。

        Returns:
            日均总成本。
        """
        if not self.items:
            return 0.0

        total_daily_cost = sum(
            self.calculate_daily_cost(item) for item in self.items
        )
        return total_daily_cost
