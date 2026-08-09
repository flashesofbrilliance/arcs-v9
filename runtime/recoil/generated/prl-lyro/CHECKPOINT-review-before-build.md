# CHECKPOINT - review before we build (A)
_2026-08-09 · Zach reviews this before any live Tidio change. Synthesizes the session's grounded docs. Nothing
below has been built; the account is untouched. Detail lives in the linked docs; this is the decision surface._

Linked detail: [icp-audiences-molder-vs-oem.md] · [experience-consistency-and-ab-plan.md] ·
[tidio-capabilities-research.md] · [current-journey-audit-baseline.md] · [prl-tidio-capture-flow-spec.md]

---

## 1. DESIGN SPEC (what we are building)

**One assistant, two journeys, routed by ICP.** Confirmed feasible on this plan (audience-scoping available).

- **Molder journey (knows the grade, transactional):** confirm grade -> capture -> **fast handoff to the
  territory rep**. Minimal AI. Mostly Flow + immediate handoff (0 Lyro quota).
- **OEM/engineer journey (has an application, consultative):** recognize application/market -> help at the
  application level only -> **route formulation/spec to one of the 2 OEM reps** + official data sheet -> capture.
  Lyro carries more here (best use of the 50/mo).
- **Universal guardrail (both journeys):** NEVER state a property value, UL/cert status, price, or lead time.
  Recognize + route + capture. Same brand voice. This is what fixes the baseline (Lyro currently states UL94
  V-0 + HDT as fact - see baseline audit).
- **Qualification:** one opening question ("Do you already know the grade you need, or want help choosing?")
  + auto-signals (grade named/role/references) -> stamp a contact property -> branch to the right audience.

## 2. PRODUCT REQUIREMENTS (acceptance criteria - how we know it works)

Must:
- R1. A spec/cert/price question is NEVER answered with a value; it routes to a specialist + offers the data
  sheet. (Test: the baseline UL94/HDT prompt must now route, not answer.)
- R2. Every genuine inquiry ends with a captured lead: first/last name, company, **phone (required)**, email,
  application/grade interest. (Phone required = Todd's locked decision; maps to Sugar phone_work.)
- R3. Molder inquiries route to the territory rep; OEM inquiries route to an OEM rep. (Rep mapping needed from
  Todd; interim = named rep / Bill Galla.)
- R4. Behavior is consistent whether the visitor is in the Flow or in Lyro (no answer-vs-route contradiction).
- R5. After-hours: no dead end - always capture + "the team will follow up".
- R6. Cost: qualified -> immediate handoff (0 quota); capture via Lyro Task where possible (0 quota); reserve
  the 50/mo Lyro conversations for genuine OEM Q&A.
Out of scope for A (later phases): live CRM write / Zapier->Sugar delivery (1.1/1.2, gated on Todd's safe test
path); competitor-grade recognition depth (1.3); SEM onramps (1.4). A is EXPERIENCE only.

## 3. IMPLEMENTATION PLAN (ordered, reversible, backup-first)

Pre: export current flows + note current data-source on/off + audience state (rollback point). Verify each
in-app label as we go (docs paths are [likely], not confirmed - help.tidio.com 403s scripted fetch).

1. **Kill the fabrication (universal fix):** set the 5 spec PDFs (Product Catalog/150 Q&As, Material-Selection,
   Competitor-Cross-Ref, Engineering-Thermoplastics, Polymer-Resources-Pro) to **Copilot-only** (off for
   customer Lyro). Keep the public prlresins.com pages on for Lyro. Verify in Playground: UL94 prompt now routes.
   > **BLOCKED / needs Zach's call (verified in-app 2026-08-09):** Tidio has **no source-level or bulk "Used by"
   > toggle** — the Lyro/Copilot switch exists only inside each Q&A entry's Edit panel. So true "Copilot-only" =
   > flipping Lyro off on several hundred entries by hand (109 Competitor + ~150 Catalog + 3 more PDFs), one miss
   > defeats R1. The only clean bulk path is **Delete the 5 PDFs from Lyro** (removes Lyro + Copilot; reversible
   > via repo re-import; PRL reps aren't using Copilot). Zach chose **HOLD** on 2026-08-09 — knowledge sources
   > left untouched pending his decision (delete-from-Lyro vs per-entry Lyro-off). Account still matches the
   > 2026-08-09 backup. See tidio-capabilities-research.md §5 for the full verification. Steps 2-7 unaffected.
2. **Guidance:** write the never-state-a-spec + recognize/route/capture rule in Lyro's voice, matching the flow.
3. **Audiences:** create "Molder" and "OEM" audiences; scope guidance/handoff (and any KB) per audience.
4. **Qualification branch:** opening question -> Update Contact Property (qualified/persona) -> Condition branch.
5. **Capture:** as a Lyro Task (quota-free) and/or the onFirstVisit flow; fields per R2; phone required.
6. **Handoff:** per persona (territory vs OEM rep); after-hours = capture + expectation (R5).
7. **Verify (acceptance):** run R1-R6 in the Playground/preview; screen-capture BOTH journeys; run the
   side-by-side /impeccable vs the baseline. Do NOT activate live until it passes + Zach signs off.

Rollback: re-enable data sources / restore flow from the export. All steps are toggles or drafts.

## Open inputs needed from Todd (batched)
- Rep routing: territory map + the 2 OEM reps' names (R3).
- Confirm "Chatbot" lead source + that phone-required is OK for the CRM write (delivery phase).
- Safe CRM test path (sandbox or one labeled test lead) - gates delivery, NOT experience.

## Decision for Zach at this checkpoint
Approve the design spec + PRD + plan as-is, OR redline. On approval, A proceeds step 1 -> 7 (backup-first,
nothing activated live until acceptance passes and you sign off).
