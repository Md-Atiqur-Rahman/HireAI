
import json
from src.database.db_config import get_connection


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

def save_job_requirement(category, reqs):
    """
    Save a list of requirements for a category.
    reqs can be a single string or a list of strings.
    """
    import json
    if isinstance(reqs, str):
        reqs = [reqs]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO job_requirements (category, requirements) VALUES (?, ?)",
        (category, json.dumps(reqs))  # <- save as JSON array
    )
    conn.commit()
    conn.close()


def get_requirements_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT requirements FROM job_requirements WHERE category=?",
        (category,)
    )
    rows = cursor.fetchall()
    conn.close()

    all_requirements = []
    for row in rows:
        try:
            reqs = json.loads(row[0])
            if isinstance(reqs, list):
                all_requirements.extend(reqs)
            else:
                all_requirements.append(str(reqs))
        except Exception:
            all_requirements.append(str(row[0]))

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