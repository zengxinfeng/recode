"""
停用对话框组件。

用于记录物品停用日期和原因。
"""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from app.views.widgets.date_input import DateInput

DISCONTINUE_REASONS = ['报废', '转卖', '闲置', '其他']


class DiscontinueDialog(QDialog):
    """
    停用对话框，用于输入停用日期和原因。
    """

    def __init__(self, parent=None, item_name: str = '') -> None:
        """
        初始化停用对话框。

        Args:
            parent: 父窗口。
            item_name: 物品名称，用于显示在标题中。
        """
        super().__init__(parent)
        self.setWindowTitle(f'停用物品 - {item_name}' if item_name else '停用物品')
        self.setMinimumWidth(350)
        self._init_ui()

    def _init_ui(self) -> None:
        """
        初始化界面组件。
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.date_input = DateInput()
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow('停用日期:', self.date_input)

        self.reason_combo = QComboBox()
        self.reason_combo.addItems(DISCONTINUE_REASONS)
        self.reason_combo.currentTextChanged.connect(self._on_reason_changed)
        form_layout.addRow('停用原因:', self.reason_combo)

        self.other_reason_input = QLineEdit()
        self.other_reason_input.setPlaceholderText('请输入停用原因')
        self.other_reason_input.setVisible(False)
        form_layout.addRow('', self.other_reason_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _on_reason_changed(self, reason: str) -> None:
        """
        处理停用原因选择变化。

        Args:
            reason: 当前选择的原因。
        """
        self.other_reason_input.setVisible(reason == '其他')
        if reason != '其他':
            self.other_reason_input.clear()

    def get_discontinue_date(self) -> QDate:
        """
        获取停用日期。

        Returns:
            停用日期（QDate 对象）。
        """
        return self.date_input.date()

    def get_discontinue_reason(self) -> str:
        """
        获取停用原因。

        Returns:
            停用原因字符串。
        """
        reason = self.reason_combo.currentText()
        if reason == '其他':
            custom_reason = self.other_reason_input.text().strip()
            return custom_reason if custom_reason else '其他'
        return reason
