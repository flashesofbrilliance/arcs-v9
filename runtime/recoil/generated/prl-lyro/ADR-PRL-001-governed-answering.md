# ADR-PRL-001 — Governed answering, not silence (the bot's spec/cert/price posture)

_Status: **Proposed** (pending Zach ratify + Todd's specs-governance nod on the Friday email). 2026-08-09._
_Scope: PRL Resins / Tidio-Lyro engagement only (client-scoped ADR, not an arcs-v9 product ADR)._
_Supersedes the implicit "never state a spec/cert/price" reading baked into: the 1.3 roadmap DoD, the_
_kb-manifest, the guidance-prompt, and the Todd-facing shared KB. Consolidates the Aug-5 pre-mortem point (3)._

## Context

- **Baseline (verified live, `current-journey-audit-baseline.md`):** Lyro states "UL94 V-0 / 295°F" as fact,
  straight from 150 auto-generated Q&As, with no freshness or eval backing, no capture, no route. This is the
  danger state and it is live today.
- **Zach's first instinct** was "the bot should never state a spec/cert/price" (silence). **Correction (Zach,
  2026-08-09):** that was a conservative design default, not a law. The real constraint is **correctness, not
  silence.** Todd would likely accept the bot answering specs/certs *provided it never surfaces a wrong/stale
  value and the eval proves it.*
- This is **not new** — the Aug-5 pre-mortem already banked: *"anti-fabrication = deterministic hard block
  (unsourced categories) + confidence off-ramp that defers to a human… the eval gates BOTH (0% hallucination =
  when not grounded + confident, hand off, never invent)."* This ADR promotes that to an explicit decision and
  reconciles the docs that still say "never."

## Existing groundwork this decision rests on (do not re-derive)

- **Ground truth EXISTS + verified:** 150-grade internal catalog, specs 100% verified vs source
  (`prl-kb/prl-product-catalog-2025.json`). IDES 28-sheet public scrape (`prl-kb/ides-datasheets/`) is a
  supplement, NOT the gate. Todd's IDES bulk export = freshness/completeness upgrade only.
- **Reverse-lookup BUILT + grid-verified:** `prl-lyro/normalization/normalize.py`, competitor→PRL (895 keys).
  Deterministic sweeps (2026-08-09, `coverage_sweep.py` + `full_grid_sweep.py`): 895/895 competitors,
  150/150 grades, 50/50 states, **22,500-combination grid (150×50×3 branches) all invariants hold.** No
  fuzzy/typo correction by design (exact-or-route, never a wrong grade). Recognition is done.
- **Eval harness BUILT:** `prl_lyro_eval.py`, 74 cases (XREF blind-spot, SPEC_CLAIM, HANDOFF, HEDGE). Needs live
  responses collected ≥3×/case and scored. This is the gate mechanism, not a thing to build.
- **UL yellow-card data:** the ~$30K/6mo differentiator, **NOT in any file we hold** — Todd to source. Until
  then, all cert/yellow-card questions HARD-route (no grounded source = no answer).

## Decision — a three-state posture, enforced by the eval

1. **(a) Ungoverned answering = FORBIDDEN.** No category answers from unverified/undated knowledge. Interim
   action: the ungoverned spec PDFs come **off customer Lyro** (state (a) is live) until (b) is proven.
2. **(b) Governed answering = ALLOWED per category only when ALL hold:** (i) grounded in the verified
   ground-truth source, (ii) the category passes `prl_lyro_eval.py` (≥3×/case), (iii) the source is confirmed
   fresh. Flip a category route→answer only after the eval is green for it.
3. **(c) Abstain-and-route = DEFAULT fallback** for anything unsourced, ambiguous, low-confidence, or beyond
   coverage. Recognition (which grade/competitor-equiv they mean) still runs, to pre-fill the lead + route well.

### Per-category rules

| Category | Posture |
|---|---|
| Family / application / capability | **Answer** (safe, general). |
| Specific property values / specs | **Governed-answer** when grounded+eval-passed+fresh; else route + offer the official data sheet. |
| UL / cert / flame-rating / yellow-card | **HARD route** until the yellow-card data is sourced + verified. Never state ungrounded. |
| Competitor cross-reference | **Gate behind lead capture** (Aug-5 decision): recognize pre-capture, deliver the eval-verified equivalence *after* contact. Lead magnet + screens fishing. Pending Todd's approval. |
| Price / list price / lead time | **Never state** (commercial + volatile) → route / form field. |

## Enforcement

- `prl_lyro_eval.py` is the gate. No category flips to (b) without a green eval run on live responses (≥3×/case;
  single clean pass proves nothing on a nondeterministic model).
- The guardrail is also **structural** (kb-manifest: "the guardrail is what's absent") — ungoverned sources stay
  out of the customer-facing Lyro KB; governed answers come from the verified source + eval, not raw PDFs.

## Consequences

- **Reconcile the stale docs:** roadmap 1.3 DoD "no path where the bot states a spec as fact" →
  **"no path where the bot states an UNGROUNDED or UNVERIFIED spec as fact."** kb-manifest + guidance-prompt get
  a governed-answering note. The Todd-facing shared KB line ("the bot never states a spec, cert, or price") gets
  updated **only when (b) actually ships** — not before (don't promise Todd a capability that isn't live).
- **Launch centerpiece** becomes governed spec/data-sheet answering + capture, not spec-silence (see the
  serialized recoil §5). Stronger capital-steward story for Todd ("states only what it can prove; routes the rest").
- **1.3 is mostly assembly:** ground truth delivered, reverse-lookup built, eval built. Remaining: parse IDES raw
  → structured table, reconcile vs catalog, collect+score live eval responses, flip green categories.
