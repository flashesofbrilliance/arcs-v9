# PRL Resins Chatbot — Punchlist: People, Process, Tools
_2026-08-04 · outstanding questions, confirmations and clarifications before go-live_
_Organized across five lenses: Technical · Business · Operational · Tactical · Logistics_

This is the list of things we need to confirm on your side before the chatbot starts sending real
leads. It is written so you can forward pieces of it straight to the friendly people who can answer.
The harder conversations (the reps and the plant floor) are handled separately, in the change
section below, because those are about trust, not answers.

---

## The frame (read first)

Three rules shape everything on this list:

1. **This is additive, not a replacement.** The bot catches leads that are being lost today in the
   gap between someone landing on the site and a rep calling them back. It feeds the reps. It does
   not take anything away from them.
2. **We run it in parallel, not on top.** The chatbot is its own channel, measured on its own. We do
   not reassign anyone's existing pipeline, we do not interrupt how a rep works today. Nobody wakes
   up to find their process changed underneath them.
3. **Baseline first, then prove it.** Before we go live we capture what today looks like, so that
   every dollar the chatbot brings in is visibly net-new and attributable, not a claim on revenue
   that was already coming.

---

## The people (change management, handled with care)

The mix here is roughly four to six white-collar execs, several of them old-school, plus a larger
group of blue-collar plant and factory workers. The risk is not technical. It is the fear of being
automated, replaced, or watched.

**Blue-collar plant and factory workers.** Phase 1 does not touch them at all. No tool, no login, no
change to their day. Say this plainly and early, because the loudest fear ("am I next") is easiest to
retire when the honest answer is "this one is not about you." Anything plant-facing later is opt-in
and assistive (a voice note that saves them writing), never surveillance, and never before they ask.

**White-collar execs and reps.** Their fear is loss of control and relevance. The message that works:
the bot does the grunt intake so you spend your time on real selling, and you still own every
relationship. There is no new tool to learn, because the lead lands in SugarCRM where you already
work. Frame it as "we caught one you would have lost," never "the system did your job."

**Who delivers the message, and when.** Confirm: does Todd or the sales manager introduce this to the
team, and does that happen **before** the first live lead lands? The one thing that breaks trust is a
rep getting a lead from a system nobody told them about.

**Pick one friendly first user.** Confirm the single cooperative person (likely the sales manager, or
one rep who is not tech-hostile) who validates the flow before anyone else sees it. Adoption spreads
from a trusted peer saying "this actually helped me," not from a rollout.

---

## The wedge: baseline + attribution (the reason this earns its keep)

This is where the chatbot stops being a cost and becomes a number Todd can take to the owner. It also
happens to be the thing that defuses turf fear, because it proves the bot added revenue rather than
took credit for pipeline that already existed.

**The one session that unlocks all of this — a "CRM Data Reality" conversation.**
Before we can promise the metric or the baseline, we need one working session with the sales manager
and whoever runs the reports, to see what actually lives in the system versus what lives in people's
heads and inboxes. Specifically:
- What **timestamps and flags** exist on a lead today (when it arrived, when it was assigned, when it
  was first worked). We cannot show "fielded within four hours" if that event was never captured.
- Whether historical deals carry **both a response-time signal and an outcome** (closed-won realized
  revenue vs closed-lost). If they do, we can show, from data PRL already owns, whether fast
  follow-up actually closes more. That single chart is the strongest thing we could put in front of
  the owner, and it costs nothing to produce if the data is there.
- What **reports exist today**, and what important information is tracked **outside** the CRM
  (spreadsheets, email, tribal knowledge).
- The **verbal and phone touchpoints that never become CRM data** — calls to the plant, sample
  requests, updates a rep gives out loud. These are real steps in the sales process that are invisible
  today. We only want to map them now, not capture them (capturing them is later, and rep-facing).

**One hard guardrail on the metric:** if there is no captured first-touch, we do **not** fix that by
asking reps to start logging their calls. That is the exact turf-stepping we are avoiding. We measure
with an automatic proxy (a status change, a logged email) or we measure less. A partial number nobody
had to work for beats a perfect number that changes how a rep works.

**Confirmations needed to make this real:**
- **Capture a baseline before go-live.** What does today look like: current lead volume, close rate,
  and average deal size, ideally split by region and by source. Someone (sales manager) needs to pull
  this once. Without it, "net-new" is a claim; with it, it is math. **This falls out of the CRM Data
  Reality session above and is the long pole. Request it early.**
- **Tag every chatbot lead** with its source and region so we can report chatbot vs Unbounce vs
  organic, and region vs region. This needs a clean source field and a region/territory field on the
  Sugar lead (see Technical).
- **Decide the visibility ladder.** Start with sales-manager-only reporting on an established baseline.
  Later, per-region or per-rep numbers can create healthy internal competition, but only once the
  numbers are friendly and Todd is comfortable surfacing them. Confirm he wants to hold that for later,
  not lead with it.

---

## 1. Technical (the plumbing)

| # | Confirmation needed | Who answers | Touches a rep? |
|---|---|---|---|
| T1 | SugarCRM requires six fields on a new lead (company, first name, last name, lead source, state, work phone). Confirm we can populate all six from the bot. | SM / Sugar admin | No |
| T2 | Add a **"Chatbot" lead source** value in Sugar, or ride the existing "Web Site"? | SM / Sugar admin | No |
| T3 | Is there a clean **region or territory field** on the lead record? Attribution by region depends on it. | SM / Sugar admin | No |
| T4 | **ZoomInfo**: confirm access, whether we can enrich a lead (backfill business email + company details), and per-lookup vs bulk. This is the fix for leads landing without an email. | Todd / whoever owns ZoomInfo | No |
| T5 | **Mailgun**: which sending domain or subdomain do we use, so we do not touch the live prlresins.com mail setup. Confirm who owns the Mailgun account. | Todd / IT | No |
| T6 | **GTM go-live switch** is the shared production container, managed by the agency (9rooftops). Confirm they will publish the go-live tag, and the timeline. | Todd / 9rooftops | No |
| T7 | **Unbounce**: which landing pages get their own flow, and confirm we can edit them. | Todd / marketing | No |
| T8 | **Territory map** (which rep covers which states/regions) for geo-routing. Still outstanding. Needed for routing AND region attribution. | SM | Lightly (their coverage) |

## 2. Business (the money and the ownership)

| # | Confirmation needed | Who answers |
|---|---|---|
| B1 | Agree the **attribution model**: a chatbot-attributed lead is one tagged Chatbot, tracked through to closed-won revenue. Who owns that report. | Todd / SM |
| B2 | **Baseline pull** before go-live (volume, close rate, deal size by region and source). | SM |
| B2a | **Schedule the CRM Data Reality session** (SM + reports owner) — unlocks B1, B2 and the whole 1.2 metric. Long pole; book early. | Todd / SM |
| B2b | Does the historical data support the **response-time vs win-rate retro-analysis**? (Only answerable in B2a.) | SM / reports owner |
| B3 | **Account ownership**: PRL should eventually own the Tidio, Zapier, ZoomInfo and Mailgun accounts (transfer, not just admin) for a clean handoff. Confirm intent. | Todd |
| B4 | **Phase 1.x scope and budget envelope** now that Todd is extending. Confirm the shape before we commit build time. | Todd |
| B5 | Is per-region or per-rep reporting politically fine to surface **later**, or sensitive now? (Recommend: SM-only first.) | Todd |

## 3. Operational (the day-to-day process)

| # | Confirmation needed | Who answers | Touches a rep? |
|---|---|---|---|
| O1 | The **four-hour callback** is the number we build around. Is it a real policy today, and who is accountable when a lead sits? | Todd / SM | Yes (their SLA) |
| O2 | Who **works a chatbot lead**: sales manager triages and assigns, or auto-assign by territory? MVP is to the SM. | SM | Yes |
| O3 | Does the SM live in Sugar, or do they need a **Monday/Friday lead digest** (we can send via Mailgun)? | SM | No |
| O4 | What happens to a lead the bot **cannot qualify** (someone off-target)? Fallback path. | SM | No |
| O5 | Who **monitors** that leads are actually flowing? A silent break means lost leads and nobody notices. | Todd / Zach | No |

## 4. Tactical (the near-term moves to go live)

| # | Confirmation needed | Who answers | Touches a rep? |
|---|---|---|---|
| C1 | **Internal message to the team** goes out before the first live lead. Confirm who says it and when. | Todd / SM | Yes |
| C2 | **One friendly first user** validates the flow before wider exposure. | Todd / SM | Yes (chosen one) |
| C3 | Approve **one labelled test lead**, or stand up a sandbox. (All records are on team "Global," so a test lead cannot be hidden and needs sign-off.) | SM | No |
| C4 | **Soft launch** on the dev site or one lander first, before site-wide. | Todd / Zach | No |
| C5 | **Phone in the bot**: required, or a placeholder so the record always creates? | SM | No |

## 5. Logistics (access, sequencing, hand-offs)

| # | Confirmation needed | Who owns | Blocked on |
|---|---|---|---|
| L1 | **SugarCRM login** that can create leads (or confirm we work through the existing Zapier connection). | Todd | Todd |
| L2 | **WordPress login / intro to the web-dev host** for the live-site go-live. | Todd | Todd |
| L3 | Named **IT contact** (the one who was on vacation) with an intro, for DNS and GTM coordination. | Todd | Todd |
| L4 | **ZoomInfo and Mailgun** account access / seats for setup. | Todd | Todd |
| L5 | **9rooftops (agency)** coordination for the production GTM go-live tag. | Todd | Todd |
| L6 | **Manual steps** that only Zach can do (logins, uploads) vs steps that need Todd or IT. Confirm the split so nothing stalls waiting on the wrong person. | Zach / Todd | - |
| L7 | **Regroup cadence** through go-live. | Todd / Zach | - |

---

## The one-line version for Todd

"The bot catches leads we are losing in the four-hour gap, feeds them straight to the sales manager
in the system he already uses, and touches nobody on the plant floor. We measure it as its own
channel from day one, so we can show exactly what net-new revenue it brought in, by region and by
source, without disrupting how anyone works today."
