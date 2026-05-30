"""
Trang xem và quản lý điểm danh
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QComboBox, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

PAGE_STYLE = """
QWidget { background: #e8eef5; }
QTableWidget { background: white; border-radius: 8px; border: none; font-size: 12px; }
QTableWidget::item { padding: 6px 10px; color: #2d3748; }
QTableWidget::item:selected { background: #fff3e0; }
QHeaderView::section { background: #1a2035; color: white; font-weight: bold; font-size: 12px; padding: 8px 10px; border: none; }
QComboBox { border:1.5px solid #e2e8f0; border-radius:6px; padding:6px; font-size:12px; min-width:200px; }
"""

STATUS_LABELS = {"present": "✅ Có mặt", "absent": "❌ Vắng", "late": "⏰ Muộn"}
STATUS_COLORS = {"present": "#c6f6d5", "absent": "#fed7d7", "late": "#fefcbf"}


class AttendancePage(QWidget):
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
        title = QLabel("📋  Điểm danh")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#1a2035;")
        hdr.addWidget(title); hdr.addStretch()

        lbl = QLabel("Chọn buổi học:")
        lbl.setStyleSheet("color:#4a5568; font-size:12px;")
        hdr.addWidget(lbl)

        self.cmb_session = QComboBox()
        self.cmb_session.currentIndexChanged.connect(self._load_attendance)
        hdr.addWidget(self.cmb_session)
        layout.addLayout(hdr)

        # Stats
        self.stats_row = QHBoxLayout()
        self.lbl_present = self._stat_badge("✅ Có mặt: 0", "#c6f6d5", "#276749")
        self.lbl_absent  = self._stat_badge("❌ Vắng: 0",   "#fed7d7", "#742a2a")
        self.lbl_late    = self._stat_badge("⏰ Muộn: 0",    "#fefcbf", "#744210")
        self.stats_row.addWidget(self.lbl_present)
        self.stats_row.addWidget(self.lbl_absent)
        self.stats_row.addWidget(self.lbl_late)
        self.stats_row.addStretch()
        layout.addLayout(self.stats_row)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["#", "Mã SV", "Họ và tên", "Lớp", "Giờ điểm danh", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.lbl_empty = QLabel("Chọn buổi học để xem danh sách điểm danh")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.setStyleSheet("color:#a0aec0; font-size:14px; padding:40px;")
        layout.addWidget(self.lbl_empty)

    def _stat_badge(self, text, bg, color):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"background:{bg}; color:{color}; border-radius:6px; padding:4px 12px; font-size:12px; font-weight:600;")
        return lbl

    def refresh(self):
        sessions = self.db.get_all_sessions()
        self.cmb_session.blockSignals(True)
        self.cmb_session.clear()
        self.cmb_session.addItem("-- Chọn buổi học --", None)
        for s in sessions:
            label = f"{s.get('subject_code','')} - {s.get('session_date','')} {s.get('start_time','')}"
            self.cmb_session.addItem(label, s["id"])
        self.cmb_session.blockSignals(False)
        self._load_attendance()

    def _load_attendance(self):
        session_id = self.cmb_session.currentData()
        if not session_id:
            self.table.setRowCount(0)
            self.table.setVisible(False)
            self.lbl_empty.setVisible(True)
            return

        records = self.db.get_attendance_by_session(session_id)
        self.table.setVisible(True)
        self.lbl_empty.setVisible(False)
        self.table.setRowCount(len(records))

        counts = {"present": 0, "absent": 0, "late": 0}
        for row, r in enumerate(records):
            status = r.get("status", "present")
            counts[status] = counts.get(status, 0) + 1

            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(r.get("student_code", "")))
            self.table.setItem(row, 2, QTableWidgetItem(r.get("full_name", "")))
            self.table.setItem(row, 3, QTableWidgetItem(r.get("class_name", "")))
            check = r.get("check_time", "")
            if "T" in check: check = check.split("T")[1][:5]
            self.table.setItem(row, 4, QTableWidgetItem(check))
            st_item = QTableWidgetItem(STATUS_LABELS.get(status, status))
            st_item.setBackground(QColor(STATUS_COLORS.get(status, "#ffffff")))
            self.table.setItem(row, 5, st_item)
            self.table.setRowHeight(row, 38)

        self.lbl_present.setText(f"✅ Có mặt: {counts['present']}")
        self.lbl_absent.setText(f"❌ Vắng: {counts['absent']}")
        self.lbl_late.setText(f"⏰ Muộn: {counts['late']}")
