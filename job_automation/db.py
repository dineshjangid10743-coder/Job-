import json
import sqlite3
from pathlib import Path
from typing import Iterable, List

from .models import Job


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db(db_path: Path) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                description TEXT,
                posted_at TEXT,
                employment_type TEXT,
                score REAL DEFAULT 0,
                raw TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                status TEXT DEFAULT 'new',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            )
            """
        )


def upsert_jobs(db_path: Path, jobs: Iterable[Job]) -> int:
    with get_connection(db_path) as conn:
        count = 0
        for job in jobs:
            conn.execute(
                """
                INSERT INTO jobs (source, title, company, location, url, description, posted_at, employment_type, score, raw)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    company=excluded.company,
                    location=excluded.location,
                    description=excluded.description,
                    posted_at=excluded.posted_at,
                    employment_type=excluded.employment_type,
                    score=excluded.score,
                    raw=excluded.raw
                """,
                (
                    job.source,
                    job.title,
                    job.company,
                    job.location,
                    job.url,
                    job.description,
                    job.posted_at,
                    job.employment_type,
                    job.score,
                    job.raw,
                ),
            )
            count += 1
        return count


def update_scores(db_path: Path, scored_jobs: Iterable[Job]) -> None:
    with get_connection(db_path) as conn:
        for job in scored_jobs:
            conn.execute(
                "UPDATE jobs SET score=? WHERE url=?",
                (job.score, job.url),
            )


def list_jobs(db_path: Path) -> List[Job]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT source, title, company, location, url, description, posted_at, employment_type, score, raw FROM jobs"
        ).fetchall()
        return [
            Job(
                source=row[0],
                title=row[1],
                company=row[2],
                location=row[3],
                url=row[4],
                description=row[5] or "",
                posted_at=row[6],
                employment_type=row[7],
                score=row[8] or 0.0,
                raw=row[9],
            )
            for row in rows
        ]
