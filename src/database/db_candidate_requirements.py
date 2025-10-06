from src.database.db_config import get_connection


def create_candidate_requirements_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidate_requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_email TEXT,
        category TEXT,
        requirement TEXT,
        keywords_matched TEXT,
        semantic_matches TEXT,
        missing_requirements TEXT,
        match_percent REAL,
        FOREIGN KEY(candidate_email) REFERENCES candidates(Email)
    )
    """)
    conn.commit()
    conn.close()
