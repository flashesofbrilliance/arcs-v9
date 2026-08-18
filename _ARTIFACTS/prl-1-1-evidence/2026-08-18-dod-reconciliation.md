# 1.1 / 1.2 Definition-of-Done Reconciliation — 2026-08-18

Scored against OUR OWN committed gates (`TEST-PLAN-go-live.md` Layer 3 = the 1.1 DoD;
`SPRINT-2-1.2-kickoff.md` acceptance criteria = the 1.2 DoD), not the Zapier co-pilot's
narrower test checklist. Purpose: no gate gets dropped silently — each is met, waived
in writing, or explicitly re-baselined.

## 1.1 DoD scorecard

| Gate | Verdict | Evidence / disposition |
|---|---|---|
| Real conversation → Sugar lead, all 6 required fields, `lead_source=Chatbot` | ✅ MET | Lead `435cee66-9b40-11f1-9cd7-02309379545d` (2026-08-18), independently read. |
| Every branch (A/B/C) tested | 🔁 RE-BASELINED | Written against live Flow A's 3-way topology. The wired flow is the linear AI-Handoff bridge — the A/B/C requirement no longer maps 1:1. New bar: one real conversation per distinct path in the flow AS WIRED. Still owed: enumerate the wired flow's actual paths and test each once. |
| Multiple states incl. a Distribution state + a split state (NY/PA) | ⏳ OPEN | Only CT tested. Cheap to close: two more staging chats (e.g. CA + NY). |
| Correct territory assignee on the test lead | ⏳ OPEN | Never fetched `assigned_user_name` on the real test lead. Close on next verification read (free). NOTE: "correct" is itself provisional until the Bill call resolves the 49% CSV mismatch — verify assignment happened and record who, don't adjudicate correctness yet. |
| Mailgun rep-notification + prospect autoresponder | ⚠️ WAIVED-FOR-NOW (needs Todd's ack) | Not built in the current Zap architecture. Current emails are internal reminders to Zach, not rep notifications, and there is no prospect autoresponder. This is a real committed feature, not paperwork — either build it as part of closing 1.1 or get Todd's explicit written deferral. Do not mark 1.1 done to Todd without one of the two. |
| Delete test leads afterward | ⏳ OPEN | ~7 test leads in sandbox (3x zach.harris@gmail.com, 3-4x synthetic Faker records). One cleanup pass owed. |
| Layer 0 regression green | ✅ MET | 22,500/22,500 at merge time. Re-run before any future dictionary/flow change. |
| Layer 1 Lyro eval (80 cases x3, zero critical) | ❓ UNKNOWN | No record it ran against the CURRENTLY-live flow/guidance. Decide: run it, or waive with rationale (e.g. flow's answering surface unchanged since last green run — only true if verified). |
| Layer 2 capture-branch tests | 🔁 RE-BASELINED | Same topology change as A/B/C above; folds into the "test each wired path" bar. |

**Stale-doc correction owed:** `TEST-PLAN-go-live.md` Layer 3 step 2 says `location_c` = FULL
state name. Disproved 2026-08-17 (abbreviations; the full-name claim was a sampling artifact).
Correct the plan so nobody follows it literally.

## 1.2 DoD scorecard (4 committed line items, $4,500 paid)

| Criterion | Verdict | Disposition |
|---|---|---|
| Reliable delivery | ✅ MET | Same evidence as 1.1 row 1; plus dedup/enrichment Zap 376827315 published (pending its own two real-chat tests). |
| Enrichment — "ZoomInfo business email fills" | 🟡 PARTIAL | Title + industry now wire in via ZoomInfo step. The criterion's named fill — business EMAIL — not yet demonstrated on any record. Close by verifying one enriched lead shows a ZoomInfo-sourced email (or re-baseline the criterion to title/industry with a written note, since the chatbot already captures email directly and the business-email fill may be redundant — flag to Todd either way). |
| Four-hour metric — recorded value OR documented proxy | 🟡 PARTIAL | No recorded time-to-first-touch. Per-lead 4h reminder email exists (fixed delay, fires regardless of rep action) + incomplete scheduled SLA Zap 376815688. The plan itself allows "the chosen proxy documented" — DECISION OWED: name the proxy in writing (e.g. "4h reminder email per lead + hourly stale-lead sweep") and this criterion closes cheaply. Todd confirmed 4h is a soft rule, which supports the proxy path. |
| Baseline (volume/close-rate/deal-size by region+source) | ❌ NOT STARTED | Requires the CRM Data Reality session with real Sugar data. Untouched. This is the largest genuinely-unbuilt 1.2 item. |

## Also open (cross-cutting, tracked elsewhere)
- Zap 376827315's own acceptance tests (2 real staging chats: new-email create, existing-email dedup) — pending; verify old Zap series_376761228 is actually OFF in the Zaps list first (triple-lead evidence showed both firing earlier today; the co-pilot's "it's gone" claim was based on the new Zap's ZDL, which cannot prove another Zap's status).
- Rep routing ground truth — gated on Bill call (unchanged).
- 1.2-A web forms — payment-gated (invoice #NYQRTJPQ-0004 open as of today).
- Phase discrepancy: client-facing receipt puts enrichment in 1.2; internal sprint doc says 1.3 and calls ZoomInfo "already paid, unused." Reconcile which phase owns it before any Todd-facing "1.2 done" claim.

## What "1.1/1.2 honestly done" requires from here (cheapest order)
1. Fetch `assigned_user_name` on lead 435cee66 (free, next read).
2. Run the 2 pending Zap acceptance chats + 2 extra states (4 staging chats total, ~10 min human time).
3. Delete all test leads (one write pass).
4. Write the 4-hour proxy decision paragraph; correct the stale location_c line in the test plan.
5. Decide + document: Mailgun rep-notification (build vs Todd-ack'd deferral) and Layer 1 eval (run vs waive).
6. Baseline session with Todd — the one real remaining build/analysis item for 1.2.
