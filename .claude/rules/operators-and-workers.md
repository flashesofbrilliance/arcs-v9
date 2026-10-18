---
paths:
  - "operators/**"
  - "src/app/api/**"
---

<!-- Moved verbatim from AGENTS.md "## Agents & workers map" on 2026-10-17 (WS1 lazy loading). Loads when Claude reads, writes or edits a matching file. -->

# Agents & workers map (live routes, backlog, foundation, Operators Library)

### Live (built)
| Agent / Worker | Type | File | Notes |
|---|---|---|---|
| Compass | Route Handler | `src/app/api/compass/route.ts` | Full Claude L0–L5 + Y-gate + persistence |
| Prep | Route Handler | `src/app/api/prep/route.ts` | PrepSession CRUD |
| Brief | Route Handler | `src/app/api/brief/[receiptId]/route.ts` | |
| Guide | Route Handler | `src/app/api/guide/[receiptId]/route.ts` | |
| History | Route Handler | `src/app/api/history/route.ts` | |
| Auth | Auth.js Handler | `src/app/api/auth/[...nextauth]/route.ts` | Magic link, not end-to-end validated yet |
| Y-gate | Pure function | `src/lib/ygate.ts` | Called inline by compass |
| **Operator MCP bridge** | stdio MCP server | `operators/arcs_mcp_bridge.py` (+ `mcp-bridge.sh`, `.mcp.json`) | Exposes the operator suite to Claude Code: `list_operators` · `describe_operator` · `run_operator` · `run_cis` · `run_inchworm` · `ledger_tail`. Dispatches by `operators/OPERATOR-REGISTRY.json` (generated, grep-verified, numbering LOCKED to `operators/docs/PERIODIC-TABLE.md`). UNBUILT/PARTIAL/BLOCKED operators answer `status=blocked` + reason, never a fake. Every call appends to `operators/ledger/operator-receipts.jsonl` (append-only; Supabase sync = later idempotent projection). Self-test: `operators/mcp-bridge.sh --self-test` |

### Backlog (not built)
| Agent / Worker | Type | Priority | Notes |
|---|---|---|---|
| Outcome handler | `POST /api/receipts/[receiptId]/outcome` | ✅ BUILT · gap=capture | **Shipped** (2026-09-02 correction): route + `Outcome` model + debrief-email nudge + drift read (`matched`→LANDED/DRIFTING, status→LOGGED). By design the human supplies `matched`/`regretScore` — a receipt can't close itself (§5.1, *In datis veritas*). NOT wired: any `receipt_outcome_matched` analytics event. **Real P1 gap = capture rate** — 2/247 closed; the harness's validation target (`Outcome.matched`/`regretScore` vs `nciScore`/CSM) exists but n=2. This, not "make SAGE fire," is the keel. See "Receipt save prompt". **Provenance (2026-10-06):** `Receipt.provenance` (`real` \| `test` \| null) is set by the owner only, never guessed, never auto-tagged. Write path: `POST /api/receipts/[receiptId]/provenance` (owner-only, 404 for anonymous rows and other accounts; a receipt carrying a synthetic outcome cannot be tagged `real`) + the Provenance control on `/receipt/[id]`. `scripts/provenance_candidates.py` (read-only, stdlib) lists the owner's untagged rows for a one-pass tag. The Accountant splits cohorts on it (`operators/prod_receipt_to_accountant.py`); measured 2026-10-06 in prod: real 0, test 189, null 78 of 267. |
| Receipt save prompt | Middleware / UI | P1 | Biggest PLG gap — soft auth nudge |
| GIGI substrate client | Lib | P2 | `src/lib/gigi.ts` — seam point in compass/route.ts |
| Stripe billing gate | Middleware | P3 | Gates COURT/DEEP mode |
| Kairos detection | Background job | P4 | Machinery in `scripts/` via ADR-023; gated at 100 receipts |
| Observatory / replay | Worker | P4 | Machinery in `scripts/` (lattice_sim, Folksonomist); gated at 100 receipts |

### Foundation (production-ready, stdlib-only Python)
| Component | File(s) | Purpose | Status |
|---|---|---|---|
| ARCS Core Kernel | `scripts/arcs_core.py` | Double Helix, Triune Logic, archetype taxonomy, Folksonomist operator | READY |
| Scanner Suite | `scripts/calendar_scan.py`, `reader_scan.py`, `listening_scan.py`, `network_scan*.py`, `forensic_scan.py`, `archetype_scan.py` | Extract OM from personal data across 6 domains | READY |
| Analysis Pipeline | `scripts/arcs_cli.py` | 5-verb framework (analyze/assess/evaluate/synthesize/recapitulate) | READY |
| Simulation Harness | `scripts/lattice_sim.py` | ADR-023 observability lattice structural testing | READY |
| Utilities | `scripts/score_me.py`, `export_apollo.py`, activation-check.sql, rls-policies.sql, smoke.sh | Scoring, export, audit, testing | READY |

### Operators Library (atomic design components, L0-L5 implementation)
| Layer | Component | File | LOC | Purpose | Status |
|-------|-----------|------|-----|---------|--------|
| **Meta-Operators** | LAB | `operators/arcs_operators_lab.py` | 28KB | Loki/Advisors/Bayesian — three-lens adversarial reasoning | READY |
| | BAR | `operators/arcs_operators_bar.py` | 19KB | Risk/ruin assessment — boundary conditions | READY |
| | SAGE | `operators/arcs_operators_sage.py` | 29KB | Sage reasoning — somatic + epistemic | READY |
| | CURATOR | `operators/arcs_operators_curator.py` | 13KB | Multi-perspective synthesis | READY |
| | KAIROS | `operators/arcs_operator_kairos.py` | 9.4KB | Timing operator — horizon/window | READY |
| | CONTRACT | `operators/arcs_operator_contract.py` | 9.8KB | Constitutional reasoning | READY |
| | OPERATOR20 | `operators/arcs_operator20.py` | 38KB | Phase 5 synthesis · Folksonomy Cultivator (54-dim DBSCAN) | READY |
| | OPERATOR21 | `operators/arcs_operator21.py` | 24KB | Anterior/posterior spline inference — knot resolution. P1 determinism PASS (2026-08-28) | READY |
| | KINTSUGI | `operators/arcs_kintsugi.py` | 26KB | Phase gate validation + healing | READY |
| | ACCOUNTANT (Op 19) | `operators/arcs_accountant.py` + `prod_receipt_to_accountant.py` | 15KB | The Scoreboard: per-cohort (founder/external/anonymous) closed positions, closure rate, fates; NCI-vs-outcome calibration only at n>=30 closed per cohort, else `sufficiency=insufficient` with n. Bound in the registry (`callable`, `run`); report `_STATE/2026-09-27-accountant-scoreboard.json` | READY |
| | ECHO EMBEDDING (RC-OPS-001 companion) | `operators/arcs_echo_embedding.py` | 11KB | Embedding-backed `signature_fn` / `orthogonality_fn` for `OrthogonalEchoDetector` (same local model as `arcs_api.py` `/api/embed`; orthogonality = 1 - cosine of domain TEXT vectors, names are only the lookup handle). `scripts/echo_ridgeline_feed.py --signature embedding` / `--compare` for before/after; first run 2026-09-27: scrambled-control FP 0.8 -> 0.0, but 0 real echoes once the shared-template control drops boilerplate lines (`_STATE/2026-09-27-echo-signature-before-after.json`). Needs the declared `embeddings` extra in `operators/.venv` | READY |
| **Primitives** | Core Elements | `operators/arcs_primitives.py` | 23KB | CoherenceSignal/Receipt, ARCS Law (C = αA - β(S-S_min)² + γW) | READY |
| | Bridge | `operators/arcs_primitives_bridge.py` | 10KB | Type conversions | READY |
| | Receipt | `operators/arcs_receipt_core.py` | 7.6KB | Receipt contract | READY |
| **Systems** | Constitutional Court | `operators/arcs_constitutional_court.py` | 25KB | Axiom enforcement | READY |
| | Heart/Coherence | `operators/arcs_hc.py` | 34KB | Coherence metrics | READY |
| | LTE | `operators/arcs_lte.py` | 46KB | Trajectory modeling | READY |
| | ROM | `operators/arcs_rom.py` | 19KB | Motion rules | READY |
| | Trace | `operators/arcs_trace.py` + `arcs_trace_loki.py` | 79KB | Execution tracing | READY |
| **Infrastructure** | Pipeline | `operators/arcs_pipeline_v1.py` | 20KB | Operator sequencing | READY |
| | Runtime | `operators/arcs_runtime_service.py` | 28KB | State management | READY |
| | API | `operators/arcs_api.py` | 40KB | External interface | READY |
| | CLI | `operators/cli_arcs_run.py` | 28KB | CLI harness | READY |
| | Storage | `operators/arcs_store.py`, `arcs_yoav_store.py` | 42KB | Persistence | READY |
| **Harness** | Client / Pipeline / Evaluator | `operators/operator_client.py`, `pipeline_runner.py`, `receipt_evaluator.py` | 52KB | ls-enum lambda client + operator sequencing + receipt scoring | READY |
| | Prod→op20 adapter | `operators/prod_receipt_to_op20_seed.py` | 4.8KB | Maps prod Receipt columns → op20 54-dim seed (faithful; never fabricates somatic/axiom) | READY |
| **Total** | see census note ↓ | `operators/` | **~21.9K LOC tracked** | **Atomic design components for L0–L5 decision pipeline** | **PRODUCTION** |

> **File census (authoritative, reconciled 2026-09-04).** The table above is a *curated catalog*
> of the core L0–L5 components, not a file count — which is why three different numbers were in
> circulation (this line said "34 files", the atlas said "38 py files", `ls` showed "44 entries").
> Counted once against the tracked tree on main (recounted 2026-09-04): **52 top-level `.py` modules · 52 `.py`
> files total** (recursive, excludes `__pycache__`) **· 62 tracked files total · 22,171 LOC**.
> Tracked subdirs: `core/` (7), `docs/` (4), `linkedin_pipeline/` (3). `audit_service/` is a
> separate WIP thread and is **not** part of this library census. Recount with:
> `git ls-files 'operators/*.py' | wc -l` (top-level) and `git ls-files operators/ | grep '\.py$' | wc -l` (all).
> (The old `operators/**/*.py` glob only matched files two-plus levels deep, so it could never reproduce the top-level count.)

**Integration status:** Operators are canonical alternative implementation. Not currently wired into compass route (which uses Claude L0–L5). Future integration: custom decision domains, audit hooks, phase gates for high-consequence decisions.

---
