
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


# ---------------- Save Job Requirement ----------------
def save_job_requirement(category_id, requirements_dict):
    print(json.dumps(requirements_dict))
    """
    Save or update full requirements JSON for a category.
    requirements_dict should be a dict with Experience, Education, etc.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if requirements already exist for this category
    cursor.execute("SELECT id FROM job_requirements WHERE category_id=?", (category_id,))
    row = cursor.fetchone()

    if row:
        # Update existing
        cursor.execute(
            "UPDATE job_requirements SET requirements=? WHERE category_id=?",
            (json.dumps(requirements_dict), category_id)
        )
    else:
        # Insert new
        cursor.execute(
            "INSERT INTO job_requirements (category_id, requirements) VALUES (?, ?)",
            (category_id, json.dumps(requirements_dict))
        )

    conn.commit()
    conn.close()


def get_requirements_by_category(category_id):
    """
    Fetch requirements JSON for a given category.
    Returns a dict (empty if none).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT requirements FROM job_requirements WHERE category_id=?", (category_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        return json.loads(row[0])
    return {
        "Experience": "",
        "Education": "",
        "TechnicalSkills": "",
        "Others": ""
    }





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