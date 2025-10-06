from datetime import datetime
import json
import sqlite3
import pandas as pd

from src.feature.dataclasses.Score import Score
from src.database.db_config import get_connection

__all__ = [
    "get_average_score",
    "get_candidates_count",
    "get_candidates_group_by_category",
    "get_candidates_paginated",
    "get_top_candidate",
    "get_total_categories"
]

def create_candidates_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Candidate TEXT,
        Email TEXT,
        Contact TEXT,
        Experience TEXT,
        TotalScore REAL,
        Skills TEXT,
        SummaryText TEXT,
        CategoryId INTEGER,
        SubmittedOn TEXT DEFAULT (DATE('now'))
    )
    """)
    
    conn.commit()
    conn.close()

def add_submitted_on_column():
    conn = get_connection()
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(candidates)")
    columns = [col[1] for col in cursor.fetchall()]
    if "SubmittedOn" not in columns:
        # Add column without default
        cursor.execute("ALTER TABLE candidates ADD COLUMN SubmittedOn TEXT")
        conn.commit()
        print("SubmittedOn column added successfully.")

        # Optionally, set existing rows to today's date
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("UPDATE candidates SET SubmittedOn = ?", (today,))
        conn.commit()
        print("Existing rows updated with today's date.")
    else:
        print("SubmittedOn column already exists.")

    conn.close()


def save_candidate(Name, email, phone, experience, total_score, skills, summary_text, category_id, score: Score = None, raw_rows=None):
    conn = get_connection()
    cursor = conn.cursor()

    # System-generated current date
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    skills_str = json.dumps(skills) if isinstance(skills, list) else str(skills)

    # Check if email already exists
    cursor.execute("SELECT 1 FROM candidates WHERE Email = ?", (email,))
    exists = cursor.fetchone()

    if exists:
        # Update existing record
        cursor.execute("""
            UPDATE candidates
            SET Candidate = ?, Contact = ?, Experience = ?, TotalScore = ?, Skills = ?, 
                SummaryText = ?, CategoryId = ?, UpdatedDate = ?, 
                ExperienceScore = ?, EducationScore = ?, TechnicalSkillsScore = ?, OthersScore = ?, Status = ?
            WHERE Email = ?
        """, (
            Name,
            phone,
            experience,
            total_score,
            skills_str,
            summary_text,
            category_id,
            now,
            score.experience if score else 0,
            score.education if score else 0,
            score.technical_skills if score else 0,
            score.others if score else 0,
            score.status if score else "Not Evaluated",
            email
        ))
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO candidates 
            (Candidate, Email, Contact, Experience, TotalScore, Skills, SummaryText, CategoryId, SubmittedOn,
             UpdatedDate, ExperienceScore, EducationScore, TechnicalSkillsScore, OthersScore, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            Name,
            email,
            phone,
            experience,
            total_score,
            skills_str,
            summary_text,
            category_id,
            now,
            now,  # UpdatedDate same as SubmittedOn for new record
            score.experience if score else 0,
            score.education if score else 0,
            score.technical_skills if score else 0,
            score.others if score else 0,
            score.status if score else "Not Evaluated"
        ))

    # --- Save raw_rows for candidate ---
    if raw_rows:
        # Optional: remove old rows for this candidate to avoid duplicates
        cursor.execute("DELETE FROM candidate_requirements WHERE candidate_email = ?", (email,))
        
        for row in raw_rows:
            cursor.execute("""
                INSERT INTO candidate_requirements 
                (candidate_email, category, requirement, keywords_matched, semantic_matches, missing_requirements, match_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                email,
                row["Category"],
                row["Requirement"],
                row["KeywordsMatched"],
                row["SemanticMatches"],
                row["MissingRequirements"],
                row["MatchPercent"]
            ))
    conn.commit()
    conn.close()
    return True

from datetime import datetime

def update_submitted_on(candidate_id, new_date=None):
    """
    Update the SubmittedOn date for a candidate by Id.
    new_date: string in 'YYYY-MM-DD' format. Defaults to today.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if new_date is None:
        new_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        UPDATE candidates
        SET SubmittedOn = ?
        WHERE Id = ?
    """, (new_date, candidate_id))

    conn.commit()
    conn.close()
    return True




def get_candidates_count(category_id=0):
    """
    Returns total number of candidates.
    If category_id=0, returns count for all categories.
    """
    conn = get_connection()
    cursor = conn.cursor()
    #print("get_candidates_count:",category_id)
    if category_id == 0:
        cursor.execute("SELECT COUNT(*) as count FROM candidates")
    else:
        cursor.execute("SELECT COUNT(*) as count FROM candidates WHERE CategoryId = ?", (category_id,))
    
    result = cursor.fetchone()
    conn.close()
    return result["count"] if result else 0

# ----------------- Get Paginated Candidates -----------------
def get_candidates_paginated(category_id=0, per_page=5, offset=0):
    """
    Returns a list of candidates for given category with pagination.
    category_id=0 means all categories.
    per_page = number of records per page
    offset = number of records to skip
    """
    conn = get_connection()
    cursor = conn.cursor()
    #print("get_tget_candidates_paginatedotal_categories:",category_id)
    if category_id == 0:
        cursor.execute(
            "SELECT * FROM candidates ORDER BY TotalScore DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        )
    else:
        cursor.execute(
            "SELECT * FROM candidates WHERE CategoryId = ? ORDER BY TotalScore DESC LIMIT ? OFFSET ?",
            (category_id, per_page, offset)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert sqlite3.Row objects to dicts
    candidates = [dict(row) for row in rows]
    return candidates

# ----------------- Get All Candidates (no pagination) -----------------
def get_all_candidates():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY TotalScore DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_total_categories(category_id=0):
    """
    Returns total distinct categories.
    If category_id=0, returns total count of all categories.
    Otherwise, checks if that category_id exists and returns 1 or 0.
    """
    conn = get_connection()
    cursor = conn.cursor()
    #print("get_total_categories:",category_id)
    if category_id == 0:
        cursor.execute("SELECT COUNT(DISTINCT CategoryId) as count FROM candidates")
    else:
        cursor.execute("SELECT COUNT(DISTINCT CategoryId) as count FROM candidates WHERE CategoryId = ?", (category_id,))

    result = cursor.fetchone()
    conn.close()
    return result["count"] if result else 0

def get_candidates_group_by_category(category_id=0):
    """
    Returns candidate counts grouped by category.
    If category_id=0, returns counts for all categories.
    Otherwise, filters only that category.
    """
    conn = get_connection()
    cursor = conn.cursor()
    #print("get_candidates_group_by_category:",category_id)
    if category_id == 0:
        query = """
        SELECT jc.name AS CategoryName, COUNT(c.id) AS total_candidates
        FROM candidates c
        JOIN job_categories jc ON c.CategoryId = jc.id
        GROUP BY jc.name
        """
        cursor.execute(query)
    else:
        query = """
        SELECT jc.name AS CategoryName, COUNT(c.id) AS total_candidates
        FROM candidates c
        JOIN job_categories jc ON c.CategoryId = jc.id
        WHERE c.CategoryId = ?
        GROUP BY jc.name
        """
        cursor.execute(query, (category_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_average_score(category_id=0):
    """
    Returns the average score of candidates.
    If category_id=0, returns average across all categories.
    Otherwise, filters by the given category_id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    #print("get_average_score:",category_id)
    if category_id == 0:
        cursor.execute("SELECT AVG(TotalScore) as avg_score FROM candidates")
    else:
        cursor.execute("SELECT AVG(TotalScore) as avg_score FROM candidates WHERE CategoryId = ?", (category_id,))

    result = cursor.fetchone()
    conn.close()
    return round(result["avg_score"], 2) if result and result["avg_score"] is not None else 0

def get_top_candidate(category_id=0):
    """
    Returns the top candidate (highest score).
    If category_id=0, finds across all categories.
    Otherwise, filters by the given category_id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    #print("get_top_candidate",category_id)
    if category_id == 0:
        cursor.execute("SELECT id, Candidate, TotalScore FROM candidates ORDER BY TotalScore DESC LIMIT 1")
    else:
        cursor.execute("SELECT id, Candidate, TotalScore FROM candidates WHERE CategoryId = ? ORDER BY TotalScore DESC LIMIT 1", (category_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "id": result["id"],
            "name": result["Candidate"],
            "score": result["TotalScore"]
        }
    else:
        return None
    
def get_skills_by_category(category_id=0):
    conn = get_connection()
    cursor = conn.cursor()
    #print("get_skills_by_category",category_id)

    if category_id == 0:
        # All categories
        cursor.execute("""
            SELECT LOWER(value) AS skill
            FROM candidates, json_each(Skills)
        """)
    else:
        # Specific category
        cursor.execute("""
            SELECT LOWER(value) AS skill
            FROM candidates, json_each(Skills)
            WHERE CategoryId = ?
        """, (category_id,))

    results = [row[0] for row in cursor.fetchall()]
    conn.close()

    return results

def get_weekly_submissions(category_id=0):
    conn = get_connection()
    cursor = conn.cursor()
    #print("get_weekly_submissions",category_id)
    if category_id == 0:
        # All categories
        cursor.execute("""
            SELECT DATE(SubmittedOn) AS submitted_date, COUNT(*) AS submissions
            FROM candidates
            GROUP BY DATE(SubmittedOn)
            ORDER BY submitted_date ASC
        """)
    else:
        # Specific category
        cursor.execute("""
            SELECT DATE(SubmittedOn) AS submitted_date, COUNT(*) AS submissions
            FROM candidates
            WHERE CategoryId = ?
            GROUP BY DATE(SubmittedOn)
            ORDER BY submitted_date ASC
        """, (category_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"SubmittedOn": row[0], "Submissions": row[1]} for row in results]








