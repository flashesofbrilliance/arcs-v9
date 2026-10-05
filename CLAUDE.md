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

# Handoff — v3.80.0 (2026-10-05)

> **Family-roster drift cleared; PR #745 merged on Zach's go (`baabdaed`).** Three receipts:
> `2026-10-04--family-roster-drift-pr745--ZH`, `2026-10-05--family-roster-drift-pr745-live-check--ZH`,
> `2026-10-05--family-roster-drift-pr745-kintsugi-phantom--ZH` (follow-ups appended, original row not edited).

## Shipped + on main
- **`scripts/sync_family_roster.py`:** the four playground performers were unlinked on purpose in #216
  (`0801c1d0`, Playground locked "not yet", cards kept, routes live). The check now passes a performer that
  is linked OR carded on build.html and still fails one absent in both (rename probe exit 1). `--check` 0,
  `--self-test` 12/12.
- **`public/build.html`:** ADR stat 78 -> 79 (ADR-084). The masthead glow (`.masthead::before`, 60px past
  the lane since `ed59a44f`) overflowed 38px at 375/790; held to the 22px gutter below 1280px. Live check:
  no horizontal overflow at 375/790/1440, desktop glow offset unchanged.

## Open (next session)
1. **Worktree hooks run the main checkout's stale pre-commit.** 25 of 27 worktrees carry
   `core.hooksPath=/Users/zharris/arcs-v9/scripts/git-hooks` in `config.worktree`; the main checkout is
   parked on `claude/falsifiable-position-criteria-inltlk`. Its kintsugi gate scores HEAD out-of-tree
   (pre-`c051d3c7`) and undercounts: build.html read 77 vs a real 95. Chip `task_bd140094` is running in
   its own session (needs Zach's yes before repointing). Unknown: what writes the absolute path.
2. Desktop glow not screenshot-compared against a pre-merge render (low).

## Lessons (in the record)
- A drift check that disagrees with a page: read the page's git log before "fixing" the page; the page may
  hold a deliberate state (locked cards) the check never learned.
- A page gate that sweeps only changed pages surfaces old debt on whoever touches the page next: measure
  main's copy before blaming your diff.
- `body{overflow-x:clip}` does not stop a mobile layout viewport from widening; contain the element.
- A ratchet's "HEAD had N" is only as fresh as the hook that computed it: check `git config --show-origin core.hooksPath`.

# Handoff — v3.79.0 (2026-10-05)

> **Schriner recoil closed on the two Vico calls; Lyndon pre-call refreshed; recoil password gate fixed
> for sandboxed previews.** Two PRs merged on Zach's explicit asks: #742 (`eba6c858`) and #746

### Shavasana — handoff pause, 2026-10-05 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): script read 0 (it scoped to the fresh handoff branch). By hand, branch `claude/great-mendel-96d315`: 5 commits (`343eef2d`, `3c83ff54`, `a20879a7` + 2 conflict merges), 2 merges to main (#742, #746), 2 receipts.
- **Inhale** (what came in): 2 dissent markers (script). By hand: Zach declined the receipt row update; one false "updated" claim of mine caught and corrected in the open.
- **Breath balance**: script read mirror; with the by-hand exhale, breathing.
- **Sycophancy check**: agreement 3 / dissent 2 (ratio 1.0) -> OK: dissent present.
- **Cold re-read (canary on the draft block.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): the Forge pass is stated as self-graded; the live check is stated as deploy-level only. Nothing downgraded.
- **Somatic read**: not asked.
- **Disposition**: RELEASED on Zach's '/handoff'.

_This block asserts nothing new. Counts, paths, and questions only._

> (`17647913`); receipts `2026-10-04--schriner-recoil-close-pr742--ZH`, `2026-10-04--lyndon-precall-refresh-pr746--ZH`.

## Shipped + on main
- **/recoil-close, Schriner** (`runtime/recoil/generated/2026-09-14-schriner.json`): only ONE "VICO - Update"
  call happened (invite 09-25, moved 09-29, held 09-30) plus the 10-02 "VICO debrief."; verbatim Granola
  transcripts `824f0855` and `8a125b5f`, none in Fathom. Closed YELLOW/CONVERGENT, req_reality 2 (owner engaged,
  never met; seat unarchitected). Beliefs P10-P13; P12 books Zach's own comp floor at req_reality 2 ("mid-$200s...
  or even like less"). No ex-ante was filed for either call. Forge adjudication was self-graded, no skeptic.
- **Recoil gate fix** (`scripts/recoil_brief.py`): the password gate died when sessionStorage was blocked
  (data: URLs, the desktop app file pane), so no password worked. Storage is now try/catch; verified unlock in
  the browser pane. Other gated pages pick it up only on re-render.
- **/recoil-prep, Lyndon**: the prep already existed (#699, `2026-10-03-oh-vico.json`, `lyndon-war.arcs.care`);
  refreshed it rather than duplicating: comp floor correction, competitor Nick, the seat probe question, a
  funding-source conflict, Joe's 10-04 scheduling reply. Merge conflict with #744's token resync resolved by
  regenerating from the SSOT (style block identical to main).
- Memory `project_joe_schriner_oxenham_autopilot_vico` corrected (the "$200-300K" was Joe's posting, not Zach's).

## Open (next session)
1. **Lyndon call not yet scheduled** (Joe said he'd reach Lyndon the morning of 10-05). After it: `/recoil-close`
   on `2026-10-03-oh-vico.json`, which has a real ex-ante to score.
2. **Receipt for #746 is stale on one field:** it says the live render was not re-checked. Checked since at
   deploy level only (prod `baabdaed` contains #746; page is admin-gated 404 to anon, rendered page not viewed).
   Zach declined the in-place row update; append a follow-up row or leave as is, his call.
3. Vico funding unresolved: pre-seed (10-03 read) vs a Tracxn "$103M over 3 rounds" snippet, likely a name collision.
4. Autopilot: if Aaron is silent by 2026-10-13, ask Joe once; at ~4 weeks resolve to ghosted.
5. Carried from v3.78.0: contrast ratchet item 3 on the Mac; Zach-only asks (receipt-pr724.sql, germinate tag,
   PR #725, PR #715); check wound-down sessions' branches.

## Lessons (in the record)
- A Granola AI summary had moved a number from the recruiter's mouth to the candidate's; the verbatim re-read
  caught it. Score from transcripts, never summaries.
- Run the prep skill against what already exists: a prior session had filed the Lyndon ex-ante 12 hours earlier.
- I told Zach a receipt was updated before it was. It was not; say "will update", then update, then report.
