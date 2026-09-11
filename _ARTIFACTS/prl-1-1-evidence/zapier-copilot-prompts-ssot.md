# Zapier Co-pilot Prompts — SSOT (2026-08-19)

> The complete, consolidated meta-prompt queue for the Zapier co-pilot. Paste the PREAMBLE once
> per co-pilot session, then task blocks as needed. Run **Task 1 first** (real data at risk);
> everything else is order-independent. Bring each task's output back to Claude Code for one
> cheap independent verification read. Related: `2026-08-18-zapier-copilot-brief.md` (the
> executed bar-raiser brief), `2026-08-18-4hr-nudge-zapier-brief.md` (superseded by Task 3),
> `2026-08-18-1.2A-web-forms-acceptance-tests.md` (payment-gated, becomes the 1.2-A prompt).

---

## PREAMBLE (paste once, first)

```
Operating rules for all tasks this session:
- SANDBOX ONLY: SugarCRM connection stays on prlresinstest.sugarondemand.com (auth 65663180). Never touch prlresins.sugarondemand.com (production).
- Preserve existing Zaps — edit, don't delete/recreate. Live pipeline = Zap 376827315 (Tidio → Code → ZoomInfo → dedup search → Paths A/B). Old series_376761228 stays OFF.
- For every claimed fix, prove it: run the step test AND read the resulting Sugar record back via API, report the record ID and actual field values. A step-test's own echo is not proof.
- Report what was actually done vs. assumed. If something turned out to be a non-issue, say so plainly.
```

---

## TASK 1 — CRITICAL: empty-email dedup guard + record repair

```
Bug (confirmed in live data): a submission with an empty email made Step "Search for existing lead by email" match an arbitrary record, and Path A updated a REAL 2021 lead: Roger A Lamarre / ROBE, id ea77a7d2-1b0b-11ec-83a4-06ab610ac1b0. Its description now ends "— Updated via Chatbot" and title/hint_account_industry say "Not specified" — all wrongly written by us.

Do, in order:
1. Add a Filter by Zapier step between the Tidio trigger and the Sugar search: continue ONLY if email exists and is not empty. If email is empty, the run must NOT reach Path A under any condition. Decide and state whether empty-email runs should halt entirely or route to Path B (create with audit note "email missing") — recommend Path B so no lead is lost.
2. Investigate why that run's email was empty despite the flow's email validation — check the trigger's task history raw payload and report what the email field actually contained.
3. Repair the damaged record via Sugar API update (id above): set description="", title="", hint_account_industry="". Read the record back after and paste its field values as proof.
4. Re-test: one step-test with an empty email (must NOT update any record), one with a real email (normal behavior). Report both outcomes with record IDs.
Done = filter live in published Zap + Roger's record clean + both tests reported.
```

---

## TASK 2 — Test-lead cleanup

```
Delete all test leads from the Sugar sandbox so pilot data starts clean. Identify them by: lead_source="Chatbot" AND (email1 in [zach.harris@gmail.com, sawayn.andrew@gislason.net, eldridge.west@yahoo.com] OR account_name starting with lorem-ipsum text like "Vitae nihil" / "Maiores necessitatibus"). Before deleting: list every candidate with id, name, email, date_entered, and WAIT for my confirmation on the list. Do NOT delete anything with lead_source other than "Chatbot". After my yes: delete, then run the same search again and confirm zero remaining. Report the count deleted.
```

---

## TASK 3 — Finish the SLA nudge Zap (376815688)

```
Complete draft Zap 376815688 (Schedule hourly → SugarCRM Find → Email):
1. Add the missing staleness filter: only leads with status="New" AND date_entered older than 4 hours (make the threshold an easily-editable value, not buried logic — it will change).
2. Email step (to zach.harris@gmail.com for now): subject "SLA Alert: [count] stale leads (>4h)", body lists each lead as name / company / assigned rep / age, each with link https://prlresinstest.sugarondemand.com/#Leads/[id] (modern SPA format — verify one link opens before wiring it in).
3. Test with threshold temporarily at 0 hours so existing sandbox leads trip it, verify the email arrives and links work, then set threshold back to 4 and publish.
Done = published, one real email received with working links, threshold at 4.
```

---

## TASK 4 — Rep notification email (replaces Mailgun for now)

```
In Zap 376827315, both paths currently email zach.harris@gmail.com only. Add/repoint the immediate (5-min) notification so it ALSO goes to info@prlresins.com, reply-to info@prlresins.com. Keep Zach's copy. Subject: "New chatbot lead: [name] — [company]". Body: name, company, email, phone, state, job title, industry, link to the Sugar record (same #Leads/[id] format). Then send one test and report: did it arrive at info@prlresins.com's inbox or get quarantined? (PRL runs Barracuda; if quarantined, say so — there's a known allow-list fix on their side, don't try to work around it yourself.) Done = test email's actual fate reported, not assumed.
```

---

## TASK 5 — Baseline data pull (read-only, no Zap changes)

```
Read-only reporting task, no Zap edits: using the SugarCRM connection's API access, pull from the SANDBOX instance:
1. Leads: count by lead_source by month for the last 24 months, plus count by location_c (state).
2. Opportunities (if the module is readable with this connection — if not, say so and stop): count + total amount by month, and whether opportunities link back to a lead/lead_source (report which relationship fields actually exist rather than guessing).
Output everything as CSV-formatted text I can paste into a sheet. Make no writes. If any module or field errors, report the exact error instead of substituting assumptions. This becomes the "baseline report" input — volume/close-rate/deal-size by region and source.
```

---

## TASK 6 — Routing ground-truth re-sweep (pure API, no Zap)

```
Pure API task using the Sugar sandbox connection — no workflow changes. Re-run the territory routing sweep: for each of the 50 US state codes, create a Lead (account_name="ROUTING-SWEEP-TEST", first_name="Sweep", last_name=[state code], lead_source="Chatbot", location_c=[state code], phone_work="555-000-0000"), immediately read back its assigned_user_name, then DELETE the record before moving to the next state. Output a CSV: state, assigned_rep, unassigned(yes/no). Delete-verify at the end: search account_name="ROUTING-SWEEP-TEST" must return zero. This refreshes the Aug-17 finding (~49% mismatch vs the client's territory list) so the eventual Bill call argues from current data. If any create fails, log the state + exact error and continue — don't stop the sweep.
```

---

## TASK 7 — Harden the Code step (state parser) with a built-in test suite

```
Code-step task in Zap 376827315, step "Process State and Name Inputs": add a self-test mode and close known gaps.
1. Edge cases to handle explicitly: leading/trailing whitespace, "N.Y."/"D.C." style punctuation, zip codes (5-digit input → extract nothing, flag parse-failed rather than defaulting silently wrong), "California or Texas" (multi-state → take first match, flag ambiguous=true), non-US ("Toronto", "Ontario" → parse-failed flag, NOT a silent CA).
2. Keep the existing contract: state_code always a valid 2-letter code (CA fallback), state_parse_failed flag, raw input passthrough — downstream mapping depends on these exact output keys, do not rename them.
3. Add a test harness INSIDE the code step (a test_mode input that runs ~20 canned cases and returns pass/fail per case), run it once, paste the results, then leave test_mode off in the published version.
Done = published step, all ~20 canned cases reported passing, output keys unchanged.
```

---

## TASK 8 — Payload hardening (truncation + defensive defaults)

```
In Zap 376827315, harden field mappings against real-world input, both paths:
1. account_name: truncate to 255 chars before the Sugar step (test data already exceeded this; confirm whether Sugar was silently accepting or truncating, and report which).
2. phone_work: strip everything except digits, +, -, (, ), spaces.
3. Every mapped field: confirm what happens when the Tidio property is missing entirely (not just empty) — does the mapping render a literal placeholder like "376827315__company" into Sugar? Test one run with a deliberately missing property and report what actually lands.
4. Any field that can arrive missing gets an explicit default ("" or a flagged value), never a raw unresolved template string.
Done = republished, the missing-property test result reported with the actual Sugar record values.
```

---

## TASK 9 — Daily unassigned-leads sweep (the routing stopgap, promised on the client status page)

```
New scheduled Zap: daily 7:00 AM America/New_York → SugarCRM search: Leads where assigned_user is empty/unassigned (figure out how the connection expresses "no assigned user" — test it, don't guess; report which filter worked) → email digest to zach.harris@gmail.com AND info@prlresins.com: subject "Unassigned leads: [count]", each lead as name/company/state/source/age + https://prlresinstest.sugarondemand.com/#Leads/[id] link. If zero unassigned, send nothing (no noise). Test by temporarily creating one unassigned lead via API (then delete it), verify the digest fires with it and stays silent without it. This is the safety net for the known routing gaps (6+ states route to nobody) — it must catch what routing drops.
```

---

## TASK 10 — ZoomInfo business-email fill check (answers an open 1.2 acceptance criterion)

```
Diagnostic only. The ZoomInfo enrichment step currently maps jobTitle and industry. Check: does the enrich_contact response also return a business email address for matched contacts, and at what accuracy? Run 3 test enrichments with realistic B2B inputs, paste the relevant response fields. If a business email IS available: propose (don't yet apply) where it should map — noting Sugar's email1 is already used for the visitor's typed email, so it would need a second field (report which email fields exist on the sandbox Leads module via API). If NOT available on this ZoomInfo plan/endpoint, say so plainly — that closes a contract line item as "re-scope needed" rather than leaving it ambiguous.
```

---

## Deliberately NOT prompted
- **1.2-A web-forms Zap** — payment-gated (invoice #NYQRTJPQ-0004 open). When paid, use
  `2026-08-18-1.2A-web-forms-acceptance-tests.md` as the prompt almost verbatim.
- **Anything touching production Sugar** — separately and explicitly gated (enum + auth repoint
  + Bill call + Todd's go).
- Task 2 keeps its human-confirmation gate on purpose — never let the co-pilot skip list-first.
