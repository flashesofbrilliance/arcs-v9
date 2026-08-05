# ADR-042 — ARCS as Coaching Cognitive-Exoskeleton: a direct GTM wedge

> **Status:** DECIDED (direction; first pilot pending)
> **Date:** 2026-08-05
> **Commit:** (set at merge)
> **Numbering note:** ADR-041 is referenced by a machine-local memory (deliverable-durability, local-first) that is not present in `_DECISIONS/` on this branch. To avoid a canon collision under write-lock, this ADR takes 042. Reconcile 041 when that branch merges rather than resolving here.

---

## D — The Decision

**Sharp question:** What is the first concrete, low-ruin GTM application of ARCS to lead with, and how do we frame it so a buyer adopts it without it reading as automation that replaces their judgment?

**Decision:** Lead with the **Call Resonance Read as a coaching instrument** ("the pre/post-call game-day tape"), framed as a **cognitive exoskeleton, not a digital twin**. It augments a person's judgment and never replaces revealed preference (NOTOMATION-clean). The scaling story is **1 → Few → Many**: one person's own tape, then their team gets the read, then the org/category. The offer is a free, non-invasive pilot (receipts are JSON; nothing touches existing systems).

---

## E — Entity / System

The compass pipeline's recoil/receipt machinery (`src/document/screens/RecoilReport.tsx`, `scripts/gen_*_close.py`, `runtime/recoil/generated/*`) repurposed as a **coaching read** over call transcripts. Counterpart of record: **Robin Daniels / Zensai** (CBO, HR-tech, actively building coaching). Adjacent GTM surfaces: the omakase/codex artifact family, the org-scale tenant pattern (cf. Yuri codex).

---

## W — Window

Now. Validated 2026-08-05 by a live buyer signal; the pilot offer is already on the table with one counterpart. The window is the current coaching land-grab in HR/sales-tech (Gong, Salesloft, balance, windmill, ladders all moving), named by the buyer himself.

---

## Y — Y-gate / Conviction

**GREEN-leaning.** Polarity positive (a real buyer mapped it to his own strategy unprompted and asked "how does it deploy"). Conviction rising across a 3-call series (park -> kairos). Stability guarded by one flag: the coaching category is crowded, so the position must be "the pre/post resonance layer," not "another call recorder."

---

## Context

Three serialized calls with Robin Daniels (Oct 23 2025, Nov 13 2025, Aug 5 2026). Call 2 failed on breadth and altitude; call 3 landed when the pitch narrowed and stayed in his register. At the kairos he named the wedge himself: *"this is the big play right now in HR coaching... a coach you wish you had."* That is a buyer defining the category and the emotional frame for us.

Two things make this a real GTM decision rather than a one-off artifact:
1. **It is low-ruin.** It reads recordings that already exist. Nothing to buy, wire, or risk. A wrong read is a conversation, not a failure (BAR-clean).
2. **The frame is the buyer's own thesis.** Robin co-authored a human-first book ("AI is not the outcome, it's just another input"). "Exoskeleton, not twin" is that thesis given a body, which is also ARCS's constitutional NOTOMATION line. The pitch is his idea reflected back, not a new idea sold in.

## Options considered

- **A. Hiring / talent-match wedge** (the original codex lead). Rejected as lead: the buyer never grabbed it; coaching is what he owned.
- **B. A/B testing / analytics wedge.** Rejected: wrong register (analytical, commoditized), no resonance.
- **C. Coaching resonance read, exoskeleton frame (this ADR).** Chosen: buyer-named, low-ruin, on-thesis, and it scales 1->Few->Many.

## Decision detail

- **Product surface:** pre-call brief (ex-ante receipt) + post-call recoil (auto-close scored against reality) + bookmarked teachable/coachable moments. The bookmark set is the coaching payload (see the coachable-moments epoch, `runtime/recoil/generated/2026-08-05-robin-coachable-moments-epoch.md`).
- **Positioning:** "the coach you wish you had," inside the coaching category, as the resonance layer, not a recorder.
- **Guardrail (COURT):** never a digital twin, never "replace the coach." Augment only. Air-gap holds: any scoring's subject stays the operator's own performance, never a scorecard of the counterpart.
- **Ego-stroke guardrail (BAR):** frame the buyer's value as reach/legacy (scale your judgment), not vanity. Substance over flattery, or it backfires with a sharp operator.
- **First step:** a free "Coach's Game-Day Tape" on one real call, non-invasive.

## Consequences

- **Positive:** a concrete, defensible, low-ruin GTM wedge with a named buyer and a scaling path; reuses existing recoil machinery; the frame is honest to NOTOMATION and to the buyer's own philosophy.
- **Cost / risk:** crowded category (mitigated by the resonance-layer position); the frame depends on staying at ground altitude and not re-pitching (the one drift risk flagged in the epoch); pilot delivery needs the coaching-bookmark artifact built.
- **Follow-ups:** build the "Robin Daniels: The Coach You Wish You Had" artifact (1->Few->Many, exoskeleton frame) with the coachable-moments epoch as its "1" proof; send one coaching-framed follow-up, no re-pitch.

## Grounding

- Calls: `runtime/recoil/generated/2026-11-13-robin-daniels-serialization.json`, `2026-08-05-robin-daniels-receipt-close.json`, `2026-08-05-robin-coachable-moments-epoch.md`.
- Live artifact: `robin-codex.arcs.care` (deployed 2026-08-05).
- Related: ADR-038 (recoil bookmark primitive), the counterpart-codex pattern.
