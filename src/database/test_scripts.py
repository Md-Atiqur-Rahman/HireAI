import sqlite3
import json

from src.database.db_config import get_connection



def executeAlter():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE job_requirements ADD COLUMN requirements TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    conn.commit()
    conn.close()
