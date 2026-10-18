<!--
session: backlog group 2 close, CI off by choice
branch: claude/handoff-billing-note
head: updated 2026-10-18 (first written 2026-10-11)
created_at: 2026-10-18T19:30:00Z
-->
## Changed
- Ranked the OPEN induced-backlog rows into six groups (the row field is `state`, not `status`; an earlier claim that it was missing was wrong). Verified the six "probably done" rows and closed five in #1583 (b236861e), which supersedes #1288: outcome-loop-timing-wiring-horizon-reviewdate-blind, compass-mobile-timeout-recover-receipt, handoff-postmerge-ci-936, receipted-fears-stunt, accountable-copypasta-card. conviction-chips-calibration stays OPEN (its gate needs at least 5 real players before it extends past the prototype). #1288 conflicted with the backlog's growth, and a local merge commit on it was blocked by the pre-commit page checks on other sessions' files, so the change was re-made on a fresh branch off main; the gate was not bypassed.
- #1578 (d107dc2e): scripts/unfold.py fills Routes and Corrections from Librarian.recommend() pre-scores, surfaced and never acted on (row unfold-uses-librarian). The stones are still UNCUT (0 FLAWLESS before and after): their only lint reason is the integrity gate on item-text cites, not Routes or Corrections. Relevance of the pre-score lines is unjudged.

## State
- GitHub Actions is OFF by Zach's choice since 2026-10-15 (`gh api repos/flashesofbrilliance/arcs-v9/actions/permissions` returns enabled=false), pending his billing fix; no PR gets a CI run. Under the standing rule (memory trade-cloud-spend-for-local-compute) PRs merge on local gates and the receipt says CI is off by choice. Re-enable with `gh api -X PUT repos/flashesofbrilliance/arcs-v9/actions/permissions -F enabled=true` once billing is fixed; that is Zach's call.
- Earlier in this session the PRs were held as if billing were a transient block; that was a stale read, corrected here.
- The five closed rows are mirrored to GitHub issues #1195, #1198, #1202, #1203 and #1221; the sync script is create-only, so those issues are still open.

## Decisions
- Zach: merge on local gates while Actions is off (receipts note CI is off by choice).

## Open
1. Backlog ripeness (2026-10-18): 8 RIPE rows. Zach decides: rc-ops-001-graduation-ruling (one-way), adr-085-acceptance-redecide (ADR-085 still PROPOSED; needs the train-vs-bypass counts), agent-receipts-audit-first-conversion (one-way external send). Read the 2026-10-17 accountant-weekly run output (13 s, reported succeeded, no new scoreboard since 2026-10-06) before closing accountant-weekly-first-unattended. forensic-arc-reconstruction: its claim (unnamed session since 2026-10-10) needs releasing; PR #951 merged. doc-gate-false-positive-cleanup is mechanical and ready.
2. 43 rows are past review_by (backlog_freshness.py), seven of them P1 and overdue about a week; fates are Zach's (renew, promote, compost, supersede). Three RUNNING claims are stale (> 3 days): forensic-arc-reconstruction, salvage-pass-promote-two, receipt-test-real-tag. Two rows are BLOCKED on dead dependencies (asm-009-net-direction-decided, tao-renders-regenerated-from-projection).
3. surfaces.arcs.care is not worth folding into the backlog yet (different job; one row mentions it). Revisit if rows get a stable key to a route.
4. scripts/unfold.py has a pre-existing integrity-gate failure (vapor path prefix `_INBOX/unfold-` in its docstring), present in main before #1578.

## Next action
Zach: decide the three one-way rows in Open item 1 (rc-ops-001 ruling, ADR-085 acceptance, the audit conversion).
