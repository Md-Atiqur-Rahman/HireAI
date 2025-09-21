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



def get_candidates_count(category_id=0):
    """
    Returns total number of candidates.
    If category_id=0, returns count for all categories.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
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