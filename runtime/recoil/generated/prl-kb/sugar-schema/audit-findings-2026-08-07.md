# SugarCRM read-only audit — findings (2026-08-07)
_Live read-only audit of Todd's production Sugar via the connected Zapier MCP (SugarCRMCLIAPI, "SugarCRM 7+
Importer"). Read-only: only Find Record / GET used, no writes. **PII redacted** — real customer names/emails/
phones are NOT stored here; only patterns._

## CONFIRMED: the email root cause (and the fix)
- Sugar's API exposes email via `email` (array, the relationship) + `email1`/`email2` (flattened). The DB has no
  `email` column, but **`email1` is a fully writable API field** — write to it and Sugar maintains the
  `email_addresses` relationship.
- **Live proof, two leads compared:**
  - A **Web Site** lead **manually entered by a sales rep** → `email1` populated, `email` array resolved. Email
    works when supplied.
  - A fresh **Unbounce-campaign** lead created by the **"Importer" system user** → `email` [], `email1` "" — no
    email, despite a real inquiry + phone.
- **Conclusion:** the field is not the problem; the **automated capture paths don't supply email**. Human entry
  captures it; the Unbounce/import path omits it. → This is exactly the gap the chatbot closes (Tidio captures
  email at inquiry, every time). **Webhook fix (confirmed): write email to `email1`.**

## Confirmed audit facts
- **No "Chatbot" `lead_source` value** — sampled leads use "Other" and "Web Site". Add "Chatbot" via Studio
  Dropdown Editor (gated write).
- **`phone_work` populated** on sampled leads; `location_c` present.
- **Rep routing is live** — leads assigned to named reps (territory/rep ownership already in use).
- **Real inquiries carry grade-level intent** — e.g. an unfilled **PA66 for fiber extrusion**, and **ABS/ABA**
  interest. Validates 1.3 recognition value (the bot should recognize these) and that specs/quantities show up
  in `description`.

## MarTech stack present (mostly unpopulated on direct leads)
Fields exist for: **Marketo** (`mkto_id`, `mkto_lead_score`, `mkto_sync`), **Sugar Hint** (`hint_*`
firmographics), **native AI scoring** (`ai_icp_fit_score_*`, `ai_lead_conv_score`, ICP/conversion bins),
**Salesfusion** (`sf_lastactivity_default`), `market_score`. On the sampled direct-capture leads these are all
null. So the **ZoomInfo emails (separate dataset) most likely arrive via a downstream enrichment/marketing flow
(Marketo/Salesfusion/Hint), not at capture** — which is why direct leads still lack email until/unless enriched.
To confirm: sample an enriched lead and see which of these is populated. Implication: the chatbot capturing
email at source is faster and more reliable than waiting on downstream enrichment.

## Data-quality signal (feeds the normalization eval)
- **`location_c` is inconsistent**: one lead "New Jersey" (full name), another "TX" (abbreviation). Mixed
  formats in the same field → a normalization target, and it affects any territory/region attribution.
- `lead_source` free-ish (Other / Web Site / Unbounce campaigns via `campaign_name`).

## Bonus: 1.4 validation
Live **Unbounce competitor-conquest campaigns** exist (e.g. a "SABIC"-targeted campaign feeding leads). Confirms
the 1.4 SEM/landing-page direction and the competitor-cross-reference angle are real and in-market.

## Still to read (read-only, next pass)
- An enriched lead → which of Marketo/Hint/ZoomInfo populates email + firmographics.
- Whether any SugarBPM/SLA process already runs (for the 4-hour metric).
- OEM↔molder: whether `account_id`/`contact_id` links are actually populated (both sampled leads had them
  empty — leads not yet linked to accounts/contacts; relevant to the OEM↔molder model question).
