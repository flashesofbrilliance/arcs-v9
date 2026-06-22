# ADR-021 — ROM A/B/C Rigor Layer: Trigger-Gated, Not Built Now

> **Status:** DECIDED
> **Date:** 2026-06-22
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Do we retrofit ROM A (Coherence Audit), ROM B (Dual-Wave Adversarial),
ROM C (Eudaimonistic Probe) onto the live SAGE wiring now, or hold the design and wait for a
concrete trigger?

---

## E — Entity / System

- `src/app/api/compass/route.ts` — calls `${SAGE_URL}/api/sage-score` as an advisory block;
  this is where any of ROM A/B/C would attach if built
- `prisma/schema.prisma` `SageTrace` model — `fired`, `signal` (raw SAGE JSON), `failureReason`,
  `latencyMs` — the only existing instrumentation; no coherence-flag field exists today
- `.claude/rules/arcs-invariants.md` — holds the ROM A/B/C design, explicitly marked
  "proposed, NOT yet enforced" as of this session
- `operators/arcs_api.py` `run_pipeline()` — where ROM B's pre-synthesis adversarial pass
  would actually execute, if built

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger (the actual gate, not vague language):**
- **ROM A:** `SageTrace` rows where `fired=true` and the parsed `signal.nci_score` diverges
  from the paired `Receipt.nciScore` by more than 20 points, in ≥10% of fired traces over any
  trailing 30-day window. This is computable today with no schema change — `signal` already
  carries SAGE's own `nci_score`/`verdict`.
- **ROM B:** a real incident where a receipt's True North visibly anchored on a premise in
  the question that should have been challenged before synthesis (the same class of failure
  ADR-013's Loki test already worries about in a different context) — not a hypothetical, an
  actual receipt.
- **ROM C:** a product requirement surfaces for explainable rigor — e.g. an enterprise/B2B
  prospect or advisory client asks "how do you know this isn't just vibes," and "not vibes 🧾"
  (the launch positioning, ADR-025) needs a literal answer beyond the NCI self-grade that
  already ships.

Any one of these firing is sufficient to re-open this ADR and scope the corresponding piece
— not all three need to fire together, and not all three need to be built together.

---

## Context

SAGE integration shipped via `/svc/sage` (Vercel Service) + `SageTrace`, a simpler path than
the `phase-1-2-1-sage-integration-week-1.md` plan (2026-06-19) specified — that plan's
subprocess-bridge/signal-adapter/canary-rollout machinery never deployed and is now dead
weight, cleared by this session. The one part of that plan not addressed by what shipped is
the ROM A/B/C research-grounded rigor layer (coherence audit, pre-synthesis adversarial wave,
goal-threat/hedonic fork) — genuinely good thinking, grounded in cited research (Karvetski &
Mandel 2020; Fariña et al. 2003; Nussbaum 2001), but speculative relative to this product's
actual failure modes. SAGE is live, useful, and has surfaced no coherence failures yet
because nothing is currently measuring for them.

---

## Options Considered

### Option A — Shelf it
- Pro: zero cost now.
- Con: loses the thinking; "shelved" designs rot the same way the dead plan did.

### Option B — Build all three now
- Pro: ships the rigor layer while the research framing is fresh.
- Con: no known failure mode is driving it; risk of building the same kind of
  speculative-but-unused scaffolding that just got cleared out of CLAUDE.md this session.

### Option C — Trigger-gated ADR; build only what fires *(chosen)*
- Keep the design (already written, in `.claude/rules/arcs-invariants.md`) explicitly marked
  as proposed-not-live.
- Define concrete, measurable trigger conditions per ROM candidate (above) instead of a
  vague "revisit later."
- When a trigger fires, scope and build that one ROM candidate — not all three reflexively.

---

## Decision

**Chosen:** Option C.

**Rationale:** The plan that originally produced ROM A/B/C also produced a large amount of
machinery (subprocess bridge, new adapter, new Receipt columns, canary rollout) that never
shipped because a simpler path made it unnecessary. That's a pattern worth not repeating —
build what a live failure mode or product need actually demands, not what a research thread
implies should exist in principle. ROM B has the clearest path to cheap validation (a
prompt-layer addition to `run_pipeline()`, no schema change) if its trigger ever fires.

**Trade-offs accepted:** If a coherence failure or anchoring incident happens before any
trigger is monitored for, we find out from the incident itself, not from a dashboard. No
automated check currently watches the ROM A trigger threshold — it requires someone to query
`SageTrace` manually. That's an acceptable cost for a quarter-horizon, medium-stakes decision.

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** The sharpest case against: nobody is actually watching the ROM A trigger
threshold, so "trigger-gated" could quietly become "never," same as Option A, just with
better paperwork. Mitigation: the threshold is cheap enough to check by hand
(`SELECT signal, receiptId FROM "SageTrace" WHERE fired=true` joined against `Receipt.nciScore`)
that it can be folded into the existing `sage_efficacy.js` periodic check (already run
manually per `arcs-session-state.md`) rather than requiring new automation.

---

## Consequences

- Unblocks: nothing was blocked — this just formally closes the loop on the stale plan.
- Creates: an explicit, checkable trigger condition instead of an open-ended "someday."
- Amends: none.

**Implementation pointer:** none yet — by design. If/when a trigger fires, the implementation
pointer is `.claude/rules/arcs-invariants.md` (design already written) +
`src/app/api/compass/route.ts` (attachment point) + `operators/arcs_api.py` `run_pipeline()`
(where ROM B's pre-synthesis pass would actually run).

---

## Linked receipts / ADRs

- CLAUDE.md Handoff v2.1.0 (2026-06-22) — corrected record of what's actually live vs. proposed
- `.claude/rules/arcs-invariants.md` — the ROM A/B/C design itself, marked proposed-not-live
- ADR-025 — Go-Live Provisional Logic ("not vibes 🧾" positioning — ROM C's trigger relates)
