import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lab.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    score REAL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
"""

SEED_SQL = """
INSERT INTO students (name, cohort, email) VALUES
    ('Alice Nguyen', 'A1', 'alice@example.com'),
    ('Bob Tran', 'A1', 'bob@example.com'),
    ('Charlie Le', 'A2', 'charlie@example.com'),
    ('Diana Pham', 'A2', 'diana@example.com'),
    ('Eve Vo', 'A1', 'eve@example.com');

INSERT INTO courses (title, credits) VALUES
    ('Machine Learning', 4),
    ('Data Structures', 3),
    ('Web Development', 3);

INSERT INTO enrollments (student_id, course_id, score) VALUES
    (1, 1, 9.2), (1, 2, 8.5),
    (2, 1, 7.8), (2, 3, 8.0),
    (3, 2, 9.0), (3, 3, 8.8),
    (4, 1, 6.5), (4, 2, 7.2),
    (5, 1, 9.5), (5, 3, 9.1);
"""

def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")
    return DB_PATH

if __name__ == "__main__":
    create_database()