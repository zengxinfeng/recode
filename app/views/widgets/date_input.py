from typing import Optional

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtWidgets import (
    QCalendarWidget,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


CALENDAR_DIALOG_WIDTH = 340
CALENDAR_DIALOG_HEIGHT = 380
CALENDAR_BUTTON_SIZE = 36
YEAR_RANGE_MIN = 1900
YEAR_RANGE_MAX = 2100

MONTH_NAMES = [
    '1月', '2月', '3月', '4月', '5月', '6月',
    '7月', '8月', '9月', '10月', '11月', '12月',
]

YEAR_LIST = list(reversed([str(year) for year in range(YEAR_RANGE_MIN, YEAR_RANGE_MAX + 1)]))


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
        self._dialog: Optional[QDialog] = None
        self._calendar: Optional[QCalendarWidget] = None
        self._year_combo: Optional[QComboBox] = None
        self._month_combo: Optional[QComboBox] = None
        self._pending_date: Optional[QDate] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置用户界面布局和控件。"""
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

        self.calendar_button = QPushButton("📅")
        self.calendar_button.setObjectName("calendarButton")
        self.calendar_button.setFixedSize(CALENDAR_BUTTON_SIZE, CALENDAR_BUTTON_SIZE)
        self.calendar_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.calendar_button.clicked.connect(self.show_calendar)
        layout.addWidget(self.calendar_button)

    def _on_line_edit_click(self, event: Optional[QMouseEvent]) -> None:
        """
        处理文本框点击事件。

        Args:
            event: 鼠标事件对象。
        """
        if event is not None and event.button() == Qt.MouseButton.LeftButton:
            self.show_calendar()

    def show_calendar(self) -> None:
        """显示日历对话框供用户选择日期。"""
        self._dialog = QDialog(self)
        self._dialog.setWindowTitle('选择日期')
        self._dialog.setModal(True)
        self._dialog.setFixedSize(CALENDAR_DIALOG_WIDTH, CALENDAR_DIALOG_HEIGHT)

        layout = QVBoxLayout(self._dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        nav_row = self._create_nav_row()
        layout.addLayout(nav_row)

        self._calendar = QCalendarWidget()
        self._calendar.setSelectedDate(self._current_date)
        self._calendar.setGridVisible(True)
        self._calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        self._calendar.setHorizontalHeaderFormat(
            QCalendarWidget.HorizontalHeaderFormat.ShortDayNames
        )
        self._calendar.clicked.connect(self._on_calendar_date_clicked)
        self._calendar.currentPageChanged.connect(self._on_page_changed)

        navbar = self._calendar.findChild(QWidget, "qt_calendar_navigationbar")
        if navbar is not None:
            navbar.hide()

        layout.addWidget(self._calendar)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        today_button = QPushButton("今天")
        today_button.setObjectName("calendarTodayButton")
        today_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        today_button.clicked.connect(self._on_today_clicked)
        button_row.addWidget(today_button)

        button_row.addStretch()

        confirm_button = QPushButton("确定")
        confirm_button.setObjectName("calendarConfirmButton")
        confirm_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        confirm_button.clicked.connect(self._on_confirm_clicked)
        button_row.addWidget(confirm_button)

        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("calendarCancelButton")
        cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_button.clicked.connect(self._on_cancel_clicked)
        button_row.addWidget(cancel_button)

        layout.addLayout(button_row)

        self._pending_date = None
        self._sync_nav_to_calendar()
        self._dialog.exec()

    def _create_nav_row(self) -> QHBoxLayout:
        """创建自定义年月导航行。"""
        nav_row = QHBoxLayout()
        nav_row.setSpacing(6)

        prev_button = QPushButton("◀")
        prev_button.setObjectName("calendarNavButton")
        prev_button.setFixedSize(32, 32)
        prev_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        prev_button.clicked.connect(self._on_prev_month)
        nav_row.addWidget(prev_button)

        self._month_combo = QComboBox()
        self._month_combo.setObjectName("calendarMonthCombo")
        self._month_combo.addItems(MONTH_NAMES)
        self._month_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._month_combo.currentIndexChanged.connect(self._on_nav_changed)
        nav_row.addWidget(self._month_combo, 1)
        
        self._year_combo = QComboBox()
        self._year_combo.setObjectName("calendarYearCombo")
        self._year_combo.addItems(YEAR_LIST)
        self._year_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._year_combo.currentIndexChanged.connect(self._on_nav_changed)
        nav_row.addWidget(self._year_combo, 1)

        next_button = QPushButton("▶")
        next_button.setObjectName("calendarNavButton")
        next_button.setFixedSize(32, 32)
        next_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        next_button.clicked.connect(self._on_next_month)
        nav_row.addWidget(next_button)

        return nav_row

    def _sync_nav_to_calendar(self) -> None:
        """将导航控件同步到日历当前页面。"""
        if self._calendar is None:
            return
        year = self._calendar.yearShown()
        month = self._calendar.monthShown()
        if self._year_combo is not None:
            self._year_combo.blockSignals(True)
            year_index = YEAR_RANGE_MAX - year
            if 0 <= year_index < len(YEAR_LIST):
                self._year_combo.setCurrentIndex(year_index)
            self._year_combo.blockSignals(False)
        if self._month_combo is not None:
            self._month_combo.blockSignals(True)
            self._month_combo.setCurrentIndex(month - 1)
            self._month_combo.blockSignals(False)

    def _on_nav_changed(self) -> None:
        """处理年月导航控件值变化。"""
        if self._calendar is None or self._year_combo is None or self._month_combo is None:
            return
        year = YEAR_RANGE_MIN + self._year_combo.currentIndex()
        month = self._month_combo.currentIndex() + 1
        self._calendar.setCurrentPage(year, month)

    def _on_page_changed(self, year: int, month: int) -> None:
        """
        处理日历页面变化，同步导航控件。

        Args:
            year: 当前显示年份。
            month: 当前显示月份。
        """
        if self._year_combo is not None:
            self._year_combo.blockSignals(True)
            year_index = YEAR_RANGE_MAX - year
            if 0 <= year_index < len(YEAR_LIST):
                self._year_combo.setCurrentIndex(year_index)
            self._year_combo.blockSignals(False)
        if self._month_combo is not None:
            self._month_combo.blockSignals(True)
            self._month_combo.setCurrentIndex(month - 1)
            self._month_combo.blockSignals(False)

    def _on_prev_month(self) -> None:
        """切换到上一个月。"""
        if self._calendar is None:
            return
        year = self._calendar.yearShown()
        month = self._calendar.monthShown()
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        self._calendar.setCurrentPage(year, month)

    def _on_next_month(self) -> None:
        """切换到下一个月。"""
        if self._calendar is None:
            return
        year = self._calendar.yearShown()
        month = self._calendar.monthShown()
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        self._calendar.setCurrentPage(year, month)

    def _on_calendar_date_clicked(self, date: QDate) -> None:
        """
        处理日历日期点击事件，记录待确认日期。

        Args:
            date: 用户点击的日期。
        """
        self._pending_date = date
        self._calendar.setSelectedDate(date)

    def _on_today_clicked(self) -> None:
        """处理"今天"按钮点击，跳转到今天并选中。"""
        today = QDate.currentDate()
        self._pending_date = today
        if self._calendar is not None:
            self._calendar.setSelectedDate(today)
            self._calendar.setCurrentPage(today.year(), today.month())

    def _on_confirm_clicked(self) -> None:
        """处理"确定"按钮点击，确认选择并关闭对话框。"""
        if self._calendar is not None:
            selected = self._pending_date or self._calendar.selectedDate()
            self.setDate(selected)
            self.date_selected.emit(selected)
        if self._dialog is not None:
            self._dialog.accept()

    def _on_cancel_clicked(self) -> None:
        """处理"取消"按钮点击，放弃选择并关闭对话框。"""
        if self._dialog is not None:
            self._dialog.reject()

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
