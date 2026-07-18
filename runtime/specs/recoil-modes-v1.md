---
version: 0.2.0
status: DRAFT — not yet canon-ratified
---

# Recoil Protocol — Reverse Listening & Deep Recall modes (v0.2.0)

**Status:** DRAFT — defined this session, not yet canon-ratified. Routed for review,
not unilaterally declared final (per the standing canon-collision discipline).

**Changelog:** v0.2.0 (2026-07-17) — chronos-sequencer risk section added; multi-pass
reports now MUST carry a `readOrder` directive, in-place superseded markers, and
always-current cover fields. v0.1.0 — initial two-pass structure.

## Why this exists

The Recoil Report (`runtime/recoil/*.md`, `src/document/screens/RecoilReport.tsx`) already
has a shape: D/E/W signal-delta/Y-gate-shift/confidence/next-steps. What it didn't have was
a defined **pass structure** for how the transcript itself gets read before that shape gets
filled in. Two passes, run every time, in this order:

## Pass 1 — Reverse Listening

Read the transcript **end-to-start**. The point: outcomes (how the call actually landed,
what the other party's closing tone/ask was) are known before cause is examined, which
blocks the common recoil failure mode of rationalizing a weak moment because "it worked out
anyway." Reverse listening extracts:

- The actual close (what was said last, what was asked/committed)
- Working backward, every moment that either supports or contradicts that close
- Flags moments where the conversation's stated trajectory (what it seemed to be building
  toward, heard forward) diverges from where it actually landed (heard backward)

## Pass 2 — Deep Recall

Read the transcript **start-to-end**, normally, but scored against the pre-call expectation
captured in the originating PrepSession/calendar context (the ex-ante receipt) rather than
read cold. Deep recall extracts:

- Signal delta per moment (expected vs. actual, the existing Recoil Report table)
- The single highest-leverage recoil moment (the existing "load-bearing quote" pattern)
- Behavioral pattern repetition (e.g. the existing "verbosity flag, twice" finding)

## Scoring cadence — 1/(call duration)

Both passes sample at a rate of **1 finding-check per (1 / duration_minutes) of transcript**,
i.e. the granularity is the reciprocal of the call length: a 10-minute call gets checked at
a coarser grain (fewer, larger segments) than a 60-minute call would at the same total
finding budget — short calls get fewer, higher-signal segments; long calls get more,
finer-grained ones, but the total review effort stays roughly call-length-invariant rather
than scaling linearly with duration. Concretely: `segment_count = round(duration_minutes / (1 / duration_minutes))`
is the wrong reading of "1/(duration)" if taken as a literal rate — the operative rule
adopted here is simpler and avoids that algebra trap: **segment the transcript into
`max(3, round(sqrt(duration_minutes)))` chunks**, each independently run through both
passes. This is the working definition; flagged for Zach to correct if "1/(duration)" meant
something more literal that this paraphrase missed.

## Chronos-sequencer risk (v0.2.0 — MANDATORY for multi-pass reports)

**The pathogen.** Recoil reports are append-don't-overwrite ledgers: each analytical
pass (base read, overlay, diamond-cut, post-send revision) is a new stratum written
after the last, and earlier strata are preserved rather than rewritten. That
preservation is deliberate — strata are provenance, the audit trail of how a belief
formed. But it means **write order preserves superseded beliefs as live-looking
text.** Any chronological or prefix reader serializes dead state as if it were
current: pass-1 scenario weights that a post-send revision overturned, a conviction
read the second-pass overlay reversed, a follow-up prescription already discharged.

Known chronological/prefix readers this bites:
- `scripts/receipt_lookup.py` (the Detective) — aggregates fields across the ledger
- Task A pre-call generation (`runtime/specs/call-brief-hooks-v1.md`) — reads prior
  reports to scope the next call
- Token-truncated LLM reads — truncation keeps the file **prefix**, i.e. exactly the
  oldest strata, and silently discards the corrections
- Human skims — top-of-file reads left-to-right in write order

This is not a hypothetical: the same pathogen has already bitten this repo twice in
other clothing — the three-way handoff-tracker version drift (CLAUDE.md Handoff
v3.0.0 note: three "latest" versions live simultaneously) and the stale
`_STATE/snapshot.json` open-items that had silently resolved. Append-only memory
plus a naive reader equals confidently wrong state.

**The mandate.** Any recoil report that accumulates more than one analytical pass
(any second stratum: overlay, revision, post-send update) MUST carry all three of:

1. **`readOrder` directive near the file head** — a top-level key placed early
   enough to survive prefix truncation, declaring the authority order explicitly:
   current-state header (`cover`) first, consolidated current state
   (`recapitulation`) second, in-place-revised sections next, and the base-pass
   strata **last, as provenance only**. This is the *anachronistic tread*: the top
   layer is truth, lower layers are how the truth got here. The directive should
   also enumerate `knownSupersededStrata` (what was overturned, by what) and
   `consumers` (who must honor this order).
2. **In-place `[SUPERSEDED — see X]` markers** on every overturned stratum, at the
   point of the dead text itself — not only in the directive. A reader who lands
   mid-file on a superseded finding must hit the marker before the finding. The
   overturned text stays (provenance); the marker makes it unquotable-as-current.
3. **Cover fields maintained in-place as always-current.** `cover`
   (Y-gate/conviction/NCI/headline) is the one section that is *overwritten*, never
   appended — it is the current-state header every reader may trust without
   archaeology. If a later pass changes the read, the change lands in `cover` in
   the same write that adds the stratum.

**Reader-side rule (mirrored in `call-brief-hooks-v1.md`):** read
`cover`/`recapitulation`/`readOrder`-designated current state FIRST; never quote a
stratum without checking it for a superseded marker.

**Worked example:** `runtime/recoil/generated/2026-07-17-chan-suh.json` — top-level
`readOrder` with directive/knownSupersededStrata/consumers, `[⚠ SUPERSEDED — …]`
markers inline (e.g. the callWalk seg-7 "cooler than Mike" divergence, overturned by
the second-pass nonverbal overlay), scenario weights revised in-place with explicit
`REVISED 45→55` annotations, and `cover` + `recapitulation` carrying the current
state.

## Output contract

Each pass produces a list of `{ timestamp_pct, finding, pass: 'reverse'|'deep', signal: 'supports'|'contradicts'|'neutral' }`
records. These feed directly into the existing Recoil Report sections:
- Reverse Listening's divergence flags → "Signal Delta Table"
- Deep Recall's load-bearing quote → "Signal Quote" (Sec 01)
- Both passes' chronological findings, merged and time-sorted → "Call Walk" Timeline (Sec 02)
