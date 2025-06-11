import sqlite3
import json
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

DB_PATH = "cv_scout.db"

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        logger.info(f"--- DATABASE: Successful connection to SQLite DB at {DB_PATH} ---")
    except sqlite3.Error as e:
        logger.error(f"--- DATABASE: Error connecting to SQLite DB: {e} ---")
        raise
    return conn

def create_tables():
    """Create the necessary tables if they don't exist."""
    conn = create_connection()
    if not conn:
        return

    # Use a set of queries to ensure tables are created correctly
    create_table_queries = [
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE,
            phone_number TEXT,
            full_report_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            match_score INTEGER,
            match_summary TEXT,
            status TEXT DEFAULT 'Received',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id),
            UNIQUE(job_id, candidate_id)
        );
        """
    ]
    
    try:
        cursor = conn.cursor()
        for query in create_table_queries:
            cursor.execute(query)
        conn.commit()
        logger.info("--- DATABASE: Tables verified/created successfully. ---")
    except sqlite3.Error as e:
        logger.error(f"--- DATABASE: Error creating tables: {e} ---")
    finally:
        if conn:
            conn.close()

def add_job(description: str) -> int:
    """Add a new job description to the database and return its ID."""
    conn = create_connection()
    sql = ''' INSERT INTO jobs(description)
              VALUES(?) '''
    cursor = conn.cursor()
    cursor.execute(sql, (description,))
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    logger.info(f"--- DATABASE: Added new job with ID: {job_id} ---")
    return job_id

def add_or_update_candidate(report: Dict[str, Any]) -> int:
    """
    Add a new candidate or update existing one based on email.
    Returns the candidate's ID.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    email = report.get("mail")
    full_name = report.get("full_name")
    phone_number = report.get("phone_number")
    full_report_json = json.dumps(report)

    # Check if candidate exists
    cursor.execute("SELECT id FROM candidates WHERE email = ?", (email,))
    data = cursor.fetchone()
    
    if data:
        # Update existing candidate
        candidate_id = data[0]
        sql = ''' UPDATE candidates
                  SET full_name = ?, phone_number = ?, full_report_json = ?
                  WHERE id = ? '''
        cursor.execute(sql, (full_name, phone_number, full_report_json, candidate_id))
        logger.info(f"--- DATABASE: Updated existing candidate with ID: {candidate_id} ---")
    else:
        # Insert new candidate
        sql = ''' INSERT INTO candidates(full_name, email, phone_number, full_report_json)
                  VALUES(?,?,?,?) '''
        cursor.execute(sql, (full_name, email, phone_number, full_report_json))
        candidate_id = cursor.lastrowid
        logger.info(f"--- DATABASE: Added new candidate with ID: {candidate_id} ---")
        
    conn.commit()
    conn.close()
    return candidate_id

def add_application(job_id: int, candidate_id: int, score: int, summary: str):
    """Link a candidate to a job by creating an application record."""
    conn = create_connection()
    sql = ''' INSERT OR REPLACE INTO applications(job_id, candidate_id, match_score, match_summary)
              VALUES(?,?,?,?) '''
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (job_id, candidate_id, score, summary))
        conn.commit()
        logger.info(f"--- DATABASE: Linked candidate {candidate_id} to job {job_id} with score {score} ---")
    except sqlite3.Error as e:
        logger.error(f"--- DATABASE: Error adding application: {e} ---")
    finally:
        conn.close()

# Initialize the database and tables when this module is first imported
create_tables()


def get_all_jobs():
    """Retrieves all jobs from the database."""
    conn = create_connection()
    try:
        # The query selects the description and the id, creating a user-friendly string
        query = "SELECT description || ' (ID: ' || id || ')' as job_display, id FROM jobs ORDER BY created_at DESC"
        jobs = conn.execute(query).fetchall()
        logger.info(f"--- DATABASE: Retrieved {len(jobs)} jobs. ---")
        # Return a list of tuples: [('Job Display String', job_id), ...]
        return jobs
    except sqlite3.Error as e:
        logger.error(f"--- DATABASE: Error retrieving jobs: {e} ---")
        return []
    finally:
        if conn:
            conn.close()

def get_ranked_candidates_for_job(job_id: int):
    """
    Retrieves and ranks candidates for a specific job ID from the database.
    """
    conn = create_connection()
    query = """
        SELECT
            c.full_name,
            c.email,
            a.match_score,
            a.match_summary,
            a.status,
            c.id as candidate_id
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        WHERE a.job_id = ?
        ORDER BY a.match_score DESC;
    """
    try:
        # Use pandas to read the SQL query directly into a DataFrame
        import pandas as pd
        df = pd.read_sql_query(query, conn, params=(job_id,))
        logger.info(f"--- DATABASE: Retrieved {len(df)} candidates for job ID {job_id}. ---")
        return df
    except Exception as e:
        logger.error(f"--- DATABASE: Error retrieving candidates for job {job_id}: {e} ---")
        # Return an empty DataFrame on error
        import pandas as pd
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()