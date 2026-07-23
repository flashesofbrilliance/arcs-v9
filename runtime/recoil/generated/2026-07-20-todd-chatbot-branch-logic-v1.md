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
1. **Exact fields** (required vs optional) from the product-development / application-discovery form. Todd gave the concepts; the form confirms the precise set (and any spec properties like durometer, color, UL, temperature).
2. **Territory map** (rep → states/regions) to turn on auto-routing. Until then, route to the SM.
3. **Resin product list + nomenclature** so the bot can recognize (and optionally autocomplete) a resin name the visitor gives.
4. **ICP / poor-fit criteria:** what makes a prospect ideal versus a poor fit, company size, industry, order volume, or anything else the SM uses to prioritize. Until answered, no fit tag ships and every lead is treated the same.
5. **FAQ content** for Branch C (optional).

_Version: v1.1 · 2026-07-23 · source: Todd Hotes Jul 20 email answers + Jul 2/9 call transcripts. v1.1 adds ICP/poor-fit gating as a soft triage tag, pending SM criteria._
