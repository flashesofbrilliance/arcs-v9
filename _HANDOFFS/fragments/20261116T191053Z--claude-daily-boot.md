<!--
session: status-release-notes-91254f
branch: claude/daily-boot
head: ae6976c3
created_at: 2026-11-16T19:10:53Z
-->
## Goal
Keep the merge queue and the backlog honest, and give every thread the same boot so cadence does not depend on memory.

## Changed
- PR #2318 merged (e4a5e36b): 32 JTBD triage holds and the anthropic-spend-monitor blocker re-dated from 11-16/11-17 to 11-30; receipt 2026-11-16--triage-holds-redate-pr2318--ZH.
- PR #2319 merged (ae6976c3): TRIAGE-DUE-SOON warning, scripts/kit_sync_refresh.sh, bash 3.2 and file:// guard hooks, ship_docs title default; receipt 2026-11-16--dreaming-picks-build-pr2319--ZH.
- Draft PRs #2221, #2260, #2267, #2276 (dreaming passes 10 to 13) and #2247 (night-moves 11-12) closed on Zach's ruling, picks applied.
- Main checkout moved to origin/main (ae6976c3); both new hooks seen denying live.
- Daily boot: scripts/daily_boot.py, called by the session-start hook (this PR).
- Memories banked: ripe-is-not-done-read-each-loop-tag, git-rev-parse-short-takes-one-rev, plus notes on the axe-upgrade and long-inline-shell memories.

## State
- Every session now starts with a boot block: the first session of the day is told to run /scrum then the cruise-control sweep; every session gets today's one thing (now recoil-brian-ssot), and the claim-a-row, flip-DONE-in-the-feature-PR, archive-on-merge and 4-session rules.
- Patent-filing chain composted (23 rows); backlog depth 6 waves.
- Open PRs: 2312 status milestones, 2272 Dependabot (needs @dependabot rebase; its red fe-smoke predates the gauntlet-log fix), 2248 (one generated-file conflict; scripts/kit_sync_refresh.sh fixes it), 2214 (five real conflicts, owner resolves), 2222 (fe-smoke red), 2073 and 2068 drafts.

## Decisions
- Zach, 2026-11-16: compost the patent-filing chain.
- Zach, 2026-11-16: build the dreaming picks (T1b, T2, F1, N1, N2, L2); close the five drafts; L1 and Q1 not picked.
- Zach, 2026-11-16: a daily boot sequence on every thread.

## Open
1. Zach: row triage-cliffs-2026-11-19-20 (READY, trigger 2026-11-18): the prl-phase-1-2 hold expires 11-19 and five blocker dates fall due by 11-20.
2. Zach: My Ally unpaid discovery over its 10 h cap: bill, box or stop.
3. Zach: @dependabot rebase on 2272; retarget 2068 to main before review.
4. Zach: confirm week 1 of the Gravity week plan; settle the Gravity date seams.
5. Candidate agents: graduate cruise-control, chief-loki, scrum-master; compost or fold chief-bayesian, chief-conductor, claim-index-sme and the four idea-* seats (0 uses since 10-20).
6. The 35 unaudited operators: adopt them as the first audit step of the core engine work.

## Next action
Next session: follow the boot block, then work triage-cliffs-2026-11-19-20 before 11-19.

## Cold-start
- Read the boot block the session-start hook prints.
- gh pr list --state open; python3 scripts/approvals_ledger.py
- python3 scripts/backlog_graph.py --top 15
- python3 scripts/universe_jtbd_adapter.py --check (TRIAGE-DUE-SOON lines)
