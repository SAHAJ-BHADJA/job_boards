"""Remotive — public JSON API, no key. https://remotive.com/api/remote-jobs"""
from . import base

NAME = "Remotive"
API = "https://remotive.com/api/remote-jobs?category=software-dev&limit=500"


def scrape():
    resp = base.http_get(API)
    data = resp.json()
    raw = []
    for item in data.get("jobs", []):
        raw.append({
            "title": item.get("title") or "",
            "company": item.get("company_name"),
            "location": item.get("candidate_required_location") or "",
            "url": item.get("url") or "",
            "posted_dt": base.parse_dt(item.get("publication_date")),
        })
    return base.filter_jobs(NAME, raw)
