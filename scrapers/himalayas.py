"""Himalayas — public JSON API, no key. https://himalayas.app/jobs/api"""
from . import base

NAME = "Himalayas"
API = "https://himalayas.app/jobs/api?limit=500"


def scrape():
    resp = base.http_get(API)
    data = resp.json()
    raw = []
    for item in data.get("jobs", []):
        # locationRestrictions is a list of regions/countries the job accepts.
        restrictions = item.get("locationRestrictions") or []
        if isinstance(restrictions, list):
            location = ", ".join(str(x) for x in restrictions)
        else:
            location = str(restrictions)
        raw.append({
            "title": item.get("title") or "",
            "company": item.get("companyName") or item.get("company"),
            "location": location or "Remote",
            "url": item.get("applicationLink") or item.get("guid") or item.get("url") or "",
            "posted_dt": base.parse_dt(item.get("pubDate") or item.get("publishedDate")),
        })
    return base.filter_jobs(NAME, raw)
