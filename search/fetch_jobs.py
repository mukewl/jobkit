"""Build a deduplicated queue of fresh jobs from one or more source adapters.

    python search/fetch_jobs.py

Reads config.json at the repo root, runs every configured source for every keyword,
drops anything already seen or off-target, writes today's queue to data/, and
regenerates the dashboard at public/index.html.

A job appears once, ever. seen_jobs.csv is the permanent record - delete it only if
you want the whole history back.

No login, no tokens, no LLM.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.insert(0, str(BASE))

import sources  # noqa: E402  (needs the path insert above)
from render_dashboard import render  # noqa: E402

CONFIG_PATH = ROOT / "config.json"
SEEN_CSV = ROOT / "seen_jobs.csv"
DATA_DIR = ROOT / "data"
DASHBOARD = ROOT / "public" / "index.html"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            "No config.json found.\n"
            "  cp config.example.json config.json   then edit it."
        )
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg["_repo_root"] = str(ROOT)
    return cfg


def tz(config: dict) -> ZoneInfo:
    return ZoneInfo(config.get("timezone", "UTC"))


# ---------------------------------------------------------------- dedupe

def load_seen() -> set[str]:
    seen = set()
    if SEEN_CSV.exists():
        with SEEN_CSV.open(newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if row:
                    seen.add(row[0])
    return seen


def append_seen(rows: list[dict]) -> None:
    new_file = not SEEN_CSV.exists()
    with SEEN_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["job_key", "first_seen", "title", "company"])
        for r in rows:
            # neutralise spreadsheet formula injection on export
            safe = [v if not (v and v[0] in "=+-@") else "'" + v
                    for v in (r["title"], r["company"])]
            w.writerow([r["key"], r["fetched"], safe[0], safe[1]])


def job_key(job: dict) -> str:
    """Stable identity for a posting, across sources.

    Prefer the numeric id most boards put in their URL; fall back to the whole
    URL; fall back again to title+company for sources with no link at all.
    """
    url = job.get("url") or ""
    src = job.get("source") or "x"
    m = re.search(r"(\d{7,})", url)
    if m:
        return f"{src}-{m.group(1)}"
    if url:
        return f"{src}-" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    blob = (job.get("title", "") + job.get("company", "")).lower()
    return f"{src}-" + re.sub(r"\W+", "", blob)[:60]


# ---------------------------------------------------------------- filtering

def keep_job(job: dict, config: dict) -> bool:
    """Relevance gate. Deliberately blunt and title-only: a job whose *title*
    carries no signal is noise however good the description reads."""
    title_l = (job.get("title") or "").lower()
    scoring = config.get("scoring", {})

    if any(w in title_l for w in scoring.get("reject_any", [])):
        return False

    must = scoring.get("must_have_any", [])
    if must and not any(w in title_l for w in must):
        return False

    loc_filter = config.get("location_filter") or []
    if loc_filter:
        loc_l = (job.get("location") or "").lower()
        if not any(m in loc_l for m in loc_filter):
            return False

    return True


# ---------------------------------------------------------------- queue

def build_queue(config: dict):
    seen = load_seen()
    today = datetime.now(tz(config)).date().isoformat()
    DATA_DIR.mkdir(exist_ok=True)
    day_file = DATA_DIR / f"queue_{today}.json"

    earlier_today = []
    if day_file.exists():
        earlier_today = json.loads(day_file.read_text(encoding="utf-8"))
        kept = [j for j in earlier_today if keep_job(j, config)]
        dropped = len(earlier_today) - len(kept)
        if dropped:
            print(f"retro-filter: dropped {dropped} now off-target jobs from today's queue")
        earlier_today = kept

    fresh, new_keys, raw_count = [], set(), 0
    for kw in config["keywords"]:
        print(f"fetching: {kw['query']}")
        batch = sources.fetch_all(kw["query"], config)
        raw_count += len(batch)
        for j in batch:
            key = job_key(j)
            if key in seen or key in new_keys or not keep_job(j, config):
                continue
            new_keys.add(key)
            j.update({"key": key, "family": kw.get("family", ""), "fetched": today})
            fresh.append(j)

    day_queue = earlier_today + fresh          # same-day re-runs add to the day
    day_file.write_text(json.dumps(day_queue, indent=1, ensure_ascii=False),
                        encoding="utf-8")
    print(f"raw {raw_count} | new this run {len(fresh)} | in today's queue {len(day_queue)}")
    return day_queue, fresh


def load_recent_days(config: dict, days: int = 7) -> list[dict]:
    """Every job from the last N daily files, newest first, deduped and
    re-filtered so a rule change cleans up old days too."""
    today = datetime.now(tz(config)).date()
    out, seen_keys = [], set()
    for f in sorted(DATA_DIR.glob("queue_*.json"), reverse=True):
        try:
            d = datetime.strptime(f.stem.replace("queue_", ""), "%Y-%m-%d").date()
        except ValueError:
            continue
        if (today - d).days >= days:
            continue
        for j in json.loads(f.read_text(encoding="utf-8")):
            if j.get("key") in seen_keys or not keep_job(j, config):
                continue
            seen_keys.add(j["key"])
            out.append(j)
    return out


def main() -> int:
    config = load_config()
    _, fresh = build_queue(config)
    if fresh:
        append_seen(fresh)

    recent = load_recent_days(config, days=config.get("dashboard_days", 7))
    DASHBOARD.parent.mkdir(exist_ok=True)
    DASHBOARD.write_text(render(recent, config), encoding="utf-8")
    print(f"dashboard: {DASHBOARD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
