# Current chatbot journey - baseline audit (B, read-only)
_2026-08-09 · Captured live in the Lyro Playground (sandbox; test questions do not count against the 50/mo
quota). This is the BASELINE (today's single experience) that the two-experience build (A) must beat. The
side-by-side /impeccable of both journeys happens AFTER A is built._

## What was tested
Prompt (a real molder/OEM spec question): "What is the UL94 flame rating and heat deflection temperature of
PRL PC-G30?"

## What Lyro did (verbatim)
> Here are the key specs for PRL PC-G30:
> - UL94 Flame Rating: V-0 at 1/8"
> - Heat Deflection Temperature: 295 F at 264 psi
> Is there anything else I can help you with?
Tagged: "AI response based on your data sources. Review sources." (i.e. pulled from the 150 auto-generated
"specifications" Q&A pairs off the Product Catalog PDF.)

## /impeccable-lens findings (customer-journey audit)
Ranked by severity.

1. **[Critical - correctness/liability] States a certification + property value as fact.** "UL94 V-0" is a
   certification claim; "295 F at 264 psi" is a spec. Presented as settled truth, no "verify with a specialist",
   no date, no data-sheet link. If any value is stale or the grade/condition differs, it is a customer-facing
   error on a regulated attribute. This is the single biggest problem and it is live for Everyone.
2. **[Critical - commercial] Zero lead capture.** The visitor gets the answer and leaves. No name/company/
   email/phone, no contact created. The most valuable moment (a buyer asking about a specific grade) produces
   nothing PRL can act on. Directly explains "leads acquired" underperformance.
3. **[High - strategy] No routing / no persona.** It does not recognize molder vs OEM, does not connect to a
   territory or OEM rep, does not offer the official data sheet. It answers and stops - the opposite of Todd's
   "get them to the right specialist fast."
4. **[High - consistency] Contradicts the flow.** The capture flow's premise is route-specs-to-a-specialist;
   Lyro undercuts it by answering them. A visitor who touches both gets two different behaviors in one session.
5. **[Med - trust] "Review sources" is the only guardrail** and it is passive (a link most users ignore). The
   guardrail should be behavioral (route), not a footnote.

## Journey map (today, single path)
Visitor opens widget -> greeting "Welcome to PRL Resins" -> asks a grade/spec question -> **Lyro answers with
specific values from the catalog Q&As** -> "anything else?" -> visitor leaves. No branch, no capture, no rep.

## What "better" looks like (the A target, for the checkpoint)
- Spec/cert questions -> recognized, NOT answered with values -> "a PRL specialist will confirm" + data sheet +
  **capture** + route (molder -> territory rep; OEM -> OEM rep). Never states a UL/property value.
- Every real question ends in a captured, routed lead. Consistent behavior in flow AND Lyro.

## Note on the formal /impeccable
/impeccable proper audits rendered UI. This baseline audits the CONVERSATIONAL journey (behavior + content),
which is where the real defects are. A visual-UI pass on the widget can be added if wanted, but the
journey-level failures above dominate.
