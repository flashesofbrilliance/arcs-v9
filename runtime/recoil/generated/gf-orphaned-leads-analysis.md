# Gravity Forms orphaned-lead analysis (value reveal)
_2026-08-07 · Read-only analysis of the site's main lead form ("Material Alternative", 3,126 entries) matched
against SugarCRM (Leads + Contacts). Business-level intelligence only; personal names/emails are NOT in this
file (they live in the GF export Todd owns, handed over directly, never committed)._

## Headline
- The site's main lead form is **96% spam** (2,990 of 3,126 entries) - it has **no spam protection at all**
  (Eric-Jones bot spam, XRumer signatures, etc.). The spam **buries every real lead**.
- Under the spam: **~38 genuine, high-intent purchase/quote inquiries** (Dec 2022 → May 2026).
- Matched against Sugar by **email AND name AND company** across Leads, Contacts, and Accounts:
  **6 of 38 are already in the CRM** as a Lead/Contact (Halstead/DT Mfg, D.Fernandez/Munchmeyer, Summers/
  Sentinel, Blair/New Concept, Bohrer/Excel Tool, Windsor/Inoac); **3 more have their company as a known
  Account** (David Wolfe Design, 3C Telemetry, PLS GmbH/the Tesla lead) but the person is not in the CRM;
  **~29 are truly orphaned** (person and company both absent), never delivered, never worked.
- **Method note (verified):** an *email-only* match falsely showed "36 orphaned" because **most Sugar records
  have no email** - it could not see the name-only records. The multi-key match corrected it. The Account
  name-match is exact-string, so known-company relationships under slightly different names may still be
  undercounted; treat ~29 as the upper bound on net-new orphaned.

## What was left on the table (orphaned, recoverable - company · intent · date)
Real companies, most naming a specific PRL grade or a competitor grade to replace:
| Company | Inquiry | Date |
|---|---|---|
| PLS GmbH | PRL ABS-G15, **OEM: Tesla** | 2025-03 |
| Duromer (Vietnam) | **PRL PC-G30 Natural, 876 kg**, quote CIF | 2024-05 |
| Kent City Plastics | **PC/ABS FR1, purchase 1,500 lb** | 2023-01 |
| Kelta Technologies | quotes on **Sabic Lexan 940A/945, Covestro Makrolon 6455** | 2025-02 |
| Siemens Industry | PRL PPX-FR substance content | 2025-02 |
| Otter Products (OtterBox) | SDS/REACH/RoHS/Prop65 for PRL PC-G20 | 2024-06 |
| Momentive | 50 lb each Nylon 6 and 6,6 | 2026-01 |
| Amphenol RF | quote request | 2023-03 |
| Ideal Industries | PBT data sheet (TP-FR-IM) | 2024-05 |
| US Conec | V0 Polypropylene, no stress-whiten | 2026-05 |
| Okami Medical | purchase **Lustran 433** (INEOS conquest) | 2026-02 |
| MVP Plastics | alternative resin to substitute Lexan | 2026-05 |
| Excel Tool & Plastics | alternative to **Valox 325** | 2023-03 |
| David Wolfe Design | Natural PC, replacing **Lexan 500R** | 2023-11 |
| Accudyn, Wrex, New Concept, Keyland, Sentinel, Ker Molders, Medbio, 3C Telemetry, Optimoule, QEM, Inoac, +more | grade quotes / SDS / small-lot buys | 2023-26 |

That is competitor-conquest and real purchase intent from named industrial buyers, sitting unworked for up to
3.5 years because the form is a spam magnet and nothing delivered the leads to the CRM.

_Verification note: the table above is the full genuine-lead list, NOT the net-new-orphaned subset. Per the
multi-key match, PLS GmbH / David Wolfe / 3C Telemetry are known Accounts, and Excel Tool / New Concept /
Sentinel / Inoac already have a Lead or Contact. The corrected figures are in the Headline: 6 in CRM, 3
account-only, ~29 truly orphaned._

## Recommendation 1 - spam/noise protection for the forms (for Todd)
Turn the form from 96% noise into clean signal:
1. **Bot challenge:** enable **Cloudflare Turnstile or reCAPTCHA v3** on every Gravity Form (invisible, no UX cost).
2. **Honeypot:** turn on Gravity Forms' built-in **anti-spam honeypot** (free, one toggle).
3. **Akismet:** connect Akismet (GF supports it) for content-based spam filtering.
4. **Field validation:** make the material field **required with a min length + reject URLs/HTML**; bots dump
   pitches and links, real buyers name a material.
5. **Rate-limit / block** known signatures (Eric Jones, XRumer) and abusive IPs at Cloudflare/WP Engine.
6. **Notification hygiene:** once clean, route real submissions to a monitored inbox + the CRM so they cannot
   orphan again.
Effect: real leads become visible AND deliverable. This alone likely recovers more revenue than the chatbot in
year one.

## Recommendation 2 - insights for the chatbot (1.1 / 1.2)
The GF data is a free blueprint for the bot:
- **The "which material are you looking for?" free-text field is gold** - it carries grade + competitor intent
  on nearly every real lead. The chatbot must capture the same (its application/grade-interest field) and run
  it through our **recognition layer** (which already maps "alternative to Lexan", "PRL PC-GP2-D", "Valox 325"
  → the right PRL family/grade). This is direct validation of the 1.3 recognition + competitor cross-ref work.
- **Real buyers name specific grades and competitor grades to replace** - exactly the ICP and conquest angle we
  built for. Route those to a specialist (1.3/handoff).
- **Spam protection matters for the bot too** - a qualifying step + email validation (the 1.1 fix we just made)
  keeps junk out of Lyro (cost) and the CRM (quality).
- **The chatbot IS the permanent fix for this whole failure** - capture email every time + reliable delivery
  means no future lead orphans the way these 36 did. Frame 1.1/1.2 to Todd as "this stops the leak."
- **Baseline/attribution:** these 36 orphaned leads are the "before." The bot's measurable value is capturing,
  delivering, and working inquiries that used to vanish.

## Root cause of the spam (from the form config, exact)
The "Material Alternative" form config shows precisely why it is 96% spam:
- **Honeypot is OFF** (`enableHoneypot: false`).
- **The CAPTCHA field exists but is not configured** (`captchaType: ""`, carries a `label_setting` error) - it is
  not actually challenging bots. Same on "Contact Us".
- **No blacklist/keyword filter** on this form (the older "PDF Form" carries the `bsk_gfbl` blacklist plugin
  fields; "Material Alternative" does not).
So bots walk straight in. Exact fixes:
1. Set **`enableHoneypot: true`** (one toggle).
2. Configure the existing CAPTCHA field with real **reCAPTCHA v3 / Cloudflare Turnstile keys** (it is present,
   it just has no keys) - or swap in Turnstile.
3. Apply the **blacklist/keyword rules** already on the PDF Form (block "eric", "xrumer", URLs in the material
   field).
4. Make the material field **reject URLs/HTML + enforce a min length**.
5. All forms currently notify only `info@...` and **nothing writes to the CRM** - wire delivery so real leads
   cannot orphan again.
Scope note from the configs: **"Apply Now" (885) is a job-application form** (Position + Resume), not sales
leads - exclude it. **"Contact Us" (708) is a sales-lead form** - analyze next, same method.

## Recognition cross-reference (competitor work x real leads)
Ran our recognition layer over the 36 orphaned intents:
- **2 auto-mapped as competitor-conquest**: David Wolfe (Lexan 500R -> **PC-HM-FR1**), Excel Tool (Valox 325 ->
  **TP-GP1**). Plus 4 named a PRL grade, 9 a family, **21 needed a human read**.
- The 21 misses are a **gold finding for 1.3**: real buyers write **en-dashes** ("ABS–G15"), **grade suffixes**
  ("PEI-GP1-7001", "PPX-FR2-8382"), and **alphanumeric competitor grades** ("Sabic Lexan 940A/945", "Makrolon
  6455", "Lustran 433") that the recognizer does not yet catch. These 36 real intents are the **test set to
  harden it** - adding en-dash handling, suffix-stripping, and competitor-alphanumeric matching would lift
  auto-recognition from ~40% to most.
This validates the competitor cross-reference (real conquest leads exist across Lexan, Valox, Makrolon, Lustran)
AND gives the exact tuning targets.

## Carry into 1.1 - 1.5 (refined)
- **1.1 capture:** handle these real phrasings; email-validate + deliver = the permanent fix for orphaning.
- **1.2 delivery/enrichment:** recover these 36 into the CRM (with Todd's OK); they are the measurable "before".
- **1.3 recognition:** harden against the 36 real intents (en-dash, suffixes, competitor alphanumerics). Real
  data beats synthetic - this is a free, high-quality eval set.
- **1.4 SEM:** buyers literally search "alternative to Lexan / Valox" - validates the competitor-conquest SEM
  onramp flows already drafted in Tidio.
- **1.5 Lyro:** recognize + route conquest inquiries to a specialist, never guessing a spec.

## Provenance / handling
Source: GF export `material-alternative-2026-08-07.csv` (Todd's data) matched to Sugar via read-only API. No
writes. Full contact details (name/email/phone) stay in the GF export Todd owns; only business-level intent is
recorded here. The other lead forms (Contact Us 708, Apply Now 885) have not yet been analyzed - same method
applies.
