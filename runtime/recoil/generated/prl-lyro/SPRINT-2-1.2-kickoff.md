# Phase 1.2 Kickoff + Doc Tracker — Sprint 2 (Delivery, Enrichment, the Metric)

_2026-08-10 (Mon) · Paid $4,500, kicked off today. This is the plan + the doc tracker + what "done" means,
so the payment-milestone sequence is clean and 1.3 starts with no blockers. SSOT; rendered artifact for
viewing/sharing is a projection of this._

## Payment-milestone sequence (each phase gated by its own payment)

| Phase | Price | Status | Gate to start |
|---|---|---|---|
| 1.1 Go-live | (original engagement) | PAID 7/24 · finishing | — |
| **1.2 Delivery + metric** | **$4,500** | **PAID 8/10 · kicking off** | paid ✓ |
| 1.3 Recognition | $4,000 | pay when ready · prework underway | needs 1.1+1.2 done (info@ email + CRM integration) |
| 1.4 SEM landers | $6,000 | pay when ready | needs 1.2 delivery |
| 1.5 Assistant (AI) | $3,500 | pay when ready | needs delivery proven; optional |

## First, what closes 1.1 (the 5th layer)

1.1 is 4/5. The 5th and final layer is **verification on the receiving end**: a real test lead goes all the
way through and is confirmed **received, complete, in SugarCRM**, with the rep notification firing. Layers
1-4 (deterministic recognition, staged end-to-end, live capture, guardrail-ready) are proven up to the moment
of the write; the write-and-receive is the one thing left. It is sandbox-gated. **1.1 is not "go-live done"
until a lead is verified on the receiving end** — and that same wiring is the first deliverable of 1.2.

## Client actions — the UAT punch list (Todd / sales manager)

The 5th layer is **User Acceptance**: it is yours to accept. Simple frame — we send a test lead through, you
confirm it arrived. If it did not, we troubleshoot until it does. That is the whole reason we test in a safe
copy first, so nothing ever goes wrong in front of a real customer.

- [ ] Grant the SugarCRM sandbox access (or approve one clearly-labeled test lead we create and delete together)
- [ ] Register **info@prlresins.com** (you / IT)
- [ ] 30 minutes with your sales manager + whoever runs your reports
- [ ] Watch a test lead run through, start to finish
- [ ] **Check it was received in SugarCRM** — complete, tagged "Chatbot," routed to the right rep
- [ ] Confirm the notification landed in the inbox
- [ ] If anything is off → **we troubleshoot until it lands clean** (loop here until it does)
- [ ] **Accept** → flip live in the window you choose

Only the last two lines are the acceptance gate; the rest set it up. "Done" = you checked, it arrived clean.

## 1.2 — what "done" looks like (Definition of Done)

1. A real test lead lands in SugarCRM with **all required fields AND an enriched business email**.
2. **Rep notification + prospect autoresponder both fire within seconds.**
3. **Time-to-first-touch is recorded** via an automatic signal (or a documented proxy: status New→Working).
4. A **baseline exists** (volume, close rate, deal size by region and source) so net-new is provable.

## What we'll need for validation (evidence per DoD item)

| # | Done means | Validation evidence |
|---|---|---|
| 1 | Lead lands complete + enriched | Screen-capture of the sandbox Lead: all 6 required fields + ZoomInfo business email, `lead_source=Chatbot`, correct rep |
| 2 | Notify + autoresponder fire fast | Timestamped Mailgun rep alert + the prospect's autoresponder, both within seconds of submit |
| 3 | The 4-hour number is instrumented | A recorded time-to-first-touch value, OR the chosen proxy documented (New→Working) |
| 4 | Net-new is provable | A baseline report by region + source (the number the chatbot's net-new is measured against, incl. the $15K lead-gen line) |

## Work sequence (ordered)

**Now — parallel prework (no sandbox needed):**
- Prep the baseline query (volume / close-rate / deal-size by region + source).
- Stand up ZoomInfo enrichment + a Mailgun sending subdomain (no live-DNS dependency).
- Finalize the Zapier Create-Lead field transform (already staged; lock it).
- Schedule the **CRM Data Reality session** (SM + reports owner) — the long pole.

**Gate: SugarCRM sandbox access (unblocked commercially; needs the grant).**

**Then — the wiring + proof (needs sandbox):**
1. Wire Tidio webhook → Zapier Catch Hook → Sugar Create-Record (sandbox).
2. Run one test lead **down each branch**; verify **received** (this closes 1.1's 5th layer).
3. Wire Mailgun notify + prospect autoresponder; verify both fire within seconds.
4. Add ZoomInfo enrichment; verify the business email fills.
5. Stamp arrival + time-to-first-touch (or adopt the documented proxy).
6. Run the CRM Data Reality session; produce the baseline.

**Close:** all 4 DoD met + evidence captured → 1.2 accepted.

## Blocker-clearance so 1.3 starts clean

1.3 depends on two things that **must land inside 1.2**, or 1.3 stalls:
- **info@prlresins.com registered** (email/DNS) — Todd/IT.
- **CRM integration proven** (the delivery wiring above).

Todd-side dependencies to line up during 1.2 (all whenever-you're-ready, but these are the gates):
grant sandbox access · register info@ · a 30-minute SM + reports session. If those three land this week,
1.2 completes on the base timeline and **1.3 opens with zero blockers.**

## Doc tracker (1.2 deliverables + status)

| Doc | Purpose | Status |
|---|---|---|
| `2026-08-04-todd-ROADMAP-1.1-to-1.4.md` | canonical roadmap | DONE |
| `2026-08-04-todd-phase-map-1.1-to-1.5.md` | acceptance table | DONE |
| Zapier Create-Lead mapping (`2026-08-03-...create-lead-mapping.md`) | field transform | STAGED — lock this sprint |
| SugarCRM config audit (artifact 5fc2e7ac) | live schema truth | DONE |
| `prl-lyro/TEST-PLAN-go-live.md` (Layer 3 = 1.2 delivery) | the acceptance gates | DONE |
| CRM Data Reality agenda | the long-pole session script | TODO — write before the session |
| Baseline report (by region + source) | the net-new benchmark | TODO — produce in the session |
| Enrichment + Mailgun setup notes | ZoomInfo/Mailgun config record | TODO |
| 1.2 evidence artifact (like the 1.1 one) | the close-out proof for Todd | TODO — at 1.2 close |

## Target done date

- **Kicked off:** Mon 2026-08-10.
- **Best:** ~2026-08-15 (few days) — sandbox lands immediately + CRM already stamps first-touch.
- **Base:** **~2026-08-22** (1 to 1.5 weeks) — sandbox access + one data session land this week.
- **Worst:** ~2026-08-24 (2 weeks) — CRM doesn't capture first-touch (use the proxy) or access stalls.
- **Hard requirement:** by the time 1.3 begins, **no blockers** — info@ registered + CRM integration proven,
  both completed inside 1.2.
