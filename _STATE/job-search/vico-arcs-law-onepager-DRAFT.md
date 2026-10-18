# DRAFT: "What ARCS means by coherence" (one page for a reader with no ARCS context)

INTERNAL STATUS: Tier 2 material under the disclosure ladder (it contains a formula). Do not send before a mutual NDA, or decide deliberately to treat it as Tier 1. Not sent. Strip the "Internal notes" block below before sharing. Every claim in the page body traces to `operators/arcs_primitives.py` (lines 13-34, 424-440) or the repo's confidence/conviction definitions; nothing here is a measured result.

---

## What ARCS means by coherence

**One idea.** A belief is about the world. Coherence is not a belief about the world. It is a property of how your beliefs, your certainty in them, and your evidence line up with each other. That makes it a second-order property: it is measured on the relationships, not on any single claim.

**Three layers, kept apart on purpose**

| Layer | Object | What it answers | In statistics terms |
|---|---|---|---|
| Belief | Confidence | How likely is this belief true? (0 to 1, anchored in evidence, not a measured probability) | The posterior probability |
| Belief about the belief | Conviction | How stable is that confidence: would a reasonable amount of new data still move it? (low, medium, high) | The precision (tightness) of the posterior |
| Decision | NCI, Net Coherence Index | How well does the whole decision hang together? Reported once per decision, never per belief | Model fit |

Confidence and conviction are separate axes on purpose. You can hold high conviction that something is false. A confidence number that drops is often a good result: a wrong prior killed at high conviction.

**The Law, in plain terms.** At the operator level, ARCS scores a decision receipt with one line:

`C = 0.5 x A - 0.3 x (S - S_min)^2 + 0.2 x W`, clamped to 0 to 1.

- **A, alignment (0 to 1):** how well the decision passes ARCS's own list of principles (the "axioms"), checked by rule.
- **S, surprise:** the gap between two assessments of the same decision, `|HCI - PCI| / 100`. HCI is the Human Coherence Index (what the person reports). PCI is the Platform Coherence Index (what the system computes independently). S_min is 0: the ideal is no gap.
- **W, witness (0 to 1):** a score from the person's recorded felt signals about the decision (six defined signals).
- The weights (0.5, 0.3, 0.2) are defaults, not fitted values.

The squared term means small disagreements cost little and large ones cost a lot. The point of S is to make a stated assessment and an independently computed one meet, and to show where they do not.

**Tiny worked example (illustrative numbers, not data).** A = 0.8, HCI = 70, PCI = 62 so S = 0.08, W = 0.6. Then C = 0.5 x 0.8 - 0.3 x 0.08^2 + 0.2 x 0.6 = 0.4 - 0.0019 + 0.12 = 0.518.

**What this does and does not claim.** It does not predict events and is not a forecasting score. It audits a person's own decisions against outcomes and against their own earlier stated beliefs. The weights are unvalidated and the number of decisions closed against outcomes so far is two, so there is no accuracy claim.

**In your terms.** If a forecast is a stated probability, ARCS keeps a second record next to it: how settled the forecaster was, and how far their stated assessment sat from an independent one. Your Brier score scores the first against outcomes. S scores the gap between two assessments before the outcome arrives.

---

## Internal notes (strip before sharing)

1. **The call definition conflicts with the repo.** On the call (L193) the definition given was coherence as "a high correlation between conviction and confidence." The repo defines conviction and confidence as independent axes (conviction is the precision of the confidence; "high conviction does not mean high confidence"). Correlating a posterior's mean with its precision is not well defined for one belief, so a quantitative reader may have heard it as muddled. The nearest correct restatement is S (the gap between stated and independently computed assessments) plus A and W. If he asks, say plainly that the call version compressed it and give this one.
2. **NCI has two implementations.** The product layer defines NCI as signal clarity, cross-substrate agreement and path-commitment, reported once per decision. The operator code (`arcs_primitives.py`, NCI formula in the CoherenceReceipt docstring) defines NCI = 0.7 x on-purpose rate + 0.3 x (1 - average irreversibility). The page above states the decision-level meaning and does not quote either formula. Reconcile or label before sharing the canon.
3. **Acronym.** The Litepaper expands ARCS as "Abductive Resonance Chrono-Kairos System"; the call used "Abductive Reasoning Coherent Systems." Settle the current one.
4. **W** depends on six somatic primitives defined in the code; the docstring figures attached to them (for example r=0.72, 76% predictive accuracy, Brier 0.25 to 0.12) have no data behind them that I could find. Do not cite them.
5. **A** depends on the DNA axiom list; confirm the list is shareable at Tier 2.
