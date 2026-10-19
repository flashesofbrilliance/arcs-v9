# RET RFP Intelligence mistakes postmortem

192 rows: K1-K79 (79), gauntlet ledger (99, prefixed G-), external-review/TODO extras (14, X/T). Dates for K47+ are approximate (trace only timestamps K1-K33). Gauntlet caught_by is inferred from the review label.

## Counts by class
docs-drift 20, claims-overstatement 18, ui-ux 16, amendment-handling 15, eval-design 14, monday-api 13, test-harness 12, security-privacy 12, ingestion 11, scope-refusal 10, packaging 10, process-cadence 10, tooling-env 8, retrieval 7, figure-gate 6, idempotency 6, other 4.

## Counts by caught_by
external-review 75, self-audit 68, test 14, rehearsal 12, eval 8, user 7, gate 5, other 2, live-demo 1.

## Detection vs severity
Automated tests, mutation checks and the scenario matrix caught the severe amendment-correctness bugs early (K17-K20: superseded deadline, zero-citation answers). Blind sets (K43, K44) exposed that our own 31/31 flattered us. External review caught the late severe items: K69-K74 (stale figure passing the gate, two-amendment chain, silent short-amendment loss), K34/K36 (history leak, localhost CSRF). Of the 11 H-weight gauntlet items, external review found 10 and self-audit 9; none came from tests.

## Five most reusable patterns
1. Every test, fault and gate must be shown to fail with the repair removed (K7, K9, K16, K28, K32, K48).
2. Fail closed, and make the refusal reach the reader: found-nothing is not the document-is-silent (K18, K42, K73).
3. Multi-step cases need fixtures, not single-step ones: two amendments, two sections, second route to same output (K71, K74, K78).
4. Render every figure and claim from records; audit each sentence against its source (K13, K14, K31, K35, K54).
5. Gates must scan everything that ships, measure the shipped artifact and be read by exit code (K34, K40, K48, K50).

## Still open (50 rows)
K62 (T2 flake, disclosed); X01/X02 (empty Q7/Q12 assertions, citation laundering); X04/X05, G-M03 (private boards, board pagination, 429 and 200-with-errors untested); G-A03 to A06 (fast-path gaps, date arithmetic, relevance floor, legal/contact gate); G-M04, G-M06 (crash idempotency, intake never rehearsed); G-R13/R14 (log retention, questions on monday); G-S01/S09/S11; X06 (partial amendments); X09 (injection unproven); TODO 6-8, 18, 19.

## Blindspots (found only externally or late)
- security-privacy: 9 of 12 external-review; none by tests or evals.
- ui-ux: 12 of 16 external; user found layout/link failures in real browsers.
- claims-overstatement: user or external found 11 of 18.
- amendment-handling edge shapes (K72-K74): only external adversarial review.
- idempotency and partial-write paths: 4 of 6 external.
- Recurrence: G-D10, D16-D18, R02, R03, A10, S01 recurred.
