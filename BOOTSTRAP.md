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

### 6. Which job boards do you use?

This is the one that decides whether the whole thing is useful, so do not rush it.

> Which job boards do you actually use? For each one, run the search you'd normally run —
> your keywords, your location, your filters — and paste me the URL you end up on. I'll
> open that same search each time and read the results.
>
> Two extras that need no URL and work anywhere: **himalayas** (remote roles worldwide) and
> **arbeitnow** (Europe and the UK, flags visa sponsorship). Want those on as well?

The URL is the whole configuration. A search someone has already tuned on a site they know
beats anything you would guess for them.

Tell them plainly, once: **they are responsible for the terms of any site they add.** Most
job boards restrict automated access. Pointing a browser at a search they ran themselves is
a judgement they get to make; do not make it for them, and do not talk them out of it either.

If they name a board but have no URL, ask them to run the search now and paste it. Do not
guess a URL format.

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

## Phase 4 — Wire up the boards

Write each board they gave you into `config.json`:

```json
"boards": [
  { "name": "Indeed France", "search_url": "https://fr.indeed.com/jobs?q=...&l=Paris", "enabled": true }
]
```

Add whichever API sources they said yes to under `sources`.

**Then prove it works before moving on.** Run `/find-jobs` once, in front of them. It opens
each board, reads the results, folds in the API sources, filters everything against their
CV, and writes the tracker.

What you are checking:

- Every board returned rows. If one came back empty, look at the page — the search may have
  expired, needed a login, or thrown a challenge. Fix it now or disable it and say why.
- The tiers look sane. If everything landed in tier X, their work authorisation is probably
  written too tightly in `profile.md`. If everything is tier A, too loosely.

A board that fails silently on day one will be assumed broken forever. Catch it here.

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
- Any other format → fill in a **copy** of `cv/templates/master_cv.html` and save it as
  `cv/master_cv.html`. Never write real content into `cv/templates/` — those files are
  tracked and get pushed. Tell them plainly that the layout will not match their original,
  and that converting their own design to LaTeX or HTML gets it back.

Then build it, and **do not continue until it is one page**:

```bash
python cv/build.py --template cv/master_cv.tex     # or cv/master_cv.html
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

1. /find-jobs            Searches your boards, drops anything you've seen, and ranks
                         what's left against your CV. Writes it to your tracker.
2. /apply-to-job <url>   Tailors your CV for that job, finds who to contact there,
                         and writes the messages
3. You apply and send    Nothing here submits a form or messages anyone for you
4. /follow-ups           A week later: who went quiet, and one nudge each

You don't need step 1. If you find a job anywhere - LinkedIn, a friend, a
newsletter - paste the link into /apply-to-job and it works exactly the same.

(/filter-jobs re-ranks your existing queue without searching again. You'll want
it after you edit your CV or change your rules.)

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
