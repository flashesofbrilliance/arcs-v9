# RET take-home: belief ledger summary (T0 2026-10-10 to submission 2026-10-14)

134 rows in `beliefs.jsonl`: 87 FALSIFIED, 24 REVISED, 14 CONFIRMED, 9 OPEN. Ids are provisional. The logs record errors far better than survivals, so CONFIRMED is under-represented.

## Anterior (T0) vs posterior (done)
- **T0:** document-QA build; the amendment is the demo spine; sample questions are traps; four regex rules suffice; no embeddings needed; a local 7B might be primary; depth is cheap off-stage.
- **Done:** the first two held. Regex rules held only on the sample; the parser now fails closed on real packages. Local model is fallback only. Depth was costly; scope was cut and deck claims rewritten.

## Five biggest shifts
1. **Real addenda (H3/H4, K42).** Forecasts 75% and 85% both failed: a real 89-page RFP plus 7 SF-30s parsed to 0 clauses and answered "not addressed". Now refused, not stored.
2. **Our own tests flattered us.** Five tests that could not fail (K7, K9, K16, K28, K48), a false from-ZIP pass, and blind set 1 at 16/20 versus 31/31 on our questions.
3. **Scope.** Bar-raiser and the recoil review overturned "depth is free": dashboards, terms, present mode cut (D-SCOPE, D-SUBTRACT).
4. **Slide claims.** 65 audited: 43 held, 16 reworded, 4 false (what leaves RET, who wrote the questions, which boards RET uses).
5. **Simulation versus rehearsal.** 3,072 scenarios caught none of K55-K58 (new amendment, paging past 100, `.env` key, poller death). A brief trace, live rehearsal and outside review found them.

## Forecast calibration
11 of 39 logged forecasts resolved; mean Brier **0.243** (coin flip is 0.25). Forecasts at 0.7 or above hit 4 of 7 (stated mean 0.79); those below 0.7 hit 3 of 4 (stated 0.54). Overconfident when sure, underconfident when unsure. Worst: H3-p2 0.72, H3-p1 0.56 (first scored TRUE on synthetic data, re-resolved FALSE on real), M1-p2 0.49. Best: M1-p3 0.0025. The H5 parser-swap forecast was never scored.

## Never tested
- 28 forecasts (pilot estimates, panel behaviour, interview, advancement) depend on events after the done-line.
- Accuracy on RET staff's real questions and on a real 400-600 page RFP, including whether the verbatim gate holds at real size (H4-p2).
- H5 (swappable adapters), H6 (RET data reachable), H7 (seat price).
- Paid-plan behaviour: monday models, automations, analytics.
- Service-account token, retention, running inside RET rather than a laptop.
- Local-model and Haiku quality on the final build; T2 fails about 1 run in 10.
