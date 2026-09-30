"""
Greenhouse — public job-board API, no key.
https://boards-api.greenhouse.io/v1/boards/{company}/jobs
Iterates a configured company list; on-site roles filtered out (require_remote).
"""
from . import base
import config

NAME = "Greenhouse"
API = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"


def scrape():
    raw = []
    for company in config.GREENHOUSE_COMPANIES:
        try:
            resp = base.http_get(API.format(company=company))
            jobs = resp.json().get("jobs", [])
        except Exception:
            continue  # unknown slug / transient error -> skip this company
        for j in jobs:
            loc = (j.get("location") or {}).get("name") or ""
            raw.append({
                "title": j.get("title") or "",
                "company": j.get("company_name") or company.title(),
                "location": loc,
                "url": j.get("absolute_url") or "",
                # first_published is the real posting date; fall back to updated_at.
                "posted_dt": base.parse_dt(j.get("first_published") or j.get("updated_at")),
            })
    return base.filter_jobs(NAME, raw, require_remote=True)
