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
# Words that indicate a role is actually remote (used by ATS scrapers that also
# list on-site jobs — we require one of these so on-site roles are dropped).
REMOTE_INDICATORS = [
    "remote", "anywhere", "distributed", "work from home", "wfh",
    "home based", "home-based", "virtual",
]
# Locations that explicitly EXCLUDE the US -> drop even if "remote".
NON_US_ONLY_INDICATORS = [
    "emea only", "europe only", "eu only", "uk only", "canada only",
    "apac only", "latam only", "india only", "australia only",
]
# Specific non-US countries/regions. If one of these appears in the location and
# there's NO US indicator, the job is dropped (e.g. "Remote Canada", "Remote - UK").
# Matched with word boundaries (see base.is_usa_remote). "georgia" omitted on
# purpose (US state vs country ambiguity).
NON_US_COUNTRIES = [
    "canada", "united kingdom", "uk", "ireland", "germany", "france", "spain",
    "italy", "netherlands", "poland", "portugal", "romania", "sweden", "norway",
    "denmark", "finland", "switzerland", "austria", "belgium", "czech",
    "hungary", "greece", "ukraine", "india", "pakistan", "bangladesh",
    "philippines", "indonesia", "vietnam", "thailand", "malaysia", "singapore",
    "japan", "china", "hong kong", "taiwan", "south korea", "australia",
    "new zealand", "brazil", "mexico", "argentina", "chile", "colombia", "peru",
    "nigeria", "kenya", "ghana", "south africa", "egypt", "morocco", "uae",
    "dubai", "israel", "turkey", "saudi", "qatar", "emea", "apac", "latam",
    "europe", "asia", "africa",
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
# Phase 2 — ATS company boards (public JSON, no key). Each slug = one HTTP call.
# Unknown/invalid slugs simply return nothing and are skipped. Add your own
# target companies here. (These are first-party boards with accurate dates and
# explicit remote flags — the highest-quality Software/ML/Platform source.)
# ---------------------------------------------------------------------------
GREENHOUSE_COMPANIES = [
    "airbnb", "stripe", "coinbase", "gitlab", "databricks", "robinhood",
    "dropbox", "doordash", "instacart", "brex", "figma", "notion", "samsara",
    "reddit", "pinterest", "lyft", "asana", "gusto", "benchling", "affirm",
    "cloudflare", "twitch", "plaid", "discord", "snowflakecomputing", "datadog",
    "mongodb", "hashicorp", "elastic", "confluent", "scaleai", "rippling",
    "cruise", "wealthfront", "chime", "sofi", "flexport", "checkr", "gemini",
]
LEVER_COMPANIES = [
    "spotify", "ycombinator", "kraken", "mercury", "deel", "revolut",
    "netlify", "voleon",
]
ASHBY_COMPANIES = [
    "ramp", "openai", "linear", "vercel", "replicate", "mistral", "anysphere",
    "perplexity", "cohere", "elevenlabs", "runwayml", "character", "suno",
    "hebbia", "sierra", "clay",
]

# Jobicy remote-job API (public, no key). We fix geo=usa and sweep a few industries.
JOBICY_GEO = "usa"
JOBICY_INDUSTRIES = ["engineering", "dev", "data-science"]
JOBICY_COUNT = 50

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ephemeral working DB (rebuilt from CSV each run; git-ignored).
DB_PATH = os.environ.get("JOBBOT_DB", os.path.join(BASE_DIR, "db", "jobs.sqlite"))

# Durable, committed source of truth (survives CI runs, opens in Excel).
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.environ.get("JOBBOT_CSV", os.path.join(DATA_DIR, "jobs.csv"))

# Dashboard output (deployed to GitHub Pages; git-ignored, regenerated).
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
DASHBOARD_HTML = os.path.join(DASHBOARD_DIR, "index.html")
DASHBOARD_CSV = os.path.join(DASHBOARD_DIR, "jobs.csv")
DASHBOARD_XLSX = os.path.join(DASHBOARD_DIR, "jobs.xlsx")

LOG_DIR = os.path.join(BASE_DIR, "logs")

# Polite HTTP defaults
HTTP_TIMEOUT = 30
USER_AGENT = "JobBot/1.0 (personal job-aggregator; contact sahajbhadja10@gmail.com)"
