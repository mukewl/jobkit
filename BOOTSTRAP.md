# Bootstrap — setup instructions for the agent

**You are setting this repo up for the person you are talking to.** Follow these phases in
order.

The single rule that makes this feel professional rather than like filling in a form:
**ask only what you cannot work out yourself.** Their CV contains their name, contact
details, job history, seniority, skills and often their languages and portfolio. Read it,
extract all of that, and show them what you found for confirmation. Never ask for something
that was on page one of the file they just gave you.

There are **six questions**. Not seven. If you find yourself wanting to ask a seventh,
you have missed something you could have inferred.

Open by telling them what is about to happen:

> I'll ask you six things, then set everything up and run one real job through it end to end.
> Takes about ten minutes, most of it you typing.

---

## Phase 1 — Check prerequisites (silent)

Run these before asking anything. Do not narrate it; just fix what you can and raise what
you cannot.

```bash
python --version
python -c "import openpyxl, pypdf; print('py deps ok')"
python -c "import playwright; print('playwright ok')"
pdflatex --version
```

- Install missing pip packages yourself: `pip install openpyxl pypdf`
- **Do not install LaTeX or a browser engine without asking.** Both are large. If neither
  `pdflatex` nor `playwright` is present, fold the choice into question 1 rather than making
  it a separate interruption.
- On Windows with MiKTeX present, run this now — its default install lacks fonts the
  template needs and the resulting error is baffling:
  ```bash
  initexmf --set-config-value="[MPM]AutoInstall=1"
  ```

---

## Phase 2 — The six questions

Use `AskUserQuestion` where your client supports it, with real options rather than open
prompts. Ask them in **two batches of three**, not one at a time. Where an answer is
genuinely open (their CV path, their target roles), free text is right.

### 1. Your CV

> Where's your CV? Give me a file path, or paste the text.

Accept anything: `.tex`, `.html`, `.docx`, `.pdf`, `.md`, or pasted text. If they have none,
say you will build one from the interview and that it will be a starting point rather than a
finished CV.

If neither LaTeX nor Playwright was found in Phase 1, add the engine choice here:

> I'll also need one of these to build PDFs — LaTeX (~400MB, best if you want exact control
> of the layout) or Playwright's Chromium (~150MB, simpler). Which would you rather?

### 2. Where can you legally work?

Countries, and whether that is about to change.

> Which countries can you work in right now without a new visa? And is that about to
> change — a permit expiring, a status change coming, a graduation?

Follow with, only if relevant: would they consider a role that needs sponsorship?

**This is the most consequential answer in the whole setup.** It is what stops the agent
spending their week on roles they cannot take.

### 3. What are you looking for, and where?

Propose from the CV rather than asking cold:

> From your CV you look like a [title] at [level]. I'd search for things like
> [3-4 phrases]. Right, or should I aim somewhere else?
>
> And which cities, countries or remote arrangements?

### 4. Languages — what's the rule?

Extract the levels from their CV first, then ask about the **rule**, which is the part you
cannot infer:

> Your CV lists [languages and levels]. When a job needs a language above your level, should
> I treat that as a hard stop, or flag it and let you judge?

### 5. Money and timing

> What salary band and currency should I use when an application demands a number, and when
> could you start?

Tell them a band is used to answer forms, not to filter jobs, so being honest costs nothing.

### 6. Where should the jobs come from?

Offer the three that ship as defaults, then ask what else they use. Present them as
options, not a lecture:

> Three sources work out of the box:
>   - **himalayas** — remote roles worldwide
>   - **arbeitnow** — Europe and the UK, and it flags visa sponsorship
>   - **csv_import** — a file you export yourself from any board
>
> Which of those fit? And are there boards you already use that I should try to add —
> a national one, or something industry-specific?

Boards vary enormously by country, so someone in Brazil or India will need different
sources than the two shipped ones. Take their answer seriously rather than talking them
into the defaults. Phase 4 is where you act on it.

---

## Phase 3 — Show your work, once

Before writing a single file, show one compact summary of everything you extracted and
everything they told you:

```
Name          Jane Doe
Contact       jane@example.com · +33 000 000 000 · linkedin.com/in/janedoe
Currently     Growth Marketing Manager, 4 years
Can work in   France only (student visa → post-study permit)
Looking for   growth marketing manager, performance marketing, digital marketing manager
Where         Paris, Lyon, remote EU
Languages     English fluent, French A1 → French above A1 is a hard stop
Money         EUR 45–60k, available immediately
Sources       CSV export from Indeed FR, plus a Welcome to the Jungle adapter
CV engine     LaTeX (found on PATH)
```

> Anything wrong before I write this?

One confirmation, then go. Do not re-ask things they have already answered.

---

## Phase 4 — Job sources

Start by switching on whichever shipped sources they picked — set `sources` in
`config.json` and run one search to prove jobs actually arrive. That alone gets them to a
working queue in under a minute, and it is worth doing before anything harder.

Then, for each *additional* board they named, work out which of these applies and say which
one you are doing:

**It has a public API or feed.** Offer to write an adapter in `search/sources/`. **Read the
terms of service first, and say what you found.** If the terms forbid automated access, say
so and do not write it — offer the export route instead.

**It has an export, or a saveable search.** The common case. Walk them through exporting
results to CSV, then point `csv_import.path` at the file. It is manual, it takes two minutes
a day, and it never breaks.

**It has neither.** Say so plainly. Suggest they search in the browser and paste rows into
a CSV. Do not invent a scraper to fill the gap.

Whatever happens, the setup must end with `csv_import` working against a real file of their
own, even if it only has five rows in it. **A configured pipeline with no jobs in it is a
failed setup.**

---

## Phase 5 — Write the configuration

**`profile.md`** from `profile.example.md`. This is load-bearing — every skill reads it
before acting. Write their work authorisation, language rule, salary and availability as
plain, blunt statements. "French A1. Treat a stated French-fluency requirement as a hard
blocker" is worth more than a paragraph of nuance.

**`config.json`** from `config.example.json`:
- `location`, `timezone` from their city
- `keywords` from their target roles, each with a `family` label
- `scoring.must_have_any` — words that must appear in a job **title**. Derive from their
  target roles and explain the mechanism, because this is the filter they will want to tune
  later
- `scoring.reject_any` — titles they would never take
- `location_filter` — their cities, plus `remote` where relevant
- `sources` and the matching source settings

**Their CV** into `cv/`:
- Already `.tex` or `.html` → copy it in as-is. **Do not restructure it.** Its formatting is
  the reason this repo exists.
- Any other format → extract the content into `cv/templates/master_cv.html` and save as
  `cv/master_cv.html`. Tell them plainly that the layout will not match their original, and
  that converting their own design to LaTeX or HTML gets it back.

Then build it, and **do not continue until it is one page**:

```bash
python cv/build.py --template cv/master_cv.tex
```

If it overflows, cut with them. Never raise `--max-pages`, never shrink the font — a master
that runs long makes every tailored version run long.

**Trackers:**

```bash
python trackers/make_trackers.py
```

---

## Phase 6 — Contact finding

State the trade honestly and let them choose:

> Finding people at each company uses Explorium. Its free tier covers search and preview,
> which is all this repo uses — but it needs an account. Without it I fall back to company
> websites and web search, which works at a 50-person startup and poorly at a large group.

If they want it:

```bash
claude mcp add -s user --transport http vibe-prospecting https://vibeprospecting.explorium.ai/mcp
```

Then: run `/mcp` in a **new** session and complete the browser sign-in. You cannot do OAuth
for them. **Never ask them for a token, a code, or a callback URL.**

---

## Phase 7 — Prove it works

Do not say you are done until a real job has been through the whole thing.

1. Ask for one job URL they actually care about
2. Run the `apply-to-job` skill on it
3. Confirm they have a one-page PDF in `applications/<Company>/` and rows in `Contacts.xlsx`

If anything fails, fix it now. Handing over a setup you have not seen work is the one
failure that wastes their whole evening.

---

## Phase 8 — Hand over

Print this, filled in with their actual details. One line per step, nothing longer:

```
You're set up. Here's the whole thing:

1. python search/fetch_jobs.py   Collects jobs from your sources, skips any you've seen before
2. /find-jobs                    Sorts them into tiers, flags language and visa risk, fills your tracker
3. /apply-to-job <url>           Tailors your CV, finds who to contact, writes the messages
4. You apply and send            Nothing here submits a form or messages anyone for you
5. /follow-ups                   A week later: who went quiet, and one nudge each

You don't need steps 1 and 2. If you find a job anywhere - LinkedIn, a friend,
a newsletter - just paste the link into /apply-to-job and it works the same.

Your files:
  profile.md          your rules. Edit this and everything changes behaviour
  cv/master_cv.<ext>  your CV. Tailored copies never edit it
  Job_Tracker.xlsx    roles
  Contacts.xlsx       people, messages, and when to follow up

Two things worth knowing:
  Contact finding stays on Explorium's free tier - it reads names off the preview
  and I type them into your spreadsheet. It never exports, which is the paid part.
  Everything personal is gitignored, so pushing this repo leaves your CV behind.
```

Emphasise point 4 out loud as well as in the text: **nothing here sends anything for them.**
It is the thing people most often assume wrongly, and the assumption is expensive.

Then tell them the single most useful thing about their own setup — the one rule in their
`profile.md` that will reject the most jobs. For someone with a language constraint that is
the language rule; for someone on a visa it is the work authorisation. Say which one it is
for them, and that editing `profile.md` is how they change it.

Then ask what is unclear, and answer it.
