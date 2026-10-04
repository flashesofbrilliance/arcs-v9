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
text: #e2e8f0 | muted: #475569 | dimmed: #64748b
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

# Handoff — v3.78.0 (2026-10-04)

> **Open-loops sweep: four merges, a disk rescue, a worktree prune with a lossless harvest, and the
> session fanned out into seven forked sessions.** Merged on Zach's go: #706 (`07d580ae`), #674
> (`b58ebc49`), #708 (`dfad5218`); #724 (`1d618b04`) merged by the exoskeleton session. One receipt
> each in `decision_receipt` (#724's filed by its own session). Oracle handoff=44.

### Shavasana — handoff pause, 2026-10-04 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): script reported 122 commits, 23 merges to main (whole day, all sessions). This session: 1 authored commit (`a5f734d3` research note, via #708), 3 merges on go (#706, #674, #708), 3 receipts filed.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: manifesto (exhale, no inhale) by the script's day-wide count.
- **Sycophancy check**: agreement 32 / dissent 0 (ratio 32.0) → RETURN by the script. Dissent this session, not marked in records: refused to merge #689 (conflicting); refused to read the LinkedIn panels as testing the 10-04 playbook; corrected "Opus is good at video" to "writes render code and prompts"; refused to prune prl-chatbot (main checked out); stopped retrying declined DB writes.
- **Cold re-read (canary on the draft draft.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): "nothing lost" in the prune narrowed to "branches bundled + gitignored trails harvested"; other gitignored files outside `_STATE`/.env/dev.db were not harvested. Disk "22 GB free" is the df reading at the time, not a stable number.
- **Somatic read**: not asked.
- **Disposition**: RELEASED on Zach's '/handoff'.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **Merges:** #706 NFTT originals dates; #674 Notomation promo record (first red was runners never
  starting, then a stale merge ref; `gh pr update-branch` fixed it); #708 Welsh/Bloom study
  (`_PATTERNS/2026-10-04-linkedin-creator-playbooks-welsh-bloom.md`). #689 skipped (conflicted), then
  landed via its own forked session.
- **Forked sessions (spawn_task):** night-moves schedule + backfill; backlog `review_by` + grooming;
  gitleaks + receipt schema test + argparse; honest.arcs.care press run; #689 + video prompt engine;
  open-loops exoskeleton (`scripts/open_loops.py`, #724); Welsh/Bloom queue changes.
- **Disk:** 4.6 GB -> 22 GB free. node_modules removed from 19 idle worktrees, npm cache cleared, old
  Playwright builds removed (kept chromium-1243, firefox-1532, webkit-2311).
- **Harvest then prune:** gitignored `_STATE/handoff-progress.*` (+ `.env*`, `dev.db`) from 42
  worktrees copied to `~/arcs-worktree-bundles/handoff-trails/2026-10-04/` (INDEX.txt). Then 49
  worktrees pruned via `cruft_sweep.py --base origin/main --capture-dirty`, each bundled and
  verified first. 67 -> 18 worktrees. Exoskeleton session claimed 20 trails on main; 18 unclaimed.

## Open (next session)
1. Kept for Zach's review (unique work): success-academy-ai-pm-5bf0d9, agent-a34d1c57f995635e7,
   recursing-brattain-190758, exciting-chandrasekhar-095f02, zen-pasteur-85c635.
2. `prl-chatbot-sugarcrm-605dbe` has `main` checked out with 341 uncommitted files (from 09-08). Not
   pruned: `--capture-dirty` would WIP-commit onto local main. Needs a side-branch decision.
3. Supabase `execute_sql` writes from this session returned "declined" three times after earlier
   inserts worked. Unexplained; check `/permissions` for a rule on `mcp__supabase__execute_sql`.
4. ~15 stale conflicting PRs (#43..#531) not triaged; #623 tao batch collides with tao-284.
5. LinkedIn: today's second Apple post numbers unread; pre-registered A/B (10-05 vs 10-12) pending.
6. Spotify cache (7.9 GB) is Zach's to clear.

## Lessons (in the record)
- `cruft_sweep.py survey` with the default base compared against a stale local `main`: every worktree
  read REVIEW with ~900 "unique" paths. Pass `--base origin/main`.
- A git bundle does not carry gitignored files. The handoff trails are gitignored, so a prune without
  a harvest would have deleted the session's working memory. Harvest, then prune.
- Check the receipt table by `receipt_id` before inserting: a parallel session had already filed
  #724's receipt under the same id, and a refs-pattern lookup missed it.

# Handoff — v3.77.0 (2026-10-04)

> **Exoskeleton video v2 + renderer landed; the video cut type ships: one shot spec to an HTML scene
> and a prompt pack.** Two PRs merged on Zach's explicit go: #689 (`6892b016`) and #709 (`8f2f98e2`);
> receipts `2026-10-04--exoskeleton-video-v2-pr689--ZH` and `2026-10-04--video-cut-type-pr709--ZH`.

### Shavasana — handoff pause, 2026-10-04 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): script counts the whole repo's day: 91 commits, 16 merges to main. This session by hand: 6 commits (`62492a31`, `da76e4e0`, `87645dbd`, `a226b139`, `9e311959`, `1fe7d3de`) + 1 conflict merge (`48bada1c`), 2 merges to main (#689, #709), 2 receipts.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers (script). By hand: one red check refused (fe-smoke on #709, fixed before merge), one invented caption cut on Zach's ask.
- **Breath balance**: script read manifesto; with the by-hand inhale, breathing.
- **Sycophancy check**: agreement 25 / dissent 0 (ratio 25.0) -> RETURN by script; the refused red merge and the cut caption are the session's dissent, not recorded as markers.
- **Cold re-read (canary on the draft draft.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): the prompt pack is stated as untried, not as working. Nothing dropped.
- **Somatic read**: not asked.
- **Disposition**: RELEASED on Zach's '/handoff'.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **#689 unblocked:** merged origin/main into `claude/greeting-wedifk` (`48bada1c`). The one conflict,
  `scripts/connector_render.py`, took main's side: main's repo-keyed `EXTERNAL_PAGES` row already gave
  the honest card its gh URL and clone chip. All checks green, then `--merge`.
- **Video cut type (`scripts/video_cut.py`):** spec in `_QUEUE/video/<id>.json` (beats: caption,
  duration, accent, shot = subject/camera/motion/light; aspects 16:9 + 9:16). `build` writes
  `_PROPOSALS/video/<id>-<16x9|9x16>.html` (the `window.DURATION` + `window.seek(t)` contract of
  `scripts/html_video_render.mjs`, palette read from `src/ui-kit/recoil-report/_tokens.css`, Inter +
  JetBrains Mono from `public/fonts/`) and `<id>-prompts.md` (per-beat, per-aspect prompts + one
  negative prompt; captions kept out because models garble text). Gates reuse `linkedin_cut.py`'s
  slop_lint, provenance_lint, PII; `--self-test` covers 7 fail-on-bad mutations + font asserts.
- **First input:** `tao-284`, 4 beats, 14.5s, captions are the proverb's words only (an invented
  bridge caption was cut on Zach's ask). MP4s rendered locally, not committed.

## Open (next session)
1. The prompt pack is untried against any external video model: paste one beat, compare to the HTML
   render. That test decides whether the generative path earns its keep.
2. `video_cut.py` and `linkedin_cut.py` run in no hook or CI job; wire both or neither.
3. Carried: `shavasana_handoff.py` exhale author filter; `post-1-brief` / `post-1-exec` wrap-lint.

## Lessons (in the record)
- `fe-smoke`'s page gate sweeps every changed `_PROPOSALS/*.html` at 375/790. A fixed-size video frame
  overflows there; scaling the stage to the viewport (scale 1 at render size) passed it, and the
  rendered poster stayed pixel-identical (ffmpeg PSNR inf).
- The Write tool turned `"—"` escapes into literal em-dashes in the fixtures; grep after writing.
