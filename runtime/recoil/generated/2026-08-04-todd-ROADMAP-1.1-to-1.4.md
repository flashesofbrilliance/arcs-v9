# PRL Resins Chatbot — ROADMAP 1.1 → 1.4
_2026-08-04 · canonical roadmap. Absorbs and re-slots the earlier 1.1–1.5 asset-map._
_Supporting detail: `2026-08-04-todd-phase-map-1.1-to-1.5.md` (acceptance-criteria table) +_
_`2026-08-04-todd-punchlist-people-process-tools.md` (people/process/tools confirmations)._

**Re-slotting note:** the knowledge/recognition work (resin alternatives, tacit knowledge outside
Good/Better/Best) is now **1.3**. The SEM onramp and the persona-conditional AI logic merge into
**1.4**. Delivery + enrichment + the 4-hour metric consolidate into **1.2**. No separate 1.5.

Standing constraints: additive not replacement · run in parallel not on top · baseline first · no
em-dashes in Todd-facing copy · Lyro stays OFF until its handoff-to-Sugar path is verified.

---

## 1.1 — GO LIVE (outstanding JTBD + client sign-offs)

**Final JTBD:** When a qualified visitor lands on the PRL site or a paid lander, capture a clean,
correctly-routed lead into SugarCRM within seconds, so a rep can follow up inside the four-hour
window, without asking any rep to touch new tooling.

**Still outstanding on the JTBD itself:**
- Sugar required-field mapping proven end to end (6 fields, name-split, phone, company fallback,
  lead_source, state normalize). See the acceptance table in the phase-map doc.
- `location_c` abbreviation-vs-full-name verified against one real live record.
- Notification path moved onto Mailgun (retires the `info@prlresins.com` DNS block).
- Lyro confirmed OFF for 1.1 (no AI lead-loss path).

**Client sign-offs required before internal testing (these are Todd/SM decisions, not build work):**
1. **Phone:** required in the bot, or a written placeholder so the record always creates.
2. **Lead source:** add a "Chatbot" picklist value, or ride "Web Site."
3. **Test lead:** approve ONE labelled test lead, or stand up a sandbox (all records live on team
   "Global," so a test lead cannot be hidden).
4. **Go-live sequence:** the team hears the message BEFORE the first live lead lands, and Todd/SM
   confirms who delivers it.
5. **First friendly user:** name the one cooperative person (likely SM) who validates before wider
   exposure.

**Currently parked on (external):** SugarCRM **sandbox access** (awaiting). This gates the test
lead, the field mapping proof, and the CRM Data Reality session.

**Definition of done for 1.1:** a test conversation down every branch produces a Sugar lead a rep
would accept as real, the notification arrives within seconds, and nothing on the plant floor or in
any rep's daily tooling has changed.

---

## 1.2 — DELIVERY, ENRICHMENT + THE METRIC (config / tools / dependencies / DoD)

**What this phase is:** the tooling that makes the 1.1 JTBD reliable and measurable, not just
demonstrable once.

**Config / tools:**
- **Tidio flow-level webhook** → Zapier **Catch Hook** (works on the current Flows plan; not
  plan-gated). [corrects the stale Jul-30 "blocked on upgrade"]
- **Zapier Create-Lead** step: the full field transform (name-split with single-word fallback,
  phone handling, company fallback, lead_source, state normalize), copied from the live
  Unbounce→Sugar mapping.
- **Mailgun**: instant notification to the rep + instant autoresponder to the prospect (the
  autoresponder is itself a partial answer to the four-hour gap, since the prospect hears back at
  once even if the rep is slow). Authenticated sending domain, no dependence on PRL IT/DNS.
- **ZoomInfo**: enrich each lead (verified business email + firmographics), which fixes the
  95%-of-Sugar-leads-have-no-email finding and sharpens routing/qualification.
- **The 4-hour metric**: stamp arrival (bot writes `date_entered`) and time-to-first-touch.

**Other dependencies (the ones that will actually gate this):**
- **SugarCRM sandbox** (awaiting) — to safely test Create-Lead and enrichment writes.
- **Tidio support account review** (awaiting email) — confirms webhook tier + seats.
- **ZoomInfo + Mailgun** account access/seats and a sending subdomain that does not touch live mail.
- **CRM DATA REALITY session (the long pole).** The metric assumes Sugar captures the *fielding*
  event. It may not. One working session with SM + the reports owner to establish: what timestamps
  exist today; whether historical deals carry BOTH a response-time signal AND an outcome (so the
  **response-time vs win-rate retro-analysis** is possible, the single strongest artifact for
  Todd's owner, built from data PRL already owns); what lives outside the CRM; and the verbal/phone
  touchpoints (calls to the plant, sample requests) that never become CRM data.
  **Guardrail:** if first-touch is not captured, do NOT fix it by asking reps to log calls (that is
  the turf-stepping we avoid). Use an auto-capturable proxy (status change New→Working, a logged
  email) or measure less.

**Definition of done for 1.2:**
- A real test lead lands in Sugar with all required fields AND an enriched business email.
- Rep notification + prospect autoresponder both fire within seconds.
- Time-to-first-touch is recorded via an automatic signal (or the proxy is explicitly chosen and
  documented).
- A baseline exists (volume, close rate, deal size by region and source) so net-new is provable.

---

## 1.3 — KNOWLEDGE + RECOGNITION LAYER (need-to-haves / sources / edge cases / tacit knowledge)

**What this phase is:** teaching the bot to recognize what a real buying signal looks like in
resin terms, and to route on it, without ever pretending to be an engineer.

**Critical need-to-haves:**
- **Machine-readable competitor/resin cross-reference DB from Todd** (the request already made).
  This is the deterministic **ground truth**: competitor grade → PRL equivalent → family. Ask for a
  defined shape, not "the data," so it lands usable in one pass.
- **The resin nomenclature grammar** (family + modifier + color-series + suffix, e.g.
  `PC-FRUV2-7001-1`) so the bot parses a grade code, not just a family name.
- **A deterministic eval harness** that grades Lyro (non-deterministic) against the ground-truth
  table: recognition, mapping, and the guardrail negatives (Lyro must REFUSE to confirm a spec,
  cert, flame rating, or price, and hand off). Proves correctness before go-live, not live.

**Source references to consider:**
- Product Selection Guide 2025 (competitor cross-ref tables are page-IMAGES today → OCR risk; the
  machine-readable DB retires it).
- The Good/Better/Best Engineering Thermoplastics Material Selection Matrix (the *formal* recommender
  spine for Branch B).
- QATF001 New Opportunity Form (the SM's own intake fields → what "qualified" means to them).
- Public product/markets/quality pages on prlresins.com (safe Lyro knowledge sources).
- Known competitor grade families: Lexan, Makrolon, Ultem, Noryl, Lustran, Valox, Zytel.

**Edge cases to account for:**
- Competitor grade **not in the guide** → do not guess; capture and hand off.
- A resin PRL **does not make** → out of scope; route to a human, never hallucinate an equivalent.
- **Ambiguous or misspelled grade codes**, and **blends** that map to more than one family.
- A **spec / cert / flame-rating / regulatory** question → hard refuse + hand off (safety line).
- An **application where multiple families fit** → offer the choice, do not pick for them.
- Someone naming an **internal PRL grade** vs a competitor grade (different handling).
- **Non-buyers**: students, researchers, distributors, or a competitor fishing → low-value tag,
  never blocked, but not routed as a hot lead.

**Working knowledge that is NOT in the Good/Better/Best framework (the tacit layer):**
The formal matrix is what is written down. Reps carry a second, unwritten map: the substitution a
senior rep reaches for when the ideal grade is out of stock, on a long lead time, or priced wrong;
grades that technically fit an application but never made the Good/Better/Best table; customer- or
region-specific preferences. Lyro can only route on what is encoded, so this has to be **elicited**
(a short interview with the SM or one senior rep) and captured as an extension of the ground-truth
DB.
- **Change-management framing (critical):** eliciting this is asking a rep to externalize their
  expertise. Frame it as "help the bot hand you better-qualified leads," never "give us your
  knowledge." Capture the *routing signal* (this input → hand to a specialist), not the rep's
  secret sauce. This is the seam where the replacement fear lives; handle it as trust, not data.

**Definition of done for 1.3:** the eval passes (recognition + mapping + guardrail refusals) against
the ground-truth DB, the tacit substitution map is captured as routing rules, and no path exists
where the bot states a spec/cert/price as fact.

---

## 1.4 — SEM ONRAMP + PERSONA-CONDITIONAL AI LOGIC (two parts)

### Part A — Landing-page updates driven by Google Search Console + Google Ads
**Goal:** the paid and organic demand that is already arriving converts on the page it lands on,
with a chatbot onramp tuned to why the visitor came.
- Pull **Google Search Console** (queries, impressions, clicks, position) and **Google Ads**
  (worst-performing terms and landers) to find where intent is arriving but not converting.
- For the underperformers, decide the **landing-page update** AND, specifically, **what the Tidio
  onramp looks like on that page**: the bot opens pre-scoped to the campaign. A "Sabic alternatives"
  lander opens the bot already framed around "looking for a Sabic equivalent," not a cold greeting.
- Wire each lander flow to the **existing Unbounce→Sugar zaps** (Sugar is already connected there).
- **New asset used:** Unbounce (edit landers + own the flow/zap wiring end to end).
- **Interpretation flag:** I read "google console / ad worst" as Search Console + Google Ads worst
  performers. Confirm if you meant something narrower.

### Part B — Conditional info by persona + AI improvisational logic
**Goal:** show each visitor only what is relevant to their job, and let the AI improvise within hard
limits.

**The two primary personas (different jobs, different questions):**
| | **Injection moulder** (processor) | **OEM** (designer / engineer) |
|---|---|---|
| Cares about | processability, drying, shrink, cycle time, price/lb, availability, MOQ | end-use performance, specs, certifications, approvals, the part's requirements |
| The bot should surface | commercial + processing info, sample/quote path | performance + qualification info, specialist match |
| The bot should NOT lead with | deep spec/cert detail | price/MOQ/processing minutiae |

**Conditional restriction logic:**
- **Infer persona** from the flow the visitor enters (which lander, which button, what they type),
  not by asking "are you a moulder or an OEM" cold.
- **Restrict/surface accordingly:** a moulder is not buried in cert tables; an OEM is not led with
  price-per-pound. Same engine, different disclosure.
- **AI conditional improvisation** = rigid where speed wins ("I know what I need," "call me"), AI
  where judgment wins ("Help me choose," "Something else"), persona-gated content in the middle, and
  the same hard guardrails throughout (never confirm spec/cert/price, hand off).

**Edge cases:** a visitor who is **both** moulder and OEM, or **neither** (distributor, student,
competitor); a persona signal that conflicts mid-conversation (started as moulder, asks an OEM
question); low-value personas that should be captured softly, never blocked.

**Definition of done for 1.4:** SEM landers open a campaign-matched onramp wired to Sugar; the bot
demonstrably surfaces moulder-relevant vs OEM-relevant info based on the entry flow; the persona
inference and the guardrail refusals both pass an eval extension of 1.3's harness.

---

## Cross-cutting (true for every phase)
- **Attribution wedge:** tag every lead with source + region from day one, so net-new attributable
  revenue is provable by channel and region. SM-only visibility first; healthy internal competition
  only once the numbers are friendly (Todd's call).
- **The $15K lead-gen displacement (budget + benchmark).** The sales team pre-paid ~$15K/yr for a
  lead-gen service they are cutting at year-end. Two consequences: (1) that spend can reallocate to
  tech (landing-page redesign, chatbot rollout, a revamped SEM strategy with an account/campaign
  management skill agent), which enlarges the 1.4+ envelope; and (2) it is the **natural benchmark**
  for the attribution wedge. The chatbot channel's net-new revenue measured against that $15K is a
  clean displacement ROI ("we replaced a $15K line and out-produced it"), which is the strongest
  framing for the owner and the cleanest justification for reallocating the budget. Do not overclaim
  it before the baseline exists; capture the $15K as the number to beat in the CRM Data Reality
  session. Opens a Phase-1.4/Phase-2 lane: **SEM + account/campaign management as an ongoing agent**,
  not a one-time lander refresh.
- **The people:** blue-collar plant floor is untouched in all of 1.x (say so plainly); white-collar
  reps get better-qualified leads in the tool they already use, never a new tool or a surveillance
  vibe.
- **External gates parked as of 2026-08-04:** SugarCRM sandbox, Tidio account-review email, the
  machine-readable competitor DB. Parallel work that does not need them: the CRM Data Reality
  agenda, the competitor-DB schema (doubles as the ask to Todd), and the eval harness scaffold.
