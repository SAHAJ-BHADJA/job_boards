"""
SQLite storage layer for Job Bot.

Schema is intentionally simple and idempotent: `url` is UNIQUE, so daily re-runs
use INSERT ... ON CONFLICT to append new jobs and refresh `last_seen_at` on
existing ones. History therefore accumulates and never gets wiped.

To move to Render Postgres later, only this file needs to change (keep the same
functions: init_db, upsert_jobs, fetch_all).
"""
import csv
import os
import sqlite3
from datetime import datetime, timezone

import config

CSV_FIELDS = [
    "title", "company", "location", "url", "platform", "search_term",
    "posted_at", "first_seen_at", "last_seen_at", "scraped_at",
]


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


def import_csv(path=None):
    """Load a previously-committed CSV into the DB (preserving original timestamps).
    This is how history persists across ephemeral CI runs. No-op if file missing.
    Returns number of rows imported."""
    from scrapers import base  # local import to avoid a circular import at module load

    path = path or config.CSV_PATH
    if not os.path.exists(path):
        return 0
    conn = _connect()
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("url") or not row.get("title"):
                continue
            # Self-heal: prune rows that no longer pass the current location/role
            # rules (e.g. after tightening filters). Time window is NOT re-applied
            # so genuinely-old-but-valid history is preserved.
            if not base.match_role(row.get("title")):
                continue
            if not base.is_usa_remote(row.get("location")):
                continue
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """
                INSERT INTO jobs
                    (title, company, location, url, platform, search_term,
                     posted_at, first_seen_at, last_seen_at, scraped_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(url) DO NOTHING
                """,
                (
                    row.get("title", ""), row.get("company", ""), row.get("location", ""),
                    row["url"], row.get("platform", ""), row.get("search_term", ""),
                    row.get("posted_at") or None,
                    row.get("first_seen_at") or now,
                    row.get("last_seen_at") or now,
                    row.get("scraped_at") or now,
                ),
            )
            n += 1
    conn.commit()
    conn.close()
    return n


def export_csv(path=None):
    """Write the whole DB to CSV (the durable, committed source of truth)."""
    path = path or config.CSV_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = fetch_all(order_by="scraped_at DESC, posted_at DESC")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})
    return path


def export_xlsx(path):
    """Write a formatted Excel workbook with clickable job links."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment

    rows = fetch_all(order_by="scraped_at DESC, posted_at DESC")
    wb = Workbook()
    ws = wb.active
    ws.title = "Jobs"
    headers = ["Job Title", "Company", "Platform", "Role", "Location",
               "Posted", "Scraped", "Link"]
    ws.append(headers)
    header_fill = PatternFill("solid", fgColor="1F2530")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = header_fill
        c.alignment = Alignment(vertical="center")
    for r in rows:
        ws.append([
            r.get("title", ""), r.get("company", ""), r.get("platform", ""),
            r.get("search_term", ""), r.get("location", ""),
            r.get("posted_at", ""), r.get("scraped_at", ""), r.get("url", ""),
        ])
        cell = ws.cell(row=ws.max_row, column=1)
        if r.get("url"):
            cell.hyperlink = r["url"]
            cell.font = Font(color="2563EB", underline="single")
    widths = [46, 22, 20, 22, 26, 20, 20, 50]
    for i, wdt in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + i)].width = wdt
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:H{ws.max_row}"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    return path


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
