# Job Bot — Project Context & Handoff

> **Purpose of this file:** Single source of truth for the Job Bot project. Any new chat / model can read this file top-to-bottom and understand the goal, the decisions, the current status, and exactly where to continue. **Keep appending to the "Progress Log" section at the bottom after every work session.**

- **Owner:** Sahaj Bhadja (sahajbhadja10@gmail.com)
- **Working directory:** `E:\Job_bot`
- **OS:** Windows 11, PowerShell primary shell
- **Created:** 2026-09-29
- **Last updated:** 2026-09-30
- **Current phase:** Phase 1 — BUILT & RUNNING locally. Tier 1 scrapers + SQLite + static HTML dashboard done. Next: get Adzuna/Jooble keys for volume, then deploy to Render.

---

## 1. Goal (in the user's words)

Build a job-aggregation pipeline + dashboard.

**Flow:**
```
scrape each platform  ->  keep only jobs posted in last 24 hrs  ->  store in DB  ->  display in dashboard
```
- **1 run per day**, for all platforms.
- Store results in a database; **append/update** — do not wipe. Keep history growing.
- **Dashboard columns (minimum):** Job Title | Job Link | Platform | Date Scraped
- Later phases can add filtering, dedup, etc. This first cut = **Phase 1**.

**Target job titles to search for (across all boards):**
1. Software Engineer
2. Machine Learning Engineer
3. Platform Engineer
4. New Grad Software Engineer

---

## 2. Target job boards (from user)

These were provided as "sites that do NOT require login to view all job listings."
> ⚠️ IMPORTANT: "no login required to browse" ≠ "no anti-bot protection." Feasibility differs a lot per site. See Section 3 for the realistic tiering.

### Group A — General / large boards
| Platform | URL |
|---|---|
| Indeed | https://www.indeed.com/jobs |
| ZipRecruiter | https://www.ziprecruiter.com/jobs-search |
| Dice | https://www.dice.com/jobs |
| Levels.fyi Jobs | https://www.levels.fyi/jobs/ |
| Simplify | https://simplify.jobs/jobs |
| Jobright | https://jobright.ai/jobs |
| Teal | https://www.tealhq.com/job-search |
| Built In | https://builtin.com/jobs |
| Startup.jobs | https://startup.jobs/ |
| Y Combinator Jobs | https://www.ycombinator.com/jobs |
| Wellfound | https://wellfound.com/jobs |
| Monster | https://www.monster.com/jobs |
| SimplyHired | https://www.simplyhired.com/ |
| Jooble | https://jooble.org/ |
| Adzuna | https://www.adzuna.com/ |
| Talent.com | https://www.talent.com/jobs |
| CareerBuilder | https://www.careerbuilder.com/jobs |
| Snagajob | https://www.snagajob.com/ |

### Group B — Remote-focused boards
| Platform | URL |
|---|---|
| We Work Remotely | https://weworkremotely.com/remote-jobs |
| Remote OK | https://remoteok.com/ |
| Remote.co | https://remote.co/remote-jobs/ |
| Himalayas | https://himalayas.app/jobs |
| Remotive | https://remotive.com/remote-jobs |
| NoDesk | https://nodesk.co/remote-jobs/ |
| Working Nomads | https://www.workingnomads.com/jobs |
| JustRemote | https://justremote.co/remote-jobs |
| Jobspresso | https://jobspresso.co/remote-work/ |
| Remote4Me | https://remote4me.com/ |
| DailyRemote | https://dailyremote.com/ |
| Remote Rocketship | https://www.remoterocketship.com/ |
| NoCommute | https://nocommute.substack.com/ |

### Group C — Niche / specialized boards
| Platform | Focus | URL |
|---|---|---|
| Authentic Jobs | Tech/design | https://authenticjobs.com/ |
| Climatebase | Climate tech | https://climatebase.org/jobs |
| Idealist | Nonprofit/mission-driven | https://www.idealist.org/en/jobs |
| Hacker News – Who is Hiring? | Startups/engineers | https://news.ycombinator.com/ |
| IEEE Job Site | Engineering | https://jobs.ieee.org/ |
| ACM Career & Job Center | CS/software | https://jobs.acm.org/ |
| HigherEdJobs | Universities/research | https://www.higheredjobs.com/ |
| Nature Careers | Research/science | https://www.nature.com/naturecareers/jobs/ |

**Total: ~39 boards.**

---

## 3. Feasibility assessment (THE honest answer)

**Can this be built? Yes.** The daily-run → DB → dashboard machinery is standard and reliable. The *hard* part is per-site scraping, because these ~39 boards fall into very different difficulty tiers. Setting expectations correctly up front is the whole point of this section.

### Tier 1 — Reliable (official API / clean JSON / RSS). Do these FIRST.
These return structured data with real posting dates → clean 24h filtering, low breakage.
- **Remote OK** — public JSON: `https://remoteok.com/api` (epoch date field)
- **Remotive** — public API: `https://remotive.com/api/remote-jobs` (has `publication_date`)
- **We Work Remotely** — RSS feeds per category (e.g. `.../categories/remote-programming-jobs.rss`)
- **Himalayas** — JSON API: `https://himalayas.app/jobs/api`
- **Working Nomads** — JSON: `https://www.workingnomads.com/api/exposed_jobs/`
- **Hacker News "Who is Hiring"** — Algolia API: `http://hn.algolia.com/api/v1/...` (monthly thread; comment timestamps)
- **Adzuna** — official REST API (needs free `app_id` + `app_key`; has posting date, good filters)
- **Jooble** — official API (needs free API key; POST request)
- **Talent.com** — partner XML feed/API (may require signup; public HTML fallback exists)

> Tier 1 alone gives a genuinely useful daily dashboard with several hundred fresh SWE/ML/Platform roles. **This is the recommended Phase 1 scope.**

### Tier 2 — Medium (HTML scrape, JS rendering, occasional breakage). Phase 2.
No official API, but no hard anti-bot wall either. Need HTML parsing and often a headless browser (Playwright). Selectors will break when sites redesign → ongoing maintenance. Posting-date availability varies (some only show "3 days ago", some none → 24h filter becomes best-effort).
- Built In, Wellfound, Startup.jobs, Y Combinator (many YC listings are on Ashby/Greenhouse/Lever — scrapeable), Simplify, Jobright, Teal, Remote.co, NoDesk, JustRemote, Jobspresso, DailyRemote, Remote Rocketship, Remote4Me, NoCommute (Substack), Authentic Jobs, Climatebase, Idealist, IEEE, ACM, HigherEdJobs, Nature Careers, SimplyHired, Snagajob, CareerBuilder.

### Tier 3 — Hard / unreliable (aggressive anti-bot). Manage expectations / may skip.
These deploy DataDome / Cloudflare / PerimeterX and actively block automated traffic. Scraping them reliably usually needs **paid rotating residential proxies + anti-bot bypass**, and even then it's brittle and arguably against their ToS.
- **Indeed** (DataDome — very hard), **ZipRecruiter** (hard), **Monster** (hard), **Dice** (moderate-hard), **Levels.fyi** (JS-heavy SPA).

**Recommendation for Tier 3:** either (a) accept frequent gaps, (b) use a paid job-data API that aggregates them (e.g., a third-party jobs API), or (c) drop them from automated scraping and treat them as manual/optional. Decide with the user before investing here.

### Cross-cutting constraints to be honest about
- **"Last 24 hours" is only as good as the date each site exposes.** Tier 1 = precise. Many Tier 2 sites give relative/no dates → we approximate (e.g., treat "today"/"1 day ago" as within 24h; or treat "first time we ever saw this listing" as its discovery date).
- **Legal/ToS:** Several boards' ToS prohibit scraping. APIs are the compliant path where available. Flag this to the user; keep volume polite (rate-limit, cache, identify a UA).
- **Dedup:** The same job appears on many boards. Phase 1 stores per-platform; a dedup layer (by normalized title+company+link) is a Phase 2+ nice-to-have.

---

## 4. Proposed architecture (NOT yet implemented — for review)

```
E:\Job_bot\
  scrapers\           # one module per board (or per tier)
    tier1\            # api/json/rss based — start here
    tier2\            # html/playwright based
  core\
    models.py         # DB schema / ORM
    dedup.py
    date_filter.py    # 24h window logic
    runner.py         # orchestrates all scrapers, writes to DB
  db\
    jobs.sqlite       # SQLite DB (simple, file-based, perfect for 1 machine)
  dashboard\
    app.py            # dashboard server (see options below)
  logs\
  config.yaml         # titles, board toggles, API keys
  requirements.txt
  PROJECT_CONTEXT.md  # <-- this file
```

### Stack choices (candidates — confirm with user)
- **Language:** Python 3.11+ (best scraping ecosystem).
- **HTTP/parse:** `httpx` + `selectolax`/`BeautifulSoup`; **Playwright** for JS-heavy Tier 2.
- **DB:** **SQLite** (zero-setup, single file, fine for this scale). Upgrade to Postgres only if it grows.
- **Schema (jobs table):** `id, title, company, location, url (unique), platform, posted_at (nullable), first_seen_at, scraped_at, search_term, raw_json`.
  - Dedup/idempotency key: `url` (UNIQUE) → daily re-runs `INSERT OR IGNORE`, so history accumulates without duplicates.
- **Dashboard options (pick one):**
  1. **Streamlit** — fastest to build, filters/sorting free, runs locally (`streamlit run`).
  2. **FastAPI + static HTML/JS** — more control, can host later.
  3. **Static HTML dashboard** reading a generated `jobs.json` — simplest to share, no server. *(Could also be a Claude Artifact.)*
- **Scheduling (1 run/day):**
  1. **Windows Task Scheduler** (native, survives reboots) — recommended for a local machine.
  2. Claude Code **`schedule` skill / scheduled cloud agent** — if runs should happen even when PC is off.
  3. A simple `while True: sleep(24h)` script — fragile, not recommended.

### Decisions made (2026-09-30)
- [x] Phase 1 scope = **Tier 1 boards only**.
- [x] Location filter = **Remote, USA only** (US indicators + worldwide/anywhere accepted; region-locked non-US dropped). See `config.py` → `INCLUDE_WORLDWIDE`, `US_INDICATORS`, etc.
- [x] Dashboard = **static HTML page** (self-contained, embeds data as JSON, client-side search/filter/sort).
- [x] Scheduler = **cloud** (Render). Build locally first, then host on Render.
- [x] Tier 3 (Indeed/ZipRecruiter/Monster/Dice/Levels) = **deferred/skipped** for now.
- [ ] Adzuna/Jooble free API keys — **NOT yet obtained** (see Section 7, highest-impact next step).

---

## 5. What is actually built (Phase 1) — file map

All under `E:\Job_bot\`. Python 3.13, deps: `requests`, `feedparser`.

| File | Purpose |
|---|---|
| `config.py` | All settings: target role matchers, remote-USA filter lists, 24h window, API keys (from env), paths. |
| `db.py` | SQLite layer. Table `jobs` with `url` UNIQUE → idempotent daily upserts (append history, refresh `last_seen_at`). Functions: `init_db`, `upsert_jobs`, `fetch_all`, `stats`. |
| `scrapers/base.py` | Shared: HTTP session w/ retry, `match_role()`, `is_usa_remote()`, `parse_dt()`, `within_window()`, `filter_jobs()` (applies role + location + 24h uniformly). |
| `scrapers/remoteok.py` | Remote OK public JSON `/api`. No key. |
| `scrapers/remotive.py` | Remotive public API (software-dev category). No key. |
| `scrapers/weworkremotely.py` | WWR RSS feeds (4 categories) via feedparser. No key. |
| `scrapers/himalayas.py` | Himalayas public JSON API. No key. |
| `scrapers/workingnomads.py` | Working Nomads public JSON. No key. |
| `scrapers/hackernews.py` | HN "Who is Hiring" via Algolia API (best-effort, freeform parsing). No key. |
| `scrapers/adzuna.py` | Adzuna REST API. **Needs free `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` env vars**; auto-skips if unset. |
| `scrapers/jooble.py` | Jooble POST API. **Needs free `JOOBLE_API_KEY` env var**; auto-skips if unset. |
| `runner.py` | **Daily entry point.** Runs all scrapers (failures isolated), upserts to DB, rebuilds dashboard, logs to `logs/runner.log`. |
| `build_dashboard.py` | Reads DB → writes self-contained `dashboard/index.html`. |
| `db/jobs.sqlite` | The database (created on first run). |
| `dashboard/index.html` | The dashboard (regenerated each run). |

**How to run locally:**
```
cd E:\Job_bot
python -m pip install -r requirements.txt   # once
python runner.py                            # daily
```
Then open `dashboard/index.html` in a browser.

## 6. First-run results & the IMPORTANT yield finding

First live run (2026-09-30 00:30 UTC) succeeded end-to-end: **3 jobs** stored
(Himalayas 1, We Work Remotely 2). RemoteOK/Remotive/WorkingNomads/HN = 0.

**This low number is NOT a bug — the filter funnel was verified working.** Root causes:
1. **Free no-key endpoints serve cached/limited data, not truly live 24h.**
   - Remote OK `/api`: newest job it returns is ~4 days old (throttled cache).
   - Remotive free API: returned only 16 software-dev jobs, newest ~8 days old.
   - So a strict *last-24h* filter legitimately yields 0 from these on a given day.
2. **The intersection is narrow by design:** role match AND remote-USA AND posted-in-24h. Few brand-new postings satisfy all three per day.
3. **By design the DB accumulates** across daily runs, so coverage grows over time — day 1 is just thin.

Funnel numbers captured for reference (raw → role_ok → loc_ok → in_24h):
- RemoteOK: 99 → 14 → 55 → 0 (newest 2026-09-26)
- Remotive: 16 → 3 → 14 → 0 (newest 2026-09-21)
- Working Nomads: 57 → 3 → 25 → 4 (but role∩loc∩24h = 0)

## 7. Highest-impact next steps (in priority order)

1. **Get free Adzuna API keys** — https://developer.adzuna.com/ (instant, free tier).
   Adzuna has real US coverage with a true `max_days_old=1` filter → this is the
   single biggest lever for actual remote-USA volume. Set env vars
   `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`, re-run `python runner.py`. Scraper already written.
2. **Get free Jooble API key** — https://jooble.org/api/about → set `JOOBLE_API_KEY`. Scraper already written.
3. **Deploy to Render** (see Section 8).
4. (Optional) Broaden Remotive to more categories; add more WWR feeds.
5. (Later) Phase 2 Tier 2 boards (Built In, Wellfound, YC/Ashby/Greenhouse, etc.).

## 8. Render deployment plan (not done yet)

Chosen: cloud scheduler. Render specifics to implement:
- **Persistence:** Render's filesystem is ephemeral. SQLite on it is wiped on
  redeploy/restart. Two options:
  - (a) **Render Persistent Disk** attached to both services (simplest; keep SQLite). Point `JOBBOT_DB` env at the disk mount path.
  - (b) **Render Postgres** (free tier) — swap `db.py` internals (functions stay the same). More robust for a hosted app.
- **Two services from this repo:**
  - **Cron Job** service → command `python runner.py`, schedule e.g. `30 13 * * *` (daily). Does scrape + DB write + regenerate dashboard.
  - **Web Service (or Static Site)** → serves `dashboard/index.html`.
    - If Static Site: needs the cron to write into the same persistent disk the web service reads, OR trigger a redeploy. Simplest robust path = a tiny Flask/`http.server` **Web Service** that serves the `dashboard/` dir from the shared disk. (A ~10-line server is fine; keeps the "just an HTML page" UX.)
- **Secrets:** set `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `JOOBLE_API_KEY` as Render env vars.
- **Repo:** needs `git init` + push to GitHub for Render to deploy from. (Project is NOT a git repo yet.)
- TODO files to add for Render: `render.yaml` (blueprint), a minimal server script, `.gitignore` (exclude `db/`, `logs/`, `__pycache__`).

## 9. Legacy: original decisions checklist (all resolved above in Section 4)

---

## 6. Progress Log (append newest at bottom — never delete history)

### 2026-09-29 — Session 1 (model: Opus 4.8)
- Received requirements + 3 board lists (~39 boards) + 4 target job titles.
- User asked ONLY for a feasibility check + this handoff file; explicitly said do NOT implement yet.
- Produced feasibility tiering (Tier 1 reliable / Tier 2 medium / Tier 3 hard).
- Created `E:\Job_bot\PROJECT_CONTEXT.md` (this file).
- Confirmed to user: **Yes, this is doable**, with the honest caveat that Indeed/ZipRecruiter/Monster/Dice/Levels are anti-bot-hardened and unreliable to scrape for free.
- **Awaiting:** user's answers to Open Decisions (Section 4) before any implementation.

### 2026-09-30 — Session 2 (model: Opus 4.8)
- User decisions: **Phase 1 Tier 1 only, remote USA only, static HTML page, cloud scheduler (Render), build locally now.**
- Built the whole Phase 1 pipeline (see Section 5 file map): `config.py`, `db.py`, 8 scrapers, `runner.py`, `build_dashboard.py`.
- Installed deps (`requests`, `feedparser`), ran `python runner.py` successfully.
- **First run: 3 jobs stored** (Himalayas 1, WWR 2). Diagnosed the low yield — confirmed it's expected behavior, not a bug (Section 6): free no-key endpoints serve cached/stale data so few fall in the strict 24h window.
- Sent the rendered dashboard to the user.
- **Next action:** user to obtain free **Adzuna** (+ optionally Jooble) API keys → set env vars → re-run for real USA volume (scrapers already written). Then Render deploy (Section 8): needs `git init`, `render.yaml`, a tiny server, persistent disk or Postgres.
- **Blocker:** Adzuna/Jooble keys (free, user action). Project not yet a git repo (needed for Render).

<!-- TEMPLATE for next entry:
### YYYY-MM-DD — Session N (model: ...)
- What was done:
- Files added/changed:
- Decisions made:
- Blockers:
- Next action:
-->
