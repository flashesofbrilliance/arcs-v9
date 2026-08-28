<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

@WORLD.md
@CLAUDE.md

---

# ARCS v9 — Agent & DevOps Handbook

> Read WORLD.md first. It is not documentation — it is the physics of the world you're building in.

---

## What this repo is

**`github.com/flashesofbrilliance/arcs-v9`** — canonical ARCS v9 decision intelligence app.
Stack: Next.js 16 · Prisma 7 + SQLite (dev) / Supabase (prod) · Auth.js v5 · Anthropic SDK.
No Tailwind (removed 2026-07-11; it was an unused Day-1 scaffold remnant). Inline styles only in components (per WORLD.md); the sole stylesheet is `src/app/globals.css` (reset + keyframes + font tokens — things inline styles cannot express).

---

## Environment variables

| Var | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude Sonnet 4.6 — powers compass route |
| `AUTH_SECRET` | Auth.js v5 session signing |
| `AUTH_RESEND_KEY` | Magic link emails via Resend |
| `DATABASE_URL` | Postgres/Supabase (prod only; SQLite used automatically in dev) |
| `RECOIL_PASSWORD` | Shared cookie gate for the whole `/recoil*` tree (`src/proxy.ts`, private-alpha) |
| `ADMIN_EMAILS` | Comma-separated admin allowlist — interim RBAC for the internal `/recoil` index + reports (`src/lib/admin.ts`). Prod fail-closed if unset; dev passes through |

---

## Routes & handlers

| Route | File | Purpose |
|---|---|---|
| `POST /api/compass` | `src/app/api/compass/route.ts` | **Core.** L0–L5 Claude pipeline → DEWY receipt + Y-gate |
| `POST /api/prep` | `src/app/api/prep/route.ts` | Create PrepSession (stakes/horizon/protecting/confidence) |
| `GET /api/brief/[id]` | `src/app/api/brief/[receiptId]/route.ts` | Cartography brief generation |
| `GET /api/guide/[id]` | `src/app/api/guide/[receiptId]/route.ts` | Step-by-step guide surface |
| `GET /api/history` | `src/app/api/history/route.ts` | Receipt history for user |
| Auth | `src/app/api/auth/[...nextauth]/route.ts` | Auth.js v5 magic link |

---

## Core lib

| File | Purpose |
|---|---|
| `src/lib/ygate.ts` | Y-gate 12D manifold → polarity × conviction × stability → state |
| `src/lib/db.ts` | Prisma client singleton |
| `src/lib/auth.ts` | Auth.js v5 config (magic link, Resend) |
| `src/lib/env.ts` | Env validation — throws on missing required vars |

---

## DEWY pipeline (compass)

```
question + prep context
  → Claude Sonnet 4.6 (L0–L5 system prompt)
  → JSON: { true_north, why, tributaries[3], nci_score, reasoning, ... }
  → computeYGate(parsed, prep, parent, sessionVersion)
  → prisma.receipt.create({ ...DEWY fields, ...yGate })
  → return receipt_id + full parsed output
```

**Tributaries** — EXACTLY 3, already implemented:
- `[0]` meta: deeper question beneath the stated one
- `[1]` challenge: uncomfortable truth / overlooked constraint
- `[2]` adjacent: cross-domain reframe

**Y-gate states → render resolution:**
`GREEN=SHARP · YELLOW/FORK=DEGRADED · SCRATCH/DELTA/DRIFT=GRAIN · PARADOX=MOIRE · RED=GRAIN`

---

## Prisma / DB

```bash
npx prisma migrate dev --name <description>   # create + apply migration
npx prisma studio                              # inspect data
npx prisma db push                             # push schema, no migration file (dev only)
```

JSON arrays stored as `TEXT` (SQLite compat). Do NOT use `Json` Prisma type until datasource is Postgres.

---

## Dev commands

```bash
npm run dev       # start (port 3000)
npx next build    # typecheck + build (preferred over tsc --noEmit — avoids TS5090 false positive)
```

---

## Agents & workers map

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

### Backlog (not built)
| Agent / Worker | Type | Priority | Notes |
|---|---|---|---|
| Outcome handler | `PATCH /api/receipts/[id]` | P1 | Closes receipt loop, fires `receipt_outcome_matched` |
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

> **File census (authoritative, reconciled 2026-08-28).** The table above is a *curated catalog*
> of the core L0–L5 components, not a file count — which is why three different numbers were in
> circulation (this line said "34 files", the atlas said "38 py files", `ls` showed "44 entries").
> Counted once against the tracked tree on this branch: **43 top-level `.py` modules · 51 `.py`
> files total** (recursive, excludes `__pycache__`) **· 60 tracked files total · 21,891 LOC**.
> Tracked subdirs: `core/` (7), `docs/` (4), `linkedin_pipeline/` (3). `audit_service/` is a
> separate WIP thread and is **not** part of this library census. Recount with:
> `git ls-files 'operators/**/*.py' | grep -v __pycache__ | wc -l`.

**Integration status:** Operators are canonical alternative implementation. Not currently wired into compass route (which uses Claude L0–L5). Future integration: custom decision domains, audit hooks, phase gates for high-consequence decisions.

---

## Gotchas

1. **No new dependencies without asking.**
2. **Inline styles only in components** — no Tailwind, no CSS modules, no utility classes. Exactly two sanctioned exceptions: next/font variable classes on `<html>` in `layout.tsx` (framework mechanism), and the single `src/app/globals.css` (document reset, `@keyframes`, font tokens, reduced-motion). No other CSS files, no other `className`.
3. **JSON arrays are TEXT strings** — always `JSON.stringify()` before write, `JSON.parse()` after read.
4. **Build with `npm run build`, not bare `npx next build`** — for typecheck (not `tsc --noEmit`; TS5090 false positives on baseUrl) AND because the cloud shell exports `NODE_ENV=development`. A bare `next build` inherits that and crashes prerendering `/_global-error` with `Cannot read properties of null (reading 'useContext')` (React loads dev internals during static export). `npm run build` pins `NODE_ENV=production` so it's reproducible; Vercel already builds in production, which is why deploys were never affected.
5. **SQLite in dev, Postgres in prod** — don't use Prisma `Json` type until datasource is Postgres.
6. **`git worktree list`** before any git operation — active worktree changes between sessions.
7. **Commit style:** `type(scope): imperative [NCI:XX]` + `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
8. **Deeper environment gotchas** (Supabase MCP blind spot, Prisma-7 adapter, Vercel CLI/env quirks, domain→project verify-live, subdomain hosting, concurrency discipline, HEIC/`sips`): see `_PATTERNS/durable-gotchas.md` — on-demand, open when the task touches that area.
9. **Sugar sandbox via Zapier MCP** (PRL work): raw GET/mutating actions on `SugarCRMCLIAPI` reach `prlresinstest.sugarondemand.com/rest/v11/` directly (connection 65663180 = sandbox; NEVER prod). `/rest/v11/bulk` takes 12+ sub-requests per call — build payloads with `scripts/sugar_bulk.py` (prod host refused by default). Zapier's editor is drivable via claude-in-chrome when Comet is logged in, but the permission classifier blocks *typing* into forms: Claude does structure/clicks/publish, the human types free-text fields.
10. **Session shell helpers**: `scripts/ship_docs.sh` (push→PR→merge, enforced docs-only gate, hang-kill+retry) · `scripts/sync_worktree.sh` (WIP-commit + merge origin/main, hook-state kept as ours, never stash) · `python3 scripts/oracle.py sync <ns>` (reconcile a lagging counter — counters drift when sessions mint off-oracle; audit first).
11. **Teleport to terminal when the work is mechanically scorable.** If a pass/fail can be written as a grep, a set-diff, a schema check, a diff, or an operator-client lambda over an `ls`-enum, do it in the shell — don't fan out agents. Reserve agents/LLM for judgment (reading for meaning, emergent tagging, VARIANT-vs-SUPERSEDED, synthesis). Scout deterministically to build the work-list and kill false positives first, then spend agents only on the residue. See memory `when-to-teleport-to-terminal-vs-agents`.
12. **Oracle-first numbering — NEVER infer an ADR/seed/receipt number.** Parallel sessions across harnesses (Claude Code, Hermes) that guess "highest + 1" collide (ADR-033/067 both doubled this way). Allocate via `python3 scripts/oracle.py next <ns>` and commit `_SEEDS/_oracle.json` — git's non-fast-forward rejection is the atomic lock. A pre-commit hook enforces this: install once with `git config core.hooksPath scripts/git-hooks` (blocks any commit that duplicates an existing ADR number; warns on off-oracle numbers). Run `python3 scripts/oracle.py audit adr` to see collisions/gaps/next-free.

---

## Connected systems

| System | Repo | Role |
|---|---|---|
| Perplexity MCP | `flashesofbrilliance/perplexity-mcp` | Claude Code search tool (search/reason/chat) |
| arcs.care | `flashesofbrilliance/arcs-care` | Live public site — separate Vercel project |
| GIGI substrate | `flashesofbrilliance/gigi` | Local-first fiber-bundle DB — seam at compass/route.ts (TBD P3) |
| arcs-canon | `flashesofbrilliance/arcs-canon` | Dewey YAML knowledge library |
| arcs-hq | `flashesofbrilliance/arcs-hq` | TS skills runtime — being archived (P1) |
