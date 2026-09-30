"""
Hacker News "Ask HN: Who is hiring?" — via the public Algolia API, no key.

Best-effort: HN comments are freeform, so we treat each top-level comment in the
last 24h as one posting, use its first line as the title, and link to the comment.
"""
import html
import re
from datetime import datetime, timezone, timedelta

from . import base

NAME = "Hacker News (Who is Hiring)"
SEARCH = "http://hn.algolia.com/api/v1/search_by_date"

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text):
    text = _TAG_RE.sub(" ", text or "")
    return html.unescape(text).strip()


def _find_latest_thread():
    resp = base.http_get(
        SEARCH,
        params={"query": "Ask HN: Who is hiring?", "tags": "story", "hitsPerPage": 10},
    )
    for hit in resp.json().get("hits", []):
        title = (hit.get("title") or "").lower()
        if "who is hiring" in title:
            return hit.get("objectID")
    return None


def scrape():
    thread_id = _find_latest_thread()
    if not thread_id:
        return []
    cutoff = int((datetime.now(timezone.utc) - timedelta(hours=base.config.WINDOW_HOURS)).timestamp())
    resp = base.http_get(
        SEARCH,
        params={
            "tags": f"comment,story_{thread_id}",
            "numericFilters": f"created_at_i>={cutoff}",
            "hitsPerPage": 1000,
        },
    )
    raw = []
    for hit in resp.json().get("hits", []):
        text = _strip_html(hit.get("comment_text", ""))
        if not text:
            continue
        first_line = text.split("\n")[0][:200]
        # HN "who is hiring" first lines usually read "Company | Role | LOCATION | REMOTE"
        raw.append({
            "title": first_line,
            "company": (first_line.split("|")[0].strip() if "|" in first_line else ""),
            "location": first_line,  # location filter scans the whole first line
            "url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            "posted_dt": base.parse_dt(hit.get("created_at_i")),
        })
    return base.filter_jobs(NAME, raw)
