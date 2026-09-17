# PRL/Todd Chatbot → Zapier → SugarCRM — Internal System Reference

_2026-09-17 · Consolidate-and-refresh, not a rebuild. Every claim below is cited to an existing
doc; nothing here is invented. Sources: `runtime/recoil/generated/prl-lyro/INTEGRATION-DOSSIER.md`
(DOSS, 2026-08-11), `_ARTIFACTS/prl-1-1-evidence/prl-system-ssot.md` (SSOT, 2026-08-18),
`_ARTIFACTS/prl-1-2-close-loop/2026-09-17-phase-systems-dependency-map.md` (PHASE-MAP, 2026-09-17),
`_DECISIONS/ADR-074-prl-sugar-custom-code-collision-surface.md` (ADR-074, 2026-09-01),
`_ARTIFACTS/prl-zap-kit/README.md` + `task3/task4/task7/task8/task9` (ZAP-KIT, verified 2026-08-26).
Ground truth re-verified live this session (2026-09-17) is marked **[LIVE 09-17]**.

Register: internal, blunt, ARCS-side detail fine. Sandbox only throughout
(`prlresinstest.sugarondemand.com`, rest/v11) — production (`prlresins.sugarondemand.com`) is
untouched and explicitly gated (DOSS §C, SSOT §1).

---

## 0. System at a glance

```
WordPress (host) → Tidio flow + Lyro (capture/qualify) → Zapier (transform + retry + dedup)
  → SugarCRM Leads (create/update + route) → ZoomInfo (enrich) → notify (rep alert)
```

Live Zapier state **[LIVE 09-17]**: dedup zap **376827315 ON** (the pipeline) · old series
**376761228 OFF** (prevents double-leads) · SLA draft **376815688 OFF** (still draft) · Gmail
notification zap **OFF** (superseded). This matches intended state — no drift found this session.

---

## 1. Tidio chatbot flow (capture)

**What it is.** The visitor-facing chat widget on the WP staging site that captures a qualified
lead (name/email/phone/company/state + intent), governs what it will answer, and screens
anti-ICP visitors, before handing off to delivery. (DOSS §D2, SSOT §2)

**How it works.** Widget key `nemtpdglmxzbcpmqlqh1gnj3wmgqsxeu` loads on the dev site
(`wfaprlredev26.wpenginepowered.com`) via mu-plugin (DOSS §D1). A flow (built + branded +
activated) greets → establishes intent (A: knows grade/spec · B: help me choose · C: other) →
branches into qualifying questions → captures fields (DOSS §B row 2). All captured values ride as
**session variables**, not Tidio contact properties, specifically to avoid Tidio's contact-property
validation friction (DOSS §D2 interface contract). A deterministic recognizer
(`normalization/normalize.py`) reflects back grade/competitor mentions and an anti-ICP keyword
watcher screens generic inquiries ("sheet") without ever stating a spec/cert/price as fact —
governed answering per `ADR-PRL-001` (Proposed, not yet ratified) (DOSS §D2, §F). The flow then
POSTs via a native Tidio flow **API-call node** (a webhook, on the current plan — no Tidio+ tier
needed for this) to a Zapier Catch Hook (DOSS §B row 3, §D2).

**What could break.**
- Flow-vs-Lyro precedence unverified in-app — if Lyro answers before the flow captures, a lead
  could exit without ever being captured (DOSS §C "Tidio flow-vs-Lyro precedence — to verify").
- The one real backup of the live flow, `backups/live-flow-lead-capture-2026-08-09.json`, is an
  **empty file (0 lines)** — the live flow is not actually backed up; any edit is unrecoverable
  until re-exported (DOSS §D2, §G — flagged twice, unresolved as of DOSS date).
- Lyro has been observed resuming existing conversations instead of restarting the flow (SSOT §1,
  "Known open defects").
- Which flow variant is actually LIVE is itself unresolved — see Open gaps §1 below.

**Dependencies.** WordPress (dev site + mu-plugin injection; prod untouched) (DOSS §D1). Tidio
account tier: Flows+Lyro purchased, **Tidio+ NOT purchased** — this is why delivery goes through a
Catch Hook node rather than a native API integration (PHASE-MAP §1.5). Todd/PRL: negative-keyword
examples for anti-ICP seeding ("owed", DOSS §C).

**How to test.** `normalization/normalize.py` self-test (recognizer), `coverage_sweep.py` (895
competitors × 150 grades × 50 states × punctuation), `full_grid_sweep.py` (150×50×3 = 22,500
invariants), `simulate_lead_e2e.py` (dry-run, prints the exact Sugar payload, no write) — all
DOSS §F, described as already passing at DOSS's 2026-08-11 date. **Honest gap:** flow-vs-Lyro
precedence is explicitly listed as "to verify," not verified (DOSS §C).

---

## 2. Zapier delivery zap "Tidio leads to SugarCRM (Deduplicate + Append)" (376827315)

**What it is.** The single Zap that owns the entire transform + dedup + delivery path: takes the
Tidio Catch Hook payload, cleans/normalizes it, enriches it, checks Sugar for an existing lead by
email, and either updates (Path A) or creates (Path B) a Sugar Lead. (DOSS §D3, SSOT §1 diagram,
ZAP-KIT README)

**How it works.** Pipeline order (SSOT §1 mermaid; ZAP-KIT Step 0 confirms this Zap ID): Tidio
trigger → Code step "Process State and Name Inputs" (name split, state parse, CA fallback +
`state_parse_failed` flag) → ZoomInfo enrich (title + industry, "Not specified" fallback) → Sugar
search by `email1` → **Path A** (found → UPDATE: title/industry/description append) or **Path B**
(not found → CREATE: full field map + audit trail) → notification emails. Dedup is handled
**Zapier-side**, not Sugar-side — Sugar has no native Lead dedup configured (ADR-074 §3). Field
transforms per DOSS §B row 4: `name`→`first_name`/`last_name` (single-word fallback) ·
`phone`→`phone_work` (required) · `company`→`account_name` · `state`→`location_c` via
`resolve_state` · `lead_source="Chatbot"` (literal) · `email`→`email1` (Sugar's Leads module has
no plain `email` column) · `description`=`inquiry_text` + grade/competitor/intent context.
Task 8 (ZAP-KIT, ship-with-notes, adversarially verified 2026-08-26) hardens this further: a
`clean()` helper strips unresolved Tidio `{{property}}` template literals and truncates
`account_name` to 255 chars; two key families exist on purpose — `*_clean` (no invented defaults,
used by Path A so a sparse payload can never overwrite real CRM data) vs `*_for_create` (defaults
like `"Unknown"`/`"Not provided"` applied, used by Path B only, since Sugar requires `last_name`
on create). Task 7 (ZAP-KIT, ship-with-notes) is a drop-in replacement body for the state/name Code
step: normalizes both full state names and 2-letter codes from dirty historical data, keeps the
existing output contract, adds `rep_email` routing output.

**What could break.**
- **The Roger Lamarre incident (real, already happened):** an empty-email payload let the dedup
  search false-match an unrelated existing lead, corrupting it with placeholder text
  ("Not specified", "Updated via Chatbot" suffix) (SSOT §1 "Known open defects," ZAP-KIT README
  "Open items," ADR-074 §3 confirms dedup is Zapier-side with no native Sugar dedup). Task 8's
  Edit-1/Routing-guard section is the fix: route by **Path rules**, not a blocking top-level
  Filter (a hard Filter before Find Record would halt the whole run and silently drop the lead —
  the opposite failure). Path A fires only when Find Record returned a match AND `email_clean` is
  non-empty; everything else goes to Path B create.
- Path A on a blank mapped field: unverified whether Sugar's update action skips vs clears the
  field on an empty value — Task 8 flags this as a must-verify-before-shipping item; if it clears,
  optional fields must be dropped from Path A's mapping entirely (ZAP-KIT task8, "Path A caveat").
- `account_name` over 255 chars has occurred in real test data (ZAP-KIT task4, task8, task9) —
  must be truncated, not just assumed short.
- Guarding on the raw Tidio email instead of `email_clean` re-opens the `{{email}}` template hole
  (a literal unresolved template string is non-empty raw, so a naive raw-email check would let it
  through) (ZAP-KIT task8 Edit 1a comment).
- Sugar's `lead_source` field is a dropdown (`lead_source_dom`) — `"Chatbot"` must exist in that
  dropdown list in the sandbox or the REST write succeeds but the UI/dropdown filters won't show
  it (ZAP-KIT task8 Edit 2 table). Per PHASE-MAP §1.2-A, `"Chatbot"` is **sandbox-only valid**;
  `"Web Site"` (for the forms leg) is valid in both sandbox and prod.

**Dependencies.** Zapier account + the Sugar sandbox connection (already used, no new creds)
(DOSS §H). ZoomInfo credentials for the enrich step (see §7). Sandbox API token for read-back
verification (ZAP-KIT task8 Step 0 curl). No Sugar Professional Services purchase required — the
custom-code collision check (ADR-074) confirmed none of PRL's five installed custom packages touch
the Leads module.

**How to test.** Dedup-zap acceptance tests are described but **flagged pending, never recorded
complete** — see Open gaps §2. Task 8's verification checklist (V1–V8) is the concrete procedure:
curl read-backs against the sandbox confirming truncation (V1), phone sanitization (V2), no
unresolved `{{...}}` templates (V3), correct defaults/routing fields (V4), the empty-email path
landing in Path B with zero modified old records (V5), the state/name Code contract intact (V6),
then test-lead cleanup (V7) and one eyeball spot-check (V8). SSOT §3 sequence diagram documents one
verified real run (Lead `435cee66…`: name split ✓, `location_c=CT` ✓, audit ✓) — that is evidence
the happy path works, not that the hardened Task 7/8 edits have been proven end-to-end since.

---

## 3. SugarCRM lead object + field mapping (incl. the description field)

**What it is.** The system of record — a Sugar Lead row created or updated per visitor, plus
territory routing metadata. (DOSS §D4, ADR-074)

**How it works.** Six required Sugar fields: `first_name, last_name, location_c, lead_source,
account_name, phone_work` (plus `email1, title, industry` used in practice) (per this session's
ground truth and DOSS §B contract invariants). `location_c` must be a valid 2-letter code or the
`state_parse_failed` flag fires and a description note is appended — **never a silent wrong
value** (ZAP-KIT task8 Edit 2, "State not confirmed by visitor" appended text). Empty email routes
to Path B create, never Path A update (the Roger Lamarre false-match guard, §2 above). The
`description` field is composed in the Code step (`description_final`), not left to raw mapping,
because Zapier field mappings can't express conditionals (ZAP-KIT task8 Edit 1a) — the composed
text is `inquiry_text` (or the literal `"Submitted via chatbot; transcript unavailable"` fallback)
plus the state-parse-failure note when applicable.

**EMPIRICAL FINDING (this session, 09-17):** the 9/1 sandbox lead's `description` field contains
the literal string **"Chatbot Lead"** — not a transcript, not `inquiry_text`, not the composed
`description_final` text described above. This means the transcript-carrying mapping described in
DOSS/ZAP-KIT is **not what's actually landing in the field today**, at least for that record. The
transcript-enrichment component (§9 below, Task C) is confirmed unbuilt — this is direct evidence
of that gap, not just an absence of a build doc.

Sugar schema audit (DOSS §D4, mechanism confirmed live 2026-08-07): 106 Leads columns
(`leads-columns.tsv`), 92/100 sampled records assigned to Bill Galla, team Global (no record
privacy), leads have **no plain `email` column** (must write `email1`), native **Hint** enrichment
fields exist (`hint_account_*`) — open question whether PRL's license includes them (§7).

**What could break.**
- The `description` field carrying a placeholder string instead of real conversation content means
  any downstream process (rep review, SLA digest context, reporting) that assumes `description`
  = transcript is working from wrong data today.
- ADR-074 confirms the custom-code layer (`wBenchmarkTargetTemplate`, `OrderHistorySetRLI`,
  `OpenOrdersSetProduct`, `SalesNumbersSetAccountRel`, `wGlobalSearch`) sits entirely on the
  revenue/opportunity side, not Leads — so lead work is additive-only, no collision (ADR-074
  Finding + Decision #1). Residual gate: confirm no SugarBPM Process Definition or Web Logic Hook
  touches Lead create/dedup — Module Loader only covers packages, not workflows (~10-min sandbox
  read, not yet closed per ADR-074 §3).
- $43.7M / 48% of opportunities have no recorded `lead_source` (baseline finding,
  `_ARTIFACTS/prl-baseline/`) — structurally caused by the custom revenue-attribution hooks plus
  the never-solved 2022 lead→closed-won linkage (Bill's own words), not a hygiene gap (ADR-074
  belief-change table).

**Dependencies.** Sandbox access (Todd-approved, provisioned as a scoped API key — not admin —
per the Aug-11 call: field types + geographic routing policies only) (DOSS §0). Kim Borst's (Sugar
Director PS) build design docs for schema context, since the original builders left Sugar (ADR-074
Context). No Sugar Professional Services purchase needed for current lead-work scope (ADR-074
Decision #1).

**How to test.** Direct curl read-back against the sandbox REST API (ZAP-KIT task8 V1–V4 pattern);
this session's empirical description-field check is exactly this kind of direct read, and it's how
the "Chatbot Lead" literal was caught — read the record, don't trust the Zap's self-reported
output (PHASE-MAP §1.2-A acceptance criteria makes this explicit as a principle: "independently
read back from Sugar, not trusting the Zap's self-reported output").

---

## 4. Routing / territory assignment (+ the central-inbox interim)

**What it is.** Assigning each new/updated Lead to the correct rep by state, so the right person
calls back — with an interim fallback for states with no coverage. (DOSS §B row 7, ZAP-KIT task4)

**How it works.** `location_c` maps to a rep via a routing table verified against a live 2026-08-26
50-state sandbox sweep (ZAP-KIT task4): Bill Galla (AL, AZ, NV) · Steve Fabrizius (AR, CO, KS, MO,
NE, OK, TX) · Lynn Winston (CA, CT, MA, ME, NH, OR, RI, VT, WA) · Howard Altman (FL, NJ) ·
Christian Cassel (GA, KY, MD, NC, SC, TN, VA) · Kathy Brown (IL, WI) · Tim Mulcahy (IN, MI) ·
Dan Damas (IA, MN, ND) · Robert Spano (NY, OH, PA). **12 states route to nobody**: AK, DE, HI, ID,
LA, MS, MT, NM, SD, UT, WV, WY (ZAP-KIT task4, task9). Distribution-only states and the NY/PA
sub-region split default to the Sales Manager/Bill; a human converts Lead→Opportunity manually
(DOSS §B row 7). SSOT §2 notes a **49% territory mismatch** found in an earlier routing sweep as a
still-open journey failure mode, with a stopgap sweep + a pending Bill call as the fix path.

**What could break.** Any of the 12 uncovered-state leads get created with no `assigned_user_id`
and, absent the Task 9 sweep (§6 below), sit invisible indefinitely. Rep-email addresses
themselves are **not stored in the doc** — they must be pulled from the sandbox user records and
confirmed with Todd before any live send (ZAP-KIT task4, "Rep email addresses are not in this doc").

**Dependencies.** Bill Galla confirmation of the territory map ("delivered once; confirm current" —
DOSS §C, still listed as a gate, not resolved). Todd approval of each rep's actual email address
before first live send (ZAP-KIT task4 Test item).

**How to test.** ZAP-KIT task4 test protocol: one live test matching an existing lead (Path A), one
creating a new lead (Path B), one unassigned-state test (e.g. WY — confirms email still reaches
info@ + Zach with no rep address), one garbage-state-input test (confirms `State parse failed:
true` shows plainly rather than presenting the CA fallback as fact).

---

## 5. Notifications (rep alert email)

**What it is.** An email fired after either Sugar path (Update or Create) succeeds, alerting the
assigned rep — plus info@ and Zach — that a new/updated lead exists. (ZAP-KIT task4)

**How it works.** Task 4 (ship-with-notes, verified 2026-08-26) adds an "Email by Zapier" step
after the Sugar action in each path. To: `[rep_email], info@prlresins.com, zach.harris@gmail.com`.
Reply-To: `info@prlresins.com`. Subject: `New chatbot lead: [name] - [company_display]`, where
`company_display` is a new Code-step output (raw account name, trimmed to 80 chars, or literal
`"Not provided"` when blank — computed upstream because Zapier field mapping can't express a blank
fallback). Body shows both `state_code` AND the raw state-as-typed plus `state_parse_failed`, so a
CA fallback is never presented as fact (ZAP-KIT task4, "Why both state lines"). Unassigned states
fall back to info@ + Zach only, never a guessed rep (ZAP-KIT task4 rep_email mapping note).

**What could break.**
- **Email by Zapier always sends from `noreply@zapiermail.com`** (not configurable), and PRL runs
  Barracuda — this sender address has never been seen by PRL's filter, so quarantine is the
  expected default outcome, not an edge case (ZAP-KIT task4 "Barracuda protocol": "Expect
  quarantine to be likely"). The allow-list fix is entirely on PRL's IT side.
- Email by Zapier is rate-limited to ~10/hour — fine for pilot volume, but will queue/drop if
  volume grows; the fix then is moving to a real mail provider (ZAP-KIT task4, README).
- **Transport is itself undecided** — see §Open gaps #4; the actually-built path is Zapier's
  native Email action, not Mailgun, contradicting an older engagement-memory claim that Mailgun is
  "in the live stack" (DOSS §D6 "Discrepancy to resolve").

**Dependencies.** Rep email addresses pulled from sandbox user records + confirmed by Todd (ZAP-KIT
task4). PRL/Todd IT: Barracuda allow-list entry for `noreply@zapiermail.com` (or the
`zapiermail.com` domain) (ZAP-KIT task4, README "Open items").

**How to test.** ZAP-KIT task4 test list (§4 above reuses the same protocol) plus explicitly:
"send one test, report the email's ACTUAL fate (inbox vs quarantine)" — this is a HONEST-test
instruction, not a pass/fail assumption; the doc expects quarantine and wants it recorded plainly,
not worked around.

---

## 6. The SLA nudge + unassigned-sweep zaps (task3/task9)

**What it is.** Two safety-net Zaps: an hourly SLA nudge for leads stuck in status `New` past a
threshold (task3, targets draft Zap **376815688**), and a daily 7am digest of leads with no
assigned rep at all (task9, a new Zap, not yet created).

**How it works.**
- **Task 3 (SLA nudge, draft Zap 376815688):** Schedule (hourly, weekends included) → Code
  ("CONFIG: SLA threshold hours", an editable Input Data field so no code-reading is needed to
  change the threshold, default N=4) → Sugar Find Records (`status=New`) → a digest-builder Code
  step (3b) that computes stale age per lead, with an explicit misalignment guard (comma-joined
  field arrays can shift if a name/company itself contains a comma — same failure family as the
  Roger Lamarre incident, flagged and handled by attaching a "(details unverified)" warning rather
  than guessing) → Filter (`stale_count > 0`) → Email to **`zach.harris@gmail.com` only** for the
  pilot (rep/info@ routing is explicitly deferred to later, "after the pilot proves clean").
- **Task 9 (unassigned sweep, new Zap):** Schedule (daily 7am America/New_York) → search Leads for
  empty `assigned_user_id` (two candidate filter forms — empty string vs `$is_null` — with an
  explicit probe procedure to determine which the sandbox actually needs, defaulting to an OR of
  both) → Filter (`count > 0`, deliberately silent on zero so a "nothing to report" email doesn't
  train people to ignore it) → digest email to `zach.harris@gmail.com` + `info@prlresins.com`.
  Read-only — never writes to Sugar (ZAP-KIT task9).

**What could break.**
- Task3: Zapier Find-Record steps may not support a relative "older than X hours" filter — the
  sheet has a Plan A (native filter) / Plan B (fetch all `New`, age-compare in Code) fallback
  built in, and expects Plan B in practice ("expected"). Find-Record result caps (often 3–10
  records) can silently undercount if the sandbox has more stale leads than the step returns
  (ZAP-KIT task3 "Known edges").
- Task9: Schedule by Zapier's daily trigger has no per-trigger timezone field — it inherits the
  Zapier account profile timezone, which must be independently confirmed as America/New_York
  before publishing, not assumed (ZAP-KIT task9, README "Open items" — this was a correction made
  during verification, not an original assumption).
- Both Zaps are **neither published** — task3 is still literally Zap 376815688 in draft state
  **[LIVE 09-17: confirmed OFF]**; task9 doesn't exist as a built Zap yet, only as a spec.

**Dependencies.** Sandbox Sugar connection (shared with the main pipeline). Zapier account profile
timezone setting (task9). None of PRL/Todd's dependencies are named for these two — they are
internal safety nets, not company-side asks, except that the eventual production version of either
"waits for the gated cutover" (task9, "Out of scope").

**How to test.** Task3: drop `threshold_hours` to 0, step through the Zap in the editor, confirm
email delivery + one working record link, then restore to 4 and re-test, then Publish. Task9: seed
one known-unassigned test lead via direct API create (with `assigned_user_id` explicitly set to
empty string, since Sugar can silently auto-assign the API user on create otherwise), run the
probe to determine the correct filter, verify the digest fires and then verify silence after
deleting the test lead. **Honest state: neither has been run through this test protocol and
flipped to published** — see Open gaps §3.

---

## 7. Enrichment (ZoomInfo / title+industry)

**What it is.** Filling in job title, industry, and (historically) business email for leads that
arrive without them, so a lead is reachable and scoreable. (DOSS §D5, SSOT §1 diagram)

**How it works.** The Zap calls ZoomInfo's enrichment API between the Code (state/name) step and
the Sugar dedup search (SSOT §1 mermaid: `C1 --> ZI[ZoomInfo enrich]`), returning title + industry
or a `"Not specified"` fallback (superseded per Task 8's cleaner default of blank, not the literal
string, to avoid re-polluting records — ZAP-KIT task8 Edit 2 table: "'Not specified' literals
polluted the Lamarre record; blank is honest"). The Aug-11 call reframed this: the ZoomInfo
integration was already **bidirectionally wired** before this engagement (DOSS §0 call outcomes),
and Sugar has its own **native "Hint" fields** (`hint_account_size/industry/location/founded_year`)
that may already cover firmographics — the open decision is whether PRL's license includes Hint,
in which case ZoomInfo would only be needed to close the `email1` gap, not for title/industry at
all (DOSS §D5).

**What could break.** Nothing is independently verified here — DOSS explicitly says "No dedicated
build artifact" and "Verification: None — unwired" for the Hint-vs-ZoomInfo decision (DOSS §D5).
The choice affects ongoing per-lead cost (ZoomInfo is paid; Hint may already be owned) and this
decision was never closed.

**Dependencies.** Todd: confirm whether PRL's Sugar license includes Hint before paying for
ZoomInfo's firmographic coverage; ZoomInfo contact is owed by Todd only if the decision lands on
paid ZoomInfo (DOSS §C, §D5).

**How to test.** No harness exists for this component specifically — see Open gaps §5. The
closest verification is the same read-back pattern as §3 (curl the Lead record's `title`/
`industry` fields and check against what ZoomInfo returned vs what Hint would have produced).

---

## 8. Lyro AI layer (1.5, off-until-proven)

**What it is.** Tidio's conversational-AI layer as a *second* path alongside the rigid capture
flow — meant to handle "help me choose" / ambiguous inquiries with judgment, while the flow stays
the fast rigid path for visitors who already know what they want. Explicitly ordered to run
**after** the flow, never nested inside it (PHASE-MAP §1.5, CLIENT-CARD framing quoted there).

**How it works.** Guidance-prompt configuration only (a prompt guide, not a knowledge-source
document dump — proprietary forms/matrix data deliberately stay off Tidio's servers)
(PHASE-MAP §1.5 LYRO §3a/3b). Knowledge sources allowed now: Product Selection Guide,
product/markets/policies/quality pages (already public). Explicitly withheld: the internal
Good/Better/Best matrix, the QATF001 form, anything on the internal server. Two new flows are
specced but require activation care: `build_ai_handoff()` (9 nodes) so a Lyro-only conversation
still reaches Sugar, and `build_full_ai()` (22 nodes) implementing the "rigid where speed wins, AI
where judgment wins" split — only "Help me choose" and "Something else" route to AI; "I know what I
need" and "call me" stay rigid (PHASE-MAP §1.5). Governed-answering carries over: never state a
spec/cert/price as fact (`ADR-PRL-001`, still Proposed).

**What could break.**
- `build_ai_handoff`'s trigger is currently defaulted to `onFirstVisit` in Tidio, which will
  collide with the main flow's own first-visit trigger — must be fixed in the Tidio UI **before**
  activating (PHASE-MAP §1.5, "must fix... before activating").
- Two product-mechanics questions are unresolved and gate everything: can Lyro trigger a flow
  directly (vs only steering via quick-reply), and can Lyro write contact properties directly (a
  possible second delivery route bypassing Tidio+ entirely)? Both unconfirmed (PHASE-MAP §1.5,
  LYRO §4 items 1–2). Per this session's ground-truth constraint: `build_full_ai` (the AI-forward
  comparison flow) and "Help me choose" **must NOT activate until handoff is verified** — getting
  this wrong makes "Help me choose" a silent lead-loss path (PHASE-MAP §1.5 point 5).
- No named owner (PRL or ARCS) for ongoing Lyro knowledge-curation or live-answer review after
  go-live — the eval harness is a one-time go-live gate in the corpus, not a maintenance cadence
  (PHASE-MAP §1.5, flagged explicitly as "the one phase where [ongoing maintenance need] is real"
  and "a genuine gap").

**Dependencies.** Tidio: Flows+Lyro tier already approved by Todd (10% lifetime discount); Tidio+
tier (needed for AI-initiated Sugar delivery without the flow-handoff workaround) **NOT
purchased** — a decision + $ approval needed if that path is ever wanted (PHASE-MAP §1.5).
Zapier/Sugar delivery path is unchanged and reused, not rebuilt for this layer.

**How to test.** Explicit order of operations (PHASE-MAP §1.5 quoting LYRO §6): (1) prove
Tidio→Zapier hop with Catch Hook only, no Sugar action, no client approval needed → (2) turn Lyro
on with guidance prompt + public knowledge sources only → (3) import the AI handoff flow, set its
real trigger, test that a Lyro conversation actually reaches it → (4) wire the Sugar action only
once Todd approves a test lead. Also gated by the same DOSS layered `TEST-PLAN-go-live.md` (L0–L4)
and the Lyro safety eval set (SPEC/SPECRISK/XREF/SCOPE/PUSHBACK/AMBIGUITY/GROUNDED, "≥3× per case")
plus `firewall-test-prompts.md` anti-fabrication prompts (DOSS §F). **Honest state: off, by
design, until the handoff mechanism above is verified — not yet done.**

---

## 9. The chat-transcript enrichment (Task C, NOT built)

**What it is.** The still-unbuilt piece that would carry the actual chat transcript (or a
meaningful summary of it) into the Sugar Lead's `description` field, so a rep sees what the
visitor actually said, not a placeholder.

**How it works — currently: it doesn't.** There is no dedicated build doc for this in the
reconciled corpus. DOSS/ZAP-KIT describe a composed `description_final` field intended to carry
`inquiry_text` (+ grade/competitor/intent context) or a stated fallback string
(`"Submitted via chatbot; transcript unavailable"`) — but this session's direct empirical check of
a real sandbox record (the 9/1 lead) found the `description` field held the literal string
**"Chatbot Lead"**, which is neither `inquiry_text` nor the documented fallback text. That mismatch
is the concrete evidence that whatever mapping is actually live today is not the transcript-
carrying mapping described in the source docs, and that this component (transcript capture and
delivery into Sugar) has not been finalized or wired end-to-end.

**What could break.** Reps reviewing leads today get zero conversational context beyond structured
fields (name/email/phone/company/state) — the qualitative "what did they actually need" signal
that the chatbot itself gathered during the flow is being thrown away before it reaches Sugar.
Any future fix must decide: full transcript vs. summary vs. structured intent tags, and must not
silently overwrite the existing `description_final` composition logic that other parts of the
system (the state-parse-failure note) already depend on.

**Dependencies.** Tidio's session-variable model (would need to expose the transcript, or a
built-in summary, as a webhook-accessible field — unconfirmed whether Tidio's API-call node payload
includes full conversation history today). The existing Zapier Code step's `description_final`
composition point is the natural integration seam if/when this is built.

**How to test.** No test exists because nothing is built. The honest verification step available
right now is exactly what this session did: pull a real sandbox Lead record and read the
`description` field directly — do not trust that the documented mapping is what's actually
running.

---

## Open gaps / unverified

1. **Which Tidio flow is actually LIVE is unresolved.** The docs recommend a 5-field
   capture-first flow (DOSS/BUILD), but the 8-27 receipt evidence shows an AI-forward flow live.
   **NOT verified this session** — needs a direct in-app check of which flow variant is currently
   active and its trigger precedence vs Lyro.
2. **Dedup zap (376827315) acceptance tests are flagged pending, never recorded complete.** Task 8's
   V1–V8 verification checklist exists and is runnable, but no completed run-log confirms all
   eight checks passed against current live state.
3. **task3 (SLA nudge), task9 (unassigned sweep), task4 (rep notification), and task8 (payload
   hardening) have never been flipped from draft/spec to published-and-live**, despite all four
   being marked "ship-with-notes" (adversarially verified 2026-08-26) in ZAP-KIT. Live Zapier
   state this session confirms 376815688 (task3's target) is still OFF.
4. **Mailgun vs. Zapier-Gmail (Email by Zapier) notification transport is undecided.** DOSS §D6
   flags this discrepancy explicitly: engagement memory names Mailgun as a secured, wired asset,
   but the repo has no Mailgun build and the actually-designed/built path uses Zapier's native
   Email action. This must be resolved before any further notification wiring, independent of the
   separate info@ DNS fix (which is proceeding on its own track via Jorge + Tidio).
5. **Enrichment ownership (Sugar Hint vs. ZoomInfo) is open.** DOSS §D5: no dedicated build
   artifact, no verification, unwired. Whether PRL's license includes Hint changes whether ongoing
   ZoomInfo spend is even necessary for firmographics (title/industry); ZoomInfo may still be
   needed for the `email1` gap regardless.
6. **Lyro handoff mechanism is unverified — this gates `build_full_ai`.** Two open product-
   mechanics questions (can Lyro trigger a flow directly; can Lyro write contact properties
   directly) must be answered before "Help me choose" is allowed to activate, per PHASE-MAP §1.5
   and this session's explicit constraint that `build_full_ai`/"Help me choose" stay off until
   handoff is verified.
