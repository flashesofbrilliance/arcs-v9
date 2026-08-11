# PRL Resins — Lead-Capture System Integration Dossier

_2026-08-11 · The formal, full-depth single source of truth for the PRL lead-capture system across all six
stack components. Internal (nothing air-gapped). The external Sugar-facing slice is the async Google Doc
(`gdoc:1R_5KrszhixFrxUnDabxGa8gAnqMMhuSJiOwvc3YR1sM`); the belief/version log is
`sugar-alignment-belieflog.jsonl`; the client-safe visual projection is artifact `0e0280a6`._

**Formalization contract.** Every component section below is written to the SAME template — Purpose ·
Prework & provenance (cited by path) · Verification · Interface contract · Current state · Open questions
(keyed to belief-log spans). This makes the depth already done *provable*, not asserted.

**Provenance / branch note (important).** All prework files cited below live on branch
**`claude/chatbot-1-1-jtbd-blockers-edda33`** (HEAD `dc0080f`), NOT in this worktree — paths are relative to
that branch (`git show claude/chatbot-1-1-jtbd-blockers-edda33:<path>`). These three SSOT files
(`INTEGRATION-DOSSIER.md`, `sugar-alignment-belieflog.jsonl`, `STATE-OF-SUGAR-2026-08-11.md`) are currently on
`claude/sugar-crm-state-prep-8f6420`. **Recommendation: consolidate all three onto `-edda33`** so the dossier
sits with the prework it cites and the Todd pickup chain stays coherent. Verified against a repo-wide inventory
pass 2026-08-11.

---

## 0. Call outcomes — Aug 11 SugarAI call (supersedes conflicting rows below)

Recoil: `2026-08-11-todd-sugar-recoil-close.md`. Belief events appended to `sugar-alignment-belieflog.jsonl`
(in_call/post_call). Deltas from pre-call assumptions:

- **Sandbox → clean-slate net-new tenant** (a production clone needs Sugar Identity/IDM re-provision). Free under the 2-sandbox allowance.
- **Access → scoped API key, NOT admin** (add field types + geographic routing policies only). Exact scope list = §6 of the Google Doc SSOT; **API-permission scoping is the immediate blocker** (Zach specifies → Alberto confirms w/ engineering → provision).
- **Integration/customization is OUT of standard support scope** → SugarCare / Professional Services (dedicated hours). New commercial track; surface any cost *before* it's incurred (Todd guardrail).
- **Enrichment → reuse the existing ZoomInfo bidirectional integration** (already wired); Hint is fallback, not new spend. (Supersedes D5.)
- **Mailgun is in the live stack** (named on the call) → reuse it for notify/autoresponder; the memory-vs-repo discrepancy is reconciled. (Supersedes D6.)
- **Contacts:** Sebastian (Tech Support Mgr) + Alberto (Support Specialist); Long (Dir CS, bridging for Beeka/CSM); Bill Galla = PRL Sugar owner.
- **SSOT mechanics:** Sugar tracks work as a **case**; our Google Doc is the intake Sebastian converts to tickets. Postman API ref + public changelog to be shared (Alberto); health-check availability TBC with dev team.
- **Todd's three guardrails:** don't disrupt Bill's CRM · know costs before incurring · don't overcomplicate (chatbot → leads into Sugar → geo-route to the 8 reps).

## A. System overview

The system turns an anonymous website visitor into a complete, correctly-routed SugarCRM Lead with a
reachable contact channel, fast enough to hit the four-hour callback standard — and never loses one.

```
WordPress (host)  →  Tidio flow + Lyro (capture/qualify)  →  Zapier (transform + retry)
     →  SugarCRM Leads (create + route)  →  ZoomInfo (enrich)  →  Mailgun (notify + autoresponder)
```

| Component | Role in the lead's journey | Current posture |
|---|---|---|
| **WordPress** | Hosts the widget on the live/dev site | Dev + local staging live; prod untouched |
| **Tidio** | Capture, qualify, govern answers, anti-ICP screen | Bot built + branded + verified on dev |
| **Zapier** | Token handling, field transform, retry, task history | Create-Lead mapping staged |
| **SugarCRM** | System of record; create Lead + territory routing | Schema audited; write gated on sandbox |
| **ZoomInfo** | Business-email enrichment (closes the no-email gap) | Paid, unused; needs contact + wiring (1.2) |
| **Mailgun** | Rep notification + prospect autoresponder | Sidesteps info@ DNS block; to wire (1.2) |

---

## B. End-to-end data-flow contract

The lead's full path with the exact field shape at each hop. This is the integration contract every
component must honor; a change to any row is a belief-log event.

| # | Hop | Input shape | Transform / action | Output shape |
|---|---|---|---|---|
| 1 | **WordPress → Tidio** | page visit | widget loads (Tidio key `nemtpdglmxzbcpmqlqh1gnj3wmgqsxeu`); flow trigger fires | chat session opened |
| 2 | **Tidio capture** | free text + button taps | greet → intent (A knows grade/spec · B help choose · C other) → branch Qs → capture; anti-ICP keyword watcher screens "sheet"; recognizer reflects grade/competitor; governed answering (cert/price route, competitor gate-behind-capture) | session vars: `{name, email, phone, company, state, intent, inquiry_text, recognized_grade?, competitor?}` — all as session variables (not contact props) to avoid Tidio validation friction |
| 3 | **Tidio → Zapier** | session vars | flow **API-call node** (native webhook, current plan) POSTs to Zapier Catch Hook | JSON payload |
| 4 | **Zapier transform** | JSON payload | `name`→`first_name`/`last_name` (single-word fallback) · `phone`→**`phone_work`** (required) · `company`→`account_name` (fallback) · `state`→**`location_c` = FULL name** via `resolve_state` (re-ask/tag if unresolved) · `lead_source="Chatbot"` · email→**`email1`** (Sugar maintains the `email` array; the automated paths currently send no email) · `description`=`inquiry_text` (+grade/competitor/intent) · `status="New"` | Sugar Leads create payload |
| 5 | **Enrichment** (1.2) | create payload | fill firmographics + business email if missing. **Native Sugar "Hint" fields exist** (`hint_account_*`) — check if PRL's license includes Hint before paying; if so ZoomInfo is needed **only** for the `email1` gap | payload + enriched `email1`/firmographics |
| 6 | **Zapier → SugarCRM** | enriched payload | **Create Record** (Leads, sandbox) | Lead row (team Global) |
| 7 | **SugarCRM routing** | Lead row | assign by `location_c` → Primary rep via territory map; distribution-only states + NY/PA sub-region split → **default to Sales Manager/Bill**; human converts to Opportunity manually | assigned Lead |
| 8 | **Zapier → Mailgun** (1.2) | create success | rep notification + prospect instant autoresponder, both within seconds | 2 emails sent |
| 9 | **SugarCRM SLA** (1.2) | assigned Lead | **4-hour escalation nudge**: no rep response within 4h of assignment → second notification | escalation fired |
| 10 | **Metric** (1.2) | Lead lifecycle | stamp arrival + time-to-first-touch (or documented `New→Working` proxy) | measured first-touch |

**Contract invariants** (must hold end-to-end): all six required Sugar fields populated · `phone_work`
non-empty · a reachable channel (email or phone) captured before any mid-flow bail · `lead_source="Chatbot"`
· `location_c` a canonical full state name, never an abbreviation/region/placeholder · no spec/cert/price
stated as fact anywhere in the conversation · every delivery attempt retried (Zapier task), never silently dropped.

---

## C. Gate map (what blocks what)

| Gate | Owner | Blocks | State |
|---|---|---|---|
| **info@prlresins.com receiving** | Todd/IT (Jorge) + Tidio | real-traffic go-live | IN MOTION (looped Aug-10) |
| **SugarCRM sandbox access** | Todd approval + SugarAI provision | Layer-3 write test + all 1.2 delivery | pending Todd's yes (Aug-11 3pm call) |
| **Delivery + notify wired + inbox owned** | us | pointing bot at real visitors | HARD GATE (pre-mortem D1) — staging only until it passes |
| **Tidio flow-vs-Lyro precedence** | us (verify in-app) | safe exposure (capture not bypassable) | to verify |
| **ZoomInfo contact** | Todd | email enrichment (1.2) | owed |
| **Negative keywords / examples** | Todd | anti-ICP *seeding* (not launch) | owed |
| **Territory map confirmation** | Bill | reliable auto-routing | delivered once; confirm current |

Not gates (resolved — do not re-derive): sandbox is commercially free (2-allowance, case 589806); Tidio
API-call node is native webhook on the current plan; recognizer/evals/IDES/exclusions/capture-flow are built
and verified; 1.3 ground truth (150 grades) delivered + verified.

---

## D. Component dossiers

> Template per component: **Purpose · Prework & provenance · Verification · Interface contract ·
> Current state · Open questions (belief-log spans).**

### D1. WordPress — the host surface

- **Purpose.** Serve the Tidio widget on the PRL site without touching production until acceptance.
- **Prework & provenance.** Dev site on WP Engine (`wfaprlredev26.wpenginepowered.com`) with the real PRL
  theme; a local Docker/OrbStack copy (`~/prl-resins-local/`) from Todd's WXR export; Tidio injected via
  mu-plugin. Gravity Forms: `prl-lyro/normalization/prl-gf-spam-filter.php` (spam/quality filter sharing the
  one `exclusions.py` ruleset), `prl-lyro/prl-gravity-forms-cleanup.md` (cleanup plan),
  `gf-orphaned-leads-analysis.md` (orphaned GF→Zapier leads), `todd-tasks-for-site-maintainer-and-it.md`.
- **Verification.** Widget render confirmed on the dev theme via page source (our key present) + screenshot.
- **Interface contract.** Widget key `nemtpdglmxzbcpmqlqh1gnj3wmgqsxeu`; flow trigger = first-visit (consider
  chat-open + returning-visitor triggers for production).
- **Current state.** Dev + local staging live; **live site untouched.** Build on staging → live, never on live.
- **Open questions.** `wordpress.staging-parity`. Gravity Forms spam fix approved (Zach applies staging→live).

### D2. Tidio — capture, qualify, govern

- **Purpose.** Capture a qualified lead, recognize resins/competitors, screen anti-ICP, and answer only what
  is safe to answer (governed answering).
- **Prework & provenance.** Research: `prl-lyro/tidio-capabilities-research.md` (every claim source-tagged
  confirmed/likely/unverified), `prl-lyro/current-journey-audit-baseline.md` (the "today" experience to beat).
  Flow build: `prl-tidio-capture-flow-spec.md`, `prl-tidio-build-assets.md`, generator
  `prl-lyro/prl_tidio_flow_gen.py`, generated `prl-chatbot-flow.json` (1339 lines) +
  `prl-chatbot-flow-capture-first.json` (1016 lines), branch logic `2026-07-20-todd-chatbot-branch-logic-v1.md`,
  voice/triggers/personas v1 sheets, `2026-08-03-todd-lyro-ai-layer-v2.md`. Lyro config SSOT (`prl-lyro/README.md`
  runbook): `guidance-prompt.md`, `kb-content/kb-content.md`, `kb-manifest.md`, `conversation-starters.md`,
  `handoff-policy.md`, `costcap-policy.md`, `audiences.md` + `icp-audiences-molder-vs-oem.md`. Governance:
  `prl-lyro/ADR-PRL-001-governed-answering.md` (**Proposed** — pending Zach ratify + Todd nod).
- **Verification.** `prl-lyro/normalization/normalize.py` (recognizer, runnable self-test); `coverage_sweep.py`
  (895 competitors · 150 grades · 50 states · punctuation · field-gate); `full_grid_sweep.py` (150×50×3 =
  **22,500** invariants); `simulate_lead_e2e.py` (staged dry-run → prints the exact Sugar payload, no writes);
  `prl_lyro_eval.py` (Lyro safety eval set); `prl-lyro/firewall-test-prompts.md` (anti-fabrication gate);
  `exclusions.py` self-test.
- **Interface contract.** All capture fields ride as **session variables** (not contact properties) to avoid
  Tidio validation friction; values still travel on the webhook. Output shape per §B row 2.
- **Current state.** Bot built, branded, activated + tested end-to-end on the dev site. Lyro AI + Flows live.
  Delivery to Sugar is the remaining wiring. **Risk flag:** the "backup" `prl-lyro/backups/live-flow-lead-
  capture-2026-08-09.json` is an **empty file (0 lines)** — the live flow is not actually backed up; re-export before edits.
- **Open questions.** `tidio.capture-order`, `tidio.flow-vs-lyro-precedence`, `tidio.webhook-native` (ALIGNED).
  Governed answering stays route-only for 1.1.

### D3. Zapier — transform, retry, task history

- **Purpose.** Do the OAuth token dance Sugar requires, transform the captured fields into a valid Leads
  payload, and make every delivery a retryable, visible task (never a silent drop).
- **Prework & provenance.** `prl-tidio-capture-flow-spec.md` (§ Webhook → Zapier Catch Hook, testable now
  against a Catch Hook); `prl-tidio-build-assets.md` (§2 Catch Hook → Sugar Create-Record field map);
  `2026-07-30-todd-tidio-deploy-integration-handoff.md` (§2 delivery decision + steps); proven existing
  Unbounce→Sugar zaps (Sabic/Covestro/Ventilator) to copy; `simulate_lead_e2e.py` prints the exact payload.
- **Verification.** Mapping grounded against the live Leads schema via read-only audit; no production write.
  End-to-end write proof is the sandbox-gated Layer-3 step.
- **Interface contract.** §B rows 4–6. Keeps Zapier in the middle by decision (a raw single-node write can drop
  a 500 and lose the lead — the exact failure this project prevents).
- **Current state.** **Staged, not yet run** against a live/sandbox write. Lock this sprint.
- **Open questions.** `zapier.create-lead-mapping`, `2.3-rate-limits`.

### D4. SugarCRM — system of record

- **Purpose.** Create the Lead, route it by territory, and be the attribution + reporting substrate.
- **Prework & provenance.** Live read-only config audit (artifact `5fc2e7ac`) + `2026-08-04-sugar-deep-dive-
  clarifications.md`. Schema design (built from public SchemaSpy docs, mechanism **confirmed live 2026-08-07**):
  `prl-kb/sugar-schema/leads-integration-design.md` (webhook contract + field map + the `email1` fix + the
  Hint-vs-ZoomInfo enrichment framing + 4-hr query design), `leads-columns.tsv` (106 cols),
  `opportunities-columns.tsv` (55 cols), `build-vs-current-state.md` (W-Systems 2020 as-built vs live drift),
  `audit-findings-2026-08-07.md`, `admin-config-runbook.md`. Territory: `prl-territory-map.csv` (50 states).
  Call prep: `prl-lyro/SUGAR-call-prep-2026-08-11.md`.
- **Verification.** Audit confirmed: 6 required fields; `phone_work` 100/100; `location_c` = full names in all
  live records; `lead_source` lacks a Chatbot value; team Global = no record privacy; 92/100 assigned to Bill
  Galla; **leads have no `email` column → write `email1`**; native **Hint** enrichment fields present.
- **Interface contract.** §B rows 6–7. OAuth2 password/refresh; write full state names; write email to `email1`;
  add "Chatbot" source.
- **Current state.** Schema known; **write blocked on sandbox access.** prod `prlresins.sugarondemand.com`,
  stale sandbox `prlresinstest.sugarondemand.com`.
- **Open questions.** All §2–§4 belief spans + the health-check/drift asks. See the Google Doc.

### D5. Enrichment (Sugar Hint vs ZoomInfo)

- **Purpose.** Fill a business email (to `email1`) and firmographics so a lead is reachable and scoreable —
  closing the no-email gap on the historical channel.
- **Prework & provenance.** **No dedicated build artifact.** Framed as a decision in
  `prl-kb/sugar-schema/leads-integration-design.md` (Finding 2): Sugar's **native Hint** fields
  (`hint_account_size/industry/location/founded_year/...`) may already enrich firmographics — **check whether
  PRL's license includes Hint before paying**. ZoomInfo would then be needed **only** for the `email1` gap.
- **Verification.** None — unwired.
- **Interface contract.** §B row 5.
- **Current state.** **Open decision: Hint (owned?) vs ZoomInfo (paid).** ZoomInfo access exists but is unused
  and unwired; confirm the Hint entitlement first (it may make ZoomInfo unnecessary for firmographics).
- **Open questions.** `zoominfo.email-enrichment` (repointed: resolve Hint-vs-ZoomInfo; ZoomInfo contact owed by Todd only if we go paid).

### D6. Mailgun / notifications

- **Purpose.** Fire the rep notification and the prospect's instant autoresponder within seconds.
- **Prework & provenance.** **No dedicated Mailgun artifact.** The **actually-designed** notification path is
  **Zapier's Gmail/Email action** (`2026-07-30-todd-tidio-deploy-integration-handoff.md` §2, Action A → test
  address); Mailgun is named once as one option among several in `prl-tidio-build-assets.md`.
- **Verification.** None — unbuilt.
- **Interface contract.** §B rows 8–9: on create-success, send rep alert + prospect autoresponder; feed the
  4-hour escalation nudge.
- **Discrepancy to resolve.** The engagement memory lists Mailgun as a secured asset that "sidesteps the info@
  DNS block," but the repo has no Mailgun build and the designed path is Zapier-Gmail. **Decide the real
  notification transport** (Zapier-Gmail vs Mailgun sending subdomain vs Resend) before wiring 1.2; the info@
  fix is proceeding independently (Jorge + Tidio).
- **Current state.** To build in 1.2 once the transport is chosen.
- **Open questions.** `mailgun.notify-autoresponder` (transport undecided), `mailgun.info-email-gate` (IN MOTION).

---

## E. How the three surfaces relate

| Surface | Audience | Depth | Path |
|---|---|---|---|
| **This dossier** | internal | full | `INTEGRATION-DOSSIER.md` |
| **Belief/version log** | internal | append-only trace | `sugar-alignment-belieflog.jsonl` |
| **Sugar async Q&A** | SugarAI team | Sugar-facing slice | `gdoc:1R_5KrszhixFrxUnDabxGa8gAnqMMhuSJiOwvc3YR1sM` |
| **Visual alignment page** | client-safe | Sugar-facing slice | artifact `0e0280a6` |

---

## F. Verification & eval harnesses (the proof the depth is real)

The system's correctness is not asserted — it is re-runnable. All paths on branch `-edda33`, under
`runtime/recoil/generated/prl-lyro/`. Re-run Layer 0 before every deploy (see `TEST-PLAN-go-live.md`).

| Harness | What it asserts | Scale / result |
|---|---|---|
| `normalization/normalize.py` | Deterministic recognizer: `recognize()` + `normalize_state()`; recognition only, never emits spec/price/UL | runnable self-test (10/10 current run) |
| `coverage_sweep.py` | Every competitor key · every grade · every state · punctuation robustness · required-field gate | 895 competitors · 150 grades · 50 states · 297 punctuation · 64 field-gate perms |
| `full_grid_sweep.py` | Recognize → route → gate → governed invariants across the full cross-product | **150 × 50 × 3 = 22,500** invariants hold |
| `simulate_lead_e2e.py` | Staged end-to-end dry-run → prints the exact Sugar Leads payload; no CRM write | per-scenario decision + field-gate PASS |
| `prl_lyro_eval.py` | Live-Lyro safety eval set: SPEC/SPECRISK/XREF (never state a spec/cert/competitor equivalence as fact), SCOPE (never invent price/MOQ), input_hygiene, PUSHBACK, AMBIGUITY, GROUNDED | eval case set (emit → score; ≥3× per case) |
| `firewall-test-prompts.md` | Anti-fabrication acceptance prompts for the Lyro Playground | pre-go-live gate |
| `normalization/exclusions.py` | Anti-ICP / negative-keyword filter shared by chatbot + Gravity Forms | self-test 8/8 |
| `TEST-PLAN-go-live.md` | The layered acceptance gate (L0 deterministic → L1 live-Lyro → L2 capture flow → L3 Sugar delivery → L4 governed answering) | the 1.1 DoD |

**Anti-fabrication is the through-line:** the bot captures + routes and, per `ADR-PRL-001` (Proposed),
states a spec/cert/price only when grounded + eval-passed + fresh; otherwise it hands off. The evals turn
"we told it not to" into a re-measurable number.

## G. Complete artifact registry

Grouped; all paths branch-relative to `-edda33`.

**Recognition & data engine** — `normalization/normalize.py` · `grade-dictionary.json` (150 grades) ·
`material-synonyms.json` · `competitor-to-prl.json` (**895 keys**) · `field-normalization.json` (state map +
lead_source canon) · `exclusions.py` + `exclusions.json` (anti-ICP SSOT, incl. `todd_provided`).

**Tidio flow build** — `prl-tidio-capture-flow-spec.md` · `prl-tidio-build-assets.md` ·
`prl_tidio_flow_gen.py` (generator) · `prl-chatbot-flow.json` (1339 ln) ·
`prl-chatbot-flow-capture-first.json` (1016 ln) · `2026-07-20-todd-chatbot-branch-logic-v1.md` · voice /
triggers-and-picker / personas-routing v1 sheets · `2026-08-03-todd-lyro-ai-layer-v2.md`.

**Lyro config SSOT** (`prl-lyro/README.md` runbook) — `guidance-prompt.md` · `kb-content/kb-content.md` ·
`kb-manifest.md` · `conversation-starters.md` · `handoff-policy.md` · `costcap-policy.md` · `audiences.md` +
`icp-audiences-molder-vs-oem.md` · `backups/CONFIG-STATE-2026-08-09.md`. **⚠ `backups/live-flow-lead-capture-2026-08-09.json` is empty (0 lines) — not a real backup.**

**Sugar schema & integration** — `prl-kb/sugar-schema/leads-integration-design.md` (contract + `email1` fix +
Hint-vs-ZoomInfo) · `leads-columns.tsv` (106) · `opportunities-columns.tsv` (55) · `build-vs-current-state.md`
· `audit-findings-2026-08-07.md` · `admin-config-runbook.md` · config-audit artifact `5fc2e7ac` ·
`2026-08-04-sugar-deep-dive-clarifications.md` · `SUGAR-call-prep-2026-08-11.md`.

**Data assets** — `prl-kb/prl-product-catalog-2025.json` (150 grades, specs 100% verified) ·
`prl-products-2025.jsonl` · `competitor-intel/cross-reference-map.csv` (335 rows, internal only) ·
`ides-datasheets/` (28-sheet public scrape) · `site-datasheets/` (~35 PDFs, held out of KB) ·
`tidio-upload/` (3 upload-ready PDFs) · `prl-territory-map.csv` (50 states) · `prl-QATF001-opportunity-form.docx`.

**WordPress / Gravity Forms** — `normalization/prl-gf-spam-filter.php` · `prl-gravity-forms-cleanup.md` ·
`gf-orphaned-leads-analysis.md` · `todd-tasks-for-site-maintainer-and-it.md`.

**Decision & planning** — `ADR-PRL-001-governed-answering.md` (Proposed) · `CHECKPOINT-review-before-build.md`
· `PREMORTEM-user-experience.md` · `experience-consistency-and-ab-plan.md` · `SPRINT-2-1.2-kickoff.md` ·
`2026-08-04-todd-ROADMAP-1.1-to-1.4.md` + phase maps · `2026-08-05-todd-plan-premortem-gauntlet.md`.

**Status routine** — `prl-status/board.json` + `render_status.py` (stdlib-only, "only-when-changed" hash gate).

## H. Sugar AI access & MCP findings (2026-08-11)

**Does SugarCRM have an MCP?** No first-party MCP server from SugarCRM itself. But relevant tooling exists,
and we are already connected to one:

| Path to Sugar | What it is | Our status |
|---|---|---|
| **Zapier MCP** | Third-party MCP already exposing PRL's live SugarCRM (`SugarCRMCLIAPI`, connection "SugarCRM 7+ Importer") — read + write, no new creds | **ALREADY CONNECTED** — this is how the config audit was run |
| **CData MCP for SugarCRM** | Third-party MCP: read-only free (Claude Desktop via JDBC); full CRUD only via CData Connect AI (paid) | not needed (Zapier covers it) |
| viaSocket / Pipedream MCP | Other third-party bridges | not needed |
| **`sugarcrm-developers/ai-for-sugar-devs`** (GitHub) | **Official** Sugar dev skills library for generating **upgrade-safe Module Loadable Packages (MLPs)** with any AI agent incl. Claude Code | **directly relevant** — the upgrade-safe way to ship the "Chatbot" `lead_source` + any Studio customization (answers belief spans 2.5/2.6 and the health/drift asks) |
| **`apidocs.sugarcrm.com` + Postman collection** | Official SugarAI REST API docs + Developer Guide | the canonical answer to auth (2.2) + rate limits (2.3) — cite in the Sugar Doc |

**Takeaways:** (1) we do **not** need a new MCP — the connected **Zapier MCP** already gives live read/write
to PRL's Sugar. (2) For upgrade-safety (the health/drift concern), the **official `ai-for-sugar-devs` MLP
path** is the right tool: package customizations as upgrade-safe MLPs rather than hand-editing Studio. (3) The
official **`apidocs.sugarcrm.com`** answers the auth/rate-limit doc-pointer asks — worth citing in the async
Doc so the Sugar team confirms rather than us guessing.
