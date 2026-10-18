# Tier fit (the Goldilocks idea): overkill, underkill, just right

> Zach, 2026-10-15: some logic or models are overkill, underkill or just right for a given task, and this is an extension or pollination of ATG.
> Prior art: memory `model-tier-routing-locked-principle` (cheapest capable tier; never downgrade irreversible work), memory `no-gate-mixes-tiers-purity-rule` (a gate is purely mechanical, judgment or human), ADR-075 (metabolic router: mechanical vs judgment split). Grep found no "goldilocks / overkill / underkill" concept in `_DECISIONS`, `_PATTERNS` or `runtime/specs`. Those three say which class of worker a step needs. None of them measures whether the tier chosen was the cheapest that works. This note supplies that measurement. It does not build a router.

## Definition (operational)

For one task class:

1. Fix a ground-truth check the task's output can be scored against (a labelled set, a grep, a schema, a human-confirmed sample).
2. Run the task on two or more tiers (mechanical rule, small model, mid model, top model, or a human).
3. Score each tier on the same check, and record cost per item.

Then, per tier run:

| Label | Test |
|---|---|
| **Just right** | The cheapest tier that passes the check. |
| **Overkill** | The tier passes, and a cheaper tier also passed. The extra cost bought nothing the check can see. |
| **Underkill** | The tier fails the check. Cost is irrelevant until it passes. |

The label belongs to a (task class, tier, check) triple, never to a tier alone. "Passes" needs a pre-registered bar (for example precision >= 0.9 on the sample), fixed before the run. A tier that passes only because the check was loosened afterwards is not just right.

Floor, inherited from the locked principle: irreversible or ruin-exposed work is never labelled overkill and never routed down on cost alone. Tier-fit measures reversible work.

## Existing data, read-only (not yet re-scored against this definition)

| Task class | Tier | Result | Reading |
|---|---|---|---|
| RET belief questions | Qwen, $0 | 14/18 | underkill at a 18/18 bar; just right only if the bar was lower |
| RET belief questions | Claude | 18/18 | passes, and the only tier that does |
| RET judgment questions | Haiku ~$0.00023/q | 16/18 and 12/12 | candidate just right; Sonnet at ~$0.0038/q (about 16x) is overkill if the same bar holds |
| Contradiction check | regex | 0 of 3 precision | underkill |
| Verdict judgment pass | Haiku | 7 of 8 sampled verdicts confirmed | about right (n=8, thin) |
| Mechanical file edits | top tier by hand | worked | overkill: a script would pass |

Source: the RET take-home belief ledger (untracked, main checkout state folder, ret-postmortem-raw-2026-10-15), plus the session's own examples. These rows were not gathered under a pre-registered bar, so they are motivating evidence, not proof.

## Relation to ATG (a different axis)

ATG decides **what to surface**: 2 to 4 tributaries per compass response (meta-question, need-to-hear branch, unnamed adjacent primitive). Tier-fit decides **how much machinery each branch gets**. They are orthogonal: any tributary can be cheap or expensive to explore, and a cheap-to-explore branch is not thereby a better one. Do not let tier-fit prune what ATG surfaces; that would let cost choose the question (the NOTOMATION and ruin-vector concern).

### Hypothesis (not adopted)

Each ATG tributary carries a **tier-fit label**: the cheapest tier expected to resolve it (mechanical / small / mid / top / human), so the human sees both the branch and the price of walking it.

Kill condition: on a sample of at least 20 tributaries from real compass receipts, run each at the labelled tier and at the top tier, scored against a pre-registered rubric. Kill the hypothesis if the label is wrong (labelled tier fails where top passes) on more than 25% of tributaries, or if the labels do not change any user's choice of branch in at least 5 observed uses. A label that is mostly wrong or never read is decoration.

## Pre-registered beliefs (claim, prior, test, kill), registered before any test is run

Format follows `_STATE/falsification-ledger.jsonl`. Verdicts are empty on purpose. Move to the ledger with a verdict once run.

```json
{"id": "TF-B1", "scope": "method", "ts": "2026-10-15", "claim": "For the RET belief-question task, Haiku passes the same check as Sonnet, so Sonnet is overkill for that class.", "prior": 0.65, "test": "Re-run the 18 RET belief questions on Haiku and Sonnet against the human-confirmed answers in that belief ledger; bar fixed now at >= 16/18 correct.", "kill": "Haiku scores below 16/18, or Sonnet scores above 16/18 while Haiku is below it.", "verdict": null}
{"id": "TF-B2", "scope": "method", "ts": "2026-10-15", "claim": "A regex-first, model-second cascade matches the model-only verdict accuracy on contradiction checks at lower cost; regex alone stays underkill.", "prior": 0.35, "test": "On the contradiction-check sample (the 3 regex cases plus a fresh human-labelled 30), run regex alone, Haiku alone, and regex-then-Haiku; bar: precision >= 0.9.", "kill": "The cascade precision is below 0.9, or its cost is not at least 30% below Haiku alone.", "verdict": null}
{"id": "TF-B3", "scope": "hypothesis", "ts": "2026-10-15", "claim": "Tier-fit labels on ATG tributaries are right at least 75% of the time and change a user's branch choice.", "prior": 0.30, "test": "See the kill condition above (20 real tributaries, top-tier comparison, 5 observed uses).", "kill": "More than 25% mislabelled, or fewer than 5 choices changed in 5 uses.", "verdict": null}
```

Not claimed: that these priors are calibrated, that two or three task classes generalize, or that cost per question is the right axis for work where latency or reviewability binds.

## Lock addendum (Zach via the filing session, 2026-10-15): the interlock

"Goldilocks" is also a double entendre: a nautical lock raises and lowers heavy things safely. Its defining property is the **interlock**: only one gate open at a time, the vessel moves one chamber at a time while levels equalize. Each part is labelled MECHANISM or METAPHOR (echo-scan convention).

| Part | Label | Status |
|---|---|---|
| Pre-commit gates (integrity gate, design-debt gate) behave as a flight of locks: each shut until the one before it passes | MECHANISM | already running |
| Tier ladder: a task enters at the cheapest tier, the verdict check is the sluice, a failed check raises it exactly one tier (never skipping), irreversible work may only exit through the top gate (ROM primitive 7, WRITE-LOCK) | MECHANISM | proposed; invariant is testable (below) |
| "Water level = difficulty" | METAPHOR | no measurement behind it; do not build on it |

**Invariant (testable):** over a log of routed tasks, no task skips a tier and no irreversible task exits below the top gate. the tier-ladder checker script (added in the following commit) asserts it, and its `--self-test` plants a skip and a downgrade and requires both to fail.

**Lock versus Golden Inchworm:** the Inchworm is three non-blocking passes (Red Thread, Golden Thread, Needle), exploratory, and may be abandoned. A lock is sequential, blocking and commit-shaped: nothing moves until the gate ahead passes. Inchworm decides what is worth attempting; the lock governs how far up the ladder an attempt may go before it can commit.

Two more pre-registered beliefs, fixed before the checker was run:

```json
{"id": "TF-B4", "scope": "method", "ts": "2026-10-15", "claim": "The interlock invariant is mechanically checkable over a routed-task log by a stdlib script.", "prior": 0.85, "test": "Run the checker's --self-test: clean logs must pass, a planted skip must fail, a planted irreversible downgrade must fail.", "kill": "Any of the three self-test cases gives the wrong verdict.", "verdict": null}
{"id": "TF-B5", "scope": "reality", "ts": "2026-10-15", "claim": "Real routed-task logs exist in the repo in a form that fits the checker's schema without invention.", "prior": 0.20, "test": "Search _STATE and operators/ledger for per-task tier, pass/fail and irreversibility fields.", "kill": "No log carries all three fields; then the checker is verified on synthetic cases only and the note says so.", "verdict": null}
```

### Results

- **TF-B4 CONFIRMED.** `scripts/tier_ladder_check.py --self-test` returned PASS: 3 clean tasks gave 0 violations, the planted skip gave 1, the planted irreversible downgrade gave 1. Synthetic cases only.
- **TF-B5 KILLED (prior 0.20 held).** The only per-call log found, `operators/ledger/operator-receipts.jsonl`, records operator calls with no tier, pass/fail-per-tier or irreversibility fields. No routed-task log exists, so the invariant has been verified on synthetic cases and has never been run over real routing. Capturing such a log is the next step before this is more than a checker.
