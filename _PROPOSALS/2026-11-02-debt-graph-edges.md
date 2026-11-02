# Debt in the backlog graph: edges and fates to rule on (2026-11-02)

Status: RULED in part (Zach, 2026-11-02: "Accept A and B"). Sections A, B and C are applied; D and E stay open.

## Rulings applied (2026-11-02)

- **A and B accepted.** A `**Depends on.** <row-id>` line was added to the body of issues #966, #1013, #1005, #1000,
  #1019, #1046, #1003 and #995 (the original bodies were saved before the edit). A live `backlog_graph.py --debt`
  run then read all 8 edges with 0 dangling ids: six of the debt nodes moved to wave 1 and two to wave 2, each behind
  the row that clears it.
- **C checks run, all three passed, issues closed with the evidence in a comment:** #993 (main checkout detached at
  `a6938dfa`, a commit on main), #1002 (`session-start.sh` line 161 runs `tool_orphan_audit.py`), #1014
  (status.arcs.care fetches `app.arcs.care/api/pulse`, which served commit `24d4e05` and the Issues debt counts).
  Open debt issues: 21 to 18.
- **E dry run** (`backlog_issue_sync.py --dry-run debt push`): 19 rows would be filed, 16 open (2 of them P1:
  `design-debt-burndown-served-surfaces`, `geometry-feed-500`) and 3 done (filed then closed for history).
  Nothing filed yet; that waits on Zach.
- **E filed (Zach: "File all 19").** `debt push` filed #1960 to #1978 (the 3 done rows filed, then closed). Then
  `debt pull`, and the 22 tracker rows whose status or issue number changed were written to the Docs Reconciliation
  artifact in one atomic batch, each pinned to the version just read. The graph now reads 78 debt issues: 34 open on
  GitHub, 34 active `debt:` nodes, three of them P1 (`actions-minutes-leak`, `design-debt-burndown-served-surfaces`,
  `geometry-feed-500`).
- **Two rows held back, not overwritten:** on the page, `ats-pdf-real-parser-validation` is marked done and
  `librarian-prescore-calibration` in-progress, but both issues (#975, #992) are open with status:decision. The
  pull would set the page back to the issue. Someone changed the page by hand, so Zach decides: close the issue
  (the page was right) or let the next pull reset the page (the issue was right).

`scripts/backlog_graph.py --debt` now reads the open debt issues (GitHub Issues, label `debt`, the SSOT since
2026-10-06) as nodes named `debt:<id>`, read-only. First run, 2026-11-02, on origin/main `24d4e052`:
59 debt issues, 21 open, **0 edges**. All 21 sit alone in wave 0, so the graph shows them but cannot order them or
tie them to the backlog work that would clear them. This sheet proposes the edges and the fates.

How an accepted edge is written: a line `Depends on: <backlog-row-id>` added to the issue body (the graph reads
it; `backlog_issue_sync.py` never rewrites issue bodies, so the line is a human or session edit on Zach's go).
Edges point from the debt to the backlog row whose landing clears it.

## A. Edges: the debt and a backlog row are the same work (5)

| # | Debt issue | Depends on (backlog row, state) | Why |
|---|---|---|---|
| A1 | `debt:accountant-weekly-unproven` (#966, P3) | `accountant-weekly-first-unattended` (OPEN, ready now) | Same job: one unattended weekly run. The row lands, the debt closes |
| A2 | `debt:sharp-render-untested` (#1013, P3) | `sharp-render-real-data` (OPEN) | Same job: first SHARP receipt verified on real data |
| A3 | `debt:prisma-8-rc` (#1005, P3) | `prisma-8-upgrade-plan` (OPEN) | Same job: plan the upgrade when 8.0 is final |
| A4 | `debt:old-anthropic-account` (#1000, P2) | `revoke-old-anthropic-keys` (HOLDING) | Same job: move old-key copies, then revoke. Its "capped until Nov 1" date has passed |
| A5 | `debt:write-lock-adr-085` (#1019, P2) | `merge-train-only-path` (HOLDING) | ADR-085 was re-decided 2026-10-20 (kept PROPOSED, row `adr-085-acceptance-redecide` DONE). What is left is the train as the only path |

## B. Edges: a backlog row would clear or measure the debt (3)

| # | Debt issue | Depends on | Why |
|---|---|---|---|
| B1 | `debt:actions-minutes-leak` (#1046, **P1**) | `ci-orbstack-linux-vm-runners` (READY) | Moving CI to local runners removes the minutes cost. The leak was last measured 2026-10-06 (`gh-actions-billing` DONE fixed billing, not the run rate). Re-measure first; Actions are still enabled on the repo |
| B2 | `debt:outcome-closure-gap` (#1003, P2) | `accountant-external-cohort-nonzero` (HOLDING) | Calibration needs 30 closed receipts per cohort; the external cohort row is where they come from |
| B3 | `debt:nftt-index-build-resync-and-tao-backfill` (#995, P3) | `nftt-story-factory-index-instructions-stale` (OPEN) | Both concern the NFTT index build drifting from the live index |

## C. Close candidates: the work looks done (3). Close only after the check named

| # | Debt issue | Evidence | Check before closing |
|---|---|---|---|
| C1 | `debt:main-checkout-parked` (#993, P2) | Row `tower-d4-main-checkout-moved` DONE 2026-10-19: main checkout moved to origin/main | `git -C /Users/zharris/arcs-v9 status` shows detached at a main commit |
| C2 | `debt:orphaned-tools-session-start` (#1002, P2) | `scripts/tool_orphan_audit.py` exists and `.claude/hooks/session-start.sh` calls it; today's session start printed "tools: 532 wired · 0 available-not-installed · 3 unused · 6 duplicates" | The line printed at today's session start (seen) |
| C3 | `debt:status-page-static-and-two-ledgers` (#1014, P2) | Phase 1 (Issues as debt SSOT) shipped 2026-10-06; `src/app/api/pulse/route.ts` exists on main; row `status-page-public-claims-fix` DONE 2026-10-18 saw live repo numbers | status.arcs.care shows live counts today, not the static floor |

## D. Stay standalone (10): no backlog row does this work

`ats-pdf-real-parser-validation`, `confidence-claim-unit-v1`, `culture-rescore-backfill`, `lattice-regenerate`
(session start still reports lattice drift, 27 days), `librarian-prescore-calibration`, `og-image-unfurl-check`,
`reading-room-lexicon-tenant`, `security-review-rerun-false-red`, `tools-17-unreferenced-scripts` (session start now
counts 3 unused, so it may have shrunk), `tools-nci-scoring-duplicate`. Each stays a wave-0 node; whether any needs
its own backlog row is a separate call.

## E. The tracker artifact is out of date with its own SSOT

The pinned Docs Reconciliation page (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection) shows 78
rows, 36 not done. GitHub has 59 debt issues, 21 open. The 59 filed rows agree with their issues (0 rows open on the
page but closed on GitHub). The gap is the other 19 rows, which were never filed as issues; 16 of them are not done.
Those 16 are debt the graph cannot see, because it reads issues, not the page. Fix:
`backlog_issue_sync.py debt push --rows <dir> --dry-run` lists them, then a real push files them and `debt pull`
refreshes the page. Both write (GitHub, then the artifact DB), so both wait on Zach.

## What the three lenses show once debt is in (same run)

- **Dependencies:** 341 active nodes (320 backlog + 21 debt), 13 waves, 11 ready now; debt adds no order yet (0 edges).
- **Risk:** 153 of 341 rated, 188 unrated. 35 loud rows (ruin high or critical, a one-way door, or debt P1); 44 rows
  inherit a loud row upstream. The six largest exposures are all in the HELD Farcaster cluster (`fc-*`, paused
  2026-10-18), so the live risk picture is the loud rows outside it.
- **Tradeoffs:** 238 of 341 costs can be banded. 35 rows are small cost and unblock others; 103 have no usable cost.

Accepting A and B gives the 8 debt issues an order and ties them to rows the assembly line can run. With C closed,
the open debt issues drop from 21 to 18, and E adds up to 16 that are tracked today only on the page.
