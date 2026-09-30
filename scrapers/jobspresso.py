"""Jobspresso — public RSS feed, no key. https://jobspresso.co/remote-work/feed/"""
import feedparser

from . import base

NAME = "Jobspresso"
FEED = "https://jobspresso.co/remote-work/feed/"


def scrape():
    try:
        resp = base.http_get(FEED, headers={"Accept": "application/rss+xml"})
    except Exception:
        return []
    parsed = feedparser.parse(resp.content)
    raw = []
    for e in parsed.entries:
        # Jobspresso is a remote board; location often in categories/summary.
        cats = " ".join(t.get("term", "") for t in e.get("tags", []) if isinstance(t, dict))
        raw.append({
            "title": e.get("title", ""),
            "company": e.get("author", "") or "",
            "location": cats or "Remote",
            "url": e.get("link", ""),
            "posted_dt": base.parse_dt(e.get("published") or e.get("updated")),
        })
    return base.filter_jobs(NAME, raw)
