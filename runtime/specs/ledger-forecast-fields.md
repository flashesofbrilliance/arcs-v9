# Falsification ledger: forecast fields (convention, 2026-10-17)

> Confirmed by Zach 2026-10-17. Purpose: make a ledger row scoreable (Brier, log score, calibration) without changing what the ledger already does. Pattern note: `_PATTERNS/2026-10-15-tier-fit-goldilocks.md`.

**Where they go (corrected 2026-10-17):** an open prediction is registered in `_STATE/assumptions.jsonl` (status `open`), because the falsification ledger's hard fate gate (`runtime/specs/fates.json`) accepts only FALSIFIED or HELD and so cannot hold a pending row. The assumption closes into a falsification-ledger F-row or HELD row. A row that already carries a verdict (an F-row or HELD row) may also carry the keys. The first version of this note named only the falsification ledger; that was wrong.

A prediction row carries three extra keys, written BEFORE the outcome is known:

| Key | Type | Meaning |
|---|---|---|
| `probability` | number in [0, 1] | The stated chance that `claim` is true (verdict CONFIRMED). Write a real number, not a hunch word. |
| `resolve_by` | `YYYY-MM-DD` | The date by which the verdict is due. |
| `resolution_source` | string | What settles it (a command, a file, a person, a URL), named so someone other than the author can check. |

Rules:
- The three keys are optional for the loader: `scripts/projection_factory.py` only fails on missing REQUIRED keys, so old rows and the public belief log are unaffected. No existing row is edited.
- A row without them is simply unscoreable. A scoring script reports that count; it never guesses a probability.
- Never edit `probability`, `resolve_by` or `resolution_source` after the verdict lands. A correction is a new row that cites the old id.
- The older `prior` key stays as is. It is not a calibrated probability unless the author says so in `test`.
- A row that passes `resolve_by` with no verdict counts as unresolved in the scoring report; it is not dropped.
- This is a convention, not a gate. Promote it to a pre-commit check only after a scoring script exists and at least one cohort nears n=30.

Scoring (`scripts/ledger_score.py`): reads both ledgers by default. Outcome 1 = verdict `CONFIRMED` or `HELD`, or assumption status `held`; outcome 0 = `FALSIFIED` or `falsified`; `open` is unresolved. An assumption whose `decided_ref` names an F-row is counted once, on the F-row. Survivorship: the falsification ledger holds claims that fell, so on its own its base rate is near 0; register predictions as they are made, not only after they fail.
