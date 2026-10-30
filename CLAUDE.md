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

# Handoff — v3.142.0 (2026-10-28)

> > Monday FDE arc (2026-10-20 to 2026-10-27): handoff provenance bench, walkthrough prep, the 2026-10-26 panel walkthrough and recoil close, and the follow-up guide at monday.arcs.care (nav click events, rc46 ZIP hosted behind the gate).

## Goal / true north
Win the monday.com FDE walkthrough on Mon 2026-10-26 (2:30-3:30 PM ET) and move to an offer by early November, starting mid-November or sooner.

## What changed
- #1629 merged with --merge (`3d144a22`): raw results of the single run (all but H8) and `_PATTERNS/2026-10-18-provenance-retrieval-results.md`. Receipt 2026-10-18--provenance-bench-results-pr1629--ZH.
- #1745 merged with --merge (`517ae98a`): the H8 run, `h8.json`, a one-line `load_librarian` fix, report addendum. Receipt 2026-10-20--provenance-bench-h8-pr1745--ZH.
- #1588 merged with --merge (`d39c9ec2`): Operator 21 Librarian posting-list lineage index. Receipt 2026-10-20--librarian-lineage-index-pr1588--ZH.
- PR #1791 merged (ae652139): the intention in _STATE/intentions.jsonl, five domino rows, PANEL-BRIEF.md. Receipt 2026-10-22--monday-offer-intention-pr1791--ZH.
- PR #1792 open: reviewer leave-behind added to the monday-walkthrough-2026-10-26 row (one-line diff).
- Graded demo boards (account assessment-lab-assignment): board descriptions and a Call ID column tooltip were added, each labelled "added Oct 22, after submission". No item was changed.
- Enterprise backlog board created: https://zachharriss-team.monday.com/boards/18436626672 (12 gap items, each with a talking point).
- monday.arcs.care live, passcode-gated (MONDAY_PASSCODE). Guide order: the case, Not proven yet, Live (video, 720p note), Code, Evidence, Agent. PRs #1817 (58fcc978), #1818 (37aa6ac0), #1819 (7cc11948); receipts 2026-10-26--monday-guide-{host-pr1817,polish-pr1818,nav-labels-pr1819}--ZH.
- Panel video re-cut (2:18, "On the running build"), unlisted at https://youtu.be/uUjJlXOusNw; thumbnail in ~/ret-rfp-explainer-rig/out-dry/.
- Recoil close updated: open by default, liability posture under-credited, guardrail ask met at Kamran's scope. Odds about 0.65 to 0.68 (judgment). File _ARTIFACTS/forge-monday-fde/walkthrough/2026-10-26-recoil-close.md is UNTRACKED on this branch.
- Email to Sam: written and sent by Zach, around 6:15 PM ET 2026-10-26.
- PR 1825 merged (head 0866ac1a, merge 445a46b8): public/monday-guide.html fires a Vercel custom event `nav_click` {label, href} on nav link clicks. Live behind the passcode (verified with an unlock cookie).
- Merged over a fe-smoke check stuck pending with 0s run time (Actions limit), on Zach's explicit "merge it anyway". Receipt 2026-10-27--monday-guide-nav-events-pr1825--ZH records that.
- Trap order T1, T2, T5, T3, T4 kept as submitted (golden.json order), per Zach.

## Current state
- Vercel analytics query API returns 404 "Web Analytics not found" for arcs-v9 (by name and by ids); /_vercel/insights/script.js serves 200. Custom events need the Pro plan; unconfirmed whether nav_click records.
- Mixmax shows bulk opens and clicks at 5:20pm and 5:40pm from Virginia: read as Safe Links style scanners, not reader interest.

## Decisions made
- Zach: merge on Vercel-only checks; merge 1588 only after H8 passed.
- Run H8 only once the machine was quiet; it took four waits and one fresh worktree. Not run under load 15 or higher.
- Zach: the deck follows the brief's sections 1.1-1.5; the spoken frame is the video's six beats. No net-new frameworks.
- Zach: the timeline follows Sam's agenda with a buffer: hellos 0-2, slides 2-12, demo and code 12-27, their questions 27-45, buffer 45-50, his questions 50-60.
- Zach: the code review is comments-first (file, rule, test, gap). The table-stakes items are named out loud. Production hardening: give his own lean first, then take it to internal peer review.
- Zach: after the freeze, no more changes to the graded boards.
- Zach: keep trap order as submitted; merge PR 1825 over the pending check.

## Open decisions (waiting on Zach)
1. Zach: the tower's decision queue (HUD rulings A1, compass anti-distillation A2, ADR-085 A3, stale backlog fates A4, and the one-way doors) in `_PROPOSALS/2026-10-19-tower-decision-queue.md` on the tower's branch.
2. Zach: run the live e2e, then the launcher, the tooltip check and the eval (Apple Note list).
3. Zach: say the six beats out loud with a timer, recorded on his phone.
4. Zach: set the old Cheat Sheet artifact to private; unpin the old Comet tabs.
5. Zach: merge PR #1792.
6. Zach: check Vercel dashboard (arcs-v9, Analytics, Events) for nav_click; it is the only human-only signal on the guide.

## Open (other)
1. Commit the skeptic's re-score script so the check can be rerun (currently scratch only).
2. universe-atlas-tokens row still OPEN; the canon atlas HTML stays uncommitted (token_source_gate).
3. The skill-building session (local_7315d7c8) is waiting on Zach's now-or-after-Monday answer.
4. rc46 Start page row 05 (Package your final submission) does not point to proof-of-one-answer.html as the "what done looks like" reference. Proposed fix: one cell, plus a mirror line on monday.arcs.care. Waiting on Zach's go (rc46 is already submitted).
5. Ex-ante receipt for the leadership call (row monday-leadership-call); Wednesday 10-28 prep (Elevate, seeing Sam).
6. Optional: stack the 4-column guide tables on mobile.
7. Optional: relabel the guide's one-answer bullet to "What one finished answer looks like (traced):".

## Next action
Wait for a reply from Sam or the panel; read nav_click in the Vercel dashboard (arcs-v9, Analytics, Events).

## Cold-start recipe
- Read _ARTIFACTS/forge-monday-fde/walkthrough/2026-10-26-recoil-close.md and memory project_monday_fde_strategic_deployments.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261020T181720Z--claude-handoff-provenance-bench.md
> Ran the pre-registered provenance-retrieval benchmark once, published every result including the failures, and merged the one change that passed (the Librarian lineage index).

### Notes: lead of 20261022T194426Z--claude-monday-interview-prep.md
### Shavasana — handoff pause, 2026-10-22 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/monday-prep-handoff), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 1 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 2 / dissent 1 (ratio 1.0) → OK: dissent present.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

- Attachment release: every claim cites a PR, board id, path or file; kept. Somatic: not asked. Disposition: release.

### Notes: lead of 20261027T131837Z--claude-monday-prep-handoff.md
> monday FDE post-call session (2026-10-26 to 10-27): panel follow-up shipped; Zach sent it to Sam.

### Notes: lead of 20261028T001502Z--claude-monday-prep-handoff.md
> Monday guide follow-up session (2026-10-27, part 2): nav click tracking shipped on the guide; analytics and email-open signals read.

### Notes: Lessons
- Read the whole organizer thread and the archive before planning; the first agenda was wrong.
- Mirror what reviewers already saw; repeated restructuring after a freeze is soothing, not preparing.
- Verify every sheet claim against the code. Caught today: "answered with a source", "3 seconds", a contradictory "No" on the real RFP, and an agenda that summed past 60 minutes.
- Reuse the project's own artifacts (README gap list, golden.json, DECISIONS.md, KINTSUGI, catalog.json) rather than rebuilding them.

> Molted from `_HANDOFFS/fragments/20261020T181720Z--claude-handoff-provenance-bench.md` (branch `claude/handoff-provenance-bench`, head `eb749100`); `_HANDOFFS/fragments/20261022T194426Z--claude-monday-interview-prep.md` (branch `claude/monday-interview-prep`, head `ae652139`); `_HANDOFFS/fragments/20261027T131837Z--claude-monday-prep-handoff.md` (branch `claude/monday-prep-handoff`, head `185ba01e`); `_HANDOFFS/fragments/20261028T001502Z--claude-monday-prep-handoff.md` (branch `claude/monday-prep-handoff`, head `874f14e4`).
