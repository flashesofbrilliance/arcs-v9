---
version: v0
status: PROPOSED (prototype, not scheduled)
date: 2026-10-04
seed: seed-pipeline-press-run (oracle seed n=1)
governed_by: ADR-084 (reliance, not trust), ROM primitive 1 (NOTOMATION)
script: scripts/press_run.py
---

# Press run v0: a weekly go/no-go digest

From a 2026-10-04 brainstorm with Zach.

## Rule

Schedule the staging, never the publishing. A run gathers, checks and stages. Only Zach's go
publishes anything. The script has no publish, post, deploy or `public/` write path.

## What a run does (proposed cadence: Tuesday 7am, not yet scheduled)

1. Reads every draft manifest in `_QUEUE/press/<id>.json` (source path, preview result, review result,
   optional `linkedin: true`).
2. Re-runs the honest check on each source. v0 uses the repo's mechanical gates: `slop_lint.py`
   (cliches, em-dashes) and `provenance_lint.py` (every metric cites evidence). Per ADR-084 this is
   what the check can be relied on for; it never checks whether a claim is true.
3. Classifies each draft: READY (preview + review + honest check pass, fresh), HELD (honest check
   fails), STALE (over the freshness ceiling), NOT_READY (no passing preview or review).
4. Stages under `_STATE/press-run/`: a one-page digest `<date>.md` with a blank go/no-go per item,
   one draft receipt per item `<date>.receipts.jsonl` (decision left null, receipt form of AGENTS.md),
   candidate public-trail rows `<date>.trail.json`, and one run row appended to `runs.jsonl`.
5. Every run files its run row, including a run where the queue is empty or nothing is ready.

## Freshness ceiling

The clock ticks in runs, not days. A draft reviewed more than N runs ago (default 3, `--ceiling`) is
STALE: re-review it or retire it. It never ages silently into READY. This is the pipeline instance of
backlog item `freshness-zeno-ceiling` (an upper bound on how long a check stays good); that item's
falsifier still governs the ADR-level version.

## Public honesty trail (not built)

`<date>.trail.json` holds dated rows: what passed the honest check this week. Rendering them on
honest.arcs.care is ADR-084 applied to the pipeline, and is a public-page change: it waits for Zach's
explicit ask. The trail states only "passed the mechanical check on <date>", never "true" or "trusted".

## LinkedIn feed

READY drafts marked `linkedin: true` are listed in the digest as next week's sources. The run never
writes `_QUEUE/linkedin/`; cuts are drafted by hand and gated by `scripts/linkedin_cut.py` as today.

## Not done, needs Zach

- Creating the scheduled task (Tuesday 7am).
- Any change to `public/honest.html` or another public page.
- Choosing the ceiling (3 is a placeholder, not calibrated).
- Whether the honest check should also call the browser tool's rule set or `tools/arcs-verb-eval`.

## Kill condition

Withdraw if after 6 runs no READY item was ever published within a week of staging (the digest is
being ignored), or if more than half of STALE flags are re-reviewed with no change (ceiling too tight).
