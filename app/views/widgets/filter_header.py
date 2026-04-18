"""
带筛选图标的表头组件。

在指定列的表头右侧绘制筛选图标，点击后发出信号。
"""

from typing import Any, Optional

from PySide6.QtCore import QPointF, Qt, QRect, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QHeaderView, QTableWidget, QWidget


class FilterHeader(QHeaderView):
    """
    带筛选图标的表头控件。

    仅在指定列（默认为第1列）显示筛选图标。

    Signals:
        filter_clicked: 筛选图标被点击，参数为列索引。
    """

    filter_clicked = Signal(int)

    FILTER_COLUMN = 1
    ICON_SIZE = 16
    ICON_MARGIN = 10

    def __init__(self, table: QTableWidget, parent: Optional[QWidget] = None) -> None:
        """
        初始化过滤表头。

        Args:
            table: 关联的表格控件。
            parent: 父部件。
        """
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._table = table
        self._has_active_filter = False
        self._hover_filter = False
        self.setSectionsClickable(True)

    def set_filter_active(self, active: bool) -> None:
        """
        设置是否有激活的筛选。

        Args:
            active: 是否有激活的筛选。
        """
        if self._has_active_filter != active:
            self._has_active_filter = active
            self.viewport().update()

    def has_active_filter(self) -> bool:
        """
        检查是否有激活的筛选。

        Returns:
            是否有激活的筛选。
        """
        return self._has_active_filter

    def paintSection(
        self, painter: QPainter, rect: QRectF, logical_index: int
    ) -> None:
        """
        绘制表头区域。

        Args:
            painter: 绘制器。
            rect: 绘制区域。
            logical_index: 逻辑列索引。
        """
        painter.save()
        super().paintSection(painter, rect, logical_index)
        painter.restore()

        if logical_index == self.FILTER_COLUMN:
            self._draw_filter_icon(painter, rect)

    def _draw_filter_icon(self, painter: QPainter, rect: QRectF) -> None:
        """
        绘制筛选图标（简洁漏斗形状）。

        Args:
            painter: 绘制器。
            rect: 表头区域。
        """
        icon_x = rect.right() - self.ICON_SIZE - self.ICON_MARGIN
        icon_y = rect.center().y()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 计算漏斗的各个点
        top_width = self.ICON_SIZE
        bottom_width = self.ICON_SIZE * 0.35
        height = self.ICON_SIZE * 0.8
        stem_height = height * 0.25

        # 漏斗形状的顶点
        top_left = QPointF(icon_x, icon_y - height / 2)
        top_right = QPointF(icon_x + top_width, icon_y - height / 2)
        mid_left = QPointF(
            icon_x + (top_width - bottom_width) / 2,
            icon_y + height / 2 - stem_height,
        )
        mid_right = QPointF(
            icon_x + (top_width + bottom_width) / 2,
            icon_y + height / 2 - stem_height,
        )
        bottom_left = QPointF(
            icon_x + (top_width - bottom_width * 0.5) / 2,
            icon_y + height / 2,
        )
        bottom_right = QPointF(
            icon_x + (top_width + bottom_width * 0.5) / 2,
            icon_y + height / 2,
        )

        # 创建漏斗多边形
        funnel = QPolygonF(
            [
                top_left,
                top_right,
                mid_right,
                bottom_right,
                bottom_left,
                mid_left,
            ]
        )

        if self._has_active_filter:
            # 激活状态：简洁的填充漏斗
            painter.setBrush(QColor("#A855F7"))
            painter.setPen(QPen(QColor("#C084FC"), 1.2))
            painter.drawPolygon(funnel)
        else:
            # 非激活状态
            if self._hover_filter:
                # 悬停状态：浅色填充
                painter.setBrush(QColor(168, 85, 247, 25))
                painter.setPen(QPen(QColor("#A855F7"), 1.2))
            else:
                # 默认状态：空心
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(QColor("#9CA3AF"), 1.2))
            painter.drawPolygon(funnel)

        painter.restore()

    def _get_icon_rect(self, rect: QRectF) -> QRectF:
        """
        获取图标点击区域。

        Args:
            rect: 表头区域。

        Returns:
            图标点击区域。
        """
        icon_x = rect.right() - self.ICON_SIZE - self.ICON_MARGIN - 6
        icon_y = rect.top()
        return QRectF(icon_x, icon_y, self.ICON_SIZE + 12, rect.height())

    def _get_section_rect(self, logical_index: int) -> QRect:
        """
        获取指定列的区域矩形。

        Args:
            logical_index: 逻辑列索引。

        Returns:
            列的区域矩形。
        """
        x = self.sectionViewportPosition(logical_index)
        width = self.sectionSize(logical_index)
        height = self.height()
        return QRect(x, 0, width, height)

    def mousePressEvent(self, event: Optional[Any]) -> None:
        """
        鼠标按下事件处理。

        Args:
            event: 鼠标事件。
        """
        if event is None:
            return

        pos = event.position()
        logical_index = self.logicalIndexAt(pos.toPoint())

        if logical_index == self.FILTER_COLUMN:
            rect = self._get_section_rect(logical_index)
            icon_rect = self._get_icon_rect(QRectF(rect))

            if icon_rect.contains(pos):
                self.filter_clicked.emit(logical_index)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Optional[Any]) -> None:
        """
        鼠标移动事件处理。

        Args:
            event: 鼠标事件。
        """
        if event is None:
            return

        pos = event.position()
        logical_index = self.logicalIndexAt(pos.toPoint())

        if logical_index == self.FILTER_COLUMN:
            rect = self._get_section_rect(logical_index)
            icon_rect = self._get_icon_rect(QRectF(rect))

            if icon_rect.contains(pos):
                if not self._hover_filter:
                    self._hover_filter = True
                    self.viewport().update()
            else:
                if self._hover_filter:
                    self._hover_filter = False
                    self.viewport().update()
        else:
            if self._hover_filter:
                self._hover_filter = False
                self.viewport().update()

        super().mouseMoveEvent(event)

    def leaveEvent(self, event: Optional[Any]) -> None:
        """
        鼠标离开事件处理。

        Args:
            event: 事件。
        """
        if self._hover_filter:
            self._hover_filter = False
            self.viewport().update()
        super().leaveEvent(event)
