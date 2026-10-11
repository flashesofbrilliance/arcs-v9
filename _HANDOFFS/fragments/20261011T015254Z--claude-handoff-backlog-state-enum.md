<!--
session: claude-handoff-backlog-state-enum
branch: claude/handoff-backlog-state-enum
head: 9d37d2bf
created_at: 2026-10-11T01:52:54Z
-->
> Gave `_QUEUE/induced-backlog.jsonl` a machine-checkable `state` enum with a gate, then closed the three rows the gate flagged as stale.

## Shavasana

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-backlog-state-enum), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 19 / dissent 6 (ratio 2.71) → OK: dissent present.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Attachment release: all claims re-checked against gh/git; none dropped. Somatic: not asked. Disposition: release.

## Goal
Make backlog status countable and stale claims detectable, without losing any prose history.

## Changed
- #1153 merged (`786cacbd`): enum spec `runtime/specs/backlog-status.json`, lossless migration (114 rows round-trip), `scripts/backlog_status_check.py` in pre-commit + CI, readers/writers moved to `status_note`. Receipt `2026-10-10--backlog-state-enum-pr1153--ZH`.
- #1159 merged (`20dfad2b`): doc-gates-advisory-ci and notomation-receipt-save-nudge set to DONE, flow-state-om-metric set to COMPOSTED (PR #598 closed unmerged, branch kept). Receipt `2026-10-10--close-stale-backlog-rows-pr1159--ZH`.
- AGENTS.md gotcha #20 records the rule (this PR).

## State
Backlog: OPEN 47, HOLDING 24, HELD 8, RUNNING 3, BLOCKED 2, DONE 20, COMPOSTED 6, SUPERSEDED 3. `backlog_status_check.py --gh` reports 0 STALE.

## Decisions
- Zach classified the 13 rows the prefix classifier could not; the other 101 were classified by rule.
- Legacy RUNNING claims got `claimed_at` 2026-10-10 because no original claim time existed.
- COMPOSTED (not DONE) for flow-state-om-metric because its work never landed.

## Open
1. The 3 RUNNING rows (forensic-arc-reconstruction, salvage-pass-promote-two, receipt-test-real-tag) print STALE from 2026-10-13 unless confirmed or closed.
2. The `--gh` check is manual; wiring it into /loops or night-moves is not done.

## Next action
On or after 2026-10-13, run `python3 scripts/backlog_status_check.py --gh` and confirm or close each RUNNING row it flags.

## Cold-start
- `python3 scripts/backlog_status_check.py --gh` for counts and STALE rows; enum in `runtime/specs/backlog-status.json`; migration log in PR #1153.
