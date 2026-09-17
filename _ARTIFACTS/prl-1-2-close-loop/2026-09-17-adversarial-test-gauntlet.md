# PRL/Todd Chatbot→Zapier→Sugar — Internal Adversarial Test Gauntlet

_2026-09-17 · Internal, blunt. Sources: `2026-09-17-prl-system-reference.md` (SYSREF),
`public/prl-status-runbook.html` #tests (CLIENT-TESTS), `2026-09-17-phase-systems-dependency-map.md`
(PHASE-MAP). Live-verified claims tagged **[live-verified 2026-09-17]**._

## 1. Cross-platform lead-flow map

| Channel | Hop | Status | Evidence |
|---|---|---|---|
| Chatbot | Tidio widget → flow capture | **unverified which variant is live** | SYSREF §1, Open gap #1: docs describe 5-field capture-first flow, but 8/27 receipt showed AI-forward flow live |
| Chatbot | Tidio → Zapier Catch Hook | works (at least once) | **[live-verified 2026-09-17]** dedup zap 376827315 ON; Zap History: "Tidio leads to SugarCRM" ran SUCCESSFUL 2026-09-01 (7 tasks) |
| Chatbot | Zapier transform/dedup → Sugar | **delayed/held today** | **[live-verified 2026-09-17]** a 2026-09-17 2:40pm run on the same zap shows "Delayed"; Zapier flags 1 held Zap run — unresolved, open forensic item |
| Chatbot | Sugar → transcript enrichment | **unbuilt** | EMPIRICAL (SYSREF §3): 9/1 lead's `description` = literal "Chatbot Lead", not `inquiry_text`/composed text — Task C confirmed unbuilt |
| Chatbot | Sugar → rep routing | partial (35 states) / **unassigned (12 states)** | SYSREF §4: 12 states (AK DE HI ID LA MS MT NM SD UT WV WY) route to nobody; task9 sweep unbuilt |
| Chatbot | Sugar action → notification | **quarantine-likely, unverified delivered** | SYSREF §5: sender `noreply@zapiermail.com`, Barracuda will likely quarantine until PRL IT allow-lists it |
| Web-form (1.2-A) | WP form → Zapier → Sugar | **not yet wired** | PHASE-MAP §1.2-A: hard-gated on invoice #NYQRTJPQ-0004 payment; Webhooks add-on licensing unconfirmed |
| Lyro AI (1.5) | Tidio Lyro → handoff flow → Sugar | **off, must stay off** | SYSREF §8: `build_ai_handoff` trigger collision unfixed; Lyro-triggers-flow / Lyro-writes-properties both unconfirmed — activating risks silent lead-loss |
| Safety nets (task3/task9) | Schedule → Sugar → digest email | **not published** | **[live-verified 2026-09-17]** SLA nudge zap 376815688 confirmed OFF; task9 sweep doesn't exist as a built Zap |

## 2. The gauntlet — stress-testing the 7 client "Tests to try"

| # | Client test | Adversarial angle | Expected pass | Likely failure (known gaps) | Proves / doesn't prove |
|---|---|---|---|---|---|
| 1 | Chat asks for details before anything else | Which flow variant actually loads? If the AI-forward flow is live (Open gap #1), the bot may converse first and never force the 5-field gate | Structured fields requested up front | **Undermined at the root** — SYSREF explicitly flags flow-vs-Lyro precedence and which-flow-is-live as unverified; the client-facing test assumes the capture-first flow is what's deployed | Proves capture UI exists; does NOT prove it's the flow actually serving visitors right now |
| 2 | Complete chat → lead appears in Sugar, tagged "Chatbot" | Zap held/delayed today (live-verified); does a lead submitted right now actually land, or queue silently? | New Sugar lead within minutes | The 9/17 "Delayed" + "1 held Zap run" state means a same-day test could sit in limbo with no visible failure to the tester | Proves the happy path CAN work (9/1 precedent); does NOT prove it works reliably today |
| 3 | Same email twice → updates, no duplicate | Roger Lamarre incident precedent: empty-email payloads previously false-matched an unrelated lead and corrupted it | Second chat updates same lead (Path A) | Task 8's Path-A guard (email_clean non-empty) is a documented fix, but dedup-zap acceptance tests (V1-V8) are "flagged pending, never recorded complete" (SYSREF Open gap #2) — no proof this specific fix is live-verified | Proves basic update path; does NOT prove the false-match class is actually closed against current config |
| 4 | Tricky name ("Dr. Jane Smith Jr.") splits sensibly | Name-split logic is single-word-fallback + first-space split (SYSREF §2) — titles/suffixes are exactly the adversarial case that breaks naive splitting | First/last populated, nothing dropped | High likelihood "Dr." or "Jr." lands in the wrong field or gets dropped; no test case for this specific pattern documented anywhere in DOSS/ZAP-KIT | Proves nothing about the transcript/description gap; isolated to name-parse correctness only |
| 5 | Blank/odd state → flagged, never guessed | `state_parse_failed` flag + description note is the documented behavior | Lead lands with honest flag, no fabricated state | Behavior IS documented and code-level real (ZAP-KIT task8 Edit 2) — best-evidenced of the 7 tests. Residual risk: does the flag actually surface anywhere a rep looks, or only in the raw `description` field a rep may not read carefully | Proves the anti-fabrication design intent; does not prove a rep will ever see/act on the flag |
| 6 | No-rep state → lands in central inbox, not lost | 12 states route to nobody by design | Lead reaches info@ + Zach, not a named rep | Real risk is not this test (which tests the *documented* interim) but whether task9's sweep — meant to catch it if this silently fails — exists at all: it doesn't (unbuilt) | Proves the documented fallback path only; provides zero backstop if the fallback itself fails silently |
| 7 | Notification email arrives, not spam-filtered | Barracuda has never seen `noreply@zapiermail.com`; SYSREF states quarantine is "the expected default outcome, not an edge case" | Email in rep inbox | **This test is expected to fail as designed** until PRL IT allow-lists the sender — testing it without that allow-list just reconfirms a known gap, not a regression | Proves nothing new; the correct action is allow-list first, then retest |

**Meta-finding:** tests 1, 2, and 7 each rest on an unresolved precondition (live flow variant, zap health today, Barracuda allow-list) that the client-facing checklist doesn't surface — a tester could "pass" the visible UI step while the actual pipeline silently fails downstream.

## 3. What's assigned vs not

- **Real rep, 9 territories, 35 states covered**: Galla / Fabrizius / Winston / Altman / Cassel / Brown / Mulcahy / Damas / Spano (SYSREF §4).
- **12 states → no rep, central inbox interim** (info@ + Zach only): AK DE HI ID LA MS MT NM SD UT WV WY. By design, not a bug — but rep email addresses themselves are "not stored in the doc" and must be pulled/confirmed before any live send (SYSREF §4).
- **Unbuilt safety net**: task9 (daily 7am unassigned-lead digest) exists only as a spec, not a built Zap. Until it ships, a lead that falls through routing (bug, not just no-rep-state) has zero automated detection.
- **SLA nudge (task3)**: built, drafted, **[live-verified 2026-09-17: OFF]** — stale `New`-status leads get no automated nudge today.
- **Bill Galla's territory map**: "delivered once; confirm current" — still an open confirmation gate (DOSS §C), not resolved.

## 4. Platform + scope limitations

- **Tidio tier**: Flows+Lyro purchased, Tidio+ NOT purchased → delivery goes through a Catch Hook webhook node, not a native API integration (PHASE-MAP §1.5). This is why Lyro can't deliver to Sugar without the flow-handoff workaround.
- **Barracuda**: sender `noreply@zapiermail.com` (Zapier's native Email action, non-configurable) will likely be quarantined until PRL IT allow-lists it or the domain (SYSREF §5) — a company-side action, not an ARCS fix.
- **Lyro-gating**: `build_full_ai` and "Help me choose" must NOT activate until the handoff mechanism (can Lyro trigger a flow / write contact properties — both unconfirmed) is verified; wrong answer = silent lead-loss (SYSREF §8, PHASE-MAP §1.5 point 5).
- **Transcript gap**: no build exists to carry chat content into Sugar's `description`; empirically the field holds a placeholder ("Chatbot Lead") today, not even the documented fallback string (SYSREF §3, §9).
- **1.2→1.5 dependency gaps** (PHASE-MAP):
  - 1.3 (smarter lead recognition) has no dated build spec — the recognition engine already exists under 1.1; what $4,000/~18hrs of "1.3" actually buys is undefined.
  - 1.4 (Unbounce paid pages) needs PRL to confirm live permalink slugs before deep-linking, and has **no acceptance-test document at all** (unlike every other phase).
  - 1.5 has no named owner (PRL or ARCS) for ongoing Lyro knowledge-curation/answer-review post-launch — the eval harness is a one-time go-live gate, not a maintenance cadence.
  - Analytics/attribution: only a `gad_source`-present check exists; no GTM tag plan or channel-attribution schema, and the $43.7M/48% no-`lead_source` baseline finding is not retroactively fixed by any of this work.

## 5. Highest-risk failures, ranked (BAR/ruin lens)

1. **Silent lead loss via the held/delayed Zap run** — a lead submitted today may sit in a "Delayed" state indefinitely with no automated alert (task9 unbuilt, task3 off). *Mitigation: investigate the 9/17 2:40pm held run now, before any client-facing claim of "it works"; ship task9 before wider testing.*
2. **False-match corruption recurrence (Roger Lamarre class)** — dedup-zap V1–V8 acceptance tests never recorded complete; a real lead could still silently overwrite/corrupt an existing Sugar record. *Mitigation: run the V1–V8 checklist against current live state before any client demo of test #3.*
3. **Lyro "Help me choose" activating prematurely** — both product-mechanics preconditions unconfirmed; if this path goes live before verified, it is a silent lead-loss vector precisely on the highest-intent visitors. *Mitigation: hard gate — do not flip Lyro-to-Sugar on without a completed step-by-step per PHASE-MAP §1.5 order of operations.*
4. **Notification never reaching a human (Barracuda quarantine)** — even a perfectly captured, perfectly routed lead produces no human action if every alert is silently quarantined. *Mitigation: get PRL IT to allow-list `zapiermail.com` before treating notification as tested; test #7 should be treated as a known-fail until then.*
5. **Unassigned-state leads with no rep AND no sweep** — 12 states rely purely on a human noticing info@/Zach's inbox; no automated backstop exists. *Mitigation: ship task9 (already fully specced) before scaling volume.*
6. **Transcript/context loss (lower ruin, real product-quality cost)** — reps get zero qualitative signal from the conversation itself. Not silent-loss-of-lead, but silently degrades every lead's actionability. *Mitigation: scope Task C explicitly rather than let it ride as an assumed "coming next."*

---

**File:** `_ARTIFACTS/prl-1-2-close-loop/2026-09-17-adversarial-test-gauntlet.md` (uncommitted, as requested).
