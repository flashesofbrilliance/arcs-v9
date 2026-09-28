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
- **Self-contained artifact/page CSS: one shared px `--measure` for BODY/card reading text — NEVER `max-width:NNch` per element** (font-dependent → misaligned right edges that read as broken wrapping). **But LEDES are the exception: a hero/section lede spans the full lane width matching its heading (`max-width:none`), never the narrow body measure — a lede narrower than its heading reads as a broken/abridged block with a dead right gutter (`design-full-width-lede-matches-heading`; Zach's standing preference, do NOT "fix" it back to `--measure`).** The "too narrow" symptom is invisible to overflow/clip gates — eyeball lede-vs-heading edges at ~1280px too. Bordered callouts carry the measure on the box, not the inner text. Before shipping any single-file HTML, run the repo's own gate (`scripts/artifact_wrap_lint.py`; `npm test` for `zachharris-xyz`) and sweep 360–1440 incl. the 700–1000 band. Em-dashes 0. Canon: `_PATTERNS/arcs-artifact-css-base.css`; AGENTS.md gotcha #13.


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

# Handoff — v3.69.0 (2026-09-27)

> **The Orthogonal Echo Detector got a signature that is a function of the text, and the first
> thing it found was the template.** One PR merged to main (#612 at `defaecc4`), one
> `decision_receipt` row (`2026-09-27--echo-embedding-signature-merge--ZH`). Draft-first; merged
> on Zach's explicit go behind a guard that proved the two red CI jobs (`leak-check`, `smoke`) were
> inherited from main at `e36084f4`.

### Shavasana — handoff pause, 2026-09-27 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 75 commits, 23 merges to main, receipts in digest: 0.
- **Inhale** (what came in): 3 falsification rows today, 16 dissent markers, 7 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 55 / dissent 26 (ratio 2.04) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): every claim carries a sha, a path, a receipt id, or a number from the committed report. Nothing downgraded. The exhale counts are the whole day across sessions, not this chip's (this chip: 1 commit, 1 merge, 1 receipt).
- **Somatic read**: `somatic: asked in this handoff` (Zach present; certainty now vs at start, sends today?). No sends from this session.
- **Disposition**: RELEASED on Zach's "Go ahead" (canary GROUNDED, dissent present).

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **`operators/arcs_echo_embedding.py`** (`24bbcb15`, PR #612): `build_embedding_detector()` binds
  the two injectables `OrthogonalEchoDetector` already exposed. Signature = segment embeddings +
  `PATTERN_LIBRARY` phrase embeddings via the same local model `arcs_api.py` serves at `/api/embed`
  (`all-MiniLM-L6-v2`, offline from the HF cache). Orthogonality = 1 - cosine of the domain TEXT
  vectors; names are only the lookup key. Detector untouched. No new dependency (the declared
  `embeddings` extra). Self-test 6/6 incl. fail-on-bad on scrambled smoke domains.
- **`scripts/echo_ridgeline_feed.py`**: `--signature keyword|embedding`, `--seed`, evidence
  segments, a pre-registered TEMPLATE control, `--compare OUT` for a same-seed before/after.
- **`_STATE/2026-09-27-echo-signature-before-after.json`** (seed 27, three unfold stones):
  keyword baseline 0 / scrambled FP proxy 0.8 (4 of 5) -> embedding baseline 3 / FP proxy 0.0
  (0 of 5), all 3 survive 8-11/12 dithers. Template control: 0 echoes for BOTH.
- Fate recorded: `fp-proxy-improved` (mechanical half). The "baseline finds real echoes" half is
  NOT met: all three matches were one keyword ("path dependent") on one boilerplate line shared by
  every stone ("every path below was checked to exist on main at cut time").
- AGENTS.md catalog row; memory `template-aliasing-shared-boilerplate-fakes-cross-domain-echo`.

## Open (next session)
1. **Backlog row status append** for `echo-detector-embedding-signature`: the row is still in
   PR #585 (open), not on main. Waypoints posted on issue #580. Append once #585 lands.
2. **Rank-4 chip (#581)** is level-triggered by this merge: propose RC-OPS-001 criterion 2 from the
   report; `criteria_status` stays Zach's ruling. Recall >= 0.80 is unmeasured (no labeled echoes).
3. **Independent-source input for the feed**: the three stones share one generator, so the detector
   has never seen a clean cross-domain pair. Feed it texts from different authors/templates before
   reading any echo as real.
4. Inherited CI red on main: `leak-check` (5 markers in `public/`), `smoke` (`ledger_check.py`
   delinquency). Not touched here.

## Lessons (in the record)
- Two adversarial controls catch two fabrication classes: scramble catches bags-of-words, the
  shared-line control catches structure the inputs share by construction. A detector fed inputs
  from one generator will always find the generator.
- Report both halves of a two-part JTBD even when the fate vocabulary names only one.


# Handoff — v3.68.1 (2026-09-27)

> **The Accountant keel chip: the external decision funnel measured from prod, founder and external split,
> and the distribution gap located by grep.** One draft PR (#586, commit `498386c6`, cut from `850d203f`),
> not merged; awaits Zach's go. No receipt yet (a receipt follows the merge, never precedes it).


### Shavasana — handoff pause, 2026-09-27 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 52 commits, 18 merges to main, receipts in digest: 0.
- **Inhale** (what came in): 3 falsification rows today, 16 dissent markers, 8 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 49 / dissent 27 (ratio 1.75) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): every claim carries a sha, a path, a query, or a PR number; the funnel numbers are the ingest of queries that ran verbatim. Nothing downgraded, nothing dropped. The exhale counts above are the whole day across sessions, not this chip's (this chip: 1 commit, 0 merges).
- **Somatic read**: `somatic: not asked` (Zach not present; no sends today from this session).
- **Disposition**: RELEASED (canary GROUNDED, dissent present). The PR itself stays draft until Zach's go.

_This block asserts nothing new. Counts, paths, and questions only._

## In the PR (#586, unmerged)
- `scripts/outcome_funnel.py`: read-only instrument over the Prisma tables (`--sql`, `--ingest`, `--self-test`
  passes). First feed at `_STATE/outcome-funnel/2026-09-27.json`, pulled via Supabase `execute_sql` on 2026-09-27.
- External: 10 receipts, 4 users, 6 debriefed, 0 closed, last receipt 2026-07-10, 0 in the last 30 days.
  Founder (separate, always): 196 receipts, 135 debriefed, 3 closed (2 matched, 1 drifted; the third landed
  2026-09-26). Anonymous: 48, none after 2026-07-13.
- Located by grep in `src/proxy.ts` + the three `public/good-*.html` pages: `/copypasta`, `/fears`, `/audit`
  are live (200) and none linked to the compass. Every CTA went to `/audit`, `/cases` or `arcs.care/advisory`.
- The move, on `/fears`: 11 kill-clause cards link into `app.arcs.care/dashboard?q=&horizon=`; the dashboard
  reads `?horizon=` (`src/app/dashboard/page.tsx`). `fears_attribution` query baseline 0.
- Backlog rows `outcome-capture-rate-keel-gap`, `receipted-fears-stunt`: status appended.

## Open (next session)
1. Zach's go on #586; then merge, one `decision_receipt` row, and `get_deployment` to confirm `/fears` live.
2. Re-run `python3 scripts/outcome_funnel.py --sql` a week after deploy; the only number that matters is
   external `last_30d` moving off 0.
3. Unconfirmed: prod `ADMIN_EMAILS` vs the founder identity; the script's `--run` mode (no psql here).
4. Carried from v3.68.0: Tao two-books ruling; memory index curation; the counterpart pulse (Yuri, Robert).

## Lessons (in the record)
- A funnel with zero inflow has no conversion problem. Check the link graph of the live surfaces (grep the hrefs)
  before designing a nudge.
- Compare detector findings from the same directory: the kintsugi ratchet read 15 vs 2 because the HEAD copy sat
  in `/tmp` without `DESIGN.md`; inside the repo it is 15 vs 15.
