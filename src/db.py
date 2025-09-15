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

def save_job_requirement(category, requirements_list):
    """
    Save one or more requirements into DB under a category.
    requirements_list: list of strings
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Store as JSON so we can support multiple requirements in one row
    requirements_json = json.dumps(requirements_list)

    cursor.execute(
        "INSERT INTO job_requirements (category, requirements) VALUES (?, ?)",
        (category, requirements_json)
    )

    conn.commit()
    conn.close()

def get_requirements_by_category(category):
    """
    Fetch all requirements for a given category.
    Returns a flat list of requirement strings.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT requirements FROM job_requirements WHERE category=?",
        (category,)
    )
    rows = cursor.fetchall()
    conn.close()

    # Flatten JSON arrays into a single Python list
    all_requirements = []
    for row in rows:
        try:
            reqs = json.loads(row[0])
            all_requirements.extend(reqs)
        except Exception:
            all_requirements.append(row[0])

    return all_requirements

def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM job_requirements")
    categories = [row["category"] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_all_requirements():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, requirement FROM job_requirements")
    rows = cursor.fetchall()
    conn.close()
    return [{"category": r[0], "requirement": r[1]} for r in rows]
