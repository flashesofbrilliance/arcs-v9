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

# Handoff — v3.29.0 (2026-08-10)

> **Active pickup point.** v3.28.0 relocated to `_ARCHIVE/handoffs.md`. **The Yuri suite is SENT.** This
> block is the closed-loop final state; there is no pending action on our side.

## Headline: the Yuri family shipped, four gauntlets deep, honest, and SENT

**SENT 2026-08-10.** Zach tweaked + sent the Gmail (Gmail draft `r-2135081402185612206` -> siryuri@gmail.com,
subj "How to read the thing I sent, and who it's for"), pointing to `yuri.arcs.care`. The stale Aug-6 draft
(carried the false model-agnostic claim + a password ref + the old 3-surface structure) was replaced with
the current honest version first. **Ball is in Yuri's court.**

**Final page structure (live, ungated, noindex):** warm two-link one-door — the before/after (codex,
"start here") + the diamond ("the call, moment by moment · a read, not the machine", face #2). **The
machine** (the scored HIT/MISS closed loop + the interactive "file your own bet" studio = the RECEIPT) is
chained off the codex close ("see it scored ->"), so the door stays two links. **Profile redacted** from
the send (dossier; page still live, unlinked). Hero opens in his terms ("the pre-meeting brief your team
already builds, but closed and scored").

**Honest + machine-gated.** ARCS runs on **Claude today**; a Google-internal version *could* run on Gemini
(never stated as present fact). Enforced by **ADR-044 / the `temporal_provenance` gate** in
`forge_counterpart.py` (refuses unhedged aspiration; caught a 2nd instance on Robin). Agentum named as the
genuinely model-agnostic one.

**Four gauntlets survived** (lens -> register -> primary transcript -> 6-facet persona ×2). The 2nd persona
gauntlet (main a946c3f/a9b2b8c) fixed: the diamond onenum contradicting its own chart (now admits the
doc-miss flicker); receipt over-anchor to internal-Google (two-path, portable-first); codex condescension
re his shop; org/VC ladder collapse; not-flattering/free/5x-disclaimer trims. Spine protected (self-scoring,
fence, hero line, doc-miss, consent, model-hedge).

## Pipeline formalized (back-propagated from the send)
This session's emergent sequence is now the canonical `/forge` flow, not tacit. The `/forge` skill encodes
the full 9 phases (gather-incl-full-comms-thread → synth → generate → verify-incl-temporal-gate → deploy →
**GAUNTLET LADDER → VIBE REFIT → SEND PREP → CAPTURE**), and the persona-facet gauntlet is a REUSABLE
parameterized Workflow: `.claude/workflows/counterpart-gauntlet.js` (`Workflow({name:'counterpart-gauntlet',
args:{counterpart, repo, transcript, comms_thread, surfaces, memory, register, already_healed}})`). Robin or
any new counterpart runs the same battle-tested ladder by construction. See [[counterpart-forge-pipeline]].

## Captured (ADRs / receipts / memories)
- **ADR-044** — Temporal-Provenance Gate. `_DECISIONS/`.
- **DEWY receipts** — `_STATE/2026-08-10-session-decisions.dewy.json` (5: temporal gate, redact-dossier
  refit, diamond earned-fidelity, persona-gauntlet method, the send).
- **Memories** — [[temporal-chain-of-custody-fact-vs-fiction]], [[earned-fidelity-not-maximal-diamond-cut]],
  [[counterpart-vantage-premortem]], [[gauntlet-tuned-to-register-catches-what-detector-cannot]] (esc 3),
  [[project_yuri_kleban_google]] (SENT).

## Next session starts at — Yuri's reply (nothing pending on our side)
When Yuri replies, the live threads (all teed up in [[project_yuri_kleban_google]]): his read on ARCS
positioning/GTM (his offered ask), Agentum chat (two builders), part-two / GCP dogfood, and the portable
diligence/M&A path (Purpose Built + ex-UBS partner). He is warm, no-agenda, bite-size, bounces off
abstraction -> keep replies short + concrete; let him pull. Point Claude at his message when it lands.

## Blocking
NONE. Sent; awaiting Yuri.

## Deploy note
Content-only pushes from `main-wt2` with `git push --no-verify`. `next.config.ts` triggers a real build;
SSOT/script/doc changes are build-excluded or harmless. Robin surfaces regenerate byte-identical unless
their SSOT changed (verify with a diff).
