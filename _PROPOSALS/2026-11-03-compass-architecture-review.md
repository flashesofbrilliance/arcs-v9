# Compass cognitive architecture review, final (2026-11-03)

Status: FINAL for this round. Graded from code and production tables, not from docs. Supersedes the first-pass scorecard given in
session chat earlier the same day, which was written before the trust-contract read and got three things wrong (corrections in
section 6). Companion files: `2026-11-03-compass-system-inventory.md` (the design), `2026-11-03-compass-loop-hypothesis.md` (the bet).

System graded: `POST /api/compass` and what it stores, emails and reads. Contract: `_CANON/trust-contract.md` v1.8 and the
/trust, /privacy, /terms pages.

## 1. Four-pillar scorecard

| Pillar | Grade (0-3) | Evidence |
|---|:-:|---|
| **Brain** | **2** | Role-routed models in one registry (`src/lib/claude-models.ts`): Haiku 4.5 for QUICKMOVE and PLAN, Sonnet 5.5 for COURT, chosen per mode by fixed code. **No fallback**: an outage returns 503 or 429 and a bad reply 502 (`route.ts:418-421`); the refusal fallback `writerCall` uses would not touch either path. **Model-choice eval is unsound**: `scripts/deep_model_eval.mjs` sends the literal placeholder `${SATOSHI_RULE}` instead of the rule, so the eval that picked the deep model never ran the production prompt. **No output eval**: unit tests check shape (`tests/unit/compass-response.test.ts`, `ygate.test.ts`, `dewy-schema.test.ts`), not content or distribution |
| **Memory** | **1** | Receipts persist per signed-in user with lineage. The model's input is the current question and prep only: the parent's state, score and version feed `computeYGate` and `sessionVersion` (`route.ts:261, 440`), never the prompt. `Outcome` rows are written (`api/receipts/[receiptId]/outcome`) and read by nothing in the compass |
| **Planning** | **2** | Fixed code picks mode and door class (`selectMode`, `doorClass`, `route.ts:36-56`), one structured call reasons, fixed code computes the Y-gate. The model never acts (NOTOMATION). One call returns 15 fields, so it is close to a God-call, but it reasons only. **The gate's main input is model-graded**: `nci_score` is the model's own number (prompt line 78, "40-60 = genuinely uncertain. Do not inflate") against fixed cutoffs at 40, 60 and 65 (`ygate.ts:83-165`) |
| **Tools** | **2** | Every outward action is fixed code, none is a model tool call: receipt write behind `if (userId)` (`route.ts:452`), confirmation email, one unasked debrief then opt-in only (`firstDebriefSentAt`, `debriefOptIn`, `debriefSentAt` dedupe, daily cron for long horizons), advisory SAGE call with a 3 s timeout, revocable hashed share links, 10 requests a minute per IP. All small and reversible. **Delete gap**: account delete missed `SessionReceipt` and `JobSwipe`; fix in PR #1996 |

**Weakest link: Memory (1).** Nothing a navigator does reaches the next decision.

## 2. Closed-loop diagnostic: weak

- **Capture:** present (outcome route, one debrief email, the daily cron).
- **Data:** thin. 5 real outcomes, all Zach's. Outside navigators: 5 users, 11 receipts, 3 got their first debrief, 0 opted in, 0 outcomes,
  1 outside receipt in the last 8 weeks (query, 2026-11-03).
- **Return arrow:** absent. Outcomes are read only by `tribune`, a count in `pulse`, and offline scripts.

The loop the contract allows today is display, not model input: show navigators their own closed outcomes beside their next bearing so
they calibrate themselves. Canon section 2 limits calibration to "aggregate, anonymized outcome data"; the model reading one person's
outcomes needs a canon amendment and 30 days notice (inventory section 4, Build B).

## 3. The signal that may be stuck

In 285 receipts the Y-gate has never returned GREEN or RED: FORK 141, PARADOX 122, SCRATCH 7, YELLOW 5, DELTA 2 (all users, all time).
The prompt anchors the model's score in 40 to 60 and the gate's cutoffs sit at 40, 60 and 65, so the combination may make GREEN
unreachable. Whether GREEN is meant to be that rare is a product call; that nothing would notice a shift is a debt either way.
Spike result (section 5) says whether a replay snapshot can gate it.

## 4. Remove-the-AI test

Delete every model call and the compass returns nothing: the intelligence does the core job, so on this skill's definition it is
**AI-native**. But nothing compounds yet, so there is no moat: a competitor with the same prompt has the same product. Verdict:
**AI-native in mechanism, wrapper in economics until the display loop is live and navigators close it.**

## 5. Fix list, severity against effort

| # | Fix | Severity | Effort | Gate before it ships |
|---|---|:-:|:-:|---|
| 1 | Outcome prompt on the receipt page and /history (no new email), then show navigators their own closed outcomes beside the next bearing (Build A) | High | Low | The per-navigator bar in the loop hypothesis |
| 2 | Compass replay eval: fixed fixtures (Zach's own plus synthetic), record score and Y-state distribution, fail on drift | High | Medium | Spike, section 5a |
| 3 | Fix `deep_model_eval.mjs` to fill `SATOSHI_RULE`, then re-check the Oct 6 deep-model choice on the real prompt | High | Low | Re-run against the same inputs |
| 4 | Y-gate cutoffs vs the model's score band (GREEN and RED never fire) | High | Medium | #2's snapshot before and after; one cutoff per round |
| 5 | Compass retry on 503 and 429 on a second role, one re-ask on bad JSON | Medium | Low | Unit test with a mocked failing client |
| 6 | Reminder date parsed in code instead of by the model (`reminder_iso`, prompt line 92) | Medium | Low | Table-driven unit test of horizon strings |
| 7 | Re-run passes the parent's bearing into the prompt, and the receipt says so | Low | Low | Unit test on the user message |

### 5a. Eval spike result

(Pending: 8 fixtures, 5 of Zach's own receipts and 3 synthetic built to test whether GREEN and RED are reachable, 3 runs each,
prod prompt and model config. Filled in when the run lands.)

## 6. Corrections to the first-pass scorecard

1. It proposed the server-side fallback as the outage fix; that fallback handles refusals only.
2. It proposed feeding outcomes into the prompt and an eval set from "real decision-and-outcome pairs"; both break canon section 2.
3. It said the debrief is skipped for horizons over 30 days; the daily cron (`api/cron/debrief`) sends it once the date is inside 30 days.

## Next

Fix #1 is the frame-the-hypothesis test and needs Zach's checkpoint-1 call (recruit a cohort, or frame traffic first). Fixes #2 to #7
go to `agentic-build-loop` one at a time, each behind its gate.
