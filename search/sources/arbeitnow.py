"""Arbeitnow - jobs across Europe and the UK, pulled from company ATS feeds.
No API key, no signup.

    https://www.arbeitnow.com/blog/job-board-api
    Postman docs: https://documenter.getpostman.com/view/18545278/UVJbJdKh

Two endpoints:

    Europe  https://www.arbeitnow.com/api/job-board-api
    UK      https://www.arbeitnow.co.uk/api/job-board-api

Their docs state the API "requires no API key" and publish no rate limit or
attribution requirement. They do sell private tailored endpoints, which is a fair
signal that the free one is meant to be used - but be a good citizen anyway: this
adapter pages politely and stops early.

The reason this one is worth having if you are job-hunting internationally: it
carries a `visa_sponsorship` flag, which almost no free source does.

Terms change. Re-read them before you rely on this.

config.json:

    "sources": ["arbeitnow"],
    "arbeitnow": {
      "region": "eu",              // "eu" or "uk"
      "pages": 2,                  // 100 jobs per page
      "visa_sponsorship_only": false
    }
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ENDPOINTS = {
    "eu": "https://www.arbeitnow.com/api/job-board-api",
    "uk": "https://www.arbeitnow.co.uk/api/job-board-api",
}
UA = "jobkit (+https://github.com/topics/job-search)"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Arbeitnow returned HTTP {exc.code}") from exc


def _posted(job: dict) -> str:
    raw = job.get("created_at")
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(raw, timezone.utc).date().isoformat()
    return str(raw or "")[:10]


def fetch(query: str, config: dict) -> list[dict]:
    settings = config.get("arbeitnow", {})
    region = str(settings.get("region", "eu")).lower()
    endpoint = ENDPOINTS.get(region)
    if endpoint is None:
        raise RuntimeError(f"arbeitnow: region must be 'eu' or 'uk', got {region!r}")

    pages = max(1, int(settings.get("pages", 2)))
    visa_only = bool(settings.get("visa_sponsorship_only", False))
    words = [w for w in (query or "").lower().split() if len(w) > 2]

    jobs, seen_slugs = [], set()
    for page in range(1, pages + 1):
        params = {"page": page}
        if visa_only:
            params["visa_sponsorship"] = "true"
        payload = _get(f"{endpoint}?{urllib.parse.urlencode(params)}")

        rows = payload.get("data") or []
        if not rows:
            break

        for job in rows:
            slug = job.get("slug") or job.get("url") or ""
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            title = (job.get("title") or "").strip()
            if not title:
                continue
            if words and not any(w in title.lower() for w in words):
                continue

            location = (job.get("location") or "").strip()
            if job.get("remote") and "remote" not in location.lower():
                location = f"{location} (remote)" if location else "Remote"

            jobs.append({
                "title": title,
                "company": (job.get("company_name") or "").strip(),
                "location": location,
                "url": job.get("url") or "",
                "posted_at": _posted(job),
                "source": "arbeitnow",
                "tags": ", ".join(job.get("tags") or [])[:120],
            })

        if page < pages:
            time.sleep(1.0)          # be a good citizen

    return jobs
