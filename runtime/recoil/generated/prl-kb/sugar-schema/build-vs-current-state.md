# SugarCRM: as-built (W-Systems, 2020) vs current state (internal)
_2026-08-07 · From the two W-Systems build docs (Forecast Module Specs + Solution Design) compared to the live
state observed read-only this week. Corrects several earlier assumptions. Internal reference for 1.2 field work._

## As-built (W-Systems, ~2020, Sugar 9.3 Enterprise On-Demand)
- **Implementer:** W-Systems. **ERP:** IQMS (manufacturing vertical), daily sync; goal = kill double-entry /
  replace spreadsheets. Sales history lives in **custom modules**: Open Orders, Open Order Line Items, Order
  History, Order History Line Items.
- **Account model:** Bill-To vs Ship-To, keyed to **IQMS Ship-To / Customer #**. **No OEM-vs-molder / channel
  modeling** in the build (correction to earlier assumption). Competitors held as a dropdown on Leads/Opps.
- **Forecast module:** deliberately "simple" 3-value per Account (Prev-Year Sales / Current-YTD Sales / Active
  Pipeline), on a wClusterBar, rolled up by Sales Rep. Rep "override" = editing the Opportunity Revenue Line
  Items (no override field). Built on wCalculated Field Updater + BPM Workflow.
- **Roles:** two only (Admin, Sales Rep), both **View-All / Edit-All** -> explains the live "everything on team
  Global, no record privacy." No territory model was designed.
- **Leads: manual-entry by design. Web-to-Lead was NOT built.** Supporting tools: Outlook Plugin (2-way, match
  on email), wMobile, wDocs (quote PDFs), wBenchmarks.

## Now vs build (drift)
- **Version:** Sugar 9.3 -> 25.2 (REST v11), ~5 years.
- **Biggest divergence: leads went from all-manual to automated capture** (Importer user, Unbounce, formerly
  Gravity-Forms->Zapier). None of that was in the build.
- **Whole enrichment/marketing stack is post-build and undocumented:** hint_* (Sugar Hint), mkto_* (Marketo),
  ai_icp_fit_*/ai_lead_conv_* (native AI scoring), sf_lastactivity (Salesfusion), market_score. Mostly NULL on
  direct leads.
- **Broken/decayed:** ZoomInfo writeback OAuth **expired**; GF->Zapier **inactive**; ZoomInfo import just
  re-enabled. **IQMS daily sync and the Outlook plugin are unconfirmed post-upgrade — worth verifying they
  survived 25.2.**
- **Email gap is a byproduct of later automation:** build assumed manual entry (rep types email); automated
  paths omit it; Leads have no email column (uses email_addresses / email1).

## Insights for the chatbot sync + 1.2 field work
- **lead_source:** add a **"Chatbot"** picklist value (build-consistent; mirrors Unbounce via campaign_name).
  Until then use "Web Site" + stamp campaign_name.
- **Write plain Lead fields + email1** (via the email_addresses relationship). **Do NOT** populate
  hint_/mkto_/ai_/sf_ — those are connector-owned; leave them for downstream enrichment.
- **Email capture is the differentiator** — it closes a gap that has existed since the 2020 build.
- **Forecast/IQMS:** the chatbot touches **Leads only**, which sit entirely outside the forecast machinery
  (forecast rolls up Order History LIs + Opportunity RLIs on Accounts). No forecast wiring needed. But a
  converted chatbot Account must eventually get an **IQMS Ship-To / Customer #** to enter the forecast.
- **Routing:** no territory model exists; assign to a **named rep** (Bill Galla per MVP), not territory rules.
- **The 4-hour SLA is NET-NEW** — the original build specifies no response-time SLA. Position it as an
  improvement we are adding, not something the build called for.

## Durable facts (for memory)
W-Systems 2020 build; IQMS ERP daily sync; custom Order-History modules; simple 3-value forecast rolled up by
rep; two View-All roles (-> Global team, no privacy); leads manual-by-design + Web-to-Lead never built; the
automated capture + enrichment stack (Hint/Marketo/Salesfusion/native-AI) is all post-build and partly broken;
Sugar 9.3 (2020) -> 25.2 (2026); no SLA in original design.
