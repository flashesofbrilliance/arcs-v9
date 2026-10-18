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

# Handoff — v3.135.0 (2026-10-13)

> ### Shavasana — handoff pause, 2026-10-13 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-decision-geometry), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 2 dissent markers, 1 unconfirmed markers in the day's records.
> - **Breath balance**: mirror (inhale, no exhale).
> - **Sycophancy check**: agreement 3 / dissent 3 (ratio 0.75) → OK: dissent present.
> - **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> Attachment release: every claim kept; each cites a PR, commit, receipt id or URL. Somatic: not asked. Disposition: release.
>
> > Built the 5x5 decision geometry explorer over the RET take-home DECISIONS.md, merged it on local gates during the Actions billing block, logged its receipt, fixed the Supabase CLI, and published a private artifact link.
>
> > RET take-home session (2026-10-10 to 2026-10-13): built and hardened Zach's monday.com FDE take-home in the separate
> > repo ret-rfp-intelligence (rc23 to rc35), rehearsed the panel in four rounds, and handed the navigation redesign to a
> > fresh session. Work product lives in that repo; this fragment banks the internal notes in _STATE.
>
> ### Shavasana — handoff pause, 2026-10-13 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/ret-takehome-handoff), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
> - **Breath balance**: breathing (both directions).
> - **Sycophancy check**: agreement 1 / dissent 0 (ratio 1.0) → OK: dissent present.
> - **Cold re-read (canary on the draft fragment.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
> - Attachment release: every claim in Changed and State was re-checked this session against git tags, the release log and the live run; none downgraded.
> - Somatic: not asked.
> - Disposition: release.

## Goal / true north
Submit the take-home Thursday 2026-10-15 morning: one ZIP under 10,000,000 bytes with source/, exactly one presentation
PDF, and README.md, that a cold reviewer can run and navigate.

## What changed
- #1294 merged with --merge (`5f3d0b17`): `scripts/decision_geometry_ret.py` (stdlib), `scripts/templates/decision-geometry.template.html`, `_ARTIFACTS/decision-geometry/{ret-decisions.json,decision-geometry.html}`. 23 decisions scored; codes 22211 (6), 21211 (6), 11211 (5), 11111 (5), 22111 (1).
- Receipt 2026-10-12--decision-geometry-explorer-pr1294--ZH logged; read back via plain Supabase MCP (project URL xbbpiryokswwvcrcutge) and via `supabase db query --linked`.
- Supabase CLI: 2.101.0 binary had an invalid code signature (exit 137 on every call); clean uninstall plus fresh install gave 2.118.0, codesign passes. Memory `supabase-mcp-wrong-org-use-cli` amended.
- Private artifact published: https://claude.ai/artifact/QFNkJMHFvG2sVdKrdUQh2R (snapshot of the page; republish after regenerating).
- #1298 (this fragment's PR); receipt 2026-10-13--ret-takehome-handoff-pr1298--ZH
- ret-rfp-intelligence main 175afe2 (pushed), release candidate rc35 (tag rc35-2026-10-13, 3.36 MB, release check exit 0,
   live end-to-end run from the ZIP passed). Not an arcs-v9 PR; that repo is the deliverable.
- Size gate fixed: rc25 to rc33 exceeded 10 MB on the decimal reading (K67); history.bundle replaced by HISTORY.txt (D-HISTORY).
- Hardening found in rehearsal: K60 (bench from ZIP), K61 (runaway pollers; one poller per computer), K62 (borderline
   eval, temperature 0 reverted), K63 to K66 (file viewer, evidence loop, column ids, poller write order), K67 (size).
- Mistake link table with a build gate (60 of 67 guarded, 7 process lessons); wiki, controls map, FAQ, cases.
- Internal notes added under _STATE (panel audit, question tree, lightning FAQ, enterprise test plan, design handoff).

## Current state
- rc35 is the latest verified release; main 175afe2 carries the newer page work (five-card start page, page bar,
  verdict-first pages, light/dark, deck opens in present mode on laptops).
- A design-gauntlet session is offered as a task chip; its handoff is the 2026-10-13 RET design-gauntlet handoff note (untracked, in the main checkout state folder).
- The explainer session is holding the video re-render until the design pass ends.

## Decisions made
- Zach: merge #1294 on local gates (wrap-lint, token_source_gate, page_gate --matrix full, kintsugi design-debt 0).
- Zach: publish a private artifact link despite unconfirmed take-home publishing terms.
- Ship HISTORY.txt instead of the git bundle: the bundle was 8.7 of 10.4 MB; cited hashes stay findable.
- Submit from the free monday.com plan the brief prescribes; enterprise access is tested in a copy only.
- Deck first, then How we got here; proof, mistakes and build log become Evidence one level down.
- Zach's packaging model (presentation/ = deck, source/ = code and documentation, README = front door) goes to the
   design session, with a show-the-tree-first gate before any file move.

## Open decisions (waiting on Zach)
1. Zach: the 11 canon choices in the #1294 PR body (text adaptation of level rules, L4 bar, L5 unreachable, A-E grades as C2, H rung keywords, drill pairing, 3125 layout, W2 tokens, unstructured records, page placement, draft spec status).
2. Zach: Actions spending limit (Settings > Billing).
3. Zach: create view-only share links for the four RET boards, then wire them in.

## Open (other)
1. Design gauntlet session: packaging model, one navigation system, link every provenance file, OTel answer.
2. Explainer videos re-render from the final head; then cut rc36 and run the live test from its ZIP.

## Next action
Start the "Run the RET design gauntlet" task chip.

## Cold-start recipe
Read the 2026-10-13 RET design-gauntlet handoff note (untracked, in the main checkout state folder); repo /Users/zharris/ret-rfp-intelligence; `cd source && ./rfp serve`
then http://127.0.0.1:8765/presentation/index.html; `./rfp status`; releases via `./scripts/release_check.sh` (detached,
read dist/release_check_exit). Debt tracker: https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm (debt collection).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261013T161607Z--claude-handoff-decision-geometry.md` (branch `claude/handoff-decision-geometry`, head `b1f0080d`); `_HANDOFFS/fragments/20261013T165149Z--claude-ret-takehome-handoff.md` (branch `claude/ret-takehome-handoff`, head `e83abaed`).

# Handoff — v3.134.0 (2026-10-13)

> 2026-10-12: the take-home design gauntlet and explainer session closed. Every finding was relayed to the take-home session and verified there; rc25 is the submission and the three phone items were skipped by Zach.

## Goal / true north
Ship the monday.com take-home by Thu 2026-10-15 17:00 ET with every claim traceable to its log.

## What changed
- #1295 merged (`1a7db6da`): handoff fragment for the design gauntlet and explainer session. Receipt `2026-10-12--handoff-design-gauntlet-pr1295--ZH`.

## Current state
- Take-home submission is rc25 (ZIP = source/ + presentation/ only); final videos are in ~/ret-rfp-intelligence/dist/videos/ (rendered from rc24), old explainers moved to dist/videos/superseded/.
- Zach skipped three phone items for submission: present-mode tap targets (3-7 px letters), the landscape-preferred overlay, the phone bottom bar.
- Watchers and the port-8766 copy server are stopped.

## Decisions made
- Run every check read-only against a copy of the take-home repo (port 8766) because bench runs append to its flightlog and that session is the single writer.
- Correct own errors in a new message rather than silently: the "about 3 s" flag was retracted after the e2e log showed a 3.2 s median; the v8 staleness flags were withdrawn once dist held v4.

## Open decisions (waiting on Zach)
1. Zach: a real-iPhone tap check of the grade tooltips (verified only under Chromium touch emulation).

## Open (other)
1. After submission: the three skipped phone items, and K-numbers still visible in the Beliefs and Evals tabs.

## Next action
Zach submits rc25 by Thu 2026-10-15 17:00 ET.

## Cold-start recipe
- /handoff-pickup; `git -C ~/ret-rfp-intelligence log --oneline -5`; videos listed in ~/ret-rfp-intelligence/dist/videos/MANIFEST.md.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261013T004500Z--claude-design-gauntlet-heuristic-bf77a6.md
> Design gauntlet and Ahmed-heuristic review of the monday take-home (127.0.0.1:8765, repo ~/ret-rfp-intelligence), read-only, relaying every finding to the take-home session as single writer; plus the explainer video v1 to v7.1, then handed the cards rig to the explainer session.

### Notes: Cold
- /handoff-pickup; `git -C ~/ret-rfp-intelligence log --oneline -5`; videos in ~/ret-rfp-intelligence/dist/videos/MANIFEST.md.

### Lessons
- Verify a subagent's NOT FOUND against the repo's evidence index before relaying it (the e2e log held the "3 s" figure).
- A video that quotes the deck drifts whenever the deck changes; generate its text from the deck's own data ids.

### Notes: Shavasana

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/design-gauntlet-heuristic-bf77a6), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 3 / dissent 0 (ratio 3.0) → OK: dissent present.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Attachment release: kept all claims; each Changed sha was read in git log on ~/ret-rfp-intelligence this session. Somatic: not asked. Disposition: release.

> Molted from `_HANDOFFS/fragments/20261013T004500Z--claude-design-gauntlet-heuristic-bf77a6.md` (branch `claude/design-gauntlet-heuristic-bf77a6`, head `5f3d0b17`).
