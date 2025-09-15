import sqlite3
from sqlite3 import Connection

# src/db.py
import sqlite3
import json

DB_FILE = "E:/Thesis/resume-analyzer/job_portal.db"  # absolute path ensures consistency

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            requirements TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_requirement(category, requirements_list):
    """requirements_list is a Python list"""
    conn = get_connection()
    cursor = conn.cursor()
    req_json = json.dumps(requirements_list)  # Convert list to JSON string
    cursor.execute("""
        INSERT OR REPLACE INTO job_requirements (category, requirements)
        VALUES (?, ?)
    """, (category, req_json))
    conn.commit()
    conn.close()

def get_requirements_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT requirements FROM job_requirements WHERE category=?", (category,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["requirements"])  # Convert JSON back to Python list
    return []

def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM job_requirements")
    categories = [row["category"] for row in cursor.fetchall()]
    conn.close()
    return categories
