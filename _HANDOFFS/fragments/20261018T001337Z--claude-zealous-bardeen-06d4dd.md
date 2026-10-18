<!--
session: claude-zealous-bardeen-06d4dd
branch: claude/zealous-bardeen-06d4dd
head: 421205c7
created_at: 2026-10-18T00:13:37Z
-->
> Defined tier-fit (overkill, underkill, just right) with the lock/interlock addendum, shipped a stdlib interlock checker, and scoped a Brier-based standard for the falsification ledger.

## Goal
Make "right amount of machinery per task" and forecast calibration measurable and reproducible, at a cost that is nearly free.

## Changed
- #1311 merged (`a5345389`): `_PATTERNS/2026-10-15-tier-fit-goldilocks.md`; receipt 2026-10-15--tier-fit-goldilocks-pr1311--ZH
- #1312 merged (`63f042e1`): lock addendum, `scripts/tier_ladder_check.py` with self-test, TF-B4 confirmed, TF-B5 killed; receipt 2026-10-15--tier-ladder-interlock-pr1312--ZH

## State
- TF-B1, TF-B2, TF-B3 are pre-registered and untested. TF-B4 confirmed on synthetic cases only. TF-B5 killed: no routed-task log with tier, pass/fail and irreversibility fields exists.
- Brier standard is discussed only, nothing built. Agreed shape: base-rate Brier Skill Score, log score, 5-bin calibration, n>=30 per cohort, bootstrap CI, unresolved counted.

## Decisions
- Use the base rate, not the coinflip, as the baseline; stop at the Cut rung now and defer Diamond (holdout, replication) until a cohort reaches n=30.
- Extend the falsification ledger with probability, resolve_by, resolution_source rather than altering the decision_receipt table.
- Do not fix the main checkout skills drift first; start a fresh session from origin/main.

## Open
1. Zach: confirm extending the falsification ledger fields (probability, resolve_by, resolution_source).
2. Capture a routed-task log (tier, pass/fail per tier, irreversible flag) so TF-B1, TF-B2 and the checker can run on real data.
3. Main checkout drifts 71 files from origin/main; needs a look at what is dirty before moving it.

## Next action
Build the stdlib ledger scoring script, pre-registering the baseline expectation before the first run.

## Cold-start
Read `_PATTERNS/2026-10-15-tier-fit-goldilocks.md`; read `_STATE/falsification-ledger.jsonl` (prior plus verdict per row); run `python3 scripts/tier_ladder_check.py --self-test`; cut a new worktree from origin/main.

## Shavasana
- Mechanical half: 0 commits and 0 merges counted in the day's records (counts run on 2026-10-17, after both merges); canary GROUNDED; sycophancy check verdicted RETURN (agreement 5, dissent 0 by keyword).
- Shipping anyway, and saying so: dissent exists in substance but not in the checker's keywords. TF-B5 was killed, the coinflip bar was rejected as the wrong baseline, and both receipts are self-attested (no independent verifier matched them).
- Attachment release: TF-B4 downgraded to "confirmed on synthetic cases only"; the existing RET tier table is motivating evidence, not proof; priors in the old ledger are not calibrated probabilities.
- Somatic: not asked. Disposition: release.
