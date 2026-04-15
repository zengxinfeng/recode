"""
多选过滤弹窗组件。

提供 Excel 风格的列过滤功能，支持多选和实时过滤。
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)


class FilterPopup(QWidget):
    """
    Excel 风格的列过滤弹窗，支持多选和实时过滤。

    Signals:
        filter_applied: 筛选应用信号，参数为选中的值列表。
    """

    filter_applied = Signal(list)

    def __init__(
        self,
        values: list[str],
        selected: Optional[list[str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        初始化过滤弹窗。

        Args:
            values: 可选值列表。
            selected: 已选中的值列表，默认为全部选中。
            parent: 父部件。
        """
        super().__init__(parent, Qt.WindowType.Popup)
        self._values = values
        self._selected = selected if selected is not None else values.copy()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置界面布局。"""
        self.setObjectName("filterPopup")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        self._create_select_all(layout)
        self._create_separator(layout)
        self._create_list_widget(layout)

        self._update_select_all_state()

    def _create_select_all(self, layout: QVBoxLayout) -> None:
        """创建全选复选框。"""
        self._select_all_cb = QCheckBox('全选')
        self._select_all_cb.stateChanged.connect(self._on_select_all_changed)
        layout.addWidget(self._select_all_cb)

    def _create_separator(self, layout: QVBoxLayout) -> None:
        """创建分隔线。"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("filterSeparator")
        layout.addWidget(line)

    def _create_list_widget(self, layout: QVBoxLayout) -> None:
        """创建选项列表。"""
        self._list_widget = QListWidget()
        self._list_widget.setObjectName("filterList")
        self._list_widget.setMaximumHeight(240)

        for value in self._values:
            item = QListWidgetItem(value)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            check_state = (
                Qt.CheckState.Checked
                if value in self._selected
                else Qt.CheckState.Unchecked
            )
            item.setCheckState(check_state)
            self._list_widget.addItem(item)

        self._list_widget.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._list_widget)

    def _on_select_all_changed(self, state: int) -> None:
        """全选复选框状态改变处理。"""
        check_state = Qt.CheckState(state)
        self._list_widget.blockSignals(True)
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            item.setCheckState(check_state)
        self._list_widget.blockSignals(False)

        self._emit_filter()

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        """列表项状态改变处理。"""
        self._update_select_all_state()
        self._emit_filter()

    def _update_select_all_state(self) -> None:
        """更新全选复选框状态。"""
        all_checked = True
        any_checked = False

        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                any_checked = True
            else:
                all_checked = False

        self._select_all_cb.blockSignals(True)
        if all_checked:
            self._select_all_cb.setCheckState(Qt.CheckState.Checked)
        elif any_checked:
            self._select_all_cb.setCheckState(Qt.CheckState.PartiallyChecked)
        else:
            self._select_all_cb.setCheckState(Qt.CheckState.Unchecked)
        self._select_all_cb.blockSignals(False)

    def _emit_filter(self) -> None:
        """发出筛选信号。"""
        selected = self.get_selected()
        self.filter_applied.emit(selected)

    def get_selected(self) -> list[str]:
        """
        获取当前选中的值列表。

        Returns:
            选中的值列表。
        """
        selected = []
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected
