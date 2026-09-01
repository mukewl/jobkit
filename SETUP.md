# Setup

About fifteen minutes by hand. If you would rather not, open the repo in Claude Code or
Codex and say *"read BOOTSTRAP.md and set this up for me"* — it does all of the below and
asks you the questions it needs.

---

## 1. Prerequisites

**Required**

- **Python 3.11+** — `python --version`
- **An AI coding agent** — [Claude Code](https://claude.com/claude-code) or Codex
- `pip install openpyxl`

**One of these two, for building the CV**

- **LaTeX**, if you want the `.tex` template:
  - Windows: `winget install MiKTeX.MiKTeX`
  - macOS: `brew install --cask basictex`
  - Linux: `sudo apt install texlive-latex-recommended texlive-fonts-recommended`
- **Playwright**, if you want the `.html` template instead:
  - `pip install playwright && python -m playwright install chromium`

**Optional but recommended**

- `pip install pypdf` — a more reliable page count on the HTML path

### If you chose MiKTeX, do this now

MiKTeX installs a minimal package set that is missing fonts this template uses. Turn on
automatic package installation before your first build, or it will fail on `helvet.sty`:

```bash
initexmf --set-config-value="[MPM]AutoInstall=1"
```

On Windows the MiKTeX binaries live in
`%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64` — reopen your terminal after installing so
they are on PATH.

---

## 2. Your profile

```bash
cp profile.example.md profile.md
```

Open it and fill it in properly. This is the file that stops the agent wasting your time —
it carries your work authorisation, your real language levels, your salary band, and your
hard rules.

Be blunt. "French A1, treat a French-fluency requirement as a hard blocker" saves you more
applications than any amount of clever tailoring.

`profile.md` is gitignored and never leaves your machine.

---

## 3. Your search config

```bash
cp config.example.json config.json
```

Edit:

- `location`, `timezone`
- `keywords` — the searches to run, each with a `family` label for grouping
- `scoring.must_have_any` — a word from this list must appear in the job **title**, not just
  the description. This is what keeps sales and engineering roles out of a marketing queue.
- `scoring.reject_any` — titles to drop outright
- `location_filter` — city and country substrings you will actually take
- `sources` — which adapters to run. Ships with `csv_import` only.

### Getting jobs in

`csv_import` reads a CSV or JSON you produce however you like — export from a board, save a
search, or paste rows in by hand. Point `csv_import.path` at it.

To pull from a live source, write an adapter: see
[search/sources/README.md](search/sources/README.md). It is about thirty lines. Read the
terms of any site you point it at first.

---

## 4. Your CV

Pick one:

```bash
cp cv/templates/master_cv.tex  cv/master_cv.tex     # LaTeX
cp cv/templates/master_cv.html cv/master_cv.html    # no LaTeX needed
```

Replace everything in `[brackets]` with your real content. This file is the single source of
truth — every tailored version is generated from it and never edits it.

Two things worth getting right now, because everything downstream depends on them:

1. **It must fit on one page.** Build it and check:
   ```bash
   python cv/build.py --template cv/master_cv.tex
   ```
   If the master is already two pages, every tailored version will be too.
2. **Every number on it must be true and defensible.** The agent is forbidden from adding
   facts, which means whatever is here is what you get.

---

## 5. Contact finding

The `apply-to-job` skill uses Explorium's Vibe Prospecting MCP to find people. Search and
preview are free; this repo never calls the paid export.

1. Sign up at [explorium.ai](https://explorium.ai)
2. Add the server:
   ```bash
   claude mcp add -s user --transport http vibe-prospecting https://vibeprospecting.explorium.ai/mcp
   ```
3. Start a fresh agent session, run `/mcp`, pick `vibe-prospecting`, and complete the
   browser sign-in.

Scope it with `-s user` so it is available from any folder. MCP servers connect at session
start, so the session where you added it will not see it — start a new one.

**Skipping this?** The skill falls back to the company's own site and web search. That works
well at small companies and badly at large ones.

---

## 6. Trackers

```bash
python trackers/make_trackers.py
```

Creates `Job_Tracker.xlsx` and `Contacts.xlsx` with headers, tier colours, filters and an
example row to delete. Both are gitignored. It refuses to overwrite existing files unless
you pass `--force`.

---

## 7. First run

```bash
python search/fetch_jobs.py
```

Opens nothing by itself — look at `public/index.html`. Then in your agent:

```
/find-jobs
/apply-to-job <a job url>
```

You should end up with a one-page PDF in `applications/<Company>/` and a handful of contacts
in `Contacts.xlsx`.

---

## Running it on a schedule

`.github/workflows/daily.yml.example` runs the collection step on GitHub Actions and commits
the results back, so your machine can be off.

```bash
mkdir -p .github/workflows
cp .github/workflows/daily.yml.example .github/workflows/daily.yml
```

**Use a private repo for this.** The workflow commits `data/` and `seen_jobs.csv`, which are
a record of every job you have been shown — mildly personal, and gitignored by default for
exactly that reason. You will need to un-ignore them for the workflow to have anything to
commit.

GitHub disables scheduled workflows after ~60 days without repository activity. The bot's own
commits keep it alive as long as new jobs keep appearing.

---

## Troubleshooting

**`LaTeX Error: File 'helvet.sty' not found`** — MiKTeX's minimal install. Run the
`initexmf` command in step 1 and build again.

**`pdflatex not found`** — installed but not on PATH. Reopen your terminal. On Windows check
`%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64`.

**The CV builds at two pages** — that is the tool working. Cut content. Do not raise
`--max-pages`, and do not shrink the font.

**A job source returns nothing** — check `seen_jobs.csv`. A job is shown once, ever, so a
role you remember will not reappear. Delete the file to reset the history.

**`refusing to overwrite`** from `make_trackers.py` — it is protecting data you have already
entered. Pass `--force` only if you mean it.

**The workbook is locked** — Excel holds an exclusive lock. Close it and retry.

**Explorium tools not found** — the server connects at session start. Start a new session
after adding it, and check `/mcp` shows it authenticated.
