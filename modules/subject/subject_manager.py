"""
modules/subject/subject_manager.py
──────────────────────────────────
Quản lý môn học.

Công khai:
    SubjectManager  – Quản lý CRUD môn học
"""
from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class SubjectManager:
    """
    Quản lý môn học.
    """

    def __init__(self, db):
        self.db = db

    def get_all(self) -> List[dict]:
        """Lấy tất cả môn học."""
        return self.db.get_all_subjects()

    def get_by_id(self, subject_id: int) -> Optional[dict]:
        """Lấy môn học theo ID."""
        subjects = self.db.get_all_subjects()
        for s in subjects:
            if s["id"] == subject_id:
                return s
        return None

    def add(self, data: dict) -> bool:
        """Thêm môn học mới."""
        try:
            self.db.add_subject(data)
            logger.info(f"Đã thêm môn học: {data.get('subject_name')}")
            return True
        except Exception as e:
            logger.error(f"Lỗi thêm môn học: {e}")
            return False

    def update(self, subject_id: int, data: dict) -> bool:
        """Cập nhật môn học."""
        try:
            self.db.update_subject(subject_id, data)
            logger.info(f"Đã cập nhật môn học: {subject_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi cập nhật môn học: {e}")
            return False

    def delete(self, subject_id: int) -> bool:
        """Xóa môn học."""
        try:
            self.db.delete_subject(subject_id)
            logger.info(f"Đã xóa môn học: {subject_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi xóa môn học: {e}")
            return False
