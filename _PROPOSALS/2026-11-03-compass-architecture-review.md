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
**Cause, found by the spike (section 5a): GREEN is structurally unreachable, and the score band is not why.** The prompt requires
"2-3 paths" with status `selected`, `viable` or `blocked` (`route.ts:86`). The gate fires FORK whenever 2 or more paths are not
`blocked` (`ygate.ts`, condition 3), and a `selected` path counts as not blocked. The model always returns 3 paths, so every receipt
gets FORK, or PARADOX when two are viable and the score is under 60. A synthetic clear yes scored 82 and a synthetic clear no scored
94; both came back FORK. My first-pass guess (the 40-60 score band against fixed cutoffs) was wrong; the spike falsified it.

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
| 4 | Y-gate FORK rule: count only `viable` paths (not `selected`) toward FORK, so a decision with one selected path can reach GREEN | High | Low | The spike's fixtures as the snapshot: the synthetic clear yes should leave FORK; real receipts should not move without a reason |
| 5 | Compass retry on 503 and 429 on a second role, one re-ask on bad JSON | Medium | Low | Unit test with a mocked failing client |
| 6 | Reminder date parsed in code instead of by the model (`reminder_iso`, prompt line 92) | Medium | Low | Table-driven unit test of horizon strings |
| 7 | Re-run passes the parent's bearing into the prompt, and the receipt says so | Low | Low | Unit test on the user message |

### 5a. Eval spike result

8 fixtures (5 of Zach's own receipts, 3 synthetic: a clear yes, a clear no, a low-stakes two-way), 3 runs each, the production prompt
with `SATOSHI_RULE` filled in, the production model per mode, no prep, no SAGE. 24 calls, 0 errors, about 50k output tokens.

| Fixture | Mode | Scores (3 runs) | Spread | Y-state, all 3 runs |
|---|---|---|:-:|---|
| z-court-1 | COURT | 52, 52, 52 | 0 | PARADOX |
| z-court-2 | COURT | 46, 46, 48 | 2 | PARADOX |
| z-court-3 | COURT | 62, 62, 62 | 0 | FORK |
| z-plan-1 | PLAN | 58, 62, 62 | 4 | FORK |
| z-quick-1 | QUICKMOVE | 72, 72, 72 | 0 | FORK |
| s-green (clear yes) | QUICKMOVE | 82, 82, 82 | 0 | FORK |
| s-red (clear no) | COURT | 94, 93, 94 | 1 | FORK |
| s-plan | PLAN | 78, 72, 78 | 6 | FORK |

**Verdict: stable enough to gate on.** Spread is 0 to 6 points per decision; the Y-state agreed on all 24 runs. A snapshot with about
8 points of tolerance per fixture and an exact Y-state match would catch a real shift without flapping. By-products: the gate is stuck
on FORK for the reason above, and every mode took about 18 s per call, so QUICKMOVE on Haiku is not faster than COURT on Sonnet for
these inputs. Inputs and outputs stayed in the session scratchpad, out of the repo.

## 6. Corrections to the first-pass scorecard

1. It proposed the server-side fallback as the outage fix; that fallback handles refusals only.
2. It proposed feeding outcomes into the prompt and an eval set from "real decision-and-outcome pairs"; both break canon section 2.
3. It said the debrief is skipped for horizons over 30 days; the daily cron (`api/cron/debrief`) sends it once the date is inside 30 days.

## Next

Fix #1 is the frame-the-hypothesis test and needs Zach's checkpoint-1 call (recruit a cohort, or frame traffic first). Fixes #2 to #7
go to `agentic-build-loop` one at a time, each behind its gate.
