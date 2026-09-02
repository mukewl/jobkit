---
name: apply-to-job
description: End-to-end prep for one job application - read the posting, produce a tailored page-checked CV in the user's own formatting, find 5-10 named people worth contacting at that company, and draft LinkedIn messages for the user to send by hand. Use when given a job URL or job description and asked to apply, prepare an application, tailor a CV for a role, or find who to reach out to about a job.
---

# Prepare one job application

Given a job posting, produce everything needed to apply by hand: a tailored CV, a shortlist
of real people, and drafted messages. **Nothing is ever sent automatically, and nothing that
costs money is ever bought.**

Read `profile.md` at the repo root before anything else. It carries work authorisation,
languages, salary and the user's hard rules. If it is missing, stop and say so.

Output folder: `applications/<Company>/`

## Step 1 — Read the posting

URL → fetch it. WebFetch first; when it 403s (Welcome to the Jungle and Ashby both do),
open it in a browser tool and read `document.body.innerText`. If both fail, stop and ask for
the pasted text. **Never guess the role.**

Extract: company, exact title, location, contract type, years required, responsibilities,
must-have skills, language requirement, and any stated work-authorisation, citizenship or
clearance requirement.

**Stop and warn before doing any work** if the posting breaches anything in `profile.md` —
a language above the stated level, the right to work somewhere the user is not authorised,
citizenship, or a clearance. Say it plainly and ask whether to continue.

## Step 2 — Tailor the CV

Follow `.claude/commands/tailor-cv.md` exactly. It is the single source of truth for the CV
rules: master is read-only, invent nothing, never exceed the profile's language level, keep
what the profile says must survive, never touch the preamble, and verify the page count with
`cv/build.py` — which exits non-zero on overflow.

## Step 3 — Find 5-10 people worth contacting

Use the **Explorium (Vibe Prospecting)** MCP. Load its tools with `ToolSearch` first —
search `vibe prospecting fetch entities prospects` and select `fetch-entities` and
`show-sample`.

### How this stays free

Explorium's search and preview are free; export costs credits. You never need the export.

`show-sample` returns five people with **real names, titles and LinkedIn URLs already
visible**. Read them straight off that response and write them into `Contacts.xlsx`
yourself. That is the entire technique. Want more than five? Run the fetch again with
`exclude_key: "prospects"` and read the next five. Every round is free.

The paid export exists to hand you a CSV. You have an agent that can type, so you do not
need one.

### Absolute rules — money

- **NEVER call `export-to-csv`.** Not once, not "just this table", not if the credit balance
  looks healthy. Search and preview are free; export is not.
- **NEVER call `enrich-prospects`.** It returns masked values that only unmask on export, so
  it buys nothing here.
- Never confirm any credit-consuming action on the user's behalf. If a tool asks to spend,
  stop and report.
- `cost_in_credits` in a response is an *export estimate*, not a charge. Exploration already
  happened for free. Do not report it as money spent.

### Procedure

1. **Find the company's `business_id`.** `fetch-entities` with `entity_type: "businesses"`,
   `website_keywords` set to the company name and its domain word, plus
   `company_country_code`. Confirm `business_name` and `business_domain` really are the
   employer before continuing — name collisions are common and cost you the whole run.
2. **Fetch prospects at that `business_id`.** `entity_type: "prospects"`, with:
   - `business_id` from step 1
   - `job_department` matching the role's function; add adjacent departments only when the
     JD calls for them
   - `job_level` — for a **large company** (1000+), use
     `["manager","senior manager","director"]`. The VP and C-suite layer is too far above a
     manager-level application to be worth contacting. For a **small company** (under ~200),
     use `["founder","c-suite","director","manager"]`, because there the founder or
     department head genuinely is the hiring manager.
   - `prospect_country_code` for the country the role sits in
3. **Call `show-sample`** with the returned `table_name`. Five rows come back with real
   names, titles and LinkedIn URLs.
4. **Want more? Re-run step 2 with `exclude_key: "prospects"`** and call `show-sample`
   again. Repeat until you have 5-10 relevant people. Every round is free.
5. If nothing relevant surfaces after two rounds, say so plainly and fall back to the
   posting itself, the company's own team and about pages, and web search.

### Reading the results

- Quote `records_available` as what you got. `records_matching_filters` is upstream
  headroom — never present it as data you hold.
- Prospect fetches return **no email or phone values**, by design. Do not imply otherwise,
  and never guess an address and present it as found.
- LinkedIn URLs come back obfuscated (`linkedin.com/in/ACoAA...`). They resolve in a
  logged-in browser, but give the name and title too so the user can just search.

Rank people by how close they sit to the actual role — the team the job describes working
with, then that team's manager. Say which are relevant and **which are noise**. A brand
director at a different division is not the right contact for a growth role, and saying so
saves the user more time than one extra name.

**Never** log into LinkedIn, search it while authenticated, send connection requests, or
send InMail. The user sends everything by hand.

## Step 4 — Draft the outreach

Append rows to `Contacts.xlsx` at the repo root with openpyxl, preserving existing rows and
formatting. Columns:

`Company | Role applied | Priority | Name | Title | Why them | LinkedIn |
Connection note (<300 char) | Message once connected | Status | Date sent |
Follow-up due | Notes`

Priority 1-3 = contact these, 4-5 = optional, 9 = surfaced but not relevant. Set `Status` to
`Not sent` and leave `Follow-up due` alone — it is a formula. Give every person a row; write
messages only for priority 1-3. Row height ~200 for rows carrying messages.

For each of the top 2-3 people write two things.

**The connection note** (under 300 characters, sent with the request): one line on what they
applied for, one line on who they are. No metrics. No pitch.

**The message once connected** (under 140 words):

1. `Hi <Name>, thanks for connecting.`
2. The honest reason for writing — they applied, and would **rather ask someone inside than
   work it out from the job ad**.
3. Two or three sentences on who they are, tied to something specific about **that person's**
   background. No numbers.
4. One or two real questions — what the team is actually like day to day, plus something
   only that person could answer about their own path or the work.
5. `Would you have 15 minutes for a call in the next week or two? Happy to fit around
   whenever suits you.`
6. `Thanks,` / the user's first name

**Ask, do not sell.** No metrics anywhere in outreach — no CAC figures, no revenue, no
follower counts. Those live on the CV, and reading as a pitch is what kills these messages.
Never close with a challenge or an ultimatum. Where the user does not meet a requirement,
name it plainly once and move on; that reads as honest, not weak.

Do not quote someone's own profile back at them. It reads as homework rather than interest.
Noticing a job change or a career path is fine; reciting their About section is not.

If the workbook is locked (open in Excel), say so and ask the user to close it rather than
silently writing somewhere else.

## Step 5 — Deliver

Leave in `applications/<Company>/`: the CV PDF and its source. Contacts and messages go in
`Contacts.xlsx`, not here.

Then report **in chat**, briefly:

1. Output path and the confirmed page count
2. What changed in the CV
3. The people found, ranked, with one line on why each is or is not relevant
4. **The connection note and the message in full**, so they can be copied straight from the
   conversation without opening the workbook
5. **Gaps** — what the posting wants that the CV genuinely does not support

Finally, remind the user to log the row in `Job_Tracker.xlsx`, or offer to do it.
