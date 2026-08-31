# Sovereignty Boundary — Hermes-harness (audit_service)

> **JTBD-E.** The line between what the harness *enforces* (invariants — must hold, surfaces cannot
> override) and what each surface *declares* (configuration — may vary). Contract-defining doc: task 19
> (`store_csm_result`) and any new store/seam work must conform to the invariants below, not redefine them.
> Frame as of `feat/audit-service` @ bc28c371.

---

## 1. Harness-enforced INVARIANTS (must hold; no surface may override)

| # | Invariant | Enforced by |
|---|---|---|
| I1 | **Audit is a side effect. It never blocks or alters the compass decision path.** | Fire-and-forget call after LLM output (`audit-client.ts`); compass returns regardless |
| I2 | **Persistence is best-effort — a store write never raises into its caller.** | `try/except … pass` in `_persist`; each `store_*` "never raises" per its docstring |
| I3 | **Stores are append-only. Prior rows are never mutated in place.** | `store_*` append one JSONL line; no rewrite path exists |
| I4 | **Writes are serialized (thread-safe).** | Single module `_LOCK` in `persistence.py` |
| I5 | **Receipt identity = (`traceId`, `sessionVersion`). Per-receipt work runs once.** | `_coverage_key`; coverage cache; store rows keyed by the pair |
| I6 | **Raw audit traces are internal/advisory — never surfaced to the end user as decision output.** | `audit-client.ts` header: traces persisted as side effect, injected only as advisory context |
| I7 | **Sampling gates writes uniformly.** A row is written iff `_should_sample(traceId)`. | `_should_sample` guards every `store_*` |

**These bind task 19.** `store_csm_result` MUST: append-only JSONL (I3), sampling-gated (I7),
under `_LOCK` (I4), never raise (I2), keyed by (`traceId`, `sessionVersion`, `operator`) (I5). It must NOT
mutate existing rows, block the endpoint, or expose results to end users.

## 2. Surface-DECLARED configuration (may vary per surface/deployment)

| Config | Mechanism | Default |
|---|---|---|
| Which operators run (SAGE/LAB/BAR/KINTSUGI) + order | endpoint choice (`/api/audit/*`, `/receipt` runs all) | all four |
| Sampling fraction | env `AUDIT_SAMPLE_RATE` ∈ (0,1] | unset = always write |
| Store file paths | env `AUDIT_BENCH_FILE`, `AUDIT_TRACE_FILE` (+ 19: e.g. `AUDIT_CSM_FILE`) | alongside module |
| Service port | env `AUDIT_SERVICE_PORT` | 8766 |
| Inject audit as advisory into LLM context | compass-route wiring (`runAudit`) | on (advisory only) |
| Operator implementation swap | **proposed** `ARCS_MODEL` (JTBD-D) | not wired |

**Declaration mechanism today = environment variables.** A config-file layer is future work; when it lands,
it declares the same axes — it does not move any Row-1 invariant into configurable space.

## 3. The boundary rule (one sentence)

**A surface may choose *which* operators run, *how often* (sampling), and *where* results are stored — but
never *whether* audit stays a non-blocking, best-effort, append-only, once-per-receipt side effect.** That
part is the harness's, not the surface's.
