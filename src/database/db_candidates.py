import json
import sqlite3
import pandas as pd

from src.database.db_config import get_connection

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
        CategoryId INTEGER
    )
    """)
    
    conn.commit()
    conn.close()

def save_candidate(Name, email, phone, experience, total_score, skills, summary_text, category_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT 1 FROM candidates WHERE Email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False  # Email exists, don't save
    skills_str = json.dumps(skills) if isinstance(skills, list) else str(skills)
    cursor.execute("""
        INSERT INTO candidates 
        (Candidate, Email, Contact, Experience, TotalScore, Skills, SummaryText, CategoryId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        Name,
        email,
        phone,
        experience,
        total_score,
        skills_str,
        summary_text,
        category_id
    ))

    conn.commit()
    conn.close()
    return True  # Successfully saved

def get_all_candidates():
    """
    Fetch all candidates from the database.
    Returns a list of dictionaries with candidate info.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Candidate, Email, Contact, Experience, TotalScore, Skills, SummaryText, CategoryId
        FROM candidates
    """)
    rows = cursor.fetchall()
    conn.close()

    # Convert to list of dicts
    candidates = []
    for row in rows:
        candidates.append({
            "Candidate": row[0],
            "Email": row[1],
            "Contact": row[2],
            "Experience": row[3],
            "TotalScore": row[4],
            "Skills": row[5].split(",") if row[5] else [],  # Assuming skills stored as comma-separated string
            "SummaryText": row[6],
            "CategoryId": row[7]
        })
    return candidates



def get_candidates_paginated(category_id=None, limit=5, offset=0):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if category_id:
        cursor.execute("""
            SELECT rowid, * FROM candidates
            WHERE category_id = ?
            ORDER BY TotalScore DESC
            LIMIT ? OFFSET ?
        """, (category_id, limit, offset))
    else:
        cursor.execute("""
            SELECT rowid, * FROM candidates
            ORDER BY TotalScore DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]



def get_candidates_count(category_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if category_id:
        cursor.execute("SELECT COUNT(*) FROM candidates WHERE category_id = ?", (category_id,))
    else:
        cursor.execute("SELECT COUNT(*) FROM candidates")

    count = cursor.fetchone()[0]
    conn.close()
    return count





