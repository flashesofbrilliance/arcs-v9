# Gravity Forms orphaned-lead analysis (value reveal)
_2026-08-07 · Read-only analysis of the site's main lead form ("Material Alternative", 3,126 entries) matched
against SugarCRM (Leads + Contacts). Business-level intelligence only; personal names/emails are NOT in this
file (they live in the GF export Todd owns, handed over directly, never committed)._

## Headline
- The site's main lead form is **96% spam** (2,990 of 3,126 entries) — it has **no spam protection at all**
  (Eric-Jones bot spam, XRumer signatures, etc.). The spam **buries every real lead**.
- Under the spam: **~36 genuine, high-intent purchase/quote inquiries** (Dec 2022 → May 2026).
- Matched against Sugar: **only 2 of 38 unique real leads are in the CRM. 36 are ORPHANED** — captured by the
  form, never delivered, never worked. (The GF→Zapier delivery is off; a rep manually entered the 2 that made
  it.)

## What was left on the table (orphaned, recoverable — company · intent · date)
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

## Recommendation 1 — spam/noise protection for the forms (for Todd)
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

## Recommendation 2 — insights for the chatbot (1.1 / 1.2)
The GF data is a free blueprint for the bot:
- **The "which material are you looking for?" free-text field is gold** — it carries grade + competitor intent
  on nearly every real lead. The chatbot must capture the same (its application/grade-interest field) and run
  it through our **recognition layer** (which already maps "alternative to Lexan", "PRL PC-GP2-D", "Valox 325"
  → the right PRL family/grade). This is direct validation of the 1.3 recognition + competitor cross-ref work.
- **Real buyers name specific grades and competitor grades to replace** — exactly the ICP and conquest angle we
  built for. Route those to a specialist (1.3/handoff).
- **Spam protection matters for the bot too** — a qualifying step + email validation (the 1.1 fix we just made)
  keeps junk out of Lyro (cost) and the CRM (quality).
- **The chatbot IS the permanent fix for this whole failure** — capture email every time + reliable delivery
  means no future lead orphans the way these 36 did. Frame 1.1/1.2 to Todd as "this stops the leak."
- **Baseline/attribution:** these 36 orphaned leads are the "before." The bot's measurable value is capturing,
  delivering, and working inquiries that used to vanish.

## Provenance / handling
Source: GF export `material-alternative-2026-08-07.csv` (Todd's data) matched to Sugar via read-only API. No
writes. Full contact details (name/email/phone) stay in the GF export Todd owns; only business-level intent is
recorded here. The other lead forms (Contact Us 708, Apply Now 885) have not yet been analyzed — same method
applies.
