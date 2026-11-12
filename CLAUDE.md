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

# Handoff — v3.144.0 (2026-11-12)

> ### Shavasana — handoff pause, 2026-11-12 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-recoil-call-service), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 1 unconfirmed markers in the day's records.
> - **Breath balance**: breathing (both directions).
> - **Sycophancy check**: agreement 14 / dissent 1 (ratio 7.0) → THIN: high agreement, little dissent.
> - **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: merges, shas and receipt ids are checked here; R3, R7 and R9 claims are labelled as those sessions' reports. Sycophancy THIN; dissent on record: merged 2154 out of the approved order and said so, and flagged R3's self-merging PR against the safe_merge rule. Somatic: not asked. Disposition: release.
>
> > Recoil call service session, 2026-11-11 to 11-12: PDF print fix, arc-weld spec and induced backlog, then a merge train of 8 child PRs.

## Goal / true north
Weld the war-room recoil report and the recoil-skim page into one standalone composable call service: call in, decompose, five verbs, deconstruct, ADR-060 hypercube, atlas v2, HUD flight with time scrub and kairos.

## What changed
- PR 2145 merged (50e8b80e): recoil PDF print clean (site chrome data-print="hide", page breaks) and module order (Where it stands first, method in lifecycle order); prod READY at 50e8b80e; receipt 2026-11-12--recoil-pdf-print-order-pr2145--ZH.
- PR 2146 merged (a09381ca): spec _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md plus 13 backlog rows (epic recoil-call-service, R0 to R12); receipt 2026-11-12--recoil-call-service-spec-pr2146--ZH.
- PR 2150 merged (ac7ab355): R1 kit reconcile; receipt 2026-11-12--recoil-kit-reconcile-pr2150--ZH.
- PR 2151 merged (d568e4f2): R2 SSOT v2 schema and v1 adapter; receipt 2026-11-12--recoil-ssot-v2-schema-pr2151--ZH.
- PR 2154 merged (b3196ff8): R4 stage runner scripts/recoil_service.py; receipt 2026-11-12--recoil-service-cli-pr2154--ZH.
- PR 2155 merged (e157c8c9) by the R3 session: token unify; its receipt 2026-11-12--recoil-token-unify-pr2155--ZH; PR 2159 set its row DONE (2df12a52); PR 2161 (fg4 sweep) merged per the R3 session's report.
- PR 2158 merged (36d18b25): R7 J1 to J3; receipt 2026-11-12--recoil-decompose-verbs-pr2158--ZH.
- PR 2152 merged (af08123b): R10 forecast base rates; receipt 2026-11-12--forecast-base-rates-pr2152--ZH.
- PR 2149 open: allowlist impeccable context and Apple Notes reads (fewer-permission-prompts).

## Current state
- PR 2164 (R5 component set) open, all checks SUCCESS, MERGEABLE CLEAN; not merged (head per gh pr view 2164).
- PR 2165 (R9 atlas v2 schema, J5) open; CI was running at the R9 session's last report; loader not opened in a browser.
- R8 hypercube index session (local_d5cf3d9b) still working, no PR yet.
- Card proposed, not started: backlog rows to session cards skill (task_7114301a).
- Backlog rows still RUNNING on main though merged: recoil-ssot-v2-schema, recoil-service-cli (R7 PR 2158 flipped them per its report, unverified here), forecast-base-rates (R8 brief flips it), recoil-kit-reconcile (R5 PR 2164 flips it).

## Decisions made
- Zach: merge 2145 and 2146; then "go ahead" on 2150, 2151, 2155, 2154; then "Yes, merge both" on 2158 and 2152.
- 2154 merged before 2155 (out of the approved order) because 2155 was red and 2154 does not depend on it; noted in its receipt.
- The lite page's generating prompt is not on this machine; its own Glass box is the only record (cited in spec §1).

## Open decisions (waiting on Zach)
None.

## Open (other)
1. Merge PR 2164 (R5) and PR 2165 (R9) once green.
2. Spec §8: meaning of 720 degrees, PDF palette, counterpart twin, autopilot hard-stop list, PII on the live Brian artifact (personal email and a sensitive fact behind the link only).
3. Start or dismiss the backlog-cards skill card.
4. Merge PR 2149 (allowlist).
5. _QUEUE/induced-backlog.jsonl conflicted on nearly every PR this session (at least 6 merges of main into branches); a per-row file or a union merge rule would remove the class.
6. Unstarted rows: R6 print target (after 2164), R11 HUD flight (after 2165), R12 Brian acceptance (after R5, R6, R8, R11).

## Next action
Zach gives or withholds the merge go on PR 2164 and PR 2165.

## Cold-start recipe
- Read the spec _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md §7 (row graph) and §8.
- gh pr view 2164; gh pr view 2165; python3 scripts/backlog_status_check.py --check.
- Merge with scripts/safe_merge.sh <pr> <head>; file one decision_receipt per merge (job_id job:backlog:<row>, tool_id tool:script:safe_merge.sh).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261112T144547Z--claude-handoff-recoil-call-service.md` (branch `claude/handoff-recoil-call-service`, head `581cf0f6`).
