"""
modules/teacher/teacher_manager.py
──────────────────────────────────
Quản lý giáo viên.

Công khai:
    TeacherManager  – Quản lý CRUD giáo viên
"""
from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class TeacherManager:
    """
    Quản lý giáo viên.
    """

    def __init__(self, db):
        self.db = db

    def get_all(self) -> List[dict]:
        """Lấy tất cả giáo viên."""
        return self.db.get_all_teachers()

    def get_by_id(self, teacher_id: int) -> Optional[dict]:
        """Lấy giáo viên theo ID."""
        teachers = self.db.get_all_teachers()
        for t in teachers:
            if t["id"] == teacher_id:
                return t
        return None

    def add(self, data: dict) -> bool:
        """Thêm giáo viên mới."""
        try:
            self.db.add_teacher(data)
            logger.info(f"Đã thêm giáo viên: {data.get('full_name')}")
            return True
        except Exception as e:
            logger.error(f"Lỗi thêm giáo viên: {e}")
            return False

    def update(self, teacher_id: int, data: dict) -> bool:
        """Cập nhật giáo viên."""
        try:
            self.db.update_teacher(teacher_id, data)
            logger.info(f"Đã cập nhật giáo viên: {teacher_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi cập nhật giáo viên: {e}")
            return False

    def delete(self, teacher_id: int) -> bool:
        """Xóa giáo viên."""
        try:
            self.db.delete_teacher(teacher_id)
            logger.info(f"Đã xóa giáo viên: {teacher_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi xóa giáo viên: {e}")
            return False
