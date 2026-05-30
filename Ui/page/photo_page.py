"""
Trang xem ảnh sinh viên & đăng ký khuôn mặt
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QScrollArea, QGridLayout, QFileDialog,
                              QComboBox, QFrame, QMessageBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
import os
import shutil
import sys
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import PHOTO_DIR, FACE_DIR
from modules.face_recognition import simple_encoder

PAGE_STYLE = """
QWidget { background: #e8eef5; }
QScrollArea { border: none; }
QComboBox { border:1.5px solid #e2e8f0; border-radius:6px; padding:6px; font-size:12px; min-width:200px; }
"""


# ─────────────────────────────────────────────────────────────────────────────
#  Dialog chụp ảnh từ camera
# ─────────────────────────────────────────────────────────────────────────────
class CaptureDialog(QDialog):
    """Mở camera, hiển thị live feed, cho phép chụp ảnh."""

    def __init__(self, student_name="", parent=None):
        super().__init__(parent)
        self.student_name = student_name
        self.captured_frame = None   # numpy BGR frame sau khi chụp
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

        self.setWindowTitle(f"📸 Chụp khuôn mặt — {student_name}")
        self.setMinimumSize(660, 540)
        self.setStyleSheet("""
            QDialog  { background: #1a2035; }
            QLabel   { color: #e2e8f0; }
            QPushButton {
                border-radius: 8px; padding: 8px 20px;
                font-size: 13px; font-weight: 600; border: none;
            }
        """)
        self._build_ui()
        self._open_camera()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Tiêu đề nhỏ
        title = QLabel(f"Đặt khuôn mặt vào khung và nhấn  📸 Chụp")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color:#a0aec0; font-size:12px;")
        lay.addWidget(title)

        # Khung camera
        cam_wrapper = QFrame()
        cam_wrapper.setStyleSheet("""
            QFrame {
                background: #0d1422;
                border: 2px solid #2d3a55;
                border-radius: 12px;
            }
        """)
        cam_lay = QVBoxLayout(cam_wrapper)
        cam_lay.setContentsMargins(8, 8, 8, 8)

        self.lbl_cam = QLabel("⏳ Đang khởi động camera...")
        self.lbl_cam.setAlignment(Qt.AlignCenter)
        self.lbl_cam.setMinimumSize(620, 420)
        self.lbl_cam.setStyleSheet("color:#718096; font-size:14px; background:transparent;")
        cam_lay.addWidget(self.lbl_cam)
        lay.addWidget(cam_wrapper)

        # Trạng thái
        self.lbl_status = QLabel("Sẵn sàng")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color:#48bb78; font-size:12px;")
        lay.addWidget(self.lbl_status)

        # Nút
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_capture = QPushButton("📸  Chụp ảnh")
        self.btn_capture.setStyleSheet("""
            QPushButton { background: #FF5722; color: white; }
            QPushButton:hover { background: #e64a19; }
            QPushButton:disabled { background: #555; color: #999; }
        """)
        self.btn_capture.setCursor(Qt.PointingHandCursor)
        self.btn_capture.clicked.connect(self._capture)

        self.btn_retake = QPushButton("🔄  Chụp lại")
        self.btn_retake.setStyleSheet("""
            QPushButton { background: #3182ce; color: white; }
            QPushButton:hover { background: #2b6cb0; }
        """)
        self.btn_retake.setCursor(Qt.PointingHandCursor)
        self.btn_retake.clicked.connect(self._retake)
        self.btn_retake.setVisible(False)

        self.btn_ok = QPushButton("✅  Xác nhận & Lưu")
        self.btn_ok.setStyleSheet("""
            QPushButton { background: #38a169; color: white; }
            QPushButton:hover { background: #276749; }
        """)
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setVisible(False)

        btn_cancel = QPushButton("✖  Hủy")
        btn_cancel.setStyleSheet("""
            QPushButton { background: #4a5568; color: white; }
            QPushButton:hover { background: #2d3748; }
        """)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_capture)
        btn_row.addWidget(self.btn_retake)
        btn_row.addWidget(self.btn_ok)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        lay.addLayout(btn_row)

    # ── Camera ────────────────────────────────────────────────────────────────
    def _open_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.lbl_cam.setText("❌ Không thể mở camera!\nKiểm tra lại thiết bị.")
            self.btn_capture.setEnabled(False)
            return
        self.timer.start(33)   # ~30fps

    def _update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        self._show_frame(frame, draw_guide=True)

    def _show_frame(self, frame, draw_guide=False):
        display = frame.copy()

        if draw_guide:
            # Vẽ khung hướng dẫn đặt mặt
            h, w = display.shape[:2]
            cx, cy = w // 2, h // 2
            rx, ry = 110, 140
            # Ellipse hướng dẫn
            cv2.ellipse(display, (cx, cy), (rx, ry), 0, 0, 360, (80, 200, 120), 2)
            # 4 góc bo
            for x0, y0, x1, y1 in [
                (cx-rx-10, cy-ry-10, cx-rx+20, cy-ry+20),
                (cx+rx-20, cy-ry-10, cx+rx+10, cy-ry+20),
                (cx-rx-10, cy+ry-20, cx-rx+20, cy+ry+10),
                (cx+rx-20, cy+ry-20, cx+rx+10, cy+ry+10),
            ]:
                cv2.line(display, (x0, y0), (x0+20, y0), (255,140,0), 3)
                cv2.line(display, (x0, y0), (x0, y0+20), (255,140,0), 3)
            cv2.putText(display, "Dat khuon mat vao trong khung",
                        (w//2 - 155, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1)

        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            self.lbl_cam.width(), self.lbl_cam.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.lbl_cam.setPixmap(pix)

    def _capture(self):
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        # Dừng live feed, hiện ảnh chụp
        self.timer.stop()
        self.captured_frame = frame
        self._show_frame(frame, draw_guide=False)

        self.lbl_status.setText("✅ Đã chụp! Kiểm tra ảnh rồi nhấn Xác nhận hoặc Chụp lại.")
        self.lbl_status.setStyleSheet("color:#68d391; font-size:12px;")
        self.btn_capture.setVisible(False)
        self.btn_retake.setVisible(True)
        self.btn_ok.setVisible(True)

    def _retake(self):
        self.captured_frame = None
        self.lbl_status.setText("Sẵn sàng chụp lại")
        self.lbl_status.setStyleSheet("color:#48bb78; font-size:12px;")
        self.btn_capture.setVisible(True)
        self.btn_retake.setVisible(False)
        self.btn_ok.setVisible(False)
        self.timer.start(33)

    # ── Cleanup ───────────────────────────────────────────────────────────────
    def closeEvent(self, event):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        super().closeEvent(event)

    def reject(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        super().reject()

    def accept(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        super().accept()


# ─────────────────────────────────────────────────────────────────────────────
#  PhotoPage chính
# ─────────────────────────────────────────────────────────────────────────────
class PhotoPage(QWidget):
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
        title = QLabel("🖼  Xem ảnh sinh viên")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a2035;")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Sinh viên:"))
        self.cmb_student = QComboBox()
        self.cmb_student.setMinimumWidth(250)
        ctrl.addWidget(self.cmb_student)

        btn_camera = QPushButton("📸 Chụp khuôn mặt")
        btn_camera.setStyleSheet("background:#FF5722;color:white;border-radius:6px;padding:6px 14px;border:none;font-size:12px;font-weight:600;")
        btn_camera.setCursor(Qt.PointingHandCursor)
        btn_camera.clicked.connect(self._capture_face)
        ctrl.addWidget(btn_camera)

        btn_upload = QPushButton("📂 Tải ảnh lên")
        btn_upload.setStyleSheet("background:#3182ce;color:white;border-radius:6px;padding:6px 14px;border:none;font-size:12px;")
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.clicked.connect(self._upload_photo)
        ctrl.addWidget(btn_upload)

        btn_face = QPushButton("👁 Đăng ký khuôn mặt")
        btn_face.setStyleSheet("background:#805ad5;color:white;border-radius:6px;padding:6px 14px;border:none;font-size:12px;")
        btn_face.setCursor(Qt.PointingHandCursor)
        btn_face.clicked.connect(self._register_face)
        ctrl.addWidget(btn_face)

        btn_refresh = QPushButton("🔄 Làm mới")
        btn_refresh.setStyleSheet("background:#38a169;color:white;border-radius:6px;padding:6px 14px;border:none;font-size:12px;")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.clicked.connect(self.refresh)
        ctrl.addWidget(btn_refresh)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        # Photo grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{background:white; border-radius:10px; border:none;}")
        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(10)
        self._grid.setContentsMargins(12, 12, 12, 12)
        self.scroll.setWidget(self._container)
        layout.addWidget(self.scroll)

        self.lbl_total = QLabel("0 ảnh")
        self.lbl_total.setStyleSheet("color:#718096; font-size:11px;")
        layout.addWidget(self.lbl_total)

    # ── Data ──────────────────────────────────────────────────────────────────
    def refresh(self):
        students = self.db.get_all_students()
        self.cmb_student.clear()
        self.cmb_student.addItem("-- Chọn sinh viên --", None)
        for s in students:
            self.cmb_student.addItem(f"{s['student_code']} - {s['full_name']}", s["id"])
        self._load_all_photos(students)

    def _load_all_photos(self, students):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 5
        count = 0
        for i, s in enumerate(students):
            card = QFrame()
            card.setFixedSize(140, 190)
            card.setStyleSheet("QFrame{background:#f0f4f8; border-radius:8px;}")
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(6, 6, 6, 6)
            card_lay.setSpacing(4)

            img_lbl = QLabel()
            img_lbl.setFixedSize(128, 120)
            img_lbl.setAlignment(Qt.AlignCenter)
            img_lbl.setStyleSheet("background:#d1d9e0; border-radius:6px; font-size:36px;")

            photo = s.get("photo_path", "")
            if photo and os.path.exists(photo):
                pix = QPixmap(photo).scaled(128, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_lbl.setPixmap(pix)
                count += 1
            else:
                img_lbl.setText("👤")

            card_lay.addWidget(img_lbl)

            name = QLabel(s.get("full_name", ""))
            name.setAlignment(Qt.AlignCenter)
            name.setWordWrap(True)
            name.setStyleSheet("font-size:10px; font-weight:bold; color:#2d3748;")
            card_lay.addWidget(name)

            code = QLabel(s.get("student_code", ""))
            code.setAlignment(Qt.AlignCenter)
            code.setStyleSheet("font-size:9px; color:#718096;")
            card_lay.addWidget(code)

            has_face = bool(s.get("face_encoding") or (photo and os.path.exists(photo)))
            badge = QLabel("👁 Đã đăng ký" if has_face else "❌ Chưa đăng ký")
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(f"font-size:9px; color:{'#276749' if has_face else '#e53e3e'};")
            card_lay.addWidget(badge)

            self._grid.addWidget(card, i // cols, i % cols)

        self.lbl_total.setText(f"{count} ảnh / {len(students)} sinh viên")

    # ── Actions ───────────────────────────────────────────────────────────────
    def _get_selected_student(self):
        sid = self.cmb_student.currentData()
        if not sid:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn sinh viên!")
            return None, None
        student = self.db.get_student(sid)
        return sid, student

    def _capture_face(self):
        """Mở camera để chụp ảnh khuôn mặt trực tiếp."""
        sid, student = self._get_selected_student()
        if not student:
            return

        dlg = CaptureDialog(student_name=student["full_name"], parent=self)
        if dlg.exec_() != QDialog.Accepted:
            return

        frame = dlg.captured_frame
        if frame is None:
            return

        # Lưu ảnh vào thư mục photos
        import numpy as np
        os.makedirs(PHOTO_DIR, exist_ok=True)
        dest = os.path.join(PHOTO_DIR, f"{student['student_code']}.jpg")
        cv2.imwrite(dest, frame)

        # Cập nhật DB
        student["photo_path"] = dest
        self.db.update_student(sid, student)

        # Tự động đăng ký khuôn mặt luôn
        self._auto_register(sid, student, dest)

    def _auto_register(self, sid, student, photo_path):
        """Đăng ký encoding ngay sau khi chụp."""
        try:
            enc, backend, message = self._create_face_encoding(photo_path)
            if enc is None:
                QMessageBox.warning(
                    self, "Cảnh báo",
                    f"Đã lưu ảnh cho {student['full_name']} nhưng {message}.\n"
                    "Vui lòng chụp lại với ánh sáng tốt hơn hoặc đăng ký khuôn mặt thủ công."
                )
            else:
                import pickle
                self.db.save_face_encoding(sid, pickle.dumps(enc))
                QMessageBox.information(
                    self, "Thành công",
                    f"Đã chụp và đăng ký khuôn mặt cho {student['full_name']}!\n"
                    f"Backend: {backend}"
                )
        except Exception as e:
            QMessageBox.warning(self, "Cảnh báo", f"Đã lưu ảnh nhưng lỗi encoding:\n{e}")

        self.refresh()

    def _upload_photo(self):
        sid, student = self._get_selected_student()
        if not student:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not path:
            return
        ext = os.path.splitext(path)[1]
        dest = os.path.join(PHOTO_DIR, f"{student['student_code']}{ext}")
        os.makedirs(PHOTO_DIR, exist_ok=True)
        shutil.copy2(path, dest)
        student["photo_path"] = dest
        self.db.update_student(sid, student)
        QMessageBox.information(self, "Thành công", f"Đã lưu ảnh cho {student['full_name']}!")
        self.refresh()

    def _register_face(self):
        sid, student = self._get_selected_student()
        if not student:
            return
        photo = student.get("photo_path", "")
        if not photo or not os.path.exists(photo):
            QMessageBox.warning(self, "Thông báo", "Sinh viên chưa có ảnh.\nVui lòng chụp hoặc tải ảnh trước!")
            return
        try:
            import pickle
            enc, backend, message = self._create_face_encoding(photo)
            if enc is None:
                QMessageBox.warning(self, "Thông báo", message)
                return
            enc_bytes = pickle.dumps(enc)
            self.db.save_face_encoding(sid, enc_bytes)
            QMessageBox.information(
                self,
                "Thành công",
                f"Đã đăng ký khuôn mặt cho {student['full_name']}!\nBackend: {backend}"
            )
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _create_face_encoding(self, photo_path):
        try:
            import face_recognition
            img = face_recognition.load_image_file(photo_path)
            encs = face_recognition.face_encodings(img)
            if encs:
                return encs[0], "face_recognition", ""
            return None, "face_recognition", "không tìm thấy khuôn mặt trong ảnh"
        except ImportError:
            result = simple_encoder.encode_from_file(photo_path)
            if result.success:
                return result.encoding, "opencv_lbp", ""
            return None, "opencv_lbp", result.message
