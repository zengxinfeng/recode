"""
主窗口模块。

提供应用程序主窗口，负责主题管理、导航和视图切换。
"""

import ctypes
import sys
from typing import Any, Optional

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.models.clothing_manager import ClothingManager
from app.models.item_manager import ItemManager
from app.utils.path_utils import get_dark_style_path, get_main_style_path
from app.views.base_management_view import STATUS_MESSAGE_DURATION
from app.views.clothing_management_view import ClothingManagementView
from app.views.item_management_view import ItemManagementView


WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1000
WINDOW_DEFAULT_HEIGHT = 750
NAV_WIDTH = 220


class MainWindow(QMainWindow):
    """
    应用程序主窗口。

    负责主题管理、导航栏、状态栏和视图切换协调。
    """

    def __init__(self) -> None:
        """初始化主窗口。"""
        super().__init__()
        self.current_theme: str = 'dark'
        self.item_manager: ItemManager = ItemManager()
        self.clothing_manager: ClothingManager = ClothingManager()
        self.item_view: Optional[ItemManagementView] = None
        self.clothing_view: Optional[ClothingManagementView] = None

        self.load_styles()
        self.init_ui()

    def showEvent(self, event: Any) -> None:
        """
        窗口显示事件处理。

        Args:
            event: Qt 显示事件对象。
        """
        super().showEvent(event)
        self.update_title_bar_color()

    def load_styles(self) -> None:
        """加载和应用 QSS 样式。"""
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
        """更新窗口标题栏颜色（仅 Windows 系统）。"""
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
        """切换主题。"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.load_styles()
        theme_name = "暗黑" if self.current_theme == "dark" else "明亮"
        self.statusBar.showMessage(
            f'已切换到{theme_name}主题', STATUS_MESSAGE_DURATION
        )

    def init_ui(self) -> None:
        """初始化用户界面。"""
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
        self._create_item_view()

        main_layout.addWidget(nav_widget)
        main_layout.addWidget(content_widget)

    def switch_view(self, item: QListWidgetItem) -> None:
        """
        切换不同的记录管理视图。

        Args:
            item: 点击的导航项。
        """
        view_name = item.text()
        if '物品记录管理' in view_name:
            if self.clothing_view:
                self.clothing_view.hide_view()
            self._create_item_view()
            self.item_view.show_view()
        elif '衣物记录管理' in view_name:
            if self.item_view:
                self.item_view.hide_view()
            self._create_clothing_view()
            self.clothing_view.show_view()

    def _create_nav_widget(self) -> QWidget:
        """创建导航侧边栏部件。"""
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
        self.nav_list.setStyleSheet(
            "QListWidget { border-radius: 0 0 12px 12px; }"
        )

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
        """创建内容区域部件。"""
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(20, 0, 20, 0)
        return content_widget

    def _create_status_bar(self) -> None:
        """创建状态栏。"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.status_label = QLabel('✅ 就绪')
        self.status_label.setObjectName("statusLabel")

        self.item_count_status = QLabel('📦 物品数量: 0')
        self.item_count_status.setObjectName("itemCountStatus")

        self.statusBar.addWidget(self.status_label)
        self.statusBar.addPermanentWidget(self.item_count_status)

    def _create_item_view(self) -> None:
        """创建物品管理视图。"""
        if self.item_view is not None:
            return

        self.item_view = ItemManagementView(self.item_manager, self)
        self.item_view.set_status_bar(self.statusBar)
        self.item_view._on_stats_updated = self._on_item_stats_updated
        self.content_layout.addWidget(self.item_view)
        self.item_view.show_view()

    def _create_clothing_view(self) -> None:
        """创建衣物管理视图。"""
        if self.clothing_view is not None:
            return

        self.clothing_view = ClothingManagementView(
            self.clothing_manager, self
        )
        self.clothing_view.set_status_bar(self.statusBar)
        self.content_layout.addWidget(self.clothing_view)
        self.clothing_view.hide()

    def _on_item_stats_updated(self, item_count: int) -> None:
        """
        物品统计更新回调。

        Args:
            item_count: 当前物品数量。
        """
        self.item_count_status.setText(f'📦 物品数量: {item_count}')
