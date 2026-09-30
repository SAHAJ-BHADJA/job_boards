"""
Jooble — official API (free key required, POST). Skipped if no key set.
Docs: https://jooble.org/api/about
"""
from . import base
import config

NAME = "Jooble"
ENDPOINT = "https://jooble.org/api/{key}"


def enabled():
    return bool(config.JOOBLE_API_KEY)


def scrape():
    if not enabled():
        return []
    raw = []
    for label, variants in config.TARGET_MATCHERS:
        keywords = variants[0]
        try:
            resp = base.http_post(
                ENDPOINT.format(key=config.JOOBLE_API_KEY),
                json={"keywords": keywords, "location": "USA"},
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
        except Exception:
            continue
        for item in resp.json().get("jobs", []):
            raw.append({
                "title": item.get("title") or "",
                "company": item.get("company"),
                "location": item.get("location") or "USA",
                "url": item.get("link") or "",
                "posted_dt": base.parse_dt(item.get("updated")),
            })
    return base.filter_jobs(NAME, raw)
