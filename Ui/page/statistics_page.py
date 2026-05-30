"""
Trang thống kê
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
                              QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

PAGE_STYLE = """
QWidget { background: #e8eef5; }
QFrame.stat-card { background: white; border-radius: 10px; border: none; }
QTableWidget { background: white; border-radius: 8px; border: none; font-size: 12px; }
QTableWidget::item { padding: 6px 10px; color: #2d3748; }
QTableWidget::item:selected { background: #fff3e0; }
QHeaderView::section { background: #1a2035; color: white; font-weight: bold; font-size: 12px; padding: 8px 10px; border: none; }
"""


class StatCard(QFrame):
    def __init__(self, icon, value, label, color="#FF5722", parent=None):
        super().__init__(parent)
        self.setProperty("class", "stat-card")
        self.setStyleSheet("QFrame { background: white; border-radius: 10px; }")
        self.setFixedHeight(100)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 32px; background: {color}22; border-radius: 8px; padding: 6px;")
        icon_lbl.setFixedSize(52, 52)
        icon_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(icon_lbl)
        lay.addSpacing(10)

        txt = QVBoxLayout()
        v = QLabel(str(value))
        v.setStyleSheet(f"font-size:24px; font-weight:bold; color:{color};")
        l = QLabel(label)
        l.setStyleSheet("font-size:12px; color:#718096;")
        txt.addWidget(v); txt.addWidget(l)
        lay.addLayout(txt)
        lay.addStretch()


class StatisticsPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setStyleSheet(PAGE_STYLE)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16); layout.setSpacing(14)

        title = QLabel("📊  Thống kê hệ thống")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a2035;")
        layout.addWidget(title)

        self.stat_grid = QGridLayout()
        self.stat_grid.setSpacing(12)
        layout.addLayout(self.stat_grid)

        # Attendance rate chart (simple bar)
        chart_title = QLabel("Tỷ lệ điểm danh theo môn học")
        chart_title.setStyleSheet("font-size:14px; font-weight:600; color:#1a2035; margin-top:8px;")
        layout.addWidget(chart_title)

        self.chart_area = QFrame()
        self.chart_area.setStyleSheet("QFrame{background:white; border-radius:10px;}")
        self.chart_area.setMinimumHeight(120)
        chart_lay = QHBoxLayout(self.chart_area)
        chart_lay.setContentsMargins(16, 16, 16, 16); chart_lay.setSpacing(8)
        self._chart_inner = chart_lay
        layout.addWidget(self.chart_area)

        # Recent attendance table
        rec_title = QLabel("Điểm danh gần đây")
        rec_title.setStyleSheet("font-size:14px; font-weight:600; color:#1a2035; margin-top:8px;")
        layout.addWidget(rec_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Sinh viên", "Mã SV", "Môn học", "Ngày", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setMaximumHeight(200)
        layout.addWidget(self.table)
        layout.addStretch()

    def refresh(self):
        stats = self.db.get_attendance_stats()
        # Clear stat grid
        while self.stat_grid.count():
            item = self.stat_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        cards = [
            ("👤", stats["total_students"], "Sinh viên", "#3182ce"),
            ("📖", stats["total_subjects"], "Môn học",   "#805ad5"),
            ("📅", stats["total_sessions"], "Buổi học",  "#d69e2e"),
            ("✅", stats["total_attendance"], "Lượt điểm danh", "#38a169"),
        ]
        for i, (ico, val, lbl, color) in enumerate(cards):
            card = StatCard(ico, val, lbl, color)
            self.stat_grid.addWidget(card, 0, i)

        # Chart
        while self._chart_inner.count():
            item = self._chart_inner.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        subjects = self.db.get_all_subjects()
        sessions_all = self.db.get_all_sessions()
        max_att = max(stats["total_attendance"], 1)
        for subj in subjects[:6]:
            s_sessions = [s for s in sessions_all if s.get("subject_id") == subj["id"]]
            att_count = 0
            for sess in s_sessions:
                att_count += len(self.db.get_attendance_by_session(sess["id"]))
            col = QVBoxLayout()
            bar_h = max(10, int(100 * att_count / max_att))
            bar = QFrame()
            bar.setStyleSheet(f"QFrame{{background:#FF5722; border-radius:4px;}}")
            bar.setFixedSize(40, bar_h)
            col.addStretch()
            col.addWidget(bar, alignment=Qt.AlignHCenter)
            val_lbl = QLabel(str(att_count))
            val_lbl.setAlignment(Qt.AlignCenter)
            val_lbl.setStyleSheet("font-size:11px; font-weight:bold; color:#1a2035;")
            col.addWidget(val_lbl)
            name_lbl = QLabel(subj.get("subject_code",""))
            name_lbl.setAlignment(Qt.AlignCenter)
            name_lbl.setStyleSheet("font-size:10px; color:#718096;")
            col.addWidget(name_lbl)
            self._chart_inner.addLayout(col)
        self._chart_inner.addStretch()

        # Recent attendance
        conn = self.db.get_connection()
        rows = conn.execute("""
            SELECT s.full_name, s.student_code, sb.subject_name, ss.session_date, a.status
            FROM attendances a
            JOIN students s ON a.student_id=s.id
            JOIN sessions ss ON a.session_id=ss.id
            JOIN subjects sb ON ss.subject_id=sb.id
            ORDER BY a.check_time DESC LIMIT 20
        """).fetchall()
        conn.close()
        self.table.setRowCount(len(rows))
        STATUS_LABELS = {"present": "✅ Có mặt", "absent": "❌ Vắng", "late": "⏰ Muộn"}
        STATUS_COLORS = {"present": "#c6f6d5", "absent": "#fed7d7", "late": "#fefcbf"}
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(r[0]))
            self.table.setItem(i, 1, QTableWidgetItem(r[1]))
            self.table.setItem(i, 2, QTableWidgetItem(r[2]))
            self.table.setItem(i, 3, QTableWidgetItem(r[3]))
            st = r[4]
            st_item = QTableWidgetItem(STATUS_LABELS.get(st, st))
            st_item.setBackground(QColor(STATUS_COLORS.get(st, "#fff")))
            self.table.setItem(i, 4, st_item)
            self.table.setRowHeight(i, 34)
