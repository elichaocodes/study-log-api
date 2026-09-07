import os
import sqlite3
from pathlib import Path

DEFAULT_DATABASE_PATH = Path(__file__).with_name("study_sessions.db")
DATABASE_PATH = Path(
    os.environ.get("DATABASE_PATH", str(DEFAULT_DATABASE_PATH))
)

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    connection = get_connection()

    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS study_sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        minutes INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    connection.commit()
    connection.close()

def insert_study_session(subject: str,minutes: int,) -> int:
    connection = get_connection()
    cursor = connection.execute(
        """
        INSERT INTO study_sessions (subject, minutes)
        VALUES (?, ?)
        """,
        (subject, minutes)
    )

    connection.commit()
    connection.close()

    return cursor.lastrowid

def get_study_session(session_id: int):
    connection = get_connection()
    row = connection.execute(
        """
        SELECT session_id, subject, minutes, created_at FROM study_sessions
        WHERE session_id = ?
        """,
        (session_id,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None

def list_study_sessions():
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT session_id, subject, minutes, created_at
        FROM study_sessions
        ORDER BY session_id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

def list_study_sessions_by_subject(subject: str):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT session_id, subject, minutes, created_at
        FROM study_sessions
        WHERE subject = ?
        ORDER BY session_id DESC
        """,
        (subject,)
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

def list_study_sessions_by_min_minutes(min_minutes: int):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT session_id, subject, minutes, created_at
        FROM study_sessions
        WHERE minutes >= ?
        ORDER BY session_id DESC
        """,
        (min_minutes,)
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

def list_study_sessions_by_subject_and_min_minutes(subject: str, min_minutes: int):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT session_id, subject, minutes, created_at
        FROM study_sessions
        WHERE subject = ?
        AND minutes >= ?
        ORDER BY session_id DESC
        """,
        (subject, min_minutes)
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

def delete_study_session(session_id: int):
    connection = get_connection()
    connection.execute(
        """
        DELETE FROM study_sessions 
        WHERE session_id = ?
        """,
        (session_id,)
    )

    connection.commit()
    connection.close()
