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

# Handoff — v3.58.0 (2026-09-08)

> **ARCS-on-ARCS design session (worktree `competent-kirch-7c6e0f`, branch `claude/epic-bardeen-94cce3`).**
> Started as an NFTT ship + drift-closure, opened into a full living-system architecture, closed by
> polishing the Target Scan schematic. All shipped work on main; forward work handed to fresh sessions.

## Shipped
- **NFTT threaded→literary drift CLOSED** (PR #312): retired the threaded `story_render.py` engine +
  schema + `.story.md` sources + 4 orphaned `-full.html` to `_ARCHIVE/nftt-threaded-engine/`; repointed
  `nftt-story-factory` skill to the literary standard (template+checklist, no engine); tool-catalog
  regenerated. Closes the v3.55.0 `story_render.py` open loop.
- **NFTT "The Factory on Itself" LIVE** at good.arcs.care/blog/nftt/the-factory-on-itself (PR #348) —
  self-referential: the factory writes its own retirement. New index Latest; `the-loop-closes` → No. 9.
  Blessed + witnessed (`_STATE/witness/2026-09-08.jsonl`).
- **Living-system spec + e2e map** (PR #349): `_SPECS/self-serve-atlas-scan-v1.md` (DRAFT/YELLOW) +
  `_ARTIFACTS/arcs-e2e-notomation-map-hud.html`. Two-order abductive profile→role self-serve scan
  (portable input = Resume + LinkedIn PDF + LinkedIn export = User1), per-tenant Supabase-RLS atlas with
  earned-fidelity progression, local-first/air-gapped-after-sync, git-anchored pulse⇄oracle heartbeat
  (OT-layer proof-of-life, kintsugi/pathogen immune response, local/global time-signature alignment).
- **Wired-loop schematic** distilled into `target-role-scan-hud.html` §05 (feedback loop as hero) +
  **all 22 em-dashes swept** to colons (PR #351). Internal artifact (noindex, unrouted).
- ADR-076 audit reconciled, no dup (oracle counter=76). Memory banked: `look-out-before-look-in`.

## Open (handed to fresh sessions, all started)
1. **Pulse Phase-0 heartbeat** (task_3fdd97bf): build `_STATE/pulse.json` + mutual-check guard per the
   spec; fixes the stale drift-sentry / disabled pollers. Load-bearing for the e2e map's freshness.
2. **Kaizen window-cost job** (task_23dfd53b): recurring; scoped to reconcile with the existing
   "Token cost ROI analysis" cloud session, not duplicate.
3. **zachharris.xyz/scan deploy** (task_7215ccad): cross-project (domain not served by this repo);
   register decision (insider-dense vs legibility layer) + domain-topology verify first.
- ADR candidates (allocate via `scripts/oracle.py next adr`): global pulse⇄oracle heartbeat; two-order
  abductive profile→role scan.
- Carried from v3.57.0: Reading Room tenants 2a-2c; ADR-076 demand probe; memory index over budget.

# Handoff — v3.57.0 (2026-09-07)

> **Open-loops arc, back-propagation ship (branch `claude/open-loops-handoff-cvgjxd`, restarted from
> main after the arc's prior PRs merged).** Closed the last named seam in the Reading Room cache: the
> Metabolic Router's back-propagation organ. Everything on main (PR #320 → `343b266`).

## Shipped
- **`scripts/cache_backprop.py`** (new, stdlib) — lazy pull-driven repair of a DIRTY `(domain, epoch)`
  cache slice. `plan` → `packet` (Curator work-packet: slice nodes + cited provenance AS-IS at HEAD +
  rubric) → `apply` (write graded statuses into the digest; stamp only that slice fresh). Grading is
  JUDGMENT, external by construction (NOTOMATION) — the script scaffolds, never grades.
- **`scripts/cache_manifest.py`** — per-slice `graded_at_sha` now preserved through `stamp`/`check`
  (new `prior_grades()` helper; `build_slices(..., prior=)`). Fixes the load-bearing hazard: re-grading
  one epoch used to falsely free every sibling epoch sharing the digest file. Only a *complete* re-grade
  advances the sha; `--partial` leaves the slice dirty (WITNESS honesty).
- **Gauntlet before commit** (runner + adversarial skeptic, refuter per finding): 3 real defects fixed —
  (1) write-before-validate left a half-graded digest on a bad apply (KINTSUGI); (2) `--partial` falsely
  stamped fresh; (3) a cleared note outlived its status. 5 stdlib tests green
  (`scripts/tests/test_cache_backprop.py`).
- **1b gate MET** (build-plan ledger + gate note updated): `product/2026-04` dirty → re-graded LIVE →
  fresh, 19 siblings stay dirty; survives a full re-stamp AND 11 commits of base advance. The 2026-04
  digest node `arch-operators-not-wired` re-graded LIVE with a confirmation note.

## Open (next session)
1. **Reading Room tenants 2a-2c** — Concordance, Chronicle, Babelfish, Codex — build on the same
   Reader + cache spine now that back-prop closes 1b.
2. **1a 4-width visual check** — headless Chromium screenshot at 375/790/tablet/desktop; then 1a's gate closes.
3. **Live admin smoke** of `/reading-room` on prod (needs a signed-in admin email).
4. Zach-gated (carried): Supabase Branching + `PREVIEW_DATABASE_URL`; PENDING 007 migration re-baseline;
   flip `INTEGRITY_GATE_BLOCK=1` after a clean week; Tribune Posterior trigger (needs the Outcome handler).
5. From v3.56.0: ADR-076 demand probe (one cheap read-only MCP tool + "Connect an agent →"); memory
   index still over the hook's budget; full `/meta-audit` epoch for the 81 lattice nodes.

> _v3.56.0 (DPRK · wrap-lint MODE-5 · post-4 s-tier · ADR-076) relocated to `_ARCHIVE/handoffs.md` on 2026-09-08; v3.55.0/3.54.0/3.53.0 relocated earlier._
