# jobkit

A job-application pipeline you run yourself, on your own machine, with your own AI coding
agent. It finds roles, writes a tailored CV that keeps your formatting, works out who to
talk to at each company, and drafts the messages. You press send.

No SaaS account. No subscription for the pipeline itself. No agent applying to jobs on your
behalf while you sleep.

---

## What it actually does

**1. Finds jobs.** A small Python pipeline pulls listings from whatever sources you plug in,
filters them on your keywords and locations, and remembers every job it has ever shown you
so nothing appears twice. Runs locally, or free on GitHub Actions on a schedule.

**2. Tailors your CV.** Your CV stays *your* CV — a LaTeX or HTML file you own. The agent
rewrites the summary, reorders your competencies and bullets for each job, and rebuilds the
PDF. The build tool **exits non-zero if the result runs over one page**, so a two-pager
cannot quietly reach an employer.

**3. Finds people.** For each application, it returns 5-10 named people at that company with
their titles and LinkedIn profiles, ranked by how close they sit to the actual role — and it
tells you which of them are noise.

**4. Drafts the outreach.** A connection note and a follow-up message per person, in a
format built to get replies: ask a real question, do not pitch, no metrics.

**5. Tracks it.** Two spreadsheets — roles and people — including a follow-up date so
nothing goes quiet unnoticed.

## What it does not do

- **It does not apply for you.** It builds the CV and the messages. You submit the form and
  you press send on LinkedIn. This is deliberate: automated applications are worth less than
  the time they save, and automated LinkedIn activity gets accounts banned.
- **It does not invent anything.** The agent is instructed, repeatedly and specifically, that
  every number, employer, tool and date on a tailored CV must already exist on your master.
  If a job wants a skill you do not have, it tells you instead of writing it in.
- **It does not ship a scraper.** See [search/sources/README.md](search/sources/README.md).

---

## Honest limitations

- **Contact-finding needs a paid service.** Explorium (Vibe Prospecting) has a free search
  and preview tier that this repo stays inside, but it needs an account. Without it you fall
  back to company websites and web search, which works fine at a 50-person startup and
  poorly at a 300,000-person group.
- **Job sources are your problem.** Only a CSV importer ships. Adapters that scrape sites are
  yours to write, and sites change their HTML without warning.
- **The LaTeX path needs a LaTeX install**, which is a genuine barrier. The HTML path needs
  only Playwright. Both are supported and both produce a page-checked PDF.
- **The pipeline's filtering is dumb on purpose.** It matches title keywords and location
  strings. All the judgement lives in the agent skills, where it can be read and argued with.

---

## Getting started

Two ways in:

**Let your agent do it.** Clone the repo, open it in Claude Code or Codex, and say:

> Read BOOTSTRAP.md and set this up for me.

It will check your prerequisites, ask you about a dozen questions, write your config and
profile, generate the trackers, and run one search and one application end to end.

**Or do it by hand.** [SETUP.md](SETUP.md) is the same thing written out, about fifteen
minutes.

## Daily use

```bash
python search/fetch_jobs.py          # collect and dedupe; opens in public/index.html
```

Then in your agent:

```
/find-jobs                            # triage today's queue into the tracker
/apply-to-job <job url>               # CV + contacts + drafted messages
/follow-ups                           # who has gone quiet, and one nudge each
```

## Layout

```
config.json          your keywords, locations, filters      (gitignored)
profile.md           your work authorisation, languages     (gitignored)
cv/master_cv.tex     your CV, the single source of truth    (gitignored)
search/              the collection pipeline + source adapters
cv/build.py          template -> PDF, with the page check
trackers/            generates Job_Tracker.xlsx + Contacts.xlsx
.claude/             the skills your agent runs
```

Everything personal is gitignored by default. Your CV, your trackers, your config and your
profile never enter git unless you go out of your way.

## Licence

MIT. Do what you like with it.
