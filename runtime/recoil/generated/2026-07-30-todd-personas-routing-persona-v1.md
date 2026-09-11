# PRL Chatbot — Personas, Routing, Bot Persona, Policies v1 (titles only)

Four design layers from the live site. **Names redacted per operator instruction: roles and
titles only.** The actual rep names/emails live on prlresins.com/our-team and in SugarCRM, and
get wired at implementation time, not written into build artifacts.

## 1. Market personas (from /markets/) — "I am a ___ solving for ___"

A third entry alongside "know what I need" / "help me choose": start from WHO the visitor is.
PRL's five market segments become the persona picker, each mapping deterministically (a lookup,
not AI) to the material families that fit via the Good/Better/Best matrix.

| "I'm working in..." (market) | Typically needs | Deterministic family shortlist |
|---|---|---|
| **Electrical** | flame retardance, electrical insulation, dimensional stability | PEI, PPO/PPE, PBT, PC |
| **Non-invasive Medical Devices** | sterilizable, high heat, transparency, compliance | PEI, PC |
| **Consumer Goods** | appearance, cost, processability | ABS, PC/ABS |
| **Building & Construction** | impact, UV/weather, flame | PC, ASA, PC/ASA, PPO/PPE |
| **Transportation** | heat, chemical resistance, impact, underhood | PC/PBT, PPE/PA, Nylon 66, PC/ABS |

Flow: "What are you building for?" → 5 market buttons → "What matters most?" (2–3 requirement
chips from that market's row) → shortlist: "For [market] with [requirement], teams usually look
at [families]. I'll flag that for a specialist to confirm." → capture. Tag `market`.

Persona in, filtered options out, human to confirm. The recommendation is a deterministic lookup,
never a hallucinated spec.

## 2. Territory routing map (from /our-team/) — titles + territories only

The account managers publish their territories. Strong draft routing table by TITLE + territory;
confirm gaps/overlaps with the VP of National Sales before turning on auto-routing.

| Role | Territory (as published) |
|---|---|
| Account Manager | Central & South Central US, Mexico |
| Account Manager | IL, WI |
| Account Manager | Mid-Atlantic, FL |
| Account Manager | OH, Western PA, Western NY |
| Strategic Account Manager | New England, West Coast, nationwide OEM development |
| Account Manager | Southeast, Southern CA |
| Distribution & Customer Service Manager | Global (distribution / service) |
| VP, National Sales | MVP catch-all + assigner |

**MVP (operator preference): keep it simple — one fielding inbox.** The webhook emails every
lead to a single fielding address (the VP of National Sales, or one shared inbox), and that
person forwards/assigns as they do today. No territory logic to build or maintain in v1.
**Target (later):** map the visitor's state → the role above → assign directly; unmapped → the
fielding inbox. Turn this on only after the map is confirmed. Rep names/emails are pulled from
SugarCRM / the team page at wiring time, not stored in build artifacts.
**Gaps to confirm before any auto-routing:** much of the West/Mountain and some state detail is
not explicitly covered on the public page.

## 3. Bot persona — titled role, not a person's name

Show the widget as a titled role, not a named employee. **Operator choice for v1: the typing
indicator reads "Customer Service Manager, Global"** (title only, refine later). This keeps the
warmth of a real person without putting an employee's name on automated messages, and matches the
redact-names rule. Optionally pair with a neutral avatar. Real handoff still goes to the right
role (specialist / customer service / account manager), matching "straight to the source."

## 4. Policies (from /policies/) — recommendation + trust/FAQ source

Children: ISO 9001 Certificate · Supplier Sustainability · Ethics · Diverse Supplier · Guiding
Principles · Conditions of Sale (+ Quality Guarantee, COVID). Use for:
- **Compliance answers** when requirements include agency/regulatory (UL, ISO, FDA, RoHS/halogen):
  confirm "we're ISO 9001 certified," link the certificate, tag `requirements` accordingly.
- **Branch C FAQ**: trust questions (quality guarantee, terms/Conditions of Sale, sustainability,
  diverse supplier) get a one-line answer + link, then offer a human.
- Factual + link only; never paraphrase a policy into a promise.

## Attributes to add
`market` (Electrical / Medical / Consumer / Building / Transportation) · `assigned_rep` (from
territory lookup, once on). Keep the rest from the build sheet.

_Version: v1 · 2026-07-30 · sources: /markets/, /our-team/, /policies/ + material matrix +
branch-logic map v1.3. Names redacted, titles only._
