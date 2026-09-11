# Brief for Zapier co-pilot — Zap series_376761228 (Tidio → Code → SugarCRM)

Two confirmed bugs, found in live sandbox test data (not hypothetical — see evidence below).
Fix both, then run one real Tidio staging conversation through the full chain and report back
the raw JSON at each of the 3 steps (Trigger output, Code output, SugarCRM step output/response).

## Bug 1 — last_name is receiving a mangled full-name string
**Evidence:** Sugar record `4167e764-9b2c-11f1-bb73-0eb473bb02df` (2026-08-18 17:43 UTC) has
`first_name: "Andre"`, `last_name: "Noble O'Kon DDS"`. That is not a last name — it looks like
Tidio's "name" contact property is a single combined field, and it's landing whole into
`last_name` with `first_name` separately pulling just the first token.

**Fix:** In the Code step, split Tidio's name property properly:
- If Tidio sends ONE combined name field: split on first space only — everything before the
  first space is `first_name`, everything after is `last_name`. Do not attempt to strip
  titles/suffixes (Dr., PhD, DDS, etc.) — pass them through as part of last_name rather than
  guessing, that's a acceptable edge case per the failure-mode doc.
- If Tidio actually sends first_name/last_name as two separate contact properties already,
  the bug is in the field mapping (wrong property referenced for last_name), not the Code
  step — check which case this actually is and report which fix applied.

## Bug 2 — location_c fallback is CA, and it's masking failures, not just typos
**Evidence:** All 5 most recent sandbox Leads (including today's 2 real test runs) show
`location_c: "CA"`, regardless of what the synthetic test data implies about state. A silent
default to a real, populous state means a parse failure and a genuine California lead are
indistinguishable in the data — nobody can tell which happened after the fact.

**Fix:** Change the fuzzy-match fallback from `"CA"` to blank/null (empty string, not
"UNKNOWN" or any placeholder that would itself fail Sugar's 2-letter enum validation — confirm
Sugar accepts an empty `location_c` on Create before shipping this). An unmapped lead should
land in Sugar unassigned rather than silently misrouted to whichever rep owns CA — the daily
unassigned-lead sweep (already documented, PRL side) is the intended catch for this, not a
fake default.

## Also check while in there
- **account_name length**: current test data included a >255-char string in this field.
  Confirm Sugar's actual `account_name` field max length and whether the Code step needs to
  truncate before sending (silent truncation is fine; a hard Sugar validation error on a real
  lead is not — confirm which happens today).
- **Auth ID**: this Zap's SugarCRM step currently uses connection/auth id `65663180`. A prior
  session (2026-08-13) proved a working sandbox connection titled `zapier.chatbot`, numeric id
  `65592413`. Confirm whether `65663180` is that same underlying Sugar user (re-issued
  connection id — fine) or a different connection (needs a permissions check — does it have
  Leads create scope?). One line in Zapier's connection settings, just needs stating either way.
- **`lead_source` value**: confirm it's hardcoded `"Chatbot"` (not user-editable/mappable from
  Tidio) — this value only exists as a valid enum option in SANDBOX Sugar, not production, so
  it must stay hardcoded and this Zap must stay pointed at the sandbox Sugar connection until
  an explicit go-ahead to touch production (not yet given).

## What "done" looks like — bring this back
1. One real Tidio staging conversation run through end to end (not a Zapier step-test replay —
   an actual chat).
2. Paste the raw JSON output of all 3 steps (Trigger, Code, SugarCRM) from that run's task
   history.
3. Confirm in Sugar sandbox: the resulting Lead has a correct `first_name`/`last_name` split,
   a `location_c` that's either a real 2-letter code or genuinely blank (not a false "CA"),
   `lead_source: "Chatbot"`, and no truncation/validation error on `account_name`.
4. State plainly which of Bug 1 / Bug 2 / the auth-id question turned out to be non-issues (if
   any) vs. genuinely fixed, so nothing gets marked done on assumption.

Handing back to Claude Code (architect/advisor role) once you have that — it will re-check the
Sugar record directly (one read call, no re-explaining needed) and either sign off or raise
the next issue.
