# Book II — Part VI: The Shared Court
## *How ARCS operates when more than one agent is bound by the receipt*

**Status:** CANONICAL  
**Version:** v1.0.0 / 2026-05-26  
**Layer:** Multi-party extension; forward spec only — no implementation dependencies  
**Structural parallel:** Parts III (constitutional court) + V (accumulation/gates)

---

## §6.0 — The Single-Agent Ceiling

The constitutional court in Part III was designed for one sovereign. It assumes a single agent who holds the question, sets the stakes, weighs the evidence, and receives the ruling. Every gate from L0 to L5 is calibrated to that assumption. The Accumulation Protocol in Part V extends it — but only inward, tracking how a single agent's priors shift across time.

Neither Part addresses what happens when two people must make a decision together and both must live with the receipt.

The gap is structural, not incidental. When two parties enter a shared decision, they bring different priors, different stakes assessments, and potentially different framings of the question itself. The existing pipeline has no mechanism for surfacing that disagreement before L5, recording it afterward, or establishing whose framing governs when the two conflict. A receipt issued under those conditions is not a joint decision. It is one person's decision with another person's name on it.

Part VI closes that gap. It does not replace the constitutional court. It extends the court's jurisdiction to sessions where more than one agent is bound by the outcome.

---

## §6.1 — Parties, Roles, and Standing

A shared session requires a defined roster before the pipeline opens. Every participant must be assigned one of two roles before L0 begins: Initiator or Respondent. Participants named on the receipt who hold neither role are recorded as witnesses — a receipt-level annotation, not a protocol role.

Initiator. The party who opens the session and submits the PrepSession. The Initiator sets the initial question framing, proposes the stakes tier, and is responsible for ensuring all parties with standing are present before L0 begins. There is exactly one Initiator per shared session.

Respondent. Any party with formal standing to contest gate conditions, challenge a stakes assessment, or enter a bound dissent before L5. A session may have one or more Respondents. A Respondent who is not present at L0 cannot be added mid-session; if a required Respondent is absent, the session must HOLD until they are present. Standing cannot be transferred or delegated in v0.1.x; if a Respondent cannot participate, the session either waits or is rescoped to a session type in which the absent party is not required.

Witnesses. Parties named on the receipt who have neither Initiator nor Respondent status. A witness carries awareness binding: they cannot later claim the decision was made without their knowledge. This is a weaker and different property than structural binding — the quorum acknowledgment and gate co-signature that Initiators and Respondents carry. Structural binding has protocol consequences (a party with structural binding can force a HOLD, enter a bound dissent, and must co-sign gates); awareness binding has none. Witnesses have no in-session rights — they may provide context if invited, but cannot contest a gate, cannot force a HOLD, and cannot block L5. A witness annotation does not require the witness's signature to close the session.

Standing is binary. Either a party holds it or they do not. The distinction between Initiator and Respondent is a distinction of origin, not of authority: at L3 and L4, both parties' stakes assessments carry equal weight. The Initiator does not break ties by virtue of having opened the session.

---

## §6.2 — The Dissent Record

A shared court that cannot record disagreement is not a court. It is a ratification machine. The Dissent Record exists to prevent that collapse.

The Dissent Record is a first-class field on every shared receipt. It is always present — empty if no dissent was logged, populated if any party with standing entered an objection before L5. Its presence does not indicate failure. A receipt with a populated Dissent Record is not a contested receipt. It is a more honest one.

A bound dissent has three required components: the name of the dissenting party, the scope of the objection, and the acknowledgment of binding. Scope must be specific — a dissenting party does not object to the receipt in the abstract; they object to a named element: a gate threshold, a stakes tier, a compass axis weighting, or a specific clause in the L4 ruling. A dissent without a defined scope is not a valid bound dissent and cannot be entered into the record. The court must ensure the dissenting party specifies scope before the session can proceed; a dissent without a defined scope is not a valid bound dissent and cannot be entered into the record.

The acknowledgment of binding is the dissent's defining feature. By entering a bound dissent, the dissenting party affirms: I object to this element of the ruling, and I accept this receipt as authoritative for future reference. The objection is real. The binding is also real. Neither cancels the other.

A bound dissent does not alter the ruling. The L4 deliberation produces one outcome; the Dissent Record annotates how parties with standing related to that outcome. A ruling with three parties accepting and one entering a bound dissent on the stakes tier is still a single ruling. The dissent is not a minority report. It is a named marker that the stakes tier was contested and that the dissenting party's objection is part of the receipt's lineage.

The Dissent Record is immutable once the session closes. A party cannot amend, retract, or add a dissent after L5. If a dissenting party later changes their view, that change belongs in a new session — a debrief, a follow-on shared session, or an Arbitration Session if the original dissent meets escalation thresholds. Clerical errors in the Dissent Record — wrong party name, incorrect scope transcription — can be corrected only by opening a new session that cites the original receipt and issues a narrow amendment receipt documenting the correction. The original receipt remains unchanged in the lineage; the amendment receipt becomes the authoritative reading of the errored field going forward.

---

## §6.3 — Deliberation Protocol

A shared receipt is valid only when every party with standing is bound by it. In a shared session, quorum is reached when all Initiators and Respondents either accept the ruling or log a bound dissent — a named objection recorded in the Dissent Record that nonetheless acknowledges the receipt as authoritative for future reference. Unanimity of agreement is not required. Unanimity of being bound is. If any party with standing refuses both to accept and to enter a bound dissent, the court cannot close the session. The pipeline must move to HOLD or escalate to an Arbitration Session, and no shared receipt is issued until the deadlock is resolved.

The L0–L5 pipeline runs in shared sessions with three modifications.

L1: Question sharpening may surface conflicting framings. In a solo session, L1 produces a single sharpened question. In a shared session, each party with standing contributes their framing independently before the framings are reconciled. If the framings are compatible — different angles on the same underlying question — L1 produces one sharpened question that the court accepts as the session's governing statement. If the framings are incompatible — addressing genuinely different questions — L1 must surface that conflict explicitly. The session cannot proceed to L2 with two unreconciled questions. Either the parties resolve the framing conflict and produce a single governing question, or the session HOLDs. Splitting into two separate solo sessions is a valid resolution. When a shared session dissolves this way — at L1, before a governing question was ever established — it produces no shared receipt. The shared session leaves no lineage artifact of its own; its existence is recorded only in the downstream solo sessions' PrepSessions, which must note that the shared session was attempted, the framing conflict that emerged, and the split that resulted.

L3: Stakes assessment must be reconciled across parties. Each party with standing submits a stakes assessment independently. If all parties agree on the tier, the session proceeds. If parties disagree, the higher tier governs — the court does not average stakes assessments, and the party with the lower estimate does not override the party with the higher one. A party who believes the stakes tier is wrong may enter a bound dissent on that specific element; the higher tier still applies to the session's gate conditions. This rule exists because understating stakes in a shared decision harms all parties, not only the one who underestimated. The asymmetry is deliberate: any party can force higher-tier constraints by submitting a higher stakes assessment, and no party can prevent this by entering a bound dissent — the higher tier applies regardless. The design accepts that stakes will occasionally be overstated in exchange for ensuring they are never systematically understated.

L4: Deliberation must account for the Dissent Record without requiring unanimity. The L4 ruling is produced by the court's deliberative process, not by vote. In a shared session, L4 must explicitly acknowledge any objections raised during L1 or L3 — not to resolve them in the ruling, but to confirm they were heard and that the Dissent Record is the appropriate place to carry them forward. The ruling stands. The dissents annotate it.

---

## §6.4 — Shared Receipts and Lineage

A shared receipt carries the same immutability and lineage properties as a solo receipt. Once issued at L5, it cannot be altered, retracted, or amended by any party. Any downstream session that references a shared receipt inherits its full lineage — including its Dissent Record. A party cannot strip the dissents from a receipt before citing it in a new session.

Shared receipts differ from solo receipts in one structural respect: their delta gate declarations must be co-signed.

Delta gates were defined in Part V as the conditions under which a prior receipt loses its authority over a downstream decision — the magnitude, direction, or time-decay thresholds that determine when accumulated drift requires a new session rather than a continuation. In a solo session, the agent who issues the receipt sets those gates unilaterally. In a shared session, that unilateral authority does not exist. A gate set by one party alone is a gate the other party had no standing to contest. A receipt whose gates were set that way is a receipt the non-setting party can always claim they would have set differently.

Co-signing closes that gap. All parties with standing must be present at L5 to co-sign gate declarations; if any party with standing is absent at L5, the session must HOLD until they are present, for the same reason it must HOLD at L0. Before L5 issues a shared receipt, every party with standing must either accept the proposed gate conditions or enter a bound dissent scoped to one or more specific gates. The same quorum rule that applies to the ruling applies to the gates: unanimity of being bound, not unanimity of agreement. A gate condition that one party accepts and another disputes in a bound dissent is still a valid co-signed gate — the dispute is part of the lineage. A gate condition that one party refuses to acknowledge at all cannot be part of the issued receipt. Such refusal forces the session to HOLD. If the unresolved gate refusal persists and a downstream session would rely on the affected receipt's gate conditions, the HOLD is a candidate trigger for an Arbitration Session as defined in §6.5 — specifically, if all three Arbitration preconditions are met: a shared receipt with a populated Dissent Record (or unresolved co-signing deadlock), a pending downstream session, and a formal declaration that the dispute materially affects that session's gate conditions.

This rule connects directly to the no-retroactive-gate-setting principle from §5.2. In a solo session, that principle prevents an agent from redefining gate conditions after the fact to avoid triggering a required new session. In a shared session, the co-signing requirement enforces the same principle at the moment of issuance: the gates must be set when all parties with standing are present and bound, not before one party arrives or after another has left.

One boundary the co-signing requirement does not cross: it does not give Respondents veto authority over gate values. A Respondent who believes a time-decay threshold is too long may enter a bound dissent. They cannot block the session from closing by refusing to acknowledge any threshold at all. That refusal is not a bound dissent — it is a refusal to be bound, and it triggers the HOLD rule from §6.3.

---

## §6.5 — The Arbitration Session

An Arbitration Session is a special shared session type triggered not by drift detection but by escalated dissent. It is the court's mechanism for resolving a deadlock that the ordinary pipeline could not close — specifically, the case where a prior shared receipt carries a Dissent Record that has not been resolved and a downstream session would rely on that contested receipt to govern its gate conditions.

An Arbitration Session is not a retry of the original session. It does not re-run the L0–L5 pipeline over the original question. Its jurisdiction is narrower: it addresses only the specific element or elements named in the escalating dissent, and it produces a revised receipt that either affirms the original ruling on those elements, modifies it, or issues a HOLD pending conditions that must be met before the downstream session can proceed.

Three conditions must be met before an Arbitration Session can open. First, a shared receipt must exist with a populated Dissent Record. Second, a downstream session must be pending that would cite the receipt as part of its lineage. Third, the dissenting party must formally declare that the unresolved dissent materially affects the downstream session's gate conditions — that the dispute is not abstract but has a specific consequence for what the next decision requires. This declaration is directed to all parties with standing on the original receipt, and it is appended as an annotation to that receipt's lineage before the Arbitration Session opens. It does not alter the original receipt; it becomes a lineage record that the arbitration output will cite. An Arbitration Session opened without all three conditions is not a valid arbitration. It is a re-litigation of a closed receipt, which the court does not permit.

The Arbitration Session roster follows the same role structure as any shared session: Initiator, Respondents, and witnesses. The original parties with standing have standing in the arbitration. New parties may be added as Respondents only if all existing parties with standing consent. The arbitration cannot redefine who was bound by the original receipt; it can only add parties who agree to be bound by the arbitration's output.

What arbitration can produce: a revised receipt with a new quorum ruling on the contested elements, co-signed under the same rules as §6.4. The revised receipt does not replace the original. It sits in the lineage downstream of it, explicitly citing the original receipt and the Dissent Record that triggered the arbitration. Any downstream session can then cite either the original receipt or the revised receipt; it must be explicit about which lineage it is building on and why.

What arbitration cannot produce: a retroactive alteration of the original receipt's lineage. The original receipt remains in the record exactly as issued. Its Dissent Record remains unchanged. The arbitration's output is a new document, not a correction of the old one. A party who wants the original receipt to say something different than what it says has no mechanism available to them. That is not a limitation of arbitration. That is the point of immutability.

If an Arbitration Session itself reaches a deadlock — if a party with standing refuses to accept or enter a bound dissent on the arbitration's proposed ruling — the arbitration moves to HOLD. There is no second-order arbitration. At that point the deadlock requires resolution outside the protocol: human governance, a third party with authority the court does not claim, or a decision by the parties to proceed without a shared receipt and accept the consequences of that choice. While arbitration is on HOLD, time-decay gates on the original receipt's live claims continue to operate. They do not pause for the arbitration deadlock. A time-decay gate that fires during an arbitration HOLD produces a delta receipt and routes through the standard kairos check; if that delta generates a kairos signal with compass proximity to the pending downstream session, it may add urgency to resolving the deadlock, but it does not automatically break it.

---

## §6.6 — What Shared Courts Cannot Fix

The shared court extends ARCS's jurisdiction without expanding its authority. Part VI adds roles, a Dissent Record, a quorum rule, co-signed gates, and an Arbitration Session. None of those additions give the court power over what happens outside the protocol. Three failure modes fall outside it entirely.

Power asymmetry. The Initiator and each Respondent hold equal formal standing. The protocol enforces this at L3, where the higher stakes tier governs regardless of who submitted it, and at L4, where the ruling is not a vote. What the protocol cannot enforce is the condition that parties arrive with equal practical influence. If one party controls the resources the other party needs, if one party's approval determines the other's professional standing, if one party has simply been in the room longer — none of that disappears when the session opens. A Respondent who nominally has standing to enter a bound dissent but knows that dissent will cost them something real outside the session is not operating under equal conditions. The court sees the dissent or its absence. It does not see the pressure that shaped either.

This is not a design flaw. It is a scope limit. The protocol is a decision architecture, not a power equalizer. Correcting for structural power asymmetry is a governance problem. The shared court can make the terms of a decision visible and the outcome immutable. It cannot make the parties equal.

Bad-faith participation. The protocol assumes that parties who enter the session intend to engage with it. A party who submits a stakes assessment they know is false, accepts a ruling they have already decided to ignore, or enters a bound dissent as a delaying tactic rather than a genuine objection cannot be detected by any gate in the L0–L5 pipeline. The Dissent Record records what parties claim; it does not record what they believe. The receipt captures what was said; it does not capture intent.

The court's response to bad-faith participation is limited and intentional: the receipt stands as issued. If a party later acts in contradiction to a receipt they accepted, that contradiction is visible to any downstream session that cites the lineage. The court produces an auditable record. The interpretation of that record — and the consequences of acting against it — belong to the parties and whatever governance sits above them.

Scope capture. A shared court that operates over time across many joint decisions may gradually expand the implicit jurisdiction of its receipts. What began as a specific decision about a specific question starts to feel like standing policy. Parties begin treating a receipt's gate conditions as general rules rather than conditions on a single decision's downstream validity. The accumulated weight of a shared lineage starts to function as a constitution that no one explicitly ratified.

The protocol has no automatic defense against this. Receipts are immutable and their lineage is cumulative by design — those properties are what make the court's output meaningful. The same properties that give receipts their authority make them susceptible to creeping scope. The boundary against scope capture is not a rule the court enforces. It is a discipline the parties must maintain: each new session must cite only the receipts that actually govern its gate conditions, not the receipts that feel relevant or that one party finds useful to invoke.

Where the boundary falls: Part VI ends here. The shared court is the outermost layer of ARCS's decision architecture. Beyond it lies organizational governance, institutional authority, and the kind of trust that cannot be receipted. The protocol reaches the edge of what formalization can do and stops.
