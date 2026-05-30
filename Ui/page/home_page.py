"""
Trang chủ - Dashboard với các card điều hướng nhanh
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


CARD_STYLE = """
QPushButton.home-card {
    background: #f0f4f8;
    border: none;
    border-radius: 12px;
    color: #2d3748;
    font-size: 13px;
    font-weight: 500;
    padding: 20px;
    text-align: center;
}
QPushButton.home-card:hover {
    background: #e2e8f0;
    border: 1.5px solid #FF5722;
}
QPushButton.home-card:pressed {
    background: #cbd5e0;
}
"""


"""
Modern Dashboard Home Page
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect
)

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


HOME_CARDS = [
    ("student",    "👨‍🎓", "Sinh viên"),
    ("recognize",  "👁",   "Nhận diện"),
    ("attendance", "📋",   "Điểm danh"),
    ("subject",    "📚",   "Môn học"),
    ("statistics", "📊",   "Thống kê"),
    ("session",    "📅",   "Buổi học"),
    ("teacher",    "👨‍🏫", "Giáo viên"),
    ("photo",      "🖼",   "Xem ảnh"),
]


class HomePage(QWidget):

    navigate = pyqtSignal(str)

    def __init__(self, db, parent=None):

        super().__init__(parent)

        self.db = db

        self.setStyleSheet("""

        QWidget{
            background:#eef2f7;
        }

        QLabel#title{
            font-size:28px;
            font-weight:bold;
            color:#0f172a;
        }

        QLabel#subtitle{
            font-size:14px;
            color:#64748b;
        }

        QFrame#stat-card{
            background:#ffffff;
            border-radius:18px;
            border:1px solid #e2e8f0;
        }

        QPushButton#feature-card{
            background:white;
            border-radius:28px;
            border:1px solid #e2e8f0;
        }

        QPushButton#feature-card:hover{
         background:#eff6ff;
         border:1px solid #93c5fd;
     } 

        QLabel#number{
            font-size:28px;
            font-weight:bold;
            color:#0f172a;
        }

        QLabel#label{
            font-size:13px;
            color:#64748b;
        }

        QLabel#feature-icon{
            font-size:52px;
        }

        QLabel#feature-text{
            font-size:17px;
            font-weight:600;
            color:#1e293b;
        }

        """)

        self._build_ui()

    def _build_ui(self):

        outer = QVBoxLayout(self)

        outer.setContentsMargins(20, 5, 20, 20)

        outer.setSpacing(12)

        # =========================
        # TITLE
        # =========================

    

        # =========================
        # STATS
        # =========================

        stats = self.db.get_attendance_stats()

        stat_row = QHBoxLayout()

        stat_row.setSpacing(15)

        stat_data = [
            ("👨‍🎓", str(stats["total_students"]), "Sinh viên"),
            ("📚", str(stats["total_subjects"]), "Môn học"),
            ("📅", str(stats["total_sessions"]), "Buổi học"),
            ("✅", str(stats["total_attendance"]), "Điểm danh"),
        ]

        for icon, val, label in stat_data:

            stat_row.addWidget(
                self._create_stat_card(icon, val, label)
            )

        outer.addLayout(stat_row)
        outer.addSpacing(25)

        # =========================
        # FEATURE GRID
        # =========================

        grid = QGridLayout()

        grid.setSpacing(22)

        for i, (key, icon, text) in enumerate(HOME_CARDS):

            card = self._create_feature_card(
                key,
                icon,
                text
            )

            grid.addWidget(card, i // 4, i % 4)

        outer.addLayout(grid)

        outer.addStretch()

        # =========================
        # FOOTER
        # =========================

        footer = QLabel("Face Attendance System © 2026")

        footer.setAlignment(Qt.AlignCenter)

        footer.setStyleSheet("""
            color:#94a3b8;
            font-size:12px;
        """)

        outer.addWidget(footer)

    # =====================================================
    # STAT CARD
    # =====================================================

    def _create_stat_card(self, icon, value, label):

        card = QFrame()

        card.setObjectName("stat-card")

        card.setFixedHeight(95)

        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(18)

        shadow.setXOffset(0)

        shadow.setYOffset(3)

        shadow.setColor(QColor(0, 0, 0, 30))

        card.setGraphicsEffect(shadow)

        layout = QHBoxLayout(card)

        layout.setContentsMargins(18, 15, 18, 15)

        layout.setSpacing(15)

        ico = QLabel(icon)

        ico.setStyleSheet("""
            font-size:38px;
        """)

        layout.addWidget(ico)

        txt = QVBoxLayout()

        number = QLabel(value)

        number.setObjectName("number")

        text = QLabel(label)

        text.setObjectName("label")

        txt.addWidget(number)

        txt.addWidget(text)

        layout.addLayout(txt)

        layout.addStretch()

        return card

    # =====================================================
    # FEATURE CARD
    # =====================================================

    def _create_feature_card(self, key, icon, text):

        card = QPushButton()

        card.setObjectName("feature-card")

        card.setCursor(Qt.PointingHandCursor)

        card.setFixedSize(210, 210)

        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(30)

        shadow.setXOffset(0)

        shadow.setYOffset(6)

        shadow.setColor(QColor(0, 0, 0, 18))

        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)

        layout.setAlignment(Qt.AlignCenter)

        layout.setSpacing(10)
        layout.setContentsMargins(20,20,20,20)

        icon_label = QLabel(icon)

        icon_label.setObjectName("feature-icon")

        icon_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel(text)

        text_label.setObjectName("feature-text")

        text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)

        layout.addWidget(text_label)

        card.clicked.connect(
            lambda _, k=key: self.navigate.emit(k)
        )

        return card

    def refresh(self):

        while self.layout().count():

            item = self.layout().takeAt(0)

            if item.widget():

                item.widget().deleteLater()

        self._build_ui()
