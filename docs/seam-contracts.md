# Seam Contracts — Hermes-harness (audit_service)

> **JTBD-C.** Every shared-state exchange point named, with its input/output shape, failure mode, and
> guard. Contract-defining doc — task 19 (`store_csm_result`) implements to Seam 2 below. Frame as of
> `feat/audit-service` @ bc28c371.

---

## Seam 1 — compass route → audit service (fire-and-forget)

- **Where:** `src/lib/audit-client.ts` `runAudit()`, called from the compass route *after* LLM output.
- **Input:** translated `OperatorPrimitives` + `llmOutput` → POST `/api/audit/{sage,lab,bar,kintsugi}` (or `/receipt`).
- **Output:** advisory operator audit, injected into Claude's context; trace persisted as a **side effect**.
- **Failure mode:** timeout or non-200 → **log and continue.** The compass decision is never blocked or altered (Invariant I1).
- **Guard:** bounded-timeout fetch, mirrors the existing `SAGE_URL` pattern; `catch` → advisory dropped, compass proceeds.

## Seam 2 — audit endpoint → persistence  ← **task 19 lands here**

- **Where:** `main.py::_persist` → `persistence.py::{store_audit_trace, store_benchmark_fragment, [19] store_csm_result}`.
- **Input:** `(traceId, sessionVersion, operator, …payload)`; `store_benchmark_fragment` also takes `operator_coverage`.
- **Output:** one appended JSONL row per `(traceId, operator)` in the relevant store; nothing returned.
- **Failure mode:** **best-effort, never raises** (I2). Not sampled → silent skip (I7). Disk error → `pass`.
- **Guard:** module `_LOCK` (I4) + `try/except pass` in `_persist`.
- **Contract task 19 MUST satisfy:**
  - append-only JSONL row (I3), path env-overridable (e.g. `AUDIT_CSM_FILE`, default alongside module)
  - sampling-gated via `_should_sample(traceId)` (I7); serialized under `_LOCK` (I4); never raises (I2)
  - row keyed by `(traceId, sessionVersion, operator)` (I5); include the `compute_csm` value + inputs used
  - called from `_persist` (once the CSM is available) — do NOT add a second write path that bypasses the guard

## Seam 3 — stores → read/UI (internal)

- **Where:** `persistence.py::{loadBenchmarkPairs, loadAuditTracesPage, audit_store_stats}` → API/UI.
- **Input:** pagination (`limit`, `offset`); **Output:** JSONL rows / aggregate stats.
- **Failure mode:** missing/empty file → empty page (never raises). **Internal/admin only** (I6).
- **Guard:** `_read_jsonl` bounded reads; results not exposed as end-user decision output.

## Store separation (informs JTBD-20)

- `audit_traces.jsonl` — lean operational trace, one row per `(traceId, operator)`.
- `benchmark_pairs.jsonl` — full fragment (primitives + llmOutput + result + coverage) for the efficacy study.
- **Task 19's CSM results** are a *third* concern: persisted computed scores. Keep them a distinct store
  (`csm_results.jsonl`) rather than overloading either existing file — task 20 consolidates/documents the
  three-store separation on top of this.

## The DB-seam question (deferred, honest)

The earlier "DB down / retry / backoff" concern does **not** apply yet: the current store is **append-only
local JSONL files, not a database.** The current guard is best-effort file append (disk error → `pass`).
A real DB seam contract (connection failure, retry/backoff, fallback) **activates at task 23** (SQLite/
Postgres migration) and is out of scope until then. Flagged here so it isn't mistaken for a live gap.
