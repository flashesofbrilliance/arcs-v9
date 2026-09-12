# PRL chatbot: session-consistency design + Lyro scoping + A/B plan
_2026-08-08 · Priority is EXPERIENCE first (delivery to email/CRM comes later). The visitor must get one
coherent experience across a session whether they are in a Flow or in Lyro. Confirmed live-config findings and
the exact changes to make it consistent._

## The architecture (confirmed with Tidio support 2026-08-07)
- **Flows = the on-ramp.** Visit-triggered (`onFirstVisit`, non-input, so it coexists with Lyro and runs first).
  Structured lead capture: greet -> qualify -> capture name/company/phone(required)/email/application -> route.
- **Lyro = the graceful off-ramp / catch-all.** Handles free-text questions the structured flow does not catch.
  Runs AFTER the flow (Flows -> Lyro -> Human). Only "Visitor Says" flows conflict with Lyro; ours does not.
- **Consistency requirement (hard):** the two must feel like ONE assistant. Same brand voice, and the SAME
  never-state-a-spec rule in BOTH. If the flow routes a spec question to a specialist but Lyro then fabricates a
  spec, the session is incoherent and the guardrail is broken. Fixing that is the point of the scoping below.

## Confirmed live state (Lyro > Knowledge > Data sources, 2026-08-08)
13 sources, all toggled ON for Lyro, audience "Everyone". The spec-bearing PDFs are the fabrication risk:
- **PRL-Product-Catalog-2025.pdf** -> auto-exploded into **150 "What are the specifications..." Q&A pairs, all
  active for Lyro.** This is a live spec-answering engine.
- **PRL-Material-Selection...**, **PRL-Competitor-Cross-Reference...**, **Engineering_Thermoplastics...**,
  **Polymer-Resources-Pro...** -> same class (property values / competitor equivalences / cert-adjacent).
- The **prlresins.com website pages** (contact, our-team, products, about) are public, application-level, safe.

## Two experiences to build and compare (Todd wants to feel BOTH)
Goal: stand up two coherent experiences so Zach + Todd can compare them, then pick (or A/B later with traffic).
Each experience is internally consistent (flow and Lyro behave the same way within it).

- **Experience A - "Answers" (Todd's original instinct):** the smart assistant answers spec/application
  questions directly. Lyro KEEPS the spec knowledge, plus a guardrail: add a certification/date safety note and
  STILL capture the lead. Paired with the AI-forward flow ("PRL Resins - Lead Capture (AI-forward)", already a
  draft). Sells capability; the risk is a stale/wrong value going customer-facing, so the safety note + "a
  specialist will confirm" is mandatory even in this arm.
- **Experience B - "Routes" (the safe/recommended one):** the structured flow captures and routes; Lyro is the
  catch-all that RECOGNIZES intent but never states a spec/cert/price, routing to a specialist. Lyro spec PDFs
  scoped out; guidance enforces route-and-capture. Paired with the standard capture flow ("PRL Resins - Lead
  Capture", already active). Never-fabricate by construction.

**Concurrency via Audiences/Personas (CONFIRMED feasible - see tidio-capabilities-research.md).** Tidio
"Audiences" are the master lever: they scope Lyro **data sources, Guidance, AND handoff** per segment (Guidance
is NOT account-global as first assumed). So we can run both experiences concurrently as ONE Lyro configured per
audience plus a routing flow (not two isolated brains; Flows->Lyro->Human stays sequential/never-nested). A
qualification flow stamps a contact property/tag (e.g. `qualified=true`) via Update Contact Property, then the
audience condition applies the right knowledge/Guidance/handoff. Route the two experiences by qualification:
- **Qualified prospect -> Experience B (route to specialist).** Signals: names a specific PRL/competitor grade,
  engineering/purchasing/quality role, target industry (EE / medical / transportation / building / consumer),
  real volume or a purchase/quote/SDS ask. A hot lead reaches a human fast, fully captured. Don't make a real
  buyer negotiate a bot.
- **Unqualified / long-tail -> Experience A (AI answers / self-serve).** Signals: general question, student /
  researcher, no company, vague, consumer. Lyro handles the tail and deflects low-value load; captures lightly
  if they warm up. (Spec-safety note still applies - a wrong cert is wrong for anyone.)

This runs BOTH experiences live at once, segmented - which is both the comparison rig AND a better strategy
(AI absorbs the tail, humans get the hot leads). Qualification is scored by early flow questions
(role / company / application / grade-or-competitor named / industry) before the branch.

**Switchable demo profiles** remain the fallback if audience-scoped knowledge proves too coarse: flip
{active flow} + {Lyro data sources on} + {guidance} to demo A vs B one at a time. Either way, export/back up first.

**Profiles (what to flip):**
| | Active flow | Lyro spec PDFs | Guidance |
|---|---|---|---|
| **A - Answers** | Lead Capture (AI-forward) | ON (+ safety note) | answer + safety note + capture |
| **B - Routes** | Lead Capture (standard) | OFF (website only) | never state spec; route + capture |

Back up first ("export for now") so flipping is always reversible.

## (a) Building Experience B (routes) - the scoping steps
Goal: Lyro helps at the application level and RECOGNIZES intent, but never STATES a spec/cert/price/lead-time -
matching the flow. Reversible (toggles), so export/back up first.

1. **Back up first ("export for now"):** export the current flows + note the current data-source on/off state,
   so we can restore. (Flow export is a safe download; only import is blocked by the native picker.)
2. **Disable for Lyro** (do not delete) the spec-bearing sources:
   - PRL-Product-Catalog-2025 (the 150 spec Q&As)
   - PRL-Material-Selection
   - PRL-Competitor-Cross-Reference
   - Engineering_Thermoplastics
   - Polymer-Resources-Pro (verify content; disable if it carries property values)
   Keep them available for **Copilot** (human agents) if desired - the risk is only customer-facing Lyro.
3. **Keep for Lyro:** the prlresins.com website pages (public, application-level) + any scrubbed
   application-level source, so Lyro can still be a helpful catch-all and recognize what someone is asking about.
4. **Guidance (Behavior > Guidance):** enforce, in Lyro's own voice, the same rule the flow uses:
   - Never state a property value, test result, UL/cert status, price, or lead time. For any of those, say a PRL
     specialist will confirm, and capture the person (name/company/phone/email/what they need).
   - Same brand voice and tone as the flow greeting, so the handoff from flow to Lyro is seamless.
   - Recognize competitor grades / applications and route them; do not guess a match.
5. **Verify (Test Lyro / Playground):** ask "what's the UL rating / spec of PRL PC-G30?" -> Lyro must ROUTE +
   capture, not answer. Ask an application question -> Lyro helps at a general level. This is the acceptance test.

## (b) A/B (2-arm) test plan - LATER, gated on traffic + a real outcome
Do NOT run a multivariate test now: staging has ~0 delivered leads and a handful of conversations, so there is
no denominator and it would just burn per-conversation Lyro quota and return noise. Tidio also has no clean
native traffic-split for flows.

Prerequisites before any A/B:
- A countable outcome wired (lead captured -> delivered), AND real production traffic.

When those exist, run a **2-arm A/B (not full multivariate)** on the ONE variable that matters, holding
everything else constant, until significance:
- **Arm 1 (recommended default):** specs ROUTE to a specialist (scoped Lyro, per above).
- **Arm 2:** specs answered by Lyro from a *verified, current* subset with a certification safety note.
- Primary metric: qualified leads captured per 100 conversations. Guardrail metric: fabrication/complaint rate.
- Segment cleanly (audience or trigger), one variable only, pre-register the win condition.
Full multivariate (many variables at once) needs far more traffic than PRL will have for a while; the 2-arm A/B
is the right tool once there is signal.

## Sequence
1. Back up. 2. Scope Lyro + Guidance (a). 3. Verify with Test Lyro. 4. THEN wire delivery (1.1/1.2) and go to
production for traffic. 5. THEN the 2-arm A/B (b). Experience is coherent before a single lead is delivered.
