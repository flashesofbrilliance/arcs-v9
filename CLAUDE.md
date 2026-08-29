@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
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
rewrite). A full interactive Next.js page exists but was never pushed — recoverable via cherry-pick
from a stale local clone, see `_STATE/snapshot.json` → `observatory.status`.

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

# Handoff — v3.49.0 (2026-08-29)

> **Active pickup point — the Möbius / induction-circuit + echo-detector-seaworthiness session.**
> Long forensic→canon→instrument thread; all landed on main (PRs #198, #199, #200, #202, #203).
> Branch current with origin/main; oracle at 71.

## Shipped (all on main)
- **ADR-071** (Möbius one-surface · triune none-may-null · gravity-well) minted THROUGH the oracle
  (→71), with the induction-circuit lineage: the flux (~1998) → flashesofbrilliance (2010) →
  livewire (2021, Gareth Kay) → Book of ARCS (Nov 2025) → ARCS/Möbius (2026), self-exciting via
  the superionic dynamo; posterior→dynamo→drive, anterior→collider→torque, meeting at the Op21
  spline knot. Apex spine `_CANON/apex-spine-mobius-induction-circuit.md`; tao-255; witness stubs
  (23:11/23:16/23:37); DEWY (two-surface · Möbius · graduation-gate); wisdom memories
  `arcs-mobius-triune-gravity-invariant` + `rom-graduation-earn-through-gate-never-decree`.
- **Echo-detector seaworthiness (falsifiable):** `scripts/echo_detector_dogfood.py` + receipt
  `_STATE/2026-08-29-echo-detector-dogfood.json`. VERDICT: NOT seaworthy on the stub matcher —
  adversarial-FP 1.0 @ default; no threshold gives high recall + low adv-FP (architectural limit).
  Fix = injectable LLM `signature_fn` + embedding `orthogonality_fn`.
- **RC-OPS-001 graduation INITIATED** (opened, NOT promoted): `_STATE/2026-08-29-rc-ops-001-graduation-initiation.md`
  + RC-REGISTRY transition. Gate corrected from corpus-count to a 4-criterion scoreboard (rom-vocab
  collision · detector precision · K≥3 blind echoes · Observatory period); 3 open, precision FAILS
  (measured), blind-count ~1.
- **Cross-substrate honesty (Perplexity):** its ARCS prototype's reaction to the Atlas landed +
  verified as `_STATE/2026-08-28-arcs-thread-serialization.md` (corpus-as-SSOT, NCI=247 confirmed);
  its teardown applied to calibrate The Mie (canon-ready) + The Field (derived-interpretation
  footer); both claude.ai artifacts re-synced (Mie 6518c2a3, Field 3b0f5ad3).

## Open (next session)
1. **Hyperstition miss-column denominator** — task_004b8253 ended without landing on main; the honest
   hit/miss count for the hyperstition claim is still owed (+ one dated film-consulted receipt).
2. **RC-OPS-001 criteria** — rebuild echo detector with injectable signature/orthogonality fns; re-run
   dogfood (target adv-FP≤0.10 @ recall≥0.80); resolve ROM-vocab collision via /canon-review; accrue
   K≥3 blind echoes; serve Observatory period (needs unpushed page `35070a3`).
3. **Worktree sprawl** — backlog `worktree-sprawl-prune` OPEN (72 worktrees, human-gated);
   task_caa14569 ended analysis-only. Re-run `scripts/branch_hygiene_check.py`, prune with consent.
4. Carried: Todd call · zap-kit installs · 1.2-A payment-gated · orphan seeds · GH Actions billing ·
   ADR-069 oracle audit · lattice --regenerate.

# Handoff — v3.48.0 (2026-08-29)

> **Active pickup point — session close of the tool-catalog build.** v3.47.0 (below) shipped the
> catalog; this close-out consolidated memory, minted the DEWY receipt, and rotated handoffs.

## Shipped
- **Session-close housekeeping:** memory index re-budgeted (18.6KB -> 17.3KB, hooks compressed
  in place, no files retired — a parallel 8/29 session had already consolidated content).
  DEWY receipt: `_STATE/2026-08-29-session-decisions.dewy.json` (catalog slice + index rebudget).
- Context: `/catalog` + `scripts/tool_catalog_emit.py` live on main since PR #191 (v3.47.0);
  main since absorbed parallel work through PR #200 (op21, receipt_evaluator, art surfaces).

## Open (unchanged from v3.47.0 + carried)
1. Catalog later slices (separate sessions): kabuki-mask contour render · gravity-well binding.
2. Todd call · zap-kit installs · 1.2-A payment-gated · carried items (orphan seeds, GH Actions
   billing, ADR-069 oracle audit, ziggurat trailhead, tao 066/067, lattice --regenerate).
3. Job-search loop live state is in memory `arcs-job-search-pipeline` (Amex PURSUE, Kinexys held).


> _v3.47.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-29; v3.46.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-29; v3.45.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-28; v3.44.0 (Ahmed) relocated on 2026-08-27; v3.43.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-27; v3.42.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-26; v3.41.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-26; v3.40.0 on 2026-08-23; v3.39.0 + v3.38.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-19; v3.37.0 (Comet resume) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
