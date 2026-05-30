"""
Header bar component
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime


class Header(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, username="Admin", parent=None):
        super().__init__(parent)
        self.username = username
        self.setFixedHeight(56)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a2035;
                border-bottom: 2px solid #2d3a55;
            }
        """)
        self._build_ui()

        self._timer = QTimer()
        self._timer.timeout.connect(self._update_time)
        self._timer.start(1000)

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        # ── Datetime box (trái) ──────────────────────────────
        datetime_box = QFrame()
        datetime_box.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 8px;
                padding: 0px 4px;
            }
        """)
        dt_layout = QHBoxLayout(datetime_box)
        dt_layout.setContentsMargins(10, 4, 10, 4)
        dt_layout.setSpacing(6)

        clock_icon = QLabel("🕐")
        clock_icon.setStyleSheet("background: transparent; border: none; font-size: 13px;")
        dt_layout.addWidget(clock_icon)

        self.lbl_datetime = QLabel()
        self.lbl_datetime.setStyleSheet("""
            background: transparent;
            border: none;
            color: #a0aec0;
            font-size: 11px;
        """)
        self._update_time()
        dt_layout.addWidget(self.lbl_datetime)
        layout.addWidget(datetime_box)

        layout.addStretch()

        # ── Title box (giữa) ─────────────────────────────────
        title_box = QFrame()
        title_box.setStyleSheet("""
            QFrame {
                background: rgba(255, 87, 34, 0.12);
                border: 1.5px solid rgba(255, 87, 34, 0.5);
                border-radius: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_box)
        title_layout.setContentsMargins(20, 6, 20, 6)

        title_lbl = QLabel("🎓  Hệ thống nhận diện khuôn mặt")
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("""
            background: transparent;
            border: none;
            color: #FF5722;
            font-size: 15px;
            font-weight: bold;
            letter-spacing: 0.5px;
        """)
        title_layout.addWidget(title_lbl)
        layout.addWidget(title_box)

        layout.addStretch()

        # ── User/logout box (phải) ───────────────────────────
        user_box = QFrame()
        user_box.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 8px;
            }
        """)
        user_layout = QHBoxLayout(user_box)
        user_layout.setContentsMargins(10, 4, 6, 4)
        user_layout.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet("background: transparent; border: none; color: #48bb78; font-size: 9px;")
        user_layout.addWidget(dot)

        user_lbl = QLabel(self.username)
        user_lbl.setStyleSheet("""
            background: transparent;
            border: none;
            color: #e2e8f0;
            font-size: 12px;
            font-weight: 600;
        """)
        user_layout.addWidget(user_lbl)

        sep = QLabel("|")
        sep.setStyleSheet("background: transparent; border: none; color: #4a5568; font-size: 12px;")
        user_layout.addWidget(sep)

        btn_logout = QPushButton("⎋ Đăng xuất")
        btn_logout.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #FF5722;
                font-size: 12px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #ff7043;
                text-decoration: underline;
            }
        """)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.clicked.connect(self.logout_requested.emit)
        user_layout.addWidget(btn_logout)

        layout.addWidget(user_box)

    def _update_time(self):
        now = datetime.now()
        self.lbl_datetime.setText(now.strftime("%I:%M %p  |  %d-%m-%Y"))