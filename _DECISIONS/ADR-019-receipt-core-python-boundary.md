# ADR-019 — receipt-core Python Boundary: ReceiptObject as Wire/Storage Type

> **Status:** DECIDED
> **Date:** 2026-05-29
> **Commit:** (set at merge)

## D — The Decision

**Sharp question:** Should `ReceiptObject` (Pydantic, `arcs_dewy`) be the canonical Python
runtime type replacing `CoherenceReceipt`/`DecisionReceipt` everywhere, or should it be the
wire/storage format only — with `DecisionReceipt` staying as the internal operator type?

## E — Entity / System

- `arcs_dewy/schema/receipt.py` — `ReceiptObject` (Pydantic v2, 38 fields, Supabase wire type)
- `arcs_primitives.py` — `CoherenceReceipt` dataclass (internal operator output)
- `arcs_receipt_core.py` — `DecisionReceipt` dataclass + `ReceiptStore` (local JSON log)
- 6+ operators (`arcs_operators_sage.py`, `lab`, `bar`, `curator`, etc.) — all produce `CoherenceReceipt`
- `arcs-worker/scanner/receipt_scanner.py` — reads `receipt-book/` → `ReceiptEvidence`; already ReceiptObject-shaped
- Supabase `Receipt` table (`owdiiyvphyifukygvxhg`) — write target for sealed receipts
- `receipt-book/` — 18 sealed JSON examples (ReceiptObject shape)

## W — Window

**Horizon:** Phase 7 implementation (active sprint)
**Revisit trigger:** Operator suite requires Pydantic validation at internal pipeline boundaries
(performance/correctness signal, not anticipatory)

## Context

Perplexity research + ACL pattern analysis from 2026-05-29 session. The boundary question
resolved to industry consensus: Pydantic at system edges (DB, API, file I/O), dataclasses
for internal pipelines. Key forcing function: 6+ operators all return `CoherenceReceipt` —
rewriting all of them is a large blast radius with no correctness gain at the operator level.

## Options Considered

### Option A — ReceiptObject everywhere (replace CoherenceReceipt)
- Single canonical type throughout the Python runtime
- Pros: One schema to maintain; Pydantic validation everywhere
- Cons: Rewrites all 6+ operators; Pydantic overhead in tight inner loops;
  forces Pydantic into places that only need lightweight dataclasses;
  high blast radius for a boundary question (irreversibility ↑)

### Option B — ReceiptObject at wire/storage boundary only (chosen)
- `CoherenceReceipt`/`DecisionReceipt` remain as internal operator types
- Bridge (`arcs_dewy` bridge) translates to `ReceiptObject` at write time
- `ReceiptObject` owns: Supabase upsert, filesystem JSON seal, RAG corpus writes
- Pros: Zero operator rewrites; ACL pattern (Anti-Corruption Layer); minimum steps to coherence
- Cons: Bridge must be kept in sync as fields evolve; one additional translation step

### Option C — Dual-schema forever (no bridge)
- Keep both types with manual JSON serialization at write sites
- Rejected immediately: already the current broken state (receipt-core gap)

## Decision

**Chosen:** Option B — `ReceiptObject` is the wire/storage boundary type.
`DecisionReceipt`/`CoherenceReceipt` remain as internal operator dataclasses.
The bridge is the Anti-Corruption Layer.

**Implementation scope (no operator rewrites needed):**
1. `ReceiptStore.write()` → calls bridge → validates as `ReceiptObject` → writes sealed JSON + upserts Supabase `Receipt` table
2. `ReceiptStore.seal()` method added — marks receipt as immutable, stamps sealed_at
3. `receipt_scanner.py` — already correct (reads ReceiptObject-shaped JSON), no change
4. Root `decision_receipt_phase*.json` files — one-time normalization pass via bridge
5. Bridge round-trip test in CI — ensures no field silently dropped on translation

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH (NCI: 82 — lifted from 58 after research resolved boundary question)
**Stability:** STABLE

**Loki test:** "Bridge silently omits new required fields added to ReceiptObject — operators
keep writing old shapes and Supabase rows are malformed."
Counter: CI round-trip test validates `CoherenceReceipt → bridge → ReceiptObject` on every
commit touching either type. Pydantic raises `ValidationError` on missing required fields — fail
fast at the bridge, not silently at the DB.

## Consequences

- `arcs_receipt_core.py`: add `seal()`, wire `write()` → bridge → Supabase upsert
- `arcs_dewy/bridge.py`: must map all `CoherenceReceipt` fields to `ReceiptObject` fields
- CI: add `tests/test_receipt_bridge_roundtrip.py` before any operator can be called "Phase 7 done"
- ADR-017 (TypeScript receipt-core canonical schema) is a parallel but separate concern — both
  ADRs must be DECIDED before any Supabase `Receipt` table write path goes live
