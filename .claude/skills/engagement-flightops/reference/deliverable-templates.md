# Engagement Flight-Ops — Componentized Deliverable Library
_Reference for /engagement-flightops. The client-facing + internal deliverables the machinery emits_
_per engagement, each parameterized by the one engagement SSOT. PRL Resins = reference instance #1._

## How to read this
Each deliverable is a **template contract**: what it consumes from the SSOT, who it's for, what it
contains, and the PRL exemplar file that IS the instance-#1 template. On engagement #2, lift the
exemplar, strip PRL specifics, parameterize the marked fields → the reusable template. Do not build
all templates as blank renders now (instance-#1 over-engineering); capture the contracts, harden on #2.

## Cross-cutting rules (apply to every template)
- **Audience gate:** every deliverable is tagged 🔒 internal / 🤝 client-facing. Client-facing renders
  run a **profiling scrub** (remove the counterpart's psychographic model) + a **channel check** (🔒
  never emailed/hosted/Drive-shared; only 🤝 gets a forwardable copy).
- **SSOT is git; Drive/HTML are mirrors.** Manual/periodic sync, never two-way auto.
- **Register-match the counterpart** (linear vs parallel, boring/low-variance vocab, etc.) from the
  SSOT's `counterpart_profile` — which itself stays 🔒 machine-local, feeding tone but never shipping.

## The two faces (the spine): one SSOT → internal ops set + scrubbed client-facing set
Every engagement renders TWICE from the same SSOT, via mechanical audience projection (reuse
`recoil-ship`'s logic; this is the omakase back-of-house → front-of-house move, `--audience external`):

| Internal ops deliverable (🔒 full) | → projects to → | Client-facing scrubbed deliverable (🤝) |
|---|---|---|
| CRM/systems deep-dive + findings | → | Discovery value-reveal (upside in their numbers, no internal candor) |
| Roadmap + phase-map (JTBD/DoD/pricing) | → | Scope doc (phases + DoD as scope, no dollar internals) |
| De-risked plan (pre-mortem, hours, pricing) | → | Kickoff / now-next-later (what's now/next/parked) |
| Project registry (all artifacts, channels) | → | Status KB (where things stand, plain language) |
| Instrument panel (all gauges incl. 🔒 budget/scope) | → | Client HUD (gauges minus budget/scope) |
| Change-mgmt punchlist (5-lens) | → | Forwardable checklist rows only |
| Pre-flight checklist (internal deps) | → | Client pre-flight checklist (the batched asks) |

**The projection is mechanical, not manual:** it (1) drops 🔒 deliverables entirely, (2) **scrubs the
counterpart-profiling** from anything shipping, (3) removes internal pricing/opportunity-cost candor,
(4) register-matches the counterpart, (5) enforces the channel rule (🤝 forwardable, 🔒 never). The
scrubbed set is the ONLY thing that may be emailed / Drive-shared / hosted. PRL instance #1: the Drive
"Project Knowledge Base" is the scrubbed projection of the internal set; `SAFE-project-kb.md` is its
git source.

## The lifecycle → deliverable map
| # | Lifecycle stage | Deliverable | Aud | Consumes from SSOT | PRL exemplar (instance #1) |
|---|---|---|---|---|---|
| 1 | Onboarding / intake | **Engagement SSOT** (the JSON) | 🔒 | — (scaffolded) | `recoil-new` → `runtime/recoil/generated/<id>.json` |
| 2 | Discovery | **Discovery value-reveal** (forward value across cost/time/integration/revenue + seat-at-table close) | 🤝 | findings, counterpart numbers | `2026-08-04-todd-discovery-value-reveal.md` |
| 2b | Discovery | **Systems / data audit** (deep-dive scope + findings) | 🔒 | systems inventory | `2026-08-04-todd-crm-deep-dive-scope.md` |
| 3 | Scoping | **Scope doc / roadmap** (phases, JTBD, DoD per phase) | 🤝 (scoped) + 🔒 (full) | phase list, JTBDs | `2026-08-04-todd-ROADMAP-1.1-to-1.4.md` + `...phase-map-1.1-to-1.5.md` |
| 4 | De-risk / planning | **De-risked plan** (dependency map + Gantt + pre-mortem FMEA + phased fixed pricing) | 🔒 | deps, failure modes, hour est. | `2026-08-04-todd-1.2-1.5-derisked-plan-gantt-premortem.md` |
| 4b | Pricing | **Engagement-shape / recalibration** (instrument options, anchor) | 🔒 | effort, budget anchor | `2026-08-04-todd-recalibration-and-engagement-shape.md` |
| 5 | Kickoff | **Pre-flight checklist** (one batched, serial, defaults-on-no-response client-input list) | 🤝 | open client inputs | `2026-08-04-todd-sends-draft.md` (Send 1) |
| 5b | Kickoff | **Kickoff note / now-next-later** (what's done, what's next, what's parked) | 🤝 | status, phase sequence | Coffee-follow-up email (Gmail draft) |
| 6 | Status / tracking | **Project KB / status SSOT** (where things stand, plain-language) | 🤝 | status, roadmap-scope, findings | `2026-08-04-todd-SAFE-project-kb.md` (+ Drive Doc) |
| 6b | Status / tracking | **Instrument panel / HUD** (compounding gauges, CWO trigger) | 🔒 gauges gated | all gauge metrics | `flight-operations-system.md` §2 + `hud-designsync-brief.md` |
| 7 | Change control | **Change work order** (fires when Scope gauge → red: what + why, approve before work) | 🤝 | scope-creep event, budget | (new template — CWO contract below) |
| 8 | People / adoption | **Change-management punchlist** (5-lens people/process/tools confirmations) | 🔒 (forwardable rows) | stakeholder map | `2026-08-04-todd-punchlist-people-process-tools.md` |
| 9 | Debrief / close | **Post-flight kaizen debrief** (well/didn't/off-rails/automate/bank/anti-patterns) | 🔒 | phase outcomes | `recoil-close` → debrief |
| 10 | Reconciliation | **Project registry** (index of every artifact: home, audience, channel, status) | 🔒 | artifact list | `2026-08-04-todd-PROJECT-REGISTRY.md` |

## Template contracts worth spelling out (net-new vs PRL)
**Change work order (§7, net-new):** one page. Fields: what was asked (outside current phase) · why it
matters · effort + fixed price · impact on timeline · approve/decline line. Trigger: Scope or Budget
gauge red. Purpose: the mechanical stop against cost bubbling.

**Kickoff / now-next-later (§5b):** three columns — Now (this phase, in flight) · Next (queued, gated
on X) · Later (parked behind a trigger). Register-matched to the counterpart. This is the client's
at-a-glance heartbeat; pairs with the HUD.

## Parameterization contract (what makes these reusable)
Every template reads these SSOT keys (names illustrative): `engagement.name`, `counterpart` (+ 🔒
`counterpart_profile` for tone only), `phases[]` (id, jtbd, dod, deps, hours, price), `findings[]`,
`gauges{}`, `stakeholders[]`, `artifacts[]` (the registry), `constraints[]`, `vendor_costs[]`.
Rendering = SSOT + template + audience-gate → output. That is the whole assembly line.
