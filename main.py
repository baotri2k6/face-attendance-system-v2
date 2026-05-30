"""
Điểm khởi động chính của ứng dụng Hệ thống nhận diện khuôn mặt
"""
import sys
import os

# Thêm thư mục gốc vào path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QFont, QFontDatabase
    from PyQt5.QtCore import QLibraryInfo
except ModuleNotFoundError as exc:
    if exc.name == "PyQt5":
        print(
            "Chua cai PyQt5 trong Python dang chay.\n"
            "Hay chay bang moi truong ao cua project:\n"
            "  source venv/bin/activate\n"
            "  python main.py\n"
            "Hoac cai thu vien:\n"
            "  python -m pip install -r requirements.txt"
        )
        sys.exit(1)
    raise

from Ui.page.login_page import LoginPage
from Ui.main_window import MainWindow


def _configure_qt_plugins():
    """
    opencv-python co kem Qt plugin rieng va co the ghi de bien moi truong
    QT_QPA_PLATFORM_PLUGIN_PATH khi import cv2. PyQt5 can dung plugin cua
    chinh PyQt5, neu khong app se loi "Could not load ... xcb".
    """
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
        QLibraryInfo.PluginsPath
    )
    if (
        os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
        and "QT_QPA_PLATFORM" not in os.environ
    ):
        os.environ["QT_QPA_PLATFORM"] = "wayland"


class App:
    def __init__(self):
        _configure_qt_plugins()
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Hệ thống nhận diện khuôn mặt")

        # Font mặc định
        QFontDatabase.addApplicationFont("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf")
        QFont.insertSubstitution("Segoe UI", "Noto Sans")
        QFont.insertSubstitution("Arial", "Noto Sans")
        QFont.insertSubstitution("Sans Serif", "Noto Sans")
        font = QFont("Noto Sans", 10)
        font.setStyleStrategy(QFont.PreferAntialias)
        self.app.setFont(font)

        self.main_win = None
        self._show_login()

    def _show_login(self):
        self.login = LoginPage()
        self.login.login_success.connect(self._on_login)
        self.login.setWindowTitle("Đăng nhập - Hệ thống nhận diện khuôn mặt")
        self.login.resize(900, 600)
        self.login.show()

    def _on_login(self, username):
        self.login.close()
        self.main_win = MainWindow(username=username)
        self.main_win.show()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = App()
    app.run()
