"""
Central configuration for Job Bot — Phase 1 (Tier 1 boards, remote-USA only).

Everything tweakable lives here so scrapers/runner stay generic.
Secrets (API keys) are read from environment variables so they never sit in git.
"""
import os

# ---------------------------------------------------------------------------
# Target roles. A job is kept if its title matches ANY matcher below.
# Each matcher: (label, [keyword-variants]). Match = title contains a variant.
# ---------------------------------------------------------------------------
TARGET_MATCHERS = [
    ("Software Engineer", [
        "software engineer", "software developer", "sde", "swe",
        "backend engineer", "full stack engineer", "fullstack engineer",
        "frontend engineer", "software development engineer",
    ]),
    ("Machine Learning Engineer", [
        "machine learning engineer", "ml engineer", "mle",
        "machine learning", "deep learning engineer", "ai engineer",
    ]),
    ("Platform Engineer", [
        "platform engineer", "infrastructure engineer", "devops engineer",
        "site reliability engineer", "sre",
    ]),
    ("New Grad Software Engineer", [
        "new grad", "new graduate", "university graduate", "entry level software",
        "early career software", "graduate software engineer", "campus software",
    ]),
]

# ---------------------------------------------------------------------------
# "Remote USA only" filter.
# A job passes if its location/region text matches a US indicator, OR is a
# worldwide/anywhere posting (those accept US applicants).
# Set INCLUDE_WORLDWIDE = False to keep strictly US-labelled postings only.
# ---------------------------------------------------------------------------
INCLUDE_WORLDWIDE = True

US_INDICATORS = [
    "united states", "usa", "u.s.", "u.s", " us ", "(us)", "us-", "-us",
    "us only", "us-based", "us based", "america", "north america",
]
# Two-letter US state codes (with word boundaries handled in matcher).
US_STATE_CODES = [
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id",
    "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
    "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok",
    "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv",
    "wi", "wy", "dc",
]
WORLDWIDE_INDICATORS = [
    "anywhere", "worldwide", "world wide", "global", "remote", "fully remote",
    "100% remote", "no location", "any location",
]
# Locations that explicitly EXCLUDE the US -> drop even if "remote".
NON_US_ONLY_INDICATORS = [
    "emea only", "europe only", "eu only", "uk only", "canada only",
    "apac only", "latam only", "india only", "australia only",
]

# ---------------------------------------------------------------------------
# Time window. Keep jobs posted within the last N hours.
# ---------------------------------------------------------------------------
WINDOW_HOURS = 24
# If a job has no reliable posting date, keep it anyway (flagged) when True.
INCLUDE_UNDATED = True

# ---------------------------------------------------------------------------
# Optional API keys (Tier 1 boards that need free signup). Left blank = skipped.
# Set them as environment variables before running to enable those scrapers.
# ---------------------------------------------------------------------------
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")
JOOBLE_API_KEY = os.environ.get("JOOBLE_API_KEY", "")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("JOBBOT_DB", os.path.join(BASE_DIR, "db", "jobs.sqlite"))
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
DASHBOARD_HTML = os.path.join(DASHBOARD_DIR, "index.html")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Polite HTTP defaults
HTTP_TIMEOUT = 30
USER_AGENT = "JobBot/1.0 (personal job-aggregator; contact sahajbhadja10@gmail.com)"
