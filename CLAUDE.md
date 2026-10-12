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
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

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
  ROM primitives, token-saving rules) plus **only the latest 1–2 handoff sections**. Sessions no longer edit
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

# Handoff — v3.133.0 (2026-10-12)

> ### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-molt7-note), receipts in digest: 1.
> - **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 2 unconfirmed markers in the day's records.
> - **Breath balance**: mirror (inhale, no exhale).
> - **Sycophancy check**: agreement 27 / dissent 6 (ratio 3.86) → OK: dissent present.
> - **Cold re-read (canary on the draft f9.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> Attachment release: kept all claims. Somatic: not asked. Disposition: release.
>
> > Molted the last fragment into v3.131.0, carrying v3.129.0's open list forward so nothing dropped out of CLAUDE.md.
>
> > ### Shavasana — handoff pause, 2026-10-12 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
> > 
> > - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/plane-landing-prl-resins-dac4ef), receipts in digest: no digest file.
> > - **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 1 unconfirmed markers in the day's records.
> > - **Breath balance**: breathing (both directions).
> > - **Sycophancy check**: agreement 1 / dissent 1 (ratio 0.5) → OK: dissent present.
> > - **Cold re-read (canary on the draft draft.md)**: GROUNDED; no ground return: none; thin air: none.
> > - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> > - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> > - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
> > 
> > _This block asserts nothing new. Counts, paths, and questions only._
>
> Attachment release: kept all claims; step 8 publish state held as unconfirmed. Somatic: not asked. Disposition: release.
>
> > PRL Phase 1.2 call with Todd (Mon 2026-10-12 10:00 ET): production prerequisites partly done live, go-live moved to a Part 2 call gated on four pre-call items.

## Goal / true north
Close PRL go-live via a Part 2 call, and submit the monday.com take-home by Thu 2026-10-15 17:00 ET.

## What changed
- PRL Phase 1.2 call held Mon 2026-10-12 10:00 ET; go-live moved to a Part 2 call gated on four pre-call items (details in the PRL fragment).
- Receipt `2026-10-12--prl-sandbox-roger-repair--ZH` logged for the Roger sandbox write; post-write values not re-read.
- Take-home rubric aligned to the FDE LAB INTRO briefing video: `flight/rubrics.json` gained reasoning_legible and ambiguity_structured, alternatives raised to 3 (take-home repo commit 08ce4a4, reported by that session). ZIP-contents gate already enforced by the take-home packager (E8).
- Relayed to the take-home session: rehearsal question in DEMO.md, HARDENING.md ("What we tried to break") surfacing snapshots/KINTSUGI/RCA work, then cut and grade rc15. Not yet confirmed done.

## Current state
- Zap 376827315 draft with the step 8 fix exists; whether it is published is unconfirmed (Comet canvas did not render for Claude in Chrome).
- The only Zapier Sugar connection ("zapier.chatbot #2") points at prlresinstest.
- Todd could not open the chatbot mailbox in Outlook, so the chatbot password is not set.

## Decisions made
- When a molt pushes a block to the archive, carry its open items into the new block.
- Production Zap is a duplicate of 376827315, not an edit of it.
- Todd types the chatbot password into Zapier himself; the password is never emailed.

## Open decisions (waiting on Zach)
1. Zach: confirm step 8 is published (Lead = 5. ID, four fields removed) before Todd's test chat.
2. Zach: downgrade the chatbot Sugar user from System Admin to a Leads-only role after go-live.
3. Zach: take-home rehearsal #1, CONSTRAINTS.md E4 to E7, the upload click, and the 17-item judgment list from the "Design gauntlet and heuristic review" session; submit by Thu 2026-10-15 17:00 ET.
4. Zach (carried from v3.131.0): Actions spending limit, then drop the gh `user` scope; approve the held dependency watch prompts and the better-sqlite3 bump (#557).

## Open (other)
1. Take-home: confirm HARDENING.md, DEMO.md line, rc15 cut and grade landed.
2. PRL pre-call items: Todd sets the chatbot password as Sugar admin; Bill sends the Tidio forwarding address; Jorge does the Outlook web check, Barracuda allow-list and quarantine release; Todd runs one test chat. Confirm where the test Tidio widget lives.
3. After Todd's test chat: verify in sandbox the matched lead changed and Roger date_modified stays 2026-10-12T10:39:39-04:00 (closes the unconfirmed items on receipt 2026-10-12--prl-sandbox-roger-repair--ZH).
4. Carried from v3.131.0: measure fe-smoke minutes and confirm the nightly a11y run, then decide on #1046; check the arcs.care/hud loader as admin; on or after 2026-10-13 run `python3 scripts/backlog_status_check.py --gh`; ADR-078 lacks a `_DECISIONS/index.json` row; the Oct-06 Success Academy check-in to Brian is unconfirmed; after submission, atlas-bundle.v1 export and the admin route; Vico intro Wed 2026-10-14 13:00 ET.

## Next action
Confirm Zap 376827315 step 8 is published before Todd's test chat; book PRL Part 2 when the four replies land.

## Cold-start recipe
- _ARTIFACTS/prl-1-2-close-loop/2026-10-09-go-live-blockers.md; https://prl.arcs.care/go-live; Granola meeting ee74074f-4a34-46a8-8862-2201b6e92be1; Gmail thread "Chatbot go-live: 4 things I need before Part 2".

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261011T025700Z--claude-handoff-molt7-note.md` (branch `claude/handoff-molt7-note`, head `72c88b00`); `_HANDOFFS/fragments/20261012T151031Z--claude-plane-landing-prl-resins-dac4ef.md` (branch `claude/plane-landing-prl-resins-dac4ef`, head `e18c60d6`).

# Handoff — v3.132.0 (2026-10-11)

> ### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-loops-verify-1010), receipts in digest: 1.
> - **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 2 unconfirmed markers in the day's records.
> - **Breath balance**: mirror (inhale, no exhale).
> - **Sycophancy check**: agreement 29 / dissent 6 (ratio 4.14) → THIN: high agreement, little dissent.
> - **Cold re-read (canary on the draft frag3.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read**: somatic: not asked.
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> > Pickup plus /loops follow-through: K34 found already closed, the three "waiting on your go" PRs found already merged by their own sessions, and the open items in two of their receipts verified live.
>
> > Closes the loop on fragment 20261011T024242Z--claude-handoff-prl-takehome: #1267 merged and live, and the take-home session's status reply arrived.
>
> ### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-prl-merged), receipts in digest: 1.
> - **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 2 unconfirmed markers in the day's records.
> - **Breath balance**: mirror (inhale, no exhale).
> - **Sycophancy check**: agreement 29 / dissent 6 (ratio 4.14) → THIN: high agreement, little dissent.
> - **Cold re-read (canary on the draft frag4.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> Attachment release: every claim kept; take-home figures are the other session's report, labelled as relayed. Somatic: not asked. Disposition: release.

## Goal / true north
Keep merged work verified live and receipted before the Mon 2026-10-12 PRL go-live call.

## What changed
- Receipt 2026-10-10--warroom-greys-pr1257-postmerge-verify--ZH: #1257 smoke and fe-smoke passed, main CI run 38104666811 succeeded, production `be3ff8f0` contains merge `bac52ae7`.
- Receipt 2026-10-10--louisville-touch-targets-pr1251-postmerge-verify--ZH: live louisville.arcs.care screenshotted at 360/790/1280; no horizontal overflow, controls 44px, bars 59px and balanced.
- #1258 (PRL agenda) was already merged with receipt 2026-10-10--prl-call-agenda-draft-pr1258--ZH; no duplicate logged.
- Main checkout's gitignored `_STATE/handoff-progress.md`: appended a correction that K34 is closed (KINTSUGI.md K34, DECISIONS.md D-K34; 0 leak matches on main and tags).
- #1267 merged (`c3dcfe03`, 2026-10-11T02:48Z); receipt 2026-10-10--prl-golive-step8-check-snapshot-pr1267--ZH. Live: prl.arcs.care/go-live shows "never a fixed record".
- #1272 merged (`ad0a8b36`); receipt 2026-10-10--handoff-fragment-prl-takehome-pr1272--ZH.

## Current state
- PRL: Zap 376827315 step 8 fix still an unpublished draft; skip-vs-clear of empty update fields untested; Todd has not seen the new checklist item.
- Take-home (reply from session "Continue monday take-home from HANDOFF.md", ~02:45Z, relayed to Zach): 21 of 24 in scope done; rc9 current (90d62d5, release_check exit 0, Claude eval 18/18), ZIP 6.00 of 10 MB; ready for rehearsal #1 per ONBOARDING.md (mock e2e and mock ask first, then doctor, sync, poll). Its in-progress logs were committed in b7d6d63 (take-home repo). Light gauntlet: 5 findings, 4 fixed, slide 6 overstatement partly fixed.

## Decisions made
- Do not touch ~/ret-rfp-intelligence from outside the take-home session.
- Follow-up receipts confirm a prior receipt's open items instead of editing the prior row.
- None new.

## Open decisions (waiting on Zach)
1. Zach: edit and send the PRL agenda draft before Mon 2026-10-12 10:00 ET.
2. Zach: rehearsal #1, CONSTRAINTS.md E4 to E7, the upload click, and a 17-item judgment list relayed by the "Design gauntlet and heuristic review" session.

## Open (other)
1. ~~The one-time "Le Woof: nudge about Hila's page" task is still enabled with a past fire time (Oct-08 09:00) and never ran.~~ Resolved 2026-10-10: Zach had the task disabled (not deleted); the Hila check itself never ran.
2. PRL Mon 2026-10-12 10:00 ET: test skip vs clear, publish the draft, repair Roger, run the repeat-chat proof.

## Next action
PRL go-live call with Todd, Mon 2026-10-12 10:00 ET.

## Cold-start recipe
- /handoff-pickup. PRL: _ARTIFACTS/prl-1-2-close-loop/2026-10-09-go-live-blockers.md and https://prl.arcs.care/go-live. Take-home: ONBOARDING.md in ~/ret-rfp-intelligence, `./rfp e2e --provider mock --runs 1`.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261011T024859Z--claude-handoff-loops-verify-1010.md` (branch `claude/handoff-loops-verify-1010`, head `c3dcfe03`); `_HANDOFFS/fragments/20261011T025250Z--claude-handoff-prl-merged.md` (branch `claude/handoff-prl-merged`, head `f32fad3b`).
