"""
Adzuna — official REST API (free app_id + app_key required).
Skipped automatically if keys are not set in the environment.
Docs: https://developer.adzuna.com/
"""
from . import base
import config

NAME = "Adzuna"
COUNTRY = "us"  # remote USA
ENDPOINT = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"


def enabled():
    return bool(config.ADZUNA_APP_ID and config.ADZUNA_APP_KEY)


def scrape():
    if not enabled():
        return []
    raw = []
    for label, variants in config.TARGET_MATCHERS:
        what = variants[0]  # primary phrase for this role
        try:
            resp = base.http_get(
                ENDPOINT.format(country=COUNTRY, page=1),
                params={
                    "app_id": config.ADZUNA_APP_ID,
                    "app_key": config.ADZUNA_APP_KEY,
                    "results_per_page": 50,
                    "what_phrase": what,
                    "max_days_old": 1,
                    "content-type": "application/json",
                },
            )
        except Exception:
            continue
        for item in resp.json().get("results", []):
            loc = (item.get("location") or {}).get("display_name") or ""
            raw.append({
                "title": item.get("title") or "",
                "company": (item.get("company") or {}).get("display_name"),
                "location": loc or "United States",
                "url": item.get("redirect_url") or "",
                "posted_dt": base.parse_dt(item.get("created")),
            })
    return base.filter_jobs(NAME, raw)
