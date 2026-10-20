# Throughput pre-registration: does the new session approach move more per unit cost? (2026-10-20)

Backlog row `throughput-baseline-2026-10-20`. Written before the open-loops sweep (the first parent run
under the new rules) reports anything. Rules change only by a dated amendment.

## The new approach being tested
From memory `fanout-token-retro-route-children-cap-the-parent` and `every-spawned-session-gets-a-backlog-row-first`:
cheaper models for mechanical children; cap a parent at 2 workstreams or 3 sprints, then hand off;
check for a live session before spawning; one owner per shared file per day; set a row DONE inside the
PR that finishes it; select before inserting a receipt; every session works a backlog row.

## Metrics (fixed now)
1. **Rows closed with evidence per day**: backlog rows that reached DONE that day with a merged PR or
   receipt named in status_note.
2. **Receipts per closed row**: receipts whose job_id names the row, counted for rows closed that day.
   Lower is better (1 is the floor: one merge, one receipt).
3. **ID coverage**: share of the day's receipts carrying both job_id and tool_id.
4. **Plan cost**: the weekly all-models percent used, read from the session usage tool, per closed row.

## Baseline (2026-10-20, old approach, JTBD framework parent session)
- Rows closed with evidence: 10 (accountant-weekly-first-unattended, jtbd-graph-s4-retrieval,
  jtbd-graph-hook-invocation-edges, reconcile-mechanical-2026-10-20, catalog-regen-five-findings-2026-10-20,
  receipt-job-tool-in-safe-merge, jtbd-architecture-note, compost-three-oldest-operators-2026-10-20,
  decision-receipt-append-only, jtbd-graph-s6-mcp-tools).
- Receipts that day: 78, of which 23 carry both ids (29%) across 12 distinct jobs.
- Merged PRs that day, all sessions: 79.
- Plan: weekly all-models 81% used at 2026-10-20T18:08Z, resetting 2026-10-23T09:00Z; 5-hour window 70%.
  The parent session held about 680,000 tokens of context.
- Known rework that day: repair PRs, separate row-DONE PRs (about 8), a replaced session (139 messages),
  three colliding allowlist PRs.

## Comparison window and verdict rule
- Window: 2026-10-21 to 2026-10-27, read in the Monday 2026-10-27 drift report.
- The new approach "moves more" if, over the window, receipts per closed row is below today's ratio AND
  ID coverage is at least 80% AND rows closed per weekly-percent spent is higher than today's
  (10 rows on the day's share of the week; the day's share is measured from the usage tool at day start
  and end from 2026-10-21 on).
- If the plan cap stalls work before the window ends, report that as a result, not a missing value.
- Caveat stated now: 2026-10-18 shows 182 receipts, most likely a bulk import; it is excluded.
