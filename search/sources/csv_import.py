"""Reference adapter: read jobs from a CSV or JSON file you produced elsewhere.

Zero dependencies, zero terms to breach, and it always works - which makes it the
right thing to ship as the default. Export a list of jobs from whatever board or
tool you already use, point config.json at it, and the rest of the pipeline behaves
exactly as it would with a live source.

config.json:

    "sources": ["csv_import"],
    "csv_import": { "path": "examples/jobs.sample.csv" }

CSV needs a header row. Recognised column names (case-insensitive, flexible):
    title | job_title | position
    company | employer | company_name
    location | city
    url | link | job_url
    posted_at | posted | date

The query argument is used as a filter: only rows whose title contains one of the
query's words survive. Pass an empty query to take everything.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ALIASES = {
    "title": ("title", "job_title", "position", "role"),
    "company": ("company", "employer", "company_name", "organisation", "organization"),
    "location": ("location", "city", "place", "region"),
    "url": ("url", "link", "job_url", "apply_url", "posting"),
    "posted_at": ("posted_at", "posted", "date", "published", "posted_date"),
}


def _pick(row: dict, field: str) -> str:
    lowered = {(k or "").strip().lower(): v for k, v in row.items()}
    for alias in ALIASES[field]:
        if lowered.get(alias):
            return str(lowered[alias]).strip()
    return ""


def _read(path: Path) -> list[dict]:
    if not path.exists():
        # Normal on a fresh install: /find-jobs writes this file after it reads
        # the boards. Absent means "nothing from the browser yet", not an error.
        return []
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("jobs", [])
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def fetch(query: str, config: dict) -> list[dict]:
    settings = config.get("csv_import", {})
    path = Path(settings.get("path", "examples/jobs.sample.csv"))
    if not path.is_absolute():
        path = Path(config["_repo_root"]) / path

    words = [w for w in (query or "").lower().split() if len(w) > 2]
    jobs = []
    for row in _read(path):
        title = _pick(row, "title")
        if not title:
            continue
        if words and not any(w in title.lower() for w in words):
            continue
        jobs.append({
            "title": title,
            "company": _pick(row, "company"),
            "location": _pick(row, "location"),
            "url": _pick(row, "url"),
            "posted_at": _pick(row, "posted_at"),
            "source": "csv_import",
        })
    return jobs
