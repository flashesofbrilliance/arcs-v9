# ADR-025 — SAGE Signal Validation Path

> **Status:** DECIDED
> **Date:** 2026-06-22
> **Commit:** b8e98e5
> **Amended:** 2026-06-22 — Consequences corrected post-ground-check (debrief UX already shipped; ADR-026 reframed as delivery fix)

---

## D — The Decision

**Sharp question:** Should we close the Option B→C gap (text-derived SAGE signal) now, or first fix Outcome delivery to create the measurement instrument that would tell us if a better signal actually helps?

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

184 Receipts, 1 Outcome = **0.5% close-loop rate**. `sage_efficacy.js` is gated at MIN_SAMPLE=20 per cohort against Outcome rows joined with SageTrace. At current rate, this gate is structurally far away.

**Post-draft ground-check (2026-06-22):** The 0.5% close-loop rate is not a missing-UX problem. `src/app/debrief/[receiptId]/page.tsx` is fully built: matched/what/regret/learning form, receipt recap card, wired to a scheduled debrief email. The bottleneck is a broken delivery pipeline:
- `reminderDate` only sets from `parsed.reminder_iso`, which only exists when a PrepSession includes `outcomeHorizon`. Compass without a PrepSession never gets a debrief email.
- Resend scheduling has a 30-day ceiling; receipts with `reminderDate` >30 days out fail silently (logged in commit `8ded67f`, unfixed).
- Debrief emails were firing at 5am ET (UTC bug) until commit `8ded67f` this morning.
- No in-app nudge exists; debrief is purely email-triggered.

The decision framing — "fix the measurement instrument before building signal precision" — is correct and unchanged. Only the mechanism of the fix changes: it’s a delivery repair, not a UX build.

---

## Options Considered

### Option A — Close the B→C gap now (text-derived signal)
- Replace `_STAKES_SIGNALS` with a text-derived signal from the compass question
- Pros: NCI reflects question semantics, not just stakes/horizon proxy
- Cons: No instrument to validate the improvement exists. Invests in precision before measurement capability. Same structural error as the proxy it replaces.

### Option B — Downgrade NCI ambitions permanently
- Document the stakes/horizon proxy as intentional; don’t surface LAB/BAR output until Outcome data exists
- Pros: Honest about limitations; no build work required
- Cons: Freezes the pipeline in a state the commit message itself calls unvalidated.

### Option C — Fix Outcome delivery pipeline first
- Repair the broken delivery path so the already-built debrief UX actually reaches users
- Once MIN_SAMPLE=20 clears, re-open Option A with real match-rate/regret delta data
- Pros: Fixes the root bottleneck. Unblocks every downstream operator validation simultaneously. No new UX surface required.
- Cons: Defers signal improvement. Adoption still opt-in; MIN_SAMPLE may take weeks regardless.

---

## Decision

**Chosen:** Option C

**Rationale:** The 0.5% close-loop rate is the actual bottleneck, not signal precision. The debrief UX is built and correct; it’s simply not reaching users due to delivery bugs (prep-gated eligibility, 30-day Resend ceiling, timezone bug, no in-app fallback). Fixing delivery is lower-cost and higher-leverage than building a new signal.

Option A is not wrong in principle; it’s wrong in sequence. Re-scope as: *build text-derived signal once Outcome delivery is repaired and MIN_SAMPLE=20 clears, so the build can be evaluated against real match-rate/regret deltas.*

**Trade-offs accepted:**
- SAGE NCI remains a soft, unvalidated proxy signal until Outcome delivery is repaired and adoption improves
- LAB/BAR/Court output stays computed-and-discarded; no wider extractor until signal is trustworthy
- No governance gates (Architecture Decision 1) — SAGE stays advisory-only, gated only by `SAGE_URL` presence

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Option A is a contained engineering task with no UX or delivery dependency. You could ship text-derived signal this week and have it ready when Outcome data eventually arrives. Counter: without validation data, you’re designing in the dark. A wrong text-signal design that bakes in for months is harder to correct than a known proxy.

---

## Consequences

- **ADR-026** covers the debrief delivery fix: eligibility extension (all receipts, not just prep-originated), long-horizon scheduler for the 30-day Resend ceiling, and in-app fallback surface. **Not a UX build — the UX already exists.**
- **Option A deferred** — explicitly not abandoned; re-open when `sage_efficacy.js` produces a result
- **SAGE advisory status preserved** — no regression
- **LAB/BAR surface work deferred** — `_extract_sage_fields()` expansion blocked until Option A is validated
- **Architecture Decision 1 (soft/hard NCI gate)** — deferred; revisit in ADR-025 re-open

**Implementation pointer:** ADR-026 (debrief delivery fix) is the next required ADR.

---

## Linked receipts / ADRs

- ADR-008 — RLS deny-all (Supabase auth architecture context)
- ADR-023 — Observability as superionic goal lattice (downstream of receipt/outcome data quality)
- ADR-026 — Debrief delivery fix (created by this decision)
