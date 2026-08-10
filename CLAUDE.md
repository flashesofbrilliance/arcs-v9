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

# Handoff — v3.28.0 (2026-08-10)

> **Active pickup point.** v3.26.0 + v3.27.0 relocated to `_ARCHIVE/handoffs.md` (lean-file policy).
> This block is the whole current picture. The Yuri counterpart family is send-ready and has survived
> the lens gauntlet, the register gauntlet, the transcript, a 6-facet persona gauntlet, AND a full
> LinkedIn-thread vibe refit. One more persona gauntlet is IN FLIGHT (see Blocking).

## Headline: the Yuri family is transcript-true, honest, vibe-matched, and machine-gated for overclaim

Everything below is live on `*.arcs.care` (ungated, noindex, link-only), main `39c4332`+.

**The family, refit to his ACTUAL vibe (full LinkedIn thread, not just the call).** Yuri is warm,
bite-size, no-agenda ("nothing to sell/ask, just kudos"), busy, and BOUNCES OFF ABSTRACTION — he told
Zach twice the pages were "high level and theoretical / how do I use this." Refit (main `fad2c55`):
- **one-door** = warm two-link entry. Hero OPENS by saying what it is in his terms ("the pre-meeting
  brief your team already builds, but closed and scored"). Menu collapsed to TWO: the before/after
  (codex, "start here") + the diamond ("the deep cut, for builders", face #2). **Profile REDACTED from
  the send** (unlinked; page still live) — it read as a dossier and was the hardest for him to judge.

**FALSE-CLAIM FIXED + machine-gated (main `b1e4fd0`, `8678392`).** "model-agnostic, runs on Gemini,
nothing leaves Google" was false present-tense — ARCS runs on **Claude/Anthropic** today. Now honest
everywhere ("Claude today; a Google-internal version could run on Gemini"), and named that **Agentum** is
the genuinely model-agnostic one (trust move). Operationalized as **ADR-044 / the `temporal_provenance`
gate** in `forge_counterpart.py` — refuses to write unhedged aspiration; on first run it caught a 2nd
live instance (Robin's one-door), now fixed. Whole corpus passes clean.

**The codex "MAGIC YOU ASKED FOR" offer-ladder** (a 4-rung sales menu mislabeled as magic, wobbly POV)
was cut to an understated no-pitch close.

**Three gauntlets deep + the persona gauntlet (main `4b1bde4`).** The 6-facet Yuri simulation +
adversarial verifier healed 15 verified cracks (buyer-relabeling → recognition; "across Alphabet"
rollout → capped; the "4/5 misses all productive" ratchet → the one honest bet; codex chart de-duped +
beat order fixed to the tape; jargon; diamond rounded to 5-pt steps). Spine protected (self-scoring,
diamond fence, earned fidelity).

## Captured this session (ADRs / receipts / memories)
- **ADR-044** — Temporal-Provenance Gate (fact-vs-fiction chain of custody). `_DECISIONS/`.
- **DEWY receipts** — `_STATE/2026-08-10-session-decisions.dewy.json` (4: temporal gate, redact-dossier
  refit, diamond earned-fidelity, persona-gauntlet method).
- **Memories** — [[temporal-chain-of-custody-fact-vs-fiction]], [[earned-fidelity-not-maximal-diamond-cut]],
  [[counterpart-vantage-premortem]], [[gauntlet-tuned-to-register-catches-what-detector-cannot]] (esc 3).

## The two drafts (ready for Zach to SEND — I do not send)
Both fulfill the reply Zach already promised on LinkedIn ("something deeper and more self-explanatory")
and answer his how-to-read / who-for / how-to-use, in his register, pointing only where the page points
(one-door + diamond; no profile, no model-agnostic claim). **Rec: lead with the LinkedIn reply** (thread
is live there), Gmail as the fuller follow-up. Full text is in the session transcript.

## Next session starts at — the in-flight gauntlet, then the send
1. **Verify the in-flight persona gauntlet** (Workflow `w6oq90dah`, run `wf_a88678dc-f66`) against the
   CURRENT pages; re-verify each flag vs source, heal only confirmed cracks, redeploy. Its context was
   refreshed to the 2-link/warm/honest state so it should not re-flag fixed items.
2. **Send** (Zach, human): LinkedIn reply first, then Gmail, pointed at `yuri.arcs.care`.

## Blocking
NONE internally. The persona gauntlet `w6oq90dah` is still running — its results land via task
notification; do not assume them. The send is Zach's.

## Deploy note
Content-only pushes from `main-wt2` with `git push --no-verify` (fresh worktree lacks node_modules).
`next.config.ts` changes trigger a real Vercel build; content/SSOT/script changes are build-excluded or
harmless. Robin surfaces regenerate byte-identical unless their SSOT changed (verify with a diff).
