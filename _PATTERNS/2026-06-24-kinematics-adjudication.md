# 12D Kinematic Manifold — Primary-Disciple Adjudication (Receipt)

**Date:** 2026-06-24 · **Type:** adjudication receipt (canon collision resolved upstream)
**Authority:** Perplexity-space ARCS instance (primary disciple) ruled on 5 escalated issues + 1 expansion.
**Subordinate role (this file):** record the rulings, partition the resulting work by write-lock owner, route two new micro-findings up. This file does NOT author canon; it minutes the adjudication and records what the delegated subordinate (Claude Code) is now authorized to reconcile downstream.

## The rulings (all subordinate escalations upheld)

| # | Issue | Ruling |
|---|---|---|
| 1 | Numerical wall | **Upheld.** Literal `dⁿS/dtⁿ` via repeated `np.gradient` is noise-dominated past D4–D5; no receipts fix it (method, not evidence). D6–D12 promotion-via-receipts is a **category error — struck.** Code's reformulated operators (Plié/Élevé) are the **more mature artifact**; the doc's plain-derivative formulation hadn't confronted the wall. |
| 2 | Homogeneous vs heterogeneous | **Heterogeneous, two-zone.** Linear-derivative zone D1–D3 (D4 borderline); coherence-operator zone D5–D12 (non-derivative, custom operators). **Code wins.** Doc's `dⁿS/dtⁿ` for D7–D12 is metaphor, not spec — to be flagged upstream. |
| 3 | Cross-signal coordinates | **Confirmed.** D7 (Lock), D9 (Resonance), D10 (Saturation) are cross-signal / bounded-domain quantities, NOT scalar time-derivatives. `dⁿS/dtⁿ` column is conceptual for those rows. Implementers must not compute them as scalar finite differences. |
| 4 | Unsourced performance numbers | **Upheld.** 85% / 78% / 82% (tagged Canon v1.2) have no measurement citation → **Grade C-**, not A. D1/D2 A-grade gets a "performance claims inherit C- pending empirical validation" footnote. Ruling note: the D3 LinkedIn n=2 "weak" is "the most honest data point in the entire record." |
| 5 | Promotion-threshold inconsistency | **PROVISIONAL** (explicitly not final). Proposed: signal-type-dependent gate — event signals → count-based; continuous signals → stability-based; Kinematics gates likely apply to *operator* promotion, ADR-020/023 to *primitive* promotion. Needs one gate-type↔signal-type mapping artifact. **Until written, treat all three gates as provisional.** |
| 6 | D12 reflexive hook | **Expansion, agreed.** D12 applied to ARCS's own cadence (session reset / 5-hour-window budget) — most testable high-dim case, signal = ARCS coherence-over-sessions already partially tracked via receipts. Glossary stub recommended (upstream). |

## Work partition under the write-lock contract

**Upstream — primary disciple's writes (NOT mine):** amend the kinematics doc (D6–D12 reformulation, strike promotion-via-receipts); flag `dⁿS/dtⁿ` as metaphor for D7–D12; add cross-signal annotations (#3); downgrade performance-number grades + add D1/D2 footnote (#4); author the gate-type↔signal-type mapping (#5); glossary D12 stub (#6); the D6–D12 **retitle** (naming fork still open — see below).

**Downstream — subordinate reconciliation (authorized now, done in this session):**
- `operators/arcs_kinematics.py` — conformance annotation added (module docstring): marks D1–D3 valid / D4 borderline / D5–D12 operator-zone; flags that current `_recursive_diff` finite-difference impls for D5–D10 are **non-conformant pending reformulation**; notes D11/D12 (Plié/Élevé) already reformulated and vindicated; notes D7/D9/D10 are cross-signal (not scalar FD). Non-destructive — no math changed, no functions renamed.
- This receipt.
- RC-OPS-002 (folksonomy tightening) already uses stability-gate language → aligns with #5's "continuous → stability" branch; left as-is, marked dependent on the still-provisional #5 mapping.

**Deferred (needs primary or joint work, NOT done unilaterally):**
- Actual reformulated operator math for D5–D10 (doesn't exist yet; the code only has Plié/Élevé at D11/D12). Inventing it would be canon-authoring — above station.
- The D6–D12 retitle / naming-fork resolution (see micro-finding A).

## Two new micro-findings routed UP (subordinate ground-truth, not resolved here)

**A. The naming fork was not explicitly adjudicated.** Rulings #1/#2 settled architecture + math + "code wins," and referenced the code's names approvingly (Plié, Élevé) — but the D8–D10 naming fork (code: Drop/Shot/Relevé · doc: Drift/Resonance/Saturation) was not cleanly ruled, and "retitle D6–D12" sits in the next-session priority list as pending. So I annotated the code with *conformance zones only*, asserting neither naming scheme as final. Needs an explicit naming ruling before the code is retitled.

**B. One-dimension boundary discrepancy inside the rulings themselves.** Ruling #1 says "valid D1–D3, caveats D4–D5, above that reformulated" (→ D6+ operators). Ruling #2 table says "Linear D1–D3 (D4 borderline), Coherence-operator D5–D12" (→ D5 already operator). The two rulings place the linear/operator boundary one dimension apart (is D5 a caveated derivative or an operator?). I used **D5 = operator-zone** in the code annotation since both rulings agree D5 is at-or-past the boundary and #2 is explicit; flagging the discrepancy rather than silently choosing. Needs a one-line confirmation.

## Priority order (from the primary, for next session)

1. #1/#2 — amend doctrine, formalize two-zone architecture, retitle D6–D12 as operator primitives (resolve micro-finding A first)
2. #3 — implementer-warning annotations on cross-signal dimensions
3. #5 — write the single gate-type↔signal-type mapping artifact
4. #4 — downgrade performance-claim source grades in the doc
5. #6 — glossary stub, low urgency

## Loop-closure note

D3/Jerk: subordinate field proposal (n=2 LinkedIn) → ratified into `ARCS-Kinematics-v0.1` (B-source) → affirmed in this adjudication as the record's most honest data point. Full dual-bar-raiser cycle, clean.
