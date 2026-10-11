<!--
session: claude-handoff-salvage-epics
branch: claude/handoff-salvage-epics
head: 833a2395
created_at: 2026-10-11T02:40:37Z
-->
> Salvaged the main-checkout WIP, ran the epic migration onto GitHub milestones, triaged every unmilestoned issue, measured Actions spend against real billing, and cut the biggest cost (the WCAG ratchet) by scoping it per PR. Memory index compacted to 17.1KB.

## Shavasana
- Mechanical: canary GROUNDED, no thin air; sycophancy OK (dissent present); exhale reads 0 only because it is scoped to this fresh handoff branch (session merged #1169, #1227, #1260).
- Attachment release: kept all claims; the #1260 saving is listed as unmeasured (Open 3), not as achieved.
- Somatic: not asked. Disposition: release.

## Goal
Close the 2026-10-10 salvage, give the backlog an epic structure on GitHub without moving the SSOT, and stop paying for Actions waste without weakening accessibility.

## Changed
- #1169 merged (`ebcceb6a`): carried `_QUEUE/epic-migration-plan.md` + the v3.67.0 SKILL.md changelog line from salvage commit b5c41786; everything else STALE or STATE. Receipt 2026-10-10--salvage-carry-epic-plan-pr1169--ZH
- #1227 merged (`d494d6b3`): 10 milestones; 51 OPEN/RUNNING backlog rows mirrored to issues #1175-#1225 via `scripts/backlog_issue_sync.py` (JSONL stays SSOT); 97 issues milestoned. Receipt 2026-10-10--epic-migration-milestones-pr1227--ZH
- Triage (no PR): closed 7 stale [backlog] mirrors (#580-584, #588, #589), milestoned 22 debt/bug issues, cross-linked 5 debt twins. Receipt 2026-10-10--triage-29-unmilestoned-issues--ZH
- #1260 merged (`833a2395`): WCAG ratchet scoped to changed pages on PRs, full sweep nightly (`.github/workflows/a11y-nightly.yml`). Receipt 2026-10-11--a11y-ratchet-pr-scope-pr1260--ZH
- #1046 comments: run rate, per-job minutes, real billing (Oct 1-11: arcs-v9 8,999 min, net $42.18; included minutes gone Oct 5)

## State
- Every open issue has a milestone. M3 (job search) due 2026-10-15.
- Progressive-handoff rows for head 44ed0c88 marked claimed (237 rows). Salvage branch kept.
- Memory: new feedback `accessibility-is-service-design-not-cost-line`; index 21,063B -> 17,079B, all 319 slugs kept, 11 hooks moved into their files.

## Decisions
- Epics: plan defaults 1-4; JSONL stays the SSOT (ADR-065), only OPEN/RUNNING rows synced (Zach).
- WCAG gate: change when pages are checked, never whether (Zach: accessibility is 2026 design best practice).

## Open
1. Zach: spending limit on Actions (Settings > Billing > Budgets) is unread.
2. Zach: drop the gh `user` scope when done (`gh auth refresh -h github.com -r user`); a suspended `gh auth refresh` job may still sit in terminal tab c1.
3. Measure fe-smoke minutes on the first non-shared code PR after #1260; confirm the first nightly a11y run (07:41 UTC) is green; then decide on closing #1046.
4. Epic plan's 5 decisions are answered; retired-model row old-anthropic-callers-moved is BLOCKED, so it has no issue.
5. ADR-078 has a file but no `_DECISIONS/index.json` row (integrity gate WARN).

## Next action
Check the 2026-10-11 07:41 UTC a11y-nightly run and one post-#1260 code PR's fe-smoke time, and post both on #1046.

## Cold-start
- `gh run list --workflow a11y-nightly.yml -L 3`; `gh issue view 1046 --comments`
- Billing: `gh api "users/flashesofbrilliance/settings/billing/usage?year=2026&month=10"` (needs `user` scope)
- Milestones: `gh api repos/flashesofbrilliance/arcs-v9/milestones`
