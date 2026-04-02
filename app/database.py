import sqlite3
from contextlib import contextmanager
import os

DATABASE_NAME = "careconnect.db"

def get_db_path():
    """Get the full path to the database file"""
    return os.path.join(os.path.dirname(__file__), DATABASE_NAME)

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize database with all required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table (supports both patients and doctors)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                age INTEGER,
                role TEXT DEFAULT 'patient',
                specialization TEXT,
                experience INTEGER,
                profile_image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Backward-compatible migrations for existing databases.
        cursor.execute("PRAGMA table_info(users)")
        user_columns = {col[1] for col in cursor.fetchall()}

        if "role" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'patient'")
        if "specialization" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN specialization TEXT")
        if "experience" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN experience INTEGER")
        if "profile_image" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")
        
        # Appointments table (updated for telemedicine)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                meeting_link TEXT,
                status TEXT DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users (id),
                FOREIGN KEY (doctor_id) REFERENCES users (id)
            )
        """)

        # Backward-compatible migration from old appointment schema.
        cursor.execute("PRAGMA table_info(appointments)")
        appointment_columns = {col[1] for col in cursor.fetchall()}

        if "patient_id" not in appointment_columns:
            if "user_id" in appointment_columns:
                cursor.execute("ALTER TABLE appointments ADD COLUMN patient_id INTEGER")
                cursor.execute("UPDATE appointments SET patient_id = user_id WHERE patient_id IS NULL")
            else:
                cursor.execute("ALTER TABLE appointments ADD COLUMN patient_id INTEGER")

        if "doctor_id" not in appointment_columns:
            cursor.execute("ALTER TABLE appointments ADD COLUMN doctor_id INTEGER")
        
        # Treatment notes table (doctor adds notes after consultation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS treatment_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL UNIQUE,
                doctor_id INTEGER NOT NULL,
                notes TEXT NOT NULL,
                treatment_plan TEXT,
                prescription TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appointment_id) REFERENCES appointments (id),
                FOREIGN KEY (doctor_id) REFERENCES users (id)
            )
        """)
        
        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Period tracker table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS period_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                last_period_date TEXT NOT NULL,
                cycle_length INTEGER DEFAULT 28,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()
