<!--
session: claude-handoff-prl-takehome
branch: claude/handoff-prl-takehome
head: ab9c6222
created_at: 2026-10-11T02:42:42Z
-->
> After pickup: corrected the stale PRL go-live blocker (snapshot + Todd's checklist), then asked the take-home session for status. Follows fragment 20261011T022634Z--claude-handoff-hud-live.

### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-prl-takehome), receipts in digest: 1.
- **Inhale** (what came in): 0 falsification rows today, 5 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 27 / dissent 7 (ratio 3.38) → OK: dissent present.
- **Cold re-read (canary on the draft frag3.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: every claim kept; #1267 and the take-home reply are stated as pending. Somatic: not asked. Disposition: release.

## Goal
Go into Monday's PRL call and the take-home rehearsal with state that matches the evidence.

## Changed
- #1267 open, not merged: Todd's go-live checklist (public/prl-status-runbook.html) adds item gl-z6 "Confirm a returning chat updates the lead it matched, never a fixed record"; `_STATE/snapshot.json` blocking line now names the step 8 static-Lead cause. page_gate 1/1; smoke pending at 02:45Z.
- No merges this leg; receipts so far: 2026-10-10--handoff-fragment-hud-live-pr1263--ZH.

## State
- PRL root cause (from _ARTIFACTS/prl-1-2-close-loop/2026-10-09-go-live-blockers.md): Sep 17 Lamarre update came from step 8's static Lead pick, not an empty email. Fix staged as an unpublished draft of Zap 376827315; published v5 unchanged.
- Take-home (~/ret-rfp-intelligence, read-only look): CI green on 90d62d5; ONBOARDING.md present; commit 823bba4 records every briefing resource as used, rejected or cited. Two files uncommitted, owned by the take-home session.
- Status request sent to session "Continue monday take-home from HANDOFF.md" (status: waiting); no reply yet.

## Decisions
- Zach approved both PRL edits; the client-facing item got a new checkbox id so Todd's saved ticks stay put.
- Leave the take-home repo to its own session; ask by message only.

## Open
1. Zach: clear the take-home session's pending prompt if it does not reply.
2. Merge #1267 when CI passes, log its receipt, confirm gl-z6 live on prl.arcs.care/go-live.
3. Relay the take-home session's reply to Zach.

## Next action
Merge #1267 once smoke passes, then check prl.arcs.care/go-live shows the new item.

## Cold-start
- `gh pr checks 1267`; `gh pr merge 1267 --merge`; insert a decision_receipt row; `curl -sL https://prl.arcs.care/go-live | grep -c "never a fixed record"`.
- PRL context: _ARTIFACTS/prl-1-2-close-loop/2026-10-09-go-live-blockers.md (root-cause and draft sections).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.
