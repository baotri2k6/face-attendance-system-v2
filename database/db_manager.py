"""
Quản lý cơ sở dữ liệu SQLite
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH


class DBManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_code TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                class_name TEXT,
                email TEXT,
                phone TEXT,
                face_encoding BLOB,
                photo_path TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_code TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT,
                email TEXT,
                phone TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT UNIQUE NOT NULL,
                subject_name TEXT NOT NULL,
                credits INTEGER DEFAULT 3,
                teacher_id INTEGER,
                created_at TEXT,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                session_date TEXT,
                start_time TEXT,
                end_time TEXT,
                room TEXT,
                note TEXT,
                created_at TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            );

            CREATE TABLE IF NOT EXISTS attendances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                check_time TEXT,
                status TEXT DEFAULT 'present',
                method TEXT DEFAULT 'face',
                note TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id),
                FOREIGN KEY (student_id) REFERENCES students(id),
                UNIQUE(session_id, student_id)
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                enrolled_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id),
                UNIQUE(student_id, subject_id)
            );
        """)
        conn.commit()
        conn.close()
        self._seed_demo_data()

    def _seed_demo_data(self):
        """Thêm dữ liệu mẫu nếu DB trống"""
        conn = self.get_connection()
        cur = conn.cursor()
        count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            from datetime import datetime
            now = datetime.now().isoformat()
            # Insert demo students
            cur.executemany(
                "INSERT OR IGNORE INTO students (student_code,full_name,class_name,email,phone,created_at) VALUES (?,?,?,?,?,?)",
                [
                    ("SV001", "Nguyễn Văn An", "CNTT01", "an.nv@example.com", "0901000001", now),
                    ("SV002", "Trần Thị Bình", "CNTT01", "binh.tt@example.com", "0901000002", now),
                    ("SV003", "Lê Hoàng Cường", "CNTT02", "cuong.lh@example.com", "0901000003", now),
                    ("SV004", "Phạm Thị Dung", "CNTT02", "dung.pt@example.com", "0901000004", now),
                    ("SV005", "Hoàng Minh Em", "CNTT03", "em.hm@example.com", "0901000005", now),
                ]
            )
            # Insert demo teachers
            cur.executemany(
                "INSERT OR IGNORE INTO teachers (teacher_code,full_name,department,email,phone,created_at) VALUES (?,?,?,?,?,?)",
                [
                    ("GV001", "TS. Nguyễn Văn Hùng", "Khoa CNTT", "hung.nv@edu.vn", "0911000001", now),
                    ("GV002", "ThS. Trần Thị Lan",   "Khoa CNTT", "lan.tt@edu.vn",  "0911000002", now),
                ]
            )
            # Insert demo subjects
            cur.executemany(
                "INSERT OR IGNORE INTO subjects (subject_code,subject_name,credits,teacher_id,created_at) VALUES (?,?,?,?,?)",
                [
                    ("MON001", "Lập trình Python",       3, 1, now),
                    ("MON002", "Cơ sở dữ liệu",          3, 1, now),
                    ("MON003", "Trí tuệ nhân tạo",       3, 2, now),
                    ("MON004", "Mạng máy tính",          3, 2, now),
                ]
            )
            # Insert demo sessions
            cur.executemany(
                "INSERT OR IGNORE INTO sessions (subject_id,session_date,start_time,end_time,room,created_at) VALUES (?,?,?,?,?,?)",
                [
                    (1, "2026-05-30", "07:30", "09:30", "P.101", now),
                ]
            )
            # Insert enrollments only after students & subjects exist
            student_ids = [r[0] for r in cur.execute("SELECT id FROM students").fetchall()]
            subject_ids = [r[0] for r in cur.execute("SELECT id FROM subjects").fetchall()]
            enrollments = [(sid, subid, now) for sid in student_ids for subid in subject_ids]
            cur.executemany(
                "INSERT OR IGNORE INTO enrollments (student_id,subject_id,enrolled_at) VALUES (?,?,?)",
                enrollments
            )
            conn.commit()
        conn.close()

    # ─── STUDENTS ──────────────────────────────────────────────────────────────
    def get_all_students(self):
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM students ORDER BY full_name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_student(self, student_id):
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def add_student(self, data: dict):
        from datetime import datetime
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO students (student_code,full_name,class_name,email,phone,face_encoding,photo_path,created_at) VALUES (?,?,?,?,?,?,?,?)",
            (data.get("student_code"), data.get("full_name"), data.get("class_name"),
             data.get("email"), data.get("phone"), data.get("face_encoding"),
             data.get("photo_path"), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def update_student(self, student_id, data: dict):
        conn = self.get_connection()
        conn.execute(
            "UPDATE students SET student_code=?,full_name=?,class_name=?,email=?,phone=?,photo_path=? WHERE id=?",
            (data.get("student_code"), data.get("full_name"), data.get("class_name"),
             data.get("email"), data.get("phone"), data.get("photo_path"), student_id)
        )
        conn.commit()
        conn.close()

    def delete_student(self, student_id):
        conn = self.get_connection()
        conn.execute("DELETE FROM enrollments WHERE student_id=?", (student_id,))
        conn.execute("DELETE FROM attendances WHERE student_id=?", (student_id,))
        conn.execute("DELETE FROM students WHERE id=?", (student_id,))
        conn.commit()
        conn.close()

    def search_students(self, keyword):
        conn = self.get_connection()
        kw = f"%{keyword}%"
        rows = conn.execute(
            "SELECT * FROM students WHERE full_name LIKE ? OR student_code LIKE ? OR class_name LIKE ?",
            (kw, kw, kw)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def save_face_encoding(self, student_id, encoding_bytes):
        conn = self.get_connection()
        conn.execute("UPDATE students SET face_encoding=? WHERE id=?", (encoding_bytes, student_id))
        conn.commit()
        conn.close()

    # ─── TEACHERS ──────────────────────────────────────────────────────────────
    def get_all_teachers(self):
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM teachers ORDER BY full_name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_teacher(self, data: dict):
        from datetime import datetime
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO teachers (teacher_code,full_name,department,email,phone,created_at) VALUES (?,?,?,?,?,?)",
            (data.get("teacher_code"), data.get("full_name"), data.get("department"),
             data.get("email"), data.get("phone"), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def update_teacher(self, teacher_id, data: dict):
        conn = self.get_connection()
        conn.execute(
            "UPDATE teachers SET teacher_code=?,full_name=?,department=?,email=?,phone=? WHERE id=?",
            (data.get("teacher_code"), data.get("full_name"), data.get("department"),
             data.get("email"), data.get("phone"), teacher_id)
        )
        conn.commit()
        conn.close()

    def delete_teacher(self, teacher_id):
        conn = self.get_connection()
        # Gỡ liên kết giáo viên khỏi môn học (giữ môn học, chỉ set teacher_id=NULL)
        conn.execute("UPDATE subjects SET teacher_id=NULL WHERE teacher_id=?", (teacher_id,))
        conn.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
        conn.commit()
        conn.close()

    # ─── SUBJECTS ──────────────────────────────────────────────────────────────
    def get_all_subjects(self):
        conn = self.get_connection()
        rows = conn.execute("""
            SELECT s.*, t.full_name as teacher_name
            FROM subjects s LEFT JOIN teachers t ON s.teacher_id=t.id
            ORDER BY s.subject_name
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_subject(self, data: dict):
        from datetime import datetime
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO subjects (subject_code,subject_name,credits,teacher_id,created_at) VALUES (?,?,?,?,?)",
            (data.get("subject_code"), data.get("subject_name"), data.get("credits", 3),
             data.get("teacher_id"), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def update_subject(self, subject_id, data: dict):
        conn = self.get_connection()
        conn.execute(
            "UPDATE subjects SET subject_code=?,subject_name=?,credits=?,teacher_id=? WHERE id=?",
            (data.get("subject_code"), data.get("subject_name"), data.get("credits", 3),
             data.get("teacher_id"), subject_id)
        )
        conn.commit()
        conn.close()

    def delete_subject(self, subject_id):
        conn = self.get_connection()
        # Xóa dữ liệu liên quan trước
        session_ids = [r[0] for r in conn.execute("SELECT id FROM sessions WHERE subject_id=?", (subject_id,)).fetchall()]
        for sess_id in session_ids:
            conn.execute("DELETE FROM attendances WHERE session_id=?", (sess_id,))
        conn.execute("DELETE FROM sessions WHERE subject_id=?", (subject_id,))
        conn.execute("DELETE FROM enrollments WHERE subject_id=?", (subject_id,))
        conn.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
        conn.commit()
        conn.close()

    # ─── SESSIONS ──────────────────────────────────────────────────────────────
    def get_all_sessions(self):
        conn = self.get_connection()
        rows = conn.execute("""
            SELECT ss.*, sb.subject_name, sb.subject_code
            FROM sessions ss LEFT JOIN subjects sb ON ss.subject_id=sb.id
            ORDER BY ss.session_date DESC, ss.start_time DESC
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_sessions_by_subject(self, subject_id):
        conn = self.get_connection()
        rows = conn.execute(
            "SELECT * FROM sessions WHERE subject_id=? ORDER BY session_date DESC",
            (subject_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_session(self, data: dict):
        from datetime import datetime
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO sessions (subject_id,session_date,start_time,end_time,room,note,created_at) VALUES (?,?,?,?,?,?,?)",
            (data.get("subject_id"), data.get("session_date"), data.get("start_time"),
             data.get("end_time"), data.get("room"), data.get("note"), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def delete_session(self, session_id):
        conn = self.get_connection()
        # Xóa điểm danh của buổi học này trước
        conn.execute("DELETE FROM attendances WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        conn.commit()
        conn.close()

    # ─── ATTENDANCE ────────────────────────────────────────────────────────────
    def get_attendance_by_session(self, session_id):
        conn = self.get_connection()
        rows = conn.execute("""
            SELECT a.*, s.full_name, s.student_code, s.class_name
            FROM attendances a LEFT JOIN students s ON a.student_id=s.id
            WHERE a.session_id=?
            ORDER BY a.check_time
        """, (session_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_attendance(self, session_id, student_id, status="present", method="face"):
        from datetime import datetime
        conn = self.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO attendances (session_id,student_id,check_time,status,method) VALUES (?,?,?,?,?)",
            (session_id, student_id, datetime.now().isoformat(), status, method)
        )
        conn.commit()
        conn.close()

    def get_attendance_stats(self):
        conn = self.get_connection()
        total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        total_sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        total_attendance = conn.execute("SELECT COUNT(*) FROM attendances WHERE status='present'").fetchone()[0]
        total_subjects = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        conn.close()
        return {
            "total_students": total_students,
            "total_sessions": total_sessions,
            "total_attendance": total_attendance,
            "total_subjects": total_subjects,
        }

    def get_students_with_face(self):
        conn = self.get_connection()
        rows = conn.execute(
            "SELECT id, full_name, student_code, face_encoding FROM students WHERE face_encoding IS NOT NULL"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── PHOTOS ────────────────────────────────────────────────────────────────
    def get_all_photos(self):
        conn = self.get_connection()
        rows = conn.execute(
            "SELECT id, full_name, student_code, photo_path FROM students WHERE photo_path != '' AND photo_path IS NOT NULL"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]