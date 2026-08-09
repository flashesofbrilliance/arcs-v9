# PRL chatbot audiences = the two ICPs (injection molder vs OEM)
_2026-08-09 · Grounded in Todd's own framing across the Granola call transcripts. The two Tidio Audiences map
to PRL's two ICPs. This is the persona/qualification axis; the markets page (prlresins.com/markets) is a
separate APPLICATION axis (EE / medical / transportation / building / consumer / sustainability)._

## The two ICPs (Todd's framework)
The resin is identical either way; the difference is who you approach and why.

| | **Injection Molder** | **OEM / engineer** |
|---|---|---|
| Primary need | Source + buy a resin already specified | Spec a resin onto a print; set requirements |
| Knows the grade? | YES (e.g. "PC FR2") | No - needs formulation help |
| Relationship | Transactional, low-friction | Strategic, long-term, value-based |
| Asks about | Lead time, price, availability | Formulation, application fit, certs/approvals |
| Who's on the call | Purchasing / sourcing | Engineers |
| References | A mold, a part, the OEM they produce for | A brand, a product line, an end product |
| PRL rep | Territory rep | One of 2 dedicated OEM reps |
| Todd's "scenario" | Scenario A (knows resin -> fastest path to rep) | Scenario B (has application -> needs help) |

Why it matters commercially: get specified on the OEM's print and you are hard to displace (high switching
cost) and it compounds across every molder that supplies that OEM. Molders are the transactional near-term
volume. So the two experiences are genuinely different journeys, not cosmetic.

## Qualification (how the bot tells them apart, early)
One or two questions up front, then set a contact property/tag and branch:
- **Opening branch:** "Do you already know the grade you need, or are you looking for help choosing?"
  - "I know the grade / I want to buy" -> **Molder path**.
  - "Help me choose / I have an application" -> **OEM path**.
- Reinforcing signals (auto-detect where possible):
  - Molder: names a specific grade, mentions a mold/part/contract, asks lead time/price/availability, names an
    OEM they produce for.
  - OEM: describes an application/end product, references a brand, mentions engineers, asks about specifying,
    certifications, or agency approvals.

## The two experiences (both ROUTE; never state a spec)
- **Molder audience -> fast lane.** Confirm the grade, capture (name/company/phone[req]/email/grade), route to
  the **territory rep** fast. Minimal AI. This is mostly a Flow + immediate handoff (0 Lyro quota). Todd's
  lowest-friction path.
- **OEM audience -> consultative lane.** Recognize the application/market, help at the application level only,
  route the formulation/spec/cert to one of the **2 dedicated OEM reps** and the official data sheet, capture
  the lead. Lyro can carry more of this conversation (its quota is best spent here), but still never states a
  property/cert value - routes it.

Consistency rule holds in BOTH: never fabricate a spec/cert/price/lead-time; capture every time; same voice.
The difference is destination (territory vs OEM rep) and tone (transactional vs consultative), not the guardrail.

## Tidio implementation (pending the audience-availability check)
- If custom Audiences are available on this plan: two Audiences ("Molder", "OEM") stamped by the opening branch
  (Update Contact Property + Condition), each with its own handoff target (territory vs OEM rep) and, if
  audience-scoped, its own Lyro guidance. Data sources: specs Copilot-only for both.
- If audiences are Plus-gated: one flow with a decision node that branches molder vs OEM to two capture/route
  paths + two handoff routings; Lyro stays global + scoped (specs Copilot-only). Slightly less rich but same
  journeys.
- Routing to named reps: molder -> territory owner; OEM -> the 2 OEM reps (per MVP, assign to the named
  rep/Bill Galla until territory rules are switched on; see the Sugar delivery spec).

## Open
- Verify custom-audience availability on this non-Plus plan (Manage/three-dot on a data source).
- Get the exact rep routing (territory map + the 2 OEM reps' names) from Todd.
