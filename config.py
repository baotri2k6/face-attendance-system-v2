"""
Cấu hình ứng dụng Hệ thống nhận diện khuôn mặt
"""
import os

# Thư mục gốc
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cơ sở dữ liệu
DATABASE_PATH = os.path.join(BASE_DIR, "data", "attendance.db")

# Thư mục lưu ảnh
PHOTO_DIR = os.path.join(BASE_DIR, "data", "photos")
FACE_DIR = os.path.join(BASE_DIR, "data", "faces")

# Cài đặt camera
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Cài đặt nhận diện khuôn mặt
FACE_RECOGNITION_TOLERANCE = 0.5
FACE_DETECTION_MODEL = "hog"  # "hog" hoặc "cnn"

# Cài đặt UI
APP_NAME = "Hệ thống nhận diện khuôn mặt"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

# =====================================================
# THEME COLOR
# =====================================================

# Primary
PRIMARY_COLOR = "#2563eb"

# Secondary
SECONDARY_COLOR = "#0f172a"

# Sidebar
SIDEBAR_BG = "#f8fafc"
SIDEBAR_TEXT = "#334155"

# Main Content
CONTENT_BG = "#eef2f7"

# Card
CARD_BG = "#ffffff"

# Border
BORDER_COLOR = "#e2e8f0"

# Hover
HOVER_COLOR = "#dbeafe"

# Success
SUCCESS_COLOR = "#22c55e"

# Danger
DANGER_COLOR = "#ef4444"

# Text
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#64748b"

# Tài khoản mặc định (trong thực tế nên lưu DB có hash)
DEFAULT_ADMIN = {
    "username": "AdminSafe",
    "password": "admin123"
}

# Tạo thư mục nếu chưa có
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(FACE_DIR, exist_ok=True)
