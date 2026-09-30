"""
We Work Remotely — public RSS feeds, no key.
Titles are usually "Company: Role"; region sometimes appears in the title.
"""
import feedparser

from . import base

NAME = "We Work Remotely"
FEEDS = [
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
]


def _split_company_title(raw_title):
    if ":" in raw_title:
        company, title = raw_title.split(":", 1)
        return company.strip(), title.strip()
    return "", raw_title.strip()


def scrape():
    raw = []
    for feed_url in FEEDS:
        try:
            resp = base.http_get(feed_url, headers={"Accept": "application/rss+xml"})
        except Exception:
            continue
        parsed = feedparser.parse(resp.content)
        for e in parsed.entries:
            company, title = _split_company_title(e.get("title", ""))
            region = e.get("region", "") or ""
            summary = e.get("summary", "") or ""
            location = region or summary
            raw.append({
                "title": title,
                "company": company,
                "location": location,
                "url": e.get("link", ""),
                "posted_dt": base.parse_dt(e.get("published") or e.get("updated")),
            })
    return base.filter_jobs(NAME, raw)
