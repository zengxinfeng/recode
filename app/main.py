import sys

from PySide6.QtWidgets import QApplication

from app.views.main import MainWindow


def main() -> int:
    """
    应用程序入口函数，初始化并运行主窗口。

    Returns:
        应用程序退出码，0 表示正常退出。
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
