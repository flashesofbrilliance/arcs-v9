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
| `STATUS_GATE_PASSCODE` | Shared passphrase for the `status.arcs.care` "for the real ones" veil (`src/lib/statusgate.ts` + `src/proxy.ts`). Prod fail-closed if unset; dev passes through. Interim until the MCP veil |
| `GITHUB_TOKEN` | Server-side read of the now-private `arcs-v9` repo for live telemetry (`/api/pulse`, `/api/field`). Fine-grained PAT, read contents+metadata. Without it the pulse widget goes dark |
| `VERCEL_TOKEN` | *Optional.* Vercel-native production deploy state for the `status.arcs.care` field board (`/api/field`). If unset (or a CLI session token that the REST API rejects), the board falls back to the GitHub Deployments API via `GITHUB_TOKEN` — which is the same Vercel deploy, so the badge works without it. Optional `VERCEL_PROJECT_ID` (default `arcs-v9`) + `VERCEL_TEAM_ID` if team-scoped |

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
| | OPERATOR20 | `operators/arcs_operator20.py` | 38KB | Phase 5 synthesis | READY |
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
| **Total** | 34 files | `operators/` | **16.6K LOC** | **Atomic design components for L0–L5 decision pipeline** | **PRODUCTION** |

**Integration status:** Operators are canonical alternative implementation. Not currently wired into compass route (which uses Claude L0–L5). Future integration: custom decision domains, audit hooks, phase gates for high-consequence decisions.

---

## Orchestration — the conductor's map (token-efficient choreography)

Every unit above is one of five layers. Picking *which layer conducts and which perform* a given job
is itself a `JTBD:` / `TOOL-FIT:` / `EX-ANTE:` receipt (gotcha 9) — the same hook, one scale up. The
**conductor's rule: push each job to the cheapest capable layer; escalate only when the job's shape
demands it.** A deterministic pipeline beats a model call; a least-privilege staff subagent beats the
main loop holding everything in one context.

| Layer | Role in the ballet | Members | Spawns? | Cost | Conduct when |
|---|---|---|---|---|---|
| **Primitives** | atomic, deterministic units — no model | `src/lib/*` (ygate, statusgate, db, env), `operators/arcs_primitives*.py`, ARCS Law | no | ~0 | a pure function / invariant settles it |
| **Operators** | single-lens reasoning pass | LAB · BAR · SAGE · CURATOR · KAIROS · CONTRACT (`operators/`) | no | 1 pass | one bounded lens (ruin, timing, synthesis…) is the job |
| **Meta-operators** | compose operators; phase-gate + heal | OPERATOR20 · KINTSUGI · pipeline · Constitutional Court | no | few passes | a job needs several lenses sequenced + validated |
| **Chiefs of staff** | conduct: decompose → delegate → synthesize (don't do object-level work) | main loop · Plan agent · a `Workflow` script · `/forge` · `/meta-audit` · `counterpart-gauntlet` | **yes** | high | the job fans out or needs cross-item synthesis |
| **Staffs of chief** | least-privilege doers, one bounded task each | Explore · recoil-gather-git/web · recoil-reason · claims-skeptic · ciso/sre/privacy-review · general-purpose | no | med | a bounded task is delegable + parallelizable |

**What sorts chief from staff:** authority to *spawn + own synthesis* (chief) vs *bounded, least-privilege,
no spawning* (staff). The efficiency win is division of labor ([[cognitive-division-of-labor-pruned-lattice]]):
a chief holds the thin plan; staff hold the heavy context in throwaway windows and return only conclusions.

**Throwaway window ≠ throwaway learning.** The discarded window loses the *context*, never the *learning* —
especially the expensive **negative results** ("searched X/Y/Z, not there; approach Z dead-ends"). Staff
return conclusion **+ durable learning-residue** (map built, branches ruled out, precedent), written to a
greppable store keyed by the job's `JTBD:` shape; a chief **checks the store before spawning** so a
same-shape job warm-starts from the prior floor, not zero. Learning capitalized once, re-paid never — this
is the attractor-basin distiller made incremental. See [[throwaway-context-not-throwaway-learning]].

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
9. **Decision-provenance hooks (greppable).** On any non-obvious tool/architecture pick, leave the receipt at the code site as a greppable couplet: `JTBD:` the job (tool-agnostic, in plain terms) and `TOOL-FIT:` chosen-X over native/obvious-Y because named-constraint-Z. Add an `EX-ANTE:` line when precedent exists — *why* X fits (prior same-shape / fractal-similar decisions) — which makes it a scoreable ex-ante fit-receipt (the watchers score it ex-post: did the tool hold or drift?). It's the ARCS loop dogfooded on the build, and it recurses to the orchestration scale (which agent/operator for which job is the same hook). Every `TOOL-FIT:` should answer a `JTBD:`. Census: `grep -rn "JTBD:\|TOOL-FIT:"`; the meta-audit Drift Sentry (§7) flags orphans and non-obvious picks with neither. Compose with `ADR-NNN` when the decision is heavy.

---

## Connected systems

| System | Repo | Role |
|---|---|---|
| Perplexity MCP | `flashesofbrilliance/perplexity-mcp` | Claude Code search tool (search/reason/chat) |
| arcs.care | `flashesofbrilliance/arcs-care` | Live public site — separate Vercel project |
| GIGI substrate | `flashesofbrilliance/gigi` | Local-first fiber-bundle DB — seam at compass/route.ts (TBD P3) |
| arcs-canon | `flashesofbrilliance/arcs-canon` | Dewey YAML knowledge library |
| arcs-hq | `flashesofbrilliance/arcs-hq` | TS skills runtime — being archived (P1) |
