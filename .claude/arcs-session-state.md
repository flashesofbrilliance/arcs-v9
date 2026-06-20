# ARCS Session State

**Last updated:** 2026-06-19 (v2.8.0)
**Environment:** Claude Code local, worktree `frosty-kepler-b69f51`
**Branch:** `main`
**Last commit (arcs-v9):** 99dc0b2 — feat(compass): wire SAGE pipeline as advisory pre-screen via Vercel Services [NCI:76]
**Last commit (arcs-care):** 136add1 — unchanged this session

## Status

- arcs-v9 Vercel: ✅ LIVE — https://app.arcs.care
- arcs-v9 Auth: ✅ magic link (unchanged)
- arcs-v9 DB: ✅ xbbpiryokswwvcrcutge / postgres — DATABASE_URL auth bug fixed this session (see below)
- Compass latency: ✅ baseline established — see benchmarks below
- Observatory: ✅ unchanged, live

## What landed this session (2026-06-19 — Compass Latency + SAGE Scoping)

### DATABASE_URL auth fix (blocker, resolved)
- Root cause: `!` in Supabase password (`1163Merwins2026!`) was mishandled by `pg`'s connection-string
  URL parser (both raw and `%21`-encoded forms failed P1000 auth)
- Fix: `src/lib/db.ts` now parses `DATABASE_URL` manually via `new URL()` + `decodeURIComponent()` on
  each component, passed to `pg.Pool` as discrete fields (not a connection-string)
- Also added DATABASE_URL to Vercel **Development** scope (was Production-only)

### Compass latency optimization — commits 964b0fa → 3c51173 → a266cf1
- **964b0fa** — Model routing: `MODEL_MAP` keys QUICKMOVE/PLAN → Haiku 4.5, COURT → Sonnet 4.6.
  `unstable_cache` wraps QUICKMOVE/PLAN inference (temp ≤0.3, deterministic); COURT bypasses cache
  (temp=0.5, adversarial variation intentional). **2.6x speedup** on non-COURT modes.
- **3c51173** — Tried replacing MODEL_MAP with the Anthropic advisor tool (beta `advisor-tool-2026-03-01`):
  Haiku executor self-routing to Opus 4.8 advisor. **Reverted** — see below.
- **a266cf1** — Reverted advisor tool, restored MODEL_MAP. **Kept** prompt caching
  (`prompt-caching-2024-07-31` beta, `cache_control: ephemeral` on the 120-line SYSTEM prompt) layered
  on top of MODEL_MAP + unstable_cache.

### Benchmark results (measured this session, local dev)
| Path | Time | Notes |
|---|---|---|
| PLAN cold (Haiku, prompt-cache cold write) | ~19.3s | one-time ~4s cache-write overhead |
| PLAN repeat (unstable_cache hit) | **120ms** | 1-hour TTL dedup on identical question+context |
| COURT cold (Sonnet, uncached by design) | ~39s | unchanged |
| Advisor tool (Haiku→Opus, any mode) | **172s** | ❌ rejected — Opus consult is synchronous, not viable for a 60s route budget |

### SAGE operator integration — LANDED — commit 99dc0b2
- Discovered `operators/arcs_api.py` already has a full FastAPI backend with a `/question-compass`
  endpoint that runs the entire SAGE→LAB→BAR→Court→Kintsugi pipeline (`run_pipeline()`). This
  superseded the original A/B/C text-adapter framing — went with "wire in the existing pipeline"
  instead of building a new text-signal adapter from scratch.
- **Key design call:** did NOT reuse `/question-compass` directly — it calls `_store_receipt()`,
  which writes to a separate Supabase `arcs_receipts` table. That would create a second, divergent
  receipt store alongside Prisma. Instead added a new lean endpoint, `POST /api/sage-score`
  (`operators/arcs_api.py`), which calls `run_pipeline()` directly and returns the raw result —
  **no persistence**. Prisma `Receipt` stays the single source of truth; SAGE is advisory-only
  context fed into Claude (NOTOMATION: enriches, never decides or writes doctrine).
- **Deployment:** added via Vercel Services (`vercel.json` → `experimentalServices`), Python sidecar
  at `routePrefix: "/svc/sage"`, `operators/pyproject.toml` added (fastapi/pydantic/numpy/uvicorn).
  **Manual step required before next prod deploy:** Vercel dashboard → Project Settings → Build &
  Deployment → Framework Preset → select **Services**.
- **Local dev:** kept `npm run dev` (did not switch to `vercel dev -L`); Python service run manually:
  `cd operators && ARCS_TRACE_DIR=/tmp/arcs_trace_logs python3 -m uvicorn arcs_api:app --port 8765`.
  `SAGE_URL=http://localhost:8765` added to `.env.local`.
- **Wiring in `compass/route.ts`:** fetches SAGE with a 3s timeout before building `userMsg`; on
  failure (timeout, non-200, unreachable) logs `[SAGE] unreachable...` and proceeds Claude-only —
  verified this fallback works by killing the service mid-session (200 OK, NCI computed without it).
- **Verified end-to-end:** SAGE 200 OK → Claude reads `OPERATOR SIGNAL` block in prompt → COURT mode
  returned NCI 76, FORK y_state, true_north referencing the 8-week timeline framing from context.
- **Open Loki risk (stated in commit body):** the synthetic signal is still stakes/horizon-derived
  (closer to "Option B" than the originally-scoped text-derived "Option C"), not a true linguistic
  feature extraction. NCI/court output should be treated as a soft signal, not validated ground
  truth, until tested against a real compass corpus.

## Open sprint

```
1. ADR-016 auth.ts wiring                                            OPEN (compass non-functional in prod without it)
2. Vercel dashboard: Framework Preset → Services                     MANUAL — required before SAGE deploys to prod
3. Validate SAGE NCI output against real compass corpus               OPEN (Loki risk above)
4. Compass Kit Phase 2 — TSX port + real API wire                    READY (carried over)
5. Panel/Chip design system components (ADR-009)                     READY (carried over)
6. ADR-006 branching strategy (first-external-user gate)              READY (carried over)
7. arcs-care: flip NEXT_PUBLIC_CASE_STUDY_APPROVED                    WAITING on Dan Pascone (carried over)
```

## Key infra facts (for next session)

- DB: `xbbpiryokswwvcrcutge` / database `postgres` / port 6543 pooler — **use manual URL parsing in
  db.ts, not a raw connection string**, password contains `!`
- Vercel project: `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9` / team `zachharris-3439s-projects`
- `next.config.ts` must keep `turbopack: { root: __dirname }` — do not let this regress to
  `experimental.turbopack`, it was accidentally overwritten once this session and restored
- SAGE service: `operators/arcs_api.py` exposes `/api/sage-score` (advisory, no persistence) and the
  pre-existing `/question-compass` (persists to a separate Supabase table — do not wire this one
  into the Next.js route without resolving the dual-receipt-store question first)
- `SAGE_URL` must be set in three places to avoid silent misses: `.env.local` (local dev), Vercel
  Preview env, Vercel Production env — `route.ts` fails open (logs + continues) if unset/unreachable

## Next session

`/handoff-pickup` → set Vercel Framework Preset to Services + add SAGE_URL to Preview/Prod →
validate SAGE NCI against real receipts → ADR-016 auth.ts wiring
