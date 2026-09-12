# ADR-072 — Engine-Sovereignty Gradient (engines are tenants, the receipt history is the freehold)

> **Status:** DECIDED
> **Date:** 2026-08-28 (doctrine minted 2026-08-19 from a witnessed moment; ratified as an ADR here)
> **Author:** Claude (canon-governance session)
> **Stakeholders:** ARCS substrate / compass pipeline / GIGI seam
>
> **Provenance note:** This doctrine circulated since 2026-08-19 but had **no ADR file** — only the
> memory `engine-sovereignty-gradient-receipts-freehold` claimed "ADR-067", a number that actually
> belongs to `ADR-067-cross-subject-comparative-recoil.md` (both allocated off-oracle the same day).
> Per the human ruling (2026-08-28), the doctrine is minted as its own **oracle-issued ADR-072**.
> This number is corroborated by `ADR-071-mobius-one-surface-triune-invariant-gravity-well.md`, whose
> DEWY receipt already refers to "engine-sovereignty (ADR-072)" as the same Möbius strip traversed over
> time. `_SEEDS/_oracle.json` committed at 73 (72 = this, 73 = the model-routing renumber). The memory
> has been de-claimed of "067" and now cites this file.

---

## D — The Decision

**Sharp question:** As the predictive engine behind ARCS changes over time (cloud LLM → JEPA → GIGI),
what is sovereign and what is replaceable — and what must survive every such swap unchanged?

**Decision:** The predictive engine is a **replaceable tenant**; the write-locked receipt history is
the **freehold**. Engine swaps are two-way doors; receipt/DEWY schema changes are one-way doors
(COURT). The engine roadmap is the temporal chain-of-custody ladder applied to the substrate — a
*sovereignty gradient* where each rung shrinks the third-party trust boundary:

```
NOW    cloud LLM (rented cortex)
NEXT   JEPA trained on the user's own receipts
LATER  GIGI — fully local, airgapped, client-side (nothing leaves the body)
```

---

## E — Entity / System

- `src/app/api/compass/route.ts` — the GIGI seam is a **reserved socket** here; never "clean it up."
- Receipt / DEWY schema (`prisma/schema.prisma`) — the freehold. Serialized world-state that every
  engine projects over but none may mutate on swap.
- The engine (currently Claude Sonnet in the compass route) — the tenant.
- `ADR-071` (Möbius / triune / gravity well) — same substrate seen topologically: engine-sovereignty
  is that one non-orientable surface traversed over *time* (one freehold history, many tenant engines).

---

## W — Window

**Horizon:** YEARS. Holds across the full engine roadmap. Revisit triggers: a JEPA prototype exists
and must consume the receipt corpus as-is; a schema change is proposed (that is a COURT one-way door,
gated separately); GIGI reaches airgapped viability.

---

## Y — Conviction

**Polarity:** GREEN. **Conviction:** HIGH — the freehold/tenant split dissolves the malformed "when
do the Python operators and the Claude pipeline fuse?" question and gives engine swaps a lawful path.
**Stability:** STABLE.

**Loki test (strongest case against):** *"You are over-abstracting. There is one engine today (an
LLM) and the JEPA/GIGI rungs are aspirational — declaring a 'sovereignty gradient' now is doctrine
ahead of implementation, and the reserved socket at compass/route.ts is dead code you are forbidding
anyone to remove."*

**Response:** The doctrine's cost today is one comment and one un-removed seam — cheap insurance
against a one-way mistake (baking engine assumptions into the receipt schema). The **falsifier makes
it honest, not aspirational:** the first JEPA prototype must consume the receipt corpus *as-is*
(projection yes, mutation no); if it cannot, the freehold claim is wrong and this ADR is falsified.
Vision decks that present JEPA/GIGI in present tense must carry a NOW/NEXT/ASPIRATIONAL slide
(temporal chain of custody) before traveling — see [[temporal-chain-of-custody-fact-vs-fiction]] and
[[brand-promise-refusal-to-overclaim]].

---

## Consequences

- Receipt/DEWY schema changes are one-way doors (COURT); engine swaps are two-way doors.
- The GIGI seam at `compass/route.ts` is protected — a reserved socket, not cruft.
- Serializability is not just audit (past coherence) but also simulation (one canonical world-state to
  fork pre-mortems from) **and** migration strategy (swap the physics engine under one serialized
  history without forking the world).
- **Falsifier (standing):** first JEPA prototype must project over the corpus without mutating it.

---

## Linked

- Memory: `engine-sovereignty-gradient-receipts-freehold` (source witness moment)
- `ADR-071` (Möbius one-surface / triune / gravity well) — the topological companion.
- `git-is-the-write-lock-untracked-is-the-gap` · `generative-recoil-live-culture` ·
  `compaction-serialization-substrate-public-good` · `three-modes-inference-corroboration-arc-weld`
- Distinct from `ADR-067-cross-subject-comparative-recoil` (which holds the real 067).
