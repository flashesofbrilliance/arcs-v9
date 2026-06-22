# ADR-025 — SAGE Signal Validation Path

> **Status:** DECIDED
> **Date:** 2026-06-22
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Should we close the Option B→C gap (text-derived SAGE signal) now, or first build Outcome-logging UX to create the measurement instrument that would tell us if a better signal actually helps?

---

## E — Entity / System

- `operators/arcs_api.py` — SAGE pipeline + `_STAKES_SIGNALS` proxy signal
- `src/app/api/compass/route.ts` — SAGE integration point
- `Receipt` + `Outcome` Supabase tables — the closed-loop data source
- `scripts/sage_efficacy.js` — efficacy validation tooling (currently structurally blocked)

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** `Outcome` row count clears MIN_SAMPLE=20 per SAGE-fired/not-fired cohort, as enforced by `sage_efficacy.js`. At that point, re-open Option A and evaluate text-derived signal against real match-rate/regret deltas.

---

## Context

SAGE shipped 2026-06-19 (commit `99dc0b2`) via Vercel Services FastAPI bridge. The full pipeline — SAGE → LAB → BAR → Court → Kintsugi — runs on every compass call. Only SAGE-shaped fields (`nci_score`, `verdict`, `court_verdict`, `signal_classification`, `is_satoshi`) are extracted back to Claude's prompt via `_extract_sage_fields()`; LAB/BAR/Court detail is computed and discarded.

The signal feeding the pipeline is synthetic: `_STAKES_SIGNALS` maps stakes/horizon combinations to a fixed vector. This is Option B (proxy). The commit message explicitly flags it: "NCI quality from this signal is unvalidated against real decision-quality outcomes. Treat the NCI/court fields as a soft signal Claude reads, not as ground truth."

**Prod DB state as of 2026-06-22 (verified via Supabase MCP):**

| Table | Count |
|---|---|
| `Receipt` | 184 |
| `SageTrace` | 9 |
| `Outcome` | 1 |
| `User` | 2 |

184 Receipts, 1 Outcome = **0.5% close-loop rate**. `sage_efficacy.js` is gated at MIN_SAMPLE=20 per cohort against Outcome rows joined with SageTrace. At current rate, this gate is structurally far away — not "close but no data yet."

The tempting next move is Option A: replace the synthetic signal with text-derived input so NCI reflects actual question semantics. The problem: even a perfect text-derived signal cannot be validated today. The measurement instrument (Outcome-logging adoption) doesn't exist. Building signal precision before the instrument is the same structural error as the synthetic proxy itself — confident-looking work with no way to confirm it helped.

The real bottleneck is the 0.5% close-loop rate. It blocks Option A validation, LAB/BAR surfacing justification, NCI trust, and every future operator efficacy argument — not just this one decision.

---

## Options Considered

### Option A — Close the B→C gap now (text-derived signal)
- Replace `_STAKES_SIGNALS` with a text-derived signal from the compass question
- Pros: NCI reflects question semantics, not just stakes/horizon proxy
- Cons: No instrument to validate the improvement exists — 1 Outcome means any quality delta is invisible. Invests in precision before measurement capability. Same structural error as the proxy it replaces.

### Option B — Downgrade NCI ambitions permanently
- Document the stakes/horizon proxy as intentional; don't surface LAB/BAR output until Outcome data exists; remove NCI from any user-facing display
- Pros: Honest about limitations; no build work required
- Cons: Freezes the pipeline in a state the commit message itself calls unvalidated. Closes the door on operator surfacing as a product direction.

### Option C — Build Outcome-logging UX first
- Make it easy for users to close the loop after a compass call: what did you decide, how did it go?
- Once MIN_SAMPLE=20 clears, re-open Option A with real match-rate/regret delta data
- Pros: Fixes the root bottleneck. Unblocks every downstream operator validation (SAGE, LAB, BAR, NCI trust) simultaneously. Produces a product feature (outcome tracking) users actually benefit from.
- Cons: Defers signal improvement. Requires UX design + Supabase work before Option A is even revisitable.

---

## Decision

**Chosen:** Option C

**Rationale:** The 0.5% close-loop rate is the actual bottleneck, not signal precision. The same gap that blocks Option A validation also blocks LAB/BAR surfacing, NCI trust, and every future operator efficacy argument. Fixing the measurement instrument unblocks all of them simultaneously. Building Option A first is solving for precision before the instrument exists — the same structural mistake as the synthetic proxy.

Option A is not wrong in principle; it's wrong in sequence. Re-scope it as: *build text-derived signal once Outcome-logging adoption clears MIN_SAMPLE=20, so the build can be evaluated against real match-rate/regret deltas rather than vibes.*

**Trade-offs accepted:**
- SAGE NCI remains a soft, unvalidated proxy signal in production until Outcome-logging adoption improves
- LAB/BAR/Court output stays computed-and-discarded for now; no wider extractor until signal is trustworthy
- No governance gates (Architecture Decision 1 soft/hard NCI gate) — SAGE stays advisory-only, gated only by `SAGE_URL` presence

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Strongest case against this decision: Option A is a contained engineering task (replace one function) with no UX dependency, while Outcome-logging UX requires design, adoption, and a long wait for data. You could ship text-derived signal this week and at least have it ready when Outcome data arrives. Counter: "ready when data arrives" assumes the signal design is correct — but without validation data, you're designing in the dark. A wrong text-signal design that bakes in for months is harder to correct than a known proxy. Better to wait and design with data.

---

## Consequences

- **Outcome-logging UX** becomes the next specced feature; needs its own ADR (ADR-026) covering the UX surface, Supabase schema changes, and the MIN_SAMPLE gate definition
- **Option A deferred** — explicitly not abandoned; re-open when `sage_efficacy.js` can produce a result against real cohorts
- **SAGE advisory status preserved** — no regression; pipeline continues running, SageTrace continues logging, fields continue reaching Claude's prompt
- **LAB/BAR surface work deferred** — `_extract_sage_fields()` expansion blocked until Option A is validated
- **Architecture Decision 1 (soft/hard NCI gate)** — explicitly deferred; document in ADR-026 as a decision point once NCI is trustworthy

**Implementation pointer:** ADR-026 (Outcome-logging UX spec) is the next required ADR before any build work begins.

---

## Linked receipts / ADRs

- ADR-008 — RLS deny-all (Supabase auth architecture context)
- ADR-023 — Observability as superionic goal lattice (downstream of receipt/outcome data quality)
- ADR-026 — Outcome-logging UX spec (created by this decision, does not yet exist)
