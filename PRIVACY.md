# Where your data goes

This repo handles a CV, a visa status, a salary expectation, and a spreadsheet of named
recruiters and hiring managers. That deserves a straight answer rather than a policy page.

There is no account, no server, and no telemetry. Nothing in this repo phones home, because
there is no home to phone. What follows is everything else.

## Stays on your machine

These are gitignored and never pushed:

```
profile.md              work authorisation, languages, salary, hard rules
config.json             your searches and boards
cv/master_cv.tex|html   your CV
applications/           every tailored CV and cover letter
Contacts.xlsx           other people's names, titles and LinkedIn URLs
Job_Tracker.xlsx        every role you have looked at
seen_jobs.csv           the history of what you have been shown
data/, public/          raw search results and the rendered dashboard
```

Check for yourself before any push:

```bash
git ls-files
```

If a file with your details is in that list, it is about to become public.

## Leaves your machine

| Where | What | When |
|---|---|---|
| `himalayas.app` | your search keywords | only if `himalayas` is in `sources` |
| `arbeitnow.com` | your search keywords | only if `arbeitnow` is in `sources` |
| Any board you add | your search keywords | only boards you paste in yourself |
| Explorium | a company name, and role titles you are looking for | during contact finding |
| Your AI provider | **your whole CV**, the job description, and your `profile.md` | every time a skill runs |

That last row is the big one and it is easy to forget. The agent has to read your CV to
tailor it, which means your CV, your visa status and your salary band go to whoever runs
your model, under their terms, not this repo's. If that matters to you, it matters before
you start, not after.

Explorium is used for search and preview only. The skills forbid `export-to-csv` and
`enrich-prospects`, which are the paid calls. Nothing here spends money.

## Other people's data

`Contacts.xlsx` fills up with real people who did not ask to be in a stranger's spreadsheet:
names, job titles, employers, LinkedIn URLs.

Under GDPR that is personal data and you are the controller of it. This repo cannot make you
compliant and does not claim to. The practical version:

- Keep it local. It is gitignored for a reason - do not move it somewhere shared.
- Keep it small. Contacts for jobs you are actually applying to, not a harvested list.
- Never sell it, publish it, or pass it on.
- Delete it when your search ends. There is no reason to still hold it a year later.

If someone asks you to remove them, remove them.

## The scheduled-run warning

`.github/workflows/daily.yml.example` commits search results back into the repository so the
collection step can run with your machine off. Those results are a record of every job you
have been shown, which says more about you than it looks like.

**Use a private repository for that, and only that.** To make the workflow useful at all you
have to un-ignore `data/` and `seen_jobs.csv`, which removes the protection that would
otherwise stop them being published. Do not run it in a public fork.

## What this never does

- No LinkedIn login, no connection requests, no InMail, no scraping while authenticated
- No messages sent on your behalf. It drafts; you press send
- No application forms submitted
- No CAPTCHA solving
- No spending without asking
- No analytics, no crash reporting, no usage tracking, no account with this project

The messages and the applications are yours to send by hand. That is a deliberate design
choice, not a missing feature.
