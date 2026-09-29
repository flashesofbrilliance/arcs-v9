# Pre-registration — Orthogonal Echo Detector seaworthiness rebuild (closes F34)

> **Discipline:** falsifiable-test. The kill-condition below is fixed **before** the rebuild is
> written, and this file is committed in its own commit **ahead of** any implementation commit so
> git history proves the goalposts were not moved to fit the result. If the target is not met, that
> is a finding to record honestly — not a reason to relax the numbers.
>
> **Date:** 2026-09-26 · **Branch:** `claude/echo-detector-seaworthy` · **Candidate:** RC-OPS-001
> (`operators/arcs_inchworm_echo.py`) · **Reverses:** the "Now" fix of F34.

---

## Belief under test (the reversal to earn)

F34 (FALSIFIED, 2026-08-29): the Orthogonal Echo Detector (ROM Primitive #5) is **not** seaworthy —
its stub matcher is architecturally incapable of discriminating genuine cross-domain kinematic
isomorphisms from adversarial weak-keyword collisions. At no `min_sim` threshold does the stub reach
both high recall and low adversarial false-positive rate.

**Reproduced on this branch before touching anything** (`echo_detector_dogfood.py --sweep`):

| min_sim | precision | recall | f1 | adv_fp_rate |
|--------:|----------:|-------:|---:|------------:|
| 0.10–0.25 | 0.56 | 1.00 | 0.71 | **1.00** |
| 0.30 | 0.71 | 1.00 | 0.83 | **0.50** |
| 0.40 | 0.60 | 0.60 | 0.60 | 0.50 |
| 0.50 | 0.33 | 0.20 | 0.25 | 0.50 |
| 0.60 | 1.00 | 0.20 | 0.33 | 0.00 |

Adv-FP only reaches 0.00 by collapsing recall to 0.20. F34 stands as reproduced.

## Root cause (the Red)

The stub scores a pattern match on **lone generic token overlap** against a keyword library that
contains weak single words (`trust`, `shock`, `gradient`, `collapse`, `stability`, `recovery`,
`spreads`, `suddenly`). The four adversarial decoys deliberately share exactly those isolated words
without sharing the underlying dynamic, so they trip every low threshold. A shared *word* is treated
as a shared *structure*. It is not.

## The fix (the Golden)

Rebuild scoring around **concept-level structural matching**:
- A `signature_fn` extracts, per domain, a set of canonical **kinematic concepts**, each detected only
  by a *relational phrase* (e.g. `output becomes input`, `first … costly … second … cheap`,
  `long stasis`, `tipping point … chain reaction`), never a lone generic word.
- A pattern matches a domain pair only when **≥ 2 distinct concepts of that pattern are present on
  both sides**. One shared structural feature is a coincidence; a shared multi-feature dynamical
  signature is an isomorphism. This is a general principle, not a per-case filter.
- `signature_fn` and `orthogonality_fn` are both **injectable** (LLM / embedding-backed in
  production); the offline defaults are **deterministic fixtures, labeled honestly as fixtures**, so
  the dogfood runs with no network.

## Kill-condition (the Needle) — FIXED, pre-registered

On the **original, unchanged 12-case bench** in `scripts/echo_detector_dogfood.py`
(5 positives · 3 clean negatives · 4 adversarial decoys), the rebuilt detector must hit, on the
**offline deterministic path** (no network, no injected LLM):

> **adversarial-FP rate ≤ 0.10  AND  recall ≥ 0.80**, at a stated operating threshold, with that same
> threshold also being the default the detector ships with.

Anti-gaming constraints (all binding):
1. The original 12 bench cases are **not edited, reordered, or weakened**. Their `expect`/`adversarial`
   labels stay exactly as F34 measured them.
2. No per-case, per-domain, or per-string special-casing. The concept library and matching rule must
   be domain-general.
3. A **held-out** bench (new positive domains + a *harder* decoy that shares exactly one real concept)
   is added and reported separately; the same rule must pass it **without any tuning against it**. A
   held-out failure is reported, not hidden.
4. If the target cannot be met without violating 1–3, the outcome is an honest "still fails, here is
   why + next" receipt. The bench is never dressed up.

## Verdict slot (filled after the run, not before)

- Original 12-case bench @ default: _to be measured_.
- Held-out bench: _to be measured_.
- F34 loop: closes (new ledger entry) **iff** the kill-condition is genuinely met; otherwise the
  finding is recorded and F34 stays open.
