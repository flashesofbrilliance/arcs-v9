# PRL Resins Chatbot — Tidio Build Sheet v1 (Phase 1 MVP)

This is the hands-on build guide: it takes the branch-logic map (v1.2) and turns it into
click-by-click Tidio Flow instructions. Build this in the free Tidio account now. Wire the
CRM/email destinations later, once SugarCRM access lands. Nothing here touches Todd's live
WordPress or SugarCRM.

## What we can build today vs. what waits

| Now (free Tidio account) | Waits on access |
|---|---|
| The whole conversation flow (greeting, A/B/C branches, contact capture) | SugarCRM lead creation (needs API key + field map) |
| Quick-reply buttons and branching | Territory auto-routing (needs the rep→region map) |
| Saving answers as visitor attributes | Email notification to the real sales manager |
| Resin-name + competitor-name recognition (keyword triggers) | Fit-tag rules (needs SM's ideal/poor-fit criteria) |
| Testing the full path in Tidio preview | Embedding on the real prl-resins.com site |

So today's goal: a fully clickable flow that captures every field correctly and routes to a
placeholder (your own email) so we can watch a real lead land end-to-end.

## Tidio concept map (their words for our pieces)

| Our design | Tidio primitive |
|---|---|
| A conversation path | **Flow** (Chatbots → Flows → new flow) |
| Bot says something | **Send a Message** node |
| Quick-reply buttons (A/B/C) | **Decision** node (each button = a branch) |
| Ask and store an answer | **Ask a question** node → save as **Visitor attribute** |
| "If they said X" logic | **Condition** node (checks an attribute) |
| Recognize a resin/competitor word | Flow trigger: **Visitor sends a message containing…** (keyword list) |
| Create the lead | **Integration / Webhook** node (SugarCRM later) |
| Notify the rep | **Send email** node (or Zapier/webhook) |

## Step 0 — turn OFF Tidio's default flows (do this first)

A new Tidio account ships with default flows, including a "Subscribe now / promotions"
newsletter card and a generic welcome. **We do not want any of these.** No newsletter, no
marketing opt-in. The bot only qualifies leads.
- Chatbots → Flows → find every default/template flow (Welcome, Collect emails, Subscribe,
  Offer/Discount) → toggle each **OFF** (or delete).
- Settings → check there is no standalone "email subscription" / pre-chat marketing widget on.
- Then build our single lead-capture flow below as the only active flow.

## QATF001 field mapping (what the bot saves → the SM's form)

Every attribute the bot captures maps to a field on the SM's New Opportunity Form (QATF001), so
the lead arrives with the top of that form pre-filled. Keep the bot short — the rep completes the
rest on the callback.

| Bot attribute | → QATF001 field |
|---|---|
| `name` | Customer Contact |
| `email` | Email |
| `phone` | Phone |
| `company` | Customer Name |
| `job_title` (optional) | Job Title |
| `territory` | routing + Shipping region |
| `current_resin` | Current Grade |
| `current_supplier` (optional) | Current Supplier |
| `reason_for_change` (optional) | Reason for Change |
| `desired_resin_or_spec` | opportunity context |
| `application` | Application Details / Problem to be solved |
| `requirements` | Special Tests or Requirements |
| `indoor_outdoor` (optional) | End Use Environment |
| `potential_volume` (optional) | Potential Volume |

**Rep collects on callback (bot does NOT ask):** addresses, pricing, order dates, release
quantities, the full material-properties checklist, color match, sample logistics.

## Trigger setup (how the flow starts)

Create ONE main flow, triggered two ways:
1. **Proactive:** trigger = "Visitor is on page for 5 seconds" (later scope to product pages).
2. **On click:** trigger = "Visitor opens the chat."

Later add a second lightweight flow triggered by **"Visitor sends a message containing"** with
the resin keyword list (see Resin recognition below) so a visitor who just types "Ultem" jumps
straight into Branch A pre-filled.

## The flow, node by node

### Node 1 — Greeting (Send a Message + Decision)
Message:
> "Hi. Looking for a resin, a spec match, or an alternative to what you use now? I can get you
> to the right person fast. What brings you in?"

Decision node, three buttons:
- **A — I know the resin or spec I need** → go to Branch A
- **B — I need help finding the right resin** → go to Branch B
- **C — Something else** → go to Branch C

### Branch A — knows what they need
1. Ask a question: "Which resin or spec are you after?" → save attribute `desired_resin_or_spec`
2. Decision: "Are you replacing a resin you use now?" [Yes / No]
   - Yes → Ask: "What are you using currently?" → save `current_resin`
   - No → continue
3. Ask: "What's the application?" → save `application`
4. Ask: "Any key requirements or specs? (optional)" → save `requirements`
5. Set attribute `branch = ready-to-spec` → go to Contact capture

### Branch B — needs help
1. Ask: "No problem. What are you making? Tell me about the application." → save `application`
2. Ask: "Any material or performance requirements? Temperature, flexibility, color, or a
   regulatory spec. (optional)" → save `requirements`
3. Decision: "Are you currently using a resin you'd want to match or improve on?" [Yes / No]
   - Yes → Ask: "What are you using now?" → save `current_resin`
4. Set attribute `branch = needs-help` → go to Contact capture

### Branch C — something else
1. Ask: "Happy to help. What can I point you to?" → save `question`
2. Send a Message: "Want someone to follow up? Share your details and I'll route it."
3. Decision: [Share details → Contact capture] / [No thanks → polite end]
4. Set attribute `branch = general`

### Contact capture (shared)
1. Ask: "Who should we get this to? (Name)" → save `name`
2. Ask (email validation ON): "Best email?" → save `email`
3. Ask: "Phone? (optional)" → save `phone`
4. Ask: "Company?" → save `company`
5. Ask: "What state or region are you in?" → save `territory`
   (Later: replace with silent IP geolocation where available.)

### Handoff / close
1. Integration node → create SugarCRM lead with all attributes (WIRE LATER).
   Today: use a **Send email** node to your own address as the placeholder so we see the payload.
2. Send a Message: "Thanks. One of our resin specialists will reach out shortly, usually within
   a few hours."

## Resin recognition (keyword triggers)

Second flow, trigger = "Visitor sends a message containing" any of these. On match, set
`desired_resin_or_spec` = the matched term and jump into Branch A step 2.

**PRL family prefixes:** PC, ABS, ASA, PEI, PPX, NY6, NY66, TP, PC/ABS, PC/PBT, PC/ASA, PPX/Nylon

**Competitor names (recognize as a real ask):** Lexan, Makrolon, Calibre (PC) · Ultem (PEI) ·
Noryl (PPE) · Lustran, Cycolac (ABS) · Valox (PBT) · Zytel, Vydyne, Akulon (nylon)

Grade-string autocomplete (full `FAMILY-MODIFIER+COLOR-SUFFIX` parsing) is a fast-follow, not v1.

## Attributes to create in Tidio (do this first)

Chatbots → Settings → Visitor attributes. Create: `desired_resin_or_spec`, `current_resin`,
`current_supplier`, `reason_for_change`, `application`, `requirements`, `indoor_outdoor`,
`potential_volume`, `name`, `email`, `phone`, `company`, `job_title`, `territory`, `branch`,
`question`, `lead_source` (default "website chatbot"), `fit` (blank until SM criteria arrive).

## Test checklist (Tidio preview)

- [ ] Run each branch A / B / C start to finish
- [ ] Confirm every answer saves to the right attribute (check the visitor panel)
- [ ] Bad email is rejected by validation
- [ ] Placeholder email lands with all fields populated
- [ ] Keyword trigger ("Ultem", "PC/ABS") jumps into Branch A
- [ ] Optional questions can be skipped

## Open items carried from the logic map

1. Exact required-vs-optional field set (from the SM's discovery form)
2. Territory map (rep → region) for auto-routing
3. ICP / poor-fit criteria → drives the `fit` tag
4. FAQ content for Branch C

_Version: v1.1 · 2026-07-30 · source: branch-logic-map v1.3 (incl. QATF001 New Opportunity Form
+ material-selection matrix from the SM). Build target: free Tidio account + local Docker
sandbox. Default Tidio flows OFF (no newsletter). CRM/email destinations stubbed to a placeholder
until SugarCRM access._
