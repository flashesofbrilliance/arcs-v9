<!--
session: 22d2d282
branch: claude/myally-email-access-concerns-5dd89f
head: 3f9b9f90
created_at: 2026-11-15T19:10:24Z
-->
## Changed
- PR 2232 merged (2fe62730): design-candidate lane (scripts/design_candidates.py, runtime/specs/design-candidates.json, read by token_source_gate, motion_policy_gate and component_source_gate, plus pre-commit). PR 2235 merged (ec7b02ed): backlog row design-candidate-lane and tool catalog.
- PR 2227 merged (8a7d3919), receipt 2026-11-13--option-board-pr2227--ZH. PR 2244 closed unmerged as superseded by PR 2243 (866de431).
- PR 2218 merged with receipt (status page rebuild).
- PR 2262 merged (73b3042a, by the busy-kirch session, receipt filed there): the ARCS Field OS wordmark takes its name from visible text on blacksmith, growth-ai, mercury-operator and sentilink-operator, which clears axe 4.14 rule label-content-name-mismatch.
- My Ally receipts: closeloop (call moved to next week, 7-day sign NO) and ex-ante sign-before-kickoff (review 2026-11-19).
- Memory banked 2026-11-15: axe-upgrade-flags-old-defect-fix-on-main-then-rebase, fe-smoke-single-runner-fixed-ports, and a bash 3.2 guard section in long-inline-shell-goes-in-a-script-file.

## State
- PR 2224 is CLOSED; Dependabot regrouped the axe-core 4.14 bump into PR 2272 (open), whose fe-smoke run is the real proof of the wordmark fix.
- fe-smoke runs only on runner arcs-mac: fixed container arcs-ci-pg-ci, port 55432 and port 3000; arcs-mac-2 and arcs-mac-3 share the same Mac.
- Design-candidate registry is empty.

## Decisions
- Zach, 2026-11-14: fix the wordmark on main rather than raise the a11y baseline.

## Open
1. Zach: make fe-smoke parallel-safe (per-runner container name and ports from RUNNER_NAME, then widen runs-on). He said "Yeah make it", then redirected to this sweep; not started.
2. Zach: merge PR 2272 once its fe-smoke is green.
3. Possible duplicate receipt for PR 2227 (2026-11-13--option-board-generator-pr2227--ZH), not reconciled.
4. Remove worktree wt-wordmark-a11y (PR 2262 merged); ask Zach first.

## Next action
Check PR 2272's fe-smoke on axe 4.14; if green, merge it with safe_merge.sh and one receipt on Zach's go.

## Cold-start
- gh pr checks 2272
- .github/workflows/ci.yml around line 212 (fe-smoke)
- python3 scripts/design_candidates.py --list
