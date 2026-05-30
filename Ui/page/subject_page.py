"""
Trang quản lý môn học
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QDialogButtonBox,
                              QComboBox, QSpinBox, QLineEdit,
                              QHeaderView, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt

PAGE_STYLE = """
QWidget { background: #e8eef5; }
QTableWidget { background: white; border-radius: 8px; border: none; font-size: 12px; }
QTableWidget::item { padding: 6px 10px; color: #2d3748; }
QTableWidget::item:selected { background: #fff3e0; }
QHeaderView::section { background: #1a2035; color: white; font-weight: bold; font-size: 12px; padding: 8px 10px; border: none; }
"""


class SubjectDialog(QDialog):
    def __init__(self, teachers, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm môn học" if not data else "Sửa môn học")
        self.setMinimumWidth(380)
        self.setStyleSheet("QDialog{background:white;} QLabel{color:#4a5568;font-size:12px;} QLineEdit,QComboBox,QSpinBox{border:1.5px solid #e2e8f0;border-radius:6px;padding:7px;font-size:13px;}")
        form = QFormLayout(self)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(10)

        self.txt_code = QLineEdit(data.get("subject_code","") if data else "")
        self.txt_name = QLineEdit(data.get("subject_name","") if data else "")
        self.spin_credits = QSpinBox()
        self.spin_credits.setRange(1, 10)
        self.spin_credits.setValue(data.get("credits", 3) if data else 3)

        self.cmb_teacher = QComboBox()
        self.cmb_teacher.addItem("-- Chọn giáo viên --", None)
        for t in teachers:
            self.cmb_teacher.addItem(t["full_name"], t["id"])
        if data and data.get("teacher_id"):
            idx = self.cmb_teacher.findData(data["teacher_id"])
            if idx >= 0:
                self.cmb_teacher.setCurrentIndex(idx)

        form.addRow("Mã môn *",    self.txt_code)
        form.addRow("Tên môn *",   self.txt_name)
        form.addRow("Số tín chỉ",  self.spin_credits)
        form.addRow("Giáo viên",   self.cmb_teacher)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def get_data(self):
        return {"subject_code": self.txt_code.text().strip(), "subject_name": self.txt_name.text().strip(),
                "credits": self.spin_credits.value(), "teacher_id": self.cmb_teacher.currentData()}


class SubjectPage(QWidget):
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
        title = QLabel("📖  Quản lý Môn học")
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
        self.table.setHorizontalHeaderLabels(["#", "Mã môn", "Tên môn học", "Tín chỉ", "Giáo viên", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        subjects = self.db.get_all_subjects()
        self.table.setRowCount(len(subjects))
        for row, s in enumerate(subjects):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(s.get("subject_code", "")))
            self.table.setItem(row, 2, QTableWidgetItem(s.get("subject_name", "")))
            self.table.setItem(row, 3, QTableWidgetItem(str(s.get("credits", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(s.get("teacher_name", "") or ""))

            cell = QWidget()
            lay = QHBoxLayout(cell); lay.setContentsMargins(4,2,4,2); lay.setSpacing(4)
            btn_e = QPushButton("✏️ Sửa"); btn_e.setStyleSheet("background:#3182ce;color:white;border-radius:4px;padding:3px 8px;border:none;font-size:11px;")
            btn_e.setCursor(Qt.PointingHandCursor); btn_e.clicked.connect(lambda _, sid=s["id"]: self._edit(sid))
            btn_d = QPushButton("🗑 Xóa"); btn_d.setStyleSheet("background:#e53e3e;color:white;border-radius:4px;padding:3px 8px;border:none;font-size:11px;")
            btn_d.setCursor(Qt.PointingHandCursor); btn_d.clicked.connect(lambda _, sid=s["id"]: self._delete(sid))
            lay.addWidget(btn_e); lay.addWidget(btn_d)
            self.table.setCellWidget(row, 5, cell)
            self.table.setRowHeight(row, 38)

    def _add(self):
        dlg = SubjectDialog(self.db.get_all_teachers(), parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["subject_code"] or not data["subject_name"]:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return
            try: self.db.add_subject(data); self.refresh()
            except Exception as e: QMessageBox.critical(self, "Lỗi", str(e))

    def _edit(self, sid):
        subjects = {s["id"]: s for s in self.db.get_all_subjects()}
        s = subjects.get(sid)
        if not s: return
        dlg = SubjectDialog(self.db.get_all_teachers(), data=s, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            try: self.db.update_subject(sid, dlg.get_data()); self.refresh()
            except Exception as e: QMessageBox.critical(self, "Lỗi", str(e))

    def _delete(self, sid):
        if QMessageBox.question(self, "Xác nhận", "Xóa môn học này?\n(Sẽ xóa luôn các buổi học và điểm danh liên quan)",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.delete_subject(sid)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa môn học!\n{e}")