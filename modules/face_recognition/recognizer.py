"""
modules/face_recognition/recognizer.py
──────────────────────────────────────
So khớp encoding khuôn mặt phát hiện được với database.

Hỗ trợ hai backend:
  • face_recognition (Euclidean distance) – chính xác
  • OpenCV LBPH classifier – fallback

Công khai:
    FaceRecognizer       – class chính
    RecognitionResult    – dataclass kết quả nhận diện một khuôn mặt
    KnownFace            – dataclass đặc tả một khuôn mặt đã biết
"""
from __future__ import annotations

import pickle
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

import numpy as np

logger = logging.getLogger(__name__)

Encoding = np.ndarray


@dataclass
class KnownFace:
    """Một khuôn mặt đã đăng ký trong hệ thống."""

    student_id: int
    student_code: str
    full_name: str
    encoding: Encoding

    @classmethod
    def from_db_row(cls, row: dict) -> Optional["KnownFace"]:
        """Tạo KnownFace từ dict trả về bởi db_manager.get_students_with_face()."""
        raw = row.get("face_encoding")
        if raw is None:
            return None
        try:
            enc = pickle.loads(raw)
            if not isinstance(enc, np.ndarray):
                return None
            return cls(
                student_id=row["id"],
                student_code=row.get("student_code", ""),
                full_name=row.get("full_name", ""),
                encoding=enc,
            )
        except Exception as e:
            logger.warning(f"Lỗi load encoding cho SV {row.get('student_code')}: {e}")
            return None


@dataclass
class RecognitionResult:
    """Kết quả nhận diện một khuôn mặt từ encoding."""

    matched: bool = False
    student_id: Optional[int] = None
    student_code: str = ""
    full_name: str = ""
    distance: float = 1.0
    confidence: float = 0.0  # 0-100%
    backend: str = ""

    def __str__(self) -> str:
        if self.matched:
            return f"{self.full_name} ({self.student_code}) - {self.confidence:.1f}%"
        return f"Không nhận diện - Distance: {self.distance:.2f}"


class FaceRecognizer:
    """
    So khớp encoding khuôn mặt với danh sách khuôn mặt đã đăng ký.

    Parameters
    ----------
    tolerance : float
        Ngưỡng khoảng cách Euclidean (face_recognition).
        0.4 = nghiêm ngặt, 0.6 = dễ chấp nhận. Mặc định 0.5.
    lbph_threshold : float
        Ngưỡng confidence cho LBPH (OpenCV). Thấp hơn = nghiêm ngặt hơn.
    """

    def __init__(self, tolerance: float = 0.5, lbph_threshold: float = 80.0):
        self.tolerance = tolerance
        self.lbph_threshold = lbph_threshold
        self._fr_available = self._check_fr()
        self._known: List[KnownFace] = []
        self._lbph_model = None  # OpenCV LBPH model (lazy train)
        self._lbph_id_map: Dict[int, KnownFace] = {}  # label_int → KnownFace

    # ── Quản lý danh sách khuôn mặt đã biết ────────────────────────────────────

    def load_from_db(self, db_rows: List[dict]) -> int:
        """
        Load danh sách khuôn mặt từ database.

        Parameters
        ----------
        db_rows : List[dict]
            Danh sách dict từ db_manager.get_students_with_face().

        Returns
        -------
        int
            Số lượng khuôn mặt được load thành công.
        """
        self._known = []
        self._lbph_id_map = {}
        count = 0

        for row in db_rows:
            known_face = KnownFace.from_db_row(row)
            if known_face:
                self._known.append(known_face)
                count += 1

        if not self._fr_available:
            self._train_lbph()

        logger.info(f"Đã load {count} khuôn mặt từ database")
        return count

    def add_known_face(self, known_face: KnownFace) -> None:
        """Thêm một khuôn mặt mới (không cần load lại toàn bộ)."""
        # Xóa entry cũ nếu đã có
        self._known = [k for k in self._known if k.student_id != known_face.student_id]
        self._known.append(known_face)
        if not self._fr_available:
            self._train_lbph()

    def count(self) -> int:
        return len(self._known)

    def is_ready(self) -> bool:
        """True nếu đã có ít nhất một khuôn mặt được nạp."""
        return len(self._known) > 0

    # ── Nhận diện ──────────────────────────────────────────────────────────────

    def recognize(self, encoding: np.ndarray) -> RecognitionResult:
        """
        Nhận diện một encoding (từ FaceEncoder).

        Returns
        -------
        RecognitionResult
        """
        if not self._known:
            return RecognitionResult(False, backend="none", distance=1.0)

        if self._fr_available:
            return self._recognize_fr(encoding)
        return self._recognize_lbph(encoding)

    def recognize_batch(self, encodings: List[np.ndarray]) -> List[RecognitionResult]:
        """Nhận diện nhiều encoding cùng lúc (một frame nhiều mặt)."""
        return [self.recognize(enc) for enc in encodings]

    # ── face_recognition backend ───────────────────────────────────────────────

    def _recognize_fr(self, encoding: np.ndarray) -> RecognitionResult:
        """Nhận diện dùng face_recognition (Euclidean distance)."""
        import face_recognition

        known_encodings = [k.encoding for k in self._known]
        distances = face_recognition.face_distance(known_encodings, encoding)
        min_idx = np.argmin(distances)
        min_dist = distances[min_idx]

        if min_dist <= self.tolerance:
            matched_face = self._known[min_idx]
            confidence = (1 - min_dist) * 100
            return RecognitionResult(
                matched=True,
                student_id=matched_face.student_id,
                student_code=matched_face.student_code,
                full_name=matched_face.full_name,
                distance=min_dist,
                confidence=confidence,
                backend="face_recognition",
            )

        return RecognitionResult(
            matched=False,
            distance=min_dist,
            backend="face_recognition",
        )

    # ── OpenCV LBPH fallback ───────────────────────────────────────────────────

    def _train_lbph(self) -> None:
        """Train LBPH model từ danh sách khuôn mặt đã biết."""
        if not self._known:
            return

        self._lbph_model = cv2.face.LBPHFaceRecognizer_create()
        self._lbph_id_map = {}

        encodings = []
        labels = []

        for i, known_face in enumerate(self._known):
            encodings.append(known_face.encoding.reshape(1, -1))
            labels.append(i)
            self._lbph_id_map[i] = known_face

        encodings_array = np.vstack(encodings)
        self._lbph_model.train(encodings_array, np.array(labels))

    def _recognize_lbph(self, encoding: np.ndarray) -> RecognitionResult:
        """Nhận diện dùng LBPH (fallback)."""
        if self._lbph_model is None or not self._lbph_id_map:
            return RecognitionResult(
                matched=False, backend="lbph", distance=1.0
            )

        label, confidence = self._lbph_model.predict(encoding.reshape(1, -1))

        if confidence < self.lbph_threshold:
            matched_face = self._lbph_id_map[label]
            confidence_pct = (1 - confidence / 255) * 100
            return RecognitionResult(
                matched=True,
                student_id=matched_face.student_id,
                student_code=matched_face.student_code,
                full_name=matched_face.full_name,
                distance=float(confidence),
                confidence=confidence_pct,
                backend="lbph",
            )

        return RecognitionResult(
            matched=False,
            distance=float(confidence),
            backend="lbph",
        )

    # ── Utilities ──────────────────────────────────────────────────────────────

    @staticmethod
    def _check_fr() -> bool:
        """Kiểm tra xem face_recognition có được cài hay không."""
        try:
            import face_recognition
            return True
        except ImportError:
            return False


# Import cv2 ở cuối tránh lỗi circular
import cv2
