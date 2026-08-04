# PRL SugarCRM — Deep-Dive Scope (turnkey for when sandbox + API land)
_2026-08-04 · 🔒 INTERNAL — contains client live-data observations. Never Drive/emailed/hosted._
_Scoped from Zach's screenshots of the live Sugar. This is the agenda for the CRM Data Reality dive._

**Why now:** we can't query yet (sandbox/API pending), but the screenshots reveal exactly which
objects and fields to drill. Scoping it now turns the wait into prepared time, and this becomes the
running sheet for the CRM Data Reality session (de-risked-plan §1.2 / punchlist B2a).

**Access gate:** SugarCRM sandbox + API (read). Zapier MCP already exposes SugarCRMCLIAPI (read-only
used to date). A read pull of the objects below is the whole dive.

---

## Objects + drill-downs (each grounded in a screenshot observation)

### 1. Opportunities (attribution spine)
Observed: "Total Revenue Digital" $12.7M stacked by Lead Source (Web Site, AdWord, Other, Lead
Forensics, Email) x stage (Closed Won / Lost / In Progress). "Won Revenue Digital" $959k = AdWord
$645k + Other $315k. "Booked Revenue" $1.44M. A live "Closed Won with No Lead Source" report exists.
Drill:
- **Won-rate + avg deal size by lead source** (Web Site is biggest won at $1.16M; the chatbot sits on
  Web Site, so it amplifies the already-best channel).
- **Lead Forensics: pipeline vs closed-won** — HYPOTHESIS: high pipeline ($913k), low/zero won.
  If confirmed = the $15K-service displacement case in their own numbers. Verify, do not assert.
- **The $26.5M no-source backfill** — quantify, and see if any is recoverable via account/date joins.
- **"Digital" vs total** — is $12.7M a digital subset? Get the full opportunity revenue picture.

### 2. Product Catalog (1.3 recognition ground truth)
Observed: 624 products, 32 pages, foldered by family (ABS/PBT, ASA, NY, PC, PC/ABS, PC/ASA, PC/TP,
PEI, PPX, TP, OTHER). Grade-code names (PCFR4, ASAG20, ABS-FR-AMB...), Color, Category, Availability.
Drill:
- **Pull all 624 grade codes + family + color + availability** → the recognition dictionary for 1.3.
  Confirms 1.3 data lives in-CRM (like the 231 competitor opps); Todd's PDF becomes a supplement.

### 3. Accounts (1.4 persona + territory)
Observed: custom fields **Resins Used, Competitors, OEM Profile, Focus Five, NDA, Type (Captive)**;
Billing State incl. **Canada (ON, QC)**; assigned rep (Pat McAllister). 21+ accounts.
Drill:
- **Persona signal** — OEM Profile + Type (Captive/...) = the moulder-vs-OEM split for 1.4B.
- **Competitors field** — competitor-intelligence layer for 1.3 recognition.
- **Territory** — routing + state-normalize must handle **provinces**, not just US states.
- **Focus Five** — likely a priority-account flag; confirm meaning, may drive lead prioritization.

### 4. Quotes (demand + conversion)
Observed: 21+, named by grade code (PC/ABS-FR2, PPX-FR3-7001, PC-UT1-7001...), stage Draft/Approved,
mostly $0 grand total (drafts), one $25,500.
Drill: **quote → win conversion**, most-quoted grades (demand signal for recognition + SEM), why so
many $0 drafts (data-hygiene or process).

### 5. Position Data / Sales Numbers (realized revenue + time-to-value)
Observed (World Magnetics): Volume/Revenue Last Year vs Shipped, with variance (e.g. -64% revenue
variance); monthly Total Sales (10 records); Revenue by Product Category.
Drill:
- **Realized-revenue** (shipped + collected) — the lagging-clock data for honest attribution.
- **At-risk / declining accounts** (World Magnetics -64% YoY) — a churn signal PRL may not be watching;
  possible net-new value surface (not scoped, just noted).
- **Time-to-value** — order-to-ship cadence sets the attribution lag.

### 6. Leads (already audited — confirm holds)
Prior audit: 6 required fields, 95% no email, lead_source picklist has no "Chatbot", team "Global".
Drill: re-confirm against sandbox; validate location_c abbreviation-vs-full-name against a real record.

---

## What this changes in the current plan (immediate)
- **1.3 is further de-risked** — recognition data (Product Catalog 624 + Competitors field + 231 opps)
  is almost entirely in-CRM; Todd's PDF is a supplement, not the spine.
- **The $15K displacement gets a data test** — Lead Forensics pipeline-vs-won is the exact query.
- **1.4 persona logic has CRM signal** — OEM Profile / Type / Focus Five fields.
- **Routing/state-normalize must handle Canadian provinces** (ON, QC).
- **Realized-revenue + time-to-value** have a home (Position Data / Sales Numbers).

## Handling
🔒 All of the above is client live-data. Stays git/machine-local. Never in the Drive KB, never emailed,
never shown beyond in-person. The Todd-safe KB keeps only the high-level "$26.5M no source" framing.
