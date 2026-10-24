# JTBD graph pre-registration, amendment 6 (2026-10-20)

Amends `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md`, s4 section. No threshold changes.

## What happened
PR 1688 (merge `e371c0fe`, 2026-10-20) rewrote the `/fold` and `scripts/handoff_fold.py`
descriptions to lead with the symptom they fix ("half-written state"), after that symptom showed up
in the s4 query set, and regenerated `runtime/specs/tool-catalog.json`. Both `/catalog` (the
baseline) and the JTBD graph read these descriptions, so this is tuning on the test set for the
queries that name that symptom.

## Rule
1. The baseline stays as written: `/catalog` as committed at the s4 start sha, which includes PR 1688.
2. Every s4 query whose job is "half-written state" or a paraphrase of it is marked `tuned: 1688`
   in the labelled-query file before the first run.
3. s4 reports two scores for both systems: all 20 queries, and the untuned subset. The win
   condition is judged on all 20 as pre-registered; the untuned subset is reported alongside so a
   reader can see whether the tuned queries carried the result.
4. From this amendment on, no tool description may be edited because of an s4 query until s4 has
   been scored. A description fix found during labelling goes in a backlog row for after s4.
