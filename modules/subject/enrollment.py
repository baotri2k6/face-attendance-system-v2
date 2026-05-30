"""
modules/subject/enrollment.py
──────────────────────────────
Quản lý đăng ký môn học.

Công khai:
    EnrollmentManager  – Quản lý đăng ký môn học cho sinh viên
"""
from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class EnrollmentManager:
    """
    Quản lý đăng ký môn học cho sinh viên.
    """

    def __init__(self, db):
        self.db = db

    def enroll_student(
        self, student_id: int, subject_id: int
    ) -> bool:
        """Đăng ký sinh viên vào môn học."""
        try:
            from datetime import datetime

            conn = self.db.get_connection()
            conn.execute(
                "INSERT OR IGNORE INTO enrollments (student_id, subject_id, enrolled_at) VALUES (?, ?, ?)",
                (student_id, subject_id, datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()
            logger.info(f"Đã đăng ký sinh viên {student_id} vào môn {subject_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi đăng ký sinh viên: {e}")
            return False

    def unenroll_student(self, student_id: int, subject_id: int) -> bool:
        """Hủy đăng ký sinh viên khỏi môn học."""
        try:
            conn = self.db.get_connection()
            conn.execute(
                "DELETE FROM enrollments WHERE student_id = ? AND subject_id = ?",
                (student_id, subject_id),
            )
            conn.commit()
            conn.close()
            logger.info(f"Đã hủy đăng ký sinh viên {student_id} khỏi môn {subject_id}")
            return True
        except Exception as e:
            logger.error(f"Lỗi hủy đăng ký: {e}")
            return False

    def get_enrolled_subjects(self, student_id: int) -> List[dict]:
        """Lấy danh sách môn học đã đăng ký của sinh viên."""
        try:
            conn = self.db.get_connection()
            rows = conn.execute(
                """SELECT s.* FROM subjects s
                   INNER JOIN enrollments e ON s.id = e.subject_id
                   WHERE e.student_id = ?""",
                (student_id,),
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Lỗi lấy môn học đăng ký: {e}")
            return []

    def get_enrolled_students(self, subject_id: int) -> List[dict]:
        """Lấy danh sách sinh viên đã đăng ký môn học."""
        try:
            conn = self.db.get_connection()
            rows = conn.execute(
                """SELECT s.* FROM students s
                   INNER JOIN enrollments e ON s.id = e.student_id
                   WHERE e.subject_id = ?""",
                (subject_id,),
            ).fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Lỗi lấy sinh viên đăng ký: {e}")
            return []
