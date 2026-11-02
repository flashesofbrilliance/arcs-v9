# Backlog graph, glass box: the facts this video may say

This file is the README for the video (the readme-to-video ceiling). Every figure below was read on 2026-11-02 from
origin/main at `75356eb3`, by running the tools themselves. Raw outputs sit beside it: `graph-2026-11-02.txt`
(`python3 scripts/backlog_graph.py --today 2026-11-02 --top 5`) and `gate-real-2026-11-02.txt`
(`python3 scripts/backlog_status_check.py --check`). The glass box artifact it explains
(https://claude.ai/artifact/QzRVPjLP4MdhZHzZuqL1jN) carries numbers from 2026-10-30; this file supersedes them.

## The five layers

1. Source: `_QUEUE/induced-backlog.jsonl`, 438 rows, one JSON object per line.
2. Gates: `scripts/backlog_status_check.py --check` checks each row's `state` against the enum and that a RUNNING row
   carries `claimed_by` and `claimed_at`. It checks shape, not merit. Exit 1 on any FAIL.
3. Graph build: `scripts/backlog_graph.py`. Nodes are the 320 active rows; edges are `depends_on` plus the inverse of
   `unblocks`. Waves are longest-path depth, 13 waves deep (wave 0 to wave 12). Ties inside a wave go by rank, order,
   priority, id. Read-only, standard library, no model calls; two runs on the same file gave byte-identical JSON.
4. Outputs: 11 rows are ready now (wave 0, a startable state, trigger RIPE, no dead or missing dependency). Tool fit
   labels: HAVE 112, PARTIAL 8, NOT-RESOLVED 183, NONE 17. Findings: dangling 0, dead dependency 0, cycles 0,
   unblocks mismatch 0.
5. Fate: a person. The script never changes a row. Fates stay human (NOTOMATION).

Rows by state: OPEN 178, READY 17, HOLDING 71, HELD 37, RUNNING 13, BLOCKED 4, DONE 94, COMPOSTED 19, SUPERSEDED 5.
DONE, COMPOSTED and SUPERSEDED (118 rows) are terminal and leave the graph. Active rows per wave, wave 0 to 12:
224, 35, 16, 8, 6, 5, 5, 4, 5, 4, 4, 3, 1.

## The row the video follows

Line 99, `doc-gate-false-positive-cleanup`, state OPEN. Job: "Clean the existing false positives the 4 doc gates
report (e.g. _ARCHIVE/handoffs.md unmerged-SHA citations) so a blocking switch would not red every PR."
`depends_on`: `doc-gates-advisory-ci` (DONE). `doc-gates-blocking` (HOLDING, wave 1) depends on it. Fates: landed,
withdrawn. Graph output: wave 0, ripeness RIPE, tool HAVE, tools `scripts/integrity_gate.py`,
`scripts/integrity_gate_selftest.py`, `canon_propagation_check.py`, tier cue 2, ready now. It is one of the 11.

On a test copy with the row set to RUNNING and no claim, the gate printed:

    FAIL  line 99 doc-gate-false-positive-cleanup: RUNNING requires `claimed_by`
    FAIL  line 99 doc-gate-false-positive-cleanup: RUNNING requires `claimed_at`

and exited 1. On a test copy with `claimed_by` and `claimed_at` written, the same gate exited 0. That claim wrote
`"claimed_by": "Zach Harris"` and `"claimed_at": "2026-11-02T16:30:00-05:00"`.

## Gaps

- The graph is shallow: 224 of 320 active rows sit in wave 0, and 178 of them have no edge at all, so inside wave 0
  the order is ranking, not dependency. The fix is writing `depends_on` into the rows, not changing the script.
- The refusal and the claim were run on a test copy. The real row is still OPEN and unclaimed.

## Takes and cut (not committed)

Voiced 2026-11-02 on Zach's go: clone "Zach Harris", eleven_v4, one take per card, 1,152 credits, ElevenLabs flow
hzOVu5uWZHazawscVmLr. Takes: `voice/01.mp3` to `voice/08.mp3` (90.88 s), durable copy in
`~/Movies/backlog-graph-glassbox-voice/`. Cut: `~/Movies/backlog-graph-glassbox.mp4`, 97.3 s, checker 0 FAIL 0 WARN,
brand-line-producer PASS. Not uploaded anywhere.
