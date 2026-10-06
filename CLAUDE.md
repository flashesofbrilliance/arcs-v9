@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  `_STATE/handoff-progress.jsonl` every turn-with-change, and asks for a `## Delta` in
  `_STATE/handoff-progress.md` at each compaction. Both are gitignored. `/handoff` folds them
  into the CLAUDE.md block and marks the ledger claimed; the global SessionStart hook flags any
  worktree whose trail was never claimed. Compaction never writes CLAUDE.md anymore.
- **Open work lives in `_QUEUE/induced-backlog.jsonl`** — items carry route/gates/trigger; execute
  from there without replanning. Dense multi-domain sessions: run `/fold` to spawn composed sessions.
- **On-demand only** (do NOT read to orient — open only when the task actually needs them):
  `MEMORY.md`, `SKILL.md`, `_ARCHIVE/handoffs.md`, `_ARCHIVE/memory-archive.md`, `_STATE/*`.
- There is no "read MEMORY→SKILL→WORLD→AGENTS in order" chain anymore. That mandate cost ~40k
  tokens per session and was retired 2026-07-19; open a specific file only when a task points to it.

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
text: #e2e8f0 | muted: #7a8699 | dimmed: #8391a7  (AA on bg; raised 2026-10-04)
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
6. **KINTSUGI IMMUNE SYSTEM** — repair seams visibly; no silent patching of integrity failures; show the break and the gold
7. **WRITE-LOCK** — one-way-door decisions require explicit write-lock declaration before commit; irreversibility is declared, not assumed

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). The full interactive Next.js page IS committed on main at `src/app/observatory/page.tsx`
(landed 2026-06-23, ~1.2k LOC); the old "never pushed" note was stale (Atlas audit 2026-09-03).
Confirm the `/observatory` route vs the static-demo rewrite before relying on either.

# Token-saving rules
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only in components — no Tailwind, no utility classes. Sanctioned exceptions (only these): next/font classes on `<html>`, and the single `src/app/globals.css` (reset + keyframes + font tokens). Tailwind was removed 2026-07-11.
- No new dependencies without asking.
- **Self-contained artifact/page CSS: one shared px `--measure` for BODY/card reading text — NEVER `max-width:NNch` per element** (font-dependent → misaligned right edges that read as broken wrapping). **But LEDES are the exception: a hero/section lede spans the full lane width matching its heading (`max-width:none`), never the narrow body measure — a lede narrower than its heading reads as a broken/abridged block with a dead right gutter (EXCEPTION, 2026-09-29: text INDEX pages such as good.arcs.care/series/* put lede, rows and footer rule on the 680px measure) (`design-full-width-lede-matches-heading`; Zach's standing preference, do NOT "fix" it back to `--measure`).** The "too narrow" symptom is invisible to overflow/clip gates — eyeball lede-vs-heading edges at ~1280px too. Bordered callouts carry the measure on the box, not the inner text. Before shipping any single-file HTML, run the repo's own gate (`scripts/artifact_wrap_lint.py`; `npm test` for `zachharris-xyz`) and sweep 360–1440 incl. the 700–1000 band. Em-dashes 0. Canon: `_PATTERNS/arcs-artifact-css-base.css`; AGENTS.md gotcha #13.


# Versioning & handoff policy (amended 2026-07-19)

> Supersedes the prior "CLAUDE.md — append new sections only; never overwrite" rule, which had grown
> this file to 28 handoff sections / ~19.8k tokens loaded on **every** session. Rationale + measurements:
> `_PATTERNS/2026-07-19-token-efficiency-audit.md`.

- **CLAUDE.md is a working file, kept lean — not an archive.** It holds durable facts (Project Map,
  ROM primitives, token-saving rules) plus **only the latest 1–2 handoff sections**. When a new handoff
  lands, move the oldest live one into `_ARCHIVE/handoffs.md`.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.87.0 (2026-10-05)

> **Briefs are owner-only; sharing goes through revocable hashed tokens (#808, `8ccd7b49`).**
> Migration applied to prod on Zach's go. Receipt `2026-10-05--brief-share-tokens-pr808--ZH`.

## Shipped + on main
- `/api/brief/[id]` + `/brief/[id]` 404 for anyone but the owner (anonymous userId-null rows included);
  children scoped to owner; gen rate limit kept. **Existing raw-id brief links stopped working.**
- `BriefShare` (32-byte token, SHA-256 stored, `revokedAt`, RLS deny-all). `POST/DELETE /api/brief/[id]/share`
  (owner, stored brief only, 10 active max, per-user limit). `/shared/brief#<token>` POSTs the fragment
  token to `/api/shared/brief` (select allowlist; never userId/sessionId/prep/rawResponse/children/protecting).
- Vercel Analytics + SpeedInsights strip `#...` (`src/components/VercelTelemetry.tsx`). `/brief/[id]` OG image removed.
- Anonymous decision: no sessionId cookie; anonymous runs are not persisted, they share via ADR-037 fragment links.
- Prod migration: SQL run via Supabase `execute_sql` in one transaction + `_prisma_migrations` rows with file
  SHA-256 checksums for `20260928000000_tribune_rls` and `20261005000000_brief_share` (prod `DATABASE_URL` is
  a sensitive Vercel env, so the prisma CLI cannot reach it). Prod probe: token-shaped lookup 404s, not 500.

## Open (next session)
1. Signed-in flow never exercised: open an owned brief, copy link, open in private window, revoke.
2. `migration_lock.toml` says `sqlite` vs postgresql datasource: a real `prisma migrate deploy` may refuse.
3. Chips running in other sessions: outcome API owner gate (task_13f704a2), compass parent scoping (task_0d7c27ea).

## Lessons
- A path-borne secret leaks to pathname analytics; put share tokens in the fragment and POST them.

# Handoff — v3.86.0 (2026-10-05)

> **cruft_sweep prune: wrong-HEAD bundles fixed (#807), then full-history bundles made incremental (#809).**
> Both merged on Zach's go with `fe-smoke` still pending (python-only). Receipts
> `2026-10-05--cruft-prune-head-safety-pr807--ZH`, `2026-10-05--cruft-incremental-bundles-pr809--ZH`.

## Shipped + on main
- **#807 (`15a5761c`):** detached worktrees returned the literal `HEAD` from `--abbrev-ref`, and
  `bundle create <f> HEAD` in the main repo bundled the MAIN checkout (`44ed0c88` x5). `.git`-less worktrees
  fell through to the enclosing checkout. `resolve_worktree()` now requires a `.git` file, toplevel == dir,
  GIT_DIR under `<common>/worktrees/`, and a `git worktree list` entry; bundled tip must equal HEAD; any
  refusal exits 2; inherited `GIT_DIR`/`GIT_WORK_TREE` scrubbed. Rule 9.
- **#809 (`f69ffb66`, asked for by the orchestration session):** bundles are `<ref> ^origin/<base>`; a tip
  already on upstream gets only a MANIFEST.tsv row (`on-origin/<base>`); detached heads pinned permanently as
  `refs/cruft-archive/<name>-<sha8>`. Rule 10.
- `--self-test` (13 checks: branch / detached / no-.git / landed worktrees over 2MB base history, <256KB
  bundle ceiling) fails on both prior versions; wired into pre-commit when the script is staged.

## Open (next session)
1. No real `prune` has run on the fixed code; first live run: `--dry-run` first, check MANIFEST.tsv rows.
2. `survey` still drops detached worktrees from its table (`worktrees()` only appends on a `branch` line) (low).
3. `fe-smoke` was pending at both merges; confirm it went green on main.

## Lessons (in the record)
- `git -C <dir>` inside the main checkout silently resolves to the main repo when `<dir>` is no longer a
  worktree: prove the GIT_DIR, never trust the path.
- A self-test with a tiny base repo cannot see a size bug: give the fixture real (incompressible) history.
