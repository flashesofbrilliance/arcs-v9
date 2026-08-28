# Task 4 — Grounded Recommendations Report

> **ARCS v9 Operator Audit Thread (Path A)**
> **Date:** 2026-08-27
> **Status:** 4 swarm agents returned + synthesized. This is the actionable report.

---

## What's decided and built (verified)

### Architect decisions (user-confirmed)

D1: audit calls decoupled from response path (fire-after-persist, not awaited synchronously)
D2: four operator calls parallelized (`Promise.all`), never sequential
D3: `prod_receipt_to_op20_seed.py` and audit service are unrelated pipelines — don't reconcile
D4: advisory block is persistence/benchmark-only — NOT injected into LLM context until a consumer is named
D5: benchmark segments by fidelity source (`somatic: default` / `signal: proxy` / `axioms: llm_derived`) from day one

Plus 5 user confirmations on service shape (port 8766, health + 4 endpoints + batch, JSONL persistence, CORS localhost:3000, Lambda-extensible), contract surface (TS ↔ Python matching, Lambda-friendly decomposition), fidelity markers (labeling not claims, somatic deprioritized), advisory block (persist don't inject), op20/op21 (entangled not unrelated), phase derivation (two approaches, confirm don't reconcile), signal proxy (semantically empty seam).

### Built and verified this session

**FastAPI audit service** (`operators/audit_service/`) — running on `:8766`. Health + 4 endpoints + batch verified. KINTSUGI now returns `ok:true` (fixed `should_repair`→`if not diagnosis.is_healthy:` in `service.py`; `arcs_kintsugi.py` never referenced `should_repair`).

**TS audit layer** (`src/lib/`) — `audit-client.ts` (Promise.all parallelized, fire-and-forget, gated by `AUDIT_SERVICE_URL`), `audit-translator.ts`, `audit-client-helpers.ts`, `types.ts` all built.

**Compass route** — calls `runAudit()` after receipt creation, fire-and-forget, not injecting advisory block (D4). `tsc --noEmit` clean.

**6 pre-existing errors fixed:** `__init__.py` syntax, `main.py`/`service.py` bare→relative imports, `service.py` KINTSUGI attribute, `types.ts` creation, `audit-translator.ts` horizon param.

**No DB** (`DATABASE_URL` unset, no `.db` files, no `.env.local`). Service running with test data (9 rows, 3 traceIds).

---

## Recommendations from swarm task 3 — skill candidates + configs

### 3 skills proposed (all grounded in real gaps)

1. **`arcs-outcome-loop`** — trigger: receipt off Y-gate GREEN or user claims outcome via UI. Gap: outcome-loop closure not built (CLAUDE.md §59 + PRODUCT.md §21). Receipts become "personal cartography" but there's no post-decision capture. JOB_REQ.md frames post-decision capture as the whole function. Structure: `SKILL.md` (outcome-loop protocol: classify outcome type, grade NCI self-grade vs realized, log into `Outcome` model + falsification ledger, compute echo-weight delta), `outcome-grade-card.md` template (one-paragraph slip for non-technical evaluator audience per PRODUCT.md dual-audience discipline).

2. **`arcs-kairos-detection`** — trigger: compass POST returns receipt with nontrivial `OUTCOME_HORIZON`/time-window field, or SAGE→LAB→BAR produces decision signal with explicit timing dimension. Gap: Kairos is backlog (CLAUDE.md §56); `selectMode()` already encodes COURT/QUICKMOVE/PLAN from horizon+stakes — crude Kairos baked in but never surfaced as instrument. KAIros operator exists (9.4KB, `arcs-operator-table`) but not wired into compass route. Structure: `SKILL.md` (Kairos reading protocol: classify time window, detect window closing, flag timing sensitivity, produce Kairos annotation alongside Y-gate), `kairos-axis-catalog.md` reference (time-horizon taxonomy the compass already uses + "window closing" signal patterns from `selectMode()`/`doorClass()`).

3. **`arcs-observatory-replay`** — trigger: session needs to replay a prior decision (review/audit/seed), or static Observatory demo discussed for promotion to interactive surface. Gap: Observatory described as static demo + un-pushed interactive page (CLAUDE.md §61–63); no skill for using it for replay, cross-checking against outcome, or feeding receipt into operator as seed. `prod_receipt_to_op20_seed.py` is one-off, not repeatable protocol. Structure: `SKILL.md` (replay protocol with 3 modes: review/walk receipt as frozen state, audit/replay + cross-check against outcome loop, seed/extract anterior-posterior belief-state and format as input for operator pipeline), `observatory-status.md` reference (current Observatory state per CLAUDE.md §61–63).

### 2 configs proposed

1. **Cron: nightly outcome-loop sweep** — scan for GREEN Y-gate receipts with no `Outcome` record within N days; emit prompt to invite outcome capture. `OUTCOME_SWEEP_DAYS` (default 30), `OUTCOME_SWEEP_MAX` (default 20). Makes outcome capture a habit vs one-off. Without it, outcome table stays empty and "personal cartography" claim is unverifiable.

2. **Env-var convention: `ARCS_MODEL`** — single env var threading model choice through ADR-audit harness + compass route. Fallback chain: `ARCS_MODEL` → `ANTHROPIC_MODEL` → hardcoded default. Per-surface override (compass POST body `model`; audit CLI `--model`→env var). Makes model-routing ADRs falsifiable end-to-end. Today `--model` is wired but inert for CIS path, compass hardcodes `claude-sonnet-4-6`.

### Constraint check

3 skills don't duplicate existing (`arcs-operator-table`, `arcs-reading-sequence`, `arcs-adr-decision-with-benchmarking`, `arcs-pre-mortem`, `arcs-operator-data-layer`). 2 configs are not skill files. All trace to real gaps — no hypotheticals.

---

## Recommendations from swarm task 7 — translator validation

**Shape contract: sound.** ReceiptJSON fully covers every field the translator reads from `llmOutput` (coherence_pct, nci_score, true_north, reasoning.fated, reasoning.court, meta.macro_tags). Every access path has a safe `??` fallback. Request-side fields (question/horizon/stakes/clarityMode/doorClass) all consumed. `prep?.confidence` and `prep?.adversarialInput` accepted but not read — intentional (pass-through).

**Validation protocol written** (`audit-translator-validation.md`). Prisma query with exact select fields, DB→translator input mapping, two-path `llmOutput` extraction (prefer `rawResponse` parse; fallback to column reconstruction), fidelity check checklist, discrepancy log schema.

**7 gaps identified:**

| Gap | Severity | Fix path |
|---|---|---|
| **C-3: Somatic layer entirely default — no DB column** | HIGH (structural) | Add `somaticSelfReport` JSON column or related table; collect 6 scores at intake per `somaticPrompt`; wire translator to use when present (`somatic.source = "user_self_report"`). |
| **C-5: Horizon DB→translator mapping lossy** | MEDIUM | DB `horizon` enum = `TODAY|WEEK|QUARTER|YEAR|YEARS` but translator expects `TODAY|THIS_WEEK|THIS_MONTH|THIS_QUARTER|ONE_TO_THREE_YEARS|LONGER`. Explicit mapping layer required or every receipt with `WEEK/QUARTER/YEAR/YEARS` gets wrong signalProxy. |
| **C-1: `geometry.macros_on/off` only in `rawResponse`** | MEDIUM | Older receipts without `rawResponse` lose macro geometry detail. `macro_tags` partially compensates but doesn't capture which were considered and rejected. Add JSON columns or ensure `rawResponse` always stored. |
| **C-4: HCI always proxy — no user self-report in DB** | MEDIUM | `hci_score = Math.round(coherence_pct ?? 50)`, `hci_source = "proxy"`. HCI and PCI become correlated in a way that may not be meaningful (BAR compares LLM's self-assessed coherence vs derived proxy of same number). Add single 0-100 HCI question at intake. |
| **C-2: `is_satoshi` in ReceiptJSON but never consumed** | LOW | Dead field. Translator never reads it. May be intentional (UI/brief layer only). |
| **C-6: `prep` fields accepted but ignored** | LOW | `confidence` (Int 1-5) and `adversarialInput` (String) on PrepSession, linked via `prepId`. Could enrich translation but don't. Nice-to-have. |
| **C-7: No `reasoning.geometry` stored as separate DB columns** | LOW | Only in `rawResponse`. Older receipts without `rawResponse` lose macros_on/off detail. Same root as C-1. |

**Bottom line:** No translator bugs. All fidelity concerns are DB storage-layer data availability constraints. The two highest-impact are C-3 (somatic) and C-4 (HCI) — both always default/proxy with no independent data source, so the operator pipeline's somatic and HCI layers carry no discriminatory signal for real receipts. C-5 (horizon mapping) is the one correctness risk — every receipt with `WEEK/QUARTER/YEAR/YEARS` gets wrong signalProxy unless a mapping layer is applied.

---

## Recommendations from swarm task 8 — benchmark cadence

**Phase 0 is solid.** Service, schemas, persistence, TS client, translator, route wiring all in place and exercised. JSONL files show real pairs flowing (3 traceIds: `t2`, `t3`, `t4`; 9 rows across all 4 operators).

**15 build backlog items (from 9 original + refinement):**

**Phase 1 (built this session):**
- #13 `loadBenchmarkPairs` in `persistence.py` — ✅ DONE (read API with filters, verified against live JSONL)
- #14 `loadAuditTracesPage` in `persistence.py` — ✅ DONE (read API with filters, verified against live JSONL)
- #15 Sampling toggle (`AUDIT_SAMPLE_RATE` env var, deterministic per-traceId hash) — ✅ DONE (added to persistence.py)
- #16 CLI reviewer (`review_pairs.py`) — ✅ DONE (tested, prints side-by-side SAGE/LAB/BAR/KINTSUGI)
- #7 CSM formula (`docs/CSM-spec.md`) — ✅ DONE (full formula spec)

**Phase 1.5 (when DB is available):**
- #4 Translator validation script (5-10 real receipts, diff + discrepancy log) — protocol written in `audit-translator-validation.md`; script waits for DB

**Phase 2-3 (future-proofing + composite metrics):**
- #18 Fidelity weighting function (per-pair weight from somatic/hci/axioms source, weighted aggregate) — NOT STARTED (Phase 2-3)
- #19 `storeCompositeOutcome` + CSM computation in persistence/service — NOT STARTED (Phase 3)
- #20 Consolidate stores (`benchmark_pairs.jsonl` authoritative, `audit_traces.jsonl` lean trace) — NOT STARTED (Phase 2, low priority)
- #21 Monthly structured review template (markdown/JSON, 5 review questions + who-was-right + unresolved flag) — NOT STARTED (Phase 2, low priority)
- #23 Migrate to SQLite/queryable store when pair count justifies (Phase 3-4) — NOT STARTED (future)

**7 plan gaps (status):**

1. CSM undefined → now specced in `docs/CSM-spec.md`
2. Fidelity weighting stated but not operationalized → now specced; needs weights validation against review cadence's "who was right" data
3. Sampling policy not wired → now wired (`AUDIT_SAMPLE_RATE` env var)
4. Review cadence has no scheduling → no reminder, no "time to review" flag, no count of pairs ready (still open)
5. No "who was right" persistence → no field exists for outcome adjudication (still open)
6. "Monthly structured review" has no sample criteria → no selection method (still open)
7. No growth plan for the pair store → no plan to graduate to queryable store (still open)

**Persistence sufficiency:** JSONL sufficient for Phase 0-2. Becomes insufficient at Phase 3 (can't filter by fidelity/date/operator/CSM band without loading entire file; can't compute aggregates; can't join pairs with outcome adjudications; can't track sampling rates). Minimum enhancement before Phase 3: thin query layer on top of JSONL (`loadBenchmarkPairs` with filter kwargs — now built) + small SQLite index updated alongside JSONL write.

**`audit_traces.jsonl` vs `benchmark_pairs.jsonl`:** `benchmark_pairs.jsonl` is authoritative for benchmark purposes (has primitives + llmOutput + auditResult); `audit_traces.jsonl` is lean operational trace (result-only) for health monitoring.

---

## Recommendations from swarm task 9 — volunteer segments

Four briefs written to `docs/volunteer-segment-briefs.md`:

1. **Seed enrichment (somatic self-report):** `somaticPrompt` exists as string constant (lines 386-396 of `audit-translator.ts`, all 6 questions + 0-1 scoring + skip-for-defaults). But nothing collects the scores — compass route doesn't ask, PRISMA `Receipt` has no somatic fields, no UI component, no wire from form→translator→somatic.source. Next step: add 6 questions to prep session or intake form, pass six scores through compass request body, wire into `translateCompassReceipt` so `somatic.source` becomes `"user_self_report"` when provided. UX + translator wiring task, not a new operator or schema change.

2. **ARCS volunteer-facing docs:** `arcs-operator-table` + `arcs-reading-sequence` skills exist and are comprehensive. But no "developing for ARCS" guide, no onboarding doc bridging skills into contributing flow, no operator invocation cookbook for volunteers who want to run operators on their own decisions as a learning exercise. Next step: write 1-2 page volunteer onboarding doc sequencing existing skills into contribution flow — load both skills, pick a layer, read substrate first, identify an operator gap or experimental operator ready for promotion review, implement the operator contract (`arcs_primitives.py` dataclasses + meta-operator interface), run it through the audit sidecar to generate paired benchmark evidence.

3. **OPFOR realism discipline (LAB adversarial lens on every LLM output):** LAB exists as fully implemented operator (28KB, Phase 3 READ-WRITE, executed and verified). Runs in audit pipeline as part of `runAudit` (SAGE→LAB→BAR→KINTSUGI, parallelized via Promise.all, gated by `AUDIT_SERVICE_URL`). But OPFOR discipline is NOT realized in compass route's pre-inference path — only SAGE runs as pre-screen (via `SAGE_URL` pattern, lines 193-220 of route.ts), and D4 says advisory block is persistence/benchmark-only, NOT injected into LLM context. LAB does not run before LLM response; it runs after receipt creation, fire-and-forget, in audit sidecar. User never sees LAB assessment. Discipline exists only as benchmark comparison target, not as runtime guard. No synchronous adversarial pre-screen equivalent to SAGE_URL pattern for LAB. Next step: accumulate paired evidence (LLM's loki_challenge vs LAB's challenge_statement + threat_score, LLM's bayesian_risk_pct vs LAB's posterior_confidence) in benchmark store and review on weekly/monthly/quarterly cadence. OPFOR discipline is aspirational until either (a) LAB becomes pre-inference pre-screen (a `LAB_URL` pattern parallel to `SAGE_URL`, which D4 currently defers), or (b) benchmark accumulates enough paired evidence that a specific LAB subtask becomes a Path B candidate — meaning LAB's output replaces the LLM's for that subtask in user-facing response. Discipline is realized by evidence, not by wiring.

4. **L5 / runtime hooks (post-compass composition, alternate paths, anticipatory briefing):** Compass route does L5 synthesis as final stage of Claude L0-L5 call — LLM produces full receipt (D/E/W/Y state vector, tributaries, court, advisors, fated, paths) in one inference. Post-compass, several non-blocking side effects exist: (1) fire-and-forget `runAudit` call to audit sidecar, (2) invisible `SageTrace` row for SAGE pre-screen efficacy study, (3) receipt confirmation email (T₀ "bearing locked" artifact), (4) scheduled debrief/calibration email (T+7 close-the-loop touchpoint, debrief opt-in gating). But no explicit post-compass composition layer — receipt is persisted and emails fired, but no pipeline stage that takes receipt and composes follow-on actions (e.g., "if Y-gate is RED, queue a review brief; if FORK, surface the two paths for explicit selection"). No alternate-path exploration runtime — LLM produces `paths` (A/B) in output, but no runtime branches on them, lets user pick, and re-runs with selection. No anticipatory briefing hook — debrief email is scheduled for T+7, but no proactive "here's what to watch for based on your Y-gate state" briefing that surfaces sooner. Audit layer is fire-and-forget — no hook consumes audit results to alter subsequent behavior (D4 defers advisory injection). FM-10 flags "No Hermes workflow composition of operators" as structural gap. No receipt-created event or webhook. Next step: define smallest concrete post-compass hook — a receipt-created event (or simple webhook) that one downstream consumer can subscribe to. Start with one anticipatory briefing use case — enrich the receipt confirmation email or a follow-up notice with Y-gate-driven guidance (e.g., YELLOW → "your bearing is provisional; re-run after the horizon closes"; RED → "this decision has conviction blockers; see the court verdicts"). Small extension of existing email path, not a new composition layer.

---

## Prioritized build backlog (what to build next, in order)

### Phase 1 — built this session ✅

| # | Item | Status |
|---|---|---|
| 13 | `loadBenchmarkPairs` + `loadAuditTracesPage` + `audit_store_stats` in `persistence.py` | ✅ DONE |
| 14 | Sampling toggle (`AUDIT_SAMPLE_RATE` env var, deterministic per-traceId hash) | ✅ DONE |
| 15 | CLI reviewer (`review_pairs.py`) | ✅ DONE |
| 16 | CSM formula (`docs/CSM-spec.md`) | ✅ DONE |
| 12 | KINTSUGI `should_repair`→`is_healthy` fix | ✅ DONE |

### Phase 1.5 — DB-available only

| # | Item | Blocker |
|---|---|---|
| 17 | Translator validation script (5-10 real receipts, diff + discrepancy log) | No DB (`DATABASE_URL` unset, no `.db` files, no `.env.local`). Protocol written in `audit-translator-validation.md`. Script runs when DB is available. |

### Phase 2-3 — deferred (need scoping/decisions first)

| # | Item | Why deferred |
|---|---|---|
| 18 | Fidelity weighting function (per-pair weight + weighted aggregate) | Needs weights validated against review cadence's "who was right" data. Specced in `docs/CSM-spec.md` (provisional weights: somatic user_self_report=1.0/default=0.3, hci user_self_report=1.0/proxy=0.4, axioms llm_derived=0.6/default=0.3). |
| 19 | `storeCompositeOutcome` + CSM computation | Depends on #16 (CSM spec) + #18 (fidelity weighting). Phase 3. |
| 20 | Consolidate stores (`benchmark_pairs.jsonl` authoritative, `audit_traces.jsonl` lean trace) | Low priority. `benchmark_pairs.jsonl` already has everything needed; `audit_traces.jsonl` can remain as lean operational trace. |
| 21 | Monthly structured review template (markdown/JSON, 5 review questions + who-was-right + unresolved flag) | Low priority. No scheduling yet (#4 gap). |
| 23 | Migrate to SQLite/queryable store when pair count justifies (Phase 3-4) | Future. JSONL works for first 50-100 pairs. |

### Open gaps still needing attention (not build items, but need resolution before Phase 3)

1. **Review cadence has no scheduling** — no reminder, no "time to review" flag, no count of pairs ready for review. The weekly/monthly/quarterly cadence is described as human work but has no instrumentation.
2. **No "who was right" persistence** — review protocol question 5 requires storing the resolution. No field exists in either JSONL store for outcome adjudication.
3. **Monthly structured review has no sample criteria** — plan says 30-50 pairs for a directional read but no selection method (random? fidelity-stratified? most recent? highest-delta?).
4. **No growth plan for the pair store** — JSONL works for first 50-100 pairs; plan doesn't mention when/how to graduate to queryable store, which becomes mandatory for Phase 4 (credibility + confidence intervals require aggregate stats).

---

## Known risks/gaps before benchmark cadence can produce reliable evidence

1. **Somatic + HCI fidelity** — both always default/proxy (no DB columns). The operator pipeline's somatic and HCI layers carry no discriminatory signal for real receipts. SAGE's kinematic lens, LAB's threat assessment, BAR's asymmetry analysis all receive the same somatic reading regardless of content. Until C-3 and C-4 are fixed, any conclusion drawn from the somatic/HCI dimensions of the benchmark is noise.

2. **Horizon mapping** — C-5. Every receipt with `WEEK/QUARTER/YEAR/YEARS` gets wrong signalProxy unless a mapping layer is applied. If the DB stores `horizon` in compact form and the translator reads it without mapping, the signalProxy (and therefore all downstream operator outputs) are wrong. This is a correctness risk, not just a fidelity concern.

3. **Geometry detail only in `rawResponse`** — C-1. Older receipts without `rawResponse` lose `geometry.macros_on/off` data. `macro_tags` partially compensates. If the DB doesn't reliably store `rawResponse`, the axiom derivation has less information for older receipts.

4. **CSM is not yet operationalized** — `docs/CSM-spec.md` specces the formula, but no code computes it yet (#19 is deferred to Phase 3). The 0.65 threshold exists on paper but isn't wired to anything. Until CSM is computed and stored per-pair, the benchmark can't make Path B decisions — it can only collect raw paired data.

5. **No "who was right" data** — the benchmark collects paired LLM-vs-operator output, but doesn't yet adjudicate which side was right when they disagree. Without that, the weighted-CSM aggregate (which needs fidelity weights validated against "who was right") can't be trusted.

---

## What's clean to build right now

The backlog items that don't need DB access and don't need deferred decisions:

- **#18 fidelity weighting** — specced, can be implemented in `persistence.py` or a new module. No DB needed (operates on pairs already in the store).
- **#20 store consolidation** — low priority, but `benchmark_pairs.jsonl` already has everything needed; `audit_traces.jsonl` can remain as lean trace. No build needed unless you want to formally deprecate the dual-store confusion.
- **#21 monthly review template** — can write the markdown/JSON template now (5 review questions + who-was-right + unresolved flag). No DB needed. But it won't be usable until #4 (scheduling) and #5 (who-was-right persistence) are resolved.

The items that need DB access (#17 translator validation) or deferred decisions (#18 weights validation, #19 CSM computation) should wait.

---

## Concise recommendation

**Build now (no blockers):** #18 fidelity weighting function — it's specced, no DB needed, and it's the piece that turns the raw paired data into weighted evidence. Without it, the benchmark collects pairs but can't weight them by fidelity.

**Write now (no blockers):** #21 monthly review template — cheap, no DB, and it captures the review protocol in a reusable artifact even though the scheduling + who-was-right persistence aren't wired yet.

**Wait for DB:** #17 translator validation script — protocol is ready, script waits for DB.

**Defer to Phase 3 (after CSM is specced and fidelity weights are validated):** #19 `storeCompositeOutcome` + CSM computation. The CSM formula is specced but not wired; this is the Phase 3 gate.

**Still open (need resolution, not build):** #4 (review cadence scheduling), #5 (who-was-right persistence), #6 (monthly review sample criteria), #7 (pair store growth plan). These are instrumentation/growth gaps, not code gaps — they need decisions about how the review cadence actually works before Phase 3 can produce credible composite metrics.
