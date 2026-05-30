"""
Fallback face encoder that only depends on OpenCV and numpy.

This is less accurate than the face_recognition/dlib backend, but it lets the
application register and compare faces on machines where dlib is not installed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np


FaceBox = Tuple[int, int, int, int]  # top, right, bottom, left
HAAR_XML = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


@dataclass
class SimpleEncodingResult:
    success: bool
    encoding: np.ndarray | None = None
    message: str = ""
    box: FaceBox | None = None


def detect_faces(frame_bgr: np.ndarray) -> List[FaceBox]:
    if frame_bgr is None or frame_bgr.size == 0:
        return []

    cascade = cv2.CascadeClassifier(HAAR_XML)
    if cascade.empty():
        return []

    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(70, 70),
    )
    boxes: List[FaceBox] = []
    for x, y, w, h in faces:
        boxes.append((int(y), int(x + w), int(y + h), int(x)))
    return boxes


def encode_from_file(image_path: str) -> SimpleEncodingResult:
    frame = cv2.imread(image_path)
    if frame is None:
        return SimpleEncodingResult(False, message=f"Không đọc được ảnh: {image_path}")
    return encode_largest_face(frame)


def encode_largest_face(frame_bgr: np.ndarray) -> SimpleEncodingResult:
    boxes = detect_faces(frame_bgr)
    if not boxes:
        return SimpleEncodingResult(False, message="Không tìm thấy khuôn mặt trong ảnh")

    box = max(boxes, key=lambda b: (b[2] - b[0]) * (b[1] - b[3]))
    encoding = encode_face_box(frame_bgr, box)
    return SimpleEncodingResult(True, encoding=encoding, box=box, message="opencv_lbp")


def encode_face_box(frame_bgr: np.ndarray, box: FaceBox) -> np.ndarray:
    top, right, bottom, left = box
    h, w = frame_bgr.shape[:2]
    pad_y = int((bottom - top) * 0.12)
    pad_x = int((right - left) * 0.12)

    y1 = max(0, top - pad_y)
    y2 = min(h, bottom + pad_y)
    x1 = max(0, left - pad_x)
    x2 = min(w, right + pad_x)

    face = frame_bgr[y1:y2, x1:x2]
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (96, 96), interpolation=cv2.INTER_AREA)
    gray = cv2.equalizeHist(gray)

    lbp = _lbp(gray)
    features = []
    cell = 24
    for y in range(0, 96, cell):
        for x in range(0, 96, cell):
            hist, _ = np.histogram(lbp[y:y + cell, x:x + cell], bins=256, range=(0, 256))
            hist = hist.astype(np.float32)
            hist /= hist.sum() + 1e-7
            features.append(hist)

    return np.concatenate(features).astype(np.float32)


def best_match(
    encoding: np.ndarray,
    known_encodings: List[np.ndarray],
    threshold: float = 0.82,
) -> Tuple[int, float]:
    if not known_encodings:
        return -1, 0.0

    scores = [cosine_similarity(encoding, known) for known in known_encodings]
    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])
    if best_score < threshold:
        return -1, best_score
    return best_idx, best_score


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-7
    return float(np.dot(a, b) / denom)


def _lbp(gray: np.ndarray) -> np.ndarray:
    center = gray[1:-1, 1:-1]
    code = np.zeros_like(center, dtype=np.uint8)
    neighbors = [
        gray[:-2, :-2],
        gray[:-2, 1:-1],
        gray[:-2, 2:],
        gray[1:-1, 2:],
        gray[2:, 2:],
        gray[2:, 1:-1],
        gray[2:, :-2],
        gray[1:-1, :-2],
    ]
    for bit, neighbor in enumerate(neighbors):
        code |= ((neighbor >= center).astype(np.uint8) << bit)

    result = np.zeros_like(gray, dtype=np.uint8)
    result[1:-1, 1:-1] = code
    return result
