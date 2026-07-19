---
version: 1.1.0
status: DRAFT — ROM candidate, not canon-ratified
changelog: >
  1.1.0 (2026-07-17) — chronos-sequencer reading discipline added to Task A/B:
  read readOrder/recapitulation-designated current state first, never quote a
  stratum without checking for a superseded marker. 1.0.0 — initial.
---

# Pre-Call / Post-Call Brief Hooks — v1

Governs the two scheduled tasks that automate what was previously a manual
`/recoil-report` run (see the 2026-07-09 Steve LaBella closed receipt for
the reference case this spec generalizes from).

## The two-tier model (do not conflate these)

| Tier | Store | Access | Contains |
|---|---|---|---|
| **Internal ledger** | `runtime/recoil/generated/*.json`, git-tracked | Auth-gated via `/recoil/[reportId]` (Auth.js session required) | Full recoil report: stated-vs-revealed ledger, risk flags, belief shifts, candid pattern analysis |
| **External taste** | `public/<name>.html`, git-tracked | Password-gated only (client-side, weak) | Curated brief tabs a counterpart may eventually see if they have the password |

**Rule:** every call with a transcript writes to the internal ledger, always.
A call only writes to the external taste page if that page **already
exists** — i.e. Zach has already deliberately decided to share a live brief
with this person. Hooks never create a new external page. Publishing a new
relationship to a shared surface is a deliberate act, not an automation.

This distinction exists because the internal ledger's candor (e.g. "declined
help," "urgency gap," stated-vs-revealed critique) is exactly the kind of
content that should never accidentally leak to the person being analyzed —
see the labella.arcs.care precedent, where a stated-vs-revealed ledger is
live behind a password the counterpart himself knows ("steve"). Future
external updates should default to a lighter, curated close-out — not a
verbatim copy of the internal candor — unless Zach has explicitly chosen
otherwise for that relationship (as he did for LaBella).

## The Detective lookup (`scripts/receipt_lookup.py`)

Before any pre-call brief is generated, run:

```
python3 scripts/receipt_lookup.py "<counterpart name or email>"
```

This scans the internal ledger for prior calls with this person and returns:
NCI trend, Y-gate trend, unresolved HIGH-severity risk flags, and a plain
advisory (e.g. "prior call showed a structural blocker — confirm it's
changed before allocating more time"). This is the missing piece flagged in
the 2026-07-09 session: nothing previously queried history before spending
call time. It is deliberately advisory, not a gate — it surfaces the pattern,
it does not block the call.

The Detective honors the chronos-sequencer discipline (below): it reads each
report's `cover` (always-current) for NCI/Y-gate, surfaces `recapitulation`
where present, and skips risk flags carrying a superseded marker rather than
re-serializing overturned strata as live findings.

## Reading prior reports — chronos-sequencer discipline

Ledger files are append-don't-overwrite: later analytical passes correct
earlier ones without deleting them, so a chronological/prefix read serializes
superseded beliefs as live text (full definition and the authoring-side
mandate: `runtime/specs/recoil-modes-v1.md` §Chronos-sequencer risk; worked
example: `runtime/recoil/generated/2026-07-17-chan-suh.json`). Whenever Task A
or Task B (or any hook, or any human) reads a prior report:

1. **Read the designated current state FIRST**: the `readOrder` directive if
   present, then `cover` (always-current header) and `recapitulation`
   (consolidated final state). Only then descend into strata, and only as
   provenance.
2. **Never quote a stratum without checking it for a superseded marker**
   (`[SUPERSEDED — see X]` or the `⚠ SUPERSEDED` inline form). A finding,
   scenario weight, conviction read, or prescription from a stratum is
   quotable only after confirming no later stratum or marker overturned it.
3. If a report predates the `readOrder` mandate (no directive present),
   treat everything outside `cover` as potentially stale and prefer the
   newest report's `cover` over any older report's body.

## Task A — Pre-call brief poller

**Cadence:** recurring, every 15 min, weekdays business hours (jitter is
fine — this is advisory, not time-critical to the minute). Because the
window is ~20 minutes and the cadence is 15 minutes, **the same event will
be seen by 1–2 consecutive firings.** Step 3 below exists specifically to
stop that from producing duplicate work — do not skip it.

**Canonical slug rule (fixed, not free-form):** the slug is the lowercased
local-part of the external attendee's email address (the part before `@`),
with `.`, `_`, and `+tags` collapsed to single hyphens — e.g.
`james.trainor@fox.com` → `james-trainor`. If more than one external
attendee, use the first non-internal one, in attendee-list order. This is
the *only* slug-generation rule. Do not derive a slug from the calendar
title or invent one per run — doing so is what caused a real duplicate on
2026-07-13 (`precall-james-trainor-2026-07-13.json` and
`precall-trainor-2026-07-13.json`, same person, same call, two separate
firings, two free-formed slugs, neither firing checked for the other).

**Procedure per firing:**
1. List calendar events starting in the next ~20 minutes.
2. Filter to events with exactly one external attendee (not @gmail.com
   internal, not a known non-1:1 domain) — or any event Zach has tagged
   `[ARCS]` in the title, whichever is broader at the time this runs.
3. **Idempotency check (do this before any lookup or API call):** compute
   the canonical slug for the event, then check whether
   `runtime/recoil/generated/precall-<slug>-<date>.json` already exists.
   If it does, this event was already handled by an earlier firing —
   **skip it entirely**: no Detective lookup, no file write, no
   notification for this event. This check must run before step 4 (the
   Detective lookup), since the lookup is the expensive/token-costing step
   this whole check exists to avoid repeating.
4. For each surviving match: run `scripts/receipt_lookup.py` against the
   attendee's name/email. If this step (or any enrichment beyond the
   Detective digest) opens a prior report file directly, apply the
   chronos-sequencer discipline above: `readOrder`/`cover`/`recapitulation`
   first, no stratum quoted without a superseded-marker check.
5. Write an internal pre-call note to the ledger convention
   `runtime/recoil/generated/precall-<slug>-<date>.json` — reusing the
   `RecoilReportData` shape's `meta`/`cover`/`loadBearingQuote` fields at
   minimum; full segment/protocol fields are optional pre-call (no
   transcript exists yet). Always include `meta.calendarEventId` (the
   calendar event's `id` field) — this is the durable dedup key once more
   than one event per day per counterpart becomes possible (recurring
   counterparts, rescheduled calls).
6. If an external brief page already exists for this counterpart
   (`public/<slug>.html`), do **not** auto-edit it. Note that fact only.
7. Notify Zach (push notification, not email — this is internal-only
   output) with the digest: who, when, what the Detective lookup found.
8. If no calendar events match after the idempotency filter, do nothing
   and end the run silently — do not notify on a no-op tick, and do not
   notify just because every match was a dedup-skip.

## Task B — Post-call recoil + close poller

**Cadence:** recurring, every 20–30 min, weekdays business hours.

**Procedure per firing:**
1. List calendar events that ended in the last ~90 minutes with exactly
   one external attendee.
2. Match each to a Granola meeting by title/attendees/end-time proximity.
3. **Idempotency check:** using the same canonical slug rule as Task A,
   check whether `runtime/recoil/generated/<date>-<slug>.json` already
   exists for this event. If it does, this call was already closed out by
   an earlier firing (the 90-minute window means up to ~4 firings can see
   the same ended call at a 20-min cadence) — skip it entirely, no
   re-transcription, no re-write, no notification.
4. If no transcript is available yet, skip silently (it may appear on a
   later tick — Granola processing lag is normal).
5. If prior reports for this counterpart inform the read (scoring against
   ex-ante expectation, belief-shift continuity), apply the
   chronos-sequencer discipline above when reading them — current state
   from `cover`/`recapitulation`, strata as provenance only.
6. Run the full `/recoil-report` procedure (`runtime/specs/recoil-modes-v1.md`):
   segment count `max(3, round(sqrt(duration_minutes)))`, Reverse Listening
   + Deep Recall passes, merge into `RecoilReportData`. If the report will
   accumulate multiple passes, it MUST carry the `readOrder` directive,
   in-place superseded markers, and always-current `cover` per that spec's
   chronos-sequencer mandate.
7. Include a stated-vs-revealed section explicitly (this is now a standard
   part of the merge, not optional — see the LaBella report's ledger
   section as the template).
8. Write the result to `runtime/recoil/generated/<date>-<slug>.json` and
   commit it. **This step is fully autonomous — no review gate** (per Zach's
   2026-07-09 decision: auto-close immediately). This is the internal
   ledger; low blast radius if imperfect, since only Zach's authenticated
   session can read it.
9. If an external brief page already exists for this counterpart AND
   already has a pre-call receipt / close-out block (the Tab 4 pattern),
   refresh that page's close-out block with a **curated** version — verdict,
   Y-gate, next action, one-line belief shift — not the full internal
   candor. Commit and deploy via `scripts/deploy-prod.sh` per the standing
   worktree rule (main worktree only). If no such page exists, skip this
   step entirely.
10. Notify Zach (push notification) with a one-line summary: Y-gate
    delta, NCI delta, and whether an external page was updated.

## What this does NOT do

- Does not auto-send any email or message to the counterpart.
- Does not create a new public brief page for someone who doesn't have one.
- Does not gate or block a call from happening based on Detective history —
  advisory only.
- Does not replace `/recoil-report` as a manually-invokable skill; the
  scheduled tasks call the same procedure, they just remove the "remember
  to run it" step.

## Known constraints (tell-forward, don't rediscover)

- Scheduled tasks (`mcp__scheduled-tasks`) only fire while the Claude Code
  app is open — if closed at fire time, the task runs on next launch, not
  retroactively for a missed window. If a call happens while the app is
  closed, its recoil report simply won't auto-generate; run `/recoil-report`
  manually to backfill.
- `CronCreate` (session-only, 7-day auto-expiry) is the wrong tool for this
  — durable `scheduled-tasks` is correct since this needs to survive across
  sessions.
- Each scheduled task run starts with zero memory of any prior conversation
  — the task prompt must be fully self-contained (this spec exists so the
  prompt can point here instead of re-deriving the procedure each time).
- **Dedup is not automatic — each run must actively check for it** (added
  2026-07-15, after a real duplicate: two firings 15 min apart both matched
  the same 2026-07-13 James Trainor call, and because neither run checked
  for an existing note before doing work, both ran a full Detective lookup
  and wrote a separate file under a differently-freeformed slug
  — `james-trainor` vs `trainor`. Zero memory across firings means the
  idempotency check has to be a filesystem check (does
  `precall-<slug>-<date>.json` already exist), not a "remember I already
  did this" check — see the canonical slug rule + step 3 in Task A and
  step 3 in Task B above).
