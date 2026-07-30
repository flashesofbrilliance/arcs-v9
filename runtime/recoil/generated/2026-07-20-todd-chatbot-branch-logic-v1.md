# PRL Resins Chatbot — Branch-Logic Map v1 (Phase 1 MVP)

Built from Todd's Jul 20 discovery answers. This is the conversation design for the Tidio
flow: what the bot says, how it branches, what it captures, and where the lead goes.

## Design principles (from Todd's answers)
- **Keep it short.** People searching for PRL usually already have a need and share info readily. Do not over-ask.
- **Qualify on specifics.** A real lead names a resin PRL sells, a spec, or an application. Vague = researcher.
- **Capture what a rep actually uses:** contact info, current material/resin, application, requirements/specs, and either the alternate resin they want to replace or the specific resin they want.
- **Deliver both ways:** create a SugarCRM lead AND email the notification.
- **Route by territory when possible.** Geolocate the visitor and assign to the rep for that territory. For the MVP, route to the sales manager and let him assign.
- **Set a fast-reply expectation.** Todd targets about 4 hours. The bot promises a quick follow-up.

## The flow

### 0. Greeting (proactive after ~5s, or on click)
> "Hi. Looking for a resin, a spec match, or an alternative to what you use now? I can get you to the right person fast. What brings you in?"

Quick-reply buttons:
- **A — I know the resin or spec I need**
- **B — I need help finding the right resin**
- **C — Something else / general question**

### Branch A — knows what they need (fast qualify)
1. "Which resin or spec are you after?" → capture `desired_resin_or_spec`
2. "Are you replacing a resin you use now?" [Yes / No]
   - If Yes: "What are you using currently?" → capture `current_resin`
3. "What's the application?" → capture `application`
4. "Any key requirements or specs? (optional)" → capture `requirements`
5. → **Contact capture**. Tag lead `ready-to-spec`.

### Branch B — needs help (research path, still light for MVP)
1. "No problem. What are you making? Tell me about the application." → capture `application`
2. "Any material or performance requirements? For example temperature, flexibility, color, or a regulatory spec. (optional)" → capture `requirements`
3. "Are you currently using a resin you'd want to match or improve on?" [Yes → capture `current_resin` / No]
4. → **Contact capture**. Tag lead `needs-help`.
   - Note: the actual "recommend a formulation" AI is a later phase. The MVP captures the details and routes to a human.

### Branch C — something else
1. "Happy to help. What can I point you to?" → capture `question`
2. If it matches an FAQ (list TBD from the SM): answer inline, then offer to connect a human.
3. "Want someone to follow up? Share your details and I'll route it." → **Contact capture** (tag `general`, low priority), or end politely.

### Contact capture (shared by A and B; optional for C)
- "Who should we get this to? (Name)" → `name`
- "Best email?" → `email`
- "Phone? (optional)" → `phone`
- "Company?" → `company`
- Location for routing: geolocate by IP silently if available; otherwise ask "What state or region are you in?" → `territory`

### ICP / fit gating (open, pending SM input)
Sits right before handoff, after the core fields (A/B) are captured. Not a hard gate: the bot
never refuses to submit a lead. It's a soft tag that helps the sales manager triage what lands
in his inbox, matching how he described qualification today (screening, not blocking).
- Compare the captured fields (application, current resin, company, requirements) against the
  SM's ideal-vs-poor-fit criteria once he gives them: things like company size, industry,
  order volume, or geography.
- Tag the lead `fit: ideal`, `fit: uncertain`, or `fit: poor` on the SugarCRM record. A
  poor-fit tag does not block the lead or change what the visitor sees, it just tells the rep
  where to spend attention first.
- **Blocked until the SM answers:** what "ideal" and "poor fit" actually look like. This is now
  its own open dependency (see below), not just a nice-to-have. Until it's answered, every lead
  ships untagged and goes to the sales manager exactly as today.

### Handoff / close
- Create a **SugarCRM lead** with every captured field + the branch tag + the fit tag (once
  defined) + `lead_source = website chatbot` + timestamp.
- **Email** the notification to the rep for that territory, or to the sales manager for the MVP.
- Set expectation: "Thanks. One of our resin specialists will reach out shortly, usually within a few hours."
- Optional (later phase): "Want the spec or tear sheet emailed while you wait?"

### Persistence (abandonment recovery)
- If the visitor gives a name or email then leaves, save the partial lead.
- On return: "Welcome back. Want to pick up where we left off?"

## Resin catalog + nomenclature (received Jul 23, from the Product Selection Guide 2025)

Todd sent the Product Selection Guide, which satisfies the resin-list dependency. The bot can now
recognize a resin name the visitor types, validate it, and even recognize when someone names a
competitor grade instead. Three usable layers:

**1. Product families (what PRL sells).** The prefix codes the bot should recognize:
- `PC` Polycarbonate · `ABS` · `ASA` · `PEI` (Ultem-class) · `PPX` Modified PPE (Noryl-class) ·
  `NY6` Nylon 6 · `NY66` Nylon 6/6 · `TP` PBT (polyester)
- Blends: `PC/ABS` · `PC/PBT` (PC/TP) · `ABS/PBT` · `PC/ASA` · `PPX/Nylon`

**2. Nomenclature grammar (so the bot can parse a grade string).** Pattern is
`FAMILY - MODIFIER + COLOR-SERIES - SUFFIX`, e.g. `PC-FRUV2-7001-1` = Polycarbonate, flame-retardant
+ UV-stabilized, black, with release.
- **Modifiers:** GP general purpose · FR flame retardant · G glass fiber · SF structural foam ·
  EN extrusion · UV UV-stabilized · MF mineral filled · IM impact modified · FD FDA feedstock ·
  TFE lubricated · HH/HM/HG/HF heat/modulus/alloy/flow · S sustainable/recycled
- **Color series:** 1000 transparent · 2000 blue · 3000 green · 4000 yellow/orange · 5000 brown/tan ·
  6000 red · 7000 black/gray · 8000 white
- **Suffix:** -1 release · -2 lubricant · -3 UV · -4 UV+release · -5 FDA · -6 FDA+release · -7 low-gloss+UV

**3. Competitor cross-reference (recognize a resin PRL does not brand).** The guide maps PRL grades to
common competitor products, so when a visitor names one, the bot recognizes it as a real resin ask and
tags it for the rep. Families to watch for: Lexan (PC), Makrolon (PC), Calibre (PC), Ultem (PEI),
Noryl (PPE), Lustran/Cycolac (ABS), Valox (PBT), Zytel/Vydyne/Akulon (nylon).

_Build note:_ ship the family-prefix recognizer + competitor-name recognizer first (cheap, high value).
Full grade-string autocomplete is a fast-follow. The injection-molding troubleshooting guide in the same
PDF is a ready FAQ source for Branch C in a later phase.

## SM intake form mapping (QATF001 New Opportunity Form v1.1, received Jul 30)

The sales manager confirmed the "need to have" fields by sending his actual intake form,
QATF001. It is a detailed internal sales form (it even has a "Filled Out During Production
Meeting" section). The bot must NOT reproduce all of it. Todd's #1 rule was keep it short. So
the bot captures a lightweight qualifying subset, and every field it captures maps to a QATF001
field, so the lead the rep receives has the top of the form already filled in. The rep collects
the rest (full property checklist, pricing, addresses, sample logistics) on the callback.

**Bot captures now → QATF001 field:**
| Bot question | QATF001 field | Notes |
|---|---|---|
| name | Customer Contact | |
| email | Email | |
| phone (optional) | Phone | |
| company | Customer Name | |
| job title (optional) | Job Title | one quick ask |
| state / region | (routing + Shipping Address region) | |
| "using a material now?" Yes/No | Currently Buying Material | |
| current_resin | Current Grade | |
| current supplier (optional) | Current Supplier | |
| reason for change (optional) | Reason for Change | |
| desired_resin_or_spec | (opportunity context) | drives rep read |
| application | Application Details / Problem to be solved | |
| requirements (free text) | Special Tests or Requirements | |
| indoor / outdoor (optional) | End Use Environment | quick toggle |
| potential volume (optional) | Potential Volume | volume = fit signal |

**Rep fills on callback (bot does NOT ask):** Billing/Shipping Address, Current Price, Est.
Selling Price, Est. Prod. Order Date, Release Quantities, the full Material Properties checklist
(Impact/Flexural/Tensile/HDT/Shrinkage/UL/Halogen/Wear/Electrical/Chemical/UV/etc.), Color
match, all Sample Information, and the entire Product Recommendation section.

**Still open (dropdown option lists):** QATF001 uses "Choose an item." dropdowns for
**Opportunity Type**, **Opportunity Sub-Type**, and **Problem to be solved**. We need those
option lists from the SM to pre-tag the lead precisely. Until then the bot passes free text.

## Material selection matrix (received Jul 30) — Branch B recommender source

The SM also sent an Engineering Thermoplastics Material Selection Matrix (Good/Better/Best across
12 features for 12 families: PC, ABS, ASA, PBT, PEI, PPO/PPE, PA6, PA66, PC/ABS, PC/ASA, PC/PBT,
PPE/PA). It rates each family Best/Better/Good on Impact, Stiffness, Heat, Dimensional Stability,
Moisture, Chemical, UV, Electrical, Flame, Surface, Processability, Cost, plus a one-line primary
application advantage per family.

**Use:** in Branch B (help me choose), when a visitor names a driving requirement (for example
"outdoor + UV" or "high heat" or "lowest cost"), the bot can surface a Good/Better/Best family
suggestion from this matrix and tag it for the rep. A small rules table, not AI, is enough for a
first pass (for example UV-critical → ASA "Best"; high heat → PEI/PPO "Best"; lowest cost → ABS
"Best"). Full recommendation AI stays a later phase.

## Fields → SugarCRM lead
| Field | Source | Notes |
|---|---|---|
| name, email, phone, company | contact capture | phone optional |
| intent / branch | A / B / C | drives the rep's read |
| desired_resin_or_spec | A | the ask |
| current_resin | A2 / B3 | the resin to match or replace |
| application | A3 / B1 | what they're making |
| requirements | A4 / B2 | specs, properties, regulatory |
| territory | contact capture | for routing |
| fit | ICP gate (pending) | `ideal` / `uncertain` / `poor` — triage only, never blocks |
| lead_source | fixed = "website chatbot" | attribution |
| created_at | system | for the fast-reply clock |

## Routing logic
- **MVP:** every lead → SugarCRM + email to the sales manager. He assigns to the rep by territory (his current process).
- **Target:** geolocate (IP or the asked state) → look up the rep for that territory → assign directly. Requires the territory map.
- **Fit tag (once defined):** rides along on the same lead, does not change routing destination or speed. It's a triage signal for the rep/SM, not a filter.

## Open dependencies (the "still needed from the SM" list)
1. ~~**Exact fields** (required vs optional) from the product-development / application-discovery form.~~ **SATISFIED Jul 30** — the SM sent QATF001 New Opportunity Form v1.1. See "SM intake form mapping" above. Sub-item still open: the dropdown option lists (Opportunity Type, Sub-Type, Problem to be solved).
2. **Territory map** (rep → states/regions) to turn on auto-routing. Until then, route to the SM.
3. ~~**Resin product list + nomenclature** so the bot can recognize (and optionally autocomplete) a resin name the visitor gives.~~ **SATISFIED Jul 23** — Todd sent the Product Selection Guide 2025. See the "Resin catalog + nomenclature" section above.
4. **ICP / poor-fit criteria:** what makes a prospect ideal versus a poor fit. Partial signal now from QATF001 (Potential Volume, Release Quantities = half/full truckloads, Est. Selling Price) but the SM has not stated explicit ideal-vs-poor thresholds. Until answered, no fit tag ships and every lead is treated the same.
5. **FAQ content** for Branch C (optional).

_Version: v1.3 · 2026-07-30 · source: Todd Hotes Jul 20 email answers + Jul 2/9 call transcripts + Product Selection Guide 2025 + QATF001 New Opportunity Form v1.1 + Engineering Thermoplastics Material Selection Matrix (both from the SM, Jul 30). v1.1 added ICP/poor-fit gating. v1.2 folded in the resin catalog + nomenclature. v1.3 folds in the SM intake-form field mapping and the material-selection matrix, and marks the exact-fields dependency satisfied._
