# ADR-067 — Engine-Sovereignty Gradient: receipts are the freehold, engines are tenants

**Status:** DECIDED (doctrine, named from a witnessed moment)
**Date:** 2026-08-19
**Y-state:** GREEN — the pattern was already load-bearing before it was named (the GIGI seam, the
conservative receipts schema, and the serializability doctrine all pre-date this articulation)
**Sequence:** allocated via oracle (trued from a stale counter: oracle held adr=65 while ADR-066
existed on disk — the same drift class the lattice tripwire flagged this session; counter set to 67)
**Witness stub:** `_STATE/witness/2026-08-19.jsonl` (verbatim, timestamped, GREEN)

## Context

A morning arc (2026-08-19) connected three threads that had been filed separately:

1. **Serializability is a simulation property, not just an audit property.** One total order of
   writes gives coherent history (the database framing) — but it is also the precondition for an
   honest pre-mortem: you can only fork counterfactuals from exactly one canonical world-state.
   Every parallel-maintained artifact is a phantom branch the loss-aversion analysis must either
   enumerate (combinatorial blowup) or ignore (silent blind spot). "Feed from the deployed
   instance, never parallel-maintain" (ADR-066 live-culture) is therefore a *predictive
   survivability* requirement, not hygiene.

2. **Three constitution decks triangulate one physics.** The interstitium framing (ARCS as the
   receipt-carrying medium between organs — not an organ), the Abductive Constitution (ARCS as
   geometry: receipts as coordinates, trajectories, gradient ascent on personal coherence), and
   the Constitutional Layer (ARCS as law: write-lock, Never rules, kill gates). Medium, geometry,
   law — the standard decomposition of a physics, arrived at from independent directions
   (corroboration-as-arc-weld).

3. **Zach supplied the missing 1%, verbatim:** *"now = LLMs, next = JEPA, later = Gigi (local
   airgapped all client side)."* The engine roadmap IS the temporal chain-of-custody ladder
   (NOW / NEXT / ASPIRATIONAL) applied to the substrate itself.

## Decision

**The predictive engine is a replaceable tenant; the write-locked receipt history is the
freehold.** ARCS's migration path is a *sovereignty gradient* — each engine generation moves
prediction closer to the person and shrinks the third-party trust boundary:

| Rung | Engine | Trust boundary | Chain-of-custody tier |
|---|---|---|---|
| NOW | Cloud LLMs (Claude L0–L5 pipeline) | Rented interpretive cortex; receipts transit a vendor | NOW |
| NEXT | JEPA world-model trained on the user's own receipts | Self-trained latent model; internet priors out of the loop | NEXT |
| LATER | GIGI — local-first, airgapped, fully client-side substrate | No external party in the trust boundary at all; nothing leaves the body | ASPIRATIONAL |

Operational consequences:

1. **Schema conservatism is strategy, not caution.** The receipts schema is the only layer that
   survives all three engines — it is JEPA's training corpus and the ground truth GIGI
   serializes. Breaking schema changes are one-way doors (full COURT treatment); engine swaps
   are two-way doors so long as history stays serialized.
2. **The GIGI seam at `src/app/api/compass/route.ts` is a reserved socket, not backlog.** It is
   the endgame's mount point and stays dormant-but-present. Do not "clean it up."
3. **Serializability is the migration strategy.** Keep one canonical write-locked history and
   the physics engine underneath can be swapped without forking the world. Migration risk
   concentrates entirely in custody of the log, not capability of the engine.
4. **Interstitium closure at the last rung:** interstitial fluid does not leave the body; GIGI
   is what makes the medium literally the user's own. The sovereignty gradient is the product's
   privacy story and its NOTOMATION story converging on the same endpoint.
5. **Claims discipline (ADR-044 / refusal-to-overclaim):** vision artifacts (the three
   constitution decks) present JEPA in the present tense; any such artifact that travels beyond
   a knowing counterpart must carry the NOW/NEXT/ASPIRATIONAL line explicitly.

## Falsifiable claim

If the receipts schema fails to carry a future engine — i.e., standing up the JEPA rung requires
a breaking rewrite of historical receipts rather than an additive projection — this ADR's
freehold claim is wrong and must be revisited. Conversely, the ADR predicts: the first JEPA
prototype consumes the existing receipt corpus as-is (projection/embedding allowed, mutation
not).

## Lineage

ADR-066 (generative recoil / live culture) · ADR-044 (temporal provenance) · git-is-the-write-lock
memory · GIGI seam (AGENTS.md backlog P2, now re-classified reserved socket) · witnessed
2026-08-19, promoted same day.
