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

# Handoff — v3.148.0 (2026-11-16)

> Two weeks of very high throughput (about 300 merged PRs, 2026-11-02 to 11-16) across the UI kit (parts 41 to 73, the kit wire advisors, token tuner, option board, design-candidate lane), the recoil call service waves 1 and 2, Gravity and Louisville sends, Rosetta Voice and status.arcs.care. This molt closes a paperwork pass: PR 2311 merged with a receipt, 23 backlog rows trued up (two stale RUNNING claims closed, then the whole patent-filing chain composted on Zach's ruling (23 rows; graph depth 12 to 6 waves), 14 ripe rows readied), the kit catalyst ledger synced, and cruise control run for the first time. The open edge is a decision queue for Zach, led by JTBD triage holds that expire 2026-11-17.

## Goal / true north
Keep the merge queue and the backlog honest: paperwork matches what merged, rankings lead with work Zach is actually doing, and the harness reports stay fresh.

## What changed
- PR #2311 merged (0baa2968, jobs intake unstall, two seed resumes); receipt 2026-11-16--jobs-intake-unstall-pr2311--ZH.
- 300 PRs merged 2026-11-02 to 11-16 (53 in the last 24h); release notes and status report given in session status-release-notes-91254f.
- Backlog sweep, 23 rows: pr-design-brief-habit and gauntlet-brief-polyform RUNNING to DONE (PRs #2148, #2141 merged 11-12); the 7 READY filing-* rows to HELD, then all 23 open filing-* rows COMPOSTED on Zach's follow-up ruling; 14 ripe OPEN rows to READY (dependencies done or date trigger passed).
- Kit catalyst ledger synced (31 derived events appended), kit-periodic-table.html regenerated.

## Current state
- Open PRs: 2312 status milestones (checks were pending); 2272 Dependabot axe 4.14 (fe-smoke red on a stale 11-15 run, only failure is gauntlet-log.html, fixed on main by #2288; needs a rebase); 2248 (one conflict in the generated kit-periodic-table.html, regenerate); 2214 (five real conflicts incl. scripts/safe_merge.sh and AGENTS.md, owner should resolve); 2222 (fe-smoke red, build not run); 2073 and 2068 drafts (2068 is based on the merged feat/myally-step1-checklist branch, retarget to main before review); dreaming passes 10 to 13 (2221, 2260, 2267, 2276) and night-moves 11-12 (2247) drafts, ruled through a one-form picker in this session.
- Backlog: OPEN 56, READY 33, HOLDING 54, HELD 137, RUNNING 3, BLOCKED 11, DONE 177.
- Cruise-control agent ran for the first time (read-only morning sweep). Approvals ledger: no PR carries a traced approval.
- Sessions: 3 running, about 12 idle with merged PRs not archived.
- Session kind-perlman-3d4858 has an unmerged stale-refresh runner on branch claude/kind-perlman-3d4858 (lattice countables, universe emit, night-moves age as receipts), schedule not installed, row stale-snapshot-refresh-loop HOLDING on Zach.

## Decisions made
- Zach, 2026-11-16: merge PR 2311.
- Zach, 2026-11-16: the patent-filing chain is premature; compost it (not yet ready to patent, core engine and later phases come first).
- Zach, 2026-11-16: sweep merged-PR paperwork and ripe rows in one pass.

## Open decisions (waiting on Zach)
1. Zach: T1 from dreaming pass 13 is urgent: 32 JTBD triage holds expire 2026-11-17 and CI gates then fail on every branch. Re-date or give them job rows.
2. Zach: rule the dreaming picker (safe_merge L1/Q1/T2 as one change, bash 3.2 F1, N1, N2, L2) and the fate of the five draft PRs.
3. Zach: My Ally unpaid discovery is 33.6 to 47.4 h against a 10 h cap: bill, box or stop.
4. Zach: comment @dependabot rebase on 2272 so fe-smoke reruns on current main.
5. Zach: confirm week 1 of _ARTIFACTS/week-plan/gravity.json; settle the Gravity date seams (RFP-O-Matic 10-30 vs 11-02, NFTT 09-02 vs 08-18).

## Open (other)
1. Findings gait: no finding closed in 7 beats; give the oldest open finding a fate.
2. Correction (kintsugi): the status report said 41 rows were already done. Only 2 cited merged PRs (gates-class-prevent-leak-and-render-drift, compounding-model-prereg) and both notes name remaining work, so they stay open; the other 39 were ripe, not done.
3. Doors left OPEN on purpose in the sweep: cia-technical-screen-prep, cia-recoil-close-michael-intro, rfp-ship-resume-tailor-rebase, rfp-ship-public-leak-gate, rfp-ship-packages-publish, myally-step1-audit.

## Next action
Zach rules T1 (triage holds expiring 2026-11-17) before end of day; everything else can wait for the next batch merge.

## Cold-start recipe
- gh pr list --state open; python3 scripts/approvals_ledger.py
- python3 scripts/backlog_graph.py --top 15
- python3 scripts/open_loops.py --summary
- _PROPOSALS/2026-11-16-dreaming-pass-13.md (T1)

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261116T182925Z--claude-status-release-notes-91254f.md` (branch `claude/status-release-notes-91254f`, head `0baa2968`).
