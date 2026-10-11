<!--
session: backlog group 2 close, Actions billing block
branch: claude/handoff-billing-note
head: e18c60d6
created_at: 2026-10-11T13:07:53Z
-->
## Changed
- Ranked the 48 OPEN induced-backlog rows into six groups (note: the row field is `state`, not `status`; an earlier claim that it was missing was wrong). Verified the six "probably done" rows against the repo and live pages and closed five in PR #1288: outcome-loop-timing-wiring-horizon-reviewdate-blind, compass-mobile-timeout-recover-receipt, handoff-postmerge-ci-936, receipted-fears-stunt, accountable-copypasta-card. conviction-chips-calibration stays OPEN (its gate needs at least 5 real players before it extends past the prototype).

## State
- GitHub Actions is billing-blocked again. On PR #1288 the `changes` and `gates` jobs failed in 2 to 3 seconds with zero steps; the job annotation reads "The job was not started because recent account payments have failed or your spending limit needs to be increased." githubstatus.com reported all systems operational, so this is the account, not an outage. Checked 2026-10-11. Until it is fixed no PR or main commit gets a CI verdict.
- #1288 is open and deliberately not merged (Zach: leave it open until billing is fixed). Its only evidence is local: fates.py check showed 0 hard misses and backlog_issue_sync.py --check showed 0 gaps.
- The five closed rows are mirrored to GitHub issues #1195, #1198, #1202, #1203 and #1221; the sync script is create-only, so those issues are still open.

## Decisions
- Zach: do not merge on red or on local evidence; wait for green CI.

## Open
1. Zach: fix the Actions billing or spending limit (GitHub settings, Billing and plans).
2. After that: re-run CI on #1288 and merge it with --merge on green, then write the receipt. #1251 (Louisville touch targets) will also need its checks re-run.
3. Close the five mirrored issues if Zach wants them closed.
4. Time-boxed backlog rows from the ranking: prl-golive-empty-email-guard (before Mon 2026-10-12 10:00 ET), accountant-weekly-first-unattended (2026-10-12), adr-085-acceptance-redecide (2026-10-13).

## Next action
Zach: unblock GitHub Actions billing, then ask for the re-run and merge of #1288.
