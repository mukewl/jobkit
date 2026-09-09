"""Job source adapters.

A source is any module in this package that exposes:

    fetch(query: str, config: dict) -> list[dict]

Each returned dict must have these keys:

    title      str   job title as posted
    company    str   employer name
    location   str   free text, e.g. "Paris, France" or "Remote"
    url        str   link to the posting ("" if none)
    posted_at  str   ISO date "YYYY-MM-DD" ("" if unknown)
    source     str   the adapter's own name

Anything else you add is passed through untouched and shows up in the dashboard.

This repo ships three adapters, all of which need no account and no API key:
`himalayas`, `arbeitnow` and `csv_import`. Adapters that scrape sites whose terms
forbid it are yours to write and yours to run - see README.md in this folder.
"""
from __future__ import annotations

import importlib

REQUIRED_KEYS = ("title", "company", "location", "url", "posted_at", "source")


class SourceError(RuntimeError):
    pass


def load(name: str):
    """Import an adapter by name from this package."""
    try:
        return importlib.import_module(f"{__name__}.{name}")
    except ModuleNotFoundError as exc:
        raise SourceError(
            f"No job source named '{name}'. Add {name}.py to search/sources/, "
            f"or remove it from \"sources\" in your config.json."
        ) from exc


def normalise(rows, source_name: str) -> list[dict]:
    """Fill in missing keys and stamp the source, so a sloppy adapter can't
    break the pipeline downstream."""
    out = []
    for r in rows or []:
        job = {k: (r.get(k) or "") for k in REQUIRED_KEYS}
        job["source"] = source_name
        if not job["title"]:
            continue
        for k, v in r.items():
            job.setdefault(k, v)
        out.append(job)
    return out


def attributions(names) -> list[str]:
    """Credit lines required by the adapters in use.

    Some sources (Himalayas, for one) require visible attribution as a condition
    of their free API. The dashboard renders whatever this returns. Honour it.
    """
    out = []
    for name in sorted(set(names)):
        try:
            text = getattr(load(name), "ATTRIBUTION", "")
        except SourceError:
            continue
        if text:
            out.append(text)
    return out


def fetch_all(query: str, config: dict) -> list[dict]:
    """Run every configured source for one query and concatenate the results.
    A source that raises is reported and skipped - one bad adapter should not
    take the whole run down."""
    jobs = []
    for name in config.get("sources", ["csv_import"]):
        try:
            mod = load(name)
            jobs.extend(normalise(mod.fetch(query, config), name))
        except Exception as exc:
            print(f"  [warn] source '{name}' failed on '{query}': {exc}")
    return jobs
