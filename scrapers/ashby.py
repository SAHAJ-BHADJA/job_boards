"""
Ashby — public job-board posting API, no key.
https://api.ashbyhq.com/posting-api/job-board/{company}
Has an explicit isRemote flag and a structured address (country).
"""
from . import base
import config

NAME = "Ashby"
API = "https://api.ashbyhq.com/posting-api/job-board/{company}"


def _country(job):
    addr = (job.get("address") or {}).get("postalAddress") or {}
    return addr.get("addressCountry") or ""


def scrape():
    raw = []
    for company in config.ASHBY_COMPANIES:
        try:
            resp = base.http_get(API.format(company=company))
            jobs = resp.json().get("jobs", [])
        except Exception:
            continue
        for j in jobs:
            if j.get("isListed") is False:
                continue
            remote = bool(j.get("isRemote")) or (j.get("workplaceType") or "").lower() == "remote"
            loc = j.get("location") or ""
            country = _country(j)
            raw.append({
                "title": j.get("title") or "",
                "company": company.title(),
                "location": f"{loc} {country}".strip(),
                "url": j.get("jobUrl") or "",
                "posted_dt": base.parse_dt(j.get("publishedAt") or j.get("updatedAt")),
                "is_remote": remote,
            })
    return base.filter_jobs(NAME, raw, require_remote=True)
