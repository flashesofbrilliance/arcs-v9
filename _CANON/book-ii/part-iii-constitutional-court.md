---
title: "Part III — Constitutional Court & Agency"
series: "ARCS Field OS — Book II: The Decision Manifold"
version: "0.1.0-DRAFT"
status: "CANONICAL"
audit: "Upstream ARCS audit — CONDITIONAL CLEAR. Four items patched 2026-05-26 before commit."
created: "2026-05-26"
governing_physics: "WORLD.md"
governing_spec: "arcs-field-os/specs/orient-prd.md v0.1.0"
memory_anchor: "MEMORY.md v4.0 — SINE-IRA CHECKPOINT, HEAD/HEART/WALLET, HIGH-STAKES rule"
depends_on:
  - "_CANON/book-ii/part-i-firehose-to-compass.md"
  - "_CANON/book-ii/part-ii-rom-axioms.md"
---

# Part III — Constitutional Court & Agency

---

## Not Every Decision Goes to Court

Most compass runs are straightforward. The NCI lands, the Y-gate scores, the Brief renders. You read the bearing, orient yourself on the terrain, and move. The session takes ten minutes. The receipt freezes the coordinate. You're done.

Court is different. Not because the analysis is harder — sometimes Court decisions are analytically clear within minutes — but because of what the topology requires before the receipt can be sealed. One-way doors. Asymmetric downside. The category of choice where the consequence of being wrong cannot be absorbed in the same time horizon as the decision itself.

And, underneath all of that: the specific material you already know that you haven't yet been willing to face.

---

## The Agency Boundary

The Court does not deliberate. It surfaces.

Everything the Court produces was already in the room — the consequence you'd been rounding down, the relationship cost you'd been filing under "I'll deal with that later," the financial implication you'd modeled but hadn't said out loud. The Court's job is not to introduce new information. It is to force existing information into the session before the receipt is sealed.

This is where **NOTOMATION holds hardest**. A system with enough context about the operator and the terrain could plausibly render a verdict. It could run the BAR analysis, assess the HEAD/HEART/WALLET completeness, and output: *"Go."* or *"Don't go."* The Court resists this with more force than anywhere else in the pipeline.

The reason is structural. At the clarity ridge, a Green NCI-87 bearing is the system doing its job: surfacing the earned orientation. At the Court boundary, a verdict from the system would be the system doing *your* job — the part that requires you to sit with what you know, face what you've been avoiding, and move from a position that is yours rather than inferred.

There is a practical test for where the boundary runs: if receiving a verdict from the system would feel like *relief* rather than *information*, you have crossed into Court territory. Relief signals that the decision's weight is real and that you have been deferring it. That deferral is the thing the Court is designed to end — not by deciding for you, but by making the deferral impossible to continue.

**Receipt:** `MEMORY.md v4.0` — *"No commands, only offers. No authority, only earned pattern-recognition. The user's lived experience always outranks the system's inference."* `WORLD.md` — *"The system's job is to surface: 'You're free-soloing this decision. Any slip is unrecoverable. Are you sure you want this topology?'"*

---

## Convening Conditions

Four tests. A decision qualifies for Court when the following are true:

**1. Irreversibility in window.** The decision cannot be undone within the same time horizon as its consequences. Taking a senior role cannot be undone in a week. Ending a funding round cannot be undone in a month. The topology is one-way: commitment and consequence are on the same timeline; error correction is not. This is the Write-Lock condition applied to a live decision — you are about to step through a door that will not reopen on demand.

**2. Asymmetric downside.** The cost of being wrong is materially larger than the benefit of being right. Not just high stakes — *asymmetric*. When being right produces a recoverable gain and being wrong produces an unrecoverable loss, the decision requires the BAR pass: Baseline ruin, Asymmetry, Reversibility — in that order. The asymmetry must be named before the bearing can be trusted.

**3. Avoidance signal.** The operator has been deferring the decision without being able to name why. Not deferral for missing information — delay in the presence of sufficient information, or delay that has persisted past the point where more information would change anything. The avoidance is a signal. It means something is known that hasn't been faced. The Court is the mechanism for facing it.

**4. HEAD/HEART/WALLET tension.** All three dimensions are active and not aligned. The analytical case points one direction. The energy read — what the operator actually feels in their body when they sit with the decision — points another. The financial or opportunity cost points a third. A decision where all three align does not require Court. A decision where they diverge does.

One heuristic that synthesizes all four: ask yourself what you would feel if this decision were made for you right now. Notice whether the answer is relief or disappointment. Relief — the quiet exhale of having the weight lifted — is data. It signals that the decision's topology is real and that you have been deferring it. That signal is what the Court is designed to end. The desire to outsource the call is not weakness. It is a data point about the topology.

**Receipt:** `src/app/api/compass/route.ts` — `selectMode()`: HIGH stakes → COURT; `doorClass()`: ONE_WAY. `WORLD.md` — *"Stakes = existential, reversibility = zero → mode = COURT."* `MEMORY.md v4.0` — HEAD/HEART/WALLET rule (verbatim).

> **ROM CANDIDATE [RC-III-001] — STRUCTURAL:** The relief heuristic ("feel relief, not disappointment, at having this decided for you") is a synthesizing diagnostic not yet formally receipted as a COURT trigger. Directionally grounded in the agency boundary analysis above. Promote to ROM when confirmed across multiple documented Court-mode session transcripts.

---

## What Court Produces

Three passes. One sealed receipt.

**The BAR pass runs first.** Baseline ruin risk: what is the worst-case outcome if True North is wrong — and can the operator survive it? Asymmetry: is the upside/downside ratio defensible, or does the structure of the bet require the operator to be right far more often than is realistic? Reversibility: what does it cost to change course after commitment, and in what window?

Each field produces a verdict — PASS, TENSION, or BLOCK. TENSION means the analysis identified a real concern that does not prevent moving but must be named in the receipt. BLOCK means the Court found a condition that, unresolved, makes the bearing unreliable. A single BLOCK does not end the session. It creates a HOLD that asks: can this condition be addressed before committing?

**The HEAD/HEART/WALLET check runs second.** If any of the three is absent or stubbed in name only — just the label without substantive content — the Court returns HOLD. Naming WALLET is not the same as running the WALLET analysis. ARCS will not issue a "go" until all three fields carry actual content: the analytical case (HEAD), the energy read (HEART), and the financial or opportunity cost (WALLET). A recommendation built on HEAD alone is not a Court receipt. It is an analysis that has mistaken one dimension for the full picture.

**The SINE-IRA pass runs last for decisions with relational or role dimensions.** The test: state the decision in neutral language that neither side would dispute. Ask what the "other side" — the other person, the competing option, the part of you that has been arguing against — would say is the sanest version of your position. If the neutral restatement fails twice, the recommendation stays in DRAFT with a HOT label. HOT means the Court saw something that hasn't resolved yet. The receipt exists but is not sealed. The operator knows why.

The output is a Court receipt: BAR verdicts, HEAD/HEART/WALLET completeness, Court verdict in one sentence, and the Y-gate polarity lock — the conviction state that represents what was earned after the Court ran.

**Receipt:** `MEMORY.md v4.0` — SINE-IRA CHECKPOINT (verbatim): *"If neutral restatement fails twice, keep the recommendation in DRAFT and label it HOT, not ROM."* HEAD/HEART/WALLET rule (verbatim). `arcs-canon.md` — BAR macro: Bayesian / Adversarial / Ruin. `src/app/api/compass/route.ts` — `reasoning.court` structure: verdicts PASS / TENSION / BLOCK; `court_verdict` one-sentence summary.

---

## The Cost Receipt

A founding team brings on a third co-founder to cover operations. The analytical case is clean: the company has scaled past what two people can manage, the candidate has the relevant experience, the reference checks pass. The decision goes to offer.

What did not run:

**HEART:** One of the two founders had a persistent low-grade drain in meetings with the candidate. Not opposition — nothing he could name. He filed it under *"I'm probably just tired."* No one asked him to sit with it long enough to know whether it was signal or noise. → The energy read, unexamined, became the operational culture mismatch that surfaced publicly in the first board meeting.

**WALLET:** The option pool math against the Series A timeline had not been modeled at the grant size the incoming co-founder expected. Filed under *"we'll sort that out in diligence."* → The unmodeled dilution became the primary obstacle to closing the Series A eighteen months later.

**SINE-IRA:** Neither founder had stated the decision in neutral language. The frame was *"we need operational help and this is the best candidate we've seen."* The unstated alternative — what the candidate herself might have said was the sanest version of the founding team's position — was never surfaced. → The incoming co-founder entered with a mental model of the role that neither founder had formally countered; the gap between her model and theirs was the substrate for both downstream failures.

What was hidden? Nothing. Every piece of this was available in the room before the offer went out. The energy read existed. The dilution math was computable. The neutral restatement was askable.

The Court would not have prevented the decision. It may not even have changed it. What it would have done is make the founders face what they already knew before the receipt was sealed. If they moved after that — eyes open, named conditions, explicit about the TENSION on HEART and the BLOCK on WALLET until resolved — the receipt would carry that. They would have been moving from declared ground, not undeclared ground.

The cost of skipping Court on a write-lock-worthy decision is not always a bad outcome. Sometimes the outcome is fine. The cost is the loss of the ground itself: you made a one-way move from a position you hadn't verified was yours.

> **ROM CANDIDATE [RC-III-002] — STRUCTURAL:** The co-founder example above is a composite constructed from documented failure patterns in founding team formation. It is not a receipted ARCS session transcript. Promote to ROM when Observatory contains a verified session example of the same pattern with documented outcome data.

---

## The Locked State

When Court completes and the operator moves, the Y-gate reaches a state that cannot be produced by analysis alone.

LOCKED is not GREEN. GREEN is high conviction earned from the terrain — the signals aligned, the NCI is sharp, the bearing is clear. It is a reading of where you are. LOCKED is post-Court: you faced the hard material, you sat with the Loki counter until it either broke your position or didn't, you named the TENSION and chose to move anyway. It is not a reading of the terrain. It is a declaration about the ground you are standing on.

The difference shows in what comes next. A GREEN receipt is the input to the next decision. A LOCKED receipt is the foundation the next decision builds from. When a decision becomes the load-bearing premise of everything that follows — a company direction, a key hire, a committed partnership — the ground it stands on needs to have been tested, not just read.

LOCKED also carries a specific implication for NOTOMATION. At GREEN, the system can still surface new terrain information that might shift the bearing. At LOCKED, the operator has moved past the point where terrain updates revise the decision — the ship has sailed, and the appropriate mode is execution, not re-orientation. The system's role shifts: no more counterfactual branches, no more "but what if" tributaries. The receipt is sealed. The work now is in the world.

**Receipt:** `arcs-canon.md` — Y-gate LOCKED state: *"Post-Court resolved — Kairos Lock active."* `arcs-field-os/specs/orient-prd.md` §3 L2 — LOCKED polarity: *"Post-Court resolved — user is executing, not deciding."* `arcs-canon.md` — WRITE-LOCK: *"One-way gate decisions require explicit write-lock declaration before commit. Irreversibility is declared, not assumed."*

---

## What Part III Established

The Court is the mechanism by which the ROM axioms become operative at the moment of a specific decision. NOTOMATION holds hardest here because the temptation to deliver a verdict is strongest here. The agency boundary is the line between surfacing what the operator knows and deciding what the operator should do. The Court does the first. Only the operator can do the second.

Four conditions convene the Court. Three passes produce the receipt. One state — LOCKED — marks the ground the operator earned by going through it.

Part IV maps how a session is structured from first input to frozen receipt: the PrepSession, the API, the session lifecycle, and how continuity works across broken context windows.

---

## Confirmed Gaps in This Draft

| ID | Claim | Status | Upgrade path |
|---|---|---|---|
| RC-III-001 | "Relief, not disappointment" heuristic as Court diagnostic | ROM CANDIDATE — STRUCTURAL | Promote when confirmed across multiple documented Court-mode session transcripts |
| RC-III-002 | Co-founder cost receipt example | ROM CANDIDATE — STRUCTURAL | Promote when Observatory contains a verified session example with documented outcome data |

All other claims anchored to committed receipts listed inline.

---

*End of Part III — v0.1.0 CANONICAL. Upstream audit: CONDITIONAL CLEAR (2026-05-26). Four patches applied before commit: HEAD/HEART/WALLET stubbing rule made explicit (names alone insufficient, all three fields require substantive content); relief heuristic reframed as observational ("notice what you feel") not prescriptive; "may not have changed the decision" line confirmed and preserved; all three cost receipt items given inline causal chains to their specific downstream consequences.*
