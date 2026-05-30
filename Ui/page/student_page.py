"""
Trang quản lý sinh viên
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
                              QHeaderView, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


PAGE_STYLE = """
QWidget { background: #e8eef5; }
QTableWidget {
    background: white;
    border-radius: 8px;
    border: none;
    font-size: 12px;
    gridline-color: #f0f4f8;
}
QTableWidget::item { padding: 6px 10px; color: #2d3748; }
QTableWidget::item:selected { background: #fff3e0; color: #1a2035; }
QHeaderView::section {
    background: #1a2035;
    color: white;
    font-weight: bold;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
}
QPushButton.action { border-radius: 6px; padding: 6px 14px; border: none; font-size: 12px; font-weight: 600; color: white; }
QPushButton.action:hover { opacity: 0.85; }
QLineEdit { border:1.5px solid #e2e8f0; border-radius:6px; padding:6px 10px; font-size:12px; }
QLineEdit:focus { border-color: #FF5722; }
"""


class StudentDialog(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm sinh viên" if not data else "Sửa sinh viên")
        self.setMinimumWidth(360)
        self.setStyleSheet("""
            QDialog { background: white; }
            QLabel { color: #4a5568; font-size: 12px; }
            QLineEdit { border:1.5px solid #e2e8f0; border-radius:6px; padding:7px; font-size:13px; }
            QLineEdit:focus { border-color:#FF5722; }
        """)
        form = QFormLayout(self)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(10)

        self.txt_code  = QLineEdit(data.get("student_code","") if data else "")
        self.txt_name  = QLineEdit(data.get("full_name","") if data else "")
        self.txt_class = QLineEdit(data.get("class_name","") if data else "")
        self.txt_email = QLineEdit(data.get("email","") if data else "")
        self.txt_phone = QLineEdit(data.get("phone","") if data else "")

        form.addRow("Mã sinh viên *", self.txt_code)
        form.addRow("Họ và tên *",    self.txt_name)
        form.addRow("Lớp",            self.txt_class)
        form.addRow("Email",          self.txt_email)
        form.addRow("Số điện thoại",  self.txt_phone)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def get_data(self):
        return {
            "student_code": self.txt_code.text().strip(),
            "full_name":    self.txt_name.text().strip(),
            "class_name":   self.txt_class.text().strip(),
            "email":        self.txt_email.text().strip(),
            "phone":        self.txt_phone.text().strip(),
        }


class StudentPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setStyleSheet(PAGE_STYLE)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("👤  Quản lý Sinh viên")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a2035;")
        hdr.addWidget(title)
        hdr.addStretch()

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Tìm kiếm...")
        self.txt_search.setFixedWidth(220)
        self.txt_search.textChanged.connect(self._search)
        hdr.addWidget(self.txt_search)

        btn_add = QPushButton("+ Thêm mới")
        btn_add.setProperty("class", "action")
        btn_add.setStyleSheet("background:#FF5722;color:white;border-radius:6px;padding:6px 14px;border:none;font-size:12px;font-weight:600;")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._add)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "Mã SV", "Họ và tên", "Lớp", "Email", "SĐT", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color:#718096; font-size:11px;")
        layout.addWidget(self.lbl_count)

    def refresh(self):
        self._load(self.db.get_all_students())

    def _search(self, keyword):
        if keyword.strip():
            self._load(self.db.search_students(keyword))
        else:
            self.refresh()

    def _load(self, students):
        self.table.setRowCount(len(students))
        for row, s in enumerate(students):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(s.get("student_code", "")))
            self.table.setItem(row, 2, QTableWidgetItem(s.get("full_name", "")))
            self.table.setItem(row, 3, QTableWidgetItem(s.get("class_name", "")))
            self.table.setItem(row, 4, QTableWidgetItem(s.get("email", "")))
            self.table.setItem(row, 5, QTableWidgetItem(s.get("phone", "")))

            # Action buttons
            cell = QWidget()
            lay = QHBoxLayout(cell)
            lay.setContentsMargins(4, 2, 4, 2)
            lay.setSpacing(4)

            btn_edit = QPushButton("✏️ Sửa")
            btn_edit.setStyleSheet("background:#3182ce;color:white;border-radius:4px;padding:3px 8px;border:none;font-size:11px;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, sid=s["id"]: self._edit(sid))

            btn_del = QPushButton("🗑 Xóa")
            btn_del.setStyleSheet("background:#e53e3e;color:white;border-radius:4px;padding:3px 8px;border:none;font-size:11px;")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, sid=s["id"]: self._delete(sid))

            lay.addWidget(btn_edit)
            lay.addWidget(btn_del)
            self.table.setCellWidget(row, 6, cell)
            self.table.setRowHeight(row, 38)

        self.lbl_count.setText(f"Tổng: {len(students)} sinh viên")

    def _add(self):
        dlg = StudentDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["student_code"] or not data["full_name"]:
                QMessageBox.warning(self, "Lỗi", "Mã sinh viên và họ tên không được để trống!")
                return
            try:
                self.db.add_student(data)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit(self, student_id):
        s = self.db.get_student(student_id)
        if not s:
            return
        dlg = StudentDialog(data=s, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                self.db.update_student(student_id, data)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _delete(self, student_id):
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa sinh viên này?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_student(student_id)
            self.refresh()
