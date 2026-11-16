<!--
session: status-release-notes-91254f
branch: claude/status-release-notes-91254f
head: 0baa2968
created_at: 2026-11-16T18:29:25Z
-->
## Goal
Keep the merge queue and the backlog honest: paperwork matches what merged, rankings lead with work Zach is actually doing, and the harness reports stay fresh.

## Changed
- PR #2311 merged (0baa2968, jobs intake unstall, two seed resumes); receipt 2026-11-16--jobs-intake-unstall-pr2311--ZH.
- 300 PRs merged 2026-11-02 to 11-16 (53 in the last 24h); release notes and status report given in session status-release-notes-91254f.
- Backlog sweep, 23 rows: pr-design-brief-habit and gauntlet-brief-polyform RUNNING to DONE (PRs #2148, #2141 merged 11-12); the 7 READY filing-* rows to HELD on Zach's ruling; 14 ripe OPEN rows to READY (dependencies done or date trigger passed).
- Kit catalyst ledger synced (31 derived events appended), kit-periodic-table.html regenerated.

## State
- Open PRs: 2312 status milestones (checks were pending); 2272 Dependabot axe 4.14 (fe-smoke red on a stale 11-15 run, only failure is gauntlet-log.html, fixed on main by #2288; needs a rebase); 2248 (one conflict in the generated kit-periodic-table.html, regenerate); 2214 (five real conflicts incl. scripts/safe_merge.sh and AGENTS.md, owner should resolve); 2222 (fe-smoke red, build not run); 2073 and 2068 drafts (2068 is based on the merged feat/myally-step1-checklist branch, retarget to main before review); dreaming passes 10 to 13 (2221, 2260, 2267, 2276) and night-moves 11-12 (2247) drafts, ruled through a one-form picker in this session.
- Backlog: OPEN 56, READY 33, HOLDING 54, HELD 137, RUNNING 3, BLOCKED 11, DONE 177.
- Cruise-control agent ran for the first time (read-only morning sweep). Approvals ledger: no PR carries a traced approval.
- Sessions: 3 running, about 12 idle with merged PRs not archived.
- Session kind-perlman-3d4858 has an unmerged stale-refresh runner on branch claude/kind-perlman-3d4858 (lattice countables, universe emit, night-moves age as receipts), schedule not installed, row stale-snapshot-refresh-loop HOLDING on Zach.

## Decisions
- Zach, 2026-11-16: merge PR 2311.
- Zach, 2026-11-16: not yet ready to patent; hold the filing chain until after the core engine and subsequent phases.
- Zach, 2026-11-16: sweep merged-PR paperwork and ripe rows in one pass.

## Open
1. Zach: T1 from dreaming pass 13 is urgent: 32 JTBD triage holds expire 2026-11-17 and CI gates then fail on every branch. Re-date or give them job rows.
2. Zach: rule the dreaming picker (safe_merge L1/Q1/T2 as one change, bash 3.2 F1, N1, N2, L2) and the fate of the five draft PRs.
3. Zach: My Ally unpaid discovery is 33.6 to 47.4 h against a 10 h cap: bill, box or stop.
4. Zach: comment @dependabot rebase on 2272 so fe-smoke reruns on current main.
5. Zach: confirm week 1 of _ARTIFACTS/week-plan/gravity.json; settle the Gravity date seams (RFP-O-Matic 10-30 vs 11-02, NFTT 09-02 vs 08-18).
6. Findings gait: no finding closed in 7 beats; give the oldest open finding a fate.
7. Correction (kintsugi): the status report said 41 rows were already done. Only 2 cited merged PRs (gates-class-prevent-leak-and-render-drift, compounding-model-prereg) and both notes name remaining work, so they stay open; the other 39 were ripe, not done.
8. Doors left OPEN on purpose in the sweep: cia-technical-screen-prep, cia-recoil-close-michael-intro, rfp-ship-resume-tailor-rebase, rfp-ship-public-leak-gate, rfp-ship-packages-publish, myally-step1-audit.

## Next action
Zach rules T1 (triage holds expiring 2026-11-17) before end of day; everything else can wait for the next batch merge.

## Cold-start
- gh pr list --state open; python3 scripts/approvals_ledger.py
- python3 scripts/backlog_graph.py --top 15
- python3 scripts/open_loops.py --summary
- _PROPOSALS/2026-11-16-dreaming-pass-13.md (T1)
