# PRL: Todd call ledger and 1.2 close-out checklist (2026-10-31)

Purpose: every call Zach had with Todd Hotes (PRL Resins), in date order, plus every item raised, sorted by phase and status, so 1.2 can be closed and the final payment can land.

## Sources and coverage

| Source | Result |
|---|---|
| Granola | 14 notes found (participant "Todd" plus keywords PRL, Polymer, Tidio, Sugar, Phase 1.2). AI summaries read for all 14. Transcripts NOT pulled (summaries were enough to list items; quotes below come from the summaries, not verbatim speech). |
| Fathom | Searched "Todd" across all recordings since 2026-06-01: 0 meetings. No Fathom data on this engagement. |
| Gmail | About 74 threads match Todd + chatbot/phase/invoice. Read in full: "Invoices for Chatbot Project" (Aug 12), "Chatbot go-live: 4 things I need before Part 2" (Oct 12), "PRL Resins // Phase 1 - Proposal" (Jul 2). Others seen by subject only. No reply from Todd appears on any of the three read threads (only Mixmax no-reply reminders). |
| Stripe | Not checked live this session. Payment status below comes from repo docs dated Aug 18 and Sep 17 and may be stale. |
| Repo | `_ARTIFACTS/prl-1-1-evidence/2026-08-18-dod-reconciliation.md`, `_ARTIFACTS/prl-1-2-close-loop/2026-09-17-phase-systems-dependency-map.md`, `2026-10-29-release-notes-phase-1-2-rc.md`, memory `project_todd_hotes_prl_resins.md`. |

## 1. Call table

| # | Date | Source | ID | Gist |
|---|---|---|---|---|
| 1 | 2026-07-02 | Granola | 36af17bf | Discovery: stack, Lighthouse audit, chatbot vision; Zach to send a phased proposal (sent same day by email). |
| 2 | 2026-07-09 | Granola | 6bcda1a5 | Chatbot first; route leads by territory straight into Sugar; build vs buy research. |
| 3 | 2026-07-20 | Granola | 20f5b815 | Phase 1 scope on Tidio; $1,500 fee proposed; 4-hour follow-up target named. |
| 4 | 2026-07-31 | Granola | 2387379e | Tidio Flows plan bought; live on site and Unbounce; DNS and territory list blocked. |
| 5 | 2026-07-31 | Granola | d471f203 | With Daniel (Tidio): AI + Flows plan, API needs Plus, use middleware for now. |
| 6 | 2026-08-03 | Granola | c09a8f23 | "Chatbot Review": note is empty, no summary. Content unknown. |
| 7 | 2026-08-05 | Granola | ea14c103 | 1.1 nearly done; 1.2 kickoff w/c Aug 10; Todd to pay 1.2 ($4,500). |
| 8 | 2026-08-06 | Granola | d4f20152 | Sugar handoff docs, IDES datasheets; payment talk (about $18K, split by card). |
| 9 | 2026-08-10 | Granola | 40dbf5af | Sandbox approval, Tidio email blocker, eval grid, acceptance criteria across 5 areas. |
| 10 | 2026-08-11 | Granola | 31391f0b | With Sugar (Long, Sebastian, Alberto): second sandbox, scoped API access. |
| 11 | 2026-09-01 | Granola | 35b35eff | 1.2 "closed and capped"; live demo routed to Lynn Winston; go-live before 1.3. |
| 12 | 2026-09-15 | Granola | 40453f62 | Misrouted leads go to Bill; transcripts on leads; three go-live steps. |
| 13 | 2026-09-17 | Granola | cd30a239 | Go-live readiness; "dead" status and field mapping bugs; Todd to record a Loom. |
| 14 | 2026-10-12 | Granola | ee74074f | "Wrapping up Phase 1.2" Part 1: lead source in prod, Zapier Pro, chatbot Sugar user. Part 2 pending. |

No call with Todd is recorded after Oct 12. The Oct 16 coffee (per memory) has no notes.

## 2. Checklist of every item raised

Status key: DONE-tested (evidence cited) · DONE-untested · OPEN · NEEDS-DECISION. Quotes are from Granola summaries, under 15 words.

### Phase 1.1 (chatbot capture and delivery)

| Item | Source + quote | Status |
|---|---|---|
| Chatbot on WordPress site and Unbounce | #4 "Chatbot live on both the main site and the Unbounce landing page" | DONE-untested on prod for the current flow 7752845 (RC runs on staging only) |
| Leads route by territory to the right rep | #2 "creates a new lead directly in Sugar CRM"; #13 Nebraska returned Steve Fabricius | DONE-tested in sandbox (RC tests 1, 3; Sep 1 Lynn Winston) |
| Minimum fields: name, email, phone, region | #2, #3 "Minimum required fields only" | DONE-tested (RC test 1: call-me asks name, phone, email, company, state) |
| Email check rejects bad input | (RC) | DONE-tested (RC test 4) |
| Tidio alerts reach an inbox (info@, DNS, Mailgun) | #4, #7, #9 "Info email account not receiving test leads" | OPEN: Bill forwarding + Barracuda allow-list asked Oct 12, no reply seen |
| Territory list from Todd to Bill | #4 "Territory list: needed from Todd" | OPEN (see 1.2 reconcile item) |
| Negative keywords / anti-ICP sheet-resin filter | #9 "add negative keyword triggers" ; Todd to share list | OPEN (no evidence the list arrived) |
| Gravity Forms spam filter update | #9 "Zach has approval to implement" | DONE-untested (not verified this session) |

### Phase 1.2 (delivery, enrichment, 4-hour metric, baseline; $4,500)

| Item | Source + quote | Status |
|---|---|---|
| Reliable delivery Tidio to Zapier to Sugar | #11 "reliable delivery verified" | DONE-tested in sandbox (RC 32/32; zap 376827315 v9) |
| No duplicates: update existing lead | #12 "update existing lead or create net new" | DONE-tested (RC tests 2, 7) |
| Empty-email guard (Roger Lamarre overwrite) | memory, Oct 12 email item 4 | DONE-tested per RC repeat-visitor test; Todd's own test chat (Oct 12 ask) not seen |
| ZoomInfo enrichment: job title | #12 "Enriches contacts via Zoom (job title, company, address)" | DONE-tested (RC test 6, "Lead Captain") |
| ZoomInfo enrichment: industry | #12, DoD doc | DONE-untested: industry not seen in Sugar read |
| ZoomInfo enrichment: business email (original DoD wording) | DoD Aug 18 "business EMAIL not yet demonstrated" | NEEDS-DECISION: verify or re-baseline to title/industry in writing |
| ZoomInfo plan tier, lookups, contact | #11 "Zach needs Todd to confirm what the ZoomInfo plan includes" | OPEN (Todd owes) |
| Unrecognized state flagged and routed | (RC) | DONE-tested (RC test 5, v9) |
| 4-hour metric or documented proxy | #3, #9 "4-hour lead response rule"; #13 "4-hour follow-up nudge" | NEEDS-DECISION: name the proxy in writing; 4-hour reminder not observed |
| 5-minute new-lead reminder | #13 "5-minute Zapier email fires" | DONE-tested before v9; DONE-untested at chatbot@ since v9 |
| Who gets alerts (Bill vs reps vs Todd) | #12 misrouted "forwarded to Bill"; #14 "lead alert emails should route to Bill" | NEEDS-DECISION partly settled: Bill gets unmatched; rep-facing alert still an open decision (RC known limits) |
| Unassigned-lead fallback (catch-all to Bill, digest) | #11 "Route all unassigned leads to Bill as catch-all" | OPEN: decided in principle (#12, #14), not built or tested in prod |
| Reconcile territory list with Bill (6 states no rep) | #11 "Todd to reconcile the territory list with Bill" | OPEN (Todd owes) |
| Sugar handoff docs ZIP from Bill | #8, #11 "Zip all documentation from the W Service build" | OPEN (Todd owes) |
| Chat transcript / Lyro synopsis into Sugar lead | #11 "pipe the raw transcript or AI blurb into the Sugar lead notes"; #12 | DONE-untested at best: RC says transcript note not checked; memory says Task C unbuilt. Treat as OPEN until shown |
| Lead status "dead" instead of "new" | #13 "Status field showing leads as dead" | DONE-untested (root cause was the dedup overwrite; RC creates show new leads, status not cited) |
| Fields landing in description, not mapped | #13 "Captured fields landing in description area" | DONE-tested for names, state, phone, company (RC test 1) |
| Swap lead assignment off Zach's email | #13 "Swap lead assignment email to Todd's account" | DONE-untested (v9 reminder to chatbot@; owner mapping in prod not tested) |
| Chatbot lead source in prod Sugar | #12, #13, #14 "Added Chatbot lead source to production SugarCRM" | DONE (on Oct 12 call, Todd did it live) |
| Zapier paid plan | #14 "Zapier Professional plan upgraded (annual)" | DONE (Oct 12) |
| chatbot@prlresins.com Sugar user + password | #14 "email verification pending" | DONE user created; password OPEN (Todd to set, Oct 12 email item 1) |
| Swap Zapier from sandbox to prod Sugar | #12, #13, #14 | OPEN (Part 2) |
| Install Tidio plugin on live WordPress | #12, #13 "Install Tidio plugin in WordPress" | OPEN (Part 2; confirm what is on prod today) |
| Live end-to-end trace on prod (three test chats) | #14 "trace a lead end-to-end live"; Oct 12 email | OPEN |
| Todd UAT sign-off on the RC | RC notes "Not yet given" | OPEN |
| Todd's own e2e test with his account assigned | #11 "Assign Todd's PRL account in sandbox" | DONE-tested in sandbox (RC tests 6, 7 used Todd's email) |
| Baseline: volume, close rate, deal size by region and source | DoD Aug 18 "NOT STARTED"; #11 "24-month pull baseline confirmed" | NEEDS-DECISION: notes conflict; confirm whether the Sep 1 scorecard counts as the baseline |
| Welcome copy: remove "spec" | #13 "remove spec from the welcome message" | DONE-untested (not verified) |
| Pick active flow (capture-first vs AI-forward) | #13 "Lead Capture AI Forward may be the better active flow" | DONE: flow 7752845 active per RC; Todd has not confirmed the choice |
| Post-call reference of active configs | #13 Zach to send | DONE (Sep 17 recap email sent per memory) |
| Todd's Loom on chatbot copy | #13 "Record a Loom with observations" | OPEN (never recorded, per memory) |

### Later / out of scope for 1.2

| Item | Source | Phase |
|---|---|---|
| Web forms to Sugar (1.2-A, invoice NYQRTJPQ-0004, $2,070) | DoD Aug 18; dep map | 1.2-A, payment-gated, not built |
| Knowledge base enrichment, persona and exclusion rules | #13 "Phase 1.3 scope covers knowledge base enrichment" | 1.3 |
| Smarter lead recognition, attribution analytics | #11 | 1.3 |
| Radius routing via ZoomInfo zip | #13 | 1.3+ |
| SEM landing-page flows, paid pages | #9, #12 | 1.4 / 1.5 |
| Weekly digest, follow-up email to lead with spec sheets | #13 | later |
| Product guide as indexed pages, IDES datasheets | #4, #8 | later |
| Lighthouse / GTM cleanup | #1 | original Phase 1 proposal, not pursued |
| Decision receipts tenant for PRL | #7 "Tabled for now" | later |
| Rep voice capture, digests to reps | #3 | Phase 2 ideas |
| Tidio HTML email styling | #12 | Phase 2 |

## 3. Payment terms and what "1.2 done" means

- Phase 1 fee proposed at $1,500 (call #3, Jul 20). Two invoices sent Aug 12: NYQRTJPQ-0002 (Phase 1.1) and NYQRTJPQ-0003 (Phase 1.2). Amounts are in the PDFs, not read here.
- 1.2 was priced at $4,500, about 20 hours (call #7; close-loop math). The Aug 18 DoD doc records the $4,500 as paid.
- Call #8 mentions about $18K in total, possibly split by card. No document found that ties $18K to specific phases.
- Invoice NYQRTJPQ-0004 ($2,070, 1.2-A web forms) was open on Aug 18 and Sep 17. Not re-checked in Stripe.
- No email or note found that names a "final payment" due when 1.2 is done. If the final payment is NYQRTJPQ-0004, note it pays for web forms work that has not been built. NEEDS-DECISION: Zach to confirm which invoice is the final payment, and check Stripe.
- 1.2 Definition of Done (Aug 18 DoD, 4 committed items): reliable delivery; enrichment ("ZoomInfo business email fills"); four-hour metric as a recorded value or documented proxy; baseline. Call #11 (Sep 1) called 1.2 "closed and capped", but Todd then chose go-live first (no 1.3 until live), and the Oct 12 call was titled "Wrapping up Phase 1.2". In practice Todd treats 1.2 as done when the chatbot runs on the live site into prod Sugar.

## 4. To close 1.2

1. Todd: set the chatbot@ Sugar password; Bill: Tidio forwarding; Jorge: Barracuda allow-list (Oct 12 email, items 1 to 3).
2. Part 2 call: connect Zapier to prod Sugar, set routing (matched to rep, rest to Bill), install or confirm Tidio on live WordPress, run three live test chats, read each back in prod Sugar.
3. On that call, confirm the 5-minute and 4-hour reminders arrive, and decide the rep-facing alert.
4. Write down the 4-hour proxy and the enrichment re-baseline (title, industry, not business email) and get Todd's yes.
5. Decide transcript note: build and show it, or move it to 1.3 in writing.
6. Settle the baseline item: point to the Sep 1 scorecard or move it.
7. Get Todd's written UAT sign-off on the RC, then name the invoice for the final payment and send it.
