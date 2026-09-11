# ADR-075 — The Metabolic Router (mechanical fan-out is automatable; judgment is not)

> **Status:** DECIDED
> **Date:** 2026-09-04 (witnessed live, then promoted the same session via DEWY receipt; ratified here)
> **Author:** Claude (reading-room / Almanac session, with Zach)
> **Stakeholders:** the whole corpus metabolism — `_DECISIONS/`, `_SEEDS/`, memory, `CLAUDE.md`
> handoffs, `_STATE/` receipts, the Atlas/Almanac cache, the drift hooks, `/canon-review`
>
> **Provenance note:** Minted through `oracle.py next adr` (allocated 75; `_SEEDS/_oracle.json`
> committed with it). The number **075 was previously *claimed* by a memory**
> (`pull-not-push-pre-render-legibility-gate`) for a "wired legibility gate" that was never
> minted or merged — the full-temporal Almanac audit (2026-09-04) found 75 was the oracle's
> *next-free* number, i.e. that claim was vapor. This file is the genuine ADR-075; the
> legibility-gate memory is being de-claimed of the number. That very failure (a record
> describing a gate that does not exist on `origin/main`) is one of the things this ADR's
> integrity gate is designed to catch. Witness stub: `_STATE/witness/2026-09-04.jsonl`.

---

## D — The Decision

**Sharp question:** The ARCS corpus has many organs (index, oracle, concordance, cache, canon
queue, drift hooks) but every new primary record is hand-carried to each of them by a human or
an agent acting as the pump. How do we semi-automate that metabolism **without** violating
NOTOMATION (scaffold cognition, never overrule revealed preference)?

**Decision:** Split every fan-out step into exactly two classes and treat the split as law:

- **Mechanical** — deterministic, idempotent, grep-able: index rows, oracle numbering,
  concordance link registration, cache-slice invalidation, re-render, drift detection. **These
  are automated** by a router.
- **Judgment** — classification of form (ADR vs memory vs seed), canon promotion
  (DEROT/ESCALATE/FORK), public projection (what/when to cast, air-gap), VARIANT-vs-SUPERSEDED,
  which factory a hardening accretes to. **These are never automated**; the router surfaces them
  into one queue for a human.

A **routing manifest** (nutrient-type → organs, each organ tagged mechanical or judgment) is the
single source of truth for the fan-out. A new **integrity gate** runs at write-time: every ADR,
commit, or script a record cites must **exist on `origin/main`** (`merge-base --is-ancestor`,
`cat-file -e`); a record citing vapor is routed tagged `DRIFTED-AT-BIRTH`, never silently.

The human stops being the pump. The human keeps being the judge.

---

## E — Entity / System

- `_SPECS/metabolic-router-v1.md` — the implementation spec (routing manifest, integrity gate,
  triggers, v1 wire order). This ADR is the ruling; that is the plan.
- `_ARTIFACTS/atlas/cache-manifest.spec.md` — the coupled cache: every route ends in
  `cache-invalidate (domain, epoch)`; re-grading is lazy, on next read.
- Existing organs the router composes (nothing net-new — verdict FORK-AND-MOD): `/witness`
  (mouth), `scripts/oracle.py` (numbering), `scripts/git-hooks/pre-commit`, the lattice /
  seedbank / memory-sync drift hooks (immune system), `/canon-review` (judgment valve), the Atlas
  curators (digestion), `night-moves` (daily batch).
- `MEMORY.md`, `_DECISIONS/index.json`, `_SEEDS/index.jsonl`, `CLAUDE.md` handoff blocks — the
  mechanical targets.

---

## W — Window

**Horizon:** YEARS. This is the operating law for the corpus, not a feature. Revisit triggers: a
router run auto-promotes something to canon (violation — that is judgment); an integrity check
produces false positives that block legitimate writes (recalibrate the gate, never remove it);
a new organ appears that fits neither class cleanly.

---

## Y — Conviction

**Polarity:** GREEN. **Conviction:** HIGH — the split dissolves the "how much should the
machine do?" question into a mechanical test (is this step deterministic and idempotent?) and
was proven live twice in one session: the corpus went stale in 24h from the author's own fixes
(cache-invalidation is real), and five load-bearing memories were found describing gates never
merged to `origin/main` (the integrity gate is needed). **Stability:** STABLE for the split;
the manifest's *contents* will evolve.

**Gate / falsifier:** the first `metabolize` run routes one new record to every organ in its
row with zero human carrying, AND the integrity gate catches a deliberately-planted cite to an
unmerged commit. If either fails, the doctrine is prose, not wired.

---

## Consequences

- Every gap surfaced from here on is answered with `spec + verdict` (NET-NEW or
  FORK-AND-MOD), per the proactive-spec rule — the router is the machine half of that rule.
- Hardening lessons become a routed nutrient (row: Hardening → judgment: which factory), so
  "every hardening accretes to the factory" becomes a gate, not a good intention.
- The Almanac / Chronicle / Concordance / public projections are all readers of one cached
  backend the router keeps fresh; none of them re-audit.
- `ADR-075` de-claims the legibility-gate memory's false number; that memory routes back
  through the integrity gate as `DRIFTED-AT-BIRTH` until its gate is actually built and merged.
