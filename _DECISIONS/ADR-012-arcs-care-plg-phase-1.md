# ADR-012 — arcs.care PLG Phase 1: Compass Model Swap + Lab Offer Card

> **Status:** DECIDED
> **Date:** 2026-05-28
> **Commit:** (set at merge)

## D — The Decision

**Sharp question:** What changes to arcs.care's compass surface maximise free-to-paid conversion — which model should power the live compass and where/how should the Lab offer surface post-result?

## E — Entity / System

- `app/api/compass/route.ts` (arcs-care) — model selection + fallback chain
- `app/compass/page.tsx` (arcs-care) — result surface, Lab offer placement
- `components/lab-offer.tsx` (arcs-care) — new component (receiptId prop, `/call?receipt=` CTA)
- arcs.care Vercel project — deploy target

## W — Window

**Horizon:** WEEK
**Revisit trigger:** First Lab booking confirmed, or conversion rate drops after 2 weeks live.

## Context

P4 (arcs-v9 Vercel deploy) is complete. P5 is the first PLG conversion mechanic: surface a paid Lab offer ($300 strategy session) immediately after a free Compass result. The Compass currently runs on a model with a retired fallback; the offer card doesn't exist yet. This ADR locks the placement strategy before implementation begins.

## Options Considered

### Option A — Inline below receipt (always show)
- Renders Lab offer card immediately below every Compass result
- Pros: maximum exposure, zero friction to see offer
- Cons: may feel premature if user hasn't absorbed the result yet; cheap feel if shown before value is demonstrated

### Option B — Conviction-gated (Y ≥ GREEN or NCI ≥ 65)
- Only surface Lab card when compass returns GREEN+ conviction or NCI ≥ 65
- Pros: offer appears when user already feels traction — highest intent moment; consistent with ARCS earned-fidelity principle
- Cons: users in fog (YELLOW/SCRATCH) never see the offer; lower raw exposure

### Option C — 30-second delay reveal
- Lab card appears 30s after result renders, via CSS animation
- Pros: user has time to read result first; still surfaces on every session
- Cons: JS timer adds complexity; feels gimmicky vs. ARCS tone (Myst, not SaaS)

## Decision

**Chosen:** Option B — conviction-gated Lab card reveal.

**Rationale:** Lab card surfaces only after the user has completed at least one Compass result and received a True North bearing. This prevents price-shock interruption of the sense-making flow — the specific Loki failure: $300 visible before True North renders → user exits without completing the free flow AND without converting. Conviction-gate aligns with NOTOMATION: tools scaffold completed cognition, not in-progress cognition.

**Trade-offs accepted:**
- ↓ Raw Lab card impressions vs. always-show (unknown delta until completion rate is measured)
- ↑ Conversion quality per impression (user has received value before seeing price)
- Revisit trigger: if Lab conversion rate <2% after 50 gated exposures, test earlier (Option A) placement

**Model swap (micro-decision, inline):** Retired fallback in `compass/route.ts` → `claude-sonnet-4-6`. Same model as arcs-v9. No architectural reason to diverge. ~5 min implementation, no separate ADR required.

## Y — Conviction

**Polarity:** YELLOW
**Conviction:** MEDIUM
**Stability:** REVISIT

**Loki test:** If the Lab card renders before the user has read the True North bearing, the $300 price shock interrupts sense-making — user exits without completing the free flow AND without converting. Option B structurally prevents this: conviction-gate = True North has already rendered. Residual risk: users in YELLOW/SCRATCH Y-state never see the Lab card at all, suppressing top-of-funnel exposure. Revisit trigger in W is load-bearing here.

## Consequences

- 4 files changed, ~2h implementation
- Deploy to arcs.care Vercel project
- Verify: POST `/api/compass` → `receipt_id` in response; Lab CTA renders with correct link
- New decision created: which model replaces the retired fallback (minor — likely claude-sonnet-4-6 already in use on arcs-v9)

**Implementation pointer:** `app/api/compass/route.ts`, `app/compass/page.tsx`, `components/lab-offer.tsx` (new)
