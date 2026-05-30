"""
Định nghĩa các model dữ liệu
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Student:
    id: Optional[int] = None
    student_code: str = ""
    full_name: str = ""
    class_name: str = ""
    email: str = ""
    phone: str = ""
    face_encoding: Optional[bytes] = None
    photo_path: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "student_code": self.student_code,
            "full_name": self.full_name,
            "class_name": self.class_name,
            "email": self.email,
            "phone": self.phone,
            "photo_path": self.photo_path,
            "created_at": self.created_at,
        }


@dataclass
class Teacher:
    id: Optional[int] = None
    teacher_code: str = ""
    full_name: str = ""
    department: str = ""
    email: str = ""
    phone: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "teacher_code": self.teacher_code,
            "full_name": self.full_name,
            "department": self.department,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at,
        }


@dataclass
class Subject:
    id: Optional[int] = None
    subject_code: str = ""
    subject_name: str = ""
    credits: int = 3
    teacher_id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "credits": self.credits,
            "teacher_id": self.teacher_id,
            "created_at": self.created_at,
        }


@dataclass
class Session:
    id: Optional[int] = None
    subject_id: int = 0
    session_date: str = field(default_factory=lambda: datetime.now().date().isoformat())
    start_time: str = ""
    end_time: str = ""
    room: str = ""
    note: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "session_date": self.session_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "room": self.room,
            "note": self.note,
            "created_at": self.created_at,
        }


@dataclass
class Attendance:
    id: Optional[int] = None
    session_id: int = 0
    student_id: int = 0
    check_time: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "present"  # present, absent, late
    method: str = "face"  # face, manual
    note: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "student_id": self.student_id,
            "check_time": self.check_time,
            "status": self.status,
            "method": self.method,
            "note": self.note,
        }
