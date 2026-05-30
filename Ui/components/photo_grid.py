"""
Photo grid component for displaying student photos
"""
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QVBoxLayout,
                              QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import os


class PhotoCard(QWidget):
    def __init__(self, name, code, photo_path="", parent=None):
        super().__init__(parent)
        self.setFixedSize(130, 160)
        self.setStyleSheet("""
            QWidget {
                background: #f0f4f8;
                border-radius: 8px;
            }
            QWidget:hover {
                background: #e2e8f0;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        img_lbl = QLabel()
        img_lbl.setFixedSize(118, 110)
        img_lbl.setAlignment(Qt.AlignCenter)
        img_lbl.setStyleSheet("background:#d1d9e0; border-radius:6px; color:#718096;")

        if photo_path and os.path.exists(photo_path):
            pix = QPixmap(photo_path).scaled(118, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_lbl.setPixmap(pix)
        else:
            img_lbl.setText("👤")
            img_lbl.setStyleSheet("background:#d1d9e0;border-radius:6px;font-size:36px;")

        layout.addWidget(img_lbl)

        name_lbl = QLabel(name)
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet("font-size:10px; font-weight:bold; color:#2d3748;")
        layout.addWidget(name_lbl)

        code_lbl = QLabel(code)
        code_lbl.setAlignment(Qt.AlignCenter)
        code_lbl.setStyleSheet("font-size:9px; color:#718096;")
        layout.addWidget(code_lbl)


class PhotoGrid(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(10)
        self._grid.setContentsMargins(10, 10, 10, 10)
        self.setWidget(self._container)

    def load_photos(self, items):
        """items: list of dicts with full_name, student_code, photo_path"""
        # Clear
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 5
        for i, item in enumerate(items):
            card = PhotoCard(
                item.get("full_name", ""),
                item.get("student_code", ""),
                item.get("photo_path", "")
            )
            self._grid.addWidget(card, i // cols, i % cols)

        # Fill empty cells
        remainder = len(items) % cols
        if remainder:
            for j in range(cols - remainder):
                spacer = QWidget()
                spacer.setFixedSize(130, 160)
                self._grid.addWidget(spacer, len(items) // cols, remainder + j)