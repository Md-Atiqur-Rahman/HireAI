
import json
from src.database.db_config import get_connection


def create_job_requirements_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            requirements TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES job_categories(id)
        )
    """)
    conn.commit()
    conn.close()



def save_job_requirement(category_id, reqs):
    """
    Save a list of requirements for a category.
    Appends new requirements to existing ones if category exists.
    """
    if isinstance(reqs, str):
        reqs = [reqs]

    conn = get_connection()
    cursor = conn.cursor()

    # Check if category already exists
    cursor.execute("SELECT requirements FROM job_requirements WHERE category_id=?", (category_id,))
    row = cursor.fetchone()

    if row and row[0]:
        # Load existing requirements and append new ones
        existing_reqs = json.loads(row[0])
        combined_reqs = existing_reqs + reqs
        cursor.execute(
            "UPDATE job_requirements SET requirements=? WHERE category_id=?",
            (json.dumps(combined_reqs), category_id)
        )
    else:
        # Insert new row
        cursor.execute(
            "INSERT INTO job_requirements (category_id, requirements) VALUES (?, ?)",
            (category_id, json.dumps(reqs))
        )

    conn.commit()
    conn.close()




def get_requirements_by_category(category_id):
    """
    Fetch all requirements for a given category.
    Returns a Python list of strings.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT requirements FROM job_requirements WHERE category_id=?", (category_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        return json.loads(row[0])
    return []




def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category_id FROM job_requirements")
    categories = [row["category_id"] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_all_requirements():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, requirement FROM job_requirements")
    rows = cursor.fetchall()
    conn.close()
    return [{"category_id": r[0], "requirement": r[1]} for r in rows]