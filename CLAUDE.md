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

# Handoff — v3.31.0 (2026-08-11)

> **Active pickup point.** v3.30.0 relocated to `_ARCHIVE/handoffs.md`. Headline: `/witness`,
> the live-capture counterpart to `/night-moves`.

## Headline: `/witness` — attest a flash of brilliance at the moment it happens

Zach asked whether a genuine insight mid-conversation deserves a scribe ("can I get a witness —
the tree did fall, and this is the sound it made"). `/night-moves` (v3.30.0) already covers the
day; nothing covered the moment.

**Built (ADR-046):**
- `WORLD.md` → **THE WITNESS** — a new section beside the Drift Sentinel. The behavioral trigger:
  Claude offers `/witness` unprompted when it notices a principle naming itself, a "wait, that's
  it," or its own line compressing sharper than the surrounding conversation. Deliberately rare —
  over-firing means the trigger is mistuned.
- `.claude/commands/witness.md` — the capture itself. Verbatim quote, timestamp, one honest `y`
  gut-check (SCRATCH/YELLOW/GREEN). No research, no options-considered, no numbering — the
  opposite weight of `/dewy-stub`. Appends to `_STATE/witness/<date>.jsonl`.

**The design point:** a witness stub is raw material, not a decision. Promotion to an
ADR/DEWY/memory is a separate, later, deliberate act — never claim more permanence at capture
time than the moment earned. Same honesty principle as ADR-044 (temporal-provenance), applied to
attestation instead of capability claims: reconstructing a "witness" after the fact is the same
dishonesty as stating aspiration as present fact.

**Proven live, first entry:** `_STATE/witness/2026-08-11.jsonl` — the founding moment itself
(the "can I get a witness" line), GREEN.

**Not wired into `/night-moves` yet** — intentional. Revisit only after a few days of real
`/witness` firings show the pattern is worth ingesting into the daily digest.

## Captured (ADRs / receipts / memories)
- **ADR-046** — Witness Trigger: Live Capture of a Flash of Brilliance. `_DECISIONS/`.
- **DEWY receipt** — `2026-08-11-witness-trigger-built`, new file
  `_STATE/2026-08-11-session-decisions.dewy.json`.
- **Memory** — [[witness-trigger-attest-in-the-moment]]. Also consolidated one orphan into
  `MEMORY.md`: [[counterpart-pseudonym-key-public-artifacts]].

## Next session starts at
No blocker from this work. Carrying forward: **Yuri's reply** (nothing pending on our side — see
[[project_yuri_kleban_google]]) and Todd's Sugar sandbox call (Aug 11, Long Ngo; sprint gate
pending Todd's approval). If `/witness` starts firing, watch for over-triggering — tighten the
signal in WORLD.md → THE WITNESS if it does.

## Blocking
NONE.

## Deploy note
Content-only pushes from `main-wt2` with `git push --no-verify`. `next.config.ts` triggers a real build;
SSOT/script/doc changes are build-excluded or harmless. Robin surfaces regenerate byte-identical unless
their SSOT changed (verify with a diff).
