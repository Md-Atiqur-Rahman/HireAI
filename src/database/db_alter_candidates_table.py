import sqlite3

from src.database.db_config import get_connection

def add_column_if_not_exists(table_name, column_name, column_type, default=None):
    """
    Adds a column to a table if it does not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]

    if column_name not in columns:
        default_str = f" DEFAULT {default}" if default is not None else ""
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}{default_str}")
        conn.commit()

    conn.close()


def alter_candidates_table():
    """
    Safely add new score and status columns to the candidates table.
    """
    add_column_if_not_exists("candidates", "UpdatedDate", "TEXT", "NULL")
    add_column_if_not_exists("candidates", "ExperienceScore", "REAL", 0)
    add_column_if_not_exists("candidates", "EducationScore", "REAL", 0)
    add_column_if_not_exists("candidates", "TechnicalSkillsScore", "REAL", 0)
    add_column_if_not_exists("candidates", "OthersScore", "REAL", 0)
    add_column_if_not_exists("candidates", "Status", "TEXT", "'Pending'")
