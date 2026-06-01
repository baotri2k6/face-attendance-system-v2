"""
Trang nhận diện khuôn mặt để điểm danh
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QListWidget, QListWidgetItem,
                              QSplitter, QFrame, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap, QColor
import cv2
import numpy as np
import pickle
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from modules.face_recognition import simple_encoder

PAGE_STYLE = """
QWidget { background: #e8eef5; }
QLabel#cam { background: #1a2035; border-radius: 8px; color: #a0aec0; font-size: 14px; }
QComboBox { border:1.5px solid #e2e8f0; border-radius:6px; padding:6px; font-size:12px; }
QListWidget { background: white; border-radius: 8px; border: none; font-size: 12px; }
QListWidget::item { padding: 8px; border-bottom: 1px solid #f0f4f8; }
"""


class RecognizePage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_frame)
        self._known_encodings = []
        self._known_simple_encodings = []
        self._known_simple_students = []
        self._known_students = []
        self._recognized_ids = set()
        self._session_id = None
        self._video_font = self._load_video_font()
        self.setStyleSheet(PAGE_STYLE)
        self._build_ui()
        self.refresh()

    def _load_video_font(self, size=16):
        font_paths = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\tahoma.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in font_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    def _draw_video_label(self, frame_bgr, text, left, bottom, right, color):
        """Draw Vietnamese text on an OpenCV frame using a Unicode font."""
        text = str(text)
        frame_h, frame_w = frame_bgr.shape[:2]
        image = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image)

        bbox = draw.textbbox((0, 0), text, font=self._video_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        pad_x = 4
        pad_y = 4
        bg_left = max(0, left)
        bg_bottom = min(frame_h - 1, bottom)
        bg_top = max(0, bg_bottom - text_h - pad_y * 2)
        bg_right = min(frame_w - 1, max(right, left + text_w + pad_x * 2))
        text_x = min(frame_w - text_w - 1, bg_left + pad_x)
        text_y = max(0, bg_top + pad_y - bbox[1])

        rgb_color = (color[2], color[1], color[0])
        draw.rectangle((bg_left, bg_top, bg_right, bg_bottom), fill=rgb_color)
        draw.text((text_x, text_y), text, font=self._video_font, fill=(255, 255, 255))
        frame_bgr[:, :] = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return frame_bgr

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16); layout.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("👁  Nhận diện khuôn mặt")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a2035;")
        hdr.addWidget(title); hdr.addStretch()
        layout.addLayout(hdr)

        # Session selector
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("Buổi học:").setObjectName("") or QLabel("Buổi học:"))
        self.cmb_session = QComboBox()
        self.cmb_session.setMinimumWidth(300)
        sel_row.addWidget(self.cmb_session)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        # Main content
        splitter = QSplitter(Qt.Horizontal)

        # Camera side
        cam_frame = QFrame()
        cam_frame.setStyleSheet("QFrame{background:white; border-radius:10px;}")
        cam_layout = QVBoxLayout(cam_frame)
        cam_layout.setContentsMargins(12, 12, 12, 12); cam_layout.setSpacing(8)

        self.lbl_cam = QLabel("Camera chưa khởi động")
        self.lbl_cam.setObjectName("cam")
        self.lbl_cam.setMinimumSize(460, 340)
        self.lbl_cam.setAlignment(Qt.AlignCenter)
        cam_layout.addWidget(self.lbl_cam)

        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("▶ Bật camera & Nhận diện")
        self.btn_start.setStyleSheet("background:#2ecc71;color:white;border-radius:6px;padding:8px 16px;border:none;font-size:12px;font-weight:600;")
        self.btn_start.setCursor(Qt.PointingHandCursor); self.btn_start.clicked.connect(self._start)
        self.btn_stop = QPushButton("■ Dừng")
        self.btn_stop.setStyleSheet("background:#e74c3c;color:white;border-radius:6px;padding:8px 16px;border:none;font-size:12px;font-weight:600;")
        self.btn_stop.setCursor(Qt.PointingHandCursor); self.btn_stop.clicked.connect(self._stop); self.btn_stop.setEnabled(False)
        btn_row.addWidget(self.btn_start); btn_row.addWidget(self.btn_stop)
        cam_layout.addLayout(btn_row)

        self.lbl_status = QLabel("Sẵn sàng nhận diện")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color:#718096; font-size:12px;")
        cam_layout.addWidget(self.lbl_status)

        splitter.addWidget(cam_frame)

        # Result side
        result_frame = QFrame()
        result_frame.setStyleSheet("QFrame{background:white; border-radius:10px;}")
        res_layout = QVBoxLayout(result_frame)
        res_layout.setContentsMargins(12, 12, 12, 12); res_layout.setSpacing(8)

        res_lbl = QLabel("✅ Đã điểm danh")
        res_lbl.setStyleSheet("font-size:14px; font-weight:bold; color:#1a2035;")
        res_layout.addWidget(res_lbl)

        self.list_recognized = QListWidget()
        res_layout.addWidget(self.list_recognized)

        self.lbl_count = QLabel("0 sinh viên đã điểm danh")
        self.lbl_count.setStyleSheet("color:#718096; font-size:11px;")
        res_layout.addWidget(self.lbl_count)

        btn_manual = QPushButton("📋 Điểm danh thủ công")
        btn_manual.setStyleSheet("background:#3182ce;color:white;border-radius:6px;padding:6px;border:none;font-size:12px;")
        btn_manual.setCursor(Qt.PointingHandCursor); btn_manual.clicked.connect(self._manual_attendance)
        res_layout.addWidget(btn_manual)

        splitter.addWidget(result_frame)
        splitter.setSizes([520, 280])
        layout.addWidget(splitter)

    def refresh(self):
        sessions = self.db.get_all_sessions()
        self.cmb_session.clear()
        self.cmb_session.addItem("-- Chọn buổi học --", None)
        for s in sessions:
            label = f"{s.get('subject_code','')} | {s.get('session_date','')} {s.get('start_time','')}"
            self.cmb_session.addItem(label, s["id"])
        self._load_face_encodings()

    def _load_face_encodings(self):
        students = self.db.get_students_with_face()
        self._known_encodings = []
        self._known_simple_encodings = []
        self._known_simple_students = []
        self._known_students = []
        for s in students:
            try:
                enc = pickle.loads(s["face_encoding"])
                if isinstance(enc, np.ndarray) and enc.shape == (128,):
                    self._known_encodings.append(enc)
                    self._known_students.append(s)
                elif isinstance(enc, np.ndarray):
                    self._known_simple_encodings.append(enc)
                    self._known_simple_students.append(s)
            except Exception:
                pass
        total = len(self._known_encodings) + len(self._known_simple_encodings)
        self.lbl_status.setText(f"Đã tải {total} khuôn mặt")

    def _start(self):
        session_id = self.cmb_session.currentData()
        if not session_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn buổi học!")
            return
        self._session_id = session_id
        self._recognized_ids = set()
        self.list_recognized.clear()

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Lỗi", "Không thể mở camera! Kiểm tra thiết bị.")
            return
        self.timer.start(100)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.lbl_status.setText("🔴 Đang nhận diện...")

    def _stop(self):
        self.timer.stop()
        if self.cap: self.cap.release(); self.cap = None
        self.lbl_cam.setText("Camera đã tắt")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lbl_status.setText(f"Hoàn thành. Đã điểm danh {len(self._recognized_ids)} sinh viên.")

    def _process_frame(self):
        if not self.cap or not self.cap.isOpened(): return
        ret, frame = self.cap.read()
        if not ret: return

        # Try face_recognition if available
        display_frame = frame.copy()
        try:
            import face_recognition
            small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb_small)
            encodings = face_recognition.face_encodings(rgb_small, locations)

            for (top, right, bottom, left), enc in zip(locations, encodings):
                top*=2; right*=2; bottom*=2; left*=2
                name = "Không nhận ra"
                color = (0, 0, 255)

                if self._known_encodings:
                    matches = face_recognition.compare_faces(self._known_encodings, enc, tolerance=0.5)
                    if True in matches:
                        idx = matches.index(True)
                        student = self._known_students[idx]
                        name = student["full_name"]
                        color = (0, 200, 0)
                        sid = student["id"]
                        if sid not in self._recognized_ids and self._session_id:
                            self._recognized_ids.add(sid)
                            self.db.mark_attendance(self._session_id, sid, "present", "face")
                            item = QListWidgetItem(f"✅ {name} ({student['student_code']})")
                            item.setForeground(QColor("#276749"))
                            self.list_recognized.addItem(item)
                            self.lbl_count.setText(f"{len(self._recognized_ids)} sinh viên đã điểm danh")

                cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
                display_frame = self._draw_video_label(display_frame, name, left, bottom, right, color)
        except ImportError:
            self._process_frame_opencv(display_frame)

        rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch*w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(self.lbl_cam.width(), self.lbl_cam.height(),
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_cam.setPixmap(pix)

    def _process_frame_opencv(self, display_frame):
        boxes = simple_encoder.detect_faces(display_frame)
        if not boxes:
            self._draw_video_label(
                display_frame,
                "Đang sử dụng OpenCV fallback",
                10,
                38,
                310,
                (0, 180, 180),
            )
            return

        for box in boxes:
            top, right, bottom, left = box
            enc = simple_encoder.encode_face_box(display_frame, box)
            idx, score = simple_encoder.best_match(enc, self._known_simple_encodings)

            name = "Không nhận ra"
            color = (0, 0, 255)

            if idx >= 0:
                student = self._known_simple_students[idx]
                name = student["full_name"]
                color = (0, 200, 0)
                sid = student["id"]
                if sid not in self._recognized_ids and self._session_id:
                    self._recognized_ids.add(sid)
                    self.db.mark_attendance(self._session_id, sid, "present", "face")
                    item = QListWidgetItem(f"✅ {name} ({student['student_code']})")
                    item.setForeground(QColor("#276749"))
                    self.list_recognized.addItem(item)
                    self.lbl_count.setText(f"{len(self._recognized_ids)} sinh viên đã điểm danh")

            cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
            label = f"{name} {score:.2f}" if idx >= 0 else name
            display_frame = self._draw_video_label(display_frame, label, left, bottom, right, color)

    def _manual_attendance(self):
        session_id = self.cmb_session.currentData()
        if not session_id:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn buổi học!")
            return
        students = self.db.get_all_students()
        from PyQt5.QtWidgets import QDialog, QListWidget, QListWidgetItem, QDialogButtonBox, QVBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle("Điểm danh thủ công")
        dlg.setMinimumSize(350, 400)
        dlg.setStyleSheet("QDialog{background:white;}")
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Chọn sinh viên để điểm danh:"))
        lst = QListWidget()
        lst.setSelectionMode(QListWidget.MultiSelection)
        for s in students:
            item = QListWidgetItem(f"{s['student_code']} - {s['full_name']}")
            item.setData(Qt.UserRole, s["id"])
            lst.addItem(item)
        lay.addWidget(lst)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject)
        lay.addWidget(btns)
        if dlg.exec_() == QDialog.Accepted:
            for item in lst.selectedItems():
                sid = item.data(Qt.UserRole)
                self.db.mark_attendance(session_id, sid, "present", "manual")
                if sid not in self._recognized_ids:
                    self._recognized_ids.add(sid)
                    list_item = QListWidgetItem(f"📋 {item.text()} [Thủ công]")
                    self.list_recognized.addItem(list_item)
            self.lbl_count.setText(f"{len(self._recognized_ids)} sinh viên đã điểm danh")

    def closeEvent(self, event):
        self._stop()
        super().closeEvent(event)
