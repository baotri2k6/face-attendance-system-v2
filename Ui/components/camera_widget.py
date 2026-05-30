"""
Camera widget for face capture and recognition
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2


class CameraWidget(QWidget):
    frame_captured = pyqtSignal(object)  # numpy array
    face_detected = pyqtSignal(list)     # list of face locations

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self._running = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_feed = QLabel("Camera chưa khởi động")
        self.lbl_feed.setAlignment(Qt.AlignCenter)
        self.lbl_feed.setMinimumSize(480, 360)
        self.lbl_feed.setStyleSheet("""
            QLabel {
                background: #1a2035;
                color: #a0aec0;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.lbl_feed)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Bật camera")
        self.btn_stop = QPushButton("■ Tắt camera")
        self.btn_capture = QPushButton("📸 Chụp ảnh")

        for btn in [self.btn_start, self.btn_stop, self.btn_capture]:
            btn.setFixedHeight(32)
            btn.setCursor(Qt.PointingHandCursor)

        self.btn_start.setStyleSheet("background:#2ecc71;color:white;border-radius:6px;border:none;")
        self.btn_stop.setStyleSheet("background:#e74c3c;color:white;border-radius:6px;border:none;")
        self.btn_capture.setStyleSheet("background:#3498db;color:white;border-radius:6px;border:none;")

        self.btn_stop.setEnabled(False)

        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_capture.clicked.connect(self._capture)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_capture)
        layout.addLayout(btn_layout)

    def start(self, cam_index=0):
        if self._running:
            return
        self.cap = cv2.VideoCapture(cam_index)
        if self.cap.isOpened():
            self._running = True
            self.timer.start(33)
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)

    def stop(self):
        self._running = False
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.lbl_feed.setText("Camera đã tắt")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def _update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            self.lbl_feed.width(), self.lbl_feed.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.lbl_feed.setPixmap(pix)
        self.frame_captured.emit(frame)

    def _capture(self):
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if ret:
            self.frame_captured.emit(frame)

    def get_current_frame(self):
        if not self.cap or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        return frame if ret else None

    def closeEvent(self, event):
        self.stop()
        super().closeEvent(event)
