"""
modules/photo/photo_manager.py
───────────────────────────────
Quản lý ảnh sinh viên.

Công khai:
    PhotoManager  – Quản lý lưu, đọc, xóa ảnh
"""
from __future__ import annotations

import logging
import os
import shutil
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class PhotoManager:
    """
    Quản lý ảnh sinh viên.

    Parameters
    ----------
    photo_dir : str
        Thư mục lưu ảnh sinh viên.
    """

    def __init__(self, photo_dir: str):
        self.photo_dir = photo_dir
        os.makedirs(photo_dir, exist_ok=True)

    def save_photo(self, image_path: str, student_code: str) -> Optional[str]:
        """
        Lưu ảnh sinh viên.

        Parameters
        ----------
        image_path : str
            Đường dẫn ảnh nguồn.
        student_code : str
            Mã sinh viên.

        Returns
        -------
        str or None
            Đường dẫn ảnh lưu hoặc None nếu lỗi.
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Ảnh không tồn tại: {image_path}")
                return None

            ext = os.path.splitext(image_path)[1]
            dest_path = os.path.join(self.photo_dir, f"{student_code}{ext}")
            shutil.copy2(image_path, dest_path)
            logger.info(f"Đã lưu ảnh: {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"Lỗi lưu ảnh: {e}")
            return None

    def get_photo(self, student_code: str) -> Optional[str]:
        """
        Lấy đường dẫn ảnh của sinh viên.

        Parameters
        ----------
        student_code : str
            Mã sinh viên.

        Returns
        -------
        str or None
            Đường dẫn ảnh hoặc None nếu không tồn tại.
        """
        for ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            path = os.path.join(self.photo_dir, f"{student_code}{ext}")
            if os.path.exists(path):
                return path
        return None

    def delete_photo(self, student_code: str) -> bool:
        """
        Xóa ảnh sinh viên.

        Parameters
        ----------
        student_code : str
            Mã sinh viên.

        Returns
        -------
        bool
            True nếu xóa thành công, False nếu không.
        """
        photo_path = self.get_photo(student_code)
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
                logger.info(f"Đã xóa ảnh: {photo_path}")
                return True
            except Exception as e:
                logger.error(f"Lỗi xóa ảnh: {e}")
                return False
        return False

    def get_all_photos(self) -> List[str]:
        """
        Lấy danh sách tất cả ảnh trong thư mục.

        Returns
        -------
        List[str]
            Danh sách đường dẫn ảnh.
        """
        return [
            os.path.join(self.photo_dir, f)
            for f in os.listdir(self.photo_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
        ]
