# Python Audit Service — Hosting Scope

> **Status:** SCOPED — awaiting direction.  
> **Date:** 2026-08-27  
> **Author:** Claude Sonnet 4.6 (per user steer)  
> **Related:** `operators/audit_service/`, `src/lib/audit-client.ts`, `docs/audit-service-interface.md`

---

## What we're deciding

Where to host the Python FastAPI audit service so `app.arcs.care`'s compass route can call it in production.

The service is **built and boot-tested**. The TS wiring (`runAudit()` in `src/app/api/compass/route.ts`) is live on `app.arcs.care` and fires a no-op when `AUDIT_SERVICE_URL` is unset. The only missing piece is hosting.

---

## Service shape (facts)

| Dimension | Value |
|---|---|
| Framework | FastAPI 0.128.8 + uvicorn 0.39.0 |
| Python | 3.11 (local) |
| Endpoints | `GET /api/audit/health`, `POST /api/audit/{sage,lab,bar,kintsugi}`, `POST /api/audit/receipt` (batch, unused by TS client) |
| Cold start (import main.py + FastAPI app object) | **0.36s** |
| Cold start (full operator set, all 4) | **0.80s** (SAGE is the heavy one at 0.79s — numpy import) |
| Operator lazy loading | service.py already lazy-loads each operator on first use — SAGE call warms only SAGE, receipt endpoint warms all four |
| Bundle size (operators/ on disk) | ~30MB — well under 500MB Vercel Function limit |
| Dependencies | `fastapi>=0.115`, `pydantic>=2.9`, `numpy>=2.0`, `uvicorn>=0.30` (4 deps, all on PyPI) |
| Persistence today | JSONL files on disk (`benchmark_pairs.jsonl`, `audit_traces.jsonl`) — local dev only |
| Traffic model | Fire-and-forget after compass LLM inference; 4000ms timeout per operator call; non-blocking; no user-facing output |

---

## Constraint: Vercel serverless is stateless

This is the key architectural constraint.

- Vercel Functions have **no persistent writable disk**. `/tmp` exists (512MB, cleared between invocations).
- The current `persistence.py` writes JSONL to disk — that works locally but **cannot work on Vercel serverless** without change.
- If the service hosts on Vercel, persistence must move to: (a) Supabase Postgres via `DATABASE_URL`, (b) an external object store, or (c) be disabled (audit trail lost, benchmark pairs lost — service still returns operator output to TS client).

For the JSONL persistence to work, the host must have a writable filesystem that survives across invocations — i.e. a container/PaaS with persistent disk, not Vercel serverless.

---

## Option A — Vercel Python serverless (Fluid Compute)

Deploy `audit_service/` as a Vercel Function using Vercel's Python runtime. Vercel auto-detects FastAPI from `main.py` + `requirements.txt`.

### How it'd work

1. Copy `operators/audit_service/` to a deployable location with its own `requirements.txt` and a `main.py` that Vercel can find.
2. Set `AUDIT_SERVICE_URL` on the Vercel project to the deployed Function URL.
3. Change `persistence.py` to write to Supabase Postgres (or disable persistence).

### Bones

```
operators/audit_service/
├── __init__.py
├── main.py              # FastAPI app — already Vercel-compatible shape
├── schemas.py           # Pydantic models
├── service.py           # operator runners (lazy-load)
├── translator.py        # compass receipt → primitives
├── persistence.py       # needs Supabase rewrite for Vercel
├── review_pairs.py      # CLI reviewer (not deployed)
└── requirements.txt     # fastapi, pydantic, numpy, uvicorn
```

Vercel detects FastAPI from `main.py` automatically. The `AUDIT_SERVICE_PORT` and `AUDIT_ALLOWED_ORIGINS` env vars become Function environment variables.

Vercel's Python runtime supports FastAPI natively per their docs (last updated 2026-08-24). One Function, Fluid compute, scales with traffic.

### Cold start

- **First SAGE call on a cold Function:** ~1.15s (0.36s import + 0.79s SAGE import).
- **Warm Function (SAGE already loaded):** <100ms (just the operator.run() call).
- **Receipt endpoint (all 4 operators) on cold:** ~1.15s (same as SAGE — lazy load is sequential, but the import cost is paid once).
- **If you set `AUDIT_SAMPLE_RATE`** to sample traces (e.g. 0.1 = 10%), the persistence load is lighter but doesn't affect cold start.

For a fire-and-forget call gated by a 4000ms TS timeout, a 1.15s cold start is workable but not invisible. If the Function is warm (getting steady compass traffic), it's fine.

### Persistence problem

Vercel Functions can't write JSONL to disk. Options:
- **Rewrite persistence to Supabase:** Use `DATABASE_URL` (already on the Vercel project) to write audit_traces + benchmark_pairs to Postgres tables. This is the clean path — same DB the compass route uses.
- **Disable persistence:** Service still returns operator output to the compass route, but no audit trail or benchmark pairs are stored. Defers the evidence-collection work.

### Costs

Vercel Functions on Fluid compute: usage-based. For low-traffic internal audit calls, likely negligible. No separate monthly bill for a service that gets a few calls per day.

### Pros / cons

| Pros | Cons |
|---|---|
| Same Vercel project as the app — one deploy pipeline | Cold start ~1.15s on first call (acceptable but not invisible) |
| No new account, no new billing | Persistence needs Supabase rewrite or disable |
| `DATABASE_URL` already available for persistence rewrite | Vercel Function bundle is stateless — JSONL persistence can't work as-is |
| Scales with traffic, zero ops | SAGE import (numpy) is the slow part — can't avoid it |

---

## Option B — External PaaS / container host (Render, Fly.io, Railway)

Deploy the service as a long-running Python process on a host that supports containers + persistent disk.

### How it'd work

1. Write a `Dockerfile` (or use the host's Python buildpack) that installs deps and runs `uvicorn audit_service.main:app`.
2. Deploy to Render / Fly.io / Railway.
3. Point `AUDIT_SERVICE_URL` at the deployed URL.

### Bones

```
Dockerfile (or buildpack)
operators/audit_service/   # mounted or copied in
requirements.txt
```

A Dockerfile approach:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY operators/audit_service/requirements.txt .
RUN pip install -r requirements.txt
COPY operators/audit_service/ ./audit_service/
# The service imports from operators/ tree — either copy the whole tree
# or make operators/ installable. Simplest: copy operators/ in full.
COPY operators/ ./operators/
WORKDIR /app
CMD ["uvicorn", "audit_service.main:app", "--host", "0.0.0.0", "--port", "8766"]
```

### Persistence

Writable disk available — JSONL files work as-is. No rewrite needed.

### Cold start

Long-running process — no cold start. First request is fast.

### Costs

| Host | Rough cost | Notes |
|---|---|---|
| Render | ~$5-7/mo (starter) | Managed, easy deploy from GitHub |
| Fly.io | ~$1.94/mo (smallest VM) + bandwidth | Docker-based, close to users |
| Railway | ~$5/mo | Managed, trialAvailable |

All three require a separate account + billing setup.

### Pros / Cons

| Pros | Cons |
|---|---|
| No cold start — long-running process | New account + billing + deploy pipeline |
| JSONL persistence works as-is (no rewrite) | Separate infra from Vercel — two deploy surfaces |
| Container is fully under our control | Ops: need to monitor, restart on crash, handle logs |
| Can run on minimal hardware (service is lightweight) | Another thing to keep alive |

---

## Option C — Supabase Edge Functions (Deno/TS) — REJECTED

Supabase Edge Functions run Deno (TypeScript/JavaScript), not Python. The audit service is Python + numpy + operator library — no path to run it on Deno without a full rewrite.

**Reject.** The rewrite cost is high (translate all four operators to TS or re-implement their logic) and the value is low (we'd be re-doing work already done in Python).

---

## Option D — Vercel Docker container — gray area

Vercel supports Docker deployments for larger functions (up to 5GB bundle on Fluid compute, public beta per their docs). This would let us deploy the audit service with a writable `/tmp` mount and persistent disk.

### Status

This is a **public beta feature** per Vercel docs ("Large Functions" / Docker support). Uncertainty:
- Is the Docker-based persistent disk actually available on the arcs-v9 project's plan?
- Does the `/tmp` mount survive across invocations, or is it still ephemeral?

If Docker on Vercel gives us a persistent writable volume, this combines the Vercel deployment surface (Option A) with the persistence we need (Option B's disk). But it's beta and the persistent-disk semantics need verification.

### Recommendation

**Do not lead with this.** Verify the feature is generally available and the disk semantics are clear before relying on it. If it works, it's the best of both worlds. If it doesn't, fall back to A (with Supabase persistence rewrite) or B (external PaaS).

---

## Option E — Do nothing (keep service local-only, TS wiring dormant)

The TS wiring is live but does nothing without `AUDIT_SERVICE_URL`. The Python service runs locally for dev/debug. No production audit trail, no benchmark pairs.

### When this is the answer

- If the audit layer's value is unproven and you want to run the benchmark cadence locally before committing to hosting.
- If you want to defer hosting decision until the operator pipeline is proven to add value.

### Trade-off

You lose the production audit trail and the Path A → Path B evidence collection. The TS wiring is shipping a no-op, which is honest but not useful.

---

## Dimension comparison

| Dimension | A: Vercel Python serverless | B: External PaaS/container | C: Supabase Edge | D: Vercel Docker (beta) | E: Do nothing |
|---|---|---|---|---|---|
| Deployment surface | Vercel (existing) | New host | Supabase (existing) | Vercel (existing) | None |
| Cold start | ~1.15s cold, warm <100ms | None (long-running) | N/A | ~1.15s cold (if same as A) | N/A |
| Persistence (JSONL) | **Broken** — needs rewrite | Works as-is | N/A | Needs verification | N/A |
| Persistence (Supabase) | Works (rewrite persistence.py) | Works | N/A | Works (if disk available) | N/A |
| New account/billing | No | Yes (Render/Fly/Railway) | No | No | No |
| Ops burden | Low (serverless) | Medium (run & monitor) | N/A | Medium (Docker + verify disk) | None |
| Bundle size limit | 500MB ( Fluent) / 5GB (Large, beta) | Container limit (host-dependent) | N/A | 5GB (beta) | N/A |
| numpy import cost | Paid on cold start | Paid once at boot | N/A | Paid on cold start | N/A |
| Ready today | Yes (with persistence caveat) | Yes (with Dockerfile) | No (wrong runtime) | Unclear (beta feature) | Yes (dormant) |

---

## Numbers

- **Service import + app:** 0.36s
- **Full operator set cold start:** 0.80s (SAGE dominates at 0.79s — numpy)
- **First SAGE call on cold Vercel Function:** ~1.15s
- **Warm SAGE call:** <100ms
- **Bundle size:** ~30MB (operators/ on disk) — well under limits
- **Deps:** 4 PyPI packages, all standard
- **Persistence I/O today:** JSONL append on disk — ~1 write per operator call (4 writes per compass run if all fire)

---

## What's already done (so you don't re-discover it)

- FastAPI service boots clean locally: `GET /api/audit/health` returns `{ok:true, operators:[SAGE,LAB,BAR,KINTSUGI], version:1.0.0}`
- All four operator endpoints respond (tested via curl during build verification on this branch)
- TS client (`audit-client.ts`) is wired into compass route, guarded by `AUDIT_SERVICE_URL` — fires no-op when unset
- Persistence layer (`persistence.py`) writes JSONL to disk — works locally, **not Vercel-serverless-compatible as-is**
- Benchmark pair store (`benchmark_pairs.jsonl`) accumulates locally — 9 rows on disk from test runs
- Review CLI (`review_pairs.py`) reads the store for human review

---

## Open questions (need your call)

1. **Hosting target:** A (Vercel Python serverless + Supabase persistence rewrite), B (external PaaS + container + JSONL as-is), D (Vercel Docker — verify before committing), or E (defer)?
2. **Persistence:** If A or D, rewrite `persistence.py` to Supabase Postgres, or disable persistence (audit trail still returned to TS client, just not stored)?
3. **If B:** which host? (Render, Fly.io, Railway — or something else?)
4. **If E:** how long to defer? Until benchmark cadence runs locally and shows operator audit value?

---

## My read (not a decision — a starting point)

**A is the path of least resistance** if you want it live on `app.arcs.care` with minimal new infra:
- Same Vercel project, same deploy surface, no new account.
- Cold start is acceptable for fire-and-forget (1.15s cold, warm is fast).
- Persistence rewrite to Supabase is a contained change — `persistence.py` swaps JSONL append for a Postgres insert using the existing `DATABASE_URL`. The benchmark store becomes a Postgres table instead of a JSONL file.

**B is the cleanest if persistence as-is matters** and you don't mind a separate host. JSONL works, no rewrite, but you get a second infra surface to maintain.

**D is the best case if it works** — Vercel deployment + persistent disk — but it's beta and the disk semantics need verification before you can rely on it. Worth checking if you're inclined toward A but want to keep JSONL.

**E is defensible** if you'd rather prove the audit layer's value before hosting it. The TS wiring is honest (no-op without URL), and you can run the benchmark cadence locally.

---

*S condensate. Tell me which direction to take and I'll write the bones + next actions.*
