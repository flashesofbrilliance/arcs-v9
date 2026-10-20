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

# Handoff — v3.141.0 (2026-10-20)

> > Shared-intention session (2026-10-20): designed the step after backlog induction (one shared intention, horizons, altitude drill-down, domino line), built a read-only risk underwriter, proved the outcome plumbing, and bridged decision-receipt outcomes into the Accountant.
>
> ### Shavasana — handoff pause, 2026-10-20 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-jtbd-framework), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 2 dissent markers, 0 unconfirmed markers in the day's records.
> - **Breath balance**: mirror (inhale, no exhale).
> - **Sycophancy check**: agreement 1 / dissent 2 (ratio 0.33) → OK: dissent present.
> - **Cold re-read (canary on the draft draft.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: every claim cites a PR, merge commit or receipt id; kept. Two own-errors stay on record in their receipts (merge before a child final push, #1621 to #1627; merge on a pending check, #1722). Somatic: not asked. Disposition: release.
>
> > Opus 5.5 JTBD framework session (2026-10-18 to 2026-10-20): planned and ran the JTBD graph roadmap (Sprints 0 to 5) as a parent session with child sessions and counter-agents, then hardened the merge and receipt path.

## Goal / true north
One generated graph of every Tool, Job, Blocker and design/runtime Dependency in arcs-v9 that Opus can query (`jtbd(job)`), kept honest by gates, receipts and pre-registered tests.

## What changed
- PR #1697 merged (cc17e2ca): status.arcs.care no-JS floor restamped to 5,065 commits, day 194. Receipt 2026-10-20--status-floor-restamp-pr1697--ZH.
- PR #1698 merged (7506fbde): scripts/decision_receipt_to_accountant.py, Accountant cohort `decisions`, accountant_weekly prints synthetic_excluded. Receipt 2026-10-20--decision-receipt-bridge-pr1698--ZH.
- Backlog: receipt-randomized-plumbing-closes DONE (proven, seed 20261020, 5 synthetic closes); ruin bands on 10 rows, confirmed by Zach.
- Open PRs, not merged: #1691 (proposal _PROPOSALS/2026-10-20-shared-intention-before-snap.md), #1694 (risk underwriter design), #1695 (risk underwriter v0 script, branch claude/risk-underwriter-v0), #1696 (claim index, another session).
- Roadmap rows jtbd-graph-s0..s5 (#1613). s0 schema and stable ids, ADR-089 (#1621, repairs #1627, #1631: wildcard host is `any`, checker uses fullmatch). s1 nodes (#1630). s2 edges (#1640). s3 gates (#1667, build fix: tsconfig excludes the fixtures folder, runtime/specs/fixtures/jtbd-graph/gates/probe-evasions.ts).
- s4 retrieval (#1706) won the pre-registered blind test (amendment 7, pool sealed by a separate session #1707, scored #1708): graph 16/18 vs /catalog 6/18, essential recall 0.89 vs 0.16. Wired into /prior-art and /catalog (#1714).
- s5 feedback (#1723, #1726): outcome weights, weekly drift report; receipts gained job_id and tool_id (#1718), on by default via the safe_merge template (#1734); timestamp parse fix (#1737) shows coverage 9/12 (75%).
- scripts/safe_merge.sh (#1728): head pinned, every check SUCCESS, refuses on conflict. Used for every later merge; it refused twice on moved heads, as designed.
- Main gate repair (#1722): dated triage holds (runtime/specs/jtbd-graph-triage.json, max 14 days) for new findings; baseline stays shrink-only. Catalog regen fixed 5 findings at source (#1735).
- decision_receipt is append-only (applied 2026-10-20 after Zach's go; proof passed; #1742, #1743). Receipt 2026-10-20--receipt-append-only-applied--ZH.
- Hook-written state untracked (#1727); schema self-test uses a frozen catalog (#1725); baseline 613 to 418 orphan tools (#1730, #1740); 3 operators composted (#1739); architecture note _PATTERNS/2026-10-20-jtbd-system-architecture.md (#1738).
- Concourse: both pre-reads live with GitHub link (#1670); tailored resume draft PR #1672, held.

## Current state
- Main checkout on origin/main. jtbd --check PASS. Triage holds due 2026-11-03.
- Sprint 5 row HOLDING: coverage check 2026-11-03, blind re-judge 2026-11-17.
- Scheduled: jtbd-weekly-drift-report (Mon, now also reconcile epoch and status-floor check), jtbd-daily-weights-refresh (Mon/Wed/Fri). Both bypass-permission mode, read-only by prompt.
- CI is off (Actions spending limit); merges rested on Vercel and local gates.

## Decisions made
- Zach: intention definition B (stated by Zach) with C (mirror from the backlog) beside it.
- Zach: surgical decomposition lives in a linked spec file per issue (path proposed in PR #1691, not on main).
- Zach: onramp swapped after D0 to the decision-receipt bridge (built, PR #1698).
- Zach: SPECIALTY tier added beside UNINSURABLE in the underwriter; prices shown, never blocking.
- Zach: hyperstition is the fixed second pass after I.D.E.A.
- Zach: execution model is a two-level lattice (parent, children, counter-agents); one pusher per branch (gotcha 22); merges pin the head.
- Zach: s4 judged by pooled blind scoring (amendment 7); "no proof yet" lane declined.
- Zach: hold new gate findings in dated triage, not the baseline.
- Zach: receipts append-only, UPDATE and DELETE refused, corrections by a superseding row.
- Every spawned session gets a backlog row first; its receipt job_id names that row (memory every-spawned-session-gets-a-backlog-row-first).

## Open decisions (waiting on Zach)
1. Zach: Amy draft to amy@recruithaus.com (Gmail draft dated 2026-10-18): send, edit or drop.
2. Zach: funnel seed kill condition due 2026-10-22 (finding f-d1cb1802f5); no receipt yet.
3. Zach: ship or hold PR #1695 (s4 freeze: do not regenerate the tool catalog).
4. Zach: whether to turn CI back on (budget).

## Open (other)
1. George (Scout Global): Zach followed up (bundle 2026-10-16, nudge 2026-10-19; Zach confirmed 2026-10-20). Waiting on George; record a verdict on 2026-10-16--scout-wonderful-fde-lead-ex-ante--ZH when he replies.
2. Vico: Zach is in touch with Joe Schriner (confirmed 2026-10-20). Open only: Zach confirms which one-page attachment went on 2026-10-14, given the Tier 2 no-send-before-NDA note.
3. Domino line D1 to D17 in PR #1691 section 4g; ripe now: D1 (intention test trigger), D2 (steelman the 10 DRAFT abort/rollback texts), D3 (= item 5).
4. Sprint 6 (next): MCP tools as graph atoms so jobs done through Supabase, Vercel, Gmail and others are visible; clears the decision-receipt-append-only triage hold by 2026-11-03.
5. 22 compost candidates in _PROPOSALS/2026-10-20-jtbd-baseline-followups.md await Zach's ruling.
6. 158 orphan jobs; 649 grandfathered integrity cites (judgment work, not scheduled).
7. Concourse: forward the take-home spec when it arrives; resume PR #1672 is ready.

## Next action
Start Sprint 6 (MCP tools in the graph) as a child session with a backlog row first.

## Cold-start recipe
- Read _PATTERNS/2026-10-20-jtbd-system-architecture.md, then the jtbd-graph-* rows in _QUEUE/induced-backlog.jsonl.
- Run `python3 scripts/universe_jtbd_adapter.py --check` and `bash scripts/safe_merge.sh --self-test`.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: Ground truth
- Prod read-only (2026-10-20): decision_receipt and Receipt tables via Supabase execute_sql; git origin/main for counts.

### Notes: SSOT
- Backlog `_QUEUE/induced-backlog.jsonl`; outcome ledger `_STATE/receipt-outcomes.jsonl`; proposal in PR #1691.

### Notes: Routes
- Outcome verdicts: `python3 scripts/receipt_outcome_queue.py record`. Accountant: `python3 scripts/accountant_weekly.py --ingest`.

### Notes: Gates
- `python3 scripts/backlog_status_check.py --check`; `python3 scripts/decision_receipt_to_accountant.py --self-test`; merge with `gh pr merge --merge` only on Zach's yes.

### Notes: Corrections
- D0 first claimed the live decisions had no receipts; George and Vico do (false null, banked in PR #1691 section 4h).
- "Over 3,500 commits" was first called stale; it is the no-merge count and correct.

### Notes: Close protocol
- Record a decision receipt for every merge; mark backlog rows DONE only with evidence in status_note.

> Molted from `_HANDOFFS/fragments/20261020T142750Z--claude-shared-intention-proposal.md` (branch `claude/shared-intention-proposal`, head `7506fbde`); `_HANDOFFS/fragments/20261020T173031Z--claude-opus-jobs-framework-be7d0b.md` (branch `claude/opus-jobs-framework-be7d0b`, head `c062a6d2`).
