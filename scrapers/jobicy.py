"""
Jobicy — public remote-jobs API, no key.
https://jobicy.com/api/v2/remote-jobs?geo=usa&industry=...&count=...
All results are remote; geo=usa restricts to USA-eligible roles.
"""
import html

from . import base
import config

NAME = "Jobicy"
API = "https://jobicy.com/api/v2/remote-jobs"


def scrape():
    raw = []
    seen = set()
    for industry in config.JOBICY_INDUSTRIES:
        try:
            resp = base.http_get(API, params={
                "count": config.JOBICY_COUNT,
                "geo": config.JOBICY_GEO,
                "industry": industry,
            })
            jobs = resp.json().get("jobs", [])
        except Exception:
            continue
        for j in jobs:
            url = j.get("url") or ""
            if url in seen:
                continue
            seen.add(url)
            raw.append({
                "title": html.unescape(j.get("jobTitle") or ""),
                "company": html.unescape(j.get("companyName") or ""),
                "location": j.get("jobGeo") or "USA",
                "url": url,
                "posted_dt": base.parse_dt(j.get("pubDate")),
            })
    # Jobicy jobs are inherently remote -> no require_remote needed.
    return base.filter_jobs(NAME, raw)
