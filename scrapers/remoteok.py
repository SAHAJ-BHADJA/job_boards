"""Remote OK — public JSON API, no key. https://remoteok.com/api"""
from . import base

NAME = "Remote OK"
API = "https://remoteok.com/api"


def scrape():
    resp = base.http_get(API, headers={"Accept": "application/json"})
    data = resp.json()
    raw = []
    for item in data:
        # First element is a legal/notice object without "position".
        if not isinstance(item, dict) or "position" not in item:
            continue
        location = item.get("location") or ""
        # RemoteOK jobs are all remote; location often blank or a region tag.
        raw.append({
            "title": item.get("position") or item.get("title") or "",
            "company": item.get("company"),
            "location": location or "Remote",
            "url": item.get("url") or item.get("apply_url") or "",
            "posted_dt": base.parse_dt(item.get("date") or item.get("epoch")),
        })
    return base.filter_jobs(NAME, raw)
