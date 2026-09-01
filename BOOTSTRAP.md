# Bootstrap — instructions for the agent

**You are setting this repo up for the person you are talking to.** Work through these
phases in order. Do not skip the interview, and do not invent answers on their behalf.

Tell them at the start roughly what is coming: a few prerequisite checks, about a dozen
questions, then you build their config, CV and trackers and run one job through end to end.
It takes about ten minutes and most of it is them typing answers.

---

## Phase 1 — Check prerequisites

Run these and report what is present:

```bash
python --version
python -c "import openpyxl; print('openpyxl ok')"
python -c "import playwright; print('playwright ok')"
python -c "import pypdf; print('pypdf ok')"
```

```bash
pdflatex --version
```

Install what is missing and safe to install (`pip install openpyxl pypdf`). **Do not install
a LaTeX distribution or a browser engine without asking** — both are large downloads.

If neither `pdflatex` nor `playwright` is available, tell them they need one before the CV
step will work, and offer both options with their sizes: LaTeX is a several-hundred-megabyte
install, Playwright's Chromium is around 150MB.

If `pdflatex` is present on Windows, run this now, because MiKTeX's default install is
missing fonts the template needs and the failure is confusing:

```bash
initexmf --set-config-value="[MPM]AutoInstall=1"
```

---

## Phase 2 — Interview

Ask these. Group them — do not fire twenty separate questions. Where they are unsure, say
what the consequence of each answer is rather than picking for them.

**About them**
1. Name, city and country, email, phone
2. Portfolio or personal site, LinkedIn URL
3. Current or most recent job title

**Work authorisation** — the most important answers here
4. Which countries can they legally work in right now?
5. Are they on a visa or permit with a status change coming?
6. Any country they would need sponsorship for and would still consider?

**Languages**
7. Which languages, at what honest level?
8. Should a job requiring a language above that level be a hard stop, or flagged for them
   to judge?

**The search**
9. What roles are they looking for? Get 3-6 search phrases, not job families
10. Which cities, regions, or remote arrangements?
11. Anything that should be rejected on sight — titles or industries they will never take

**Practicalities**
12. Salary band and currency
13. When can they start?
14. Do they already have a CV file? What format, and where is it?

---

## Phase 3 — Write their config

**`profile.md`** — from `profile.example.md`, filled in with their answers. This file is
load-bearing: every skill reads it. Be specific and blunt in it. If they said French A1,
write that treating a French-fluency requirement as a hard blocker is the rule.

**`config.json`** — from `config.example.json`:
- `location`, `timezone` from their city
- `keywords` from their search phrases, each with a sensible `family` label
- `scoring.must_have_any` — words that must appear in a job **title**. Derive these from
  their target roles, and explain the mechanism: this is the filter that keeps unrelated
  roles out
- `scoring.reject_any` from their never-take list
- `location_filter` from their cities plus `remote` if applicable

Show them both files and ask if anything is wrong before continuing.

---

## Phase 4 — Their CV

If they have a CV already:
- **`.tex`** → copy it to `cv/master_cv.tex` and use it as-is. Do not restructure it. It is
  theirs, and its formatting is the reason this repo exists.
- **`.docx`, `.pdf` or anything else** → read the content, then fill
  `cv/templates/master_cv.html` with it and save as `cv/master_cv.html`. Tell them plainly
  that the layout will not match their original, and that if they want their exact design
  they should convert it to LaTeX or HTML themselves and drop it in.

If they have no CV, fill the template from the interview answers and tell them it is a
starting point, not a finished CV.

Then build it and **do not proceed until it is one page**:

```bash
python cv/build.py --template cv/master_cv.tex
```

If it is two pages, work with them to cut. Do not raise `--max-pages` and do not shrink the
font — a master that overflows makes every tailored version overflow.

---

## Phase 5 — Contact finding

Explain the trade honestly: Explorium's free tier covers search and preview, which is all
this repo uses, but it needs an account. Without it, contact-finding falls back to company
websites and web search, which is fine for small companies and weak for large ones.

If they want it:

```bash
claude mcp add -s user --transport http vibe-prospecting https://vibeprospecting.explorium.ai/mcp
```

Then tell them to run `/mcp` in a **new** session and complete the browser sign-in. You
cannot do the OAuth for them, and you must not ask them for a token or a callback URL.

---

## Phase 6 — Trackers

```bash
python trackers/make_trackers.py
```

Tell them to delete the example row in each once they have looked at it.

---

## Phase 7 — Prove it works

Do not declare success until a job has been through the whole thing.

1. Ask them for one real job URL they are actually interested in
2. Run the `apply-to-job` skill on it
3. Confirm they end up with: a one-page PDF in `applications/<Company>/`, and rows in
   `Contacts.xlsx`

If any step fails, fix it now rather than handing over a broken setup.

---

## Phase 8 — Hand over

Tell them, in plain terms:

- The three commands they will actually use: `/find-jobs`, `/apply-to-job <url>`,
  `/follow-ups`
- That `profile.md`, `config.json` and their CV are theirs to edit whenever things change,
  and that editing `profile.md` changes how every skill behaves
- That **nothing sends anything for them** — they submit forms and press send on LinkedIn
- That everything personal is gitignored, so if they push this repo their CV, trackers and
  profile stay behind

Then ask what is still unclear, and answer it.
