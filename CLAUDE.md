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

# Handoff — v3.56.0 (2026-09-07)

> **Long multi-thread session (worktree `dprk-lazarus-malware-analysis-4a7acf`).** Started from the
> DPRK/NFTT close-out, then: a measure/wrap SAFEGUARD + audit, an impeccable pass on post-4, a
> delegated Dealroom research crawl, and a new ADR. All shipped work is on main or merging.

## Shipped
- **wrap-lint MODE 5 (container/measure mismatch gate)** — `scripts/artifact_wrap_lint.py`, pre-commit
  wired (PRs #256/#258/#260). Catches the desktop "narrow prose in a wide container" bug that overflow
  checks miss; scans `<style>` only (correctness + perf), strips CSS comments, FP-reducer for
  `.hero .lede{max-width:none}` overrides, and a `wrap-lint-allow: measure-mismatch` opt-out for
  intentional two-width designs. Fixed the dossier (`.wrap` 940→700 = inner==measure), 3 narrow ledes
  (blacksmith-observatory, blog-nftt-index, recruithaus-ammo), marked 3 two-width pages
  (wing/scott-cut/observatory). AEO robots/sitemap now reachable on good.arcs.care (proxy + next.config).
- **NFTT post-4 impeccable pass = s-tier, ZERO edits** (verified clean at 1280/790/375: no pan, no
  split-emphasis, no mono overflow, measure coherent). Posts 1-3 swept clean too. The template produces
  diamond-cut text handling by construction; the 4-width JS test method is banked.
- **Dealroom talent research** (delegated agent) — `_ARTIFACTS/research/2026-09-04-dealroom-talent-report-grammar.md`
  (PR #273): 15 report/viz patterns + an MCP-led-growth GTM analysis Zach flagged.
- **ADR-076 — MCP-Led Growth: the attribution wedge** (PR #307, merging). DRAFT/YELLOW: MCP = free land
  on the authed core, API = paid expand, wedge = ARCS's native attribution (cited receipts, not the
  model guessing). Drafted as ADR-075; **renumbered to 076 after a parallel session's DECIDED ADR-075
  "Metabolic Router" merged first** (oracle-first doctrine; collision resolved cleanly, audit no-dup).
- Housekeeping: lattice epoch re-pinned e9=2026-09-03 (honest spot-check, not a full meta-audit);
  iCloud deliverable→Files sync convention set up (ARCS/dated subfolders); memory consolidated + 5 new
  memories banked (MODE-5 tripwire doctrine, MCP-led-growth, dealroom grammar, NFTT provenance/aphorisms,
  template s-tier proof).

## Open (next session)
1. **ADR-076 demand probe** (the ADR's own next step): ship ONE cheap read-only MCP tool over the public
   NFTT/receipt corpus + a "Connect an agent →" affordance; measure pull. Do NOT build a hosted MCP
   server before that signal. If quiet across a fair window, the thesis weakens (falsifier stated).
2. Memory index still ~20KB over the hook's 17.4KB budget — further trim needs de-indexing live wisdom (Zach's call).
3. Full `/meta-audit` epoch to re-derive all 81 lattice node statuses (spot-check done; full run deferred).
4. story_render.py / literary-theme drift still stands (see v3.55.0 in `_ARCHIVE/handoffs.md`).

> _v3.55.0 (NFTT "Confirmed Not My Bug" b-version) relocated to `_ARCHIVE/handoffs.md` on 2026-09-07; v3.54.0 + v3.53.0 relocated earlier._
