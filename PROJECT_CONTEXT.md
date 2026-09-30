# Job Bot — Project Context & Handoff

> **Purpose of this file:** Single source of truth for the Job Bot project. Any new chat / model can read this file top-to-bottom and understand the goal, the decisions, the current status, and exactly where to continue. **Keep appending to the "Progress Log" section at the bottom after every work session.**

- **Owner:** Sahaj Bhadja (sahajbhadja10@gmail.com)
- **Working directory:** `E:\Job_bot`
- **OS:** Windows 11, PowerShell primary shell
- **Created:** 2026-09-29
- **Last updated:** 2026-09-30
- **Current phase:** Phase 2 — **DEPLOYED & LIVE.** Phase 1 (remote job boards) + Phase 2 (ATS company boards: Greenhouse/Lever/Ashby, plus Jobicy & Jobspresso), auto-run daily via GitHub Actions, hosted free on GitHub Pages. Remaining lever: add free Adzuna/Jooble keys, and expand ATS company lists in `config.py`.
- **Live dashboard:** https://sahaj-bhadja.github.io/job_boards/
- **Repo:** https://github.com/SAHAJ-BHADJA/job_boards

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
| `scrapers/greenhouse.py` | **(Phase 2)** Greenhouse ATS boards for companies in `config.GREENHOUSE_COMPANIES`. No key. `require_remote=True`. |
| `scrapers/lever.py` | **(Phase 2)** Lever ATS boards for `config.LEVER_COMPANIES`. No key. Uses `workplaceType`. |
| `scrapers/ashby.py` | **(Phase 2)** Ashby ATS boards for `config.ASHBY_COMPANIES`. No key. Uses `isRemote` + address country. |
| `scrapers/jobicy.py` | **(Phase 2)** Jobicy remote API, `geo=usa` across `config.JOBICY_INDUSTRIES`. No key. |
| `scrapers/jobspresso.py` | **(Phase 2)** Jobspresso RSS feed. No key. |
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

## 6b. Phase 2 — Tier 2 boards (added 2026-09-30)

Implemented the CI-safe subset of Tier 2 (plain HTTP only — GitHub Actions has no
headless browser). Probed every candidate live before building.

**Integrated platforms — full list (13 sources):**
- *Phase 1 (remote boards, no key):* Remote OK, Remotive, We Work Remotely, Himalayas, Working Nomads, Hacker News (Who is Hiring)
- *Phase 1 (need free key):* Adzuna, Jooble
- *Phase 2 (ATS boards + aggregators, no key):* **Greenhouse, Lever, Ashby** (first-party company boards, accurate dates + explicit remote flags), **Jobicy** (remote API, native `geo=usa`), **Jobspresso** (RSS)

**Highest-value addition = the ATS boards.** They are first-party, have accurate
`first_published`/`createdAt`/`publishedAt` dates and explicit remote flags, and no
anti-bot. Company slugs live in `config.GREENHOUSE_COMPANIES` / `LEVER_COMPANIES` /
`ASHBY_COMPANIES` — **just add slugs to expand coverage** (unknown slugs skip safely).
YC-style startups largely use these ATSs, so this also covers "YC jobs" indirectly.

**Skipped Tier 2 boards (need a headless browser + anti-bot bypass — not CI-safe):**
startup.jobs (Cloudflare 403), remote.co (Cloudflare), HigherEdJobs (Incapsula),
DailyRemote (no feed), NoDesk (SPA), Wellfound (GraphQL + bot wall), Built In,
SimplyHired, CareerBuilder, Snagajob, YC SPA, Nature/IEEE/ACM (YM/Incapsula).
Revisit only if we add a Playwright-based runner (heavier, more fragile).

**Filter hardening (Phase 2):** ATS boards list on-site roles too, so a
`require_remote=True` path was added (`base.is_remote` + `is_remote` job flag).
Also tightened `is_usa_remote` to reject explicit non-US countries even when
"remote" is present (fixes "Remote Canada" leaking in) via `config.NON_US_COUNTRIES`
+ `base._FOREIGN_RE`. `db.import_csv` now re-applies the role+location filters on
load, so old rows self-heal when filters tighten (time window is NOT re-applied, to
preserve valid history).

**First Phase 2 run:** 24 matched (Greenhouse 12, Jobicy 6, Ashby 2, WWR 2,
Himalayas 1, Lever 1); after the Canada fix + self-heal → **23 clean rows**.
Local run takes ~3–4 min (OpenAI's Ashby board alone is ~13 MB); fine for daily CI.

## 7b. DEPLOYED: hosting & storage (final architecture, 2026-09-30)

User chose **Excel export + free GitHub hosting** over Render. Implemented:

- **Durable store = `data/jobs.csv`** — committed to the repo, so history survives
  ephemeral CI runs; opens directly in Excel; diff-friendly. This is the source of truth.
- **SQLite** (`db/jobs.sqlite`, git-ignored) is rebuilt from the CSV at the start of
  each run and used for clean dedup (UNIQUE url) + querying, then dumped back to CSV.
- **Exports each run:** `dashboard/jobs.csv` + `dashboard/jobs.xlsx` (formatted,
  clickable links, autofilter) — surfaced as download buttons on the dashboard.
- **Automation:** `.github/workflows/daily.yml`
  - Triggers: `cron: "0 13 * * *"` (13:00 UTC = 18:30 IST) + manual `workflow_dispatch`.
  - Steps: checkout → setup Python 3.13 → pip install → `python runner.py`
    (Adzuna/Jooble keys read from repo **Secrets**) → commit `data/jobs.csv` if changed
    → upload `dashboard/` as Pages artifact → deploy to Pages.
  - Uses default `GITHUB_TOKEN` (contents:write, pages:write, id-token:write). Its own
    commit does NOT retrigger the workflow (no loop).
- **Hosting:** GitHub Pages, source = GitHub Actions (enabled via API `build_type=workflow`).
  - **Live URL: https://sahaj-bhadja.github.io/job_boards/**
  - Verified 200: `/`, `/jobs.csv`, `/jobs.xlsx`. First Actions run (id 36653353003) = success.

**To add API keys later (no code change needed):** GitHub repo → Settings → Secrets and
variables → Actions → New repository secret: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`,
`JOOBLE_API_KEY`. Next daily run (or manual `gh workflow run daily.yml`) picks them up.

**Known non-blocking warnings in CI:** Node20 deprecation + ubuntu-latest migration
notices from the actions. Harmless now; bump action versions eventually.

## 8. Render deployment plan (SUPERSEDED — kept for reference only)

> NOTE: We went with GitHub Actions + Pages instead (Section 7b). Render is no longer
> the plan. This section is retained only if a future pivot to Render is wanted.

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
- **Blocker:** Adzuna/Jooble keys (free, user action).

### 2026-09-30 — Session 2 (cont.) — Version control set up
- Confirmed Adzuna = correct API; user needs to register an app at developer.adzuna.com for `app_id`/`app_key` (the pasted page was just the version endpoint; scraper uses the Search endpoint).
- Initialized git, added `.gitignore` (excludes `db/`, `logs/`, `dashboard/index.html`, `__pycache__`, `.env`, `*.sqlite`), `README.md`, `.env.example`.
- Pushed to **https://github.com/SAHAJ-BHADJA/job_boards** (branch `main`, public). First commit `1a5198c`. gh authenticated as SAHAJ-BHADJA (has `repo` + `workflow` scopes).
- Repo is PUBLIC → keys must stay in env vars only (never commit `.env`).
- **Next action:** (1) user gets Adzuna key; (2) build Render deploy files (`render.yaml`, tiny web server, choose persistent-disk vs Postgres) and push.

### 2026-09-30 — Session 2 (cont.) — Excel export + free GitHub hosting (DEPLOYED)
- User asked "can't we just use Excel?" → explained SQLite is already just a file and gives free dedup; agreed to add Excel/CSV export AND switch hosting from Render to **free GitHub Actions + Pages**.
- Added `data/jobs.csv` as durable committed source of truth; SQLite rebuilt from it each run; added `export_csv`/`import_csv`/`export_xlsx` to `db.py`; runner now imports history → scrapes → exports CSV+XLSX → builds dashboard. Added CSV/Excel download buttons.
- Added `.github/workflows/daily.yml` (daily cron + manual), enabled Pages (build_type=workflow).
- Pushed (commit `66d8929`). Triggered workflow run `36653353003` → **build + deploy both succeeded.**
- **Verified LIVE:** https://sahaj-bhadja.github.io/job_boards/ (200), plus `/jobs.csv` and `/jobs.xlsx` (200).
- **Phase 1 is complete and running in the cloud, $0 cost.**
- **Only remaining user action for more volume:** add `ADZUNA_APP_ID`/`ADZUNA_APP_KEY` (+ optional `JOOBLE_API_KEY`) as GitHub repo Actions Secrets. No code change needed.
- **Next possible work:** Phase 2 (Tier 2 boards), dedup across boards, email/alert on new matches.

### 2026-09-30 — Session 3 (model: Opus 4.8) — Phase 2 implemented
- Listed the 8 Phase 1 platforms for the user, then implemented Phase 2.
- Probed all Tier 2 candidates live; built only the CI-safe (plain-HTTP) ones: **Greenhouse, Lever, Ashby** (ATS boards, company lists in `config.py`), **Jobicy** (geo=usa), **Jobspresso** (RSS). Documented the browser-only boards we skipped and why (Section 6b).
- Added `base.is_remote` + `require_remote` for ATS on-site filtering; tightened `is_usa_remote` with `NON_US_COUNTRIES` (fixed "Remote Canada" leak); made `import_csv` self-healing. Added unit tests (all pass).
- First run: 24 matched → **23 clean** after fix (Greenhouse 11, Jobicy 6, Ashby 2, WWR 2, Himalayas 1, Lever 1). Total sources now **13**.
- **Next action:** push, trigger CI, verify live. Then optional: add API keys, expand ATS company slugs, Phase 3 (cross-board dedup, alerts).

<!-- TEMPLATE for next entry:
### YYYY-MM-DD — Session N (model: ...)
- What was done:
- Files added/changed:
- Decisions made:
- Blockers:
- Next action:
-->
