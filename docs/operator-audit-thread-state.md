# Operator Audit Thread — State + Build Backlog

> **Last updated:** 2026-08-27
> **Purpose:** single source of truth for the Operator Audit Thread (Path A): what's decided, what's built, what's[next]

---

## 1. Decisions locked (architect↔implementer, live back-and-forth)

These are confirmed by the user after the architect session's artifact. Build against these.

### D-series (decisions)

| ID | Decision | Confirmed? |
|---|---|---|
| **D1** | Audit calls decoupled from response path — fire-after-persist / background, not awaited synchronously before the compass route replies | ✅ user confirmed |
| **D2** | Four operator calls parallelized (`Promise.all`), never sequential | ✅ user confirmed |
| **D3** | `prod_receipt_to_op20_seed.py` and the audit service are unrelated pipelines — don't reconcile | ✅ architect: high-conv non-issue |
| **D4** | Advisory block is persistence/benchmark-only — NOT injected into LLM context until a consumer is named and built | ✅ user confirmed |
| **D5** | Benchmark segments by fidelity source (`somatic: default` / `signal: proxy` / `axioms: llm_derived`) from day one | ✅ architect |

### A-series (assumptions, flagged)

| ID | Assumption | Confidence | Notes |
|---|---|---|---|
| **A1** | SAGE kinematic lens on the 12-element categorical proxy produces meaningful signal | Low | Proxy is semantically empty — seam, not real data |
| **A2** | `deriveAxiomsFromLlm` heuristics track real axiom compliance | Low | May conflate mention with compliance |
| **A3** | Horizon→phase (translator) and surface→phase (op20 adapter) are different concepts sharing a name | Medium | Confirm, don't reconcile |
| **A4** | FastAPI sidecar correct given constraint of reusing the 16.6K LOC Python operator library as-is | High | Forced by keeping Python operators canonical |

### User confirmations (architect↔implementer, live)

1. **Service shape:** single process port 8766, health + 4 per-operator endpoints + batch, persistence via JSONL, CORS localhost:3000. Lambda-extensible on the contract side. Don't merge batch; don't add pre-inference advisory endpoint now.
2. **Contract surface:** TS `OperatorPrimitives` ↔ Python `AuditRequest`/`AuditResponse`/`OperatorPrimitives`. Confirmed matching. Lambda-friendly decomposition (per-operator endpoints = self-contained Lambda functions; batch = single-function internal shape).
3. **Fidelity markers:** source fields are labeling, not fidelity claims. `llm_derived` ≠ ground truth. Somatic deprioritized (hardest to provide empirically without larger study).
4. **Advisory block:** persist, don't inject for now. Confirmed. Deferring pre-inference conditioning until benchmark validates the signal is worth it.
5. **op20 vs op21:** entangled, two sides of the same coin — NOT unrelated. Architect session was wrong to call them unrelated. Re-examine.
6. **Phase derivation:** two approaches on disk (surface→phase in op20 adapter vs horizon→phase in translator). Different concepts, confirm rather than reconcile.
7. **Signal proxy:** 12-element categorical proxy fed to SAGE kinematic lens is semantically empty. Treat as seam, not real data.

---

## 2. What's built and verified (this session)

### FastAPI audit service (Python) — `operators/audit_service/`

| File | Purpose | Status |
|---|---|---|
| `main.py` | FastAPI entrypoint: health + 4 per-operator endpoints + batch. CORS localhost:3000. Serves on :8766. | ✅ built + running + curl-verified |
| `schemas.py` | Pydantic models: `AuditRequest`, `AuditResponse`, `CombinedAuditResponse`, `OperatorPrimitives`, `FidelityMarkers`, `HealthResponse` | ✅ built, mirrors TS shapes |
| `translator.py` | `DecodedPrimitives` dataclass + `build_kintsugi_receipt()` — decodes TS-built dict into operator-native dataclasses | ✅ built |
| `service.py` | `run_sage()`, `run_lab()`, `run_bar()`, `run_kintsugi()` — operator runners. LAB/BAR re-run SAGE internally. | ✅ built, KINTSUGI `should_repair`→`is_healthy` fix applied |
| `persistence.py` | `store_audit_trace()`, `store_benchmark_fragment()`, `clear_store()` — writes `audit_traces.jsonl` + `benchmark_pairs.jsonl` | ✅ built, writes verified |
| `__init__.py` | Package docstring | ✅ fixed (was bare-text syntax error) |
| `requirements.txt` | fastapi, pydantic, numpy, uvicorn | ✅ present |

**Verifications done:**
- Health: `GET /api/audit/health` → `{"ok":true,"operators":["SAGE","LAB","BAR","KINTSUGI"],"version":"1.0.0"}`
- All 4 endpoints: `POST /api/audit/{sage|lab|bar|kintsugi}` → 200, `ok:true`, structured output
- Batch: `POST /api/audit/receipt` → 200, all 4 operators in one call (139.4ms total, anyFailed:false)
- Persistence: `audit_traces.jsonl` + `benchmark_pairs.jsonl` writing on disk (9 rows across 3 traceIds from test calls)
- KINTSUGI fix confirmed (was `'KintsugiDiagnosis' has no attribute 'should_repair'`; fixed to `not diagnosis.is_healthy`)

### TS audit layer — `src/lib/`

| File | Purpose | Status |
|---|---|---|
| `audit-client.ts` | `runAudit()`: parallel Promise.all fetch to 4 endpoints, 4s timeout each, fire-and-forget, gated by `AUDIT_SERVICE_URL`. Builds advisory block (persistence-only per D4). | ✅ built, Promise.all parallelized |
| `audit-translator.ts` | `translateCompassReceipt()`: compass receipt → `OperatorPrimitives` (signal, fated, axioms, somatic, hci_score, pci_score, irreversibility, onPurpose, nextAction, phaseId, signalClassification). Includes `deriveAxiomsFromLlm()`, `signalProxyFromContext()`, `fatedFromQuestionAndTrueNorth()`, `somaticPrompt` export. | ✅ built, `types.ts` created, `deriveAxiomsFromLlm` horizon param fixed |
| `audit-client-helpers.ts` | `previewAuditOutput()` + `operatorAdvisoryBlock()` — one-line summaries for context/trace | ✅ built |
| `types.ts` | `ReceiptJSON` + `AuditRequestShape` interfaces | ✅ created (was missing — import error) |

### Compass route integration — `src/app/api/compass/route.ts`

- Calls `runAudit()` AFTER receipt creation (line ~393-411), fire-and-forget, catches errors, gated by `AUDIT_SERVICE_URL`
- Does NOT inject advisory block into LLM context (D4)
- `tsc --noEmit` clean (zero errors, zero warnings)

### Pre-existing errors fixed this session

| File | Error | Fix |
|---|---|---|
| `operators/audit_service/__init__.py` | Bare text on lines 3-4 (no `#` prefix) — syntax error | Added `#` comment prefix |
| `main.py` | Bare imports `from schemas import`, `from service import`, `from persistence import` — failed at runtime | Changed to relative imports `from .schemas import` etc. |
| `service.py` | `from translator import` — bare import | Changed to `from .translator import` |
| `service.py` | `if diagnosis.should_repair:` — `should_repair` doesn't exist on `KintsugiDiagnosis` (has `is_healthy`) | Changed to `if not diagnosis.is_healthy:` |
| `src/lib/types.ts` | Missing — `import type { ReceiptJSON } from "./types"` failed | Created `types.ts` with `ReceiptJSON` + `AuditRequestShape` |
| `audit-translator.ts` | `deriveAxiomsFromLlm` input type missing `horizon` — called `input.horizon` but type was `{ stakes, doorClass, clarityMode }` | Added `horizon: string` to input type |

---

## 3. Swarm results (4 agents, first batch)

### Task 6 (TS route fixes) — COMPLETE ✅

**Result:** `tsc --noEmit` is clean. Zero errors, zero warnings.

**Contract types untouched.** No changes needed.

### Task 8 (benchmark cadence setup) — COMPLETE ✅

**Phase 0 is solid.** Service, schemas, persistence, TS client, translator, route wiring all in place and exercised. JSONL files show real pairs flowing (3 traceIds: `t2`, `t3`, `t4`; 9 rows across all 4 operators).

**9 missing items (ordered build list):**

1. Fix KINTSUGI `should_repair` attribute error → **DONE** (service.py, curl-verified)
2. Implement `loadBenchmarkPairs` in `persistence.py` → **DONE** (read API with filters)
3. Implement `loadAuditTracesPage` in `persistence.py` → **DONE** (read API with filters)
4. Translator validation script (5-10 real receipts, diff + discrepancy log) → **NOT STARTED** (protocol written, waits for DB)
5. Sampling toggle (`AUDIT_SAMPLE_RATE` env var, deterministic per-traceId hash) → **DONE** (added to persistence.py)
6. CLI reviewer (`review_pairs.py`) → **DONE** (tested, prints side-by-side)
7. CSM formula (`docs/CSM-spec.md`) → **DONE** (full formula spec)
8. `storeCompositeOutcome` + CSM computation → **NOT STARTED** (Phase 3)
9. Fidelity weighting function (per-pair weight + weighted aggregate) → **NOT STARTED** (Phase 2-3)

**Plan gaps (7):**
- CSM undefined (Phase 3 needs it; now specced in `docs/CSM-spec.md`)
- Fidelity weighting stated but not operationalized (now specced; needs weights validation)
- Sampling policy not wired (now wired: `AUDIT_SAMPLE_RATE` env var)
- Review cadence has no scheduling (no reminder; no "time to review" flag)
- No "who was right" persistence (no field exists for outcome adjudication)
- "Monthly structured review" has no sample criteria (no selection method)
- No growth plan for the pair store (no plan to graduate to queryable store)

**Persistence sufficiency:** JSONL sufficient for Phase 0-2. Becomes insufficient at Phase 3. Minimum enhancement before Phase 3: thin query layer + small SQLite index.

**`audit_traces.jsonl` vs `benchmark_pairs.jsonl`:** `benchmark_pairs.jsonl` is authoritative for benchmark purposes; `audit_traces.jsonl` is lean operational trace.

### Task 3 (skill candidates) — COMPLETE

**3 skills proposed:**
1. `arcs-outcome-loop` — trigger: receipt off Y-gate GREEN or user claims outcome. Gap: outcome-loop closure not built (CLAUDE.md §59 + PRODUCT.md §21).
2. `arcs-kairos-detection` — trigger: receipt with timing dimension. Gap: Kairos is backlog (CLAUDE.md §56); `selectMode()` encodes crude Kairos but never surfaced as instrument.
3. `arcs-observatory-replay` — trigger: replay a prior decision. Gap: Observatory is static demo + un-pushed interactive page (CLAUDE.md §61–63); no skill for replay/seed.

**2 configs proposed:**
1. Cron: nightly outcome-loop sweep — scans for GREEN Y-gate receipts with no Outcome record within N days. Makes outcome capture a habit.
2. Env-var convention: `ARCS_MODEL` — threads model choice through ADR-audit harness + compass route. Makes model-routing ADRs falsifiable.

### Task 7 (translator validation) — COMPLETE ✅

**Shape contract: sound.** ReceiptJSON fully covers every field the translator reads from `llmOutput`.

**Validation protocol written** (`audit-translator-validation.md`): Prisma query, DB→translator input mapping, two-path `llmOutput` extraction, fidelity check checklist, discrepancy log schema.

**7 gaps identified:**
- C-3 (HIGH): Somatic layer entirely default — no DB column. Add somatic self-report column + intake wire.
- C-5 (RESOLVED → ADR-034): Horizon DB→translator mapping. DB `horizon` enum
  differs from translator's expected enum. RESOLVED via `horizonToValue()` +
  `horizonToPhaseId()` in `audit-translator.ts` — translator reads DB `horizon`
  and maps it inline (no separate mapping layer needed). Documented in ADR-034.
  E2 experiment → RESOLVED.
- C-1 (MEDIUM): `geometry.macros_on/off` only in `rawResponse`. Older receipts lose this data.
- C-4 (MEDIUM): HCI always proxy — no user self-report in DB. HCI and PCI become correlated.
- C-2 (LOW): `is_satoshi` in ReceiptJSON but never consumed.
- C-6 (LOW): `prep` fields accepted but ignored.
- C-7 (LOW): No `reasoning.geometry` stored as separate DB columns.

**Bottom line:** No translator bugs. All fidelity concerns are DB storage-layer data availability constraints.

### Task 9 (volunteer segments) — COMPLETE ✅

Four briefs written to `docs/volunteer-segment-briefs.md`:

1. **Seed enrichment (somatic self-report):** `somaticPrompt` exists as string constant (all 6 questions). But nothing collects the scores — no UI, no wire from form→translator→somatic.source. Next step: add 6 questions to prep/intake, pass scores through request body, wire into translator so `somatic.source` becomes `"user_self_report"`.
2. **ARCS volunteer-facing docs:** `arcs-operator-table` + `arcs-reading-sequence` skills exist and are comprehensive. But no "developing for ARCS" guide, no onboarding doc bridging skills into contributing flow, no operator invocation cookbook. Next step: write 1-2 page volunteer onboarding doc sequencing existing skills into contribution flow.
3. **OPFOR realism discipline (LAB adversarial lens):** LAB exists as fully implemented operator (28KB, Phase 3 READ-WRITE). Runs in audit pipeline. But OPFOR discipline NOT realized in compass route's pre-inference path — only SAGE runs as pre-screen (D4). LAB doesn't run before LLM response. Discipline exists only as benchmark comparison target. Next step: accumulate paired evidence (LLM loki_challenge vs LAB challenge_statement, etc.) in benchmark store and review on cadence. Discipline realized by evidence, not wiring.
4. **L5 / runtime hooks (post-compass composition, alternate paths, anticipatory briefing):** Compass route creates Receipt + returns it with Y-gate state. Post-compass side effects: fire-and-forget `runAudit`, invisible `SageTrace`, receipt confirmation email (T₀), scheduled debrief email (T+7). But no explicit post-compass composition layer, no alternate-path exploration runtime, no anticipatory briefing hook beyond T+7, no receipt-created event/webhook. FM-10 flags "No Hermes workflow composition of operators" as structural gap. Next step: define smallest concrete post-compass hook — receipt-created event/webhook; start with anticipatory briefing use case enriching existing email path with Y-gate-driven guidance.

---

## 4. Build backlog (remaining, from agent 8's findings)

### Phase 1 (unblocks evidence collection) — built this session

| # | Item | Status |
|---|---|---|
| **13** | `loadBenchmarkPairs` in `persistence.py` — filter by traceId/operator/fidelity/date range | ✅ DONE — read API with filters, verified against live JSONL |
| **14** | `loadAuditTracesPage` in `persistence.py` — paginated read | ✅ DONE — read API with filters, verified against live JSONL |
| **15** | Sampling toggle (`AUDIT_SAMPLE_RATE` env var, deterministic per-traceId hash) | ✅ DONE — added to persistence.py, env-gated |
| **16** | CLI reviewer (`review_pairs.py`) — loads pairs, prints side-by-side LLM vs operator | ✅ DONE — tested, prints side-by-side (SAGE/LAB/BAR/KINTSUGI) |
| **17** | Translator validation script (5-10 real receipts, diff + discrepancy log) | ⏳ NOT STARTED — protocol written (`audit-translator-validation.md`), waits for DB |

### Phase 1.5 (when DB is available)

| # | Item | Notes |
|---|---|---|
| **17** | Translator validation script — run 5-10 real receipts through `translateCompassReceipt`, diff + log discrepancies | **NOT STARTED** — protocol in `audit-translator-validation.md`; script waits for DB |

### Phase 2-3 (future-proofing + composite metrics)

| # | Item | Phase | Priority |
|---|---|---|---|
| **18** | Fidelity weighting function — per-pair weight from somatic/hci/axioms source, weighted aggregate | 2-3 | Medium |
| **19** | `storeCompositeOutcome` + CSM computation in persistence/service | 3 | Medium |
| **20** | Consolidate stores — `benchmark_pairs.jsonl` authoritative, `audit_traces.jsonl` lean operational trace | 2 | Low |
| **21** | Monthly structured review template (markdown/JSON) — 5 review questions + who-was-right + unresolved flag | 2 | Low |
| **23** | Migrate to SQLite/queryable store when pair count justifies (Phase 3-4) | 4 | Low (future) |

### Phase 3 prep (design task, not build)

| # | Item | Notes |
|---|---|---|
| **16** | CSM formula (`docs/CSM-spec.md`) — alignment, delta, coherence_loss, severity → [0,1] | ✅ DONE — full formula spec, per-operator subtask maps, coherence loss per operator, severity computation, fidelity adjustment, aggregate weighting, 5 open questions |

---

## 5. Runtime state

| Component | Status |
|---|---|
| FastAPI audit service | Running on `:8766`. Health + 4 endpoints + batch verified. KINTSUGI now returns `ok:true`. |
| `tsc --noEmit` | Clean (zero errors, zero warnings) |
| `audit_traces.jsonl` | 9 rows (t2 SAGE/LAB/BAR/KINTSUGI, t3 KINTSUGI, t4 SAGE/LAB/BAR/KINTSUGI) |
| `benchmark_pairs.jsonl` | 9 rows (same traces/operators) |
| KINTSUGI bug | **FIXED** in `service.py` (`if not diagnosis.is_healthy:`). New calls return `ok:true` (curl-verified). |

---

## 6. Next action

**Task 4 (synthesis report) is the next deliverable.** It synthesizes tasks 3, 7, 8, and 9 into a single actionable report. The four agent outputs are all read and synthesized into this state file. Task 4 should be a concise, grounded recommendations report covering:
- What's built and decided (summary)
- Recommendations from each swarm task (skills/configs, translator validation, benchmark cadence, volunteer segments)
- Prioritized build backlog (what to build next, in order)
- What's deferring to later phases
- Known risks/gaps that need attention before the benchmark cadence can produce reliable evidence

This is the report the user asked for when they said "launch task 4" — the grounded synthesis of everything the swarm found.
