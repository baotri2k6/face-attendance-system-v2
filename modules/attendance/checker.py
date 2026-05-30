"""
modules/attendance/checker.py
──────────────────────────────
Kiểm tra điểm danh dựa trên nhận diện khuôn mặt.

Công khai:
    AttendanceChecker  – Quản lý logic kiểm tra điểm danh
    CheckResult        – Kết quả kiểm tra
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Kết quả kiểm tra điểm danh một sinh viên."""

    student_id: int
    student_code: str
    full_name: str
    check_time: datetime
    status: str = "present"  # present, absent, late
    confidence: float = 0.0
    method: str = "face"  # face, manual
    note: str = ""


class AttendanceChecker:
    """
    Quản lý logic kiểm tra điểm danh.

    Parameters
    ----------
    late_threshold_minutes : int
        Số phút sau giờ bắt đầu buổi học được tính là "muộn". Mặc định 15.
    """

    def __init__(self, late_threshold_minutes: int = 15):
        self.late_threshold_minutes = late_threshold_minutes
        self._checked_today: dict = {}  # student_id -> CheckResult

    def check_attendance(
        self,
        student_id: int,
        student_code: str,
        full_name: str,
        confidence: float = 100.0,
        session_start_time: Optional[datetime] = None,
    ) -> CheckResult:
        """
        Kiểm tra điểm danh cho một sinh viên.

        Parameters
        ----------
        session_start_time : datetime, optional
            Thời gian bắt đầu buổi học. Nếu có, sẽ so sánh để xác định "late" hay "present".

        Returns
        -------
        CheckResult
        """
        now = datetime.now()
        status = "present"

        if session_start_time:
            time_diff = now - session_start_time
            if time_diff > timedelta(minutes=self.late_threshold_minutes):
                status = "late"

        result = CheckResult(
            student_id=student_id,
            student_code=student_code,
            full_name=full_name,
            check_time=now,
            status=status,
            confidence=confidence,
            method="face",
        )

        self._checked_today[student_id] = result
        logger.info(
            f"Điểm danh: {full_name} ({student_code}) - {status} - {confidence:.1f}%"
        )
        return result

    def mark_manual(
        self,
        student_id: int,
        student_code: str,
        full_name: str,
        status: str = "present",
    ) -> CheckResult:
        """Đánh dấu điểm danh thủ công."""
        result = CheckResult(
            student_id=student_id,
            student_code=student_code,
            full_name=full_name,
            check_time=datetime.now(),
            status=status,
            confidence=100.0,
            method="manual",
        )
        self._checked_today[student_id] = result
        return result

    def is_already_checked(self, student_id: int) -> bool:
        """Kiểm tra xem sinh viên đã được điểm danh hôm nay hay chưa."""
        return student_id in self._checked_today

    def get_checked_list(self) -> List[CheckResult]:
        """Lấy danh sách sinh viên đã điểm danh hôm nay."""
        return list(self._checked_today.values())

    def clear(self) -> None:
        """Xóa danh sách điểm danh hôm nay."""
        self._checked_today.clear()

    def get_stats(self) -> dict:
        """Lấy thống kê điểm danh hôm nay."""
        results = self.get_checked_list()
        return {
            "total": len(results),
            "present": len([r for r in results if r.status == "present"]),
            "late": len([r for r in results if r.status == "late"]),
            "absent": len([r for r in results if r.status == "absent"]),
        }
