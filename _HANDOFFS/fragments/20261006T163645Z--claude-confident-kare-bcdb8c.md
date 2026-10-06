<!--
session: claude-confident-kare-bcdb8c
branch: claude/confident-kare-bcdb8c
head: dc50746b
created_at: 2026-10-06T16:36:45Z
-->
## Goal
Option C: make receipt outcomes measurable. Tag test vs real receipts, split Accountant cohorts, prove the predict->close->score plumbing on test data only.
## Changed
- #1029 merged (1fceb396): Receipt.provenance + Outcome.synthetic (migration 20261006120000, applied in prod), compass accepts provenance/resolveBy, outcome route allows synthetic only on test receipts, Accountant test/real cohorts, scripts/receipt_efficacy_probe.py (dry-run).
- Receipts 2026-10-06--receipt-provenance-pr1029--ZH and 2026-10-06--provenance-backfill-189--ZH.
## State
- Prod backfill done with Zach's yes in-session: 189 founder receipts created before 2026-09-21 tagged provenance=test. The 20 since stay null; external and anonymous untouched.
- No synthetic outcomes written to prod. Probe is dry-run only.
## Decisions
- Zach: tag the 189 pre-09-21 founder receipts as test (confirmed in session, count verified 189 before write).
## Open
1. Zach: tag the 20 founder receipts since 2026-09-21 as test or real individually; real cohort is empty until he files real ones.
2. Real receipts need passing provenance:"real" + resolveBy (no UI yet, API body only).
3. Run scripts/accountant_weekly.py with the new export columns and confirm the test/real cohorts show up.
4. Writing synthetic outcomes to prod (plumbing proof against the real route) needs Zach's explicit yes.
5. Orchestrator owns the tracker row outcome-closure-gap.
## Next action
Re-run the weekly Accountant export and check the test cohort shows 189 receipts, real 0.
## Cold-start
Read PR #1029 diff; scripts/receipt_efficacy_probe.py --self-test; operators/prod_receipt_to_accountant.py (cohort_of).
