# Surface Composition — ARCS v9

> **JTBD-B.** Each surface declares which kernel pieces it composes, and at what **voltage** (importance:
> how load-bearing the piece is to that surface) and **current** (frequency: how often it fires per
> request). High/Med/Low on each axis. Derived from the route sources on `feat/audit-service` @ 2529ec56.

Legend — **V** = voltage (criticality), **C** = current (call frequency per request).

---

## Compass — `POST /api/compass` (the core)

| Kernel piece | V | C | Role |
|---|---|---|---|
| `@anthropic-ai/sdk` (L0–L5 pipeline) | **High** | High | The decision engine — sharpens question → DEWY output |
| `ygate.computeYGate` | **High** | 1×/req | Constitutional Y-gate → state + render resolution |
| `prisma` (receipt.create, sageTrace.create, user.find/update, receipt.update) | High | High | Persist receipt + lineage |
| `lib/sanitize` (clampText/Int/Array) | High | High | Input guard on every user field |
| `lib/ratelimit` | Med | 1×/req | Abuse guard (`clientIp`) |
| `lib/auth` | Med | 1×/req | Anonymous allowed (ADR-016) → soft identity |
| `resend` + `emails/*` (debrief, receipt) | Low | ≤1×/req | Side-effect delivery, non-blocking |
| `lib/env`, `unstable_cache` | Low | n | Config + memoization |
| **audit_service harness (`runAudit`)** | — | **0** | **SEAM — not wired.** Would attach here as fire-and-forget (Seam 1) |

## Brief — `GET /api/brief/[receiptId]`

| Kernel piece | V | C | Role |
|---|---|---|---|
| `@anthropic-ai/sdk` (messages.create ×2) | **High** | High | Two-column cartography generation |
| `prisma` (brief find/create, receipt.find) | High | Med | Read receipt, cache brief |
| `lib/auth` | Med | 1× | Ownership check |
| `lib/sanitize` | Med | Med | Guard generated inputs |

## Guide — `GET /api/guide/[receiptId]`

| Kernel piece | V | C | Role |
|---|---|---|---|
| `@anthropic-ai/sdk` (messages.create) | **High** | Med | Step-by-step guide surface |
| `prisma` (prepGuide find/create/update, receipt.find) | High | Med | Read receipt, persist guide |
| `lib/auth`, `lib/env` | Med | 1× | Ownership + config |

## Prep — `POST /api/prep`

| Kernel piece | V | C | Role |
|---|---|---|---|
| `prisma` (prepSession.create) | High | 1× | Persist the calibration instrument |
| `lib/auth` | Med | 1× | Attach to user |

_Lowest-complexity surface — pure calibration capture, no LLM._

## History — `GET /api/history`

| Kernel piece | V | C | Role |
|---|---|---|---|
| `prisma` (receipt.findMany) | High | 1× | The world's memory (WORLD.md) |
| `lib/auth` | **High** | 1× | Scopes to the user — no cross-user leak |
| `lib/flags` | Low | 1× | Feature gating |

## Auth — `/api/auth/[...nextauth]`

| Kernel piece | V | C | Role |
|---|---|---|---|
| `lib/auth` (handlers) | **High** | 1× | Magic-link identity (Auth.js v5 + Resend) |
| `lib/ratelimit` | Med | 1× | Guard the auth endpoint |

---

## The harness as a surface (audit_service)

| Kernel piece | V | C | Role |
|---|---|---|---|
| operators SAGE/LAB/BAR/KINTSUGI (`service.py`) | **High** | 4×/receipt | The four audit runners |
| `coverage_hooks.record_coverage` | Med | **1×/receipt** | Approach D coverage (once per receipt — I5) |
| `persistence` (store_audit_trace, store_benchmark_fragment, [19] store_csm_result) | High | per-op | Append-only JSONL stores (Seam 2) |
| `compute_csm` + Task-18 fidelity weighting | High | per-pair | Coherence score + fidelity-weighted aggregates |

---

## Reading the map

- **Highest-voltage pieces** are `ygate` (compass), `lib/auth` (history/auth), and the Anthropic SDK
  (every generative surface). These are where a regression is most load-bearing.
- **Highest-current** is the Anthropic SDK + `prisma` + `sanitize` on the compass path — the hot loop.
- **The one dark seam** is `runAudit` on the compass route: the harness exists and verifies (this branch)
  but is not yet composed into the live decision path. Wiring it is a fire-and-forget attach per Seam 1,
  bound by Invariant I1 (never blocks compass). That wiring is the harness's path to production use.
