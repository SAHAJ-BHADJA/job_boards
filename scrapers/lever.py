"""
Lever — public postings API, no key.
https://api.lever.co/v0/postings/{company}?mode=json
Uses workplaceType/location to keep only remote roles.
"""
from . import base
import config

NAME = "Lever"
API = "https://api.lever.co/v0/postings/{company}?mode=json"


def scrape():
    raw = []
    for company in config.LEVER_COMPANIES:
        try:
            resp = base.http_get(API.format(company=company))
            jobs = resp.json()
        except Exception:
            continue
        if not isinstance(jobs, list):
            continue
        for j in jobs:
            cats = j.get("categories") or {}
            loc = cats.get("location") or ""
            workplace = (j.get("workplaceType") or "").lower()
            country = j.get("country") or ""
            raw.append({
                "title": j.get("text") or "",
                "company": company.title(),
                "location": f"{loc} {country}".strip(),
                "url": j.get("hostedUrl") or "",
                "posted_dt": base.parse_dt(j.get("createdAt")),
                "is_remote": workplace == "remote" or base.is_remote(loc),
            })
    return base.filter_jobs(NAME, raw, require_remote=True)
