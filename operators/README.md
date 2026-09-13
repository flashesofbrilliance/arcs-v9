# ARCS Operators Library — Atomic Design Components

> **Status:** Reference implementation — module-level Python, **not wired into the live
> compass route or any deployed surface**. Relabeled 2026-07-11: the prior
> "Production-ready canonical" claim was not backed by integration, deployment, or
> end-to-end test evidence (see `_PATTERNS/2026-07-11-operator20-archaeology.md`,
> Collision Report #3).
> **Version:** v9.0
> **Total:** 34 files, 16.6K LOC, 736 KB

This directory contains the atomic design components that compose the ARCS decision engine. These operators implement the L0–L5 decision pipeline at component resolution, providing the modular building blocks for decision intelligence.

## Architecture

### Core Meta-Operators (Decision Reasoning)

| Operator | File | LOC | Purpose |
|----------|------|-----|---------|
| **LAB** | `arcs_operators_lab.py` | 28KB | Loki/Advisors/Bayesian — Three-lens adversarial reasoning |
| **BAR** | `arcs_operators_bar.py` | 19KB | Risk/ruin assessment — boundary analysis |
| **SAGE** | `arcs_operators_sage.py` | 29KB | Sage reasoning — somatic signal + epistemic confidence |
| **CURATOR** | `arcs_operators_curator.py` | 13KB | Curatorial selection — multi-perspective synthesis |
| **KAIROS** | `arcs_operator_kairos.py` | 9.4KB | Timing operator — window/horizon analysis |
| **CONTRACT** | `arcs_operator_contract.py` | 9.8KB | Constitutional reasoning — axiom compliance |
| **OPERATOR20** | `arcs_operator20.py` | 38KB | Phase 5 operator — advanced synthesis |
| **KINTSUGI** | `arcs_kintsugi.py` | 26KB | Repair/healing — phase gate validation |

### Atomic Elements (Primitives)

| Component | File | Purpose |
|-----------|------|---------|
| **Primitives** | `arcs_primitives.py` | Core data structures: CoherenceSignal, CoherenceReceipt, FATEDReasoning, AxiomCheck, SomaticReading. Defines ARCS Law: C = αA - β(S-S_min)² + γW |
| **Bridge** | `arcs_primitives_bridge.py` | Type bridges and conversions between operator outputs |
| **Receipt Core** | `arcs_receipt_core.py` | Receipt representation and storage contract |

### Pipeline & Orchestration

| Component | File | Purpose |
|-----------|------|---------|
| **Pipeline** | `arcs_pipeline_v1.py` | Pipeline composition — operator sequencing |
| **Runtime Service** | `arcs_runtime_service.py` | Runtime execution and state management |
| **API Layer** | `arcs_api.py` | External API interface to operators |
| **CLI Runner** | `cli_arcs_run.py` | Command-line execution harness |

### Major Systems

| System | File | LOC | Purpose |
|--------|------|-----|---------|
| **Constitutional Court** | `arcs_constitutional_court.py` | 25KB | Constitutional reasoning engine — axiom enforcement |
| **Heart/Coherence (HC)** | `arcs_hc.py` | 34KB | Coherence calculation — alignment metrics |
| **LTE** | `arcs_lte.py` | 46KB | Long-term expectation — trajectory modeling |
| **Rules of Motion (ROM)** | `arcs_rom.py` | 19KB | Canonical motion rules |
| **Trace** | `arcs_trace.py` | 39KB | Execution tracing and debugging |
| **Trace Loki** | `arcs_trace_loki.py` | 40KB | Loki adversarial trace analysis |
| **CIS** | `arcs_cis.py` | 22KB | Cognitive Interface System ("Babel Fish") — HC→LTE integration: altitude detection + cognitive-safety-modulated signal encoding (per the file's own header) |
| **Diagnostic** | `arcs_diagnostic.py` | 17KB | System diagnostics and validation |

### Storage & Infrastructure

| Component | File | Purpose |
|-----------|------|---------|
| **Store** | `arcs_store.py` | Core storage layer |
| **Yoav Store** | `arcs_yoav_store.py` | Global serializability layer — ordered commit log + conflict detection across multi-future (YOAV clock) state (per the file's own header) |
| **Substrate** | `arcs_substrate.py` | Substrate/foundation layer |
| **BAR Seeding** | `arcs_seed_bar.py` | BAR operator initialization |
| **Backup** | `arcs_backup.py` | Backup utilities |
| **Kinematics** | `arcs_kinematics.py` | Movement/motion primitives |
| **DEWY Log** | `arcs_dewy_log.py` | DEWY decision logging |
| **No-Go Inventory** | `arcs_no_go_inventory.py` | Constraint/boundary tracking |
| **Init Bundles** | `arcs_init_bundles.py` | Initialization helpers |
| **Battery** | `arcs_battery.py` | Energy/persistence system |

### Testing & Fixtures

| Component | File | Purpose |
|-----------|------|---------|
| **Test Receipts** | `seed_test_receipts.py` | Test fixture generator |

### ROM Candidates — Experimentation (not yet canonical)

> Everything above this section is production-ready canonical. Everything below
> is explicitly **not**. Do not treat as constitutional; do not depend on its
> output for any decision-gating logic until promoted.

| Operator | File | RC ID | Promotion trigger |
|----------|------|-------|--------------------|
| **INCHWORM+ECHO** | `arcs_inchworm_echo.py` | RC-OPS-001 | Observatory period — findings must be logged and replayed through Observatory across multiple real sessions, with severity grading and named patterns confirmed accurate in hindsight, before promotion to full ROM. See file header and `_PATTERNS/2026-06-23-governance-roadmap.md` task #7. |
| **PROFILE-SCAN-FOLKSONOMY-TIGHTENING** | `_SPECS/profile-scan-spec-v1.md` (§ "Term collision") | RC-OPS-002 | Hypothesis: term variation across Profile Scan block variants (Thread/Signal/5D/Genome meaning different things per document) is folksonomy edge-weight tightening, not inconsistency to standardize away — per the Folksonomist operator (`arcs_core.py`) and ADR-023's model. **Promotion gate = measured-baseline-stability, NOT a magic number.** The "100+ receipts" in ADR-020/023 is arbitrary (ADR-020 itself says 50 in two places, 100 in a third); the real, non-arbitrary condition is ADR-023's own `g > Gini_baseline(corpus)` where the baseline is a *measured* quantity. Promote when the corpus's measured Gini/Zipf baseline has stabilized (stops moving materially as N grows / CI tight enough) — possibly well under 100 — and only if the terms are then shown to actually be converging, not just accumulating. Corpus this session was n=5; convergence is NOT yet measurable. **Update 2026-07-13: the receipt-corpus Gini baseline now exists** — Gini_baseline(233) = 0.577, still drifting (+0.02/checkpoint, argmax attractor flipped BAR→KAIROS in the last 60 receipts) ⇒ NOT yet stabilized; see ADR-023's 2026-07-13 amendment for method + full table. |

## Key Relationships

```
INPUT: CoherenceSignal
  ↓
SAGE (epistemic confidence, somatic reading)
  ↓
LAB (adversarial challenge, Bayesian posterior)
  ↓
BAR (ruin risk, boundary conditions)
  ↓
CURATOR (multi-perspective synthesis)
  ↓
KINTSUGI (phase gate validation)
  ↓
OUTPUT: CoherenceReceipt (signed, sealed, witnessed)
```

## ARCS Law

The canonical coherence equation governing all operators:

```
C = αA - β(S - S_min)² + γW

where:
  C = Coherence (decision quality)
  A = Alignment with DNA axioms
  S = Surprise (deviation; minimized when S = S_min)
  W = Witness (somatic signal validation)
  α = 0.5 (axiom weight)
  β = 0.3 (surprise penalty)
  γ = 0.2 (witness weight)
```

## Documentation

- **Operator Deep Dives:** `docs/ARCS-Operator17-AdversarialDetective.md`, `docs/ARCS-Operator20-FolksonmyCultivator.md`
- **Atomic Design Guide:** `docs/ARCS-AtomicDesign-ProductionGuide.md`
- **Periodic Table of Elements:** `docs/PERIODIC-TABLE.md`

## Development Notes

**Dependencies (corrected 2026-07-11 — the prior "all operators are stdlib-only" claim was false):** 12 of 34 files import numpy and/or scipy: `arcs_api`, `arcs_hc`, `arcs_constitutional_court`, `arcs_kinematics`, `arcs_operators_bar`, `arcs_operators_lab`, `arcs_operators_curator`, `arcs_operators_sage`, `arcs_pipeline_v1`, `arcs_primitives`, `arcs_store`, `waveform_optimizer` (verified by grep). The remaining 22 are stdlib-only. Operators are composable and testable in isolation.

**Status (relabeled 2026-07-11):** These operators are a reference implementation of the ARCS decision reasoning engine at component resolution. They complement (not replace) the Claude L0–L5 pipeline in the compass route — but they are not integrated with it, and no deployment or end-to-end evidence backs a "production-ready" label.

**Integration:** Currently not wired into the compass route (which uses Claude). Future integration points:
- Custom operator chains for specialized decision domains
- Audit/trace hooks for decision transparency
- Phase gate enforcement for high-consequence decisions

## Composition Boundary — Agentic Harness (external consumer)

`operators/` is the atomic component catalog only. It does not contain
orchestration, delegation-by-JTBD, RAG/model routing, sealed-environment
builders, multi-tenant runtime, or artifact rendering (ziggeraut/russian-doll,
UA/player schema, ticket outputs). Those live in `harness/` at repo root,
as a separate composition layer that *consumes* operators — it does not
extend this catalog's taxonomy.

**Public contract (what harness/ may depend on):**
- TODO: enumerate the operator modules exposed as stable harness-facing
  surface (expected candidates: `arcs_pipeline_v1.py`, `arcs_runtime_service.py`,
  `arcs_api.py`, `arcs_receipt_core.py`, `arcs_operator_contract.py` — confirm
  against harness JTBD list before finalizing).
- TODO: state which exports are contract-stable (harness may pin to them)
  vs. internal (harness must not reach past the declared entry points).
- TODO: multi-tenant isolation — confirm no operator module holds
  process-global/module-level mutable state that would leak `user0` into a
  net-new tenant's execution; flag any that do as harness-blocking until
  refactored or explicitly scoped per-tenant by the caller.

**Not owned here:** JIT compile-from-entry-point, decentralized ID refs,
polymorphic surface composition, sealed-env/external-dependency integration.
See `harness/README.md` (TODO: create on first harness commit) for those.
