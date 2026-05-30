
"""
Modern Sidebar Navigation
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QGraphicsDropShadowEffect
)

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


NAV_ITEMS = [
    ("home",      "🏠", "Trang chủ"),
    ("student",   "👨‍🎓", "Sinh viên"),
    ("recognize", "👁", "Nhận diện"),
    ("attendance","📋", "Điểm danh"),
    ("subject",   "📚", "Môn học"),
    ("teacher",   "👨‍🏫", "Giáo viên"),
    ("session",   "📅", "Buổi học"),
    ("statistics","📊", "Thống kê"),
    ("photo",     "🖼", "Xem ảnh"),
]



SIDEBAR_STYLE = """

QWidget#Sidebar{
    background-color:#f8fafc;
    border-right:1px solid #e2e8f0;
}

/* =========================
   LOGO
========================= */

QLabel#logo{
    color:#1e293b;
    font-size:18px;
    font-weight:bold;
    padding:18px;
}

/* =========================
   MENU BUTTON
========================= */

QPushButton.nav-btn{

    background:transparent;

    color:#475569;

    border:none;

    border-radius:12px;

    padding:14px 16px;

    font-size:14px;

    font-weight:600;

    text-align:left;
}

/* Hover */

QPushButton.nav-btn:hover{

    background:#e0f2fe;

    color:#0284c7;
}

/* Active */

QPushButton.nav-btn[active="true"]{

    background:#dbeafe;

    color:#2563eb;

    border-left:4px solid #2563eb;
}
"""


class Sidebar(QWidget):

    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setObjectName("Sidebar")

        # sidebar rộng hơn
        self.setFixedWidth(230)

        self.setStyleSheet(SIDEBAR_STYLE)

        self._buttons = {}

        self._current = "home"

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(12, 15, 12, 15)

        layout.setSpacing(8)

        # =========================
        # LOGO
        # =========================

        logo = QLabel("🎓 Face Attendance")

        logo.setObjectName("logo")

        logo.setAlignment(Qt.AlignCenter)

        layout.addWidget(logo)

        # =========================
        # MENU BUTTONS
        # =========================

        for key, icon, label in NAV_ITEMS:

            btn = QPushButton(f"{icon}   {label}")

            btn.setProperty("class", "nav-btn")

            btn.setProperty("active", "false")

            btn.setFixedHeight(50)

            btn.setCursor(Qt.PointingHandCursor)

            btn.clicked.connect(
                lambda _, k=key: self._on_click(k)
            )

            # shadow nhẹ
            shadow = QGraphicsDropShadowEffect()

            shadow.setBlurRadius(15)

            shadow.setXOffset(0)

            shadow.setYOffset(2)

            btn.setGraphicsEffect(shadow)

            self._buttons[key] = btn

            layout.addWidget(btn)

        layout.addStretch()

        self._set_active("home")

    def _on_click(self, key):

        self._set_active(key)

        self.page_changed.emit(key)

    def _set_active(self, key):

        for k, btn in self._buttons.items():

            active = "true" if k == key else "false"

            btn.setProperty("active", active)

            btn.style().unpolish(btn)

            btn.style().polish(btn)

        self._current = key

