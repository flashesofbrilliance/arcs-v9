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

# Handoff — v3.8.0 (2026-07-19)

> **For Claude Code:** active pickup point. v3.7.0 above is preserved for history; v3.6.0 and older were
> relocated to `_ARCHIVE/handoffs.md` per the lean-file policy this session established.
> Branch `claude/token-efficiency-audit-ip3l3x` — **MERGED to main** (verified 2026-07-19: main contains
> the lean CLAUDE.md ≈3.7k tok + MEMORY.md ≈6.5k tok; branch is an ancestor of `main`).

## What this session did (17 commits, `c2eaf80`..`117fcf0`)

A token/budget efficiency audit that turned into a fix chain. Full narrative in `MEMORY.md [v3.8.0]`;
per-topic detail in the `_PATTERNS/2026-07-19-*` docs.

- **Audit + Fix #1/#2:** the real #1 token drain was the append-forever CLAUDE.md/MEMORY.md loaded every
  session (~24.6k–39k tok), not the Sentinel. Split dead history to `_ARCHIVE/`; CLAUDE.md 19.8k→3.6k,
  MEMORY.md 14.8k→5.8k; amended the append-only policy to lean-working-file + archive.
- **ADR-035:** ratified the real Commit-NCI rubric (5 lenses); wired `nci-scoring` skill + `/nci-commit` +
  `/drift-check`. Added `/rca` (triage-gated root-cause command).
- **Tech-debt batch** (`_PATTERNS/2026-07-19-tech-debt-batch.md`): A1 console cleanup, A5/A6 fixes, B1
  diagnosed clean, A2/A3/A4 triaged out. **B4** build-red root-caused to shell `NODE_ENV=development` →
  pinned `NODE_ENV=production` in the build script (use `npm run build`, not bare `npx next build`).
- **B2:** implemented the spec 5-lens `nci_by_lens`/`nci_grade` (additive), surfaced weak-lens in the brief,
  added a `stop_reason` truncation guard.
- **Security:** `_PATTERNS/2026-07-19-threat-assessment.md` + `src/lib/sanitize.ts` (unit-tested 8/8) —
  trust boundary at every recursive rung against injection cascade.

## Open items (also in `_QUEUE/PENDING.md`)

- ~~**Merge this branch to main**~~ ✅ DONE 2026-07-19 — merged; lean CLAUDE.md/MEMORY.md confirmed on main.
- **Out-of-band** (`_PATTERNS/2026-07-19-out-of-band-actions.md`): Sentinel — DISABLED 2026-07-19; rebuild
  **report-only** from the `arcs-decision-receipts` env using the full recipe in
  `_PATTERNS/sentinel-rebuild-spec.md`. Also: SageTrace RLS (Supabase CLI), connector/env/DNS/key items,
  Dan Pascone gate.
- **In-repo follow-ups:** cadence lens from time-ROM; HOLD gate at NCI<40 (overlaps the Calibrate HOLD gap).

## Honesty flag

All compass-side changes are build + typecheck + unit-tested, but **NOT driven via a live compass call**
(no `ANTHROPIC_API_KEY` in the cloud session). Verify end-to-end after merge/deploy.

## Last confirmed commit

`117fcf0` — feat(security): trust boundary at every recursive rung.

## Next session starts at

`/handoff-pickup` → merge is done; pick an out-of-band item (Sentinel rebuild, SageTrace RLS) or the
B2 cadence/HOLD-gate follow-up.

---

# Handoff — v3.9.0 (2026-07-19)

> **For Claude Code:** active pickup point. v3.8.0 above preserved; v3.7.0 and older -> `_ARCHIVE/handoffs.md`.
> Two feature PRs shipped to main this session (both MERGED).

## What shipped

- **Token-efficiency audit (PR #62) - MERGED.** Detail: `MEMORY.md [v3.8.0]` + `_PATTERNS/2026-07-19-*`.
  CLAUDE.md/MEMORY.md lean split; ADR-035 Commit-NCI rubric + `nci-scoring` skill + `/nci-commit` +
  `/drift-check` + `/rca`; tech-debt batch; B4 NODE_ENV build fix; B2 5-lens `nci_by_lens`; recursive
  trust-boundary sanitizer (`src/lib/sanitize.ts`).
- **Stateless anonymous brief sharing (PR #100, ADR-037) - MERGED.** Detail: `MEMORY.md [v3.9.0]`. Anon
  bearings shareable via URL-fragment payload (zero server write); recipient recomposes client-side;
  one-view localStorage gate -> `/compass?shared=1` onramp. `src/lib/shareLink.ts` (sanitizes the
  attacker-controllable payload), `/brief/share`, receipt-page "Share" (ephemeral only). Trust-contract
  **v1.3** amended canonical-first (`_CANON/trust-contract.md`), then derived /trust + /privacy. A
  `privacy-review` agent gated it (caught that the canonical doc hadn't been amended - fixed before merge).
- **Branded receipt error/fallback page** (part of #100) - replaced bare red text with Wordmark + card +
  adaptive CTAs (anon-not-here vs load failure).

## Honesty flag (carry forward)

Compass-side changes (B2 5-lens, sanitizer, anon-share) are build + typecheck + unit-tested but **NOT driven
via a live compass call** (no `ANTHROPIC_API_KEY` in the cloud session). **Verify after deploy:** run the
compass anonymously -> Share -> open the link in another browser -> confirm one-time recompose -> onramp.

## Open items (also in `_QUEUE/PENDING.md`)

- **Out-of-band** (`_PATTERNS/2026-07-19-out-of-band-actions.md`): Drift Sentinel disabled by operator
  2026-07-19, rebuild report-only (`_PATTERNS/sentinel-rebuild-spec.md`); SageTrace RLS (Supabase CLI);
  **Vercel platform toolbar** -> disable in dashboard (Settings -> Toolbar); connector/env/key hygiene.
- **In-repo:** B2 cadence lens from time-ROM; HOLD gate at NCI<40 (overlaps Calibrate HOLD gap); the
  Receipt-save-prompt PLG gap.

## Concurrency note

A second session ran on main this whole session (J-items: leak-check gate, watchdog, status board, VOICE
rules). The ADR namespace is lock-free - `ls _DECISIONS/` right before claiming a number (035=commit-nci,
036=repo-split, 037=anon-share). Rebase on origin/main before any push.

## Next session starts at

`/handoff-pickup` -> live-verify the anon-share flow on the deployed site; then an out-of-band item or the
B2 cadence / HOLD-gate follow-up.
