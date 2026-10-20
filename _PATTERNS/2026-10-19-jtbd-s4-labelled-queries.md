# JTBD graph s4: labelled query set (TEMPLATE, labels not yet written)

Status: DRAFT. Not valid as a gate until Zach fills every `label` cell and the file is committed;
the commit sha that contains the filled labels is the one the s4 run and the /catalog baseline cite.
Rules come from `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md` (s4 section). Nothing here
changes them.

## How to fill it (about 20 minutes)
1. Keep, edit or replace rows 1 to 5. They are verbatim asks from your own recent sessions
   (2026-10-17 to 2026-10-19), picked because they do not name a tool. At least 5 rows must stay real asks.
2. Write rows 6 to 20: jobs you actually have, in your own words. Do not copy a catalog `jtbd` line
   (that leaks the answer to /catalog).
3. For each row put ONE tool id in `label`, using the schema form, for example `tool:script:oracle.py`,
   `tool:command:loops`, `tool:skill:cruft-sweep`, `tool:op:21`. If no existing tool does the job, write
   `none` (both systems are then scored correct only if they say no tool fits).
4. Do not run /catalog or the graph on these before committing. Labels written after seeing either
   system's answer void the gate.

No labels are suggested here on purpose: a label proposed by an agent that has read the catalog is
the contamination the pre-registration guards against.

| # | Source | Job statement | label | tuned |
|---|---|---|---|---|
| 1 | real ask | check if the scheduled ones are hung | | |
| 2 | real ask | check them for half-written state | | 1688 |
| 3 | real ask | molt the handoff fragments now | | 1688 |
| 4 | real ask | I closed a bunch of stuff - check again? | | |
| 5 | real ask | measure landing drag on the last three handoffs (tokens to first useful action, re-derivation count) | | 1688 |
| 6 | Zach | | | |
| 7 | Zach | | | |
| 8 | Zach | | | |
| 9 | Zach | | | |
| 10 | Zach | | | |
| 11 | Zach | | | |
| 12 | Zach | | | |
| 13 | Zach | | | |
| 14 | Zach | | | |
| 15 | Zach | | | |
| 16 | Zach | | | |
| 17 | Zach | | | |
| 18 | Zach | | | |
| 19 | Zach | | | |
| 20 | Zach | | | |

## Tuned rows (amendment 6)
Rows 2, 3 and 5 are marked `tuned: 1688`. PR 1688 rewrote the `/fold` and `scripts/handoff_fold.py`
descriptions after row 2's symptom showed up here. Row 2 is the half-written-state query the amendment names.
Rows 3 and 5 are marked too, to be safe: row 3 (molt) targets handoff_fold.py, whose description changed,
and row 5 (landing drag) matches the words "cuts landing drag" that 1688 added. s4 reports an untuned-subset
score alongside the all-20 score. Any row Zach adds later that paraphrases half-written state is marked the same way.

## Scoring (fixed, for whoever runs it)
- Baseline first: the /catalog procedure at the start sha, a fresh session with only that command and
  `runtime/specs/tool-catalog.json`, one shot per row, same model tier as the s4 run. Map its one
  recommended tool to a schema id; top-1 correct if it equals `label`.
- Early read (2026-10-19 proposal, does not change any threshold): if the baseline scores 18 or more
  of 20, s4 cannot win by a margin worth its upkeep, so s4 and s5 stop and only s3's integrity gates
  are kept. That stop is a choice Zach makes on the number, not an automatic kill.
