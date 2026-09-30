"""Working Nomads — public JSON, no key.
https://www.workingnomads.com/api/exposed_jobs/
"""
from . import base

NAME = "Working Nomads"
API = "https://www.workingnomads.com/api/exposed_jobs/"


def scrape():
    resp = base.http_get(API)
    data = resp.json()
    # API returns a list (sometimes wrapped) of job dicts.
    items = data if isinstance(data, list) else data.get("jobs", [])
    raw = []
    for item in items:
        raw.append({
            "title": item.get("title") or "",
            "company": item.get("company_name") or item.get("company"),
            "location": item.get("location") or "",
            "url": item.get("url") or "",
            "posted_dt": base.parse_dt(item.get("pub_date") or item.get("publication_date")),
        })
    return base.filter_jobs(NAME, raw)
