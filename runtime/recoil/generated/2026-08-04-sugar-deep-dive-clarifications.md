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
