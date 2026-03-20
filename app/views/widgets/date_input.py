from typing import Optional

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


CALENDAR_DIALOG_WIDTH = 300
CALENDAR_DIALOG_HEIGHT = 280
CALENDAR_BUTTON_SIZE = 32


class DateInput(QWidget):
    """
    自定义日期输入框，点击时弹出日历选择界面。

    提供一个只读的文本框和一个日历按钮，用户点击后弹出日历对话框选择日期。

    Signals:
        date_selected: 当用户选择日期后发出，携带选中的 QDate 对象。
    """

    date_selected = Signal(QDate)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        初始化日期输入框。

        Args:
            parent: 父部件，可选。
        """
        super().__init__(parent)
        self.setObjectName("dateInputContainer")
        self._current_date: QDate = QDate.currentDate()

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        设置用户界面布局和控件。
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.line_edit = QLineEdit()
        self.line_edit.setObjectName("dateInput")
        self.line_edit.setReadOnly(True)
        self.line_edit.setText(self._current_date.toString('yyyy-MM-dd'))
        self.line_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.line_edit.mousePressEvent = self._on_line_edit_click
        layout.addWidget(self.line_edit)

    def _on_line_edit_click(self, event: Optional[QMouseEvent]) -> None:
        """
        处理文本框点击事件。

        Args:
            event: 鼠标事件对象。
        """
        if event is not None and event.button() == Qt.MouseButton.LeftButton:
            self.show_calendar()

    def show_calendar(self) -> None:
        """
        显示日历对话框供用户选择日期。
        """
        dialog = QDialog(self)
        dialog.setWindowTitle('选择日期')
        dialog.setModal(True)
        dialog.setFixedSize(CALENDAR_DIALOG_WIDTH, CALENDAR_DIALOG_HEIGHT)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)

        calendar = QCalendarWidget()
        calendar.setSelectedDate(self._current_date)
        calendar.setGridVisible(True)
        calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        layout.addWidget(calendar)

        calendar.clicked.connect(self._on_calendar_date_clicked)

        dialog.exec()

    def _on_calendar_date_clicked(self, date: QDate) -> None:
        """
        处理日历日期点击事件。

        Args:
            date: 用户选择的日期。
        """
        self.setDate(date)
        self.date_selected.emit(date)

    def setDate(self, date: QDate) -> None:
        """
        设置当前日期并更新显示。

        Args:
            date: 要设置的日期。
        """
        self._current_date = date
        self.line_edit.setText(date.toString('yyyy-MM-dd'))

    def date(self) -> QDate:
        """
        获取当前选择的日期。

        Returns:
            当前选择的 QDate 对象。
        """
        return self._current_date
