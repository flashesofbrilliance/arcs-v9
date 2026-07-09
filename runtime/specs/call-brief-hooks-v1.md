---
version: 1.0.0
status: DRAFT — ROM candidate, not canon-ratified
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

## Task A — Pre-call brief poller

**Cadence:** recurring, every 15 min, weekdays business hours (jitter is
fine — this is advisory, not time-critical to the minute).

**Procedure per firing:**
1. List calendar events starting in the next ~20 minutes.
2. Filter to events with exactly one external attendee (not @gmail.com
   internal, not a known non-1:1 domain) — or any event Zach has tagged
   `[ARCS]` in the title, whichever is broader at the time this runs.
3. For each match: run `scripts/receipt_lookup.py` against the attendee's
   name/email.
4. Write an internal pre-call note to the ledger convention
   `runtime/recoil/generated/precall-<slug>-<date>.json` — reusing the
   `RecoilReportData` shape's `meta`/`cover`/`loadBearingQuote` fields at
   minimum; full segment/protocol fields are optional pre-call (no
   transcript exists yet).
5. If an external brief page already exists for this counterpart
   (`public/<slug>.html`), do **not** auto-edit it. Note that fact only.
6. Notify Zach (push notification, not email — this is internal-only
   output) with the digest: who, when, what the Detective lookup found.
7. If no calendar events match, do nothing and end the run silently — do
   not notify on a no-op tick.

## Task B — Post-call recoil + close poller

**Cadence:** recurring, every 20–30 min, weekdays business hours.

**Procedure per firing:**
1. List calendar events that ended in the last ~90 minutes with exactly
   one external attendee.
2. Match each to a Granola meeting by title/attendees/end-time proximity.
3. If no transcript is available yet, skip silently (it may appear on a
   later tick — Granola processing lag is normal).
4. Run the full `/recoil-report` procedure (`runtime/specs/recoil-modes-v1.md`):
   segment count `max(3, round(sqrt(duration_minutes)))`, Reverse Listening
   + Deep Recall passes, merge into `RecoilReportData`.
5. Include a stated-vs-revealed section explicitly (this is now a standard
   part of the merge, not optional — see the LaBella report's ledger
   section as the template).
6. Write the result to `runtime/recoil/generated/<date>-<slug>.json` and
   commit it. **This step is fully autonomous — no review gate** (per Zach's
   2026-07-09 decision: auto-close immediately). This is the internal
   ledger; low blast radius if imperfect, since only Zach's authenticated
   session can read it.
7. If an external brief page already exists for this counterpart AND
   already has a pre-call receipt / close-out block (the Tab 4 pattern),
   refresh that page's close-out block with a **curated** version — verdict,
   Y-gate, next action, one-line belief shift — not the full internal
   candor. Commit and deploy via `scripts/deploy-prod.sh` per the standing
   worktree rule (main worktree only). If no such page exists, skip this
   step entirely.
8. Notify Zach (push notification) with a one-line summary: Y-gate
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
