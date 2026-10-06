---
version: 0.1
status: PROPOSAL (prompt NOT changed; no API spend yet)
date: 2026-10-05
resolves: Ahmed-order collision C4 (runtime/specs/ahmed-order-vocabulary.md, on branch claude/agitated-wu-1c9eeb @ 487c6dc9)
---

# Tributary answers: proposal + pre-change eval

## 1. Why 197 of 267 receipts have no `atgTributaries` (prod, read-only, 2026-10-05)

| Month | Receipts | With `atgTributaries` | Null, but `rawResponse` holds `"tributaries"` |
|---|---|---|---|
| 2026-06 | 204 | 7 | **197** |
| 2026-07 to 2026-10 | 63 | 63 | 0 |

- **All 197 nulls are June 2026, and all 197 still carry the tributaries in `rawResponse`.** Writer gap,
  not a model gap: the `atgTributaries` column write landed in `7c028a28` (#25, 2026-06-30). Last null row
  2026-06-28; every receipt since July has the column.
- The 7 June rows that *do* have it (1 user, 2 days, from 2026-06-12) interleave with nulls until 06-28.
  Likely a preview/branch build writing to the prod DB before #25 merged. **Unconfirmed.**
- **Dry run (2026-10-05, read-only SQL, route's fence strip mirrored): 197/197 recoverable.** All parse,
  all hold exactly 3 tributaries, every `type` is meta/challenge/adjacent, every `prompt` is non-empty,
  0 exceed the 1000-char clamp, 0 carry an answer. 48 of them were markdown-fenced.
- **Backfill: decided against (Zach, 2026-10-05).** Legacy June rows stay null. Writes since July are healthy (63/63), which is all that matters. The dry run is kept above only as evidence the data was recoverable.

## 2. Proposed prompt change (`src/app/api/compass/route.ts`, rules + OUTPUT SHAPE)

Replace the `tributaries` rule with:

```
- tributaries: EXACTLY 3. Each has a question and a short answer.
  - [0] meta, [1] challenge, [2] adjacent (unchanged definitions)
  - prompt: the question, first person, specific to THIS decision.
  - answer: 1-2 plain sentences that answer it from what the user actually gave you
    (question + prep context). If that material cannot answer it, say what is missing,
    e.g. "Unknown from what you shared: it depends on whether your top client would stay."
    Never invent a fact, number, name or precedent to make an answer sound complete.
  - answer_basis: "given" (answered from the user's material) | "inferred" (reasoned, not stated)
    | "unknown" (cannot be answered at this fidelity).
  - Phrase the question directly. Do not open with "Am I really deciding X, or am I deciding Y".
```

Shape: `{ "type": "meta", "label": "Meta-Question", "prompt": "string", "answer": "string", "answer_basis": "unknown" }`

**Storage (no schema change):** the same `atgTributaries` TEXT JSON gains two optional keys. Writer:
`answer: clampText(scrubProse(o.answer), 600)`, `answer_basis` clamped to the 3-value enum, else
`"unknown"`. Old rows simply lack the keys; readers treat absent as "open question" (the C4 fidelity
rule: render as open, never invent).

**Fidelity coupling (WORLD.md render scale):** the Y gate already decides render resolution. The page
renders `answer_basis: "unknown"` as an open question in every state, and at GRAIN/MOIRE
(SCRATCH/DELTA/DRIFT/PARADOX/RED) renders `inferred` answers as open too. Only the render changes;
the stored data stays whatever the model said.

**Second writer to fix in the same PR:** `src/app/api/receipts/save/route.ts:96` stores
`b.tributaries` raw (client-supplied, no clamp). With answers it would persist unclamped text. It
should run through the same sanitizer as the compass route.

**Budget:** +3 answers is about 150-250 output tokens. QUICKMOVE runs at `max_tokens` 2048 and already
has a truncation guard; the after-eval must record `stop_reason` per run.

## 3. Eval per `_PATTERNS/slop-free-rubric.md`

### Before (done, $0): mechanical baseline over the 207 stored prompts (70 receipts)

| Cohort | n | Dash (em or spaced) | "X, or am I Y" binary | "Am I really/actually..." opener | Has a number | Words avg / stdev |
|---|---|---|---|---|---|---|
| Before 2026-07-15 | 120 | 89 (74%) | 25 | 21 | 30 (25%) | 35 / 8 |
| From 2026-07-15 | 87 | 27 (31%) | 20 | 9 | 8 (9%) | 32 / 7 |

Read: the em-dash rule is working but not done (31%); rubric **B1 (binary contrast) scores 2** because
the meta slot is templated as "Am I really deciding X, or am I deciding Y" (a pattern, not one deliberate
use); specificity (D1) dropped as prompts got cleaner. Burstiness ~7 clears the >=6 floor. The prompt
text above targets B1 directly.

### Still needed (needs API spend, not run)

1. **Before, judgment layer:** `scripts/slop_eval.py` (LLM judge) on a sample of current outputs.
2. **After:** run the old and new prompt on the same fixed set of 12 decisions (synthetic, mirroring
   prod themes: fundraise timing, partner exit, STR purchase, career and AI, tool choice, GTM), at
   QUICKMOVE and COURT. Score both arms on: slop_lint metrics, slop_eval rubric total (ship bar <= 3,
   no row = 2), `stop_reason`, and an **honesty check per answer**: does every fact in an answer trace
   to the input? Any invented fact fails the arm. Count `unknown` share; 0% unknown on thin inputs is
   a fabrication signal, not a win.

Estimated cost: 12 decisions x 2 prompts x 2 modes = 48 compass calls plus ~60 judge calls. At current
Sonnet pricing, roughly $2-4. Zach said go (2026-10-05). **Blocked:** the local `ANTHROPIC_API_KEY` (`/Users/zharris/arcs-v9/.env.local`)
returns "You have reached your specified API usage limits ... regain access on 2026-11-01". All 48
compass calls were rejected with HTTP 400, so $0 was spent. Prod is unaffected (a receipt was written
2026-10-06 02:05 UTC). The harness is ready to re-run as soon as the key works (session scratchpad
`eval/harness.py`, `eval/cases.json`). Note: QUICKMOVE runs on Haiku 4.5 and COURT on Sonnet 4.6, so
the real cost should come in under the estimate.
