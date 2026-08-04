# PRL Resins — Zapier → SugarCRM "Create Lead" mapping (STAGED, no production write)

_2026-08-03 · grounds the Catch Hook → SugarCRM Create Record step against the LIVE Leads schema
(pulled via Zapier MCP `sugarai_create_record`, module=Leads, connection "SugarCRM 7+ Importer")._

**Status: staged, not wired, nothing written to SugarCRM.** Do not execute a write against the
client's production Sugar before Todd approves one labelled test lead (or a sandbox is confirmed).

## The chain
```
Tidio flow (webhook/API node)  →  Zapier Catch Hook (trigger)  →  SugarCRM Create Record (module Leads)
                                        └ optional: Gmail notify (existing draft Zap)
```

## Live Leads REQUIRED fields (6) — verified from the action schema
`account_name` · `first_name` · `last_name` · `lead_source` · `location_c` · `phone_work`

**The problem staging caught:** the chatbot currently captures a single `name`, treats `phone` as
optional, and may not force `company` or `state`. Sugar rejects a create if ANY required field is
empty. So without the fixes below, real chatbot leads fail to create.

## Field mapping (Tidio payload → Sugar Leads)
Tidio session variables carried on the webhook: `name, email, phone, company, state, message, title`.

| Sugar field (key) | Req | Source | Handling / note |
|---|---|---|---|
| `module` (param) | ✓ | const `Leads` | |
| `account_name` | ✓ | `{{company}}` | If bot leaves company blank → **create fails.** Make company required in bot, or fall back to a constant like `Individual / not given`. |
| `first_name` | ✓ | `{{name}}` → first token | Bot captures ONE name field. Add a **Zapier Formatter → Split Text** (by space): first segment. |
| `last_name` | ✓ | `{{name}}` → remaining tokens | Same split. **Single-word name → last_name empty → create fails.** Fallback `last_name = "(chatbot)"` when empty. |
| `lead_source` | ✓ | const | **No "Chatbot" picklist value exists** (options: …Web Site, …Other…). Use `Web Site` now, OR Todd adds a `Chatbot` value (decision). |
| `location_c` | ✓ | normalize(`{{state}}`) | **SELECT accepts state ABBREVIATIONS for US** (`AL,AZ,CA,…,MI,…,NY,…`), plus a few full names (Canada-Ontario, MEXICO, CHINA…). Bot free-text state must be mapped to a key. **Discrepancy to verify:** the Jul-30/Aug-03 handoff claimed live records store FULL state names; the action's picklist keys are abbreviations. Confirm against a real existing lead before go-live. |
| `phone_work` | ✓ | `{{phone}}` | **Phone is optional in the bot → blank blocks create.** Decision: require phone in bot, OR set a placeholder (e.g. `000-000-0000`) when blank. |
| `email1` | – | `{{email}}` | The value proof: ~95% of existing leads have no email; the bot captures it every time. |
| `description` | – | compiled | `{{message}}` + role `{{title}}` + `Source: PRL website chatbot` + timestamp. |
| `status` | – | const `New` | Matches 100/100 existing. |
| `assigned_user_id` | – | Bill Galla | Pick "Bill Galla" in the Zap dropdown (92/100 existing route to him). |
| `team_id` | – | Global | Pick "Global" (all records are on team Global). |
| `title` | – | `{{title}}` | Job role, if captured. |

## The 3 client decisions this blocks on (surface to Todd)
1. **Phone:** required in the bot, or placeholder on blank? (`phone_work` is required in Sugar.)
2. **Lead source:** add a `Chatbot` picklist value in Sugar, or ride `Web Site` for now?
3. **Test lead:** approve ONE clearly-labelled test lead against production, or stand up a sandbox?
   (All records are on team "Global" — no record-level privacy — so a test lead can't be hidden.)

## Build steps (Zapier UI — Zach), ready to execute once Tidio webhooks are unblocked
1. In the existing Zap (Catch Hook), add action **SugarCRM → Create Record**, module **Leads**,
   account **SugarCRM 7+ Importer**.
2. Insert a **Formatter → Split Text** step on `name` (separator: space) before the Sugar step;
   map first segment → `first_name`, remaining → `last_name` (with the empty-fallbacks above).
3. Map the table above. Constants: `lead_source`, `status=New`, assigned user, team.
4. Do NOT turn the Zap on against production until Todd signs off on the test lead.

## Verify-before-go-live checklist
- [ ] `location_c` format resolved against a real lead (abbreviation vs full name).
- [ ] Copy the exact field handling from the existing Unbounce→Sugar Zap (proven-good mapping).
- [ ] Tidio plan upgraded so the webhook node can POST (still the upstream blocker as of Jul 30).
- [ ] One labelled test lead approved by Todd; confirm it lands, assigned to Bill Galla, status New.
