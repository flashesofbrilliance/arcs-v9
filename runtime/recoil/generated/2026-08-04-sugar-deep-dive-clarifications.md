# SugarCRM deep-dive: running clarifications

**Source:** 100 live Lead records pulled via Zapier MCP (`sugarai_new_record`, module=Leads),
2026-08-03. Analyzed 2026-08-04. This is a living list: findings from the data that raise a
question before they justify a conclusion. Each has a way to test it rather than assume.

**Read-once caveat:** this is a 100-record snapshot, and 92 of those were bulk-imported (see C1),
so treat every rate below as directional, not settled, until confirmed on real web-era leads.

---

## C1. 92% of the sample is a bulk import, not organic web capture  [highest priority]
- **Data:** `created_by` = "Importer Importer" on 92/100; "Rachel Pomposi" on 8/100.
- **Why it matters:** the email rate, after-hours rate, and day-of-week pattern all describe an
  imported list, not how website visitors actually behave. We may have been reading a migration.
- **Clarify with Todd/SM:** what is the "Importer" batch, a purchased list, a migration from an
  old system, trade-show scans? When was it loaded? Is it representative of inbound?
- **Test:** re-pull filtered to `created_by != Importer` (or `lead_source = Web Site`) and
  recompute the baselines on the ~8 genuinely-web leads. That is the real denominator.

## C2. Only 5/100 carry a real email (confirmed), but which 5?
- **Data:** `email1` / `email` / `webtolead_email1` each populated on exactly 5/100.
- **Why it matters:** the "chatbot gives every lead an email" value prop hinges on web leads
  NOT already having one. If the 5 with email are the 8 web-source leads, the gap is smaller
  than pitched; if the 5 are random imports, the web channel captures ~zero email and the pitch
  is even stronger.
- **Test:** crosstab email-present against `lead_source`/`created_by` on a clean pull. This is a
  10-minute query and it either strengthens or weakens the headline.

## C3. California is tied for #1 in volume but has NO direct rep
- **Data:** CA = 12 leads (tied with TX). In the territory map CA is a "Distribution" state,
  no direct rep, Nicole secondary.
- **Why it matters:** the second-highest-demand state routes to a channel, not a person. That is
  a coverage question hiding in the routing config.
- **Clarify with Todd:** are CA (and the other 11 distribution states) leads under-served today,
  or is distribution deliberate there? It decides where the chatbot routes that volume.

## C4. Demand mix ranks the database build order
- **Data (description text):** ABS mentioned 24x, polycarbonate 20x, Lexan 8x (top competitor),
  PC blends 7x, SABIC 4x, nylon 4x, PBT 3x, Valox/Noryl/Makrolon 2x each, Ultem 1x.
- **Why it matters:** when we build the searchable material database (1.4), this is the priority
  order. PC and ABS first covers the bulk of real questions; Lexan is the competitor to map first.
- **Test:** confirm against a clean web-lead pull; the import may skew the mix.

## C5. Repeat companies suggest existing accounts use the web form
- **Data:** Hunter Industries, IMI Norgren, NC Customs each appear 2x.
- **Why it matters:** if existing customers are re-entering through the lead form, some "leads"
  are actually reorders or account activity, which inflates lead counts and muddies conversion math.
- **Clarify with SM:** should the bot detect a known company / existing account and route
  differently (to the account owner) rather than as a net-new lead?

## C6. International demand does not show up here
- **Data:** 1 international lead (Mexico) in 100, despite Todd citing China, Vietnam, Malaysia as
  real markets.
- **Why it matters:** international business is captured somewhere other than this web channel
  (reps, distributors). The chatbot as scoped will not touch it, which is fine, but worth naming
  so nobody expects it to.

## C7. Rich vs thin inquiries split the intent signal
- **Data:** description median 78 chars; 29/100 are one-liners (<40 chars), 21/100 are rich
  (>200 chars, up to ~2,000).
- **Why it matters:** the rich ones are real spec conversations; the one-liners are low-signal.
  The chatbot's branch logic should aim to convert thin inquiries into rich ones by asking the
  right two or three questions.
- **Smoke test:** measure description richness on chatbot-sourced leads vs the historical
  baseline once live. If the bot lifts median description length, that is a clean, provable win.

---

## Hypotheses worth a smoke-screen feature or eval
- **H1 (email lift):** chatbot leads will carry an email ~100% vs the ~5% baseline. Provable in
  the first 30 real leads. This is the north-star leading indicator.
- **H2 (richness lift):** chatbot leads will have longer, more structured descriptions than the
  web-form baseline. Measurable, and it argues the bot qualifies better than a form.
- **H3 (coverage gap):** a real share of leads come from distribution-only states. If confirmed,
  a "no direct rep" routing rule is needed before auto-routing, not after.
- **H4 (known-account detection):** a non-trivial share of inbound is existing customers. A
  smoke feature: bot asks "have you ordered from us before?" and tags accordingly, to test how
  many self-identify as returning.

## What this deep dive canNOT tell us (needs a cleaner pull or Todd)
- True web-era conversion, because the sample is mostly imported.
- Closed-won vs closed-lost (all 100 are status "New"), so ICP still cannot be derived from data.
- Anything about the ERP (IQMS); Sugar is downstream of it.

---

# Addendum — Opportunity + Order-History reports (reviewed 2026-08-04)

Screenshots of the live SugarCRM reports (Opportunities, Order History, competitor-grade
report, lead-source dashboards) substantially update the picture. These are the real sales
substance, not the 100-lead Leads snapshot. What changed:

## R1. The competitor cross-reference ALREADY EXISTS in Sugar, structured  [reverses a prior claim]
- **Data:** report "Oppty's with Competitor Grade" = **231 opportunities** each carrying a named
  competitor grade mapped to a PRL grade: 357U, FR3010, PC-10FR, Cycolac FR-15, LG AF312A,
  AF366, TRISTAR PC-10GFR, RTP 2099, LG ABSFR, MG47/GPM5500, etc.
- **Why it reverses R-earlier:** I told Todd the "what's your equivalent to Lexan 141" data was
  trapped as images in the Product Selection Guide PDF. The COMMERCIAL cross-reference (competitor
  grade to PRL grade) is already machine-readable in the CRM. The spec datasheets are still in
  PDF, but the lookup the chatbot most needs is structured data we can ground on today.
- **Action:** reframe the "comparison tables are pictures" agenda item. The PDF is still the
  barrier for detailed spec Q&A, but a "we make an equivalent to X" answer can be grounded on
  these 231 records now. This is a stronger, more concrete build story.

## R2. $26.56M in closed-won revenue has NO lead source  [the real pain]
- **Data:** report "Opportunities - Closed Won with No Lead Source" = $26.56M, all "Undefined".
- **Why it matters:** this is the attribution black hole. They cannot tell what marketing
  actually produces revenue. The chatbot tagging every lead with a source (the C3/labeling
  decision) is not housekeeping, it directly attacks a $26.56M blind spot. This is the number
  worth showing his team, alongside the four-hour callback metric.

## R3. Web-source leads DO carry email  [softens the "5% have email" headline]
- **Data:** lead "Art Browning" (Fab Tex Innovations) is lead_source = Web Site and has
  art@fabtexinnovations.com. The lead-source dashboard also shows an "Email" source and real
  web/AdWord pipeline.
- **Why it matters:** the "5 of 100 have email" figure was dragged down by the 92 imports. Real
  web leads already capture email through the form. **Do not lead with "the site captures almost
  no email" in front of Todd** — he can open his own CRM and see web leads with emails, and it
  costs credibility. Reposition the chatbot value from "captures an email" to "captures
  qualification depth (resin + application + competitor grade) AND a clean source tag" — which is
  both true and more valuable given R1 and R2.

## R4. AdWord is the best-converting paid source  [validates the SEM onramps]
- **Data:** lead-source dashboard — Won revenue by source: AdWord $645k, Other $315k; Web Site
  $6M total pipeline but $3.08M of it Closed Lost; Email only $68k total. "Lead Forensics" (a
  paid website visitor de-anonymization tool) is also a source at $913k.
- **Why it matters:** the 5 competitor SEM onramps (SABIC/Lexan/Ultem/Noryl/Valox) point exactly
  at the traffic that already converts best. That is a data-backed reason to turn them on, not a
  nice-to-have. Also: they already pay for Lead Forensics, so "de-anonymize + qualify the visitor"
  is a concept Todd already buys into.

## R5. Scale + margin context (for pricing the retainer)
- **Data:** $86.5M shipped since Jan 2025 (32.9M lbs); $8.07M in opportunities created in the
  LAST 30 DAYS; $10.25M open pipeline next 90 days; 39,504 order-history line items; a sample
  order shows ~40% gross margin (unit $4.98 / cost $2.97). Open pipeline product mix: PC dominant,
  then PC/ABS, TP, PPX, ABS.
- **Why it matters:** this is a serious, high-margin business, not a small shop. It supports
  pricing the engagement against pipeline impact, not against hours. One recovered lost deal
  covers a year of retainer many times over.

## Corrections to the earlier list
- **C2 (which 5 have email):** answered. Web leads carry email; the 5/100 was an import artifact.
  Retire the "site captures no email" framing.
- **C4 (demand mix):** confirmed and extended — open-opportunity mix is PC-dominant, then PC/ABS,
  TP, PPX, ABS. Build PC + PC/ABS cross-refs first.
