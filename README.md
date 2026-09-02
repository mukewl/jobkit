# jobkit

**Give it a job link. Get back a tailored one-page CV, the names of the people worth
talking to at that company, and the messages to send them.**

```
/apply-to-job https://boards.example.com/acme/senior-marketing-manager
```

That one command is the whole point of this repo. Everything else is optional scaffolding
around it.

It runs on your machine, in your own AI coding agent, on your own CV. No SaaS account for
the pipeline, no subscription, and nothing applying to jobs on your behalf while you sleep.

---

## The one command

`/apply-to-job <url>` does four things:

**Reads the posting** and stops you first if it breaks a rule you set — a language you do
not have, a country you cannot work in, a citizenship or clearance requirement. It says so
before writing anything, instead of after.

**Tailors your CV.** Your CV stays *your* CV — a LaTeX or HTML file you own and control. It
rewrites the summary, reorders your competencies and bullets for this specific job, and
rebuilds the PDF. The build step **exits non-zero if the result runs over one page**, so a
two-pager cannot quietly reach an employer.

**Finds 5–10 real people** at that company, with titles and LinkedIn profiles, ranked by how
close they sit to the actual role — and tells you which ones are noise.

**Drafts the messages.** A connection note and a follow-up per person, in a format built to
get replies: ask a real question, do not pitch, no metrics.

You submit the form. You press send. It never does either for you.

**You do not need the rest of this repo to use it.** Found a job on LinkedIn, from a friend,
in a newsletter? Paste the URL and run the command. The job search below is a convenience,
not a prerequisite.

---

## The optional half: finding jobs

If you want a queue instead of hunting manually:

```
/find-jobs
```

One command. It searches every board you configured, drops anything you have already been
shown, **ranks what is left against your actual CV**, and writes it to your tracker in
tiers — apply now, stretch, check the language first, cannot take it.

**You configure boards by pasting a URL.** Run the search you would normally run on a site
you already use — your keywords, your filters, your city — and paste the URL you land on.
That search is the configuration:

```json
"boards": [
  { "name": "Indeed France", "search_url": "https://fr.indeed.com/jobs?q=growth&l=Paris", "enabled": true }
]
```

Job boards vary enormously by country, so this is deliberately yours to choose rather than
a list we picked. **You are responsible for the terms of any site you add** — most boards
restrict automated access, and pointing a browser at a search you ran yourself is a
judgement you get to make.

Two API sources need no URL and work anywhere, if you want them:

| Source | Covers | Notes |
|---|---|---|
| **himalayas** | Remote, worldwide | No key. [Free public API](https://himalayas.app/docs/remote-jobs-api) |
| **arbeitnow** | Europe and the UK | No key. Flags **visa sponsorship**, which almost nothing free does |

Every job is shown once, ever. A permanent `seen_jobs.csv` means you never re-read the same
listing.

## Keeping it free

Contact-finding uses [Explorium's Vibe Prospecting](https://vibeprospecting.explorium.ai)
MCP server. **Search and preview are free. Export costs credits.**

This repo stays inside the free tier on purpose, and the skill is explicitly forbidden from
leaving it:

- ✅ It searches, previews the results, and **reads the names off the preview**
- ✅ Your agent then writes those names into `Contacts.xlsx` itself
- ❌ It never calls `export-to-csv`
- ❌ It never calls `enrich-prospects`
- ❌ It never confirms a credit-consuming action on your behalf

That is the whole trick: you do not need the paid export, because the preview already shows
you five people with names, titles and LinkedIn URLs — and copying five rows into a
spreadsheet is something the agent does for free. Run the search again with a different
filter and you get five more.

You still need an Explorium account, which is free to create. Without one, the skill falls
back to company websites and web search: fine at a fifty-person startup, weak at a
300,000-person group.

---

## Getting started

Clone it, open the folder in Claude Code or Codex, and say:

> Set this up for me.

Six questions — your CV, where you can legally work, what you are after, your language rule,
salary and timing, and which job boards suit you. Everything else it reads off your CV. Then
it writes your config, imports your CV, builds the trackers, and runs one real job through
end to end before it tells you it is done.

Doing it by hand instead: [SETUP.md](SETUP.md), about fifteen minutes.

---

## Everything you can run

```
/apply-to-job <url>     the main event: CV + people + messages
/find-jobs              search your boards and rank the results against your CV
/filter-jobs            re-rank an existing queue, after a CV or rule change
/follow-ups             who has gone quiet, and one nudge each
```

## What it will not do

- **Apply for you.** Automated applications are worth less than the time they save.
- **Touch LinkedIn.** No logging in, no connection requests, no InMail. Automated LinkedIn
  activity gets accounts banned, and it is not worth your account.
- **Invent anything.** Every number, employer, tool and date on a tailored CV must already
  exist on your master. If a job wants a skill you do not have, it tells you rather than
  writing it in.

## Layout

```
config.json          your sources, keywords, filters         (gitignored)
profile.md           work authorisation, languages, rules    (gitignored)
cv/master_cv.tex     your CV, the single source of truth     (gitignored)
.claude/skills/      the skills your agent runs
search/              collection pipeline and source adapters
cv/build.py          template -> PDF, with the page check
trackers/            generates Job_Tracker.xlsx + Contacts.xlsx
```

Everything personal is gitignored. Push this repo and your CV, trackers, profile and config
stay behind.

## Licence

MIT.
