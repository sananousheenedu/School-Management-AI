import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "school.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            father_name TEXT,
            class_name TEXT NOT NULL,
            section TEXT NOT NULL,
            phone TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(student_id, date),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            exam TEXT NOT NULL,
            obtained REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Demo user
    cur.execute(
        "INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)",
        ("admin", "Principal")
    )

    conn.commit()
    conn.close()

def add_student(roll_no, name, father_name, class_name, section, phone):
    conn = get_connection()
    conn.execute(
        """INSERT INTO students
        (roll_no, name, father_name, class_name, section, phone)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (roll_no, name, father_name, class_name, section, phone)
    )
    conn.commit()
    conn.close()

def get_students(search=""):
    conn = get_connection()
    if search:
        rows = conn.execute(
            """SELECT id, roll_no, name, class_name, section, father_name, phone
               FROM students
               WHERE name LIKE ? OR roll_no LIKE ?
               ORDER BY class_name, section, roll_no""",
            (f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT id, roll_no, name, class_name, section, father_name, phone
               FROM students
               ORDER BY class_name, section, roll_no"""
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_attendance(student_id, date, status):
    conn = get_connection()
    conn.execute(
        """INSERT INTO attendance(student_id, date, status)
           VALUES (?, ?, ?)
           ON CONFLICT(student_id, date)
           DO UPDATE SET status=excluded.status""",
        (student_id, date, status)
    )
    conn.commit()
    conn.close()

def save_mark(student_id, subject, exam, obtained, total):
    conn = get_connection()
    conn.execute(
        """INSERT INTO marks(student_id, subject, exam, obtained, total)
           VALUES (?, ?, ?, ?, ?)""",
        (student_id, subject, exam, obtained, total)
    )
    conn.commit()
    conn.close()

def get_results():
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            s.roll_no AS "Roll No",
            s.name AS "Student",
            s.class_name AS "Class",
            s.section AS "Section",
            m.subject AS "Subject",
            m.exam AS "Exam",
            m.obtained AS "Obtained",
            m.total AS "Total",
            ROUND((m.obtained / m.total) * 100, 1) AS "Percentage"
        FROM marks m
        JOIN students s ON s.id = m.student_id
        ORDER BY s.class_name, s.section, s.roll_no
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_attendance_report():
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            s.roll_no AS "Roll No",
            s.name AS "Student",
            s.class_name AS "Class",
            s.section AS "Section",
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS "Present",
            COUNT(a.id) AS "Recorded",
            CASE
                WHEN COUNT(a.id) = 0 THEN 0
                ELSE ROUND(
                    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END)
                    * 100.0 / COUNT(a.id), 1
                )
            END AS "Attendance %"
        FROM students s
        LEFT JOIN attendance a ON a.student_id = s.id
        GROUP BY s.id
        ORDER BY s.class_name, s.section, s.roll_no
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_dashboard_stats():
    conn = get_connection()

    students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]

    # V1 uses a simple demo teacher count.
    teachers = 5

    subjects = conn.execute("SELECT COUNT(DISTINCT subject) FROM marks").fetchone()[0]

    attendance_row = conn.execute("""
        SELECT
            CASE
                WHEN COUNT(*) = 0 THEN 0
                ELSE ROUND(
                    SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)
                    * 100.0 / COUNT(*), 1
                )
            END
        FROM attendance
    """).fetchone()[0]

    conn.close()

    return {
        "students": students,
        "teachers": teachers,
        "attendance": attendance_row or 0,
        "subjects": subjects,
    }

def find_low_attendance(threshold=75):
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            s.roll_no AS "Roll No",
            s.name AS "Student",
            s.class_name AS "Class",
            s.section AS "Section",
            ROUND(
                SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)
                * 100.0 / COUNT(a.id), 1
            ) AS "Attendance"
        FROM students s
        JOIN attendance a ON a.student_id = s.id
        GROUP BY s.id
        HAVING (
            SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)
            * 100.0 / COUNT(a.id)
        ) < ?
        ORDER BY "Attendance"
    """, (threshold,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def find_failed_students(subject=None, pass_percentage=50):
    conn = get_connection()

    if subject:
        rows = conn.execute("""
            SELECT
                s.roll_no AS "Roll No",
                s.name AS "Student",
                s.class_name AS "Class",
                s.section AS "Section",
                m.subject AS "Subject",
                m.obtained AS "Obtained",
                m.total AS "Total",
                ROUND((m.obtained / m.total) * 100, 1) AS "Percentage"
            FROM marks m
            JOIN students s ON s.id = m.student_id
            WHERE LOWER(m.subject) = LOWER(?)
              AND (m.obtained / m.total) * 100 < ?
            ORDER BY "Percentage"
        """, (subject, pass_percentage)).fetchall()
    else:
        rows = conn.execute("""
            SELECT
                s.roll_no AS "Roll No",
                s.name AS "Student",
                s.class_name AS "Class",
                s.section AS "Section",
                m.subject AS "Subject",
                m.obtained AS "Obtained",
                m.total AS "Total",
                ROUND((m.obtained / m.total) * 100, 1) AS "Percentage"
            FROM marks m
            JOIN students s ON s.id = m.student_id
            WHERE (m.obtained / m.total) * 100 < ?
            ORDER BY "Percentage"
        """, (pass_percentage,)).fetchall()

    conn.close()
    return [dict(row) for row in rows]

def find_student_result(name):
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            s.roll_no AS "Roll No",
            s.name AS "Student",
            s.class_name AS "Class",
            s.section AS "Section",
            m.subject AS "Subject",
            m.exam AS "Exam",
            m.obtained AS "Obtained",
            m.total AS "Total",
            ROUND((m.obtained / m.total) * 100, 1) AS "Percentage"
        FROM marks m
        JOIN students s ON s.id = m.student_id
        WHERE s.name LIKE ?
        ORDER BY m.subject
    """, (f"%{name}%",)).fetchall()
    conn.close()
    return [dict(row) for row in rows]
