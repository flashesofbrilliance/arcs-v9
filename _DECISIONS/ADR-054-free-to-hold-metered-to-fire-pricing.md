# ADR-054 — Free to hold, metered to fire: the ARCS activation pricing model

**Status:** Accepted · 2026-08-13

> *"Ass, gas, or grass — nobody rides for free."* Nobody rides the vox animus (ARCS, the ride) for
> free; you pay gas to fire it. The bank is free; the ride is metered.

## Context
Long-standing tension: you cannot monetize the open tool (germinate) without adding the very
friction the public-good goal was meant to avoid. ADR-053 resolves the ontology (dormant seed vs
animating spark); this ADR turns that seam's economic face into a concrete pricing model.

## Decision
**Monetize the spark, never the bank.**

### The three roles
- **The seed is the token.** Free to mint, plant, water, and hold. Portable, carries provenance,
  grants *eligibility* to ride — but does **not** pre-pay the gas.
- **ARCS is the ride.** The vox animus firing: ripeness judgment beyond mechanical token-match,
  converting dormant potential → kinetic at the Kairos moment.
- **Gas is the fee.** You pay to *ride* — the usage-metered cost of activation. Holding potential
  energy is free; igniting it is where the meter runs.

### What is FREE (never metered; lives in germinate, commercial users included)
`mint` · `plant` · `water` · `hold` · **mechanical** `sprout` · `manifest` / `drift-check` ·
`handoff` / serializability substrate · the seed schema and bank format itself.
germinate stays a friction-free MIT public good. No commercial licensing, no license gates, no
metering may be added to the germinate repo (antipattern — enforced by ADR-053's boundary).

### What is METERED (the gas; ARCS-side private service)
- **Ripeness judgment** — deciding whether a seed is genuinely ripe for *this* soil, beyond
  token/soil match (the part germinate's generic contract deliberately cannot do).
- **Kairos activation** — firing the right seed (and the right human) at the opportune moment;
  the "conditional, not scheduled" spark (see the Kairos sketch + public-good #2).
- **Rosetta-primed synthesis / compute** — activation informed by ARCS's private accumulated
  priors (the rosetta stone), not available to a bare germinate install.

### Meter unit
Bill per **activation** (one vox-animus firing) — not per stored seed, not per seat, not per
GB. Storage and holding are free by construction; only ignition runs the meter. This keeps the
incentive aligned with the doctrine: accumulate freely, pay only when you convert potential to
kinetic.

### The token fork — DECIDED: metaphorical now
- **Metaphorical (adopted, ships sooner, no crypto baggage):** seeds = portable credits carrying
  provenance; "gas" = usage-metered activation billing on the ARCS service. No chain, no wallet,
  no token regulatory surface.
- **Literal on-chain (documented, deferred):** seeds = on-chain provenance tokens; gas literal.
  **Revisit only when** the backlogged ARCS blockchain registry AND germinate hash-chaining both
  exist AND a real customer need for cross-party provenance portability is demonstrated. Until
  then, on-chain buys nothing and adds regulatory/UX surface.

## Consequences
- Revenue sits on the spark (activation service/intelligence/compute), never the substrate —
  so open-sourcing germinate costs no revenue.
- Willingness-to-pay is **unvalidated**: validate demand for *the ride* (ripeness/Kairos
  activation), not the bank, before hardening prices. This is the first care-note to revisit.
- Pairs with ADR-053 (boundary) and the activation/Kairos sketch. Proverb: tao-247.

## Lineage
[[seed-monetization-free-to-hold-metered-to-fire]] · ADR-053 ·
[[compaction-serialization-substrate-public-good]] · [[recoil-as-second-product-surface]].
