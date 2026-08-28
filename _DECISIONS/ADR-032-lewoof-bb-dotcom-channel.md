# ADR-032 — Le Woof × Better & Better pilot: lead structure on the .com channel

> **Status:** DECIDED
> **Date:** 2026-08-03
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** On the Le Woof × B&B pilot — now scoped to Le Woof's own .com (Vlad wants Amazon dropped for launch) — which economic structure does Hila push first?

---

## E — Entity / System

Le Woof LLC (Hila) ↔ Better & Better (Vlad; runs Petsie). Channel: lewoofbrand.com (Shopify). 240-unit consignment pilot, 16 oz shampoo, $45 MSRP, Sept–Dec 2026. External to arcs-v9 codebase; hosted brief at lewoof.arcs.care (public/lewoof.html).

---

## W — Window

**Horizon:** QUARTER (4-month pilot)
**Revisit trigger:** 75% sell-through gate; B&B's actual DTC acquisition efficiency; a shift back to Amazon or to B&B's own domain.

---

## Context

Original recommendation (Amazon channel) led with a FLAT fee — simplicity + keep B&B profitable + protect ASIN. Vlad then narrowed to .com only. On Le Woof's own store the economics and risk allocation change materially: no Amazon 15%/FBA fees; Le Woof is merchant of record (cash flow inverts); traffic is bought not found; transparency flips (her dashboard); the asset becomes the customer list/storefront, not an ASIN.

---

## Options Considered

### Option A — 50/50 of net proceeds, B&B funds acquisition from its half (LEAD)
- Pays Le Woof $11.70/unit (fixed, independent of ad spend) — MORE than flat's $8.
- Puts acquisition risk on the operator running acquisition; keeps B&B positive in base/best.
- Cons: B&B goes negative if it acquires inefficiently (relationship strain).

### Option B — Flat fee $10–12/unit (FALLBACK)
- Simplest; Hila's stated preference; B&B safe in all scenarios.
- Cons: pays Le Woof less ($6–8/unit) and mis-parks acquisition risk.

### Option C — 50/50 + $2,400 commitment
- Highest to Le Woof ($5,208) but sinks B&B (−$1,872). Rejected as opener.

---

## Decision

**Chosen:** Option A (50/50 net) as the lead; Option B (flat) as the live fallback; drop the commitment fee.

**Rationale:** On .com it pays Le Woof more AND allocates ad risk correctly AND is transparent because it's her store. Flat kept as the simplicity concession for Vlad.

**Trade-offs accepted:** B&B's pilot P&L becomes hostage to their own DTC acquisition efficiency (unverified vs their Amazon pedigree).

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** MEDIUM-HIGH
**Stability:** STABLE (pending diligence on B&B DTC capability)

**Loki test:** If B&B's DTC acquisition is weak, 50/50-net makes them lose money and sour the partnership; flat would protect the relationship better despite paying Le Woof less. Mitigation: confirm capability, keep flat live, cap pilot, revisit at the gate.

---

## Consequences

Two revised term sheets (50/50-net = recommended, flat = fallback) + revised recommendation memo produced. Non-negotiables shift from ASIN-ownership to customer-data/email-list ownership + merchant-of-record + Faire price consistency. Hosted brief updated at lewoof.arcs.care.

**Implementation pointer:** public/lewoof.html (live brief); Cowork-generated docx set (memo + 2 term sheets); Claude project doc claude/LeWoof_BetterAndBetter_Deal_Memory.md.

on_purpose_label: aligned · irreversibility: low · self-graded NCI ≈ 90

---

## Linked receipts / ADRs

- Supersedes the Amazon-channel flat-fee-lead recommendation (2026-07-31, Cowork session; no ADR).
