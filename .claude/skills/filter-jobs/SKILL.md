---
name: filter-jobs
description: Score and tier the current job queue against the user's CV and profile, flag language and work-authorisation risk, and write the results to the tracker. Runs automatically at the end of find-jobs; use it on its own to re-tier an existing queue after changing the CV, the profile, or the filter rules.
---

# Filter jobs against this CV

The pipeline matched title words and location strings. That is all it can do. Everything
that needs reading comprehension happens here.

`find-jobs` calls this automatically — you rarely need to run it by hand. Do run it on its
own after the user edits their CV, changes `profile.md`, or wants a queue re-judged under
new rules.

## Read first

- **`profile.md`** — work authorisation and language level. These decide eligibility, and
  getting them wrong costs the user a week.
- **`cv/master_cv.tex`** or **`.html`** — their actual experience. You are scoring against
  this, not against a job family label.
- **`data/queue_<today>.json`** — the roles to judge. If today's file is missing, take the
  most recent.
- **`Job_Tracker.xlsx`** — what is already there, so you do not add it twice.

## Tier each role

**A — apply now.** Fits their experience, no eligibility problem, and they could plausibly
get an interview. Be selective. If everything is tier A, the tier means nothing.

**B — a real stretch.** Above their seniority, an adjacent function, or a domain they would
have to argue for. Worth it when A runs dry.

**C — probably blocked, check first.** A language bar, an on-site requirement they cannot
meet, a clearance. Do not spend an application on a guess — but do not silently bin it
either, because the guess is sometimes wrong.

**X — they cannot take it.** Wrong country for their work authorisation, or a stated
citizenship requirement. Say which.

### Two things the pipeline cannot see

**Language risk.** Infer it from the posting title, which is objective and free: markers
like `(H/F)`, `(F/H)`, `(M/W/D)`, `CDI`, `CDD` mean it was written for a local market and
the role probably runs in that language. Record the evidence, not just the verdict — "F/H
in the title" is checkable, "seems French" is not.

**Work authorisation.** Compare the role's country against what `profile.md` allows. A
"remote — Europe" posting still usually needs the right to work in one specific country;
treat that as unresolved rather than fine.

### Where you disagree with the score, say so

A low-scoring role at a company whose domain matches the user's background is often worth
more than a high-scoring generic one. The pipeline has no way to know that a hospitality
degree makes a hotel-software company interesting. You do. Put it in the notes and raise it
in your summary.

Equally: a role that scores well but sits three levels above them is a B at best. Score is
an input, not a verdict.

## Write the tracker

Append to the `Applications` sheet in `Job_Tracker.xlsx` with openpyxl. **Preserve existing
rows and any Status the user has already filled in** — never rewrite the sheet wholesale.

`# | Tier | Company | Role | Location | Work auth | Score | Source | Job link | Status |
Date applied | CV file | Notes`

- Dedupe against what is already there by company and role before appending, and report how
  many were new versus already known
- `Status` starts at `Not started`
- Colour the tier cell: A `C6EFCE`, B `FFEB9C`, C `FCE4D6`, X `E7E6E6`
- **Pair every row with its own link before you sort.** Sorting rows and zipping them
  against an unsorted list of URLs attaches every link to the wrong job. Build
  `(row, url)` pairs first, then sort the pairs. Check two rows by hand afterwards.

If the workbook is open in Excel it will be locked. Say so and ask them to close it — do
not write somewhere else instead.

## Report

Tier A in full, notable Bs, counts for C and X, and anything where you disagreed with the
score. Say how many were new. Then point at the best one:

```
/apply-to-job <url>
```
