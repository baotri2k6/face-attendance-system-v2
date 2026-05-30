"""
Trang đăng nhập
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DEFAULT_ADMIN


class LoginPage(QWidget):
    login_success = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
    QWidget {
        background-color: #1a2035;
        font-family: "Noto Sans", "DejaVu Sans";
    }

    QFrame#card {
        background-color: white;
        border-radius: 18px;
    }

    QLabel#title {
        background: transparent;
        color: #FF5722;
        font-size: 28px;
        font-weight: bold;
    }

    QLabel#sub {
        background: transparent;
        color: #718096;
        font-size: 14px;
    }

    QLabel.field-label {
        background: transparent;
        color: #2d3748;
        font-size: 13px;
        font-weight: bold;
    }

    QLineEdit {
        background-color: #f7fafc;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px;
        font-size: 13px;
        color: #2d3748;
    }

    QLineEdit:focus {
        border: 2px solid #FF5722;
    }

    QPushButton#login-btn {
        background-color: #FF5722;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 14px;
        font-weight: bold;
    }

    QPushButton#login-btn:hover {
        background-color: #e64a19;
    }
""")
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedSize(450, 500)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(36, 36, 36, 36)
        card_lay.setSpacing(16)

        icon = QLabel("👁")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 28px;")
        card_lay.addWidget(icon)
        title = QLabel("Hệ thống nhận diện\nkhuôn mặt")
        title.setFont(QFont("Noto Sans", 20, QFont.Bold))
        title.setStyleSheet("font-size: 24px;")
        title.setObjectName("title")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        card_lay.addWidget(title)
        sub = QLabel("Đăng nhập để tiếp tục")
        sub.setObjectName("sub")
        sub.setAlignment(Qt.AlignCenter)
        card_lay.addWidget(sub)
        card_lay.addSpacing(10)

        lbl_user = QLabel("Tên đăng nhập")
        lbl_user.setProperty("class", "field-label")
        card_lay.addWidget(lbl_user)

        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Nhập tên đăng nhập")
        self.txt_user.setText(DEFAULT_ADMIN["username"])
        card_lay.addWidget(self.txt_user)

        lbl_pass = QLabel("Mật khẩu")
        lbl_pass.setProperty("class", "field-label")
        card_lay.addWidget(lbl_pass)

        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.Password)
        self.txt_pass.setPlaceholderText("Nhập mật khẩu")
        self.txt_pass.returnPressed.connect(self._do_login)
        card_lay.addWidget(self.txt_pass)
        card_lay.addSpacing(8)

        btn = QPushButton("Đăng nhập")
        btn.setObjectName("login-btn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._do_login)
        card_lay.addWidget(btn)

        self.lbl_err = QLabel("")
        self.lbl_err.setAlignment(Qt.AlignCenter)
        self.lbl_err.setStyleSheet("color: #e53e3e; font-size:12px;")
        card_lay.addWidget(self.lbl_err)

        outer.addWidget(card)

    def _do_login(self):
        user = self.txt_user.text().strip()
        pwd = self.txt_pass.text().strip()
        if user == DEFAULT_ADMIN["username"] and pwd == DEFAULT_ADMIN["password"]:
            self.login_success.emit(user)
        else:
            self.lbl_err.setText("❌ Sai tên đăng nhập hoặc mật khẩu!")
