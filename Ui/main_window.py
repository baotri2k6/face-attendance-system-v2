"""
Cửa sổ chính của ứng dụng
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QStackedWidget, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
from database.db_manager import DBManager
from Ui.components.sidebar import Sidebar
from Ui.components.header import Header
from Ui.page.home_page import HomePage
from Ui.page.student_page import StudentPage
from Ui.page.teacher_page import TeacherPage
from Ui.page.subject_page import SubjectPage
from Ui.page.session_page import SessionPage
from Ui.page.attendance_page import AttendancePage
from Ui.page.recognize_page import RecognizePage
from Ui.page.statistics_page import StatisticsPage
from Ui.page.photo_page import PhotoPage


class MainWindow(QMainWindow):
    def __init__(self, username="AdminSafe"):
        super().__init__()
        self.username = username
        self.db = DBManager()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        self.header = Header(username=self.username)
        self.header.logout_requested.connect(self._logout)
        root.addWidget(self.header)

        # Body: sidebar + content
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._change_page)
        body.addWidget(self.sidebar)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #e8eef5;")

        self.pages = {
            "home":       HomePage(self.db),
            "student":    StudentPage(self.db),
            "recognize":  RecognizePage(self.db),
            "attendance": AttendancePage(self.db),
            "subject":    SubjectPage(self.db),
            "teacher":    TeacherPage(self.db),
            "session":    SessionPage(self.db),
            "statistics": StatisticsPage(self.db),
            "photo":      PhotoPage(self.db),
        }

        # Wire home navigation
        self.pages["home"].navigate.connect(self._nav_from_home)

        for page in self.pages.values():
            self.stack.addWidget(page)

        body.addWidget(self.stack)
        root.addLayout(body)

    def _change_page(self, key):
        page = self.pages.get(key)
        if page:
            self.stack.setCurrentWidget(page)
            if hasattr(page, "refresh"):
                page.refresh()

    def _nav_from_home(self, key):
        self.sidebar._on_click(key)
        self._change_page(key)

    def _logout(self):
        reply = QMessageBox.question(self, "Đăng xuất", "Bạn có muốn đăng xuất?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            # Re-launch login
            from Ui.page.login_page import LoginPage
            self._login_win = LoginPage()
            self._login_win.login_success.connect(self._reopen)
            self._login_win.resize(800, 600)
            self._login_win.show()

    def _reopen(self, username):
        self._login_win.close()
        win = MainWindow(username)
        win.show()
        self._main_ref = win

    def closeEvent(self, event):
        # Stop any cameras
        if "recognize" in self.pages:
            rec = self.pages["recognize"]
            if hasattr(rec, "_stop"):
                rec._stop()
        super().closeEvent(event)
