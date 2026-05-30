"""
modules/attendance/reporter.py
───────────────────────────────
Tạo báo cáo điểm danh.

Công khai:
    AttendanceReporter  – Tạo báo cáo điểm danh
"""
from __future__ import annotations

import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AttendanceReporter:
    """
    Tạo báo cáo điểm danh.
    """

    @staticmethod
    def generate_daily_report(attendance_records: List[dict]) -> dict:
        """
        Tạo báo cáo điểm danh hàng ngày.

        Parameters
        ----------
        attendance_records : List[dict]
            Danh sách records từ database.

        Returns
        -------
        dict
            Báo cáo với các thống kê.
        """
        total = len(attendance_records)
        present = len([r for r in attendance_records if r["status"] == "present"])
        late = len([r for r in attendance_records if r["status"] == "late"])
        absent = total - present - late

        return {
            "date": datetime.now().date().isoformat(),
            "total_students": total,
            "present": present,
            "late": late,
            "absent": absent,
            "present_rate": (present / total * 100) if total > 0 else 0,
        }

    @staticmethod
    def generate_student_report(
        student_id: int, attendance_records: List[dict], days: int = 30
    ) -> dict:
        """
        Tạo báo cáo điểm danh cho một sinh viên (N ngày gần nhất).

        Parameters
        ----------
        student_id : int
            ID sinh viên.
        attendance_records : List[dict]
            Danh sách tất cả records từ database.
        days : int
            Số ngày tính lại.

        Returns
        -------
        dict
            Báo cáo với các thống kê.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        student_records = [
            r
            for r in attendance_records
            if r["student_id"] == student_id
            and datetime.fromisoformat(r["check_time"]) >= cutoff_date
        ]

        total = len(student_records)
        present = len([r for r in student_records if r["status"] == "present"])
        late = len([r for r in student_records if r["status"] == "late"])
        absent = total - present - late

        return {
            "student_id": student_id,
            "period_days": days,
            "total_sessions": total,
            "present": present,
            "late": late,
            "absent": absent,
            "attendance_rate": ((present + late) / total * 100) if total > 0 else 0,
        }
