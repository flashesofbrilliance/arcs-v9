# Ledger scoring: pre-registered baseline (2026-10-17)

> Written and committed BEFORE the first real run of the ledger scoring script (built in the same PR). The actual result is recorded in the section at the bottom, beside this prediction, without editing the prediction.

Context: `runtime/specs/ledger-forecast-fields.md` (confirmed by Zach 2026-10-17, PR #1459) and `_PATTERNS/2026-10-15-tier-fit-goldilocks.md`.

## What I looked at before predicting

Only the shape of `_STATE/falsification-ledger.jsonl`, not any score: 42 rows, every row carries the same 11 keys (`id scope ts claim test verdict delta fix confidence refs canon`). No row has `probability`, `resolve_by`, `resolution_source` or `prior`. Whether every verdict is FALSIFIED I read off the key counts, which is a fact about labels, not about calibration.

## Prediction

- n scored (new-field): 0. n scored (legacy prior): 0. The old rows hold only a word-valued `confidence` ("high"), which the script must NOT map to a number.
- n unscoreable: 42 (all rows). n unresolved: 0.
- Base rate, Brier, BSS, log score: undefined (no scored rows). The script prints 'insufficient (n=0)' and no skill claim.
- BSS range if I am wrong and some rows do score: below 0.0 to 0.2 (my prior is that rough, never-calibrated numbers do no better than the base rate). The bootstrap interval, if printed at all, should straddle 0.

## What would surprise me

Any scored row at all, or a BSS above 0.3 on fewer than 30 rows: either would mean the script is reading a number the author never wrote down as a probability.

## Caveats stated up front

- Old priors were not written as calibrated probabilities, so the first number from any legacy row is rough and labelled 'legacy prior, not calibrated'.
- The ledger is a falsification ledger: it logs claims that were tested, and may over-represent FALSIFIED rows. The base rate from it describes the ledger, not the world.
- A BSS from fewer than 30 rows per cohort is not reported as skill.

## Actual result (recorded after the first real run)

Run on 2026-10-17 against the 42-row ledger, after the prediction was committed (the prediction commit precedes this one in the PR history):

- rows read 42, unparseable 0. n scored 0 (new-field 0, legacy 0). n unresolved 0. n unscoreable 42.
- Base rate, Brier, BSS, log score: not computed ('no scored rows'). No skill claimed.
- Prediction held on every line. Nothing surprised me. The result is a statement about the ledger's missing fields, not about forecasting skill: calibration scoring starts when new rows carry `probability`, and a skill claim needs n=30 per cohort.
