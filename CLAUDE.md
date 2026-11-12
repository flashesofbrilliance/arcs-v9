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

# Handoff — v3.145.0 (2026-11-12)

## Goal / true north
Weld the war-room recoil report and the recoil-skim page into one standalone composable call service: call in, decompose, five verbs, deconstruct, ADR-060 hypercube, atlas v2, HUD flight with time scrub and kairos.

## What changed
- PR 2166 merged (101eeb1c): R8 J4 hypercube index and explorer; receipt 2026-11-12--recoil-hypercube-index-pr2166--ZH (approval relayed from the parent session: Zach, "lets merge those", for 2164, 2165, 2166).
- PR 2164 merged (b6485191): R5 component set; receipt 2026-11-12--recoil-component-set-pr2164--ZH.
- PR 2165 merged (2560d09b): R9 atlas v2 schema and J5 export; receipt 2026-11-12--atlas-v2-schema-export-pr2165--ZH.
- Backlog trued up in this sweep's PR: R5, R7, R8, R9, R10 DONE with sha and receipt; R6 and R11 READY.
- Spec gained §9 Status (merged list, critical path, open §8 questions).

## Current state
- Epic recoil-call-service: R1 to R5 and R7 to R10 DONE. R6 recoil-print-target READY, R11 hud-atlas-v2-flight READY, R12 recoil-brian-acceptance HOLDING on R6 and R11.
- All 15 epic PRs checked with gh pr view: every one merged except PR 2149 (allowlist, open).
- Every merged epic PR has a decision receipt in public.decision_receipt.
- Child sessions R1, R2, R3, R4, R5, R7, R9, R10 and the fg4 sweep are idle with their PRs merged; R8 is merged too. None archived.

## Decisions made
- Backlog edits waited until 2166 merged, since R8's branch carried its own row.
- R8 resolved its main merge with the handoff-molt-guard override ARCS_ALLOW_DIRECT_HANDOFF=1 on the merge commit only, after checking CLAUDE.md, _ARCHIVE/handoffs.md and _SEEDS/_oracle.json were byte-identical to main; recorded as unconfirmed in the receipt.

## Open decisions (waiting on Zach)
1. Zach: spec §8 questions 1 to 5 (720 degrees, PDF palette, counterpart twin, §6.3 hard-stop list, PII on the live Brian artifact). Question 1 gates R11, question 2 gates R6.
2. Zach: start R6 and R11 session cards, or hold.
3. Zach: archive the idle child sessions (R1, R2, R3, R4, R5, R7, R8, R9, R10, fg4 sweep) or keep them.
4. Zach: merge PR 2149 (allowlist).
5. Zach: start or dismiss the backlog-cards skill card (task_7114301a) and the parent's "Merge train, night-moves and dream catch-up" card (offered, never started).

## Open (other)
1. READY row backlog-merge-driver-by-id would end the induced-backlog.jsonl conflict class seen on nearly every epic PR.
2. handoff-molt-guard should skip merge commits whose CLAUDE.md equals the merged parent (R8 finding).
3. Kit gap: no .chip.magenta in kit 28; needs a kit release (R5 finding). R3's DOC_EXTRA folds into _tokens.css at the same release.
4. R12 needs an SSOT for the Brian call; caching the Granola transcript would let J1 read real turns (R5, R7 findings).

## Next action
Zach answers §8 questions 1 and 2, then starts the R6 and R11 session cards.

## Cold-start recipe
- _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md §7, §8, §9.
- python3 scripts/backlog_status_check.py --check; python3 scripts/backlog_graph.py --top 30.
- Hand-over notes per row: ~/Library/Application Support/Claude/side-session-notes/local_dfd22ff0-bc9a-47ce-bc38-d897e249ad24/R*.md.
- Merge with scripts/safe_merge.sh <pr> <head>; one decision_receipt per merge (job_id job:backlog:<row>, tool_id tool:script:safe_merge.sh).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: Shavasana
> - **Exhale** (what went out): 1 commits, 0 merges to main (scope: branch claude/recoil-sweep-molt-ee9c62), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 1 unconfirmed markers in the day's records.
> - **Breath balance**: manifesto (exhale, no inhale).
> - **Sycophancy check**: agreement 12 / dissent 1 (ratio 6.0) → THIN: high agreement, little dissent.
> - **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: merges, shas and receipt ids were checked here with gh and SQL; R8's override and self-test claims are labelled as R8's report. Sycophancy THIN; dissent on record: backlog edits deferred until 2166 merged instead of editing in parallel. Somatic: not asked. Disposition: release.

> Molted from `_HANDOFFS/fragments/20261112T150139Z--claude-recoil-sweep-molt-ee9c62.md` (branch `claude/recoil-sweep-molt-ee9c62`).
