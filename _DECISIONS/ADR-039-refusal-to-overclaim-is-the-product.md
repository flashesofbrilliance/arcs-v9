# ADR-039 — The refusal to overclaim is the product (survivability, not immunity)

**Status:** Accepted (RC-grade brand-positioning decision) · **Date:** 2026-08-01
**Related:** ADR-017 (receipt schema), WORLD.md (BAR/free-solo), `/terms` ("a covenant, not a
liability shield"), memory `brand-promise-refusal-to-overclaim`, Tao verse xxvii.

## Context
ARCS advises on irreversible, high-consequence decisions. The tempting positioning is
"protection." That is a lie with teeth: overclaimed protection manufactures false safety, which
is strictly worse than known exposure, because it stops the user watching the cracks.

## Decision
ARCS **never claims to shield or to grant immunity.** Its promise is two smaller, truer things:
1. **Fewer blind fragilities** — surface the gray swans (modelable edges/conditions/blindspots).
2. **Slips that survive being wrong** — the BAR move: re-rig the decision so a single slip is
   recoverable. Survivability, not immunity.

This honesty is **one spine at three altitudes**, and they must stay consistent:
- **Physics:** there is a Lyapunov horizon; ARCS maps gray swans but cannot see past it (black swans).
- **Product:** `defer`, the confidence-floor, DRAFT-withholding, and BAR are the *wired* refusals
  to claim certainty ARCS does not have. The map never lies about how certain it is.
- **Terms:** "a covenant, not a liability shield."

## Consequences
- No surface, artifact, or copy may promise protection/immunity/"we've got you covered."
- Any output must be able to state where its own horizon ends (`defer`/confidence carry it).
- **Corollary — the record is the survivor.** On a long horizon the survival rate → 0; the
  goal is the *receipt*, made durable/immutable/content-hashed/signed so it outlives the
  decider and lets ruin be reconstructed forensically, witness-free. Durability is therefore
  **core promise, not a B2B upsell** — it makes the refusal-to-overclaim honest at the record
  layer too.
- **Enforcement (follow-up):** a copy-lint that fails on immunity/shield language on any public
  surface (parallels `leak_check.sh`); ledger entry when wired.
