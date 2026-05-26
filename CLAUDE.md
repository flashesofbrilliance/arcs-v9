@AGENTS.md
@WORLD.md

# Project Map (read this before exploring)

## Stack
- Next.js 16 App Router · Prisma 7 + SQLite (`dev.db`) · Auth.js v5 magic link · Anthropic SDK

## Routes
| Path | File | Purpose |
|------|------|---------| 
| `/` | `src/app/page.tsx` | Home / entry |
| `/dashboard` | `src/app/dashboard/page.tsx` | **Main compass UI** — question input, prep form, result |
| `/compass` | `src/app/compass/page.tsx` | Magic-link login form |
| `/brief/[receiptId]` | `src/app/brief/[receiptId]/page.tsx` | Cartography brief (two-column) |

## API Routes
| Endpoint | File | Purpose |
|----------|------|---------| 
| `POST /api/compass` | `src/app/api/compass/route.ts` | L0–L5 Claude pipeline → Receipt |
| `POST /api/prep` | `src/app/api/prep/route.ts` | Create PrepSession |
| `GET /api/brief/[receiptId]` | `src/app/api/brief/[receiptId]/route.ts` | Generate/fetch Brief |

## Lib
- `src/lib/db.ts` — Prisma client singleton
- `src/lib/auth.ts` — Auth.js v5 config (Resend magic link)
- `src/lib/ygate.ts` — Y gate computation (GREEN/YELLOW/RED/FORK/SCRATCH/DELTA/PARADOX/DRIFT)
- `src/lib/env.ts` — env validation

## Schema (prisma/schema.prisma)
Core models: `User` · `PrepSession` · `Receipt` (DEWY + Y gate + kinematic + lineage) · `Brief` · `Outcome`
All JSON arrays stored as TEXT (SQLite). Enums as plain strings.

## Design tokens (inline style objects, no CSS framework)
```
bg: #020408 | surface: #0d1117 | border: #1e293b
text: #e2e8f0 | muted: #475569 | dimmed: #64748b
cyan: #00F0FF | green: #00FF9D | gold: #FFD700 | red: #FF4D6D
```

## Y states → render resolution
GREEN=SHARP · YELLOW/FORK=DEGRADED · SCRATCH/DELTA/DRIFT=GRAIN · PARADOX=MOIRE · RED=GRAIN

# ARCS v9 Architecture (governing law)

## ROM Primitives — constitutional, never violate
1. **NOTOMATION** — scaffold/sequence cognition only; never compress/replace/overrule revealed preference
2. **HYPERSPHERE CONTEXT MANIFOLD** — What / Who / Where-When / Why / Flow-State
3. **HYPERSTITION PIPELINE** — Ethereal → Loki Test → Receipt Evaluation → ROM
4. **GOLDEN INCHWORM** — Red Thread → Golden Thread → Needle (3-pass, non-blocking)
5. **ORTHOGONAL ECHO DETECTOR** — surface cross-domain kinematic isomorphisms

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Observatory/replay · Blockchain registry · L6–L7 engine · Python Vector Collision microservice

# Token-saving rules
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only — no CSS files, no Tailwind, no className.
- No new dependencies without asking.

# Handoff — v0.1.0 (2026-05-26)

> **For Claude Code:** this section is your pickup point. Read in order below.

## Orientation chain
1. `MEMORY.md` — versioned context log; what happened before you arrived
2. `SKILL.md` — your contract: what you can do, what you must not do, priority queue
3. `WORLD.md` — physics spec; governing law (already referenced above)
4. `AGENTS.md` — agents/workers map, DEWY pipeline, Y-gate states

## Open sprint (Issue #1 — P0 Backlog Sprint 1)
All four sub-issues are unblocked and ready to start. Dependency order:

```
#2 DEWY Receipt Schema
  └─ #3 Time ROM (embed into #2)
       └─ #4 Compass → DEWY flow
            └─ #5 Book II Canon chapter
```

## File targets to create
```
runtime/specs/dewy-receipt-schema-v1.md     ← Issue #2
runtime/specs/dewy_receipt.schema.json      ← Issue #2 (machine-readable companion)
runtime/specs/time-quality-attribution-rom.json ← Issue #3
runtime/flows/question-compass-to-dewy.md   ← Issue #4
canon/book-ii-time-firmware-modes.md        ← Issue #5
```

## Versioning policy (enforced)
- `MEMORY.md` — append-only; new entries at top; never delete prior versions
- `SKILL.md` — update in place; increment version header; keep changelog
- `CLAUDE.md` — append new `## Handoff — vX.Y.Z` sections only; never overwrite
- Spec files — use front-matter `version` field; `*-v2.md` only on breaking schema change
- Python scripts — never overwrite; create `*_v2.py` for breaking changes

## Last confirmed commit
`e66d4de` — 2026-05-26 16:15 — `arcs_cli.py` 5-verb pipeline + apex spine DEWY receipt [NCI:81]
