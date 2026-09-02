---
name: find-jobs
description: Collect fresh jobs from every configured board and API source, then immediately score and tier them against the user's CV and write them to the tracker. Use when asked to find jobs, run a search, refresh the queue, check for new roles, or see what is out there.
---

# Find jobs

Collect, then filter. **Always both.** A pile of unranked listings is not a result — the
user asked what is worth applying to, so finish the job before reporting.

Read `profile.md` and the user's CV at `cv/master_cv.*` before you start. Work
authorisation and language level decide what survives, and the CV decides what scores well.

---

## Step 1 — Boards the user searches themselves

Read `boards` from `config.json`. For each entry with `"enabled": true`:

1. Open its `search_url` in a browser tool.
2. Read the results list. Prefer an accessibility snapshot or `document.body.innerText`
   over a screenshot — you want text, not pixels.
3. Extract per row: **title, company, location, url, posted date.**
4. Paginate or scroll if the page has more and it is cheap to do so. Stop after two
   consecutive scrolls with nothing new, and never more than five pages.

Write everything you find to `data/browser_jobs.csv` with the header:

```
title,company,location,url,posted_at
```

That file is what `csv_import` reads, so browser results go through exactly the same
dedupe and filtering as everything else rather than around it.

**When a board fails, say so and move on.** Sites break, redirect, or throw a challenge.
One dead board must not take down the run — report it in your summary and carry on.

**Never solve a CAPTCHA and never log in on their behalf.** If a board demands either, stop
on that board, say which one and why, and suggest they either log in themselves in that
browser first or export results to CSV instead.

If `boards` is empty or all disabled, skip this step silently. It is optional.

## Step 2 — API sources

```bash
python search/fetch_jobs.py
```

This runs the sources in `config.json`, folds in `data/browser_jobs.csv` via `csv_import`,
drops anything already in `seen_jobs.csv`, applies the keyword and location filters, writes
`data/queue_<date>.json`, and rebuilds `public/index.html`.

Report any `[warn]` lines rather than hiding them.

## Step 3 — Filter against the CV (never skip this)

Now follow **`.claude/skills/filter-jobs/SKILL.md`** in full. It is the single source of
truth for tiering, and it writes the tracker.

Do not stop at step 2 and hand over a raw queue. The keyword filter in the pipeline is
deliberately crude — it matches title words and location strings and knows nothing about
whether the user can actually take the job or do it well. The filter step is where the
value is.

## Step 4 — Report

Tier A roles in full. Notable B ones. Counts for C and X. Which boards worked and which
failed. Do not paste the whole queue into the chat — that is what the tracker and the
dashboard are for.

Close with the single most useful next action, which is almost always:

```
/apply-to-job <url of the best tier A role>
```
