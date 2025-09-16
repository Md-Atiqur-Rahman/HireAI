from src.database.db_config import get_connection

# -------------------
# Database helper functions
# -------------------
def create_category_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def save_job_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO job_categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM job_categories")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def delete_job_requirements():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_requirements;")
    conn.commit()
    conn.close()
