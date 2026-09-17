# PRL/Todd — Phase Systems + Dependency Map (INTERNAL, 1.2-A / 1.3 / 1.4 / 1.5)

_2026-09-17 · Internal source-of-truth for later client-facing phase cards. Reconciled from the
corpus below only — no invented scope. Register: blunt, ARCS-side detail OK, not for Todd's eyes
as-is._

**Corpus reconciled:**
`2026-07-30-todd-tidio-triggers-and-picker-v1.md` (TRIG) ·
`2026-07-30-todd-personas-routing-persona-v1.md` (PERS) ·
`2026-08-03-todd-lyro-ai-layer-v2.md` (LYRO) ·
`prl-lyro/INTEGRATION-DOSSIER.md` (DOSS) ·
`2026-07-30-todd-tidio-build-sheet-v1.md` (BUILD) ·
`2026-08-18-1.2-web-forms-addendum-implementation-spec.md` (1.2A-SPEC) ·
`2026-08-18-1.2A-web-forms-acceptance-tests.md` (1.2A-TEST) ·
`public/todd-call.html` (CLIENT-CARD, what Todd has already been told)

---

## 1.2-A — Web forms → Sugar delivery

| | |
|---|---|
| **Systems touched** | WordPress (Gravity Forms — confirm still the plugin in use, don't assume) · Gravity Forms Webhooks add-on (may need install/license — the one real cost unknown) · Zapier (same Catch Hook / Zap pattern as the chatbot leg, can be one Zap serving both triggers) · SugarCRM Leads (same Create Record action, same 6-field map) |
| **ARCS-side build work** | Confirm form plugin + confirm Webhooks add-on availability (1.2A-SPEC step 1–2) · configure webhook step pointing at the existing chatbot Catch Hook URL (no-code if add-on present) · map WP form fields → the same 6 payload keys (`account_name, first_name, last_name, lead_source, location_c, phone_work, email1`), reusing the proven Code-step fixes (name-split-on-first-space; `location_c` fallback + sibling `description` audit field on parse failure) from the chatbot leg — do not re-litigate these, re-apply (1.2A-TEST) · hardcode `lead_source="Web Site"` (valid in both sandbox AND prod, unlike "Chatbot" which is sandbox-only) (1.2A-SPEC, 1.2A-TEST) |
| **PRL (company-side) dependencies** | **One-time:** payment on invoice #NYQRTJPQ-0004 ($2,070) — hard gate, no live-webhook wiring until it clears (1.2A-TEST) · confirm/approve if new form fields (company/state) must be added — visible scope change, flag before building, do not silently add (1.2A-SPEC, 1.2A-TEST) · approve Gravity Forms Webhooks add-on purchase if not already licensed (cost/timeline unknown) · Todd sign-off before same-day build start (1.2A-SPEC intent). No training-agent/ongoing-maintenance dependency named for this phase in the corpus — it is a one-time delivery-wiring addendum, not a knowledge-curation phase. |
| **Acceptance criteria** | Same DoD discipline as the chatbot leg: (1) step-level Zapier test-run (necessary, NOT sufficient) → (2) real (non-synthetic) form submission on WP staging with realistic data, independently read back from Sugar (not trusting the Zap's self-reported output) — confirms name split, `location_c` real-or-flagged, `lead_source: "Web Site"`, `account_name` doesn't truncate on long names → (3) duplicate-submission check (double-click resubmit) — new test not needed on the chatbot leg, is needed here (1.2A-TEST). "Done" = one real Sugar Lead ID + a plain statement of tested-vs-assumed, independently verified. |
| **Provenance** | 1.2A-SPEC, 1.2A-TEST |

---

## 1.3 — Smarter lead recognition

| | |
|---|---|
| **Systems touched** | Tidio (flow-level keyword recognition, no new integration) · existing PRL data already in CRM/site (grade dictionary, competitor cross-reference) — reused, not new systems |
| **ARCS-side build work** | Corpus is thin on 1.3 as a standalone dated spec — it is largely **already built and shipped** under the 1.1/1.2 umbrella, not a distinct future build: `normalization/normalize.py` deterministic recognizer (grade + competitor + state), `grade-dictionary.json` (150 grades), `competitor-to-prl.json` (895 keys), `field-normalization.json`, keyword-trigger jump straight into Branch A pre-filled (BUILD "Resin recognition" section; DOSS §D2/§F — `coverage_sweep.py` 895 competitors × 150 grades × 50 states, `full_grid_sweep.py` 22,500 invariants). The **client-card framing of "1.3"** (CLIENT-CARD: "buyers name specific grades... teaches the bot to recognize... never guesses a spec") describes work whose engine already exists per DOSS; 1.3-as-priced-phase reads as productizing/extending recognition rather than net-new build — **GAP: no dated spec file draws the line between what's already shipped under 1.1 verification and what net-new work $4,000/~18hrs (CLIENT-CARD receipt template) actually buys.** Grade-string full autocomplete (`FAMILY-MODIFIER+COLOR-SUFFIX` parsing) is explicitly flagged as fast-follow, not v1 (BUILD) — this is the most likely candidate for actual 1.3 scope but it is not confirmed as such anywhere. |
| **PRL (company-side) dependencies** | Territory map confirmation with Bill ("delivered once; confirm current") (DOSS §C) · negative-keyword/ICP examples from Todd (anti-ICP seeding, "owed") (DOSS §C) · no training-agent component named — recognition is deterministic/rule-based (lookup tables), explicitly NOT AI-guessed (BUILD, LYRO, DOSS anti-fabrication through-line), so no ongoing curation loop is implied by the corpus for 1.3 itself. |
| **Acceptance criteria** | Reuse the L0 deterministic-layer gate from DOSS §F/`TEST-PLAN-go-live.md`: `normalize.py` self-test, `coverage_sweep.py`, `full_grid_sweep.py` (22,500 invariants) — these already exist and pass today per DOSS, so 1.3 acceptance should be defined as "extends coverage of X" with its own delta sweep, not a fresh harness. |
| **Provenance** | BUILD ("Resin recognition" + "Grade-string autocomplete... fast-follow"), DOSS §D2/§F/§G, CLIENT-CARD (price/estimate only, no technical detail) |

---

## 1.4 — Paid landing pages / SEM (Unbounce)

| | |
|---|---|
| **Systems touched** | Unbounce (landing pages; Tidio JS snippet added via Script Manager — Unbounce is NOT covered by the WordPress plugin, separate install) (TRIG) · Tidio (URL-scoped Condition-node triggers) · GTM/analytics (implied by CLIENT-CARD's `gad_source` UTM handling; not detailed as a build task anywhere in corpus — see cross-cutting gap below) |
| **ARCS-side build work** | Add Tidio snippet to Unbounce via Script Manager (prerequisite, TRIG) · build per-page URL Condition-trigger chain: `Trigger: page view` → `Condition: URL contains <slug>` → tailored bot greeting → drop into pre-tagged branch (competitor / product family) (TRIG page→greeting map: sabic-alternatives, lexan/makrolon/calibre, ultem, noryl, valox) · build the generic `gad_source`-present fallback trigger for any paid-search visitor not matching a specific page (TRIG) · build order: specific-competitor triggers first (highest intent), generic fallback last · every SEM open keeps "Just have someone call me" escape hatch (TRIG) · add `competitor` and `product_family` attributes (TRIG) · Branch A product picker built from the real `/products/` taxonomy (PC, ABS, ASA, PEI, PPX, Nylon 6/66, PBT, blends, Structural Foam, Profile Extrusion) with deep links to live product-page permalinks — **must verify live URL shape on prlresins.com before wiring** (TRIG) |
| **PRL (company-side) dependencies** | **One-time:** confirm live permalink slugs/URL shape on prlresins.com before deep-linking (TRIG) · Unbounce admin access to add the Script Manager snippet · confirm current SEM/Unbounce campaign URL structure matches the slug map assumed in TRIG. No ongoing/training-agent dependency named — this is deterministic URL-matching, not AI, so no curation loop. |
| **Acceptance criteria** | No dedicated acceptance-test doc exists for 1.4 in this corpus (unlike 1.2-A) — **GAP**: reuse the pattern from 1.2A-TEST/DOSS §F (step-level test insufficient, need a real visit-through-each-tagged-URL test confirming correct greeting + correct branch pre-fill + correct attribute tag, verified by reading the resulting Tidio session vars / Sugar payload, not just watching the flow preview). Verify each specific-competitor URL pattern plus the generic `gad_source` fallback before go-live (TRIG ordering note implies this is the test order too). |
| **Provenance** | TRIG (both parts), CLIENT-CARD (price $6,000, "already in motion... ad spend lands on a funnel that works") |

---

## 1.5 — AI assistant (Lyro layer)

| | |
|---|---|
| **Systems touched** | Tidio Lyro AI (new tier: **Tidio+**, ~$359/mo base — PRL bought Flows+Lyro but explicitly did NOT buy Tidio+) (LYRO §1) · Tidio Flows (existing, unchanged — `build_full` remains live) (LYRO §5) · SugarCRM (delivery still only via flow webhook, not via Lyro directly, on current plan) (LYRO §1–2) · Zapier (unchanged delivery path, reused) |
| **ARCS-side build work** | Guidance-prompt configuration (prompt-guide, NOT knowledge-source upload — proprietary forms/matrix stay off Tidio's servers) (LYRO §3a/3b, verbatim prompt text in LYRO) · knowledge sources: safe-to-add now = Product Selection Guide, product/markets/policies/quality pages (all already public); do-not-upload = internal Good/Better/Best matrix, QATF001 form, anything on the internal server (LYRO §3a) · conversation-starter buttons (4 drafted) (LYRO §3c) · new flow `build_ai_handoff()` (9 nodes, `--flow ai`) so a Lyro-only conversation still reaches Sugar (LYRO §5) · new comparison flow `build_full_ai()` (22 nodes, `--flow full-ai`) implementing the "rigid where speed wins, AI where judgment wins" split — only "Help me choose" and "Something else" route to AI; "I know what I need" and "call me" stay rigid (LYRO §4b) · **must fix `build_ai_handoff` trigger in Tidio UI before activating** — currently defaulted to `onFirstVisit`, which will collide with the main flow (LYRO §4, item 1) · governed-answering rule set carried over: never state a spec/cert/price as fact, always hand off (LYRO prompt body; DOSS ADR-PRL-001, Proposed) |
| **PRL (company-side) dependencies** | **One-time:** Todd already approved the Tidio account upgrade to Flows+Lyro (10% lifetime discount) — Tidio+ tier NOT purchased, so a decision (and $ approval) is needed if AI-initiated Sugar delivery is ever wanted without the flow-handoff workaround (LYRO §1) · verify with Tidio support whether Lyro can trigger a flow directly or only steer via quick-reply, and whether Lyro can write contact properties directly (a possible second delivery route bypassing Tidio+ entirely) — both unconfirmed, must resolve before shipping (LYRO §4, items 1–2) · **ongoing / training-agent component: YES, and this is the one phase where it's real.** The knowledge base is deliberately curated (safe public pages only, prompt-guided rather than document-dump) and the corpus explicitly flags an accuracy/safety eval loop (`prl_lyro_eval.py`, `firewall-test-prompts.md`) as pre-go-live and re-runnable (DOSS §F) — **but no owner is named for who reviews Lyro's live answers over time, updates the guidance prompt as products/policies change, or re-runs the eval set periodically once shipped.** This is a genuine gap: the corpus treats the eval harness as a one-time go-live gate, not an ongoing maintenance cadence, and never assigns a PRL-side (or ARCS-side) owner for post-launch AI-answer review. Phone-required policy in the handoff flow tracks Sugar's live data (`phone_work` populated 100/100) — if Todd wants to relax it, must change in all three flow builders at once (LYRO §4, item 3). |
| **Acceptance criteria** | Order of operations given explicitly (LYRO §6): (1) prove Tidio→Zapier hop with Catch Hook only, no Sugar action, no client approval needed → (2) turn Lyro on with guidance prompt + public knowledge sources only → (3) import AI handoff flow, set its real trigger, test a Lyro conversation actually reaches it → (4) wire the Sugar action only once Todd approves a test lead. Also gated by DOSS's layered TEST-PLAN-go-live.md (L0–L4) and the Lyro safety eval set (SPEC/SPECRISK/XREF/SCOPE/PUSHBACK/AMBIGUITY/GROUNDED cases, "≥3× per case") plus `firewall-test-prompts.md` anti-fabrication prompts (DOSS §F). CLIENT-CARD frames this correctly to Todd: "it runs after them, never nested inside them... structured lead capture always goes first." |
| **Provenance** | LYRO (all sections), DOSS §D2/§F/§G (eval harness), CLIENT-CARD (price $3,500, ordering rationale, "runs after flows" constraint) |

---

## Cross-cutting: analytics + site-tagging (GTM / UTM / attribution)

**Owns it:** primarily **1.4**. TRIG's SEM triggers already key off `gad_source` (a GTM/Google Ads
UTM-style parameter) being present in the URL as the fallback trigger condition — that is the only
place in the reconciled corpus where per-traffic-channel tagging is operationalized. No dedicated
GTM-tag-plan or analytics-build document exists anywhere in the corpus.

**The gap it's meant to close:** CLIENT-CARD's 1.2 baseline finding — **$43.7M of opportunities
(48% of the total) have no recorded `lead_source`** — is the named business case for why source
attribution matters, but that finding is a *diagnostic* from the 1.2 baseline pull, not a GTM build.
The chatbot's own `lead_source` stamping (`"Chatbot"` sandbox-only / `"Web Site"` prod-valid per
1.2A-TEST) closes the gap only for chatbot- and form-sourced leads; it does not retroactively
attribute the $43.7M of historical opportunities, and it does not itself distinguish *which*
paid-traffic channel/source drove a given chatbot lead beyond the coarse `gad_source`-present check.

**GAP TO FLAG:** the corpus never specifies a GTM tag plan, a UTM parameter schema beyond
`gad_source`, or how per-channel-source lead recognition (e.g., distinguishing a Google Ads SABIC
campaign visitor from an organic-search or email-campaign visitor) would be captured as a
structured field and pushed into Sugar for reporting. 1.4's `competitor`/`product_family` tags
(TRIG) give content-level attribution but not channel-level attribution. If per-channel lead
scoring/reporting is an actual deliverable of 1.4 (as CLIENT-CARD's framing implies — "ad spend
lands on a funnel that works"), it needs its own build spec; none currently exists.

---

## Summary of biggest per-phase dependencies (5 lines)

1. **1.2-A** is blocked hard on Todd's payment (invoice #NYQRTJPQ-0004) and on confirming the Gravity Forms Webhooks add-on is actually licensed — the one real cost unknown.
2. **1.3** has almost no dated build spec of its own; the recognition engine it's sold as building already exists and is verified (DOSS), so the real net-new scope is unclear — likely just the "fast-follow" grade-string autocomplete, unconfirmed.
3. **1.4** depends on PRL confirming live Unbounce/product-page URL slugs before any deep link is wired, and has no acceptance-test document at all (every other phase does).
4. **1.5** is the only phase with a genuine ongoing-maintenance need — curating Lyro's knowledge sources and reviewing its live answers over time — but the corpus assigns no owner (PRL or ARCS) for that cadence post-launch.
5. **1.5** also has two unresolved product-mechanics questions (can Lyro trigger a flow directly / write contact properties) that must be answered before it ships, since the wrong answer makes "Help me choose" a silent lead-loss path.

**Real corpus gaps to flag (not invented, genuinely silent):**
- No GTM/UTM tag plan or channel-attribution schema beyond the single `gad_source` presence check.
- No named owner/cadence for ongoing Lyro knowledge-curation or answer review after go-live.
- No dated 1.3-specific build spec distinguishing already-shipped recognition work from net-new 1.3 scope.
- No acceptance-test document for 1.4 (1.2-A and the chatbot leg both have one; 1.4 does not).
