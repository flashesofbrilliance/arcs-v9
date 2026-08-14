# ADR-049 — RESERVED (awaiting best-fit backfill)

**Status:** RESERVED · 2026-08-13 · allocated-by: gap-stub (ADR-057 oracle convention)

## Why this stub exists
This number was a true gap (free on main AND across all branches) below the high-water mark. Per the
user's convention (2026-08-13) — *"stub the missing pieces and figure out the logical best-fit as we get
new ADR stamps"* — it is reserved as a self-documenting placeholder so the namespace stays contiguous and
no reader mistakes it for a lost decision.

## Best-fit hint (from neighbors)
Sits between ADR-046 (witness) / ADR-047 (model-tier-routing) and ADR-050 (federated-family) /
ADR-051 (drift-receipt) — the **routing → governance/family-infra** era. A future decision in that theme
(or a human-ratified collision-mover, see `_INBOX/adr-collision-remap.jsonl`) is the natural fill.

## How to fill
Replace this file with the real ADR (keep the number). Do NOT hand-guess a NEW number — draw it from
`scripts/oracle.py next adr` so the namespace stays serialized.
