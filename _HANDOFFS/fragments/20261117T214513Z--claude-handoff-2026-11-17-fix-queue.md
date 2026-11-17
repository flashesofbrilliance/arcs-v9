<!--
session: claude-handoff-2026-11-17-fix-queue
branch: claude/handoff-2026-11-17-fix-queue
head: 41126776
created_at: 2026-11-17T21:45:13Z
-->
## Goal
Clear the 2026-11-17 repo fix queue: merge only what Zach approved, park the rest as reviewable PRs, keep main's gates green.

## Changed
- PR #2340 merged (44e26e57): 11-16 night-moves digest; receipt 2026-11-17--night-moves-digest-pr2340--ZH.
- PR #2341 merged (41126776): reading_room_sync on main, stale-refresh wiring, project_mirror.sh; gate chain public words for 1fb74fe4 and 38cc17ce (Zach's Pair A each), claims scope reviewed; receipt 2026-11-17--reading-room-sync-pr2341--ZH.
- PR #2342 opened (ready): meta-audit and safe_merge descriptions carry the user's words; recall fixtures 3/3 incl. a new safe_merge one; DONE row project-mirror-nightly fixes main's ORPHAN-TOOL failure.
- PR #2343 opened (draft): triage cliffs fated on Zach's answers; row triage-cliffs-2026-11-19-20 DONE inside it.
- PR #2323 rebased onto main; description now explains why #2293's merge commit is not on main (2293 retargeted onto 2290's branch 14 min after 2290 merged, then merged there).
- PR #2272: commented @dependabot rebase; its gauntlet-log axe failure was already fixed on main in de2ad62a.
- G53 applied: branch.autoSetupMerge removed from .git/config (global true now governs). git worktree prune cleared six dead entries (night-moves 11-13, 11-14 and four scratchpad ones). ~/Claude/wt-reading-room-sync removed.

## State
- main fails universe_jtbd_adapter --check (ORPHAN-TOOL project_mirror.sh) until #2342 merges; #2343's CI depends on that.
- Step 4 needed no PR: all 19 jobs-pipeline commits (incl. the board defaults, Boston/NYC boards and job-search records) are already in #2335.
- #2335 is the agreed first-lander over #2338, but neither has merge approval; #2338 rebases and regenerates the forge ledger and bundles after #2335 lands.
- prl-phase-1-2 ORPHAN-JOB hold renewed to 2026-12-01 (Zach asked 2027-02-01; the gate caps holds at 14 days).

## Decisions
- Zach, 2026-11-17: merge #2341 and #2340 only; #2335 lands before #2338; keep the stripe plugin; apply G53; leave sharp-turing parked.
- Zach, 2026-11-17: good-agent-files, agent-readable-arcs-hosts, prl-phase-1-2 DONE; nftt-every-mistake-became-a-gate and paid-brief-first-dollar re-dated 12-01; proposal_construction.py gets a DONE row.

## Open
1. Zach: merge #2342 (restores main's jtbd-graph gate), then #2343.
2. Zach: merge go for #2335, then #2338 rebase plus regenerate.
3. Zach: review #2323; watch #2272 after Dependabot's rebase.
4. prl-phase-1-2 hold falls due 2026-12-01 again; a tool atom for the Zapier/Tidio work would end the renewals.

## Next action
Merge #2342 with scripts/safe_merge.sh so main's jtbd-graph gate is green again.

## Cold-start
- gh pr list --state open
- python3 scripts/universe_jtbd_adapter.py --check
- python3 scripts/backlog_graph.py --top 15
