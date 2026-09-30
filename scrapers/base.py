"""
Shared helpers for all scrapers: HTTP, role-title matching, USA-remote filter,
24h window filter, and date parsing.

Each scraper module exposes:  fetch() -> list[dict]   with raw-ish records, then
calls filter_jobs() to apply the role/location/time rules uniformly.
"""
import re
import time
from datetime import datetime, timezone, timedelta

import requests

import config

_session = requests.Session()
_session.headers.update({"User-Agent": config.USER_AGENT, "Accept": "application/json"})


def http_get(url, **kwargs):
    kwargs.setdefault("timeout", config.HTTP_TIMEOUT)
    last_err = None
    for attempt in range(3):
        try:
            resp = _session.get(url, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:  # noqa: BLE001 — polite retry on any transient error
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise last_err


def http_post(url, **kwargs):
    kwargs.setdefault("timeout", config.HTTP_TIMEOUT)
    return _session.post(url, **kwargs)


# --------------------------------------------------------------------------- #
# Role-title matching
# --------------------------------------------------------------------------- #
def match_role(title):
    """Return the matched role label, or None if the title matches no target."""
    if not title:
        return None
    t = title.lower()
    for label, variants in config.TARGET_MATCHERS:
        for v in variants:
            if v in t:
                return label
    return None


# --------------------------------------------------------------------------- #
# USA-remote location filter
# --------------------------------------------------------------------------- #
_STATE_RE = re.compile(
    r"\b(" + "|".join(config.US_STATE_CODES) + r")\b", re.IGNORECASE
)
_FOREIGN_RE = re.compile(
    r"\b(" + "|".join(re.escape(c) for c in config.NON_US_COUNTRIES) + r")\b",
    re.IGNORECASE,
)


def is_remote(text):
    """True if the text signals a remote role (for ATS boards mixing on-site jobs)."""
    t = (text or "").lower()
    return any(w in t for w in config.REMOTE_INDICATORS)


def is_usa_remote(location_text):
    """True if the location indicates US eligibility (or generic worldwide).

    A location that names a specific non-US country and gives no US signal is
    rejected even when it says "remote" (e.g. "Remote Canada")."""
    loc = (location_text or "").lower()

    # Hard exclusions first (region-locked, non-US).
    for bad in config.NON_US_ONLY_INDICATORS:
        if bad in loc:
            return False

    # Explicit US signals win immediately.
    for good in config.US_INDICATORS:
        if good in loc:
            return True
    # State codes like "NY", "CA" (only trust when the string is short/locationy).
    if len(loc) <= 40 and _STATE_RE.search(loc):
        return True

    # A specific foreign country with no US signal => not USA.
    if _FOREIGN_RE.search(loc):
        return False

    if config.INCLUDE_WORLDWIDE:
        for w in config.WORLDWIDE_INDICATORS:
            if w in loc:
                return True
        # Empty location on a remote board => treat as worldwide.
        if not loc.strip():
            return True

    return False


# --------------------------------------------------------------------------- #
# Date / time-window handling
# --------------------------------------------------------------------------- #
def parse_dt(value):
    """Best-effort parse of many date formats -> aware UTC datetime, or None."""
    if value is None or value == "":
        return None
    # Epoch seconds (int/float/str of digits)
    try:
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
            ts = float(value)
            if ts > 1e11:  # milliseconds
                ts /= 1000.0
            return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (ValueError, OSError):
        pass

    if isinstance(value, str):
        v = value.strip().replace("Z", "+00:00")
        # Try ISO first
        try:
            dt = datetime.fromisoformat(v)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        # Common RFC-822 / feed formats
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(value.strip(), fmt)
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def within_window(dt):
    """True if dt is within the configured window; None dt handled by caller."""
    if dt is None:
        return None
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.WINDOW_HOURS)
    return dt >= cutoff


def to_iso(dt):
    return dt.isoformat() if dt else None


# --------------------------------------------------------------------------- #
# Unified filter: apply role + location + time to raw records.
# raw record dict must have: title, company, location, url, posted_dt (datetime|None)
# --------------------------------------------------------------------------- #
def filter_jobs(platform, raw_records, require_remote=False):
    out = []
    for r in raw_records:
        role = match_role(r.get("title"))
        if not role:
            continue
        # ATS boards list on-site roles too; require an explicit remote signal.
        if require_remote and not (
            r.get("is_remote") or is_remote(r.get("location")) or is_remote(r.get("title"))
        ):
            continue
        if not is_usa_remote(r.get("location")):
            continue
        w = within_window(r.get("posted_dt"))
        if w is False:
            continue
        if w is None and not config.INCLUDE_UNDATED:
            continue
        out.append({
            "title": r["title"].strip(),
            "company": r.get("company"),
            "location": r.get("location"),
            "url": r["url"],
            "platform": platform,
            "search_term": role,
            "posted_at": to_iso(r.get("posted_dt")),
        })
    return out
