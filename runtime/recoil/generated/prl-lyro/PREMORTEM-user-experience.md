# Pre-mortem — user-error & UX failure modes (PRL chatbot, 1.1)

_2026-08-09 · Assume the launch went badly. Why? Role-played as the actual visitors (a molder who
knows their grade, an OEM engineer describing a part, a press operator in a hurry, a tire-kicker, a
competitor). Each failure mode below is scored Likelihood x Impact, with its current design status and
the mitigation. "Designing around them" = the CHANGES list at the end._

Status legend: ✅ handled by current design · ◐ partial · ✗ gap to fix.

---

## A. Abandonment & friction (the capture-first risk)

**A1. The contact wall feels like a lead-harvest and they bail. [High L · High I · ◐]**
Capture-first asks name/company/phone/email/state before any value. A browser who just wanted to look
leaves. Mitigation in place: warm greeting explains why ("so a specialist can follow up"), only 5 fields,
one intent tap. Still the single biggest conversion risk. → Design around it: keep the "why" line, add a
one-line privacy reassurance, and A/B capture-first vs capture-after (the plan already exists) to measure
the real drop rather than guess.

**A2. They abandon MID-capture and we have no way to reach them. [Med L · High I · ✗ GAP]**
Current order is name → company → phone → email → state. Someone who bails after name+company leaves NO
contact channel — which defeats the whole "never lose the lead" purpose of capturing first. → Fix: secure a
REACHABLE field (email or phone) as the 2nd question, so any partial is still actionable. Recommended order:
**name → email → phone → company → state.**

**A3. Exploratory "help me choose" user resents being carded before they've explained anything. [Med · Med · ◐]**
The OEM who wants to talk through a part hits a form first. → Consider a lighter touch for the "help me
choose" entry: one clarifying exchange, THEN capture. Tension with capture-first; this is the A/B's real job.

## B. Input errors (garbage in)

**B1. Junk to bypass a required field ("asdf", "a@a.a", "1111111111"). [High · Med · ◐]**
Email/phone have format validation, so blatant junk is caught. Name/company can't be validated for
authenticity → a determined bypasser still creates a low-quality lead. → Accept it (the alternative is more
friction), but tag low-confidence leads (no email domain match, obviously-fake name) so reps triage.

**B2. Over-strict validation traps a REAL user in a loop. [Med · High · ✗ VERIFY]**
An international number, an extension, a "+1", or a legit rare email TLD gets rejected, the visitor re-tries,
fails again, rage-quits. The generator sets `failedNode=None` with `number_of_repeats=1` — **must verify the
flow does NOT dead-end on a validation failure** and that phone validation accepts common real formats
(spaces, dashes, +country, extensions). A guardrail that blocks real customers is worse than a loose one.

**B4. State entered as abbreviation, region, or placeholder. [High · High · ✅ FIXED 2026-08-09]**
"CT" for Connecticut, "North East"/"Midwest" (a region, not a state), or "N/A"/"none"/"-". The old resolver
converted to abbreviation (backwards — Sugar's records + the territory map use FULL names), so **every state
silently failed to route** and regions/placeholders were written to `location_c` as garbage. Fixed:
`resolve_state()` accepts abbrev/full/informal/mixed-case → canonical full name; regions/placeholders/foreign
return a `status` so the flow can **re-ask** instead of writing junk. Covered by 34-case self-test + 213 sweep
cases. → Remaining design work: the flow's state question must act on the status (re-ask on
region/placeholder/unknown, "Which US state?"); the webhook applies `resolve_state` and tags "state needs
confirmation" + routes to Sales Manager when unresolved, never inventing a state.

**B3. Compound answer in one message ("John at Acme, need PC for outdoor, 203-555-1212"). [Med · Med · ✗]**
The rigid flow's step-by-step capture expects one field per turn; a compound reply gets saved wholesale to
"name". → Lyro parses this far better than the flow; ensure compound/natural input routes to the AI parse,
or add a confirm step ("I got your name as… is that right?").

## C. The guardrail reads as an unhelpful bot

**C1. "I just want the UL rating and it won't tell me." [High · Med · ◐]**
The governed route is correct (never state a stale cert), but to the visitor it can feel evasive. → Frame
the route as VALUE, not refusal: "Our specialist will confirm the exact current number so you're not working
off a stale spec, and I'll get you the official data sheet." Never "I can't answer that." This copy change is
the difference between "careful" and "useless."

**C2. Bot doesn't acknowledge what they typed → they feel unheard. [Med · Med · ◐]**
A visitor types a specific grade and the bot jumps straight to "a specialist will follow up." → Acknowledge
first ("Got it — you're after a Lexan 141 equivalent"), THEN capture/route. The recognizer already knows the
grade; use it to reflect the ask back.

## D. Delivery & trust (the most damaging)

**D1. Bot says "your info's been saved, a specialist will reach out" — and no one does. [High if premature · Critical · ✗ HARD GATE]**
Until delivery→SugarCRM + rep notification is wired (sandbox-gated), a captured lead sits in Tidio only. If
the bot is pointed at REAL traffic before that, every "we'll be in touch" is a broken promise — the exact
trust failure that kills a launch, and it lands on Todd. → Hard rule: **do not expose to real visitors until
delivery + notification fire and someone owns the inbox.** Staging/testing only until Layer 3 passes.

**D2. The 4-hour callback promise is made but not met. [Med · High · ◐]**
The close promises "usually within a few hours." If a rep doesn't act, trust breaks on the second interaction.
→ The Mailgun instant autoresponder (1.2) covers the prospect immediately; the metric instruments whether the
human 4-hour promise is actually kept. Don't promise a time the team can't hold — soften to "shortly" if the
4-hour SLA isn't yet enforced.

## E. Technical UX bugs

**E1. A visitor who TYPES a question first bypasses the capture gate (and Lyro may state a spec). [Med · High · ✗ VERIFY]**
If Lyro answers a free-typed question before the flow's capture runs, capture is skipped AND the anti-
fabrication guardrail depends entirely on Lyro's config, not the flow. → Verify Tidio flow-vs-Lyro
precedence: the capture flow must run first, or Lyro must defer to it. This is the open item in
`experience-consistency-and-ab-plan.md`; it is also a UX-consistency failure (two different behaviors).

**E2. Returning visitor gets no flow (trigger is first-visit-only) or a jarring re-trigger. [Med · Low · ◐]**
→ Consider a chat-open trigger and a "welcome back" path so a returning buyer isn't stranded or re-carded.

**E3. Mobile: the widget + 5-field capture is longer and fiddlier on a phone. [Med · Med · ✗ TEST]**
Press operators and buyers on the plant floor are on phones. → Test the capture on mobile explicitly; keep
each question short; make sure the keyboard type matches the field (email/number keyboards).

## F. Edge personas

**F1. Non-English visitor (China/Vietnam/Malaysia molders). [Low for 1.1 · Med · note]** English-only. Out
of scope for 1.1; flagged for later (Phase 2 translation).
**F2. Competitor / tire-kicker fishing for data. [Med · Low · ✅]** Capture-first screens this by design —
they won't give real contact info, and the competitor match is gated behind capture.

---

## Design changes this pre-mortem calls for (ranked)

1. **[D1 · HARD GATE]** Do not point the bot at real traffic until delivery + notification are wired and the
   inbox is owned. Staging only until Layer 3. (Non-negotiable — prevents the broken-promise failure.)
2. **[A2] Reorder capture to secure a reachable channel 2nd:** name → **email → phone** → company → state, so
   a mid-capture bail still leaves a contactable lead. (Implementable now in the generator.)
3. **[C1/C2] Reframe the governed route as value + acknowledge the ask:** "specialist confirms the exact
   current number + here's the official data sheet," and reflect the recognized grade back first. (Copy change.)
4. **[B2/E1 · VERIFY] Two verifications before go-live:** validation-failure does not dead-end and accepts
   real phone/email formats; and the capture gate is not bypassable by typing first (flow-vs-Lyro precedence).
5. **[A1] Add a one-line privacy reassurance** at capture; keep the "why we ask" line; run the capture-first
   vs capture-after A/B to measure real drop.
6. **[B1] Tag low-confidence leads** (fake-looking name / no business email) so reps triage instead of chasing.
7. **[E3] Mobile pass** on the capture flow before launch.
8. **[E2] Returning-visitor path** (chat-open trigger + "welcome back").

Items 2 and 3 are safe to implement in the flow generator now; 1 and 4 are gates; 5–8 are the next layer.
