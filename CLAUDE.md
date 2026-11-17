@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  the handoff-progress ledger (jsonl + md under `_STATE/`, gitignored) every turn-with-change, and asks for a `## Delta` at each compaction. Both are gitignored. `/handoff` folds them
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
text: #e2e8f0 | muted: #7a8699 | dimmed: #8391a7  (AA on bg; raised 2026-10-04)
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
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade (canon name; the compass prompt runs L3 as the Kintsugi immune check, and no cascade code exists) · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). The full interactive Next.js page IS committed on main at `src/app/observatory/page.tsx`
(landed 2026-06-23, ~1.2k LOC); the old "never pushed" note was stale (Atlas audit 2026-09-03).
Confirm the `/observatory` route vs the static-demo rewrite before relying on either.

# Token-saving rules
- **Invoke the `token-savings-bank` skill** (user-level, `~/.claude/skills/token-savings-bank`) before any
  fan-out (subagents, chips, parallel sessions), bulk edit, or long resumable task, and whenever you notice
  waste (top-tier model on mechanical work, a subagent for a one-grep question, re-deriving state). It governs
  Claude Code session tokens, which count against the subscription limit (the weekly cap stalled the morning
  jobs task 2026-09-30/10-01). API spend is separate: prompt caching, Batch API, and Haiku roles in
  `src/lib/claude-models.ts`.
- **Before planning any non-trivial task, run `/prior-art <job>`** (`scripts/prior_art.py`): it ranks memory, `_PATTERNS/`, ADRs and the tool catalog against the job so the plan starts from past lessons. Open only the top hits that apply; open the plan with a "Prior art:" line.
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only in components — no Tailwind, no utility classes. Sanctioned exceptions (only these): next/font classes on `<html>`, and the single `src/app/globals.css` (reset + keyframes + font tokens). Tailwind was removed 2026-07-11.
- No new dependencies without asking.
- **Self-contained artifact/page CSS: one shared px `--measure` for BODY/card reading text — NEVER `max-width:NNch` per element** (font-dependent → misaligned right edges that read as broken wrapping). **But LEDES are the exception: a hero/section lede spans the full lane width matching its heading (`max-width:none`), never the narrow body measure — a lede narrower than its heading reads as a broken/abridged block with a dead right gutter (EXCEPTION, 2026-09-29: text INDEX pages such as good.arcs.care/series/* put lede, rows and footer rule on the 680px measure) (`design-full-width-lede-matches-heading`; Zach's standing preference, do NOT "fix" it back to `--measure`).** The "too narrow" symptom is invisible to overflow/clip gates — eyeball lede-vs-heading edges at ~1280px too. Bordered callouts carry the measure on the box, not the inner text. Before shipping any single-file HTML, run the repo's own gate (`scripts/artifact_wrap_lint.py`; `npm test` for `zachharris-xyz`) and sweep 360–1440 incl. the 700–1000 band. Em-dashes 0. Canon: `_PATTERNS/arcs-artifact-css-base.css`; AGENTS.md gotcha #13.


# Versioning & handoff policy (amended 2026-07-19)

> Supersedes the prior "CLAUDE.md — append new sections only; never overwrite" rule, which had grown
> this file to 28 handoff sections / ~19.8k tokens loaded on **every** session. Rationale + measurements:
> `_PATTERNS/2026-07-19-token-efficiency-audit.md`.

- **CLAUDE.md is a working file, kept lean — not an archive.** It holds durable facts (Project Map,
  ROM primitives, token-saving rules) plus **only the latest handoff section** (older arcs live in `_ARCHIVE/handoffs.md` and git; `scripts/handoff_fold.py archive` trims between molts; the cap is 2, the default keep is 1, since 2026-10-17). Sessions no longer edit
  this file to hand off: `/handoff` writes a fragment (`_HANDOFFS/fragments/`, one file per session, raw
  material) and `scripts/handoff_fold.py molt` synthesizes ALL fragments into ONE arc block (Goal, What
  changed, State, Decisions, Open, ONE Next action, Cold-start recipe), versioned by
  `scripts/oracle.py next handoff`, refusing bookends; overflow moves to `_ARCHIVE/handoffs.md` by version
  (ADR-085 part (d) + 2026-10-06 amendment). Unmolted fragments are newer than any block below.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.151.0 (2026-11-17)

## Goal / true north
Clear the 2026-11-17 repo fix queue: merge only what Zach approved, keep main's gates green, leave nothing parked without a reason.

## What changed
- PR #2340 merged (44e26e57): 11-16 night-moves digest; receipt 2026-11-17--night-moves-digest-pr2340--ZH.
- PR #2341 merged (41126776): reading_room_sync on main, stale-refresh wiring, project_mirror.sh; gate chain public words for 1fb74fe4 and 38cc17ce (Zach's Pair A each); receipt 2026-11-17--reading-room-sync-pr2341--ZH.
- PR #2342 merged (59a24f3a): meta-audit and safe_merge descriptions carry the user's words (recall fixtures 3/3, one new); DONE row project-mirror-nightly fixed main's jtbd-graph ORPHAN-TOOL failure; receipt 2026-11-17--prior-art-recall-pr2342--ZH.
- PR #2343 merged (32ac856f): 11-19/11-20 triage cliffs fated on Zach's answers, row triage-cliffs-2026-11-19-20 DONE; receipt 2026-11-17--triage-cliffs-pr2343--ZH.
- PR #2344 merged (24df7530): handoff v3.150.0; receipt 2026-11-17--handoff-v3-150-pr2344--ZH.
- PR #2323 merged (5f273852): re-land of #2293; its description records why #2293's merge commit never reached main (retargeted onto #2290's branch 14 minutes after #2290 merged); receipt 2026-11-17--good-cruft-claims-reland-pr2323--ZH.
- PR #2335 merged (27b72d26), then PR #2338 rebased and merged (44bcf73a); #2338's forge-bundles.json and forge-cost-ledger.jsonl were resolved by replaying each commit's own writes (bundle upsert, ledger append), verified equal to main plus #2338's 30 bundles; receipts 2026-11-17--jobs-pay-screen-pr2335--ZH and 2026-11-17--forge-six-fresh-roles-pr2338--ZH.
- PR #2272: commented @dependabot rebase; its axe failure (gauntlet-log) was already fixed on main in de2ad62a.
- G53 applied: branch.autoSetupMerge removed from .git/config. git worktree prune cleared six dead entries; temp worktrees under ~/Claude removed.

## Current state
- The fix queue has nothing left to merge. Open PRs: 2272 (waits on Dependabot's rebase), 2248, 2068.
- jtbd-graph --check passes on main.
- prl-phase-1-2 is DONE; its ORPHAN-JOB hold was renewed to 2026-12-01 (Zach asked 2027-02-01; the gate caps holds at 14 days).
- Worktree unruffled-moser-c1595d still holds #2338's branch at its pre-rebase head (clean, behind).

## Decisions made
- Zach, 2026-11-17: merge #2340 and #2341 in step 0; later "go ahead" on #2342, #2343, #2344, #2323, #2335 then #2338.
- Zach, 2026-11-17: keep the stripe plugin; apply G53; leave sharp-turing (next-step detector, floor-light) parked.
- Zach, 2026-11-17: good-agent-files, agent-readable-arcs-hosts, prl-phase-1-2 DONE; nftt-every-mistake-became-a-gate and paid-brief-first-dollar re-dated to 2026-12-01; proposal_construction.py got a DONE row.

## Open decisions (waiting on Zach)
1. Zach: #2272 after Dependabot's rebase; check its fe-smoke result.
2. Zach: nftt-every-mistake-became-a-gate (LinkedIn teaser) and paid-brief-first-dollar (STRIPE_PAYMENT_LINK, prod migration) fall due 2026-12-01.

## Open (other)
1. The prl-phase-1-2 hold falls due 2026-12-01; a tool atom for the Zapier/Tidio work would end the renewals.
2. Possible guard: refuse a merge when the PR's base branch already merged (the #2293 failure).

## Next action
Next session: follow the boot block; then check #2272 once Dependabot has rebased it.

## Cold-start recipe
- Read the boot block the session-start hook prints.
- gh pr list --state open; python3 scripts/approvals_ledger.py
- python3 scripts/universe_jtbd_adapter.py --check
- python3 scripts/backlog_graph.py --top 15

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261117T220159Z--claude-handoff-2026-11-17-after-merges.md` (branch `claude/handoff-2026-11-17-after-merges`, head `44bcf73a`).
