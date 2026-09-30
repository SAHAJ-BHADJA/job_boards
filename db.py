"""
SQLite storage layer for Job Bot.

Schema is intentionally simple and idempotent: `url` is UNIQUE, so daily re-runs
use INSERT ... ON CONFLICT to append new jobs and refresh `last_seen_at` on
existing ones. History therefore accumulates and never gets wiped.

To move to Render Postgres later, only this file needs to change (keep the same
functions: init_db, upsert_jobs, fetch_all).
"""
import os
import sqlite3
from datetime import datetime, timezone

import config


def _connect():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT NOT NULL,
            company       TEXT,
            location      TEXT,
            url           TEXT NOT NULL UNIQUE,
            platform      TEXT NOT NULL,
            search_term   TEXT,
            posted_at     TEXT,      -- ISO8601 UTC, may be NULL if unknown
            first_seen_at TEXT NOT NULL,
            last_seen_at  TEXT NOT NULL,
            scraped_at    TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_platform ON jobs(platform)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_scraped ON jobs(scraped_at)")
    conn.commit()
    conn.close()


def upsert_jobs(jobs):
    """jobs: iterable of dicts with keys
    title, company, location, url, platform, search_term, posted_at (ISO or None).
    Returns (inserted_count, seen_again_count).
    """
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    inserted = 0
    seen_again = 0
    for j in jobs:
        if not j.get("url") or not j.get("title"):
            continue
        cur = conn.execute(
            """
            INSERT INTO jobs
                (title, company, location, url, platform, search_term,
                 posted_at, first_seen_at, last_seen_at, scraped_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(url) DO UPDATE SET
                last_seen_at = excluded.last_seen_at
            """,
            (
                j.get("title", "").strip(),
                (j.get("company") or "").strip(),
                (j.get("location") or "").strip(),
                j["url"].strip(),
                j.get("platform", "").strip(),
                j.get("search_term", ""),
                j.get("posted_at"),
                now,
                now,
                now,
            ),
        )
        # rowcount is 1 for insert; ON CONFLICT update also reports 1, so detect
        # via changes: compare via lastrowid not reliable. Use a select instead.
        if cur.rowcount == 1 and cur.lastrowid:
            # Could be insert or update; check if first_seen == now to classify.
            row = conn.execute(
                "SELECT first_seen_at FROM jobs WHERE url = ?", (j["url"].strip(),)
            ).fetchone()
            if row and row["first_seen_at"] == now:
                inserted += 1
            else:
                seen_again += 1
    conn.commit()
    conn.close()
    return inserted, seen_again


def fetch_all(order_by="scraped_at DESC, posted_at DESC"):
    conn = _connect()
    rows = conn.execute(f"SELECT * FROM jobs ORDER BY {order_by}").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def stats():
    conn = _connect()
    total = conn.execute("SELECT COUNT(*) c FROM jobs").fetchone()["c"]
    by_platform = conn.execute(
        "SELECT platform, COUNT(*) c FROM jobs GROUP BY platform ORDER BY c DESC"
    ).fetchall()
    conn.close()
    return total, [dict(r) for r in by_platform]
