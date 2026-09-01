# Job sources

A source adapter is a Python module in this folder exposing one function:

```python
def fetch(query: str, config: dict) -> list[dict]:
    ...
```

Each dict it returns needs `title`, `company`, `location`, `url`, `posted_at`, `source`.
Missing keys are filled in with `""` by `normalise()`, and any extra keys you add are
passed through to the dashboard untouched.

Register it by adding the module name to `sources` in your `config.json`:

```json
"sources": ["csv_import", "my_board"]
```

A source that throws is reported and skipped — one broken adapter will not take down a run.

## Why only one adapter ships

`csv_import` is the only adapter in this repo, on purpose. It reads a CSV or JSON you
exported from anywhere, so the pipeline works out of the box with no account, no API key,
and nothing that could breach a site's terms.

**Scraping adapters are yours to write and yours to run.** Many job boards — LinkedIn among
them — prohibit automated collection in their terms of service, including of endpoints that
need no login. Whether that matters to you depends on your jurisdiction, your volume, and
your appetite. It is not a decision this repo should make for you by shipping the code
pre-written, so it doesn't.

## Writing your own

Reasonable places to start, in rough order of friendliness:

- **A board's official API**, where one exists. Check the terms first — some allow
  non-commercial use, some require an API key, some forbid it outright.
- **RSS or JSON feeds** that a board publishes deliberately. These exist to be consumed.
- **An export you produce by hand** — search a board in your browser, export or copy the
  results, feed them through `csv_import`. Slow, but unimpeachable.

Whatever you pick, read the terms yourself. Do not take a stranger's README as legal advice,
including this one.

## Being a good citizen

If you do write a scraping adapter, at minimum: identify yourself honestly in the
user-agent, sleep between requests, respect `robots.txt`, cache aggressively so you never
fetch the same page twice, and stop at the first sign you are being rate-limited rather than
working around it.
