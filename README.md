<div align="center">

# 🎓 Hệ thống Điểm danh Nhận diện Khuôn mặt
### Face Attendance System v2

Phần mềm quản lý điểm danh sinh viên tự động bằng nhận diện khuôn mặt qua camera,  
xây dựng với **Python · PyQt5 · OpenCV · SQLite**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green?logo=qt)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-red?logo=opencv)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>

---

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Giao diện](#-giao-diện)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Cách sử dụng](#-cách-sử-dụng)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Cơ sở dữ liệu](#-cơ-sở-dữ-liệu)
- [Cấu hình](#-cấu-hình)
- [Kiến trúc module](#-kiến-trúc-module)
- [Xử lý sự cố](#-xử-lý-sự-cố)

---

## ✨ Tính năng

### Điểm danh thông minh
- 📸 **Nhận diện khuôn mặt tự động** qua camera theo thời gian thực
- ⏰ **Phân loại trạng thái** tự động: Có mặt / Muộn / Vắng mặt
- ✏️ **Điểm danh thủ công** khi cần bổ sung hoặc chỉnh sửa
- 🔄 **Hai chế độ nhận diện**: dùng `face_recognition` (chính xác cao) hoặc OpenCV fallback (không cần cài thêm)

### Quản lý dữ liệu
- 👨‍🎓 **Sinh viên** — thêm, sửa, xóa, tìm kiếm, upload ảnh, chụp ảnh trực tiếp từ camera
- 👨‍🏫 **Giáo viên** — quản lý thông tin giảng viên theo khoa/bộ môn
- 📚 **Môn học** — tạo môn, gắn giảng viên phụ trách, quản lý tín chỉ
- 🗓️ **Buổi học** — lên lịch buổi học theo môn, phòng, thời gian
- 📋 **Điểm danh** — xem danh sách điểm danh từng buổi, chỉnh sửa trực tiếp

### Thống kê & báo cáo
- 📊 **Dashboard tổng quan** — thống kê nhanh sinh viên, môn học, buổi học, điểm danh
- 📈 **Biểu đồ thống kê** — tỷ lệ điểm danh, xu hướng theo thời gian
- 🖼️ **Thư viện ảnh** — xem ảnh toàn bộ sinh viên, trạng thái đã đăng ký khuôn mặt

### Đăng ký khuôn mặt
- 📷 **Chụp trực tiếp** — mở camera, hiển thị khung hướng dẫn, chụp và đăng ký ngay
- 📂 **Upload ảnh** — tải ảnh có sẵn từ máy lên
- 🔁 **Đăng ký tự động** — sau khi chụp, hệ thống tự tạo encoding và lưu vào DB

---

## 🖥️ Giao diện

| Trang | Mô tả |
|-------|-------|
| **Đăng nhập** | Xác thực tài khoản admin |
| **Trang chủ** | Dashboard tổng quan với 4 chỉ số chính và lối tắt tới các trang |
| **Sinh viên** | Bảng danh sách, form thêm/sửa, tìm kiếm theo mã/tên/lớp |
| **Nhận diện** | Live camera feed, nhận diện và điểm danh tự động theo buổi học |
| **Điểm danh** | Xem và chỉnh sửa danh sách điểm danh từng buổi |
| **Môn học** | Quản lý môn học và giảng viên phụ trách |
| **Giáo viên** | Thông tin giảng viên theo khoa/bộ môn |
| **Buổi học** | Lịch buổi học: ngày, giờ, phòng, môn học |
| **Thống kê** | Biểu đồ tỷ lệ điểm danh, thống kê tổng hợp |
| **Xem ảnh** | Thư viện ảnh sinh viên, đăng ký khuôn mặt |

---

## 💻 Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|------------|---------|
| Hệ điều hành | Windows 10/11, Ubuntu 20.04+, macOS 11+ |
| Python | 3.9 trở lên |
| RAM | Tối thiểu 4 GB (khuyến nghị 8 GB khi dùng `face_recognition`) |
| Camera | Webcam USB hoặc camera tích hợp |
| Ổ cứng | ~500 MB (chưa kể ảnh sinh viên) |

---

## 🚀 Cài đặt

### Bước 1 — Tải mã nguồn

```bash
git clone https://github.com/baotri2k6/face-attendance-system-v2.git
cd face-attendance-system-v2
```

### Bước 2 — Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Bước 3 — Cài thư viện cơ bản

```bash
pip install PyQt5 opencv-python numpy
```

### Bước 4 — (Tùy chọn) Cài `face_recognition` để nhận diện chính xác

> Nếu bỏ qua bước này, hệ thống vẫn chạy được nhưng tính năng nhận diện sẽ dùng OpenCV fallback.

**Windows:**
```bash
pip install cmake
pip install dlib
pip install face_recognition
```

**Ubuntu / Debian:**
```bash
sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev
pip install dlib face_recognition
```

**macOS:**
```bash
brew install cmake
pip install dlib face_recognition
```

### Bước 5 — Chạy ứng dụng

```bash
python main.py
```

---

## 📖 Cách sử dụng

### Đăng nhập

| Tài khoản | Mật khẩu |
|-----------|----------|
| `AdminSafe` | `admin123` |

> ⚠️ Nên đổi mật khẩu sau khi triển khai thực tế. Cấu hình trong `config.py` → `DEFAULT_ADMIN`.

---

### Quy trình sử dụng cơ bản

```
1. Thêm giáo viên  →  Trang Giáo viên
2. Thêm môn học    →  Trang Môn học (gắn giáo viên phụ trách)
3. Thêm sinh viên  →  Trang Sinh viên
4. Đăng ký mặt    →  Trang Xem ảnh → Chọn sinh viên → Chụp khuôn mặt
5. Tạo buổi học   →  Trang Buổi học (chọn môn, ngày, phòng)
6. Điểm danh      →  Trang Nhận diện → Chọn buổi học → Bật camera
7. Xem kết quả    →  Trang Điểm danh hoặc Thống kê
```

---

### Đăng ký khuôn mặt sinh viên

1. Vào **Xem ảnh** → chọn sinh viên từ dropdown
2. Nhấn **📸 Chụp khuôn mặt**
3. Đặt mặt vào khung hướng dẫn (ellipse xanh), nhấn **Chụp ảnh**
4. Xem trước ảnh → nhấn **Xác nhận & Lưu**
5. Hệ thống tự động tạo encoding và lưu DB

> Hoặc nhấn **📂 Tải ảnh lên** để dùng ảnh có sẵn, sau đó nhấn **👁 Đăng ký khuôn mặt**.

---

### Điểm danh bằng camera

1. Vào **Nhận diện**
2. Chọn **Buổi học** cần điểm danh từ dropdown
3. Nhấn **▶ Bắt đầu**
4. Sinh viên lần lượt nhìn vào camera — hệ thống tự nhận diện và ghi nhận
5. Nhấn **⏹ Dừng** khi xong

Kết quả điểm danh xem tại trang **Điểm danh**, lọc theo buổi học.

---

## 📁 Cấu trúc dự án

```
face-attendance-system-v2/
│
├── main.py                          # Điểm khởi động ứng dụng
├── config.py                        # Cấu hình toàn cục (đường dẫn, màu sắc, camera...)
├── requirements.txt                 # Danh sách thư viện cần cài
│
├── data/                            # Dữ liệu runtime (tự tạo khi chạy)
│   ├── attendance.db                # Cơ sở dữ liệu SQLite
│   ├── photos/                      # Ảnh chân dung sinh viên
│   └── faces/                       # Dữ liệu encoding khuôn mặt
│
├── database/
│   ├── db_manager.py                # Toàn bộ thao tác CRUD với SQLite
│   └── models.py                    # Dataclass: Student, Teacher, Subject, Session, Attendance
│
├── modules/                         # Logic nghiệp vụ (tách biệt với UI)
│   ├── attendance/
│   │   ├── checker.py               # Kiểm tra trạng thái điểm danh (present/late/absent)
│   │   └── repoter.py               # Tạo báo cáo điểm danh
│   ├── camera/
│   │   └── capture.py               # CameraManager, FrameBuffer
│   ├── face_recognition/
│   │   ├── encoder.py               # FaceEncoder — mã hóa khuôn mặt từ ảnh/frame
│   │   ├── detector.py              # FaceDetector — phát hiện vị trí khuôn mặt
│   │   ├── recognizer.py            # FaceRecognizer — so khớp với DB
│   │   └── simple_encoder.py        # Encoder đơn giản dùng OpenCV thuần
│   ├── photo/
│   │   ├── photo_manager.py         # Quản lý lưu/xóa ảnh sinh viên
│   │   └── thumbnail.py             # Tạo thumbnail cho lưới ảnh
│   ├── subject/
│   │   ├── subject_manager.py       # Logic quản lý môn học
│   │   └── enrollment.py            # Quản lý đăng ký môn học của sinh viên
│   └── teacher/
│       └── teacher_manager.py       # Logic quản lý giáo viên
│
└── Ui/
    ├── main_window.py               # Cửa sổ chính, điều phối các trang
    ├── components/
    │   ├── header.py                # Thanh tiêu đề (thời gian, tên người dùng, đăng xuất)
    │   ├── sidebar.py               # Thanh điều hướng bên trái
    │   ├── camera_widget.py         # Widget hiển thị live camera feed
    │   └── photo_grid.py            # Lưới hiển thị ảnh sinh viên
    └── page/
        ├── login_page.py            # Trang đăng nhập
        ├── home_page.py             # Dashboard tổng quan
        ├── student_page.py          # Quản lý sinh viên
        ├── teacher_page.py          # Quản lý giáo viên
        ├── subject_page.py          # Quản lý môn học
        ├── session_page.py          # Quản lý buổi học
        ├── attendance_page.py       # Xem & chỉnh sửa điểm danh
        ├── recognize_page.py        # Điểm danh tự động bằng camera
        ├── statistics_page.py       # Thống kê & biểu đồ
        └── photo_page.py            # Thư viện ảnh & đăng ký khuôn mặt
```

---

## 🗄️ Cơ sở dữ liệu

File SQLite lưu tại `data/attendance.db`, tự tạo khi chạy lần đầu.

### Sơ đồ quan hệ

```
students ──────────────┐
  id, student_code,    │ (many)
  full_name, class,    │
  face_encoding,       ├──── enrollments ──── subjects
  photo_path           │       student_id         id, subject_code,
                       │       subject_id          subject_name,
                       │                           credits,
teachers ──────────────┤                           teacher_id ──── teachers
  id, teacher_code,    │
  full_name,           └──── attendances ──── sessions
  department                   student_id         id, subject_id,
                               session_id         session_date,
                               status             start_time,
                               method             end_time, room
                               check_time
```

### Trạng thái điểm danh

| Giá trị | Ý nghĩa |
|---------|---------|
| `present` | Có mặt đúng giờ |
| `late` | Đến muộn (sau 15 phút kể từ giờ bắt đầu) |
| `absent` | Vắng mặt |

### Phương thức điểm danh

| Giá trị | Ý nghĩa |
|---------|---------|
| `face` | Nhận diện khuôn mặt tự động |
| `manual` | Điểm danh thủ công |

---

## ⚙️ Cấu hình

Tất cả cấu hình nằm trong `config.py`:

```python
# Camera
CAMERA_INDEX = 0          # Index của camera (0 = webcam mặc định)
CAMERA_WIDTH  = 640       # Độ phân giải ngang
CAMERA_HEIGHT = 480       # Độ phân giải dọc

# Nhận diện khuôn mặt
FACE_RECOGNITION_TOLERANCE = 0.5   # Ngưỡng nhận diện (thấp hơn = chặt hơn)
FACE_DETECTION_MODEL = "hog"       # "hog" (CPU) hoặc "cnn" (GPU, chính xác hơn)

# Tài khoản admin
DEFAULT_ADMIN = {
    "username": "AdminSafe",
    "password": "admin123"
}
```

### Điều chỉnh ngưỡng nhận diện

| `FACE_RECOGNITION_TOLERANCE` | Hành vi |
|------------------------------|---------|
| `0.4` | Rất chặt — ít nhầm, có thể bỏ sót |
| `0.5` | Cân bằng (mặc định) |
| `0.6` | Thoải mái hơn — nhận diện nhiều hơn nhưng dễ nhầm |

---

## 🏗️ Kiến trúc module

Hệ thống tách biệt **UI** và **logic nghiệp vụ** theo mô hình phân lớp:

```
┌─────────────────────────────────────────┐
│                 Ui/page/                │  ← Hiển thị, tương tác người dùng
├─────────────────────────────────────────┤
│              Ui/components/             │  ← Widget tái sử dụng
├─────────────────────────────────────────┤
│                 modules/                │  ← Logic nghiệp vụ thuần Python
├─────────────────────────────────────────┤
│              database/                  │  ← Truy cập dữ liệu (SQLite)
└─────────────────────────────────────────┘
```

### Luồng nhận diện khuôn mặt

```
Camera frame
    │
    ▼
FaceDetector.detect()          ← Tìm vị trí khuôn mặt trong frame
    │
    ▼
FaceEncoder.encode_from_frame() ← Trích xuất vector đặc trưng 128 chiều
    │
    ▼
FaceRecognizer.recognize()     ← So sánh với encodings trong DB
    │
    ▼
AttendanceChecker.check()      ← Xác định trạng thái (present/late)
    │
    ▼
DBManager.mark_attendance()    ← Ghi vào SQLite
```

---

## 🔧 Xử lý sự cố

### ❌ `AttributeError: module 'cv2' has no attribute 'data'`
`cv2.data` chỉ có trong `opencv-contrib-python`. Cài đúng gói:
```bash
pip uninstall opencv-python
pip install opencv-contrib-python
```

### ❌ `AttributeError: module 'cv2' has no attribute 'face'`
Tương tự — cần `opencv-contrib-python`:
```bash
pip install opencv-contrib-python
```

### ❌ `ModuleNotFoundError: No module named 'face_recognition'`
Cài theo thứ tự:
```bash
pip install cmake
pip install dlib
pip install face_recognition
```
Nếu lỗi `dlib`, đảm bảo đã cài **Visual Studio Build Tools** (Windows) hoặc `build-essential` (Linux).

### ❌ Chương trình tự đóng khi xóa sinh viên/môn học/buổi học
Do FOREIGN KEY constraint trong SQLite. Đảm bảo dùng bản `db_manager.py` mới nhất — đã xử lý xóa cascade.

### ❌ Camera không mở được
- Kiểm tra `CAMERA_INDEX` trong `config.py` — thử đổi từ `0` sang `1` nếu có nhiều camera
- Đảm bảo không có ứng dụng khác đang dùng camera

### ❌ Nhận diện khuôn mặt không chính xác
- Đảm bảo ảnh đăng ký rõ nét, đủ sáng, nhìn thẳng
- Giảm `FACE_RECOGNITION_TOLERANCE` xuống `0.45` trong `config.py`
- Dùng `FACE_DETECTION_MODEL = "cnn"` nếu máy có GPU

---

## 📦 Danh sách thư viện

| Thư viện | Phiên bản | Bắt buộc | Mục đích |
|----------|-----------|----------|---------|
| `PyQt5` | ≥ 5.15 | ✅ | Giao diện đồ họa |
| `opencv-python` | ≥ 4.5 | ✅ | Xử lý camera và ảnh |
| `numpy` | ≥ 1.21 | ✅ | Xử lý ma trận encoding |
| `cmake` | ≥ 3.25 | ⚙️ Tùy chọn | Cần để build dlib |
| `dlib` | ≥ 19.24 | ⚙️ Tùy chọn | Nhận diện khuôn mặt chính xác |
| `face_recognition` | ≥ 1.3 | ⚙️ Tùy chọn | API nhận diện khuôn mặt cấp cao |

---

## 📄 Giấy phép

Dự án được phát hành theo giấy phép **MIT**. Xem file `LICENSE` để biết thêm chi tiết.

---

<div align="center">

Made with ❤️ by **Nguyễn Trí**  
Face Attendance System © 2026

</div>
