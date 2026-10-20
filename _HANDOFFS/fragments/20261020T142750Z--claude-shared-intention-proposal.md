<!--
session: nifty-hopper-699e97
branch: claude/shared-intention-proposal
head: 7506fbde
created_at: 2026-10-20T14:27:50Z
-->
> Shared-intention session (2026-10-20): designed the step after backlog induction (one shared intention, horizons, altitude drill-down, domino line), built a read-only risk underwriter, proved the outcome plumbing, and bridged decision-receipt outcomes into the Accountant.

## Changed
- PR #1697 merged (cc17e2ca): status.arcs.care no-JS floor restamped to 5,065 commits, day 194. Receipt 2026-10-20--status-floor-restamp-pr1697--ZH.
- PR #1698 merged (7506fbde): scripts/decision_receipt_to_accountant.py, Accountant cohort `decisions`, accountant_weekly prints synthetic_excluded. Receipt 2026-10-20--decision-receipt-bridge-pr1698--ZH.
- Backlog: receipt-randomized-plumbing-closes DONE (proven, seed 20261020, 5 synthetic closes); ruin bands on 10 rows, confirmed by Zach.
- Open PRs, not merged: #1691 (proposal _PROPOSALS/2026-10-20-shared-intention-before-snap.md), #1694 (risk underwriter design), #1695 (risk underwriter v0 script, branch claude/risk-underwriter-v0), #1696 (claim index, another session).

## State
- Accountant decisions cohort: 33 receipts in scope, 1 scored (held), 4 self-closed (never scored), 28 open.
- Compass Receipt table: 271 receipts, 0 tagged real; 3 outcomes scored; 5 synthetic excluded.
- Concourse "over 3,500 commits" is the no-merge count (3,590 on main 2026-10-20) and stays as written.
- Intention (Zach, 2026-10-20): mono no aware; four horizon lines and the exclusion are in PR #1691 section "First intention".

## Decisions
- Zach: intention definition B (stated by Zach) with C (mirror from the backlog) beside it.
- Zach: surgical decomposition lives in a linked spec file per issue (path proposed in PR #1691, not on main).
- Zach: onramp swapped after D0 to the decision-receipt bridge (built, PR #1698).
- Zach: SPECIALTY tier added beside UNINSURABLE in the underwriter; prices shown, never blocking.
- Zach: hyperstition is the fixed second pass after I.D.E.A.

## Open
1. Zach: Amy draft to amy@recruithaus.com (Gmail draft dated 2026-10-18): send, edit or drop.
2. George (Scout Global): Zach followed up (bundle 2026-10-16, nudge 2026-10-19; Zach confirmed 2026-10-20). Waiting on George; record a verdict on 2026-10-16--scout-wonderful-fde-lead-ex-ante--ZH when he replies.
3. Zach: funnel seed kill condition due 2026-10-22 (finding f-d1cb1802f5); no receipt yet.
4. Vico: Zach is in touch with Joe Schriner (confirmed 2026-10-20). Open only: Zach confirms which one-page attachment went on 2026-10-14, given the Tier 2 no-send-before-NDA note.
5. Zach: ship or hold PR #1695 (s4 freeze: do not regenerate the tool catalog).
6. Domino line D1 to D17 in PR #1691 section 4g; ripe now: D1 (intention test trigger), D2 (steelman the 10 DRAFT abort/rollback texts), D3 (= item 5).

## Next action
Zach rules on PR #1695, then D2: review the 10 DRAFT abort and rollback texts one row at a time.

## Cold-start
- Read PR #1691's proposal file, sections 4e (build order), 4g (domino line), 4k (bridge).
- `python3 scripts/decision_receipt_to_accountant.py` for the decisions cohort (needs `python3 scripts/universe_receipts_adapter.py --export` first).
- Until PR #1695 merges, run the underwriter from its branch: `git show origin/claude/risk-underwriter-v0:<script> > /tmp/ru.py` (script name in the PR).

## Ground truth
- Prod read-only (2026-10-20): decision_receipt and Receipt tables via Supabase execute_sql; git origin/main for counts.

## SSOT
- Backlog `_QUEUE/induced-backlog.jsonl`; outcome ledger `_STATE/receipt-outcomes.jsonl`; proposal in PR #1691.

## Routes
- Outcome verdicts: `python3 scripts/receipt_outcome_queue.py record`. Accountant: `python3 scripts/accountant_weekly.py --ingest`.

## Gates
- `python3 scripts/backlog_status_check.py --check`; `python3 scripts/decision_receipt_to_accountant.py --self-test`; merge with `gh pr merge --merge` only on Zach's yes.

## Corrections
- D0 first claimed the live decisions had no receipts; George and Vico do (false null, banked in PR #1691 section 4h).
- "Over 3,500 commits" was first called stale; it is the no-merge count and correct.

## Close protocol
- Record a decision receipt for every merge; mark backlog rows DONE only with evidence in status_note.
