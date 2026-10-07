<!--
session: claude-mystifying-tesla-6bc6f3
branch: claude/mystifying-tesla-6bc6f3
head: 90fcea9c
created_at: 2026-10-07T17:40:54Z
-->
## Changed
- #1066 merged (`4e4972a7`, `--merge`): server-side satoshi base-rate gate (`src/lib/satoshi.ts`), prompt anchor "fewer than 1 in 50" built from the same constants, same gate on the EPHEMERAL_SAVE path, 9 unit tests incl. the real `/api/compass` handler against the stubs. Receipts `2026-10-06--satoshi-base-rate-gate-pr1066--ZH` (PR open) and `2026-10-07--satoshi-base-rate-gate-merge-pr1066--ZH` (merge).

## State
- Prod audit 2026-10-06 (aggregates only): 34 of 267 receipts isSatoshi; 33 of 34 PLAN mode, MEDIUM stakes, TWO_WAY door, flagged nci median 78 vs 58; COURT (deep model) flagged 1 of 96. The fast model read "high nci" as "satoshi".
- The gate keeps the flag only when claimed, stakes HIGH, nci_score >= 70 (ygate STEEP threshold). Replay over the 267 rows keeps 1 of 34; eligible ceiling 8 of 267. Historical rows untouched.
- Consumers: ygate.ts never reads the flag; only render is the InstrumentCluster Peak gauge; receipt page hardcodes false.
- Unit 153 pass (144 before); build clean; 6 PR checks green. `claude-security-review` failed on API 400 "Credit balance is too low" on the `ANTHROPIC_API_KEY` repo secret (0 findings). CI on the merge commit was queued, not observed.

## Decisions
- Enforce the compass meaning of satoshi (rare, category-defining) in a deterministic server gate rather than a prompt-only rewording; the prompt line is derived from the gate's constants so they cannot drift.
- Merged on Zach's yes with the security-review check red for a credit error, not a finding.

## Open
1. Zach: Anthropic credit on the org behind the `ANTHROPIC_API_KEY` repo secret; re-run the security review on `4e4972a7`.
2. Canon collision, escalated not resolved: `operators/arcs_rom.py` SATOSHI_CRITERIA (nci >= 50, irreversibility <= 0.5, most receipts qualify) vs the compass rare-move meaning now enforced. Zach decides which definition the word keeps.
3. EX-ANTE to score: after 50 new receipts, re-run the audit aggregates (flagged vs unflagged by stakes, mode, doorClass, nci bucket) and check the rate is under 1 in 50.

## Next action
Re-run the satoshi audit aggregates once 50 post-merge receipts exist and score the EX-ANTE in `src/lib/satoshi.ts`.

## Cold-start
- Gate + rationale: `src/lib/satoshi.ts`; tests: `tests/unit/satoshi.test.ts` (`npm run test:unit`).
- Audit SQL shape: project-scoped Supabase `execute_sql` (project `xbbpiryokswwvcrcutge`), `select "isSatoshi", count(*), percentile_cont(0.5) within group (order by "nciScore") ... from "Receipt" group by 1`, plus breakdowns by stakes, mode, "doorClass", "yState", provenance; never select question text.
- Receipts: `2026-10-06--satoshi-base-rate-gate-pr1066--ZH`, `2026-10-07--satoshi-base-rate-gate-merge-pr1066--ZH`.

## Lessons
- A red `claude-security-review` with "Credit balance is too low" is billing, not a finding; the other CI jobs use a placeholder key and stay green (memory `anthropic-api-budget-shared-cap-ci-drain` updated).
- Pull aggregates before touching a model flag: the inflation lived entirely in one mode/model/stakes cell, which made a two-condition bar sufficient.
