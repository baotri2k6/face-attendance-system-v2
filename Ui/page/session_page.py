"""
Trang quản lý buổi học
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QDialog, QFormLayout, QDialogButtonBox,
                              QComboBox, QLineEdit, QHeaderView, QMessageBox,
                              QAbstractItemView, QDateEdit)
from PyQt5.QtCore import Qt, QDate

PAGE_STYLE = """
QWidget { background: #e8eef5; }
QTableWidget { background: white; border-radius: 8px; border: none; font-size: 12px; }
QTableWidget::item { padding: 6px 10px; color: #2d3748; }
QTableWidget::item:selected { background: #fff3e0; }
QHeaderView::section { background: #1a2035; color: white; font-weight: bold; font-size: 12px; padding: 8px 10px; border: none; }
"""


class SessionDialog(QDialog):
    def __init__(self, subjects, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm buổi học" if not data else "Xem buổi học")
        self.setMinimumWidth(380)
        self.setStyleSheet("QDialog{background:white;} QLabel{color:#4a5568;font-size:12px;} QLineEdit,QComboBox,QDateEdit{border:1.5px solid #e2e8f0;border-radius:6px;padding:7px;font-size:13px;}")
        form = QFormLayout(self)
        form.setContentsMargins(20, 20, 20, 20); form.setSpacing(10)

        self.cmb_subject = QComboBox()
        for s in subjects:
            self.cmb_subject.addItem(f"{s['subject_code']} - {s['subject_name']}", s["id"])
        if data and data.get("subject_id"):
            idx = self.cmb_subject.findData(data["subject_id"])
            if idx >= 0: self.cmb_subject.setCurrentIndex(idx)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        if data and data.get("session_date"):
            self.date_edit.setDate(QDate.fromString(data["session_date"], "yyyy-MM-dd"))

        self.txt_start = QLineEdit(data.get("start_time","07:00") if data else "07:00")
        self.txt_end   = QLineEdit(data.get("end_time","09:00") if data else "09:00")
        self.txt_room  = QLineEdit(data.get("room","") if data else "")
        self.txt_note  = QLineEdit(data.get("note","") if data else "")

        form.addRow("Môn học *",    self.cmb_subject)
        form.addRow("Ngày học",     self.date_edit)
        form.addRow("Giờ bắt đầu", self.txt_start)
        form.addRow("Giờ kết thúc",self.txt_end)
        form.addRow("Phòng",        self.txt_room)
        form.addRow("Ghi chú",      self.txt_note)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        form.addRow(btns)

    def get_data(self):
        return {"subject_id": self.cmb_subject.currentData(),
                "session_date": self.date_edit.date().toString("yyyy-MM-dd"),
                "start_time": self.txt_start.text().strip(),
                "end_time": self.txt_end.text().strip(),
                "room": self.txt_room.text().strip(),
                "note": self.txt_note.text().strip()}


class SessionPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setStyleSheet(PAGE_STYLE)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16); layout.setSpacing(10)

        hdr = QHBoxLayout()
        title = QLabel("📅  Quản lý Buổi học")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a2035;")
        hdr.addWidget(title); hdr.addStretch()
        btn_add = QPushButton("+ Thêm buổi học")
        btn_add.setStyleSheet("background:#FF5722;color:white;border-radius:6px;padding:6px 14px;border:none;font-size:12px;font-weight:600;")
        btn_add.setCursor(Qt.PointingHandCursor); btn_add.clicked.connect(self._add)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "Mã môn", "Tên môn", "Ngày", "Giờ", "Phòng", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        sessions = self.db.get_all_sessions()
        self.table.setRowCount(len(sessions))
        for row, s in enumerate(sessions):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(s.get("subject_code", "")))
            self.table.setItem(row, 2, QTableWidgetItem(s.get("subject_name", "")))
            self.table.setItem(row, 3, QTableWidgetItem(s.get("session_date", "")))
            time_str = f"{s.get('start_time','')} - {s.get('end_time','')}"
            self.table.setItem(row, 4, QTableWidgetItem(time_str))
            self.table.setItem(row, 5, QTableWidgetItem(s.get("room", "")))

            cell = QWidget(); lay = QHBoxLayout(cell); lay.setContentsMargins(4,2,4,2); lay.setSpacing(4)
            btn_d = QPushButton("🗑 Xóa")
            btn_d.setStyleSheet("background:#e53e3e;color:white;border-radius:4px;padding:3px 8px;border:none;font-size:11px;")
            btn_d.setCursor(Qt.PointingHandCursor); btn_d.clicked.connect(lambda _, sid=s["id"]: self._delete(sid))
            lay.addWidget(btn_d)
            self.table.setCellWidget(row, 6, cell)
            self.table.setRowHeight(row, 38)

    def _add(self):
        subjects = self.db.get_all_subjects()
        if not subjects:
            QMessageBox.information(self, "Thông báo", "Vui lòng thêm môn học trước!")
            return
        dlg = SessionDialog(subjects, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            try: self.db.add_session(dlg.get_data()); self.refresh()
            except Exception as e: QMessageBox.critical(self, "Lỗi", str(e))

    def _delete(self, sid):
        if QMessageBox.question(self, "Xác nhận", "Xóa buổi học này?\n(Sẽ xóa luôn dữ liệu điểm danh của buổi này)",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.delete_session(sid)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa buổi học!\n{e}")