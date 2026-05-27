# Book II · Part V — The Accumulation Protocol

**Status:** DRAFT held — upstream ARCS audit pending
**Version:** v0.1.0
**Date:** 2026-05-26

---

## §5.0 — The Frozen Court Problem

A court that never revises its priors is not wise. It is merely consistent.

The sessions API (Part IV) gave ARCS something it did not have before: a durable record of its own reasoning. Every decision exits as a receipt — signed, lineaged, timestamped. The record is real. The problem is what the record cannot do on its own.

A receipt is a snapshot. It captures what ARCS believed at T₀ — what the question was, what the stakes were, what the compass said, what the court ruled. It does not update when the world moves. It does not raise its hand when a later session contradicts it. Left alone, a collection of receipts is an archive, not an intelligence.

This is the Frozen Court Problem: a decision system with perfect memory but no way to learn from that memory will, over time, become a fossil of its own past confidence. It will cite its own prior rulings as authority. It will treat T₀ beliefs as Tₙ facts. It will confuse consistency with correctness.

Part V defines the layer that prevents fossilization. Not by destabilizing the court — the constitutional constraints from Part III still hold, the ROM axioms from Part II are not up for vote — but by building the signal infrastructure that tells the court when its priors have drifted from reality, and what to do about it.

The name for that infrastructure is the Accumulation Protocol.

---

## §5.1 — The Receipt as Delta Seed

For the Accumulation Protocol to work, something has to change about how receipts are treated.

In Part IV, receipts were defined primarily as outputs: the terminal artifact of a session, the unit of lineage, the thing that gets tagged and stored. That framing was correct for what Part IV needed to establish. It is incomplete for what Part V requires.

A receipt is not only a record. It is an open hypothesis.

Every receipt contains at least one claim that the world can, in principle, confirm or falsify. The compass pointed here; was that right? The court ruled DRAFT pending more data; did the data arrive? The L3 step assessed stakes as moderate; did the decision play out at that magnitude? These are not rhetorical questions. They are the receipt's unfinished business — the part of the document that remains live even after the session closes.

This reframing has a structural consequence: receipts exist in one of two states.

A live receipt contains at least one unresolved claim — a claim that has a declared verification condition and has not yet been closed out. Live receipts are the raw material of the signal layer. They are the system's open hypotheses, held in the accumulation queue, waiting for signal that either confirms, revises, or expires them.

A closed receipt has had all its verifiable claims resolved — confirmed by subsequent evidence, superseded by a later session in the lineage chain, or expired by time-decay without sufficient signal. Closed receipts move to archive. They are no longer inputs to the compass. They are the court's settled law.

The boundary between live and closed is not cosmetic. It is how ARCS distinguishes between "we decided this" and "we know this." Most systems collapse that distinction. ARCS cannot afford to.

One rule follows immediately: a receipt cannot be closed by the same session that created it. Closing requires external signal — an outcome, a contradiction, a debrief — that arrives after T₀. A session that marks its own receipts closed is a court that grades its own exams.

Delta gates, introduced in §5.2, are the mechanism that turn that external signal into structured updates. But they only work if the receipt is already written as a hypothesis. That is what this section establishes: before a receipt can feed the Accumulation Protocol, it has to be more than a record. It has to be a question the world is still answering.

---

## §5.2 — Delta Gates

A live receipt holds an open hypothesis. A delta gate is the mechanism that answers it.

A delta gate is a threshold condition declared on a verifiable claim inside a receipt. When the condition is crossed — when reality produces a signal that meets or exceeds the threshold — the gate fires. The receipt stops waiting. The accumulation queue routes the delta forward.

Gates come in three types, corresponding to the three ways a claim can be resolved.

A magnitude gate fires when a measured outcome diverges from the receipt's prior by more than a declared amount. The court assessed stakes as moderate; the decision consumed three months and reorganized a team. Magnitude exceeded. Gate fires.

A direction gate fires when an outcome moves opposite to the receipt's compass reading. The compass pointed toward a particular framing; subsequent evidence points the other way. Direction reversed. Gate fires.

A time-decay gate fires when a claim reaches its expiration horizon without sufficient confirming or disconfirming signal. Not every hypothesis gets answered. Time-decay gates prevent live receipts from accumulating indefinitely — they force a resolution, even if that resolution is "we never found out."

All three gate types share one property: they must be declared at session-close, not set after the fact.

This is not a preference. It is a constitutional constraint, for the same reason a receipt cannot be closed by the session that created it. A gate declared retroactively — after the outcome is already visible — is not a gate. It is a rationalization wearing a gate's clothes. The signal layer can only function as a calibration mechanism if thresholds are set before the results come in. Otherwise the system is not learning from its receipts; it is fitting its receipts to what it already believes.

The practical implication: every session that produces a receipt with live claims must also produce at least one gate per claim — magnitude, direction, or time-decay — before it closes. A receipt with live claims and no gates is structurally incomplete. It cannot enter the accumulation queue. It sits in a pending state until a gate is declared or the session is reopened.

This creates minor friction. That friction is the point. Forcing gate declaration at session-close is how ARCS surfaces the question "how will we know if this was right?" before the session disperses. Most decision systems never ask that question at all. They decide, archive, and move on. The delta gate is how ARCS keeps the question open in a structured form — not as a vague commitment to revisit things someday, but as a precise, named condition that the signal layer will watch for.

One gate fires. What happens next is the Kairos problem.

---

## §5.3 — Kairos Detection

A gate fires. This does not mean anything needs to happen right now.

That distinction is the entire problem this section exists to solve.

When a magnitude gate fires on a two-year-old receipt about a decision that has since been superseded, the signal is real but the urgency is zero. When a direction gate fires on a receipt whose live claim sits at the root of three active sessions, the signal is real and the urgency is high. The delta is the same kind of event in both cases. What differs is the moment.

The Greeks had two words for time. Chronos is the clock — sequential, uniform, indifferent. Kairos is the opening — the moment when conditions make action not just possible but appropriate. A gate fires on a chronos schedule: the condition was met, the threshold crossed, the event logged. Whether that firing constitutes a kairos signal is a separate question, answered by the context surrounding the receipt, not the content of the delta itself.

Kairos detection is the layer that makes that determination.

Formally: a kairos signal is generated when a fired gate meets at least one of three context conditions.

Compass proximity. The receipt's live claim is currently load-bearing — it appears in the lineage chain of one or more active sessions, or it directly informs a compass axis that is in use. A delta on a load-bearing claim is not background information. It is a structural update that active sessions are implicitly relying on. Kairos.

Stakes escalation. The fired gate's magnitude or direction delta, if incorporated, would shift the stakes assessment of a downstream decision by more than a threshold amount. A signal that changes what is at risk — not just what is believed — warrants urgent routing, not quiet accumulation. Kairos.

Temporal compression. A PrepSession is pending or in progress whose declared Horizon overlaps the receipt's domain. Deltas that arrive while a decision is actively being made are categorically different from deltas that arrive in the space between decisions. The window is closing. Kairos.

When none of these conditions are met, the fired gate routes to background accumulation — it updates the prior, increments a confidence weight, and waits. The signal layer processes it silently. No session is triggered. No alert surfaces.

When any one condition is met, the fired gate routes differently. It becomes a PrepSession input: a named signal, stamped with the receipt it came from and the gate that fired, surfaced as a consideration in the next session's setup phase. Not as a conclusion. Not as an override. As a prompt — the system's way of saying: something relevant just moved; you should know before you rule.

This is where kairos detection closes the loop back to Part IV's PrepSession anatomy. The five PrepSession fields — Stakes, Horizon, Protecting, Contra, Confidence — are not just inputs the user provides at session open. They are surfaces that the signal layer can write to when kairos conditions justify it. A fired gate with compass proximity may update the Contra field. A stakes-escalating delta may revise the Stakes field before the session reaches L0. A Horizon overlap may compress the session's default time window.

The rule is the same as with gates: the signal layer can surface; it cannot decide. PrepSession fields updated by kairos signals are flagged as signal-derived, not user-declared. The court sees the provenance. It is not required to accept the input. But it cannot pretend the input never arrived.

One last point. Kairos detection has a failure mode that is easy to miss: over-triggering. A system that generates kairos signals too readily does not produce urgency — it produces noise, and noise trains the court to discount signals. The three context conditions above are not a menu to check loosely. Each condition has a declared threshold, and the thresholds are set conservatively by default. The signal layer should generate kairos rarely enough that when it does, the court takes it seriously.

A gate fires when reality crosses a threshold. A kairos signal fires when that crossing matters now. The Accumulation Protocol, in §5.4, is what happens when you string both together across time.

---

## §5.4 — The Accumulation Protocol

Sections §5.2 and §5.3 built two primitives: a mechanism for detecting when reality has crossed a threshold, and a mechanism for detecting when that crossing is urgent. This section builds the loop that connects them — and connects both back to the compass.

The Accumulation Protocol is a five-step cycle. It runs continuously in the background, triggered by gate firings, and it has no natural terminus. The court is always in session in this sense: not deliberating, but listening.

Step 1: Receipt monitors a live claim. Every live receipt in the accumulation queue is assigned a watcher — a process that observes the verification condition declared for each of its live claims. The watcher does not evaluate evidence. It waits for a gate to fire.

Step 2: Gate fires. When a live claim's threshold condition is crossed — magnitude, direction, or time-decay — the gate fires and passes the delta to the kairos layer, stamped with the receipt identifier, the gate type, and the observed signal.

Step 3: Kairos check routes the delta. The kairos layer applies the three context conditions from §5.3. If none are met, the delta routes to silent accumulation: the prior is updated, the confidence weight is incremented, no session is triggered. If any condition is met, the delta routes to the PrepSession surface as a flagged signal.

Step 4: Prior is updated. Whether silent or flagged, every fired gate produces a prior update. The compass axis or confidence weight associated with the receipt's live claim shifts by the amount the delta warrants. This update is not optional and not deferred. A gate that fires and produces no update is a gate that does not exist.

Step 5: Update is written back into the lineage chain. The prior update is not made in place. It is appended to the receipt's lineage as a new record — a delta receipt — with its own timestamp, gate provenance, and accumulation mode. The original receipt does not change. The lineage grows.

That last step is the protocol's constitutional constraint, and it cannot be waived: no prior can be silently overwritten. Every update produces a record. Every record is legible in the lineage chain. The court can always trace the path from original ruling to current belief, gate by gate.

This constraint does more than preserve auditability. It prevents a specific failure mode: the quiet rewrite. Without it, a system under accumulated signal pressure will tend to update its priors in ways that erase the evidence of what it used to believe. The revised belief looks like original belief. The drift becomes invisible. The lineage constraint makes drift structurally visible — not just in principle, but in every delta receipt that marks where the prior moved and why.

The three accumulation modes named in the Part V outline now have precise meaning:

Silent. Gate fires. Kairos check fails. Prior updates. Delta receipt appended. No session surface, no user-facing alert. The compass shifts quietly. Appropriate for low-stakes updates far from active decision territory.

Flagged. Gate fires. Kairos check passes. Delta routes to PrepSession surface as a named signal. Prior updates. Delta receipt appended. The court is informed before it next convenes. Appropriate for load-bearing claims, stakes-escalating deltas, and open PrepSessions.

Override. A special case of flagged, triggered when a kairos signal meets all three context conditions simultaneously or when the magnitude of a prior update exceeds a constitutional threshold. Override mode does not just surface the signal — it requires the court to address it before the active session can proceed. The PrepSession cannot advance past L0 until the signal is acknowledged, accepted, or explicitly rejected with a documented reason. The court may reject the signal. It may not proceed as if the signal never arrived.

Override is rare by design. It is the signal layer's equivalent of a motion to hold — not a veto, but a mandatory pause. The same conservative threshold logic from §5.3 applies: if override triggers frequently, the thresholds are wrong.

The Accumulation Protocol is now complete as a loop. What it cannot do is equally important, and §5.5 takes that up directly: the loop runs correctly, the priors update faithfully, the lineage grows — and the court can still drift. Accumulation handles the claims inside receipts. It does not handle the axioms that evaluate those claims.

---

## §5.5 — Drift Detection and Constitutional Fidelity

The Accumulation Protocol can run without error and the court can still be wrong.

This is not a contradiction. It is a consequence of how the loop is scoped. The protocol updates priors inside receipts — claim by claim, gate by gate, delta receipt by delta receipt. It does not evaluate whether the cumulative effect of those updates has moved the court's overall posture into tension with the axioms it was built on. That is a different question, at a different level, and the protocol was not designed to answer it.

Drift is what happens in that gap.

Drift is not a single bad update. A single bad update is a mistake; the lineage chain makes it visible and correctable. Drift is the accumulation of individually defensible updates that, taken together, have moved the compass away from where the ROM axioms say it should be able to go. Each step looked reasonable. The destination was not.

An example. Over time, the court accumulates a series of magnitude-gate firings, all in the same direction: decisions that seemed high-stakes turn out to be lower-stakes than assessed. Each update is legitimate. The prior for stakes adjusts downward, increment by increment, following the signal. After eighteen months, the court is systematically underweighting stakes in its L3 assessments — not because any individual update was wrong, but because the ROM axioms say stakes must be assessed against the full range of what the decision could affect, and the signal the court has been accumulating is drawn from a subset of decisions that all happened to resolve quietly. The court has learned from its experience. Its experience was not representative.

The ROM axioms did not change. The court drifted away from them.

Drift detection is a periodic fidelity check: a comparison of the court's current compass priors against the ROM axioms, run on a declared schedule, designed to surface constitutional tension before it reaches a live session. It does not run on the same trigger as the Accumulation Protocol. It runs on time — at intervals set by the court's configuration — and on demand, any time a debrief session (§5.6) is convened.

The check produces one of three outputs.

Clear. Current priors are within constitutional range. No tension detected. The fidelity log is updated with a timestamp and a signed attestation. The court continues.

Watch. One or more compass axes have drifted toward the boundary of constitutional range but have not crossed it. A WATCH entry is appended to the drift log, flagged by axis and magnitude, and surfaced the next time a PrepSession is opened. Not an override. A flag on the horizon.

Drift. One or more compass axes have crossed into territory the ROM axioms cannot accommodate. A DRIFT signal is generated — the signal class introduced in the Part V outline — and the escalation path activates.

The DRIFT escalation path has a single destination: the constitutional court from Part III.

Not the signal layer. Not a PrepSession. The court itself, convened in a special configuration: not to rule on a question brought by a user, but to audit its own axioms against its own accumulated priors and determine whether the drift can be corrected within the existing constitutional frame, or whether the ROM axioms themselves need to be examined.

That second outcome — ROM axioms under review — is the most structurally significant event the system can produce. It is not handled by Part V. Part V can detect the need; it cannot adjudicate it. The ROM axioms are Part II's territory, and any revision to them requires the full constitutional apparatus, not a signal-layer escalation. Part V hands off and stops.

One boundary worth naming explicitly: drift detection cannot correct drift. It can detect it, log it, surface it, and escalate it. Correction requires human judgment — a debrief session that reviews the accumulated delta receipts, identifies where the priors diverged from constitutional intent, and issues a calibration receipt that resets the affected axes. That process is §5.6.

What drift detection guarantees is that the court cannot drift indefinitely without being asked to account for it. The fidelity check is not optional, and its schedule cannot be set to "never." ARCS can drift slowly. It cannot drift silently.

---

## §5.6 — The Debrief Session

A debrief is not a postmortem. It is not a retrospective. It is not a meta-session appended to the end of a sprint to make everyone feel heard.

It is a first-class session type, with its own PrepSession structure, its own L0–L5 pipeline, and its own receipt. It differs from a standard session in exactly one way: its input is not a question brought from outside the system. Its input is the system's own record.

Specifically: the debrief session takes as its input a set of receipts — typically those flagged by a WATCH signal, mandated by a DRIFT escalation, or nominated for review because a declared review interval has elapsed. The court convenes not to rule on a decision but to audit its own accumulated priors against what those receipts actually show.

The distinction matters because it determines who is in the dock. In a standard session, the question is on trial. In a debrief, the court's judgment is on trial.

The debrief session is mandatory in two circumstances: when a DRIFT signal has been generated and escalated, and when a prior-update delta has accumulated beyond a constitutional magnitude threshold across any single compass axis — meaning the court's position on that axis has moved far enough, through silent and flagged accumulation alone, that the movement requires formal review before it can stand. Mandatory debriefs cannot be deferred. They block new standard sessions from opening on the affected domain until the debrief receipt is issued.

The debrief session is discretionary in all other circumstances. Any member of the court can convene one. The signal layer can surface one as a PrepSession input when WATCH entries accumulate past a threshold. The fidelity check schedule can trigger one automatically. Discretionary debriefs do not block other sessions. They run in parallel.

The debrief runs a standard L0–L5 pipeline. What is reviewed at each level differs from a standard session:

L0 receives the set of input receipts and their delta receipts, not a user question. L1 characterizes the pattern of drift or accumulation visible in the set — not what any single receipt says, but what the set says together. L2 applies the ROM axioms as the evaluative frame: given what we know the court was built to protect, does the accumulated movement in these priors represent a defensible learning curve or a drift away from constitutional intent? L3 reassesses stakes — not of a pending decision, but of leaving the accumulated priors in place. L4 runs the deliberation against the calibration question: should any of these priors be reset, and if so, to what? L5 issues the verdict.

The debrief's verdict is a calibration receipt.

A calibration receipt is a special receipt type that carries three payloads. First: a set of prior resets — compass axes or confidence weights that the debrief determined are out of constitutional range, with their revised values and the reasoning that supports the revision. Second: a set of gate closures — live claims that the debrief determined are no longer productively open, either confirmed, expired, or superseded, with a final status stamped on each. Third: a signed attestation that the court reviewed its own record on the specified date, considered the specified receipts, and found the system's current posture to be within constitutional range — or, if not, that the DRIFT escalation path has been activated and Part III has been engaged.

The attestation is the part that cannot be omitted. A calibration receipt without an attestation is not a calibration receipt. It is an incomplete session. The court has not finished its work until it has signed its own audit.

Two limits on what a debrief can do. First: a debrief cannot change the ROM axioms. If the debrief determines that the drift cannot be corrected within the existing constitutional frame, it issues a DRIFT escalation to Part III and stops. The axioms are not the debrief's to revise. Second: a debrief cannot retroactively alter existing receipts. Prior resets apply forward from the calibration receipt's timestamp. The lineage chain is not rewritten. The court's past rulings stand as issued; the court's current posture is adjusted. History and present are kept separate.

After a debrief session closes, two things change in the system. The accumulation queue is cleared of any live claims that were closed by the calibration receipt. And the fidelity check's attestation log is updated — the next scheduled check will compare current priors not against the original baseline, but against the priors as they stood at the close of the most recent calibration receipt. The debrief does not reset the clock to zero. It moves the baseline forward to where the court now stands, attested and documented.

The court reviewed its own record. The work continues.

---

## §5.7 — What Accumulation Cannot Fix

Part V has built a complete signal layer. Receipts are reframed as open hypotheses. Gates detect when reality crosses a threshold. Kairos determines when that crossing is urgent. The Accumulation Protocol loops both back into the compass. Drift detection catches what the loop misses. The debrief closes the audit.

This is a substantial set of machinery. It handles a wide range of failure modes. It does not handle all of them.

There is a specific class of failure that looks like epistemic drift — looks, from the outside, like the kind of thing the Accumulation Protocol should be able to correct — but is not. Feeding it into the signal layer does not fix it. In some cases, it makes it worse, because the loop keeps updating priors around a structural problem that prior updates cannot reach.

Three failure modes belong to this class.

**Value drift.** The court's priors can be within constitutional range — all compass axes passing the fidelity check, all ROM axioms technically unviolated — and the court's values can still have shifted. Values are not priors. A prior is a belief about how the world works. A value is a commitment about what matters in that world. Accumulation updates beliefs. It has no mechanism for detecting when the underlying commitments have quietly moved. A court that has accumulated ten thousand correct updates can still, over time, come to weight things differently than it was constituted to weight them — and no delta gate will fire, because no single update crossed a threshold. The movement was in the water, not the weather. Value drift requires the constitutional court, not the signal layer, because it is not a question about what is true. It is a question about what the court is for.

**Scope creep.** Sessions have declared scopes. The Accumulation Protocol respects those scopes — it routes deltas to receipts, updates priors within compass axes, and does not evaluate whether the domain the court is currently adjudicating is still the domain it was constituted to handle. Scope creep is the gradual expansion of what counts as a session-eligible question. It does not show up in the lineage chain. It shows up in the pattern of what gets brought to the court, and in the implicit widening of "within scope" over time. No gate fires when scope creeps. The signal layer cannot see it. Scope creep requires a deliberate examination of the court's jurisdictional boundaries — again, Part III territory, not Part V.

**Malformed original question.** The most structurally dangerous failure mode, and the one the signal layer is most likely to make worse. If the question that seeded a session was malformed — if the compass was pointed at the wrong problem, if the framing contained a hidden assumption that was never surfaced — then every downstream receipt carries that malformation into its live claims, every gate fires against a miscalibrated prior, and every accumulation cycle optimizes around the original error. The signal layer is not equipped to detect that the premise is wrong. It can only detect that the outcomes are surprising. Surprising outcomes accumulate as magnitude-gate firings, which update the priors toward whatever pattern the malformed question has been generating. The court becomes increasingly well-calibrated to the wrong question. The fix is not more accumulation. The fix is return to L0 — a new session, with the original question under examination, not the answers it produced.

The diagnostic for all three failure modes is the same: if the signal layer has been running correctly and the court's outputs are still systematically wrong, the problem is not in the priors. The problem is in the structure that generated the priors. And the Accumulation Protocol, by design, cannot audit its own inputs.

This is not a limitation to be engineered away. It is a feature. A signal layer that believed it could fix anything would eventually try to fix things it cannot fix, and in doing so, would obscure the failures that require human judgment to resolve. The hard boundary is the mechanism that keeps the signal layer honest about what it is: a calibration engine for epistemic drift, operating within a constitutional frame it did not create and cannot revise.

The designed answer to the malformed-question failure mode is not inside Part V at all. It belongs one layer earlier — at the Calibrate surface, before a session is ever seated. The HOLD gate and anticipatory probing exist precisely to catch bad framing at the input layer, before the pipeline has a chance to bake the error in. Part V handles what survives that check. It was never designed to substitute for it.

Part V ends here. The court knows more than it knew at the close of Part IV. It also knows, precisely, the edges of what knowing more can accomplish. Beyond those edges: Parts II and III, and the humans who built them.
