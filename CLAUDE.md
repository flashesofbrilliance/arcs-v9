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

# Handoff — v3.146.0 (2026-11-12)

> One arc across five sessions: the recoil call service's wave 1 closed (R1 to R11 merged), wave 2 was induced, and the first real model run (Gasmi, J1 to J4) passed its pre-set bar except the cold-reader check. Fragment items written before later merges are superseded by the State and Open below; the What changed list keeps them raw.

## Goal / true north
The recoil call service, wave 2: ground truth on real calls (real model run, Brian acceptance), reuse the shipped player and induction tools instead of rebuilding them, and end the backlog-file conflict class.

## What changed
- Draft index runtime/specs/backlog-index.json (17 clusters over 310 active rows, 9 bundles, 15-row ruin watch list) and page _PROPOSALS/rendered/2026-11-12-backlog-index.html, both uncommitted on claude/backlog-groom-panel-3f737b.
- Panel binding: Librarian Op 21 and Folksonomist Op 20 and Accountant Op 19 BOUND but none reads backlog rows (no row adapter; Op 21 recommend returns only ADR-086 for backlog queries). Auditor Op 28 UNBUILT, UNBOUND. Sage UNBOUND (SAGE is a pipeline archetype; op25-sage-naming-ruling is open). Scholar UNBOUND (nothing by that name). Sentry = scripts/sentries.py, assumed reading of "sentury". Skeptic, Alchemist, brand-line-producer, impeccable BOUND.
- Skeptic found 6 false claims in the draft, all corrected; 1 objection rejected with evidence. Alchemist wrote 17 falsifiable claims; 4 polarity readings changed. Accountant, Sentry, Librarian, Folksonomist objections held open.
- #2166 merged as 101eeb1c (by the sweep session local_393c66c5 on Zach's "lets merge those"; receipt filed by that session, id not checked here): `scripts/recoil_stage_j4.py` (J4 as a stage plugin), `scripts/recoil_hypercube_explorer.py` generating `_ARTIFACTS/recoil-hypercube-explorer.html` (kit blocks, template recoil-skim; 2D slice plus filled-cell list; empty data renders grain n=0), and a `PLUGINS` list in `scripts/recoil_service.py`. Rows recoil-decompose-verbs and forecast-base-rates set DONE; recoil-hypercube-index DONE on main.
- #2177 open, head b0772883, not merged: J4 operator becomes a judged axis. The ruling-to-operator table (GROUNDED LAB, INFERENCE KKL, STRUCK FUNHOUSE) is dropped; operator glosses are bound to the periodic table and registry (LAB op 17 Detective, COURT op 18 Immune, KKL Kai force; BAR and FUNHOUSE from ADR-060 section 4) with a drift self-test. J4 version 1 to 2. Zach's go relayed from local_dfd22ff0: "go ahead". Handed to the recoil orchestrator local_6d106b64 to merge.
- Child session local_61d373e9 "Gasmi twin page: match the war-room look" is running, no PR yet: make `public/recoil-ext/2026-10-29-gasmi.html` (counterpart-safe twin, redirect added by PR 2168 ad288444) look like the war-room page Zach sent Doug on 2026-11-11. It confirms the target with Zach by screenshot first; no merge or deploy without his go.
- #2180 open, not merged: `scripts/recoil_brief.py` gains layout "stack" (header card, then numbered sections in one scroll, CSS scoped under .stack, main landmark); the Gasmi SSOT sets it through `meta.external_sets` (`page.layout=stack`); twin regenerated with `scripts/recoil_ext_build.sh`. One hood line reworded ("tab" to "Sections 2 to 5 are the method..."). No receipt yet (nothing merged).
- Screenshots for the PR live on side branch `pr-assets/gasmi-twin-warroom-look` (not for merge).
- PR 2170 merged (adb4f8d4): recoil sweep, backlog true-up, spec §9, molt v3.145.0; receipt 2026-11-12--recoil-sweep-molt-v3145-pr2170--ZH.
- PR 2175 merged (c1e9fc0f): R6 recoil print target, light print palette, folds open; receipt 2026-11-12--recoil-print-target-pr2175--ZH. Merged here on Zach's "go ahead", after PR 2173.
- PR 2173 (R11 HUD flight) merged at 16fa869c by the recoil orchestrator session on Zach's direct go there; its receipt and row are that session's.
- Backlog row recoil-print-target set DONE in this fragment's PR.
- PR 2172 merged (28eff75b): wave-2 backlog induction (epic recoil-call-service-wave2, 7 rows) and spec §10; receipt 2026-11-12--recoil-wave2-backlog-pr2172--ZH.
- PR 2173 merged (16fa869c): R11 HUD atlas v2 flight; receipt 2026-11-12--hud-atlas-v2-flight-pr2173--ZH (Zach, "Yes, merge 2173").
- PR 2179 merged (485a304d): first real model run on Gasmi recorded in spec §10.4, hud-atlas-v2-flight DONE; receipt 2026-11-12--recoil-first-real-run-pr2179--ZH.
- PR 2177 merged (402847e6): R8 J4 judged operator axis; receipt 2026-11-12--recoil-j4-operator-judged-pr2177--ZH (Zach, "Yes, both").
- Real run, Zach's "go ahead" on the spend: J1 to J4 PASS on Gasmi, 9 cells of 3,125, 0 invented, rerun UNCHANGED; J4 v2 rerun after 2177, also 9 cells, operators now judged (COURT appears).
- Spec §8 answered: Q1 360 orbit plus time scrub (reported by R11), Q2 light for print (reported by R6), Q3 same component set with audience filter plus a per-artifact light or dark default, Q5 keep on the private Brian page UBr7UHAo, the link-shared page RUNuc7zk has no email.

## Current state
- Epic recoil-call-service: R1 to R11 DONE on main (2175 at c1e9fc0f, 2173 at 16fa869c, 2177 at 402847e6). R12 recoil-brian-acceptance stays HOLDING by design: wave 2 added recoil-real-model-run and recoil-kairos-7s-test as its dependencies.
- Wave 2 READY: recoil-epic-tool-catalog, backlog-merge-driver-by-id, recoil-brian-ssot, recoil-hardstop-amend, recoil-runner-beats. uikit-recoil-player (PR 1826, 9cfc8c3f) and recoil-backlog-induction-tool-snap (recoil_induce.py, 9779524d) set DONE on Zach's "Yes, do both".
- Spec §8: all five answered (Q1 360 orbit plus time scrub; Q2 light for print; Q3 same component set, audience filter, per-artifact light or dark default; Q4 item by item, see spec; Q5 keep on private UBr7UHAo, the shared RUNuc7zk has no email).
- Recoil queue: only PR 2180 (Gasmi twin page) open; counterpart-facing.

## Decisions made
- Zach: drop the ruling-to-operator mapping (operator is judgment).
- Zach: target is the 11-11 war-room look, not today's fold layout; drop the Y, NCI, topology and req-reality chips on the external page.
- One merge queue: the recoil-wave2 session merges recoil PRs; the merge-train lane keeps non-recoil PRs. Merges only on Zach's word in the merging session; peer relays are not approval.
- recoil-real-model-run re-pointed from Brian to Gasmi (Gasmi's SSOT is on main).
- Loki: GitHub ignores local merge drivers, so the backlog driver removes the hand resolution, not the CONFLICTING round trip; union merge stays rejected.

## Open decisions (waiting on Zach)
1. Zach: merge PR 2180 (deploys the page Doug can open; run the PII and gauntlet check first; it changes the Gasmi SSOT the real run used).
2. Zach: confirm spec §8 Q4 item 3 reading (paid call past the budget: no change).
3. Zach: the cold-reader check on 3 sampled Gasmi J4 cells.
4. Zach: archive the idle recoil child sessions or keep them.
5. Zach: the groom's decision packet (18 proposed fates), "sentury" means Sentry, op25-sage-naming-ruling and the Scholar seat.
6. Zach: ideas not acted on: a standing merge policy for green two-way-door recoil PRs (conflicts with the approved merge hard stop unless amended), cruise control on a daily schedule, the scrum agent across both lanes.
7. Zach: move the main checkout (d4d064cc, behind origin/main, skills load stale) after a backup branch; then PR 2149.

## Open (other)
1. handoff-molt-guard blocks merge commits that bring a molt from main; skip when CLAUDE.md equals the merged parent.
2. backlog_status_check.py crashes on a date-only claimed_at.
3. Delete branch pr-assets/gasmi-twin-warroom-look after 2180 merges.
4. Unexplained one-line overwrite of _QUEUE/induced-backlog.jsonl in the recoil-wave2 worktree (restored from HEAD, nothing committed).

## Next action
Zach decides PR 2180; then start up to three wave-2 READY rows as session cards (recoil-epic-tool-catalog, backlog-merge-driver-by-id, recoil-runner-beats) within the 4-session cap.

## Cold-start recipe
- _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md §8 to §10.
- python3 scripts/backlog_graph.py --top 30; filter epic recoil-call-service-wave2.
- Real run: python3 scripts/recoil_service.py run --call runtime/recoil/generated/2026-10-29-gasmi.json --until J4 --budget-usd 1.00 (key from .env.local; spend needs Zach's go).
- Merge: scripts/safe_merge.sh <pr> <head>, one receipt per merge.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261112T155620Z--claude-backlog-groom-panel-3f737b.md
> backlog-groom-panel (branch claude/backlog-groom-panel-3f737b): clustered the global induced backlog with the named panel. Mid-flight: index and page drafted, not committed, no backlog row changed.

### Notes: lead of 20261112T160140Z--claude-handoff-r8-hypercube.md
# R8 recoil hypercube index (J4) and its follow-ups, 2026-11-12

### Notes: lead of 20261112T160943Z--claude-handoff-frag-gasmi-twin.md
# Gasmi counterpart twin matches the war-room look Doug's link showed, 2026-11-12

> Molted from `_HANDOFFS/fragments/20261112T155620Z--claude-backlog-groom-panel-3f737b.md` (branch `claude/backlog-groom-panel-3f737b`, head `ec9f1ea5`); `_HANDOFFS/fragments/20261112T160140Z--claude-handoff-r8-hypercube.md` (branch `claude/handoff-r8-hypercube`, head `f43a3f0d`); `_HANDOFFS/fragments/20261112T160943Z--claude-handoff-frag-gasmi-twin.md` (branch `claude/handoff-frag-gasmi-twin`, head `80e9827b`); `_HANDOFFS/fragments/20261112T161200Z--claude-recoil-sweep-molt-ee9c62.md` (branch `claude/recoil-sweep-molt-ee9c62`, head `737e810c`); `_HANDOFFS/fragments/20261112T161610Z--claude-recoil-wave2-f55f64.md` (branch `claude/recoil-wave2-f55f64`).
