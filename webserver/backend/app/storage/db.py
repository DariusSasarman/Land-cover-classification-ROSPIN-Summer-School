import os
import sqlite3
from contextlib import contextmanager
from app.config import DATABASE_PATH
from app.logger import get_logger

logger = get_logger("storage.db")


@contextmanager
def get_db():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        logger.error("Database error occurred, rolling back transaction: %s", exc)
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    logger.debug("Initializing database schema at: %s", DATABASE_PATH)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                organization TEXT,
                region TEXT,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aoi_requests (
                request_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aoi_classifications (
                request_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'done',
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migration: add status column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE aoi_classifications ADD COLUMN status TEXT NOT NULL DEFAULT 'done'")
        except Exception:
            pass  # Column already exists
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aoi_requests_email ON aoi_requests(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aoi_classifications_email ON aoi_classifications(email)")
    logger.debug("Database tables verified successfully.")

