# Job Bot 🛰️

Daily aggregator for **remote-USA** engineering roles — *Software Engineer, Machine
Learning Engineer, Platform Engineer, New-Grad Software Engineer* — pulled from
Tier-1 job boards (official APIs / clean JSON / RSS), stored in a database, and
shown on a static HTML dashboard.

> **Flow:** scrape each platform → keep jobs posted in the last 24h (remote, USA)
> → store in DB (idempotent, history accumulates) → regenerate dashboard.

## Quick start (local)

```bash
python -m pip install -r requirements.txt
python runner.py            # scrape + store + rebuild dashboard
# then open dashboard/index.html
```

## Sources (Phase 1, Tier 1)

| No key needed | Free key needed |
|---|---|
| Remote OK, Remotive, We Work Remotely, Himalayas, Working Nomads, Hacker News (Who is Hiring) | Adzuna, Jooble |

Set free keys via environment variables (see `.env.example`). Scrapers auto-skip
when a key is missing.

## Configuration

All knobs live in `config.py`: target role matchers, the remote-USA location
filter, the 24-hour window, and paths.

## Scheduling

Designed to run once per day. Local: Windows Task Scheduler. Cloud: Render Cron
Job (see deployment notes in `PROJECT_CONTEXT.md`).

## Full context / handoff

**`PROJECT_CONTEXT.md`** is the living design + status doc — read it to understand
decisions, the yield findings, the file map, and the Render deployment plan.

## Roadmap

- **Phase 1 (done):** Tier 1 scrapers + SQLite + static dashboard.
- **Next:** add Adzuna/Jooble keys for volume; deploy to Render.
- **Phase 2:** Tier 2 boards (Built In, Wellfound, YC/Ashby/Greenhouse, …).
- **Phase 3+:** dedup across boards, alerts, more roles.
