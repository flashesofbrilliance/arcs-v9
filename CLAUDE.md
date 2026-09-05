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

# Handoff — v3.51.0 (2026-09-05)

> **ARCS-on-ARCS close — drove the loop-closing to proof, then folded.** Durable state lives in
> `_STATE/pickup-prompt.md` (the resume seed — freshened, fold-recorded, and independently
> resume-tested). This block POINTS to it; it does not re-derive it. On `feat/audit-service`,
> 19 commits ahead of origin (unpushed — push is a consent gate).

## Shipped / proven (this session)
- **The drive (loop-closing, proven by dogfood):** `claims-skeptic` (independent strand) CONFIRMED
  4/5 core repo claims + caught **deceipt #13** (my "only audit-translator references operators" —
  `audit-client.ts` does too; both dead code, load-bearing claim holds). `outcome-grep` caught
  **deceipt #12** (I'd mislabeled it "DB-blocked"; ran via MCP → 247/247 horizon, 88 one-way, 2
  outcomes). `_STATE/deceipt-ledger.md` now **13**.
- **/fold executed — 3 composed sessions spawned as chips** (human-started, NOTOMATION): NFTT
  `confirmed-not-my-bug` b-rework+ship · memory-index consolidation (why we did NOT consolidate on
  the trunk — it's owned) · **outcome-capture keel** (the "external=apply-with-governor" fold; the
  247/2-closed P1). Trunk left clean.
- **Resume test PASSED:** a fresh agent booted from `pickup-prompt.md` alone, reconstructed the
  gestalt + backlog, and independently re-verified 2/3 structural GREENs (handler-built,
  operators-unwired). The "17 commits ahead" count drifted to 18-then-19 — a self-dating number the
  seed itself flags; direction intact. Seed is seaworthy for resume.

## Open (next session)
1. **Start the 3 chips** as fresh worktree sessions — each self-contained (ground-truth-as-of + SSOTs
   + gates baked into the chip prompt).
2. **Push 19 commits to origin** — off-machine backup; **consent gate** (memory content leaving the
   machine is a real privacy call).
3. **DB claims 247/2/6-of-9-degenerate** remain MCP-verified *by me*, NOT independently (claims-skeptic
   lacks Supabase) — the one un-closed strand, now owned by the keel chip.
4. **ROM candidate** (session calibration-method) parked at the gate — graduates only by a live receipt
   of the method catching an error the existing primitives would miss, never by a compelling thread.


# Handoff — v3.50.0 (2026-08-29)

> **Canon-governance session — the three escalated collisions are RESOLVED and the oracle gate is
> armed.** Renumbered up the version chain (48→49→50) as parallel sessions shipped their own
> v3.48.0 (tool-catalog) and v3.49.0 (Möbius) while this branch was in flight. On
> `claude/elastic-driscoll-a80e72` (PR #194). Oracle audit clean (68 ids, 0 collisions); rebased
> onto live main three times.

## Shipped (this branch)
- **ADR-033 duplicate → Option A.** Serialization Pathogen Family keeps 033; the model-routing/adr-
  audit decision renumbered to oracle-issued **ADR-073** (index.json + header renumber note).
- **Engine-sovereignty doctrine → minted as ADR-072** (oracle-issued). Honors the forward reference
  in main's Möbius (ADR-071) DEWY receipt, which cites "engine-sovereignty (ADR-072)". Old "067"
  claim retired (067 = cross-subject-comparative-recoil); memory + MEMORY.md index re-pointed.
- **ROM vocabulary → Option A.** 7 ROM Primitives (`.claude/arcs-canon.md`) = CANON; 6 execution laws
  → "behavioral laws (derived)"; 7 axioms → "epistemic foundations". Authority index
  `runtime/specs/ROM-AXIS-INDEX.md` + tier banners on all three source files.
- Both `_DECISIONS/CANON-COLLISION-*.md` → **RESOLVED**. `_SEEDS/_oracle.json` adr 71→73.
  `build.html` sv-adrs → 68 (true distinct-ADR count). DEWY receipt appended
  (`_STATE/2026-08-28-session-decisions.dewy.json`).
- **`_DECISIONS/index.json` fully backfilled.** 10 files were missing entries (032, 033-pathogen,
  034, 038, 044, 048, 049, 058, plus 070/071); index now 1:1 with 68 files (set-diff verified).
- **Oracle pre-commit gate ARMED** for this worktree (`core.hooksPath = scripts/git-hooks`).
- **Norse ROM candidates**: Loki inversions written (Ullr + Baldur); numbering gate cleared. NOT
  ratified — remaining hard gate is a live Ullr Graduation Receipt + a live Baldur Witness Receipt.

## Open (next session)
1. **Nightly canon-propagation cron — still HELD.** Arm after merge: `cp scripts/launchd/care.arcs.canon-propagation.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/care.arcs.canon-propagation.plist`.
2. **Norse ROM ratification** blocked on the live-receipt gate (see above).
3. **Canon-propagation queue** has one judgment item (`invariant-non-sycophantic`, default no) — left for /canon-review.
4. **Merge PR #194 promptly** — main is churning fast; this branch went stale 3× on the handoff/build.html hot files (canon work never conflicted).


> _v3.49.0 (Möbius/induction) relocated to `_ARCHIVE/handoffs.md` on 2026-09-05; v3.48.0 (tool-catalog close) relocated on 2026-08-29; v3.47.0 (tool-catalog) + v3.46.0 (receipt-surface) relocated on 2026-08-29; v3.45.0 relocated on 2026-08-28; v3.44.0 (Ahmed) relocated on 2026-08-27; v3.43.0 relocated on 2026-08-27; v3.42.0 relocated on 2026-08-26; v3.41.0 relocated on 2026-08-26; v3.40.0 on 2026-08-23; v3.39.0 + v3.38.0 relocated on 2026-08-19; v3.37.0 (Comet resume) relocated on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
