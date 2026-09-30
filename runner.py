"""
Job Bot runner — the daily entry point.

Runs every Tier 1 scraper, filters to remote-USA target roles posted in the last
24h, stores results in SQLite (idempotent), then regenerates the static
dashboard. One scraper failing never aborts the run.

Usage:
    python runner.py
"""
import os
import shutil
import sys
import traceback
from datetime import datetime, timezone

import config
import db
import build_dashboard
from scrapers import (
    remoteok, remotive, weworkremotely, himalayas,
    workingnomads, hackernews, adzuna, jooble,
)

SCRAPERS = [
    remoteok, remotive, weworkremotely, himalayas,
    workingnomads, hackernews, adzuna, jooble,
]


def _log(msg):
    os.makedirs(config.LOG_DIR, exist_ok=True)
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line)
    with open(os.path.join(config.LOG_DIR, "runner.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    _log("=== Job Bot run started ===")
    db.init_db()

    # Load prior history from the committed CSV (persists across ephemeral CI runs).
    imported = db.import_csv()
    _log(f"CSV   imported {imported} prior rows from {config.CSV_PATH}")

    all_jobs = []
    for mod in SCRAPERS:
        name = getattr(mod, "NAME", mod.__name__)
        # Skip key-gated scrapers cleanly when disabled.
        if hasattr(mod, "enabled") and not mod.enabled():
            _log(f"SKIP  {name} (no API key configured)")
            continue
        try:
            jobs = mod.scrape()
            _log(f"OK    {name}: {len(jobs)} matching jobs")
            all_jobs.extend(jobs)
        except Exception as e:  # noqa: BLE001
            _log(f"FAIL  {name}: {e}")
            _log(traceback.format_exc())

    inserted, seen_again = db.upsert_jobs(all_jobs)
    _log(f"DB    matched-this-run={len(all_jobs)} new={inserted} already-seen={seen_again}")

    # Durable source of truth + downloadable exports.
    db.export_csv(config.CSV_PATH)
    os.makedirs(config.DASHBOARD_DIR, exist_ok=True)
    shutil.copyfile(config.CSV_PATH, config.DASHBOARD_CSV)
    try:
        db.export_xlsx(config.DASHBOARD_XLSX)
    except Exception as e:  # noqa: BLE001 — never fail the run over Excel export
        _log(f"WARN  xlsx export failed: {e}")

    build_dashboard.build()
    total, by_platform = db.stats()
    _log(f"OUT   csv={config.CSV_PATH} xlsx+html -> {config.DASHBOARD_DIR}")
    _log(f"DASH  rebuilt (DB total={total})")
    _log("=== Job Bot run finished ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
