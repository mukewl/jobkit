---
description: Tailor the master CV to one job posting and build a page-checked PDF that keeps the original formatting
argument-hint: "<job-url | pasted JD text> [--out <folder>]"
---

# Tailor the CV to a job

Produce ONE tailored PDF for the job in `$ARGUMENTS`, in the master's exact formatting.
Invent nothing.

## Inputs

- **Profile (read first):** `profile.md` at the repo root. It carries work authorisation,
  languages, salary, and hard rules. If it is missing, stop and tell the user to copy
  `profile.example.md` to `profile.md` and fill it in.
- **Master CV (read-only, never edit):** `cv/master_cv.tex` or `cv/master_cv.html`,
  whichever exists. If both exist, prefer the one the user names; otherwise `.tex`.
- **Argument:** a job URL, or pasted job-description text.
  - URL → fetch it. Try WebFetch first. Many job sites return 403 to it (Welcome to the
    Jungle and Ashby both do) — when that happens, open the URL in a browser tool and read
    `document.body.innerText`. If both fail, stop and ask for the pasted text.
    **Never guess the role.**
  - Text → use it directly.
- Optional `--out <folder>` → output directory. Default `applications/<Company>/`.

## Step 1 — Read the posting

Extract: company, exact title, location, contract type, years required, responsibilities,
must-have skills, language requirement, and any stated work-authorisation, citizenship or
clearance requirement.

**Stop and warn before doing any work** if the posting requires a language above the level
in `profile.md`, requires the right to work somewhere the user is not authorised, or
requires citizenship or clearance. State it plainly and ask whether to continue. Do not
quietly tailor a CV for a job the user cannot take.

## Step 2 — Tailor

Copy the master to the output folder, then edit only these parts:

1. **Summary** — retarget to this role. Three sentences maximum. Match the master's voice;
   if the master is impersonal, stay impersonal.
2. **Competencies line** — reorder so what this JD asks for comes first. You may drop items
   to save space. **You may not add one that is not already in the master.**
3. **Experience bullets** — reword to lead with the outcome this JD cares about, and
   reorder bullets within a role.
4. **Section order** — only if the JD clearly calls for it.

### Hard rules

- **No new facts.** Every number, date, employer, job title, tool and scope must already
  appear in the master. If the JD wants a tool the master does not have, it does not go in.
  Say what is missing in your summary instead.
- **Never claim a language above the level in `profile.md`.** The header language line is
  copied verbatim.
- **Never remove** anything `profile.md` lists under "CV facts that must survive tailoring".
- **Do not touch** the preamble, document class, geometry, fonts, or spacing. Formatting
  fidelity is the whole point of this command.
- Rewording is allowed. Upgrading scope ("managed" → "owned") only where the job title in
  the master already carries that authority.

### To fit one page

In this order: tighten the summary → trim the competencies list → shorten the weakest
bullets → drop the oldest, thinnest role. Never shrink the font or margins. Never drop the
two most recent roles.

## Step 3 — Build and verify

```bash
python cv/build.py --template <output>/<name>.tex --out <output>/<name>.pdf
```

`build.py` **exits non-zero if the PDF runs past one page.** If it does, go back to the fit
list above, cut more, and build again. Repeat until it passes. Do not hand over a two-page
CV, and do not raise `--max-pages` to make the error go away.

If it reports that `pdflatex` is missing, tell the user to install a LaTeX distribution —
or to switch to the `.html` master, which needs no LaTeX.

## Step 4 — Deliver

- Name the PDF `CV_<Company>_<Role>.pdf`, no spaces.
- Keep the source file beside it so it can be re-edited.

Report back, briefly:

1. Output path and the confirmed page count
2. What you changed — summary, competencies, which bullets
3. **Gaps** — what the posting asks for that the CV genuinely does not support. Be straight
   about it; this is what gets asked in a first-round call.
