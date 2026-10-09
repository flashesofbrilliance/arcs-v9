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

# Handoff — v3.121.0 (2026-10-09)

## Goal / true north
Get the My Ally LD mutual NDA signed on fair, two-way terms without slowing the relationship; keep the counterpart surfaces honest and tested.

## What changed
- NDA review of "Mutual NDA — Access Consulting & Zach Harris 10.9.26" (counterparty Access Consulting, LLC, Leah's consultancy). Outliers flagged: AI-tools clause (4), auto-destroy at 60 days (8.1(c)), one-way sharing (3.1 vs 3.2), broad derivative-works ban (6.2); retroactive to Oct 8 (Recital E). Not legal advice.
- myally.arcs.care/mnda-edits live (PR #1127, `cbe69507`; receipt `2026-10-09--myally-mnda-edits-page-merge-pr1127--ZH`): six proposed edits (Recital B; 3.2; 6.2; new 6.4 ARCS/independent-methods carve-out; 8.1(c) 90 days; 8.3 version history) with toggleable Why notes and a clean copy. Generator `_ARTIFACTS/sow-scaffold-2026-10-08/build_nda_redlines.py` (source text `mnda-original.txt`).
- Checklist step 1 on the plan links to /mnda-edits (PR #1128, `31d82681`).
- Clean signable PDF generated to `~/Downloads/Mutual NDA (revised) - Access Consulting & Zach Harris 10.9.26.pdf` (7 pages, edits verified, signature blocks kept together).
- Zach SENT the reply to Chelsea (cc Kelly, Leah) with the revised PDF and the /mnda-edits link.
- MNDA chip in the plan and primer header next to the theme toggle: PR #1129 open, CI green except fe-smoke still running; Zach asked to merge when green.

## Current state
- Waiting on Access Consulting: Leah's signature on the revised NDA or counsel's counter-wording; Chelsea and Leah's plan feedback (1-2 days).
- Zach decided to keep the Oct 8 Granola transcript and treat it as NDA-covered once signed; recording disclosure not raised pre-signing (his call). Obligations recorded in memory `project_my_ally_ld_sow_scaffold`.

## Decisions made
- Edits framed as requests, not conditions; counsel's equivalent wording welcome.
- Redlines hosted on Zach's own passcode-gated domain rather than a third-party artifact, to avoid sharing their NDA terms with another service.
- Toast rejected in favour of a checklist link plus a header chip.

## Open decisions (waiting on Zach)
None.

## Open (other)
1. None.
2. Merge PR #1129 when fe-smoke is green; verify the chip live.
3. On signature: countersign, then point them to the intake form; Phase 0 starts from the spec.
4. Signature line still reads "Zach Harris, individually"; consider signing through an entity if manana is one.
5. Wed 2026-10-14: 1:00 PM Vico/Lyndon intro, then /recoil-close.

## Next action
Merge PR #1129 once CI is green, then wait for the signed NDA.

## Cold-start recipe
- Rebuild NDA page: `python3 _ARTIFACTS/sow-scaffold-2026-10-08/build_nda_redlines.py` (after build_proposal_view.py).
- Live check: POST passcode to `/api/myally/unlock`, curl `/mnda-edits` with the cookie.

### Notes: Lessons
- An NDA that is retroactive pulls existing recordings and AI-processed notes inside it; check your tooling against its AI and destruction clauses before signing, not after.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261009T200639Z--claude-fervent-napier-9c6c13.md` (branch `claude/fervent-napier-9c6c13`, head `31d82681`).

# Handoff — v3.120.0 (2026-10-09)

> > PRL go-live blocker re-confirmed in the sandbox: the Sep 17 "dead" lead was the empty-email guard overwriting Roger Lamarre again. Monday's call now opens with the fix.

## Goal / true north
Close out 2026-10-09 evening: My Ally LD reply received, Vico intro prepped, day's design work landed, digest corrected.

## What changed
- PR 1115 (merged): `_ARTIFACTS/prl-1-2-close-loop/2026-10-09-go-live-blockers.md` (findings, technical fixes, admin creates by owner, business blockers); backlog item `prl-golive-empty-email-guard` (OPEN).
- Receipt: 2026-10-09--prl-go-live-blockers-note-pr1115--ZH.
- My Ally LD: Chelsea replied 2026-10-09 15:06 ET (cc Leah, Kelly, chelsea@myallygps.com), thread `1a121bb189899df1`: plan is "thoughtful and really easy to follow"; she and Leah take a day or two to review and send feedback to shape the proposal; attached "Mutual NDA — Access Consulting & Zach Harris 10.9.26.pdf" (mutual, as asked). Counterparty is Access Consulting (Leah's consultancy), which answers part of the SOW question of whose paper and which entity.
- PR #1101 merged (`d9c31a7a`): retired greys, design-debt ratchet, plus stacked #1102, #1103, #1105 now on main. Receipt `2026-10-09--design-retired-greys-ratchet-merge-pr1101--ZH`.
- Night-moves 2026-10-09 digest landed and corrected (PRs #1119, #1120, #1121, #1122); integrity gate verdict OK.
- Counterpart pulse run: Vico intro call found in inbox ahead of memory; Kam (Aug 17) and Fun.xyz (Sep 24) quiet, left open.
- Vico/Lyndon pre-call refresh (PR #1124, `710f74b0`): call Wed 2026-10-14 1:00 PM ET on Teams; ex-ante prediction unchanged from 2026-10-03, window and intel refreshed. Zach verified the live war room (app.arcs.care/warroom/lyndon-war, admin sign-in plus the SSOT gate value).

## Current state
- My Ally LD: NDA in hand, unsigned; feedback from Chelsea and Leah expected in a day or two.
- Vico: prepped; call Wed 10-14 1pm.

## Decisions made
- Zach does no weekend work. Guard fix, Roger repair and no-email proof happen ON the Mon call as item 1; prod switch waits until the no-email chat CREATES.
- Kam and Fun.xyz left open, not marked stalled.

## Open decisions (waiting on Zach)
None.

## Open (other)
1. Review and sign the Access Consulting mutual NDA (counsel if unsure; not legal advice here).
2. After the NDA is signed: intake form and build spec, then Phase 0; written proposal waits for Chelsea and Leah's feedback.
3. Wed 2026-10-14: 9:30 My Ally check-in reminder (may be moot after their reply); 1:00 Vico intro; run /recoil-close right after.
4. The war-room page's built-in password gate is client-side only (value readable in page source); the real lock is the admin route.

## Next action
Review the Access Consulting NDA; when signed, return it and point them to the intake form.

## Cold-start recipe
- My Ally thread: Gmail `1a121bb189899df1`. Vico SSOT: `runtime/recoil/generated/2026-10-03-oh-vico.json`; render with `./scripts/recoil --data <ssot> --audience internal --format html`.

### Notes: Lessons
- Check the inbox before writing a handoff that names a counterpart's state; the reply came from Chelsea, not the founder, and carried the NDA.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261009T181804Z--claude-prl-handoff-memory-check-6c5e92-c.md` (branch `claude/prl-handoff-oct9-c`, head `3859829d`); `_HANDOFFS/fragments/20261009T192058Z--claude-fervent-napier-9c6c13.md` (branch `claude/fervent-napier-9c6c13`, head `710f74b0`).
