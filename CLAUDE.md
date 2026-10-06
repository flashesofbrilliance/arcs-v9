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
  ROM primitives, token-saving rules) plus **only the latest 1–2 handoff sections**. Sessions no longer edit
  this file to hand off: `/handoff` writes a fragment (`_HANDOFFS/fragments/`, one file per session) and
  `scripts/handoff_fold.py fold` assigns versions, prepends the blocks here and moves the oldest to
  `_ARCHIVE/handoffs.md` (ADR-085 part (d), 2026-10-06). Unfolded fragments are newer than any block below.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.103.0 (2026-10-06)

> **Job Factory, fourth part: Missed-pile Undo + newest-listed sort live, and the intake caught up after 25 days.**
> Merged on Zach's asks with receipts: #892 (`bcee855e`, Upside previews, `2026-10-06--upside-previews-pr892--ZH`) and #895
> (`df3d79b9`, `2026-10-06--jobs-date-sort-undo-clear-pr895--ZH`). Oracle handoff=48.

## Shipped + on main
- **#895:** Zach cleared the Missed pile by accident. The clear only writes `missed_cleared_at` (one clear ever,
  2026-10-06T01:12Z); `PATCH /api/jobs/settings {undoClearMissed:true}` deletes it, and the banner shows an **Undo clear**
  button. New **Sort: Newest listed** (firstSeen desc). claude-security-review could not run (API cap); local ciso-review
  PASS posted on the PR. Live at df3d79b9 (verified via get_deployment + API, not the signed-in page).
- **Intake (production data, no PR):** request `cmuvmiqhi...` consumed: 95 alert emails 09-11 -> 10-05, 422 unique,
  46 dupes, **376 new rows UNSCORED**; watermark now 2026-10-05T23:30:12Z. Board 1,205 rows.

## Open (next session)
1. **Zach:** sign in and click **Undo clear** (677 scored rows still hidden; my direct DB delete was declined).
2. **Score the 376 new rows** with `node scripts/jobs_score_sweep.mjs` once the API cap lifts (or 2026-11-01).
3. Morning task still fails preflight on the API cap; intake (Gmail + consume) needs no model, so it could be split out
   of the preflight gate.
4. Chip filed: constant-time compare for the pipeline token in `src/lib/jobs.ts` (task_301be2ed).
5. Carried: Upside send (confirm 2 new titles), Tenex send.

## Lessons (in the record)
- A "stale queue" can be a dead intake: the freshest unswiped row was 12 days old because no mail had been read since 09-11.
- A background agent can stop on "waiting on batches" without writing its output; check the file before trusting the notice.

# Handoff — v3.102.0 (2026-10-06)

> **Receipt, brief and ledger share one vocabulary in the Ahmed order.** #880 (`28225089`), #885 (`2f3cb294`),
> #890 (`a8fd8358`), all merged with CI green (Actions is running again). Receipts
> `2026-10-06--ahmed-order-vocabulary-pr880--ZH`, `--ahmed-order-receipt-pr885--ZH`, `--ahmed-order-brief-pr890--ZH`.

## Done
- `src/lib/vocabulary.ts` + `runtime/specs/ahmed-order-vocabulary.md`: Decision, True North, Reasons, Open questions,
  Next moves, (brief: Situation), Evidence folded. Rulings: label is True North; DEWY keeps all three meanings; a Decision
  is a call, bet or choice; `horizonLabel()` gives plain English ("This Week"). Minted **tao-285** (oracle) as the
  open-question empty state: no model-written answers.
- `src/organisms/AhmedOrder.tsx` renders both pages. Fixed: True North hardcoded SHARP on /receipt; brief never showed
  Reasons; `briefView` defaulted missing values to GREEN/SHARP/TWO_WAY; DebriefCard called NCI "Conviction";
  375px overflow on long path tags; stakes never rendered.

## Open (next session)
1. No GREEN/RED/LOCKED receipt exists in prod: SHARP render untested on real data.
2. Live /brief/[id] against the real API not exercised (verified via Playwright-mocked `/api/brief` with real rows).
3. Chip running: compass answers for open questions (task_160443dd). The receipt-view spend chip landed as #888.

## Lessons (in the record)
- A worktree with symlinked `node_modules` breaks Turbopack dev (`next/font` resolve). Use `next dev --webpack`.
- Real data, zero spend: render ephemeral receipts from sessionStorage, and briefs by mocking `/api/brief` with a read-only row copy.
