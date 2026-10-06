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

# Handoff — v3.91.0 (2026-10-05)

> **cruft_sweep survey compares against origin/<base> (#837, merged without CI on Zach's go); first live prune
> on the fixed code.** Receipt `2026-10-05--cruft-survey-origin-base-pr837--ZH`.

## Shipped + on main
- **#837 (`9bef38d7`):** `resolve_base()` turns a bare `--base` into `origin/<base>` for every subcommand (a stale
  local main made ~46 files read "unique" in every fresh worktree); `worktrees()` keeps detached entries; detached
  heads already on upstream are no longer pinned. Rule 11. `--self-test` 16/16; the #809 version fails 3. Live
  survey: SAFE 7 -> 19, `li-main` and `m715` listed.
- **Live prune (Zach's go):** `cool-bell-742f40` (5edc25fe) and `unruffled-pike-3b578c` (21cc370c). Sessions were
  already archived (archive left the worktrees detached but intact). Both tips on origin/main: no bundle, MANIFEST
  rows `on-origin/main`, worktrees removed, exit 0. Two redundant `refs/cruft-archive` pins deleted by hand.

## Open (next session)
1. **GitHub Actions blocked by billing** ("recent account payments have failed or your spending limit needs to be
   increased"): no check runs on any PR until Zach fixes Settings -> Billing & plans. #837 merged with none.
2. The incremental-bundle path (a SAFE worktree with its own commits) has still only run in the self-test.

## Lessons (in the record)
- A dry run proves resolution, not the write path: only a real prune exercised the manifest and pin logic, and it
  found the redundant pins.
- Six checks failing at once in seconds is infrastructure, not code: read the annotation before calling it red.

# Handoff — v3.90.0 (2026-10-05)

> **Job Factory session, second half: slices 2-4, 6-7 landed, the FDE handoff, the job routes on current
> models, a Tenex application ready to send, and three spending limits hit in one evening.** Merged on Zach's
> asks with receipts: #782 (`36d42cf0`), #784 (`a60b02f9`), #789 (`495d8221`). A parallel merge-train session
> merged #761 #769 #771 #773 #775 with its own receipts. Oracle handoff=45 (v3.88.0 and v3.89.0 were taken by parallel sessions today).

### Shavasana — handoff pause, 2026-10-05 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): script read 0 (scoped to the fresh handoff branch). By hand this half-session: 3 merges by me (#782 #784 #789) with receipts, 5 more by a parallel merge-train (receipted), 1 open PR (#832), 1 scheduled-task prompt revised (and one bad write restored within a minute), 1 Tenex application staged for Zach.
- **Inhale** (what came in): 1 dissent marker, 2 unconfirmed markers (script). By hand: a 6-facet gauntlet HELD the Tenex letter v1 (two trust-breakers also in the resume); Zach corrected the GitHub-link drop; three spending limits falsified "the line is running".
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 16 / dissent 3 (ratio 4.0) -> OK: dissent present.
- **Cold re-read (canary on the draft handoff-v389.md)**: GROUNDED after adding merge SHAs and receipt ids (first pass: NO GROUND RETURN on "Shipped + on main").
- **Attachment release** (Claude, cold re-read): "the security review drained the API cap" is held as the main suspect, not a finding, until the Console shows usage by key; the 11 failed cuts are recorded as not written, not as pending work done.
- **Somatic read**: not asked.
- **Disposition**: RELEASED on Zach's 'run handoff while CI waits'.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **Slices 2, 3, 4, 6, 7** (#771 `ca742146`, #761 `367b528f`, #773 `567b224c`, #775 `5ae9a6b2`, #769 `38f8aab6`; receipts `2026-10-05--pr<N>-merge-train--ZH`): Missed state + backlog drift + intake-stall signal; Lane
  close-form with fate + reason; autonomy flags with 5 locked stations; named-trust chip + name-leak script;
  prose gate (provenance strict, slop lint/eval, honest) + application answers.
- **#784 FDE handoff** (`a60b02f9`, receipt `2026-10-05--fde-handoff-pr784--ZH`): bridge-scan's routing gate "score under target-role-scan" was never executed; 52 rows sat
  PASS. Backfill ran (45/52 handed off, 22 PURSUE; Upside 0.966 PASS -> 0.889 PURSUE). Role Scan SRC line now
  names the real scorer.
- **#789 job routes** (`495d8221`, receipt `2026-10-05--job-routes-model-migration-pr789--ZH`): writer routes on `claude-sonnet-5-5` (no temperature, effort low/medium, `fallbacks:"default"`),
  scorers on the `claude-haiku-4-5` alias, `modelError()` returns 503 + the API's message + a code, new
  `GET /api/jobs/model-health`. Live-proven on the PR preview before the cap hit.
- **#782** (`36d42cf0`, receipt `2026-10-05--lane-full-width-pr782--ZH`): Lane root `width:100%` (flex-column body had shrunk it to 699px; 3 of 5 stages per row).
- **Morning task** (scheduled, outside repo; file `~/.claude/scheduled-tasks/arcs-job-search-loop-retargeted-alerts/SKILL.md`, verified `grep -c model-health` = 1): preflight (d) now calls `/api/jobs/model-health`; usage_limit = FAIL
  reported verbatim, never retried.

## Spending limits hit (all three are Zach's decisions)
1. **Anthropic API workspace cap** (`wrkspc_01LPHV...`): every model route in production 503s until it is raised or
   resets 2026-11-01. Main suspect: `claude-security-review` (228 runs in Oct, 197 on 10-04/05) on the
   `ANTHROPIC_API_KEY` repo secret. Unconfirmed that the GitHub secret shares the workspace: Console usage-by-key
   settles it. Production routes themselves were small (3-day logs, mostly cached/Haiku; `/api/guide` is Opus 4.5).
2. **GitHub Actions billing**: jobs no longer start ("recent account payments have failed or your spending limit
   needs to be increased"). No PR can go green until Billing & plans is fixed.
3. Claude plan weekly limit hit earlier (killed the 9/30, 10/01 morning runs); separate meter, not the API key.

## Update after the handoff (same session)
- **#846** (`d7171ca9`, receipt `2026-10-05--tenex-bundles-upside-overclaims-pr846--ZH`): Tenex founder note filed beside the
  Senior application; stale `evidence.PROPOSED.jsonl` removed; Upside resume's two gauntlet-falsified lines fixed. The Tenex
  Senior bundle itself landed in `8c2d61fe` (location-fix session). Open item 3 below is done except the send (Zach's).

## Open (next session)
1. **#832** (security review once per PR, path-scoped; ~87% fewer runs measured on October) is OPEN, not merged:
   CI cannot start (GitHub billing). Merge when green per Zach, or on local verification if he says so.
2. **11 resume cuts** for the shortlist's open FDE rows failed on the API cap before writing anything; script at
   the session scratchpad `cut_all.sh` pattern: `forge_edit_from_seed.mjs --jobid <id>` then the location +
   overclaim fixes. Shortlist: `_STATE/job-search/missed-shortlist-2026-10-05.md` (uncommitted; regenerate if lost).
3. **Tenex Senior FDE application is READY for Zach to send** (resume + cover letter + founder note, all in iCloud
   `ARCS/resumes/tenex-senior-forward-deployed-engineer/`). Local bundle uncommitted on branch
   `claude/forge-tenex-senior`; commit it now that #791's seed-style fix is on main.
4. Chips running/filed: 31 resumes "Fully remote (US)" -> "New York Metro" (task_f0cd3f02, running); preview
   magic-link sign-in (task_ca922c90, running); deterministic teardown lenses (task_f1b1f738, ended: check its PR).
5. Migrate the remaining old models (brief, compass, guide on Opus 4.5, tribune, annotations, slop_eval,
   network_scan); stale local `@anthropic-ai/sdk` 0.100.1 vs `^0.128`.
6. Slice 5 held behind its tripwire (queue must run dry two weeks; 484 rows Missed today).

## Lessons (in the record)
- A spending cap hides as a 500. Surface the upstream error with a code, and preflight the API before a run.
- CI that runs an agent on every push is a production cost line; scope it to the paths it can protect.
- I passed a placeholder (`@@FILE@@`) as a scheduled-task prompt and restored it within a minute: write the full
  text, then verify the stored file, every time.
- Memory said the GitHub profile was linkable; I dropped the link anyway before checking. Read memory first.
