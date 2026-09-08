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
- **Self-contained artifact/page CSS: one shared px `--measure` for BODY/card reading text — NEVER `max-width:NNch` per element** (font-dependent → misaligned right edges that read as broken wrapping). **But LEDES are the exception: a hero/section lede spans the full lane width matching its heading (`max-width:none`), never the narrow body measure — a lede narrower than its heading reads as a broken/abridged block with a dead right gutter (`design-full-width-lede-matches-heading`; Zach's standing preference, do NOT "fix" it back to `--measure`).** The "too narrow" symptom is invisible to overflow/clip gates — eyeball lede-vs-heading edges at ~1280px too. Bordered callouts carry the measure on the box, not the inner text. Before shipping any single-file HTML, run the repo's own gate (`scripts/artifact_wrap_lint.py`; `npm test` for `zachharris-xyz`) and sweep 360–1440 incl. the 700–1000 band. Em-dashes 0. Canon: `_PATTERNS/arcs-artifact-css-base.css`; AGENTS.md gotcha #13.


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

# Handoff — v3.59.0 (2026-09-08)

> **ARCS-on-ARCS shipping session** (worktree `agitated-feynman-b23c40`, branch `feat/audit-service`).
> Drove loop-closing to proof, then shipped a run of live surfaces. Resume seed:
> `_STATE/pickup-prompt.md`. Deceipt ledger now **15** (`_STATE/deceipt-ledger.md`).

## Shipped + verified live
- **NFTT "Assets and Liabilities"** (good.arcs.care/blog/nftt/assets-and-liabilities) — double-entry
  ledger essay (receipts=assets, deceipts=liabilities), companion to confirmed-not-my-bug. PR #332.
- **Field Instruments public-goods chapter** (good.arcs.care/instruments) — atomized microservices
  reach-tagged at true tier (Wired / Proven / Seed), no fake install paths. PR #337 (+ routing fix #340).
- **Day-151 milestone** on `status.html`; its cited commit SHAs preserved via a `--merge` (not squash).
- **Informativeness ratchet — real CI arm.** Was wired into the DISABLED `ci.yml` (never ran, deceipt
  #15); moved to a dedicated cheap `informativeness.yml` (pull_request, path-filtered, stdlib-only) +
  the pre-commit arm. Reproducible DB audit (247/189/2) + dead-trio build fix landed in PR #306.

## Deceipts booked (12–15)
#12 outcome-grep mislabeled "DB-blocked"; #13 claims-skeptic caught a 2nd operator ref; #14 "247/247
horizon" was actually `window` (horizon all-NULL); #15 CI ratchet wired to a dead workflow. #13 and
#15 were caught by the INDEPENDENT strand / Zach's "show me", NOT by self-review.

## Key lesson
**"Wired" must mean wired to something that RUNS, verified by a run — not the presence of a step.**
Two defects (the "running in production" overclaim, the `next.config` /instruments re-catch) were both
caught by field-contact, never by my own confidence.

## Open (next session)
1. **Extract `informativeness-auditor`** from the harness into a standalone package (the Seed→Proven
   graduation the instruments page tracks).
2. **Outcome-capture keel** — the P1 gap (2/247 closed); chip spawned, still the keel.
3. Memory index near budget (6 retired this session, Zach-approved); retirement stays human-owned.
4. ROM candidate (calibration method) parked at the gate; graduates only on a live receipt.


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

> _v3.57.0 (Reading Room / integrity gate) relocated to `_ARCHIVE/handoffs.md` on 2026-09-08; v3.56.0 (DPRK · wrap-lint MODE-5 · post-4 s-tier · ADR-076) relocated to `_ARCHIVE/handoffs.md` on 2026-09-08; v3.55.0/3.54.0/3.53.0 relocated earlier._
