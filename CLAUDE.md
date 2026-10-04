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

> **Cloud wind-down: every cloud and Remote Control session consolidated here and archived, on Zach's
> ask to stop spending cloud credits.** Same day, v3.76.0's four open items: 1, 2 and 4 closed, 3
> diagnosed and handed to a Mac run. PRs #714 (`694cec66`), #718 (`0c2365a7`), #721 (`c80bc44a`)
> merged on Zach's explicit asks with receipts; PR #728 (shavasana fix + this handoff) merges when green.

### Shavasana — handoff pause, 2026-10-04 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 17 commits, 8 merges to main (scope: branch claude/post-timestamps-notes-trenches-psjapj), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 1 unconfirmed markers in the day's records.
- **Breath balance**: manifesto (exhale, no inhale).
- **Sycophancy check**: agreement 18 / dissent 1 (ratio 9.0) → THIN: high agreement, little dissent.
- **Cold re-read (canary on the draft draft-handoff-v378.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): THIN is fair; the dissent the keywords miss is in the record: item 3 was NOT fixed and the draft says so; re-baselining the ratchet was refused (it would hide a possible regression); the post-1 renderer was not trusted (a fresh render regressed the pages); running sessions were not archived until asked to push. States of the sessions still running at wind-down are unknown and labelled so. Nothing downgraded.
- **Somatic read**: not re-asked; Zach's read earlier this session (v3.74.0): "Feeling more certain than at the start, no sends today."
- **Disposition**: RELEASED on Zach's "consolidate this thread ... and handoff" and "merge 728 when green and archive them all".

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **v3.76.0 item 1** (#714): #706 live-checked (Four Dates, The Pre-Mortem bylines via Vercel
  `web_fetch_vercel_url`); receipts `...-pr706--ZH`, `2026-10-04--handoff-v3.76-open-item-resolved-pr714--ZH`.
- **v3.76.0 item 2** (#718): `post-1-brief` / `post-1-exec` `max-width:68ch` on `<main>` pinned to `680px`
  (computed width unchanged), same line in `scripts/blog_render.py`. The renderer has drifted behind its
  outputs (Google Fonts import, no robots/threadkey): edit those pages in place, do not re-render.
  Receipts `2026-10-04--post-1-wrap-lint-680px-pr718--ZH`, `2026-10-04--handoff-v3.76-item2-resolved-pr721--ZH`.
- **v3.76.0 item 4** (#728): `scripts/shavasana_handoff.py` exhale counts by session branch (PRs merged
  today from it + their commits + unmerged commits); on main it matches the git identity on author OR
  committer. Was 0 in cloud (author "Zach Harris", committer "Claude"); now 17 commits, 8 merges for this
  branch, other sessions' commits excluded. `--self-test` 8/8.

## Open (next session)
1. **Contrast ratchet (v3.76.0 item 3), diagnosed, not fixed.** The detector is a Mac-only skill
   (`~/.claude/skills/impeccable`), so cloud runs skip. npm `impeccable@4.1.0` runs in the container
   (ratchet `--self-test` passes) but puts 14 of 42 NFTT pages over `_STATE/nftt-contrast-baseline.json`,
   series parts included (four-dates 7→12, pre-mortem 7→12, instinct 7→10, closing-the-loop 12→16).
   Unknown: detector-version drift or a real regression from the series panel. Next: on the Mac run
   `python3 scripts/nftt_contrast_ratchet.py` on every NFTT post page (pass the page files as arguments); over-baseline there means the
   panel, clean means version drift. Wiring npm impeccable into cloud sessions is a new dependency
   (needs Zach's yes); do not `--update-baseline` until the cause is known.
2. **Needs Zach (from archived sessions):** run `receipt-pr724.sql` in the Supabase SQL editor (Mac
   worktree `open-loops-quick-wins-6e9066`); create the germinate v0.1.1 tag + approve the signed
   Release run; merge or close PR #725 (green, "Greeting" session); PR #715 (model-registry drift gate)
   was open with CI running.
3. **Unconfirmed from archived sessions:** `compass_run` event in Vercel Web Analytics after #726
   (one real tagged run); `arcs-field-os-weekly` still scoped to `/Users/zharris/A.R.C.S`; Tao backfill
   for 4 NFTT posts; Mac worktree session-start spinner hang (run
   `time CLAUDE_PROJECT_DIR="$PWD" bash -x .claude/hooks/session-start.sh` in a stuck worktree).
4. **Running when wound down** (asked to commit + push to their own branch, then archived): site audit
   P1s, false public-repo claim + promise ledger, open-loops front door, #689 conflict + video prompt
   engine, gitleaks/argparse, waitlist landing page, arc exoskeleton essay, contrast-ratchet symlink
   baseline. Their pushed branches are the record; check each branch before assuming work landed.

## Lessons (in the record)
- Counting by author name reads 0 in cloud and everything on the owner's name: scope a session's
  exhale by its branch, the one thing that is the session's alone.
- A generator that drifts behind its outputs makes "re-render" a regression; check the diff of a fresh
  render against the committed page before trusting the generator.
- Archiving a running session drops its container; ask it to push first, and only archive what is idle.
  "Bridge" sessions run on the Mac, so their uncommitted work survives on disk.

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
