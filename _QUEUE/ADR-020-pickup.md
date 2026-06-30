# Claude Code Pickup — ADR-020: # ADR-020: Tribune Intelligence Layer

> **Status:** DRAFT
> **Generated from:** `_DECISIONS/ADR-020-tribune-intelligence-layer.md`
> **Horizon:** UNSET | **Conviction:** UNSET
> **Auto-generated:** 2026-06-23 18:07 UTC

---

## What was decided

Implement the Tribune Intelligence Layer as a three-phase annotation system (Anterior / Proactive / Posterior) that wraps the existing Receipt flow without modifying the sealed ReceiptObject (ADR-019).

---

## Three-Phase Model

### ANTERIOR (Predictive / Pre-mortem)
Before the needle moves. Surfaces: what this class of decision typically breaks on, planning frame gaps, premortem ("if this fails in 6 months, here's why"). Runs before receipt is saved.

### PROACTIVE (Kinematic / During)

## Implementation pointer

See ADR for details.

## Full ADR

See `_DECISIONS/ADR-020-tribune-intelligence-layer.md` for complete context, options considered, and rationale.

## Done when

`_QUEUE/PENDING.md` ADR-020 row updated to `DONE` + commit.
