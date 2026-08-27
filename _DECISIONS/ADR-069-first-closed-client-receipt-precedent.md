# ADR-069 — First closed client receipt: expectation management moves from promise to precedent

> **Status:** DECIDED
> **Date:** 2026-08-26
> **Commit:** (set at merge)
> **Numbering note:** minted in-session against index tail ADR-068; oracle audit pending (counters drift when sessions mint off-oracle — flag on next oracle pass).
> **Lineage:** receipt-calibrated pricing mechanism (2026-08-04, Todd memory shard) → 1.2 ex-ante receipt (deck, Aug 10) → mid-phase update (Aug 18) → close-loop (this session) → THIS. Witness stub: `_STATE/witness/2026-08-26.jsonl`.

---

## D — The Decision

**Sharp question:** Now that the first ex-ante → ex-post receipt has closed in a paying client engagement (and closed RED on the estimate), what governs Todd-facing expectation management going forward?

**Decision:** The closed receipt is canon. All forward expectation-setting with Todd (and, by rule of three, future clients) is **precedent-shaped, not promise-shaped**: every claim about a future phase must cite the banked receipt record, and every phase must produce one.

## E — Entity / System

The Todd/PRL engagement; the receipt-calibrated pricing mechanism; every future ex-ante receipt (1.3+); the prl.arcs.care/status/receipt surface (the public face of the record); by extension, the engagement-flightops component reused on any client.

## W — Window

**Horizon:** YEARS (engagement-lifetime + reusable component).
**Revisit trigger:** a receipt closes and its lesson is NOT converted into the next phase's structure (mechanism becomes theater), or a client-facing claim ships without receipt citation.

## Context

The mechanism was designed 2026-08-04 to fix the exact 1.1 failure (under-estimate, eat it silently). 1.2 ran it end to end: bet written before kickoff ($4,500 / ~20h / wrong-if 12–30h), mid-phase update published when the band broke (Aug 18), close-loop scored honestly (~2.1x central, method disclosed, no timesheet theater). The cap held. Crucially, **the first closed receipt is a losing one on the estimate** — which is what makes it credible rather than marketing.

## The big SO WHAT — how the shape changes for Todd expectation management

1. **"Trust me" is retired; "read the last receipt" replaces it.** Todd is a System-2 self-questioner who wants reasoning shown. The engagement now has case law: every forward number cites backward evidence. This is a stronger trust instrument than any green streak, BECAUSE the first entry is red.
2. **The cap is now proven, not promised.** Todd watched a 2x overrun cost him $0. "You pay the quote, never the overrun" moved from contract language to observed fact. That purchases the right to keep 1.3 at the TOP of its disclosed range without it reading as an ask.
3. **Variance gets named and priced, not absorbed.** The receipt showed coordination (not build) blew the band. So expectation management shifts from "how many hours" to "which preconditions are closed before the clock starts." The pre-start input batch IS the new expectation instrument.
4. **Bands widen honestly instead of estimates inflating quietly.** Future wrong-if bands are set from measured multiplier history (1.2: ~2.1x on coordination-heavy scope), asymmetric where risk is asymmetric. No sandbagging: the bet stays the honest central estimate; the band carries the risk.
5. **The receipt surface is the meeting.** Close-loop conversations happen ON the artifact (prl.arcs.care/status/receipt), Todd's linear-checklist register, one page, altitude arch. Verbal recaps stop being the record.
6. **Losing receipts are publishable.** The gate for what Todd sees is honesty of measurement, not favorability of outcome. This is the [[brand-promise-refusal-to-overclaim]] made structural.

## Options Considered

**A — Quiet close** (bank math internally, tell Todd verbally): rejected — wastes the credibility purchase; the red receipt is worth more shown than hidden.
**B — Re-price 1.3 upward citing the overrun:** rejected — misreads the data (coordination, not build) and breaks the pre-disclosed-range promise; violates the with-Todd re-pricing gate.
**C — Precedent-shaped expectation management + precondition pricing (CHOSEN).**

## Consequences

- 1.3 ex-ante receipt must cite the 1.2 close (multiplier, cause, precondition list) at kickoff.
- Every engagement phase without a closed receipt is an open loop and blocks the next kickoff conversation.
- The pattern is one client instance; second client closing a receipt triggers extraction into the engagement-flightops class (rule of three: ADR-066 ladder).

**Y-state:** GREEN · **Stability:** STABLE (first full cycle observed end to end)
