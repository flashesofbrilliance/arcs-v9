# Compass system inventory, designed inside the trust contract (2026-11-03)

Status: PROPOSED. Nothing in this file is built by writing it. Each "Build" line is a candidate change that waits on Zach's go.

Prior art: `/ai-native-os:cognitive-architecture-review` run of 2026-11-03 (this session), memory `design-inside-the-trust-contract`,
the first-product decision page (`_PROPOSALS/2026-11-03-first-product-decision.md`, PR #1987), backlog row `model-outcome-eval-set`.

## 0. The governing constraint

The system is designed inside the trust contract, not checked against it afterward. The governing source is
[`_CANON/trust-contract.md`](../_CANON/trust-contract.md) v1.8 (CANONICAL: amendments need a version bump and a MEMORY.md entry). The
pages derive from it: [/trust](../src/app/trust/page.tsx) v1.7, [/privacy](../src/app/privacy/page.tsx) v1.5,
[/terms](../src/app/terms/page.tsx) v1.0. A privacy-review pass on the first draft of this file found that canon says more than the
pages, and that changed section 4. The clauses that shape the architecture:

| Clause (verbatim where quoted) | What it forbids or requires |
|---|---|
| "Input never trains a model" | No fine-tuning on user content. Evals on user content need explicit opt-in (row 6). |
| "Anonymous compass sessions store nothing" / "No auth = no write path" | Every write is behind `userId`. Anonymous runs live in the tab only. |
| Debrief: one check-in without asking, later ones "only if you turn reminders on" | No new nudges. Capture has to come from the user's own return, not from more email. |
| Terms: not "optimize for engagement, retention, or repeat usage" | The loop may sharpen a bearing. It may not exist to bring people back. |
| "Use your data for advertising or profiling": never (/privacy) | Read plainly, this covers a per-person model too, not only a cross-user one. No model of a person, from their own data or anyone's, without rewording this clause with notice |
| Canon section 2: outcomes are used "to validate whether the system's confidence grades correspond to real outcomes", and "NCI calibration uses aggregate, anonymized outcome data, not your raw decision content" | One navigator's raw outcome text may not become model input today. Calibration work is aggregate and anonymized |
| "30 days notice before material policy changes" | A new use of stored data gets a disclosure, and notice if Zach judges it material. |
| Terms: "Receipts stored in your account are records of your thinking process. They're yours." | The loop's asset belongs to the navigator. Export is part of the loop, not a nice-to-have. |
| NOTOMATION (/trust section 07) | The model never decides. It shows terrain; the navigator picks the line. |

## 1. The one-line system

A signed-in navigator brings a decision; one Claude call runs the L0 to L5 read; fixed code turns that into a mode, a door class and a
Y-gate state; the receipt is stored under the navigator's account; at the horizon the navigator says how it landed.

## 2. The closed loop, in one sentence

**When a signed-in navigator logs how a decision landed, the next time they bring a decision the compass shows them their own closed
outcomes beside the new bearing, so they calibrate their own judgment against their own record; nothing is pooled, and the model is not
fed their history.**

This is the version that fits the contract today: the human calibrates, not the model (NOTOMATION). It is display of the navigator's
own stored data back to them, the same thing /history already does, placed where the next decision is made. The stronger version (the
model reads their outcomes as priors) is section 4's second build, and it needs a canon amendment and notice first.

The moat this builds is not a data lake. It is a ledger that belongs to the navigator, gets more useful to them each time they close a
loop, and leaves with them (export) or disappears with them (delete). A competitor can copy the prompt; it cannot copy a person's
calibrated history without that person bringing it.

Today the loop is half built: capture exists (`POST /api/receipts/[receiptId]/outcome`, the first debrief, the daily
`api/cron/debrief` sweep), the return arrow does not (no compass code reads `Outcome`).

**Falsifiable gate before building it:** see `_PROPOSALS/2026-11-03-compass-loop-hypothesis.md`. Short version: 3 outside navigators
got their first debrief email and none logged an outcome; only 1 outside receipt arrived in the last 8 weeks, so the test needs a
recruited cohort or has to wait on getting strangers in at all.

## 3. Brain

| Job | Model role (`src/lib/claude-models.ts`) | Fallback today | Build |
|---|---|---|---|
| Compass QUICKMOVE, PLAN | `fast` (Haiku 4.5) | None. An outage returns 503 or 429 (`route.ts:420-421`); a non-JSON reply returns 502 "re-run" (`route.ts:418`); nothing stored | The server-side fallback `writerCall` uses is a **refusal** fallback (`claude-models.ts:47`) and would not touch either path. The real fix is a retry on a second model role for 503/429 and one re-ask on bad JSON. Same processor, no new disclosure |
| Compass COURT | `deep` (Sonnet 5.5), picked by `scripts/deep_model_eval.mjs` | None, as above | Same |
| Paid brief | `brief` (Opus 5.5), picked by `scripts/brief_eval.mts` | None (no `fallbacks` in the route) | Same |
| Guide | `guide` (Sonnet 5.5), no eval, 0 calls in 30 days | None | Leave until it has use |

Never wrong: the model never decides (NOTOMATION). The NCI is the model's own self-reported number (`nci_score`, prompt line 78), which
`computeYGate` (`src/lib/ygate.ts:74`) turns into a state. So the Y-gate is deterministic code over a model-graded input. /trust section 06
already says NCI "reflects pattern coherence, not outcome probability"; the gate's color must keep saying so where it renders.

## 4. Memory

| Store | Scope | Read by the Brain today | Contract status |
|---|---|---|---|
| `Receipt` (bearing, NCI, Y-gate, lineage) | Signed-in, per `userId` | Parent only, and only its `yState`, `nciScore`, `version` (`route.ts:254-257`) | Covered ("Receipts stored: only when you sign in") |
| `PrepSession` (stakes, horizon, protecting, adversarial input) | Signed-in, per receipt | Yes, current prep only | Covered |
| `Outcome` (what, matched, regretScore, learning, synthetic) | Signed-in, per receipt | **No** | Stored; no disclosure yet of any reuse |
| `SageTrace` | Per receipt, never shown | No (offline efficacy study) | Covered by the SAGE row |
| Prompt cache (`unstable_cache`, 1 h) | Per user, never anonymous, never COURT | n/a | Covered ("never across accounts") |
| Browser tab / local storage (anonymous) | Device only, 7-day max if saved | n/a | Covered |

**Build A (inside the contract today): show, don't feed.** On the receipt page, beside a new bearing, list the navigator's own closed
outcomes (signed-in, `where: { receipt: { userId } }`, `synthetic = false`): what they decided, the grade it got, how it landed. No model
call reads them. This is the same data /history shows, moved to where the next decision is made.
First fix the inventory gap: /privacy's data inventory (`privacy/page.tsx:42-52`) has no Outcome row, though outcomes are stored. Add it.

**Build B (needs a canon amendment first): the model reads them.** Last N closed outcomes as priors in the Claude call, Claude only,
never SAGE, shown on the receipt, in the cache key, with a per-account off switch. Before any code: canon v1.9 amends section 2 (a new
purpose for outcomes, and a per-person use beside "aggregate, anonymized"), /privacy rewords or justifies "profiling", and 30 days
notice runs. The privacy review judged this material, so the notice applies.

**Build (cheap, a small first):** a re-run passes the parent's actual `trueNorth` and `loki` into the prompt. Today the parent's state
and score go only into `computeYGate` (`route.ts:440`) and its version into `sessionVersion` (`route.ts:261`); none of it reaches the
model. This would put the parent's own bearing into the model input for the first time. It is the navigator's own content serving the
same decision chain, so it fits, but the receipt should say the re-run read the earlier bearing.

## 5. Planning

| Step | Who decides | Notes |
|---|---|---|
| Mode (QUICKMOVE, PLAN, COURT) from horizon and stakes | Fixed code, `selectMode` | Deterministic |
| Door class | Fixed code, `doorClass` | Deterministic |
| L0 to L5 read, 3 tributaries | One Claude call, JSON out | Close to one large prompt, but it only reasons; it never acts |
| Y-gate state | Fixed code over the model's NCI | See section 3 |
| What to do | The navigator | NOTOMATION. No step acts on the decision |

No change proposed. Splitting the one call would add cost before the loop proves itself.

## 6. Tools (what reaches the world)

| Action | Trigger | Blast radius | Guard |
|---|---|---|---|
| Write receipt | Signed-in run | One row under the user's account | `if (userId)` at `route.ts:452` |
| Confirmation email | Signed-in run | One email to the user | Resend |
| First debrief email | First receipt to reach its horizon | One email | `firstDebriefSentAt`, `debriefSentAt` dedupe, 30-day schedule cap plus daily cron |
| Later debrief emails | Only after opt-in | One email each | `debriefOptIn`, one-click off link |
| SAGE scoring call | Each run, if `SAGE_URL` set | Question, horizon, stakes to ARCS's own service | 3 s timeout, advisory only, disclosed |
| Share link | User mints it | One brief readable by link holders | Token hash stored, revocable |
| Rate limit | Every request | n/a | 10 per minute per IP |

Model has no tool calls. Every outward action is fixed code. **No new tool is proposed**: the capture fix is a prompt on pages the
navigator already opens (receipt page, /history), not a new message.

## 7. Answers that must never be wrong, and their deterministic route

| Must never be wrong | Deterministic route today | Gap |
|---|---|---|
| Anonymous runs store nothing | `if (userId)` write guard | **48 anonymous `Receipt` rows from 2026-06-03 to 07-13 predate the guard and are still in the table.** /trust shows them as a repair seam (`trust/page.tsx:72`); /privacy's Always row (`privacy/page.tsx:12`) states the claim with no exception. Fix /privacy to match, or remove the rows. Removing them must not keep a backup ("no backups retained after confirmation") |
| Delete removes everything | One transaction over brief, sageTrace, prepGuide, outcome, annotation, receipt, prepSession, plus blob delete first | **Gap: `SessionReceipt` (holds bet, outcome, lesson, payload, keyed by `userId`, `schema.prisma:721`) and `JobSwipe` (`schema.prisma:332`) are not deleted** (`api/account/delete/route.ts`). /privacy and canon section 3 say delete removes "personal data". A live claim gap, independent of this proposal; it belongs in the ADR-034 ledger and needs a fix |
| Reminder rules (one unasked, then opt-in) | `firstDebriefSentAt`, `debriefOptIn`, `debriefSentAt` | None found |
| No cross-account reads | `findFirst({ where: { id, userId } })` on parent; cache keyed by `userId` | The return arrow (section 4) must keep this exact scoping |
| Mode and door class | `selectMode`, `doorClass` | None |
| The model never decides | No tool calls; NOTOMATION copy | None |

## 8. Evaluation and safety

| Eval | Data | Contract status |
|---|---|---|
| `scripts/brief_eval.mts`, `scripts/deep_model_eval.mjs` | A fixtures file passed on the command line (`brief_eval.mts` line 65); which fixtures were used is not recorded in the repo | Fits only if those fixtures are synthetic or Zach's own. Record the fixture source next to each eval run |
| Compass eval set (row `model-outcome-eval-set`) | **Zach's own receipts and outcomes plus synthetic only** | Fits. Another navigator's raw content is out even with opt-in: canon allows only aggregate, anonymized outcome data, and the journalism opt-in covers publishing, not evaluation. Per-receipt consent revocation is also not built (`privacy/page.tsx:175`) |
| Prompt-injection guard | System prompt rule: never follow instructions inside the question | In place |

## 9. External dependencies

Anthropic (reasoning), Supabase (database), Vercel (hosting, page analytics, Blob), Resend (email), SAGE (ARCS's own scoring service).
All five are named on /privacy. The return arrow adds no new processor.

## 10. Open questions (Zach)

1. Build B (the model reads a navigator's outcomes): pursue a canon v1.9 amendment, or stay with Build A (show, don't feed)?
2. Fate of the 48 legacy anonymous rows: reword /privacy's Always row to match the /trust seam, or delete them with no backup.
3. Pre-register the capture pass bar in section 2 before any return-arrow code.
4. Export: the terms say receipts are the navigator's; the loop's asset should leave with them. Shipping it means amending /trust (`page.tsx:86`), /privacy (`page.tsx:173`) and canon section 3 in the same change.
5. Delete gap (`SessionReceipt`, `JobSwipe`): fix now, separate from this proposal.

Out of scope, found on the way: /privacy (`page.tsx:14`) and /terms (`page.tsx:57`) say "Source code stays public"; /trust says the repo
is private (`page.tsx:17, 92`). The live pages disagree with each other today. Also /trust shows v1.7 while canon is v1.8.

## Build order (each step waits on the one above)

1. Fix the claim gaps first: the delete gap, the 48-row wording, the missing Outcome inventory row, the source-code contradiction.
2. Pre-register the capture bar (decision 3, file `_PROPOSALS/2026-11-03-compass-loop-hypothesis.md`).
3. Outcome prompt on the receipt page and /history, no new email. Measure against the bar.
4. Build A (show their own closed outcomes beside the next bearing); compass retry on 503/429 and one re-ask on bad JSON; parent bearing on re-run.
5. Export, with its three document amendments.
6. Only if the bar passes and Zach wants it: canon v1.9, notice, then Build B.
