"""Himalayas - remote jobs, worldwide. No API key, no signup.

    https://himalayas.app/docs/remote-jobs-api

Terms, as published by Himalayas at the time of writing:

  - "No API key or authentication is required."
  - The API is rate limited and returns 429 if you exceed it.
  - Data refreshes every 24 hours, so "there is no benefit to polling more
    frequently than once per day."
  - "If you display Himalayas job data on your own website or application,
    include a visible link back to himalayas.app and mention that the data is
    sourced from Himalayas."

That attribution requirement is why ATTRIBUTION exists below - the dashboard
renders it automatically. Do not remove it. If you fork this and drop the
credit, you are breaking their terms, not ours.

Terms change. Re-read them before you rely on this.

config.json:

    "sources": ["himalayas"],
    "himalayas": { "limit": 100 }
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://himalayas.app/jobs/api"
SEARCH = "https://himalayas.app/jobs/api/search"
UA = "jobkit (+https://github.com/topics/job-search)"

ATTRIBUTION = 'Remote roles via <a href="https://himalayas.app">Himalayas</a>.'


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise RuntimeError(
                "Himalayas rate limit hit (429). Their data only refreshes daily, "
                "so run this once a day rather than repeatedly."
            ) from exc
        raise RuntimeError(f"Himalayas returned HTTP {exc.code}") from exc


def _location(job: dict) -> str:
    restrictions = job.get("locationRestrictions") or []
    if isinstance(restrictions, list) and restrictions:
        return "Remote (" + ", ".join(str(r) for r in restrictions[:3]) + ")"
    return "Remote"


def _posted(job: dict) -> str:
    raw = job.get("pubDate") or ""
    # seen as both an ISO string and an epoch value; handle either
    if isinstance(raw, (int, float)):
        from datetime import datetime, timezone
        seconds = raw / 1000 if raw > 1e11 else raw
        return datetime.fromtimestamp(seconds, timezone.utc).date().isoformat()
    return str(raw)[:10]


def fetch(query: str, config: dict) -> list[dict]:
    settings = config.get("himalayas", {})
    limit = min(int(settings.get("limit", 100)), 100)

    # Search when we have a query - the browse endpoint returns the newest jobs
    # across every category, so filtering it client-side finds almost nothing.
    if query:
        url = f"{SEARCH}?{urllib.parse.urlencode({'q': query, 'limit': limit})}"
    else:
        url = f"{ENDPOINT}?{urllib.parse.urlencode({'limit': limit})}"
    payload = _get(url)

    # No client-side filtering: with a query the search endpoint has already
    # matched, and without one we deliberately want everything recent.
    jobs = []
    for job in payload.get("jobs", []):
        title = (job.get("title") or "").strip()
        if not title:
            continue
        jobs.append({
            "title": title,
            "company": (job.get("companyName") or "").strip(),
            "location": _location(job),
            "url": job.get("applicationLink") or "",
            "posted_at": _posted(job),
            "source": "himalayas",
            "seniority": job.get("seniority") or "",
        })
    return jobs
