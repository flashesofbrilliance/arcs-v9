# PRL 1.1 — Land the Plane · One-Shot Pickup Prompt
> Self-contained. A fresh session executes from this file alone. SSOT for client-facing truth:
> Google Drive folder "PRL Resins — Chatbot" — primary doc: "POVs & Approaches (shared SSOT)"
> (id `1Uj0CgUmN5NfRBYrRV77RbcKuzDsBCJWMJK6dE9gLuyM`) + "Open Questions + Call Outcomes"
> (id `1fjGqDLohB7z8pcqyd7KNmkaf0ipoOWPYbmgWo2-_MC8`). Engineering truth: this file + the DEWY
> ledger (`_STATE/2026-08-1*.dewy.json` in worktree prl-sugarcrm-sandbox-ready-7198dd).
> Scope law (Todd's guardrail #3, verbatim from SSOT): **"Don't overcomplicate. The point is:
> chatbot → leads into Sugar → geo-route to the 8 reps."**

## MISSION
Finish 1.1: every real chat on the PRL site creates a complete, `Chatbot`-tagged, geo-routed
Lead in SugarCRM — proven in sandbox, then promoted to prod in Todd's window. Put 1.2 in motion
(enrichment = reuse ZoomInfo; four-hour metric = baseline done, needs Todd's data session) and
stage 1.3 (SEM Onramp flows already drafted in Tidio). Do NOT expand scope.

## STATE OF TRUTH (all live-verified 2026-08-17; trust but re-verify cheaply on pickup)
| Fact | Evidence |
|---|---|
| Sugar **Create Lead proven E2E in sandbox** via Zapier MCP (`zapier.chatbot` conn `028b8e8b…`, numeric 65592413) | Created lead `155bc286-9a45…`: `lead_source=Chatbot`, `location_c=CT` → **auto-routed to rep Lynn Winston**, created_by "Chatbot Integration"; verified; deleted |
| **Required fields** (create rejects without) | `account_name, first_name, last_name, lead_source, location_c, phone_work` |
| **`location_c` is a strict ABBREVIATION enum** (CT/TX/NJ + intl values) | Create-spec pull + successful CT create. **Corrects SSOT §2.4** which said "full state names" — push this correction to the Drive doc |
| Email → `email1`; inquiry text → `description` | Spec + test create |
| **Prod picklist lacks "Chatbot"**; sandbox has it | `/Leads/enum/lead_source` diff prod vs sandbox. THE cutover gate — 100% silent rejection if missed |
| Tidio (PRO): Flows Actions palette has native **"Send to Zapier"** node (+ raw "API call" backup) | Visually confirmed in PRL account |
| Tidio flow landscape | **"PRL Resins - Lead Capture"** = LIVE (28 runs, 43% engagement, **flow-level Leads acquired = 0**, has unactivated draft edits); **"AI Handoff (lead delivery bridge)"** = Draft, collects lead via Ask-a-question chain, **ends with NO delivery node**; 5 "SEM Onramp" drafts = future 1.4; "Lead Capture (AI-forward)" = separate draft |
| Zapier plan = **Pro** ($29.99/mo, 750 tasks; ~95 used) | Billing screenshot. Task cost is a non-constraint (~20/mo at current volume) |
| Todd's flow-design answers (Drive doc "Zach and Todd") | Phone: **ask for it** · "Chatbot": **separate dropdown** · test lead: **approved** |
| Chatbot is **staging-only by design** (wfaprlredev26); goes to prod at cutover | Confirmed; intentional |
| Routing reality | Abbrev `location_c` → territory rep; "Other"-source firehose (blank email, full state names) → all to Bill (167/928); reps get "Web Site" leads |

## PRODUCT REC (the lean cut — no new tools, no code, no upgrades)
**Pipe:** Tidio live flow → **Send to Zapier** node (fires at lead-capture completion) → one Zap:
trigger = Tidio Send-to-Zapier → **Formatter/lookup step: state answer → abbreviation enum**
(the only transform) → action = SugarCRM Create Record (Leads) with the field map above →
**sandbox connection first**, repoint to prod at cutover. Rejected alternatives (for the record):
owned Vercel webhook (code to maintain; task cost doesn't bind), Zapier SDK (beta = rug-pull risk
for a client's production pipe). Delivery-layer retry = Zapier's native task history + replay —
that IS the "retry + visible task history" the SSOT promises; build nothing extra.

## IMPLEMENTATION PLAN (each leg gated; file/score a DEWY receipt per leg)
1. **Map the live flow** (human-or-copilot in Tidio UI; agent cannot do this alone): export or
   walk "PRL Resins - Lead Capture"; confirm it collects first/last/company/phone/email/state +
   resin need into contact properties; resolve the unactivated draft edits (keep or discard —
   ask Zach, don't guess). Decision on record: **rebuild-clean bias** — if the tangle resists
   mapping in <1hr, graft delivery onto the clean "AI Handoff" draft instead and reconcile later.
2. **Wire delivery (sandbox)**: add Send-to-Zapier node at every capture-complete terminus; build
   the Zap (trigger → state-abbrev transform → Sugar create on connection 65592413). Run ONE
   tagged test chat (`ARCSTEST` / `zach.harris+chatbote2e@gmail.com`).
3. **Record the evidence** (the client-facing proof): screenshot each hop — Tidio convo → Zapier
   task history run → Sugar sandbox record w/ fields + routing — assemble "1.1 E2E Evidence"
   artifact; delete test lead after capture.
4. **Promote script** (repo, reusable): pre-flight checks as code — prod picklist has "Chatbot"
   (Studio step, 2 min, do at cutover), Zap repointed to prod conn `0259be25…` (19157430),
   Tidio widget on prod site, one verified prod create in Todd's window, kill switch = Tidio
   flow toggle. Output: PASS/FAIL punch list, not prose.
5. **1.2 in motion (parallel, no build):** enrichment = **reuse ZoomInfo bidirectional** (SSOT
   decision, no new spend — verify it's actually syncing before claiming it); four-hour metric
   baseline already captured (928 leads · ~10/mo · 42% stuck "New") — needs Todd's SM/reports
   session to instrument; keep §6 scoped-API-permission list moving with Sugar (case 589806) in
   parallel — do NOT block on it.

## ORCHESTRATION & TOKEN BUDGET (the ballet — cheapest capable tier per job)
- **Main loop (this model):** judgment, client-facing writing, fate-gated stitches, UI copilot.
- **Delegate cheap+mechanical** (Explore/low-effort subagents, ~≤30k tokens total): Sugar
  read-sweeps, enum/count diffs, evidence-file assembly, receipt bookkeeping.
- **MCP directly (no subagent):** all Sugar reads/writes (proven), Gmail drafts, Drive SSOT
  read/update. **Human-only:** Tidio + Zapier UI config, WordPress login, anything reCAPTCHA.
- **Budget cap for the whole 1.1 landing: ~150k tokens.** If exceeding, stop and re-plan —
  overspend signals scope creep, which violates guardrail #3.
- **Reusable "done" workflow:** per leg — ex-ante receipt → build → evidence (screenshot/API
  read) → score expected-vs-actual → update Drive SSOT + prl.arcs.care + runbook (60fbdf00) +
  vendor roadmap (fb2878f6) **as a coupled pair, always in sync**. Done = receipt scored GREEN
  with evidence attached, not "it should work."

## VALIDATION PUNCH LIST (run in order; each is PASS/FAIL)
- [ ] Live-flow map complete: every capture path ends in Send-to-Zapier; required fields all collected
- [ ] Test chat → Zapier task fires (task history shows run, no error)
- [ ] Sandbox Lead created: all 6 required fields + email1 + description populated correctly
- [ ] `lead_source = Chatbot`; `location_c` = correct abbreviation from a full-state-name answer (transform works)
- [ ] Auto-routed to correct territory rep (not Bill, unless state unmapped → confirm default)
- [ ] Negative test: chat with no phone → flow requires it (Todd: "ask for it"); no partial lead
- [ ] Negative test: unmapped/intl state → defined default, not silent failure
- [ ] Test lead deleted; zero residue (`ARCSTEST` search = 0)
- [ ] Cutover pre-flight: prod picklist has "Chatbot" BEFORE Zap repoint; one verified prod create in Todd's window; kill switch tested
- [ ] Evidence artifact assembled + Drive SSOT §2.4 corrected (abbreviations) + artifacts synced

## ISSUES & OBSERVATIONS LEDGER (carry forward; do not re-derive)
1. **Gravity Forms fills do NOT reach Sugar and do NOT email** — proven (ARCSTEST submits: 0 GF→Sugar
   leads after days; notify emails were Barracuda-quarantined, Jorge released + allow-listed the old
   sender as a band-aid). Real "Web Site" leads arrive via **Sugar native Web-to-Lead** (webtolead_email1
   fingerprint). Rec: subtract GF from the CRM path; route via native Web-to-Lead. **Josh-gated; a
   deviation from 1.1–1.5 scope — park unless Todd prioritizes.**
2. **Website intake is dead**: 0 new website-source leads since Jul 27; newest lead of any source Aug 7.
3. **Staging reCAPTCHA is domain-locked to prlresins.com** → staging forms unsubmittable (Josh task:
   register staging domain or disable on staging).
4. **Mailgun ownership resolved by elimination (Aug 17 texts): NOT Jorge, NOT Todd** ("never heard
   of it before Josh mentioned it") → almost certainly **Josh/WFA**. Route the send-only-key ask to
   Josh. The staged Todd nudge (`r2265883981846174104`) asks Todd for it — STALE, do not send.
5. **Comms state (Aug 17, via text):** Todd re-engaged — week is shot, will try to arrange a
   Jorge+Josh call, **deputized Zach to "just talk to Josh"** directly, and **asked for a one-page
   what-we've-done doc** (Zach committed to refreshing last week's Drive docs). Josh re-engaged
   same morning (SMTP guidance + call offer). Sugar case 589806 open (§6 list = our action).
6. **SSOT tensions to reconcile in Drive doc:** location_c full-names→abbreviations (evidence wins);
   "scoped API key not admin" vs. the working zapier.chatbot admin user (flag to Sugar/PS, migrate to
   scoped key when provisioned); clean-slate sandbox track vs. working prlresinstest (build on what
   works, don't block).
7. Minor: prod picklist label mismaps ("Public Relations" → value "Lead Forensics"); 42% of all leads
   stuck status "New" (the four-hour-metric pain, quantified); Tidio dashboard "Leads acquired 16"
   (Lyro/overall) vs Flows-level 0 — both true, different counters.
8. **Deck lineages reconciled (Aug 17, commit 7b400ed):** public/todd-call.html (the prl.arcs.care
   root default) had forked at Aug 10 and REGRESSED fixes — it showed the Stripe pay-1.2 button
   post-payment + the stale reCAPTCHA claim. Reconciled onto one SSOT (_ARTIFACTS/prl-roadmap-deck.html),
   deployed to BOTH public/todd-call.html and public/prl-chatbot.html. Rule: any deck edit deploys to
   both files, and the vendor artifact rebuilds via build-vendor-deck.sh. Also added: the 1.2 optional
   tributary card (web form rebuilt on Sugar's native web-to-lead + de-SPOF access) — scoped B/B/W with
   Todd on the call, no price stated.
9. **De-SPOF directive (Zach, Aug 17):** eliminate single-person gates on mail testing — ask Jorge ONCE
   for a PRL-owned test mailbox (e.g. leads-test@) Zach can access, and route the Mailgun send-only key
   to PRL ownership; after that, deliverability tests self-serve. Fold the mailbox ask into the Jorge
   loop-closer; the key ask into the Josh thread.
10. **Todd approvals + facts (Aug 17 evening emails):** (a) Web-forms plan (subtract GF → Sugar native
    Web-to-Lead) — Todd: "Makes total sense. And yes, it's how the leads from the PPC landing pages are
    supposed to work." → APPROVED in principle, AND pins B/B/W unknown #1: the working W2L pipe is fed by
    the Unbounce/PPC landing pages (matches the "Unbounce – Sabic" campaign lead fingerprint). Best case
    = point the contact form at the same mechanism the landing pages use. (b) Negative-keyword list
    started (thread "Negative Key Word"): first entry **"sheet resin" / plastic sheets — PRL makes
    pellets, not sheets**. Todd will send more. Feeds BOTH the anti-ICP lead screen (chatbot + form) and
    the 1.4 SEM negative keywords. Keep a running list; suggest a shared Drive doc when the list grows.
11. **Never reproduce credentials** found in the "Zach and Todd" Drive doc (plaintext passwords live
   there — flag to Todd to rotate + move to a manager; do not copy them anywhere).

## PICKUP (verbatim kickoff for a fresh session)
"Read `_ARTIFACTS/prl-11-oneshot-pickup.md` in the chatbot worktree. Re-verify the four cheap
facts (sandbox conn alive via a 1-record Leads read; prod picklist still lacks Chatbot; Tidio
flows unchanged; Gmail: any Todd/Josh replies). Then execute the implementation plan legs in
order with me as UI copilot for Tidio/Zapier. File the ex-ante receipt before wiring. Budget cap
150k tokens. Scope law: chatbot → leads into Sugar → geo-route to 8 reps. Nothing else."
