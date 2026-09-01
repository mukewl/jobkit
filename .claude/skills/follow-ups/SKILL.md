---
name: follow-ups
description: Find outreach that has gone cold and draft one nudge each - reads Contacts.xlsx for messages sent more than a week ago with no reply. Use when asked about follow-ups, who to chase, what has gone quiet, or which messages need a nudge.
---

# Chase what has gone quiet

The unglamorous half of outreach, and the half most people skip. One nudge after about a
week roughly doubles reply rates. A second nudge does not, and a third makes an enemy.

Read `profile.md` for the user's name and voice before drafting anything.

## Step 1 — Find what is due

Read `Contacts.xlsx` at the repo root. A row needs chasing when **all** of these hold:

- `Status` is `Request sent` or `Connected`
- `Date sent` is more than 7 days ago (the `Follow-up due` column computes this, but
  compute it yourself too — the formula only evaluates once Excel has opened the file, so it
  reads as `None` to openpyxl on a freshly written workbook)
- `Notes` does not already record a nudge

Skip anything at `Replied`, `No reply`, or `Not sent`. `No reply` means the user has already
decided it is dead; do not resurrect it.

If nothing is due, say so plainly and stop. Do not invent work.

## Step 2 — Draft one nudge each

Short. Shorter than the original — under 60 words. The whole message is: I am still
interested, here is one new thing, no pressure.

Structure:

1. `Hi <Name>, just following up on this.` — or a variant that does not sound automated
2. One sentence of genuinely new information: the application has progressed, they shipped
   something relevant, the user published something. **If there is nothing new, say the
   nudge is a nudge** — that is more honest than manufacturing a reason
3. Repeat the ask once, smaller than before. "Even 10 minutes" beats re-asking for 15
4. An explicit way out: something like "happy to leave it if the timing is wrong"

Never guilt-trip, never mention that they did not reply, never re-send the original message
with a new greeting stapled on. No metrics — the same rule as first contact.

The way out in point 4 is not politeness padding. It gives a busy person permission to
answer at all, and it means the user hears back either way.

## Step 3 — Report and record

Show each draft in chat, grouped by company, with how many days it has been.

Then update `Contacts.xlsx`: append `Nudged <date>` to `Notes` for each row you drafted for.
Do not change `Status` — the user has not sent it yet. Preserve every other cell.

If a contact has already been nudged once and is still quiet, do not draft a second one.
List them under a short "leave these" heading instead, and say why: two unanswered messages
is the point where persistence stops reading as interest.
