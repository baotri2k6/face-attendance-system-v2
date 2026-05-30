"""
modules/face_recognition/detector.py
────────────────────────────────────
Phát hiện khuôn mặt trong frame/ảnh.

Hỗ trợ ba backend:
  • face_recognition HOG (nhanh, CPU)
  • face_recognition CNN (chính xác, cần GPU)
  • OpenCV Haar Cascade (fallback, không cần face_recognition)

Công khai:
    FaceDetector     – class chính
    DetectionResult  – dataclass kết quả phát hiện
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Kết quả phát hiện một khuôn mặt."""
    top: int
    right: int
    bottom: int
    left: int
    confidence: float = 1.0  # Chỉ dùng cho Haar

    def width(self) -> int:
        return self.right - self.left

    def height(self) -> int:
        return self.bottom - self.top

    def center(self) -> tuple:
        return ((self.left + self.right) // 2, (self.top + self.bottom) // 2)


class FaceDetector:
    """
    Phát hiện khuôn mặt.

    Parameters
    ----------
    model : "hog" | "cnn" | "haar"
        Backend sử dụng.
        - "hog"  : face_recognition + HOG (nhanh, CPU)
        - "cnn"  : face_recognition + CNN (chính xác hơn, cần GPU)
        - "haar" : OpenCV Haar Cascade (không cần face_recognition)
        Nếu face_recognition chưa cài, tự động fallback về "haar".
    upsample : int
        Số lần upsample khi dùng HOG/CNN (tăng = phát hiện mặt nhỏ hơn, chậm hơn).
    scale_factor : float
        Hệ số thu nhỏ frame trước khi detect (tăng tốc độ). 0.5 = thu nhỏ 2x.
    min_face_size : int
        Kích thước khuôn mặt tối thiểu (px) cho Haar backend.
    """

    HAAR_XML = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

    def __init__(
        self,
        model: str = "hog",
        upsample: int = 1,
        scale_factor: float = 0.5,
        min_face_size: int = 60,
    ):
        self.model = model
        self.upsample = upsample
        self.scale_factor = scale_factor
        self.min_face_size = min_face_size

        self._fr_available = self._check_face_recognition()
        self._cascade: Optional[cv2.CascadeClassifier] = None

        if not self._fr_available and model in ("hog", "cnn"):
            logger.warning(
                "face_recognition chưa được cài đặt. "
                "Tự động chuyển sang backend 'haar'."
            )
            self.model = "haar"

        if self.model == "haar":
            self._cascade = cv2.CascadeClassifier(self.HAAR_XML)
            if self._cascade.empty():
                raise RuntimeError(
                    f"Không tải được Haar Cascade từ: {self.HAAR_XML}"
                )

    # ── Public API ─────────────────────────────────────────────────────────────

    def detect(self, frame_bgr: np.ndarray) -> List[DetectionResult]:
        """
        Phát hiện khuôn mặt trong frame BGR (từ cv2.VideoCapture).

        Returns
        -------
        List[DetectionResult]
            Danh sách kết quả; rỗng nếu không phát hiện được.
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return []

        if self.model in ("hog", "cnn"):
            return self._detect_fr(frame_bgr)
        return self._detect_haar(frame_bgr)

    def detect_largest(self, frame_bgr: np.ndarray) -> Optional[DetectionResult]:
        """Chỉ trả về khuôn mặt lớn nhất (dùng khi chụp ảnh đăng ký)."""
        results = self.detect(frame_bgr)
        if not results:
            return None
        return max(results, key=lambda r: r.width() * r.height())

    def is_face_recognition_available(self) -> bool:
        return self._fr_available

    # ── face_recognition backend ───────────────────────────────────────────────

    def _detect_fr(self, frame_bgr: np.ndarray) -> List[DetectionResult]:
        """Phát hiện dùng face_recognition (HOG/CNN)."""
        import face_recognition

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        model = "cnn" if self.model == "cnn" else "hog"
        locs = face_recognition.face_locations(
            rgb, number_of_times_to_upsample=self.upsample, model=model
        )
        return [DetectionResult(top, right, bottom, left) for top, right, bottom, left in locs]

    # ── OpenCV Haar Cascade backend ────────────────────────────────────────────

    def _detect_haar(self, frame_bgr: np.ndarray) -> List[DetectionResult]:
        """Phát hiện dùng OpenCV Haar Cascade (fallback)."""
        # Thu nhỏ frame để tăng tốc độ
        h, w = frame_bgr.shape[:2]
        scaled = cv2.resize(
            frame_bgr,
            (int(w * self.scale_factor), int(h * self.scale_factor)),
        )

        gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
        faces = self._cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(self.min_face_size, self.min_face_size),
        )

        results = []
        scale_inv = 1.0 / self.scale_factor
        for x, y, fw, fh in faces:
            # Chuyển lại từ scaled frame sang frame gốc
            left = int(x * scale_inv)
            top = int(y * scale_inv)
            right = int((x + fw) * scale_inv)
            bottom = int((y + fh) * scale_inv)
            results.append(DetectionResult(top, right, bottom, left))

        return results

    # ── Utilities ──────────────────────────────────────────────────────────────

    @staticmethod
    def _check_face_recognition() -> bool:
        """Kiểm tra xem face_recognition có được cài hay không."""
        try:
            import face_recognition
            return True
        except ImportError:
            return False
