"""
modules/photo/thumbnail.py
────────────────────────────
Xử lý thumbnail, convert frame sang QPixmap.

Công khai:
    ThumbnailManager  – Tạo thumbnail từ ảnh
    frame_to_pixmap   – Convert frame OpenCV sang QPixmap
"""
from __future__ import annotations

import logging
import os
from typing import Optional
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ThumbnailManager:
    """
    Tạo và quản lý thumbnail.

    Parameters
    ----------
    cache_dir : str
        Thư mục lưu cache thumbnail.
    """

    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def create_thumbnail(self, image_path: str, size: tuple = (128, 128)) -> Optional[str]:
        """
        Tạo thumbnail từ ảnh.

        Parameters
        ----------
        image_path : str
            Đường dẫn ảnh gốc.
        size : tuple
            Kích thước thumbnail (width, height).

        Returns
        -------
        str or None
            Đường dẫn thumbnail hoặc None nếu lỗi.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Không đọc được ảnh: {image_path}")
                return None

            thumb = cv2.resize(img, size)
            thumb_name = f"thumb_{Path(image_path).stem}.jpg"
            thumb_path = os.path.join(self.cache_dir, thumb_name)
            cv2.imwrite(thumb_path, thumb)
            return thumb_path
        except Exception as e:
            logger.error(f"Lỗi tạo thumbnail: {e}")
            return None

    def clear_cache(self) -> None:
        """Xóa tất cả thumbnail trong cache."""
        try:
            for f in os.listdir(self.cache_dir):
                if f.startswith("thumb_"):
                    os.remove(os.path.join(self.cache_dir, f))
            logger.info("Đã xóa cache thumbnail")
        except Exception as e:
            logger.error(f"Lỗi xóa cache: {e}")


def frame_to_pixmap(frame_bgr: np.ndarray):
    """
    Convert frame BGR từ OpenCV sang QPixmap.

    Parameters
    ----------
    frame_bgr : np.ndarray
        Frame BGR từ cv2.VideoCapture.

    Returns
    -------
    QPixmap
        QPixmap object có thể dùng trong PyQt5.
    """
    from PyQt5.QtGui import QPixmap, QImage

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    bytes_per_line = ch * w
    q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(q_img)
