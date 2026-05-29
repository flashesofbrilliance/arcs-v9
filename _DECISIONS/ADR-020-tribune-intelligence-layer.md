# ADR-020: Tribune Intelligence Layer

**Date:** 2026-05-29
**Status:** DECIDED
**NCI:** OM (architecture derived from existing canon)
**Revisit trigger:** 50+ real receipts in prod; or if CLUE event schema (ADR-TBD) changes the receipt lifecycle model

---

## Decision

Implement the Tribune Intelligence Layer as a three-phase annotation system (Anterior / Proactive / Posterior) that wraps the existing Receipt flow without modifying the sealed ReceiptObject (ADR-019).

---

## Three-Phase Model

### ANTERIOR (Predictive / Pre-mortem)
Before the needle moves. Surfaces: what this class of decision typically breaks on, planning frame gaps, premortem ("if this fails in 6 months, here's why"). Runs before receipt is saved.

### PROACTIVE (Kinematic / During)
Detached observation of decision trajectory in motion. **Silent by default** — emits only when a silence threshold fires:
- BAR tier = Ruin
- Drift state ≥ DERAILMENT
- NCI delta > 15 points within session

When active, surfaces: trajectory drift, evidence bar evaluation (BAR → LAB → Court), fork vs. reinvent signal, Board role objection mapping, anticipatory stakeholder sell-through framing, meta-tooling recommendations (net-new skills/agents to collapse 0→1).

### POSTERIOR (Anticipatory / Post-mortem)
After execution. Surfaces: actual vs. predicted outcome, recoil analysis, baton-forward framing for successor decisions. May run days after the Anterior/Proactive phases.

---

## Architecture

- Tribune stored in a separate `tribunes` table with `receipt_id` FK
- Relationship: 1 receipt → up to 3 Tribune rows (one per phase)
- Generation: per-phase API calls, lazy (on-demand), to `POST /api/tribune` in arcs-v9
- Context payload per call: `{ receipt_id, phase, nci_score, bar_tier, drift_state, clarity_mode, baton_id?, prior_tribune_output? }`
- Runs in arcs-v9 only — requires auth (gate on ADR-016 magic link verified end-to-end)
- Guard: do not ship until at least one receipt is persisting in prod

---

## Canonical Mappings

Do not reinvent. These are already in canon:

| Tribune Concept | Canonical Source |
|---|---|
| Evidence bar tiers | BAR (Baseline / Asymmetric / Ruin) → LAB → Court |
| Stakeholder model | Six Board roles: Detective / Accountant / Loki / Sentry / Alchemist / Elder |
| Kinematic signals (v1) | Intra-session only: NCI delta, drift state (Drift Sentinel), BAR tier, clarity mode |
| Timing / Kairos signals | KKL (not KKR): Kairos / Kairos Lock / Chronos |
| Court auto-escalation | Irreversibility ≥ 0.7, BAR Ruin, or identity wavefunction conflict |
| Cross-session patterns | Deferred — gate: 100+ receipts (L6 engine territory) |

**LAB = Loki + Advisors + Bayesian:**
- L (Loki): Adversarial attack — steelman the opposition, find kill shots
- A (Advisors): Board consensus — what would the elder board recommend?
- B (Bayesian): Probabilistic scoring — posterior probability given current evidence

**Coalition readiness score** = proportion of Board roles resolved to GREEN after LAB pass.

---

## Schema Additions

```sql
-- New table: tribunes
CREATE TABLE tribunes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  receipt_id    UUID REFERENCES receipts(id) ON DELETE CASCADE,
  created_at    TIMESTAMPTZ DEFAULT now(),
  phase         TEXT NOT NULL CHECK (phase IN ('anterior','proactive','posterior')),
  bar_tier      TEXT CHECK (bar_tier IN ('baseline','asymmetric','ruin')),
  lab_result    JSONB,          -- {loki: ..., advisors: ..., bayesian: ...}
  court_invoked BOOLEAN DEFAULT false,
  drift_state   TEXT,           -- from Drift Sentinel
  nci_delta     NUMERIC,        -- NCI at open vs. NCI at decision point
  clarity_mode  TEXT,           -- SIMPLE | RICH | DEEP
  baton_id      UUID REFERENCES receipts(id),  -- forward chain link
  board_votes   JSONB,          -- {detective: 'green'|'red', ...}
  content       JSONB           -- phase-specific generated content
);

CREATE INDEX idx_tribunes_receipt_id ON tribunes(receipt_id);
CREATE INDEX idx_tribunes_baton_id ON tribunes(baton_id);

-- Additive migration on receipts table (nullable, no breaking change)
ALTER TABLE receipts ADD COLUMN IF NOT EXISTS baton_id UUID REFERENCES receipts(id);
```

---

## What This Is NOT

- Not a replacement for the Receipt — Tribune annotates, Receipt is canonical
- Not a new doctrine layer — fully downstream of L0-L7, LAB, Court, and Triune Logic
- Not a campaign/multi-receipt structure (defer to Phase 3+, gate: 50+ receipts)
- Not always-on commentary — Proactive is silent below threshold (Clarity before Curvature)

---

## Y-State

The Tribune makes ARCS anticipatory — decisions arrive pre-mortemed, observed in motion, and debriefed. The receipt chain becomes auditable end-to-end. The Posterior phase closes the Kintsugi loop: detect, repair, re-encode.

---

## Loki Test

"You're just wrapping every decision in AI commentary nobody will read."

Defense: Anterior and Posterior are opt-in phases. Proactive is silent unless BAR Ruin, Drift ≥ DERAILMENT, or NCI delta > 15 fires. SIMPLE mode surfaces one line per phase, not a transcript.

---

## Implementation Order

1. `POST /api/tribune` route with silence threshold gate (Proactive)
2. `tribunes` migration + `baton_id` column on `receipts`
3. Anterior phase generation (runs pre-save)
4. Proactive phase generation (runs mid-session, conditional)
5. Posterior phase generation (runs post-execution, async)
6. UI: Tribune panel on receipt detail view (SIMPLE: 1 line/phase; DEEP: full output)

Gate on: ADR-016 auth verified in prod + ≥1 receipt persisting in prod.

---

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
