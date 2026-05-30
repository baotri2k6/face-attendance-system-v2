"""
Trang quản lý giáo viên
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
                              QHeaderView, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt


PAGE_STYLE = """
QWidget { background: #e8eef5; }
QTableWidget { background: white; border-radius: 8px; border: none; font-size: 12px; gridline-color: #f0f4f8; }
QTableWidget::item { padding: 6px 10px; color: #2d3748; }
QTableWidget::item:selected { background: #fff3e0; color: #1a2035; }
QHeaderView::section { background: #1a2035; color: white; font-weight: bold; font-size: 12px; padding: 8px 10px; border: none; }
QLineEdit { border:1.5px solid #e2e8f0; border-radius:6px; padding:6px 10px; font-size:12px; }
"""


class TeacherDialog(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm giáo viên" if not data else "Sửa giáo viên")
        self.setMinimumWidth(360)
        self.setStyleSheet("QDialog{background:white;} QLabel{color:#4a5568;font-size:12px;} QLineEdit{border:1.5px solid #e2e8f0;border-radius:6px;padding:7px;font-size:13px;}")
        form = QFormLayout(self)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(10)
        self.txt_code   = QLineEdit(data.get("teacher_code","") if data else "")
        self.txt_name   = QLineEdit(data.get("full_name","") if data else "")
        self.txt_dept   = QLineEdit(data.get("department","") if data else "")
        self.txt_email  = QLineEdit(data.get("email","") if data else "")
        self.txt_phone  = QLineEdit(data.get("phone","") if data else "")
        form.addRow("Mã GV *",       self.txt_code)
        form.addRow("Họ và tên *",   self.txt_name)
        form.addRow("Khoa / Bộ môn", self.txt_dept)
        form.addRow("Email",         self.txt_email)
        form.addRow("Số điện thoại", self.txt_phone)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def get_data(self):
        return {"teacher_code": self.txt_code.text().strip(), "full_name": self.txt_name.text().strip(),
                "department": self.txt_dept.text().strip(), "email": self.txt_email.text().strip(),
                "phone": self.txt_phone.text().strip()}


class TeacherPage(QWidget):
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

        hdr = QHBoxLayout()
        title = QLabel("👨‍🏫  Quản lý Giáo viên")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a2035;")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_add = QPushButton("+ Thêm mới")
        btn_add.setStyleSheet("background:#FF5722;color:white;border-radius:6px;padding:6px 14px;border:none;font-size:12px;font-weight:600;")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._add)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["#", "Mã GV", "Họ và tên", "Khoa/BM", "Email", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        teachers = self.db.get_all_teachers()
        self.table.setRowCount(len(teachers))
        for row, t in enumerate(teachers):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(t.get("teacher_code", "")))
            self.table.setItem(row, 2, QTableWidgetItem(t.get("full_name", "")))
            self.table.setItem(row, 3, QTableWidgetItem(t.get("department", "")))
            self.table.setItem(row, 4, QTableWidgetItem(t.get("email", "")))

            cell = QWidget()
            lay = QHBoxLayout(cell)
            lay.setContentsMargins(4, 2, 4, 2)
            lay.setSpacing(4)
            btn_e = QPushButton("✏️ Sửa")
            btn_e.setStyleSheet("background:#3182ce;color:white;border-radius:4px;padding:3px 8px;border:none;font-size:11px;")
            btn_e.setCursor(Qt.PointingHandCursor)
            btn_e.clicked.connect(lambda _, tid=t["id"]: self._edit(tid))
            btn_d = QPushButton("🗑 Xóa")
            btn_d.setStyleSheet("background:#e53e3e;color:white;border-radius:4px;padding:3px 8px;border:none;font-size:11px;")
            btn_d.setCursor(Qt.PointingHandCursor)
            btn_d.clicked.connect(lambda _, tid=t["id"]: self._delete(tid))
            lay.addWidget(btn_e); lay.addWidget(btn_d)
            self.table.setCellWidget(row, 5, cell)
            self.table.setRowHeight(row, 38)

    def _add(self):
        dlg = TeacherDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["teacher_code"] or not data["full_name"]:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
                return
            try:
                self.db.add_teacher(data)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _edit(self, tid):
        teachers = {t["id"]: t for t in self.db.get_all_teachers()}
        t = teachers.get(tid)
        if not t: return
        dlg = TeacherDialog(data=t, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            try:
                self.db.update_teacher(tid, dlg.get_data())
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _delete(self, tid):
        if QMessageBox.question(self, "Xác nhận", "Xóa giáo viên này?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.delete_teacher(tid)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa giáo viên!\n{e}")