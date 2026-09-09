# Contributing

The most useful thing you can add is a job source for your own country. Everything else is
secondary.

## Adding a job source

Job boards vary enormously by country, and the two shipped adapters cover remote-worldwide
and Europe. Almost everywhere else is a gap.

An adapter is one module in `search/sources/` exposing one function:

```python
def fetch(query: str, config: dict) -> list[dict]:
    ...
```

Each row it returns needs six keys:

```
title      str   job title as posted
company    str   employer name
location   str   free text, e.g. "Paris, France" or "Remote"
url        str   link to the posting ("" if none)
posted_at  str   ISO date "YYYY-MM-DD" ("" if unknown)
source     str   the adapter's own name
```

Missing keys are filled with `""` by `normalise()`, and extra keys pass through to the
dashboard untouched. A row with no `title` is dropped. An adapter that raises is reported and
skipped rather than taking the run down, so failures are survivable but silent - print
something on the way out if you want to be found.

Read `search/sources/__init__.py` for the contract and `search/sources/himalayas.py` for a
short, real implementation. Users enable it by adding the module name to `sources` in their
`config.json`.

Test it on its own before wiring anything up:

```bash
python -c "import sys; sys.path.insert(0,'search'); from sources import load, normalise; \
rows = normalise(load('yoursource').fetch('marketing', {}), 'yoursource'); \
print(len(rows)); print(rows[0] if rows else 'EMPTY')"
```

### The one rule for adapters

**Documented public APIs only.** An adapter that scrapes HTML from a site whose terms forbid
automated access will not be merged, however well it works and however easy it was. The
repo's position on this is in `search/sources/README.md` and it is not up for negotiation in
a pull request - people run this against their real accounts and their real job search.

If a board publishes an API or a feed, link its documentation in the PR. If it requires
attribution, set `ATTRIBUTION` on your module and the dashboard renders it.

## The CV rule

`cv/build.py` exits non-zero when the PDF runs past one page. That check is the point of the
file.

Do not weaken it. Raising `--max-pages`, shrinking the font, or narrowing the margins to make
a CV fit is not a fix - it is how a two-page CV reaches an employer. If a CV overflows, the
answer is to cut content. A PR that makes the overflow easier to ignore gets closed.

## Never commit personal data

This repo is designed so that the files holding your CV, your contacts and your search
history are gitignored. Test with the sample data instead:

- `examples/jobs.sample.csv` for the search pipeline
- `cv/templates/master_cv.tex` and `.html` for the CV path - **fill in a copy**, never the
  template itself. Those files are tracked.

Before you push:

```bash
git status --short
git ls-files
```

If your CV, your tracker or your `config.json` appears, stop.

## Skills are code

The files in `.claude/` are prompts, and a prompt change changes what the tool does on
someone's real job application. Treat them like code: say what you changed, why, and what you
ran to see it behave differently. "Tidied up the wording" is not a description of a
behavioural change.

Several rules in there were learned expensively - the master CV being read-only, inventing
nothing, checking blockers before doing work, never touching LinkedIn. If a change softens
one of those, say so explicitly in the PR rather than letting it through as an edit.

## Bug reports

Include:

- OS and Python version
- Which CV engine, LaTeX or Playwright
- The exact command you ran and its full output
- Which job source, if it is a search problem
- Whether the job was already in `seen_jobs.csv` - a job is shown once, ever, so "it found
  nothing" is often that

Redact your own details before pasting output. Nobody needs your phone number to reproduce a
LaTeX error.
