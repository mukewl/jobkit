---
name: find-jobs
description: Run the job search pipeline, then triage the results into the tracker - dedupe against what is already there, tier each role by fit and eligibility, and flag language or work-authorisation risk. Use when asked to find jobs, run a search, refresh the queue, check for new roles, or sort a batch of job listings.
---

# Find and triage jobs

Two halves: the pipeline collects, you judge. The pipeline is deliberately dumb — it filters
on title keywords and location strings only. Everything that needs reading comprehension
happens here.

Read `profile.md` at the repo root first. Work authorisation and language level decide the
tiers, and getting them wrong wastes the user's week.

## Step 1 — Run the pipeline

```bash
python search/fetch_jobs.py
```

It reads `config.json`, runs every configured source for every keyword, drops anything
already in `seen_jobs.csv`, writes today's queue to `data/queue_<date>.json`, and rebuilds
`public/index.html`.

If it exits saying there is no `config.json`, tell the user to copy `config.example.json`
and edit it. If a source errors, the run continues without it and prints a warning — report
that warning rather than hiding it.

**A job appears once, ever.** If the user expected a role and it did not show, it is almost
certainly in `seen_jobs.csv` from a previous run. Check there before concluding the source
is broken.

## Step 2 — Triage

Read `data/queue_<today>.json`. For each role, decide a tier:

- **A** — fits the profile, no eligibility problem, and the user could plausibly get an
  interview. Apply now.
- **B** — a genuine stretch on seniority or function, or an adjacent role. Worth it when
  tier A runs dry.
- **C** — probably blocked by language or another soft requirement. Read the posting before
  writing it off, but do not spend an application on a guess.
- **X** — the user cannot take it. Wrong country for their work authorisation, or a stated
  citizenship or clearance requirement.

Two things the pipeline cannot see and you must add:

**Language risk.** Infer it from the title itself, which is objective and cheap: markers
like `(H/F)`, `(F/H)`, `(M/W/D)`, `CDI`, `CDD` mean the posting was written for a local
market and the role probably runs in that language. Say the evidence, not just the verdict.

**Work authorisation.** Compare the role's country against what `profile.md` allows.
Remote-in-a-region postings usually still need the right to work in a specific country —
treat them as unresolved rather than fine.

Where a job's score and its real value disagree, say so. A low-scoring role at a company
whose domain matches the user's background is worth more than a high-scoring generic one,
and the pipeline has no way to know that.

## Step 3 — Write to the tracker

Append to the `Applications` sheet in `Job_Tracker.xlsx` with openpyxl, preserving existing
rows and any status the user has already filled in. Columns:

`# | Tier | Company | Role | Location | Work auth | Score | Source | Job link | Status |
Date applied | CV file | Notes`

**Dedupe against what is already in the sheet** by company and role before appending, and
report how many were new versus already known. Set `Status` to `Not started`. Colour the
tier cell: A green `C6EFCE`, B amber `FFEB9C`, C peach `FCE4D6`, X grey `E7E6E6`.

Pair each row with its own link before sorting. Sorting a list and zipping it against an
unsorted list of URLs attaches every link to the wrong job — check this explicitly.

If the workbook is open in Excel it will be locked; say so and ask the user to close it.

## Step 4 — Report

Give the tier A roles in full, the notable B ones, and a count for C and X. Call out
anything where you disagree with the pipeline's score and why. Do not paste all twenty rows
into the chat — that is what the tracker is for.
