# ADR-044 — Temporal-Provenance Gate: capability claims carry fact-vs-fiction chain of custody

**Status:** ACCEPTED · **Date:** 2026-08-10 · **Supersedes/relates:** ADR-039 (refusal to overclaim), ADR-035 (Commit-NCI), [[temporal-chain-of-custody-fact-vs-fiction]]

---

## D — The Decision

**Sharp question:** How do we stop ARCS from stating *aspirational* capabilities ("model-agnostic, runs on Gemini, nothing leaves Google") as *present fact*, when the system has no formal mechanism to distinguish what is true NOW from what is only true of a future/hypothetical deployment?

**Decision:** Every claim ARCS makes about **its own capabilities** carries a temporal placement — **NOW** (shipped + verified), **NEXT** (in flight), **ASPIRATIONAL** (design intent) — with provenance. **Fiction-vs-non-fiction IS the NOW-vs-not-NOW line.** Enforced by machine: a `temporal_provenance()` gate in `scripts/forge_counterpart.py`, wired into `run_gates` beside the fabrication/honesty checks, **refuses to write** when an aspirational-capability phrase ships without a temporal hedge or attribution to a product that genuinely is it.

---

## E — Entity / System

`scripts/forge_counterpart.py::temporal_provenance()` + `run_gates`; every counterpart surface the forge emits (Yuri + Robin families). Denylist `_ASPIRATIONAL_CAPABILITY` (model-agnostic, runs on Gemini, nothing leaves Google/the building/your side, air-gapped); clearance via `_TEMPORAL_HEDGES` (could / would / an internal version / Claude today / on your stack / …) or `Agentum` proximity (his product genuinely is model-agnostic).

---

## W — Window

**Horizon:** DURABLE (constitutional-adjacent — an extension of the refusal-to-overclaim brand promise, ADR-039).
**Revisit trigger:** when ARCS ships a genuinely model-agnostic runtime (then "model-agnostic" moves NOW and leaves the denylist), or when the heuristic produces a false-positive that blocks a legitimately-hedged write (tune the hedge window / add a hedge token).

---

## Y — Yellow gate

**Polarity/Conviction/Stability:** GREEN. The failure it prevents is a confirmed, high-cost class (a false capability claim to a technical counterpart inverts trust). The mechanism is the same primitive ARCS already trusts (the ex-ante receipt = temporal chain of custody for decisions), turned on the product. Validated on first run.

---

## Context

The 2026-08-10 false claim ("model-agnostic, runs on Gemini, nothing leaves Google") was not a typo — it was **aspiration leaking into the present tense** with nothing to catch it. ARCS runs on **Claude/Anthropic** today; a Google-internal Gemini deployment does not ship yet. The irony: ARCS *already has* this mechanism for the object level (the ex-ante receipt files a bet at T-minus and scores it at T-plus — fiction resolved to non-fiction), but never turned it on **claims about ARCS itself**, so "model-agnostic" never had to pass its own Loki test. This also cuts against the hyperstition pipeline (Ethereal → Loki Test → Receipt → ROM): the claim skipped Ethereal straight to ROM.

---

## Options Considered

- **A — Catch it by vigilance (status quo).** Rejected: it failed once already; a technical counterpart (Yuri, who built a genuinely model-agnostic product) would catch what we miss.
- **B — Ban the phrases outright.** Rejected: "nothing leaves your side" and "model-agnostic" are TRUE of Agentum and true of a *hedged* future ARCS claim; a blunt ban over-cuts.
- **C — A temporal-provenance gate that requires a hedge or product-attribution (chosen).** Refuses unhedged present-tense aspiration; passes honestly-hedged and Agentum-attributed claims. Same enforce-or-waive doctrine as the fabrication gate.

---

## Decision & Consequences

**Chosen: C.** On first corpus sweep the gate caught a **second** live instance the hand-fix missed — Robin's one-door ("air-gapped … nothing leaves Zensai") — now hedged honest. The whole counterpart corpus passes clean.

- **Positive:** the honesty hole is closed by machine, not by attention; extends ADR-039 from a promise to an enforced gate; a capability claim can now be written as a mini-receipt (`CLAIM: model-agnostic · NOW: Claude · SCORE-BACK: when Gemini ships`).
- **Cost/Risk:** heuristic (phrase + hedge-window), so it can false-positive; mitigated by the `Agentum` exception and a generous hedge window, and by being tuneable (extend `_ASPIRATIONAL_CAPABILITY` / `_TEMPORAL_HEDGES`). It checks the counterpart forge surfaces only, not arbitrary ARCS copy elsewhere — a future generalization could lift it into a shared lint.
- **Follow-up:** consider lifting the check into a repo-wide content lint; consider a first-class `status` field (NOW/NEXT/ASPIRATIONAL) on capability claims in SSOTs so the gate reads intent instead of inferring it.
