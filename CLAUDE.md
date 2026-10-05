@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  `_STATE/handoff-progress.jsonl` every turn-with-change, and asks for a `## Delta` in
  `_STATE/handoff-progress.md` at each compaction. Both are gitignored. `/handoff` folds them
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
  ROM primitives, token-saving rules) plus **only the latest 1–2 handoff sections**. When a new handoff
  lands, move the oldest live one into `_ARCHIVE/handoffs.md`.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.82.0 (2026-10-05)

> **Stale worktree hooks fixed at the source; two PRs merged without CI during a GitHub Actions outage.**
> PR #760 (`6cb36019`, handoff v3.80.0) and PR #756 (`04622e99`, hooksPath repoint) merged on Zach's
> explicit "without CI". Receipts: `...-pr760--ZH`, `...-pr760-actions-stall-cause--ZH`,
> `2026-10-05--hookspath-repoint-pr756--ZH`, `...-pr756-manual-two--ZH`, `...-pr756-control-invalid--ZH`.

## Shipped + on main
- **#756 (chip task_bd140094, session archived):** the desktop app's `configureHooksPath` writes the main
  checkout's absolute `scripts/git-hooks` into each worktree's `config.worktree` on create and reopen, so
  worktrees ran the main checkout's stale pre-commit (the kintsugi 77 vs 95 phantom on #745).
  `scripts/hookspath_arm.sh` repoints to relative `scripts/git-hooks` (`--self-test` PASS, run locally
  before merge); `session-start.sh` calls it. 28 worktrees repointed by the chip; `cranky-chatelet-990429`
  and `reverent-edison-589194` repointed by hand.
- **#760:** handoff v3.80.0; conflict with v3.79.1 resolved (v3.79.1 archived).

## Open (next session)
1. **App-vs-SessionStart ordering untested.** `sweet-mayer-2ce4fb` was kept absolute as the control but is
   invalid: its branch predates #756, so its own `session-start.sh` has no repoint. Each worktree runs its
   own branch's hook, so the fix only works in worktrees containing `04622e99`. Test: start a fresh
   worktree session (or sync sweet-mayer to main and reopen), then `git config --show-origin core.hooksPath`.
   Pre-#756 worktrees the app rewrites stay on main-checkout hooks until they pick up main.
2. **GitHub Actions major outage** (githubstatus, 2026-10-05 ~20:17Z on; 37 runs queued, 0 running).
   #760 merged with 6 checks never run, #756 with 4. Re-check those runs after the incident resolves.
   Minutes quota not read (gh token lacks `user` scope).
   **Addendum (cool-bell session, same day):** the stalled jobs were ALSO billing. The `generated-views`
   check-run annotation on #756 read "not started because recent account payments have failed or your
   spending limit needs to be increased". Zach added a card + $10 Actions budget; all 9 #756 checks then
   ran and passed (after the 21:08Z merge). $10 is thin for ~6 jobs per push: check the budget first when
   runs sit queued with 0 in progress. Duplicate receipt `2026-10-05--worktree-hookspath-repoint-pr756--ZH`
   was filed before this session saw v3.82.0; the canonical one is `2026-10-05--hookspath-repoint-pr756--ZH`.
3. Carried from v3.80.0: desktop glow at >=1280px not screenshot-compared pre/post #745 (low).

## Lessons (in the record)
- A fix that lives in `.claude/hooks/` only reaches worktrees whose branch contains it: check
  `git merge-base --is-ancestor <fix> HEAD` in a control before reading its result as a test.
- "Merge without CI" on a code change: run the PR's own self-test locally first, and receipt the unrun checks.
- `archive_session` refused a linked child ("live work") from its running parent repeatedly, even with
  Remote Control off; the sidebar archive worked.
- Status pages before quota theories: `githubstatus.com/api/v2/components.json` answered in one call.

# Handoff — v3.81.0 (2026-10-05)

> **Job Factory: the Sept 2025 prototype read in full, a gauntleted spec, two slices merged, five open,
> and the morning loop found dead since 2026-09-11 and fixed.** Merged on Zach's explicit asks: #757
> (`1118a1ec`, slice 1 + seeds 5-16) and #754 (`602c7166`, slice 0). Receipts
> `2026-10-05--job-factory-slice1-culture-evidence-pr757--ZH`, `2026-10-05--lane-kanban-drag-drop-pr754--ZH`.

### Shavasana — handoff pause, 2026-10-05 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): script read 0 (it scoped to the fresh handoff branch). By hand, across 7 session branches: ~10 commits, 2 merges to main (#757, #754), 2 receipts, 5 open PRs (#761 #769 #771 #773 #775), 1 scheduled-task prompt rewritten, 1 hung run stopped.
- **Inhale** (what came in): 0 falsification rows (script). By hand: a 6-facet gauntlet returned 19 verified fixes against my own spec (3 breaks were mine: Ghosted on a timer, gated rows parked, rubric rewritten without receipt); the live dry run falsified half the first-pass culture hits; the morning-task "succeeded" runs were falsified by the watermark.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: script agreement 6 / dissent 0 -> RETURN. Fair as a count, but the dissent is in the record and not keyword-shaped: the gauntlet, the dry run, the 3.5-week stall, and two slices that came back HELD on real data (the Thesis Care letter; 94 of 95 bundles without an evidence ledger).
- **Cold re-read (canary on the draft handoff-v380.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): "the morning task is fixed" is downgraded to "the prompt is fixed"; the first fixed run's outcome is unseen. The cause line names three factors; only the dirty main checkout and the usage limit are evidenced (git state + one transcript), Gmail is not.
- **Somatic read**: not asked.
- **Disposition**: RELEASED on Zach's '/handoff'.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **Slice 0, Lane kanban** (#754): drag and drop between stages, filter, every row per column (was capped at 4).
- **Slice 1, culture with evidence** (#757): `rubric.culture_cues` in `runtime/specs/target-role-scan.json`,
  `src/lib/culture-cues.ts`; quotes stored in `jdHits.culture_pos/neg`, shown on Role Scan; 2+ negative
  phrases cap culture at 1 and fire the grind gate. Live dry run precision 6/13 then 5/5 after fixing JS
  `async=true`, "governance boundary", "Transparency in Coverage". Cap never fired on live rows (0 negatives
  in top 20); backfill rescore not run.
- **Seeds 5-16** in `_SEEDS/index.jsonl` from a full read of `flashesofbrilliance/job-tracker-pro`:
  9 candidates (culture-cue lexicon germinated) + 3 anti-seeds (synthetic seed data, protection theater,
  consentless biometrics).
- **Spec**: the claude.ai doc "Job Factory: spec, recommendation, plan" (artifact id dd89f5d5) is the only copy. 6-facet gauntlet: 19
  verified fixes applied; teardown lenses BAR/COURT/KKL/FUN HOUSE/anterior-posterior run by hand (FUN HOUSE on
  probation: stop building if sends per week do not rise in 3 weeks).

## Open PRs (merge on green CI after the outage)
| PR | Slice | Note |
|---|---|---|
| #761 | 3 outcome fate + reason | was stacked on #754, now standalone; pipeline token 403 on outcome |
| #769 | 7 prose gate + answers | 1 of 95 bundles has an evidence ledger, so most drafts HOLD on provenance |
| #771 | 2 Missed + drift + intake stall | conflicts with #775 in `JobsBoard.tsx` Row type + tag line |
| #773 | 4 autonomy flags | PATCH admin-only; 5 stations locked |
| #775 | 6 named trust chip + name-leak gate | 57 board rows, 6 companies; 0 of 412 staged files leak a name |

## Morning task (scheduled `arcs-job-search-loop-retargeted-alerts`)
- Found: no ingest since 2026-09-11. The main checkout sits on another session's dirty branch, so
  `git pull --ff-only origin main` failed every run; the weekly usage limit killed 9/30 and 10/1; runs still
  read "succeeded". One run hung 42 h (stopped).
- Fixed on Zach's yes: dedicated detached worktree `.claude/worktrees/morning-jobs` at origin/main, a
  loud preflight (`STATUS: FAILED <reason>`), 10-day backlog chunks, Step 7 reads `/api/jobs/drift`.
- First fixed run `local_c4605b5e` started 2026-10-05 20:53 UTC; outcome not seen (may await tool approvals).

## Open (next session)
1. **GitHub Actions major outage** (since 19:11 UTC). A background watcher in this session re-runs CI on the
   5 PRs once Actions is operational; if the session ended, re-run by hand, merge green with `--merge`, receipt each.
2. Add the autonomy read (`GET /api/jobs/autonomy`) to the morning task once #773 deploys.
3. Once #769 and #775 merge, wire #775's name-leak script into #769's prose gate. Champions tab ignores `?company=`.
4. Backfill culture rescore (top two tiers first); a shared vetted evidence ledger for prose provenance.
5. Chip running in a separate session: deterministic mechanical halves for the five teardown lenses.
6. Carried from v3.79.0: Lyndon call + `/recoil-close`; Autopilot 10-13 nudge; Vico funding question.

## Lessons (in the record)
- A run that does nothing must not read as a run that worked: the stall hid for 3.5 weeks behind "succeeded".
- My own journey diagram broke the human line in three places; the gauntlet caught it, not me.
- A live dry run beat the fixtures: half the first-pass culture hits were false.
