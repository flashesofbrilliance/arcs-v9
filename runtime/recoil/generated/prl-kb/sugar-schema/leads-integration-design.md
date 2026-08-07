# SugarCRM 1.2 integration design (from public schema, no creds)
_2026-08-07 · Built from the public SchemaSpy docs (apidocs.sugarcrm.com/schema/25.2.0/ent) — no sandbox, no
credentials. This is the webhook/lead-delivery contract, ready to wire the moment sandbox access lands.
Compact column refs: `leads-columns.tsv` (106), `opportunities-columns.tsv` (55)._

## FINDING 1 — why emails aren't populating (CONFIRMED live 2026-08-07)
The `leads` table has **no `email` column** (Sugar stores email in the `email_addresses` relationship). BUT the
API exposes **`email1`** (flattened primary) and **`email`** (the array) as **writable fields** — write to
`email1` and Sugar maintains the relationship. **Live read-only audit confirmed the mechanism:** a rep-entered
Web Site lead had `email1` populated (email works when supplied); a fresh Unbounce-import lead created by the
"Importer" system user had `email1` empty. So the field is fine — **the automated capture paths just don't send
email.** **Fix (validated):** the lead-delivery webhook writes the captured email to **`email1`** on the Leads
module. This is exactly the gap the chatbot closes by capturing email at inquiry. See
`audit-findings-2026-08-07.md`.

## FINDING 2 — enrichment: Sugar has NATIVE "Hint" fields
Leads carry `hint_account_size, hint_account_industry, hint_account_location, hint_account_founded_year,
hint_industry_tags, hint_account_*` (SugarCRM **Hint** enrichment). So before paying for ZoomInfo, check
whether PRL's license includes Hint — it may already enrich firmographics natively. ZoomInfo would then only be
needed for the **email** gap (Finding 1). Decision for Todd: Hint (owned?) vs ZoomInfo (paid) for enrichment.

## Webhook → Leads field map (chatbot → sugar columns)
| Chatbot field | Sugar target | Notes |
|---|---|---|
| first name | `first_name` | |
| last name | `last_name` | |
| company | `account_name` (+ later `account_id` link) | account link = OEM/molder model, below |
| phone | `phone_work` | **required** per audit; enforce in the Flow form or placeholder |
| email | **email_addresses relation**, NOT a lead field | Finding 1 |
| application / grade interest | `description` (+ `lead_source_description`) | free text for MVP |
| — | `lead_source` = a "Chatbot" picklist value | audit: picklist has no chatbot value yet; add it |
| — | `status` = "New" | audit: 100/100 existing are "New" |
| — | `assigned_user_id` = Bill Galla (interim) | audit: 92/100 routed to him; territory auto-routing later |
| — | `date_entered` | auto; the clock-start for the 4-hour number |

## The 4-hour number — measurement design
- **Clock start:** `leads.date_entered` (lead created).
- **First touch:** earliest related activity. Leads link to activities via `calls_leads` (call_id ↔ lead_id),
  and analogous `*_leads` tables for meetings/emails. First-touch time = min(`calls.date_start`) for the lead.
- **Dependency (known):** this only works if reps **log** the call/activity. Per the hard guardrail, do NOT
  fix a missing first-touch by making reps log calls (turf-stepping). If activities aren't logged, use an
  **auto-proxy**: `date_modified` / first `status` change / assignment timestamp as the first-touch signal.
- Deliver as: time-to-first-touch per lead + the baseline (what it was before the chatbot channel).

## OEM ↔ molder model (the 1.2 audit question, now schema-grounded)
The relationship machinery exists: `leads.account_id`/`account_name` → `accounts`; `accounts_contacts`
(contact↔account, with a `primary_account` BIT) → who buys where; `accounts_opportunities` → deals per account.
So an OEM (spec-holder) and the molder (buyer) can both be Accounts linked to the same Contact/Opportunity. The
**open question is not "can Sugar model it" (it can) but "does PRL currently populate these links"** — that is
the read-only sandbox audit (blocked on access), not a schema question. Schema says the model is available.

## Closed-won / lost revenue by channel (attribution)
`opportunities` has `amount_usdollar`, `sales_stage`, `date_closed`, `date_closed_timestamp`, `probability`,
and **`lead_source`**. So "closed-won revenue by lead source, by region" (the attribution wedge, channel-level)
is fully supported once `lead_source="Chatbot"` exists and flows Lead→Opportunity. No schema blocker.

## What this unblocks NOW (no creds)
The entire field-map, the email-relationship fix, the enrichment decision framing, the 4-hour query design, and
the attribution query design are all designed from public schema. Sandbox is needed only to (a) confirm the
email path, (b) see whether OEM/molder links + activities are actually populated, (c) run the live baseline.
Everything is now execution-ready, not discovery.
