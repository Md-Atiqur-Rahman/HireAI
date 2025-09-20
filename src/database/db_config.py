import os
import sqlite3
from sqlite3 import Connection

# src/db.py
import sqlite3
import json

# DB_FILE = "E:/Thesis/resume-analyzer/job_portal.db"  # absolute path ensures consistency
DB_FILE = os.getenv("DB_PATH", "job_portal.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def drop_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()
    print(f"Table '{table_name}' dropped successfully.")

# Usage

