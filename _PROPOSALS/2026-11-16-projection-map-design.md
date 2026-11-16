---
title: Projection map, design brief
pr: TBD
status: PROPOSED (PR open, not merged)
---

# Projection map

## Why
Zach asked whether signature reads of his calls were evidence or vibes. Judged reads had one coder
and no agreement check. This tool counts instead, then checks the judged part with two blind coders.

## What
A stdlib Python pipeline over Granola transcripts, code only (private data stays in a gitignored
`projection-data/` folder):
- `extract.py` pulls exact transcripts from fetch-only helper logs and checks each against Granola's
  own character count.
- `projection.py` scores each call: talk share, questions, uptake, and the Laconic and Grug circuit
  breakers (mid-curve = both on one turn).
- `pool.py` pools by audience with pre-registered verdicts and within-audience permutation tests.
- `outcome.py` labels a call advanced when a later recorded call shares a name or company token.
- `ACCUMULATION.md` is the protocol (an ADR-081 attractor-basin instance): basin states, a frozen
  discovery/test line at 2026-11-16, and the candidate ledger.
- Three `_MEMORY/` files bank the findings and method lessons for import into live memory.

## Requirements
- No transcript, name or result enters git (folder `.gitignore` admits code and docs only).
- Every test is pre-registered before it runs; reversals are logged in the ledger, never erased.
- Patterns found in the discovery set promote only on calls after the frozen line.

## Implementation plan and state
Built and run on 114 calls (113 locally after one transcript was deleted for card details).
Next: score each verified call after 2026-11-16 with both streams and update the ledger.

Full spec: `tools/projection-map/README.md` and `tools/projection-map/ACCUMULATION.md`.
