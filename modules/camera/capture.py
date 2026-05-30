"""
modules/camera/capture.py
──────────────────────────
Quản lý camera và capture frame.

Công khai:
    CameraManager  – Quản lý camera, capture frame
    FrameBuffer    – Buffer để lưu frame gần nhất
"""
from __future__ import annotations

import logging
from typing import Optional
from collections import deque
import threading

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class FrameBuffer:
    """Buffer FIFO để lưu các frame gần nhất."""

    def __init__(self, maxsize: int = 30):
        self.maxsize = maxsize
        self.buffer: deque = deque(maxlen=maxsize)
        self.lock = threading.Lock()

    def put(self, frame: np.ndarray) -> None:
        """Thêm frame vào buffer."""
        with self.lock:
            self.buffer.append(frame)

    def get(self) -> Optional[np.ndarray]:
        """Lấy frame gần nhất từ buffer."""
        with self.lock:
            if self.buffer:
                return self.buffer[-1]
        return None

    def get_all(self) -> list:
        """Lấy tất cả frame trong buffer."""
        with self.lock:
            return list(self.buffer)

    def clear(self) -> None:
        """Xóa tất cả frame trong buffer."""
        with self.lock:
            self.buffer.clear()

    def size(self) -> int:
        """Số lượng frame hiện tại trong buffer."""
        with self.lock:
            return len(self.buffer)


class CameraManager:
    """
    Quản lý camera, capture frame.

    Parameters
    ----------
    camera_id : int
        ID của camera (0 = default camera).
    fps : int
        Target FPS.
    width : int
        Chiều rộng frame.
    height : int
        Chiều cao frame.
    """

    def __init__(
        self,
        camera_id: int = 0,
        fps: int = 30,
        width: int = 640,
        height: int = 480,
    ):
        self.camera_id = camera_id
        self.fps = fps
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False
        self.frame_buffer = FrameBuffer()

    def open(self) -> bool:
        """Mở camera."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                logger.error(f"Không thể mở camera {self.camera_id}")
                return False

            # Set properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

            self.is_opened = True
            logger.info(f"Mở camera {self.camera_id} thành công")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi mở camera: {e}")
            return False

    def close(self) -> None:
        """Đóng camera."""
        if self.cap:
            self.cap.release()
            self.cap = None
            self.is_opened = False
            logger.info(f"Đóng camera {self.camera_id}")

    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture một frame từ camera."""
        if not self.is_opened or self.cap is None:
            return None

        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Lỗi capture frame")
            return None

        self.frame_buffer.put(frame)
        return frame

    def get_frame(self) -> Optional[np.ndarray]:
        """Lấy frame gần nhất (không capture lại)."""
        return self.frame_buffer.get()

    def get_frame_info(self) -> dict:
        """Lấy thông tin camera."""
        if not self.is_opened or self.cap is None:
            return {}

        return {
            "camera_id": self.camera_id,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        }

    def __del__(self):
        """Cleanup khi object bị destroy."""
        self.close()
