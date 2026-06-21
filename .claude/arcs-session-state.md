# ARCS Session State

**Last updated:** 2026-06-21 (v2.9.0)
**Environment:** Claude Code local, worktree `frosty-kepler-b69f51`
**Branch:** `main` (merged from `sage-services-preview`)
**Last commit (arcs-v9):** 1ec1292 — security(scripts): read-only Postgres role for sage_efficacy.js
**Last commit (arcs-care):** 136add1 — unchanged this session

## Status

- arcs-v9 Vercel: ✅ LIVE — https://app.arcs.care — Framework Preset is **Services** (was Next.js;
  switched this session), SAGE Python sidecar confirmed building and serving traffic in Production
- arcs-v9 Auth: ✅ magic link (unchanged) — `AUTH_SECRET` still missing on Preview (separate, minor gap)
- arcs-v9 DB: ✅ xbbpiryokswwvcrcutge / postgres — single DB shared across local/Preview/Production
- Compass: ✅ model routing + prompt caching + SAGE pre-screen + NCI self-grade, all live in prod
- SAGE efficacy study: ✅ infra live (SageTrace table + sage_efficacy.js), correctly gated at n=0
  with-SAGE Outcomes — will start producing real numbers once Outcomes accumulate post-launch
- Observatory: ✅ unchanged, live

## What landed this session (2026-06-19 → 2026-06-21)

Long session, several distinct phases. Summarized newest-first since that's most actionable.

### Phase 5 — Read-only DB role for analysis scripts (1ec1292)
- New Postgres role `arcs_readonly`: SELECT-only via table grants, verified write-blocked
- **Gotcha hit:** table-level GRANT SELECT alone wasn't enough — this project's RLS deny-all
  policies (ADR-008) silently filtered all rows for the new role (count(*) returned 0 against a
  table with 1 real row, no error). Needed `ALTER ROLE arcs_readonly BYPASSRLS` explicitly.
  Re-verified writes still blocked after granting it. Saved as a standalone memory.
- `sage_efficacy.js` now prefers `DATABASE_URL_READONLY` (`.env.local`, gitignored), warns + falls
  back to write-capable `DATABASE_URL` if unset.

### Phase 4 — NCI self-grade rubric live in Production (1bf7251, 7fc29b4)
- Canon (`_CANON/arcs-v9-additional/ARCS-v9-Chapter-Book-Canon.md` §1.2) specifies every non-trivial
  output should self-grade Factual/Sources/Honesty/Action — was documented spec only, never wired
  into the live SYSTEM prompt. Now implemented: SYSTEM prompt + OUTPUT SHAPE + new `nciSelfGrade`
  Receipt column. **Visible** (unlike SageTrace) — flows straight through the API response.
- Verified genuinely substantive, not performative: live test produced `honesty: false` (Claude
  caught itself anchoring on SAGE's signal as ground truth) and separately `factual: false` +
  `action: false` (caught a vague "confirm with deployment lead" with no lead named).
- **Caught before damage:** main's `operators/pyproject.toml` was missing the `scipy` fix that only
  existed on the preview branch — would have crashed SAGE in prod with `ModuleNotFoundError`. Found
  by checking build logs of the just-deployed Production build, fixed same session (7fc29b4).

### Phase 3 — SAGE efficacy infrastructure + research scripts (merged from sage-services-preview)
- `SageTrace` table (separate from Receipt, never `include`d by any client route — invisible by
  construction, not convention) logs every SAGE call: fired/signal/failureReason/latencyMs
- `scripts/sage_efficacy.js` — compares Outcome.matched/regretScore with-SAGE vs without-SAGE,
  gated at n=20/group (currently n=0/n=1 — correctly reports GATED)
- `scripts/tf_sage_distillation.py` + `scripts/torch_sage_distillation.py` — pure research,
  distill the deterministic SAGE kinematic classifier into TF/PyTorch models trained on synthetic
  data (NOT real Outcomes). 81.9%/80.8% classification accuracy, framework-comparable. Found a real
  property of the deterministic classifier along the way: a pure linear ramp rarely hits
  `strong_signal` because near-zero acceleration noise has a random sign relative to velocity,
  tripping `phase_cancellation` — needs consistent curvature, not just a consistent slope.
- `scripts/vercel-debug.sh` — codifies 4 CLI gotchas hit this session (curl path syntax, flaky
  logs, sensitive-var masking, git-branch scoping never applying to CLI deploys)

### Phase 2 — SAGE wiring + decision_mode bug fix (commits from 2026-06-19, detailed in prior log)
- Model routing (Haiku/Sonnet by mode) + prompt caching + advisor-tool revert (172s, rejected) —
  see git log 964b0fa/3c51173/a266cf1 for full detail, omitted here for length
- SAGE wired as advisory pre-screen via Vercel Services (`POST /api/sage-score`, no persistence —
  Prisma stays single source of truth; the pre-existing `/question-compass` endpoint was NOT reused
  because it writes to a separate Supabase table)
- Found + fixed: `decision_mode`/`door_class` in the API response were silently overwritten by
  Claude's own echoed values (`...parsed` spread order bug) — pre-existing, unrelated to SAGE,
  found while validating SAGE. Fixed in 2a27d5b, verified live.

### Phase 1 — DATABASE_URL auth fix (blocker, resolved)
- Root cause: `!` in Supabase password mishandled by `pg`'s connection-string URL parser
- Fix: `src/lib/db.ts` parses `DATABASE_URL` manually via `new URL()` + `decodeURIComponent()`

## Open items (accurate as of this update)

```
1. ADR-016 auth.ts wiring                                  OPEN — compass works anonymous-only
                                                             without it (ADR-016 Option C), not
                                                             fully blocking, but magic-link auth
                                                             on Preview is currently broken
                                                             (AUTH_SECRET unset there)
2. Validate SAGE NCI against real with-SAGE Outcomes        OPEN — infra is ready (SageTrace +
                                                             sage_efficacy.js), genuinely no
                                                             data yet. Re-run the script
                                                             periodically; nothing to build,
                                                             just needs real usage + time.
3. AUTH_SECRET missing on Preview env                       OPEN — small, separate from SAGE work
4. Compass Kit Phase 2 — TSX port + real API wire           READY (carried over, untouched)
5. Panel/Chip design system components (ADR-009)            READY (carried over, untouched)
6. ADR-006 branching strategy (first-external-user gate)    READY (carried over, untouched)
7. arcs-care: flip NEXT_PUBLIC_CASE_STUDY_APPROVED          WAITING on Dan Pascone (carried over)
```

## Key infra facts (for next session)

- DB: `xbbpiryokswwvcrcutge` / database `postgres` / port 6543 pooler — manual URL parsing in
  db.ts (password contains `!`)
- Vercel project: `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9` / team `zachharris-3439s-projects`
- **Framework Preset is Services** (project-wide, not per-environment) — do not revert this
- `vercel deploy` (CLI) does NOT attach git-branch metadata — any env var scoped to a specific
  git-branch silently never applies to a CLI-triggered deploy. Scope to "all preview branches"
  (pass `""` as the git-branch positional in `vercel env add`) unless deploys are git-push-only.
- `operators/pyproject.toml` needs `scipy` (already fixed on main) — if this regresses again,
  it's because someone branched off an older commit before 7fc29b4
- `arcs_readonly` Postgres role exists for read-only analysis scripts — needs `BYPASSRLS` granted
  (already done) or it will silently see 0 rows under this project's RLS deny-all policies
- `next.config.ts` must keep `turbopack: { root: __dirname }` — regressed once this session, restored

## Next session

`/handoff-pickup` → ADR-016 auth.ts wiring, or AUTH_SECRET on Preview, or pick up one of the
carried-over READY items (Compass Kit Phase 2 / Panel-Chip / ADR-006). SAGE efficacy validation
needs no action — just time and real usage.
