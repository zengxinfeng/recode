"""
衣物管理模块。

负责衣物数据的存储、加载、添加、删除和计算功能。
"""

import json
from pathlib import Path
from typing import Any, Literal

from PySide6.QtCore import QDate

from app.utils.path_utils import get_clothing_file_path

ClothingStatus = Literal['active', 'discontinued']
DiscontinueReason = Literal['报废', '转卖', '闲置', '其他']

DISCONTINUE_REASONS: list[DiscontinueReason] = ['报废', '转卖', '闲置', '其他']


class ClothingManager:
    """
    衣物管理类，负责数据的存储、加载、添加、删除和计算。

    Attributes:
        items: 衣物列表，每个衣物为包含名称、类型、价格和购买日期的字典。
        save_path: 数据文件的保存路径。
    """

    def __init__(self) -> None:
        """
        初始化衣物管理器。

        设置保存路径，确保目录存在，并加载已保存的数据。
        """
        self.items: list[dict[str, Any]] = []
        self.save_path: Path = get_clothing_file_path()
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        self.load_data()

    def load_data(self) -> None:
        """
        从本地文件加载衣物数据。

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
        将衣物数据保存到本地文件。
        """
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

    def add_item(
        self, name: str, clothing_type: str, price: float, purchase_date: QDate
    ) -> None:
        """
        添加新衣物到列表。

        Args:
            name: 衣物名称。
            clothing_type: 衣物类型。
            price: 购买价格。
            purchase_date: 购买日期（QDate 对象）。
        """
        item = {
            'name': name,
            'clothing_type': clothing_type,
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
        根据索引删除衣物。

        Args:
            index: 要删除的衣物索引。
        """
        if 0 <= index < len(self.items):
            del self.items[index]
            self.save_data()

    def update_item(
        self, index: int, name: str, clothing_type: str, price: float, purchase_date: QDate
    ) -> None:
        """
        根据索引更新衣物信息。

        Args:
            index: 要更新的衣物索引。
            name: 新的衣物名称。
            clothing_type: 新的衣物类型。
            price: 新的购买价格。
            purchase_date: 新的购买日期（QDate 对象）。
        """
        if 0 <= index < len(self.items):
            existing_item = self.items[index]
            self.items[index] = {
                'name': name,
                'clothing_type': clothing_type,
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
        将衣物标记为已停用。

        Args:
            index: 要停用的衣物索引。
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
        将已停用的衣物重新启用。

        Args:
            index: 要重新启用的衣物索引。
        """
        if 0 <= index < len(self.items):
            self.items[index]['status'] = 'active'
            self.items[index]['discontinued_date'] = None
            self.items[index]['discontinued_reason'] = None
            self.save_data()

    def get_items(self) -> list[dict[str, Any]]:
        """
        获取所有衣物列表。

        Returns:
            衣物列表。
        """
        return self.items

    def get_all_clothing_types(self) -> list[str]:
        """
        获取所有不重复的衣物类型列表。

        Returns:
            衣物类型列表。
        """
        types = set()
        for item in self.items:
            if item.get('clothing_type'):
                types.add(item['clothing_type'])
        return sorted(list(types))

    def calculate_days_used(self, item: dict[str, Any]) -> int:
        """
        计算衣物已使用天数。

        Args:
            item: 衣物字典。

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

    def get_total_assets(self) -> float:
        """
        计算所有衣物的总资产。

        Returns:
            总资产金额。
        """
        total = sum(item['price'] for item in self.items)
        return total
