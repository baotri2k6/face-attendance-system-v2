"""
modules/face_recognition/encoder.py
────────────────────────────────────
Trích xuất vector đặc trưng (encoding) từ khuôn mặt.

Hỗ trợ hai backend:
  • face_recognition (chính xác, 128D vector)
  • OpenCV LBPH (fallback)

Công khai:
    FaceEncoder     – class chính
    EncodingResult  – dataclass kết quả encoding
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)

Encoding = np.ndarray
FaceLocation = Tuple[int, int, int, int]  # (top, right, bottom, left)


@dataclass
class EncodingResult:
    """Kết quả trích xuất encoding từ khuôn mặt."""
    encoding: Optional[Encoding] = None
    success: bool = False
    message: str = ""
    backend: str = ""  # "face_recognition" hoặc "lbph"


class FaceEncoder:
    """
    Trích xuất vector đặc trưng (encoding) từ khuôn mặt.

    Parameters
    ----------
    model : "small" | "large"
        Model accuracy cho face_recognition.
        - "small" : nhanh hơn
        - "large" : chính xác hơn (mặc định)
    """

    def __init__(self, model: str = "small"):
        self.model = model
        self._fr_available = self._check_fr()
        self._lbph: Optional[cv2.face.LBPHFaceRecognizer] = None

        if not self._fr_available:
            logger.warning(
                "face_recognition chưa cài. FaceEncoder dùng chế độ giới hạn "
                "(OpenCV LBPH – chỉ dùng được sau khi train)."
            )

    # ── Public API ─────────────────────────────────────────────────────────────

    def encode_from_file(
        self, image_path: str, known_location: Optional[FaceLocation] = None
    ) -> EncodingResult:
        """
        Tạo encoding từ file ảnh.

        Parameters
        ----------
        known_location : tuple, optional
            (top, right, bottom, left) đã phát hiện bởi FaceDetector.
            Nếu có, chỉ encode khuôn mặt tại vị trí đó (nhanh hơn).
        """
        if self._fr_available:
            return self._encode_fr_file(image_path, known_location)
        return self._encode_lbph_file(image_path)

    def encode_from_frame(
        self, frame_bgr: np.ndarray, known_location: Optional[FaceLocation] = None
    ) -> EncodingResult:
        """
        Tạo encoding từ numpy frame BGR (từ camera).

        Parameters
        ----------
        known_location : tuple, optional
            (top, right, bottom, left) đã phát hiện bởi FaceDetector.
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return EncodingResult(None, False, "Frame rỗng")

        if self._fr_available:
            return self._encode_fr_frame(frame_bgr, known_location)
        return self._encode_lbph_frame(frame_bgr, known_location)

    def encode_batch(self, image_paths: List[str]) -> List[EncodingResult]:
        """Encode nhiều ảnh một lúc. Hữu ích khi đăng ký từ nhiều góc độ."""
        results = []
        for path in image_paths:
            results.append(self.encode_from_file(path))
        return results

    def is_face_recognition_available(self) -> bool:
        return self._fr_available

    # ── face_recognition backend ───────────────────────────────────────────────

    def _encode_fr_file(
        self, image_path: str, known_location: Optional[FaceLocation]
    ) -> EncodingResult:
        import face_recognition

        try:
            img = face_recognition.load_image_file(image_path)
            locs = [known_location] if known_location else None
            encs = face_recognition.face_encodings(
                img, known_face_locations=locs, model=self.model
            )
            if not encs:
                return EncodingResult(
                    None,
                    False,
                    "Không tìm thấy khuôn mặt trong ảnh",
                    "face_recognition",
                )
            return EncodingResult(encs[0], True, backend="face_recognition")
        except Exception as e:
            return EncodingResult(None, False, str(e), "face_recognition")

    def _encode_fr_frame(
        self, frame_bgr: np.ndarray, known_location: Optional[FaceLocation]
    ) -> EncodingResult:
        import face_recognition

        try:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            locs = [known_location] if known_location else None
            encs = face_recognition.face_encodings(
                rgb, known_face_locations=locs, model=self.model
            )
            if not encs:
                return EncodingResult(
                    None,
                    False,
                    "Không tìm thấy khuôn mặt trong frame",
                    "face_recognition",
                )
            return EncodingResult(encs[0], True, backend="face_recognition")
        except Exception as e:
            return EncodingResult(None, False, str(e), "face_recognition")

    # ── OpenCV LBPH fallback ───────────────────────────────────────────────────

    def _encode_lbph_file(self, image_path: str) -> EncodingResult:
        """Fallback: trích xuất histogram LBP từ vùng mặt."""
        try:
            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                return EncodingResult(
                    None, False, f"Không đọc được ảnh: {image_path}", "lbph"
                )
            return self._encode_lbph_frame(img_bgr)
        except Exception as e:
            return EncodingResult(None, False, str(e), "lbph")

    def _encode_lbph_frame(
        self, frame_bgr: np.ndarray, known_location: Optional[FaceLocation] = None
    ) -> EncodingResult:
        """Trích xuất LBP histogram từ frame."""
        try:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

            # Nếu có vị trí khuôn mặt, chỉ crop vùng đó
            if known_location:
                top, right, bottom, left = known_location
                gray = gray[top:bottom, left:right]

            # Tính LBP histogram
            hist = self._compute_lbp_histogram(gray)
            return EncodingResult(hist, True, backend="lbph")
        except Exception as e:
            return EncodingResult(None, False, str(e), "lbph")

    @staticmethod
    def _compute_lbp_histogram(gray: np.ndarray, radius: int = 1) -> np.ndarray:
        """Tính LBP histogram từ ảnh xám."""
        from skimage.feature import local_binary_pattern

        lbp = local_binary_pattern(gray, 8, radius, method="uniform")
        hist, _ = np.histogram(lbp, bins=59, range=(0, 59))
        return hist.astype(np.float32)

    # ── Utilities ──────────────────────────────────────────────────────────────

    @staticmethod
    def _check_fr() -> bool:
        """Kiểm tra xem face_recognition có được cài hay không."""
        try:
            import face_recognition
            return True
        except ImportError:
            return False
