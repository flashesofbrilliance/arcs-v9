# Recoil — PRL × SugarAI sandbox call, Aug 11 2026 (3:00 PM EDT)

_Recoil-close on the SugarCRM sandbox/technical alignment call. Grounded in the Granola transcript
(`31391f0b-3ce6-4fa1-8f40-62bd7387c057`). Attendees: Zach, Todd Hotes (PRL), Long Ngo (Director, Customer
Success — bridging for Beeka), Sebastian (Technical Support Manager), Alberto (Support Specialist). Bill Galla
(VP Sales / national sales manager) named as the PRL Sugar owner; Beeka (brand rep/CSM) out this week._

## Reverse listening — where it landed
Went in to "unblock the sandbox + get a named technical contact + a health-check." Landed on a cleaner but
more commercial picture: **the sandbox is free and easy, but the integration/customization work itself is
out of standard support scope** — it routes to **SugarCare (dedicated PS hours) or Professional Services**.
The technical unblock is real but gated on **Zach specifying the exact scoped API permissions** so support can
provision without handing over full admin. Todd set three plain guardrails that are the real acceptance frame.

## Deep recall — pre-call belief vs reality

| Pre-call belief | Reality on the call | Update |
|---|---|---|
| Copy latest production **down** to the sandbox (refresh or new) | Cloning production requires **re-provisioning Sugar Identity/IDM**; lean shifted to a **clean-slate net-new tenant** as easiest. Either is free (2-sandbox allowance). | **CHANGED** → clean-slate preferred |
| Get Zach **admin** access | Zach explicitly asked for a **scoped test API key, NOT full admin** — just to add field types + geographic routing policies. Support wants the exact scope first. | **CHANGED** → scoped key |
| Sandbox is THE gate | The gate is now **API-permission scoping**: Zach specifies exact perms → Alberto confirms with engineering → provision. | **REFRAMED** |
| Support will guide the integration | **Integration/customization is out of standard support scope.** Vehicle = SugarCare / Professional Services (dedicated hours). | **NEW (commercial)** |
| We need a named dev-rel contact | Got **Sebastian (Tech Support Mgr) + Alberto (Support Specialist)** for support-scope; the *technical build* guidance sits with **PS/SugarCare**, TBD. | **PARTIAL** |
| ZoomInfo unwired / Hint-vs-ZoomInfo open | **ZoomInfo bidirectional enrichment already exists** (import Sugar → enrich → push back). | **RESOLVED (mostly)** |
| Mailgun: no build, memory-vs-repo discrepancy | Todd/Zach named **Mailgun as part of the current live stack** (Gravity Forms + Zapier + Mailgun). | **RECONCILED** — it's real |
| Sugar might have an MCP | Support offers **only publicly-available documentation**; no MCP. Postman collection + changelog are the path. | Confirmed (no first-party MCP) |

## Todd's three guardrails (the real acceptance frame — quote-grounded)
1. **"We're not going to do anything to disrupt Bill's access or flow to the CRM."** The whole business runs on it.
2. **"If there are any additional costs to our program with Sugar, I just want to know those before."**
3. **"Not overcomplicating this… the whole point here is to be able to transition the leads into Sugar and
   have them disseminate geographically based on our 8 different reps around the country."**

These are the constraints every downstream decision is scored against. (Ties to the machine-local Todd profile:
low-drama, justifiability-not-affordability, scope-discipline.)

## What was confirmed / offered
- **Sandbox:** free under the 2-sandbox license allowance; refresh-clone OR net-new both possible; clone needs
  IDM/Sugar-Identity re-provision, users set their own credentials after.
- **Postman:** a full RESTful API reference page exists; Alberto to confirm **how much can be shared** (checks
  with engineering/PS).
- **Release notes / changelog:** publicly available; Alberto to share (for tracking recent changes). Future
  changes he can't speak to.
- **Health check:** Zach's framing accepted; Alberto unsure it's publicly available → **checks with the dev team**.
- **SSOT mechanics:** Sugar wants everything **tracked as a case** (case + child cases). Our Google Doc feeds
  it — **Sebastian converts the doc into Sugar tickets/cases**. The case is their system of record; our doc is
  the async intake.
- **Invoices:** no overdue invoices; Alberto to check open invoices with AR.

## Action items (owner → action)
| Owner | Action | Status |
|---|---|---|
| **Zach** | Create the Google Doc SSOT of open questions (done — in the shared folder); **specify the exact scoped API permissions** needed | doc done; **perms spec = the blocker** |
| **Alberto + Sebastian** | Confirm exact API permission scope with engineering, then **provision scoped sandbox access** | pending |
| **Sebastian** | Convert the Google Doc SSOT into Sugar support case/tickets | pending |
| **Alberto + Long** | Evaluate **SugarCare / Professional Services** fit for the integration work | pending |
| **Long** | Follow up with **Beeka** on account tier, QBR history, right-sizing | pending |
| **Alberto** | Share the **Postman collection** + public **release notes / changelog**; check **open invoices** with AR | pending |
| **Zach + Todd** | Offline: map technical roadmap ↔ tier/cost trade-offs before committing to PS/SugarCare | pending |

## Next steps
1. **Immediate blocker:** Zach writes the exact scoped-API-permission list into the SSOT doc → Alberto confirms
   with engineering → sandbox provisioned. Nothing builds until this clears.
2. **Follow-up call** after Alberto + Sebastian take a first pass at the open-questions doc.
3. **Commercial track (parallel):** Long ↔ Beeka QBR/right-sizing; Alberto ↔ PS/SugarCare scoping — surfaces any
   additional cost **before** it's incurred (Todd's guardrail #2).

## What we owe / what they owe
- **We owe:** the scoped-permission list in the SSOT; keep the SSOT case-convertible (clean, itemized).
- **They owe:** provision scoped sandbox access; Postman + changelog; PS/SugarCare + tier read; AR invoice check.

## Belief updates banked
See `prl-lyro/sugar-alignment-belieflog.jsonl` (in_call/post_call events appended 2026-08-11): sandbox-path →
clean-slate; admin-api → scoped key; new spans `sugar.support-scope-commercial`, `sugar.contacts`,
`sugar.api-scoping-blocker`; `zoominfo.email-enrichment` → bidirectional-exists; `mailgun.notify-autoresponder`
→ reconciled (in live stack).
