@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
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

# Handoff — v3.32.0 (2026-08-11)

> **Active pickup point.** v3.31.0 relocated to `_ARCHIVE/handoffs.md`. Headline: the **model-tier
> router** (ADR-047) — recommend Haiku/Sonnet/Opus by reversibility x value, with a ruin-floor guardrail.

## Headline: model-tier router — route by reversibility x value, never downgrade ruin

Zach wanted to save $$ ASAP by pushing cheap work to cheap models. Built the mechanized form and
locked the operating principle.

**Built (ADR-047):**
- `scripts/model_tier_router.py` — stdlib, zero-dep heuristic classifier, **same shape as the watcher
  family** (`surface_watch.py` / `adr_dewy_watch.py`: compiled cue lexicons -> score -> recommend,
  `--self-test` / `--stdin` / `--json` / `--sessions`, dedup JSONL ledger to `_INBOX/` (gitignored)).
- Routes: routine/deductive/reversible -> **Haiku**; structured-in-guardrails -> **Sonnet**;
  abductive/high-value/irreversible -> **Opus**.
- **Guardrail (the whole point):** any ruin/irreversible cue (delete, drop, migration, deploy, prod,
  payment, auth, secret, publish, send) **floors the rec at Opus + flags `needs_human_confirm`, never
  downgraded** — even when the task is framed as "quick / just". Ambiguity rounds UP to Sonnet. Ties
  break toward the more capable tier. NOTOMATION: recommends only, never auto-switches.
- 10/10 self-test + guardrail invariant assertion. Dogfooded live: building the router itself routed
  to Sonnet (honest); a typo fix to Haiku; "quick prod redeploy" caught -> Opus.

**The design point:** the cost pressure itself is the ruin vector — the urge to save fast is exactly
what tempts cutting the corner on the one one-way-door task. The router happily downgrades routine
work but refuses to downgrade survivability. Locked to memory as a go-forward operating principle:
[[model-tier-routing-locked-principle]] (governs hand-routing too, not just the script).

**Not wired into any dispatch layer** — intentional. Wiring tier recs into the conductor/staff layer
would flip the NOTOMATION posture and needs a stronger guardrail proof than a self-test (noted in ADR-047).

## Captured (ADRs / memories)
- **ADR-047** — Model-Tier Routing by Reversibility x Value. `_DECISIONS/`, indexed in `index.json`.
- **Memory** — [[model-tier-routing-locked-principle]] (feedback, LOCKED). Ran a full
  `/consolidate-memory` pass: re-filed the 13 "Misc" stragglers into real sections, dropped 6 dormant
  July job-app pointers from the index (files kept on disk), index now 136 lines, reconciles clean.

## Next session starts at
No blocker from this work. Optional router follow-ups: open a PR (branch
`claude/kind-grothendieck-fd2df4`), or wire recs into the staff layer (out of scope; see caveat above).
Carrying forward: **Yuri's reply** (nothing pending on our side, [[project_yuri_kleban_google]]);
Todd's Sugar sandbox call gate pending Todd's approval.

## Blocking
NONE.

## Deploy note
This session touched only `scripts/`, `_DECISIONS/`, `_STATE/`, `.gitignore`, and `~/.claude/` memory
— no `next.config.ts`, no product code, so no build triggered. Commits `efcb386` + `c61d948` already
pushed to `origin/claude/kind-grothendieck-fd2df4`. Content-only pushes from `main-wt2` with
`git push --no-verify` per prior convention; SSOT/script/doc changes are build-excluded or harmless.
