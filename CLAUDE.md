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

# Handoff — v3.147.0 (2026-11-15)

> Three days (2026-11-12 to 11-15) across about fifteen sessions, folded from the shared progress ledger because no session left a fragment. The design-system kit grew from a pile of one-off pages into numbered organisms with a trial lane: option board (2227), atomic composer seed (2225), operator and chiefs roster (2229), chip true-up (2230), design-candidate lane (2232), strata explorer 69 (2238), week-plan 70 and proof lockup 71 (2239, 2240, 2270), hardening week strip (2261). Gravity overview work ran as one orchestrated family under harrison-dogfood. An axe 4.14 bump exposed a latent wordmark a11y defect, fixed on main (2262). Recoil wave 2 advanced in parallel: recoil-epic-tool-catalog, backlog-merge-driver-by-id, recoil-runner-beats and recoil-real-model-run are DONE on main.

## Goal / true north
Land the open kit and Gravity PRs on Zach's word, prove the axe 4.14 bump green, and finish recoil wave 2 (two READY rows, then the kairos test and Brian acceptance).

## What changed
- PR 2232 merged (2fe62730): design-candidate lane (scripts/design_candidates.py, runtime/specs/design-candidates.json, read by token_source_gate, motion_policy_gate and component_source_gate, plus pre-commit). PR 2235 merged (ec7b02ed): backlog row design-candidate-lane and tool catalog.
- PR 2227 merged (8a7d3919), receipt 2026-11-13--option-board-pr2227--ZH. PR 2244 closed unmerged as superseded by PR 2243 (866de431).
- PR 2218 merged with receipt (status page rebuild).
- PR 2262 merged (73b3042a, by the busy-kirch session, receipt filed there): the ARCS Field OS wordmark takes its name from visible text on blacksmith, growth-ai, mercury-operator and sentilink-operator, which clears axe 4.14 rule label-content-name-mismatch.
- My Ally receipts: closeloop (call moved to next week, 7-day sign NO) and ex-ante sign-before-kickoff (review 2026-11-19).
- Memory banked 2026-11-15: axe-upgrade-flags-old-defect-fix-on-main-then-rebase, fe-smoke-single-runner-fixed-ports, and a bash 3.2 guard section in long-inline-shell-goes-in-a-script-file.

## Current state
- Merged since v3.146.0 (receipts filed by the merging session unless noted): 2218, 2225, 2226, 2227, 2228, 2229, 2230, 2231, 2232, 2235, 2238, 2239, 2240, 2243, 2251, 2261, 2262, 2265, 2270, 2271. Two receipts may exist for 2227 (see Open).
- Open PRs: 2273 rosetta /voice link and leak gates; 2272 Dependabot minor-and-patch incl. axe-core 4.14 (replaces closed 2224); 2266 kit 73 braided lanes on status.arcs.care/beliefs; 2259 chip radius; 2248 kit-periodic-table rows; 2247 night-moves 11-12; 2222 Reading Room sixth room; 2221, 2260, 2267 dreaming passes 10 to 12; 2219 tabbed-brief lockup; 2214 Hermes review gate; 2073 Harrison recoil close; 2068 My Ally three-things rule.
- Kit numbering settled: 69 strata, 70 week-plan, 71 proof lockup, 73 braided lanes.
- fe-smoke is single-runner by construction (fixed container and ports on one Mac).
- Recoil wave 2 on main: DONE recoil-epic-tool-catalog, backlog-merge-driver-by-id, recoil-runner-beats, recoil-real-model-run; READY recoil-brian-ssot, recoil-hardstop-amend; HOLDING recoil-kairos-7s-test and R12 recoil-brian-acceptance.
- MEMORY.md index at 24,402 bytes of the 24,576 cap.

## Decisions made
- Zach, 2026-11-14: fix the wordmark on main rather than raise the a11y baseline.

## Open decisions (waiting on Zach)
1. Zach: PR 2219 (tabbed-brief lockup). Owner local_44360349 is blocked by the kintsugi gate on public/rosetta-voice.html (23 findings from main): fix the page on main, or book a seam.
2. Zach: confirm week 1 of _ARTIFACTS/week-plan/gravity.json before weeks 2 to 7 are drafted.
3. Zach: the Gravity date seams, RFP-O-Matic (10-30 vs 11-02) and NFTT (09-02 vs 08-18), raised by local_44360349.
4. Zach: PR 2218's status-page grammar choices (gain seam, open interval, pressure gauge, canonical altitude ladder) and whether to start the wire and audit sessions.
5. Zach: rule on dreaming pass 5 F1 (bash 3.2 harness refusal, 57 hits in 34 sessions in 4 days); the lesson is banked in memory, the formal ruling and any hook are not.
6. Zach: the visual-grammar run waits on the composer-dogfood first round and his go.

## Open (other)
1. proposal_construction.py ORPHAN-TOOL hold in jtbd-graph-triage.json resolves by 2026-11-20 (owner: the session that added it).
2. Production deploy after the kit merges not checked.
3. Carried from v3.146.0: PR 2180 Gasmi twin, spec §8 Q4 item 3, cold-reader check on 3 Gasmi J4 cells, the groom decision packet, the main-checkout move (main checkout at 4afdce16, behind origin/main; project skills load stale).

## Next action
Zach clears the merge queue in one pass (2272 after green fe-smoke, then 2266, 2219, 2073); then start recoil-brian-ssot as the next wave-2 session card.

## Cold-start recipe
- gh pr list --state open
- cat _STATE/handoff-progress.md (the per-session deltas this block folds)
- python3 scripts/backlog_graph.py --top 30; filter epic recoil-call-service-wave2
- Merge: scripts/safe_merge.sh <pr> <head>, one receipt per merge.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261115T191024Z--claude-myally-email-access-concerns-5dd89f.md` (branch `claude/myally-email-access-concerns-5dd89f`, head `3f9b9f90`).
