import json
import sqlite3
from pathlib import Path
from datetime import datetime


# -------JSON-------------------------------------------------------
def save_to_json(jobs: list[dict], filepath: str = "jobs.json") -> int:
    """
    Append new jobs to a JSON file. Deduplicates by URL.
    Returns the count of newly added jobs
    """
    existing: list[dict] = []

    if Path(filepath).exists():
        with open(filepath) as f:
            existing = json.load(f)
    seen_urls = {job["url"] for job in existing}
    new_jobs = [j for j in jobs if j["url"] not in seen_urls]

    for jobs in new_jobs:
        job["scraped_at"] = datetime.utcnow().isoformat()
    with open(filepath, "w") as f:
        json.dump(existing + new_jobs, f, indent=2)
    print(f"[JSON] Saved {len(new_jobs)} new jobs -> {filepath}")
    return len(new_jobs)


# ----------SQLite-----------------------------------------------------------------


def init_db(db_path: str = "jobs.db") -> sqlite3.Connection:
    """Create the DB and jobs table if they don't exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS jobs(
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    title          TEXT NOT NULL,
    company        TEXT,
    location       TEXT,
    url            TEXT UNIQUE,
    tags           TEXT,
    scraped_at     TEXT
    )""")
    conn.commit()
    return conn


def save_to_db(jobs: list[dict], db_path: str = "jobs.db") -> int:
    """
    Insert new jobs into SQLite. Skips duplicates (by URL).
    Returns the count of newly inserted rows."""
    conn = init_db(db_path)
    inserted = 0

    for jobs in jobs:
        try:
            conn.execute(
                """
                INSERT INTO jobs(title, company, location, url , tags, scraped_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    job.get("title"),
                    job.get("company"),
                    job.get("location"),
                    job.get("url"),
                    json.dumps(job.get("tags", [])),
                    datetime.utcnow().isoformat(),
                ),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # duplicate URL -skip silently
    conn.commit()
    conn.close()

    print(f"[SQLite] Inserted {inserted} new jobs -> {db_path}")
    return inserted


def query_jobs(keyword: str = "", db_path: str = "jobs.db") -> list[dict]:
    """Fetch jobs from SQLite, optionally filtered by keyword in little."""
    conn = init_db(db_path)
    query = "SELECT title, company, location, url, tags FROM jobs"
    params = ()
    if keyword:
        query += " WHERE LOWER(title) LIKE ?"
        params = (f"%{keyword.lower()}%",)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [
        {"title": r[0], "company": r[1], "location": r[2], "url": r[3], "tags": r[4]}
        for r in rows
    ]
