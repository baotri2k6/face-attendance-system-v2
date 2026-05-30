"""
modules – Gói logic nghiệp vụ cho Hệ thống Nhận diện Khuôn mặt

Cấu trúc:
    face_recognition/
        detector.py    – FaceDetector   (phát hiện vị trí khuôn mặt)
        encoder.py     – FaceEncoder    (trích xuất vector đặc trưng)
        recognizer.py  – FaceRecognizer (so khớp với DB)
    camera/
        capture.py     – CameraManager, FrameBuffer
    attendance/
        checker.py     – AttendanceChecker, CheckResult
        reporter.py    – AttendanceReporter
    photo/
        photo_manager.py – PhotoManager
        thumbnail.py     – ThumbnailManager, frame_to_pixmap
    subject/
        subject_manager.py – SubjectManager
        enrollment.py      – EnrollmentManager
    teacher/
        teacher_manager.py – TeacherManager
"""

from . import face_recognition
from . import camera
from . import attendance
from . import photo
from . import subject
from . import teacher

__all__ = [
    "face_recognition",
    "camera",
    "attendance",
    "photo",
    "subject",
    "teacher",
]
