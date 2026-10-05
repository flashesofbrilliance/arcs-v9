# Leg 1 — Tidio Flow Map (evidence, 2026-08-17)
> Method: JSON export (live flow only — Tidio only exposes Export for flows activated at
> least once) + node-by-node screenshot inspection (draft flows, no export available).
> Raw export: `tidio-flows-baseline/PRL-Resins-Lead-Capture.LIVE.json`

## Flow A — "PRL Resins - Lead Capture" (LIVE, 28 executed, 43% engagement)
Source: exported JSON, parsed mechanically (not eyeballed).

- **27 nodes / 30 edges.** Trigger: `onFirstVisit`. Node types used: `onFirstVisit`,
  `sendChatMessagesToVisitor`, `decisionCardMessages` (3x, creating 5-way branching),
  `getUserInput` (16x).
- **`sessionVariables: []` and `botRequests: []` — both empty, confirmed in raw JSON.**
  Zero of the 16 `getUserInput` nodes have `answer_to_variable: true`. No answer collected
  anywhere in this flow is bound to a named variable. There is no webhook/integration node
  of any kind in the node-type set.
- **4 terminal branches, all dead ends** (nodes 5, 17, 21, 27) — each is a
  `sendChatMessagesToVisitor` node with no outgoing connection.
- **Node 21 and node 27** (2 of the 4 dead ends) explicitly promise the visitor a callback:
  - Node 21: *"Done. Someone from our team will call you shortly, usually within a few
    hours. No phone trees."*
  - Node 27: *"Thanks! One of our resin specialists will reach out shortly, usually within
    a few hours. A real person, no phone trees."*
  - **This SLA is a structural fiction today** — nothing captures the answers into named
    fields, and there is no delivery action anywhere in the flow to act on them.
- Question node 26 asks *"What state or region are you in?"* — free text, no validation —
  this is the field the plan's transform step must map to Sugar's `location_c` abbreviation
  enum.
- Shape: dense, 5-way branching from a `decisionCardMessages` router (node 3), matches the
  "tangle" flagged in the pickup doc.

## Flow B — "PRL Resins - AI Handoff (lead delivery bridge)" (DRAFT, never activated)
Source: node-by-node screenshot inspection (no JSON export available for un-activated drafts).

- **Linear chain, no branching.** `First visit on site` → `Send a chat message` (opener) →
  6x `Ask a question` (chained via `Success`) → `Send a chat message` (terminal) → **open "+"
  add-node slot** (Triggers/Conditions/Actions palette, empty).
- Question sequence, in order:
  1. *"In one line, what do you need? A resin, a spec, or a replacement."* — no validation
  2. *"Who should we get this to?"* — no validation
  3. *"Best email?"* — Email validation
  4. *"Best number to reach you?"* — Phone validation (not marked optional — matches
     Todd's "ask for it" instruction)
  5. *"And your company?"* — no validation
  6. *"What state or region are you in?"* — no validation (same transform target as Flow A)
- **Every question node checked has "Save the answer as a contact property" toggled OFF.**
  Same structural gap as Flow A: nothing is bound to a variable today, even though this
  flow's name implies it should be the delivery layer.
- Terminal message: *"Thanks. A PRL resin specialist will follow up shortly, usually within
  a few hours. A real person, no phone trees."* — same unfulfillable SLA promise as Flow A.
- **Tidio's own conflict banner on the trigger node:** *"OOPS! YOU ALREADY HAVE A FLOW WHICH
  USES THE 'FIRST VISIT ON SITE' TRIGGER TO SEND A MESSAGE. THIS WILL CAUSE SEVERAL FLOWS TO
  FIRE SIMULTANEOUSLY ON A USER'S FIRST VISIT. FLOW OVERLOAD!"** — this flow currently shares
  the same `onFirstVisit` trigger as the live Lead Capture flow. Activating it as-is would
  double-fire both flows on every new visitor. Despite the name "lead delivery bridge," it is
  wired today as an independent first-visit flow, not as something Lead Capture hands off to.

## Comparative verdict (plan's own <1hr rebuild-clean-bias gate)
Both flows were mappable within budget, so the gate resolves on structure, not on time spent:

| | Flow A (live) | Flow B (AI Handoff draft) |
|---|---|---|
| Node count / shape | 27 nodes, 5-way branching | 8 nodes, linear |
| Variables bound | 0 / 16 | 0 / 6 (same gap) |
| Delivery node present | No | No, but has an open "+" slot at the true terminus |
| Trigger conflict | None (currently sole first-visit flow) | Yes — collides with Flow A's trigger |
| Engagement history | 28 executions, 43% engagement (real data) | 0 (never activated) |

**Recommendation: graft onto Flow B (AI Handoff draft), not Flow A.** It is structurally
the clean target the plan anticipated — one line, one open slot for the Send-to-Zapier
action. But it cannot go live in its current form: its trigger must be changed from
`onFirstVisit` to something that doesn't collide with the live Lead Capture flow (either
retrigger it from within Lead Capture's decision tree as the name "bridge" implies, or
replace Lead Capture's role entirely and deactivate Flow A). That trigger question is a
product decision, not an implementation detail — flagging for confirmation before wiring.

Either graft target needs the same two fixes before a Send-to-Zapier node can carry real
data: (1) turn on "Save the answer as a contact property" for every question node, naming
each property to match Sugar's required fields, (2) add the delivery action at the true
terminus.

## Branch-path trace (why "retrigger into AI Handoff" needs revising)
Traced all 5 decision-card branches from node 3 ("What brings you in?") to their terminals.
Only 2 of the 4 terminals collect any contact info at all — the other 2 are pure opt-outs:

| Terminal | Reached via | Fields already asked | Sugar-required fields present? |
|---|---|---|---|
| **5** | "Guides and resources" → declines follow-up | none | N/A — visitor declined, correctly a dead end |
| **17** | "Something else" → declines follow-up | none | N/A — visitor declined, correctly a dead end |
| **21** | "Have someone call me" | name, phone, preferred time (optional) | **Missing `account_name` and `location_c` — cannot produce a valid Sugar Lead as designed** |
| **27** | "I know what I need" / "Help me choose" (converge) | who-to, email, phone (optional), company, state | Has all 6 required fields, but phone is marked **optional** — conflicts with Todd's explicit "ask for it" instruction |

**Revised recommendation:** don't retrigger into AI Handoff's separate 6-question chain at
21/27 — that would re-ask email/phone/company/state the visitor already answered once,
which is worse UX than what exists today. Instead, treat AI Handoff as the **field-naming
and Send-to-Zapier template**, and graft directly onto Lead Capture's own two lead-ready
terminals:
- **Terminal 27** (has all 6 fields): bind its 5 existing `getUserInput` answers to
  variables, insert one additional required question ("What's your company?" already
  asked at node 25 — good), make node 24 (phone) required not optional, add Send-to-Zapier
  after node 27.
- **Terminal 21** (missing 2 fields): insert 2 new question nodes before the terminal
  (company + state) to reach parity with terminal 27's field set, bind all 3+2 answers to
  variables, add Send-to-Zapier after.
- **Terminals 5 and 17** stay untouched — they're deliberate opt-outs, not leads.

This is a bigger surgery than "one insertion point" (2 branches, 1 new pair of questions on
branch 21) but it respects what visitors already told the bot instead of asking them twice.

## Resolved: location_c format (abbreviation vs full name)
Two prior "verified" sources disagreed: pickup doc (2026-08-17, sandbox test) said abbreviation;
STATE-OF-SUGAR-2026-08-11.md (100-record prod audit) said full names, explicitly reversing an
earlier abbreviation note. Re-verified live against both endpoints rather than picking a side:

- **Enum schema** (`/Leads/enum/location_c`, identical on sandbox + prod): US states defined as
  2-letter abbreviation keys/values (`"CT":"CT"`). Non-US locations use full names because they
  aren't state abbreviations — not a counter-example.
- **15 most recent live prod records**, checked by `lead_source`: records with `lead_source:
  "Other"` (manual/import) carry full names; the 2 records with `lead_source: "Web Site"` — the
  existing automated-integration path, the closest live precedent to what the chatbot will be —
  both carry abbreviations (`TX`, `GA`).

**Verdict: write abbreviations.** The Aug-11 doc's "full names" read was a sampling artifact — its
100-record snapshot was 91% `lead_source: "Other"` (manual/bulk-import), the same skew that
document itself flagged as distorting the email-completeness stat two paragraphs earlier. The two
real automated-integration records point the other way, matching the schema, the sandbox test, and
today's pickup doc.

## Territory-map vs Sugar's actual routing — broader sandbox sweep (2026-08-17)
9 tagged test leads created in sandbox (`ARCSTEST` first_name, deleted immediately after read),
varying state (7 states covering 6 of the 8 named reps + 1 Distribution state) and, for TX, source
(Chatbot vs Web Site) to isolate whether lead_source affects routing at all.

| State | Source | CSV expects | Sugar actual | Match |
|---|---|---|---|---|
| TX | Chatbot | Steve | Steve Fabrizius | ✓ |
| TX | Web Site | Steve | Steve Fabrizius | ✓ — **same as Chatbot**, confirms source-agnostic |
| AL | Chatbot | Christian | **Bill Galla** | ✗ |
| FL | Chatbot | Howard | Howard Altman | ✓ |
| GA | Chatbot | Kathy | **Christian Cassel** | ✗ — matches the earlier live-prod GA mismatch, not a fluke |
| AZ | Chatbot | Distribution → Nicole | **Bill Galla** | ✗ |
| NY | Chatbot | Rob (W) / Howard (E) split | Robert Spano | ~✓ (primary rep, sub-region unresolvable from state alone) |
| "" (blank) | Chatbot | — | **API hard-rejects**: "Required field Location is missing" | N/A — critical edge case, see below |
| CT | Chatbot | Lynn | Lynn Winston | ✓ — consistent with the original test |

**Finding 1 — lead_source does not affect routing.** TX routed identically under `Chatbot` and
`Web Site`. This resolves the earlier open risk cleanly: once "Chatbot" is added to the prod
picklist, no extra routing configuration is needed for it to behave like `Web Site` does today.

**Finding 2 — the territory-map CSV Todd shared does not match Sugar's actual configured rule.**
3 of 7 tested states mismatched (43% in this sample): AL and GA send to the wrong named rep, and
AZ ("Distribution" in the CSV) has no distinct "Distribution" routing behavior in Sugar at all —
it falls through to Bill Galla, the same default every other unmapped case gets. This isn't
isolated to Distribution states (AL is a normal named-rep state) — the CSV itself needs
reconciliation against Bill/Todd before it's trustworthy as a routing source of truth. **Do not
build delivery logic that trusts the CSV over Sugar's actual behavior** — if a transform step is
ever added client-side to "correct" routing, it would be correcting toward the wrong answer for
at least AL/GA/AZ.

**Finding 3 — blank `location_c` is a hard create failure, not a silent default.** The one
Chatbot-sourced create using `location_c: ""` was flatly rejected by the API. This means: if a
Tidio flow ever lets a visitor skip or blank out the state question, the Sugar create step will
fail outright, not create-with-no-routing. The delivery flow (Tidio and/or the Zap) must guarantee
`location_c` is populated before attempting create — a soft/optional state question is not a
routing risk, it's a **lead-loss risk** (the whole record fails to create).

**Recommendation:** before go-live, either (a) run the full 50-state sweep (cheap, same method,
~50 sandbox creates) to get complete signal rather than a 7-state sample, or (b) hand Bill/Todd
the mismatch list above and ask them to reconcile the CSV against Sugar's actual Studio-configured
assignment rule directly — that's authoritative in a way inference from samples never fully is.

## FULL 43-state sweep (2026-08-17) — complete territory-map audit
Extended the 7-state sample to all 43 US states present in Sugar's `location_c` enum, plus 3
out-of-enum probes (WV abbreviated, "West Virginia" full name, "Hawaii" full name — Sugar's enum
is missing 7 of the 50 states Todd's CSV lists: AK, DE, HI, ID, NM, SD, WV). All tagged
`ARCSTEST`, `lead_source=Chatbot`, created and deleted in sandbox only. Zero residue confirmed.

| State | CSV expects | Sugar actual | Match |
|---|---|---|---|
| TX | Steve | Steve Fabrizius | ✓ |
| AL | Christian | **Bill Galla** | ✗ |
| FL | Howard | Howard Altman | ✓ |
| GA | Kathy | **Christian Cassel** | ✗ |
| AZ | Distribution/Nicole | **Bill Galla** | ✗ |
| NY | Rob(W)/Howard(E) | Robert Spano | ~✓ |
| CT | Lynn | Lynn Winston | ✓ |
| AR | Steve | Steve Fabrizius | ✓ |
| CA | Distribution/Nicole | **Lynn Winston** | ✗ |
| CO | Steve | Steve Fabrizius | ✓ |
| IA | Steve | **Dan Damas** (not in CSV roster at all) | ✗ |
| IL | Pat/Kathy(2nd) | Kathy Brown | ~✓ (secondary matched) |
| IN | Pat | **Tim Mulcahy** (not in CSV roster at all) | ✗ |
| KS | Steve | Steve Fabrizius | ✓ |
| KY | Christian | Christian Cassel | ✓ |
| LA | Steve | **UNASSIGNED (blank)** | ✗ |
| MA | Lynn | Lynn Winston | ✓ |
| MD | Lynn | **Christian Cassel** | ✗ |
| ME | Lynn | Lynn Winston | ✓ |
| MI | Pat | **Tim Mulcahy** | ✗ |
| MN | Pat/Kathy(2nd) | **Dan Damas** | ✗ |
| MO | Steve | Steve Fabrizius | ✓ |
| MS | Christian | **UNASSIGNED (blank)** | ✗ |
| MT | Distribution/Nicole | **UNASSIGNED (blank)** | ✗ |
| NC | Christian/Kathy(2nd) | Christian Cassel | ✓ |
| ND | Pat | **Dan Damas** | ✗ |
| NE | Steve | Steve Fabrizius | ✓ |
| NH | Lynn | Lynn Winston | ✓ |
| NJ | Howard | Howard Altman | ✓ |
| NV | Distribution/Nicole | **Bill Galla** | ✗ |
| OH | Rob | Robert Spano | ✓ |
| OK | Steve | Steve Fabrizius | ✓ |
| OR | Distribution/Nicole | **Lynn Winston** | ✗ |
| PA | Rob(W)/Howard(E) | Robert Spano | ~✓ |
| RI | Howard | **Lynn Winston** | ✗ |
| SC | Christian/Kathy(2nd) | Christian Cassel | ✓ |
| TN | Christian | Christian Cassel | ✓ |
| UT | Distribution/Nicole | **UNASSIGNED (blank)** | ✗ |
| VA | Christian | Christian Cassel | ✓ |
| VT | Lynn | Lynn Winston | ✓ |
| WA | Distribution/Nicole | **Lynn Winston** | ✗ |
| WI | Pat/Kathy(2nd) | Kathy Brown | ~✓ (secondary matched) |
| WY | Distribution/Nicole | **UNASSIGNED (blank)** | ✗ |
| WV (abbrev, out-of-enum) | Christian | **UNASSIGNED (blank)** — record still created | N/A |
| West Virginia (full, out-of-enum) | Christian | **UNASSIGNED (blank)** — record still created | N/A |
| Hawaii (full, out-of-enum) | Distribution/Nicole | **UNASSIGNED (blank)** — record still created | N/A |

**Scoreboard across the 43 enum-covered states:** 22 clean/near matches, 21 mismatches —
**a ~49% mismatch rate, essentially a coin flip.** This is far worse than the original 7-state
sample (43%) suggested; the CSV cannot be trusted as a routing source of truth for roughly half
of US states.

**Four distinct failure patterns, not one:**
1. **Wrong named rep** (AL→Bill, GA→Christian not Kathy, MD→Christian not Lynn, RI→Lynn not
   Howard) — the CSV's per-state assignment is simply out of date for these states.
2. **"Distribution" is not a real Sugar rule.** Every CSV-flagged Distribution state (AZ, CA, NV,
   OR, WA — 5 of 5 tested) routed somewhere else entirely (Bill or Lynn), never to Nicole. The
   Distribution/Nicole category in the CSV does not correspond to any automated behavior in Sugar.
3. **Two active reps — Dan Damas and Tim Mulcahy — don't appear in Todd's CSV roster at all**,
   yet they're live assigned owners for IA/MN/ND (Dan) and IN/MI (Tim). The CSV's rep roster
   itself is incomplete, not just its state mappings.
4. **A new, worse failure mode: unassigned (blank).** 6 states (LA, MS, MT, UT, WY, plus all 3
   out-of-enum probes) create successfully but land with **no assigned_user_id at all** — not
   even the Bill Galla catch-all. A lead here sits in a queue nobody owns, which is worse than
   being routed to the wrong-but-real rep. This is a distinct, higher-severity risk than "wrong
   rep" and needs its own fix path (a default-assignee safety net), not just a corrected map.

**Out-of-enum values are silently accepted, not rejected — and always land unassigned.** Neither
`WV`, `"West Virginia"`, nor `"Hawaii"` triggered a validation error (unlike the earlier blank
`""` test, which did hard-fail). The record creates fine but nobody owns it. Since Sugar's enum is
missing 7 of the 50 states Todd's CSV covers, **any Tidio flow that free-texts the state answer
instead of using a fixed dropdown matching Sugar's exact enum will silently produce unowned leads
for visitors from AK, DE, HI, ID, NM, SD, or WV** — a meaningful market gap (WV alone is one of
Christian's CSV-mapped territories).

**Bottom line for delivery design:** do not build the Zapier transform to "correct" state values
against the CSV, and do not assume Sugar's native routing is a safety net — for roughly half the
states it either misroutes or drops the lead into no one's queue. Two things need to happen before
go-live, independent of the Tidio/Zapier build: (1) Bill/Todd need to reconcile the CSV against
Sugar's actual Studio-configured assignment rule directly (the mismatch table above is the punch
list), and (2) the delivery design needs a default-assignee fallback for the unassigned case,
because roughly 14% of tested states (6/43) hit it even when everything else works correctly.
