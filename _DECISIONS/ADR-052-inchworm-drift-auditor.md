# ADR-052 — Inchworm drift-auditor for orphaned artifacts

**Status:** Accepted · 2026-08-11

## Context
The knowledge lattice (runtime/specs/knowledge-lattice-v1.json) was an owner-less, epoch-pinned
snapshot decaying by neglect (claimed "32 ADRs"; repo had 44) and shipping stale to a prospect surface.

## Decision
Give owner-less artifacts an inchworm auditor across both session boundaries (`scripts/lattice_drift_check.py`):
- **OPEN** (session-start): orient — check drift vs repo truth, emit a receipt to `_INBOX/`.
- **CLOSE** (pre-compact): advance — regenerate ONLY the mechanical countables (idempotent; writes
  only on real drift). Node statuses, edges, and prose stay human-authored (NOTOMATION).

## Consequences
The orphan can't silently rot; the judgment layer stays a receipt for the human, never auto-rewritten.
Note: this ADR is what makes the "44 ADRs" self-referentially true going forward.
