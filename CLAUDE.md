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

# Handoff — v3.72.0 (2026-09-30)

> **Reading Room tenant #3 shipped: the Chronicle, "Drishti: a Chronicle of ARCS".** PR #651 merged to
> main at `e902a439` on Zach's explicit go; one `decision_receipt` row
> (`2026-09-30--chronicle-reading-room-tenant--ZH`). The fe-smoke job was red on 5 tests (blacksmith `/`, `/observatory`,
> growth-ai `/forge`, two smoke `/recoil` gates), the same 5 failing on main run 36668935316; the chronicle
> tests pass in CI.

## Shipped + on main
- **Shape (Zach, 2026-09-29):** five books by git epoch (Genesis `471d5739`..`a61d492e`, Exodus ..`445ebf08`,
  Leviticus ..`1dffaa2e`, Numbers ..`d21c7ee6`, Deuteronomy ..`aef6180a`; Day 0 = `471d5739`, matching
  status.arcs.care DAY 173) x five fathoms (the profile-scan "Five Fathoms", rendered as a resolution descent:
  30,000 ft / 8-bit to ground truth / 8K). Each book: a chakra (Muladhara..Vishuddha; Ajna and Sahasrara shown
  as not yet reached), a canon epigraph (`tao-137`, `tao-150`, `tao-099`, `tao-012`, `tao-028`), and a closing
  Operator 25 Shavasana. Oxherding was proposed and dropped for chakras.
- **SSOT:** `runtime/specs/chronicle-books.json` (prose + claims + the written half of each Shavasana). Renderer
  `scripts/chronicle_render.py` computes every fathom-4 count and the Shavasana mechanical half from git + the
  falsification ledger, reads epigraph text from `_CANON/tao-proverbs.jsonl` by id, and exits 1 on an em-dash,
  an unknown tao id, or a non-contiguous boundary. `--check` and `--self-test` (9/9).
- **Route:** `/api/reading-room/chronicle` (concordance clone) + `outputFileTracingIncludes` entry; manifest
  `chronicle` built:true. Test `tests/chronicle.spec.ts` (22: one-fathom-at-a-time in every book, 4 widths x 5
  fathoms, lede spans the lane).

## Open (next session)
1. Live admin render at app.arcs.care/reading-room/chronicle not verified after deploy.
2. Somatic reads for all five Shavasanas are pending Zach.
3. Unproven in the page: first READY deploy date, the ADR-collision cause, 2/247 closed outcomes (re-measure
   against the DB), the Nov 2025 Book of ARCS.
4. Concordance route has no `outputFileTracingIncludes` entry; spun off as its own task (running separately).

## Lessons (in the record)
- A count named "merges" was a count of PR-merge subjects (Numbers 139 vs 214 merge commits). The skeptic pass
  caught it in five places; name a count by the predicate that produced it.
- CI checks out shallow: any gate that re-derives from deep history must fall back to the committed render.
- The impeccable pre-commit detector reads DESIGN.md: `--dimmed` fails 4.5:1; muted copy uses text-secondary.

# Handoff — v3.71.0 (2026-09-28)

> **Chip rank 7 closed: Operator 21 (Librarian) retrieves by expected value under a context budget
> instead of recency.** PR #613 merged to main at `150beb19` on Zach's explicit go; one
> `decision_receipt` row (`2026-09-28--librarian-recommend-op21-merge--ZH`). Draft-first; both red
> CI jobs (`leak-check`, `smoke`) verified inherited from main run 36373013499 and untouched by the diff.

### Shavasana — handoff pause, 2026-09-28 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 31 commits, 12 merges to main, receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 1 dissent markers, 1 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 16 / dissent 2 (ratio 5.33) → THIN: high agreement, little dissent.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): every claim carries a sha, a path, a PR number, or a receipt id. Nothing downgraded, nothing dropped.
- **Somatic read**: asked in this handoff (certainty now vs at start; sends today?). `somatic: pending Zach's answer`.
- **Disposition**: RELEASED on Zach's 'run the handoff'. Sycophancy check read THIN (16:2), not RETURN; the dissent on record is the two red CI jobs traced to main, the integrity-gate FAIL on the `_STATE` run file, and the four `what_unconfirmed` rows in the receipt.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **`operators/arcs_librarian.py`** (`aaf81d33`): stdlib-only `Librarian.recommend(q, budget, stakes)` over
  ADRs, seeds + seed ledger, tao, LEGEND, LORE, registry rows, lattice nodes, falsification / assumption /
  backlog / witness / operator ledgers, memory bodies, store receipts, and its own prior picks (1087
  candidates on the first run). Formula per `seed-service-librarian-retrieval-policy`: value =
  p_load_bearing x cost_if_absent(stakes); cost = read_friction (tier steps + tokens/8000 + stale surcharge)
  + bytes/remaining_budget; take iff value - cost >= 0. Source-trust tier is read before backing; unbacked
  items only ever land in `what_unconfirmed`; a ZERO-WEIGHT source contributes no backing even with a
  resolvable sha. `reserve_ratio` + `curation_debt` in every result. Ouroboros: a prior pick falsified by an
  F-row demotes its class. `--self-test` 13/13.
- **`runtime/specs/read-friction-tiers.json`**: the seed's tier prose made data (closes the ledger gap).
- **Registry row 21** rebound `latest` -> `recommend` in `scripts/operator_registry_emit.py`; regenerated with
  `--probe` (READY, probe ok); `--check` green. `ARCSStore.recommend` delegates and adds store receipts.
  Bridge self-test 15/15 including `run_operator(21, payload={q, budget, stakes})`.
- **First real run** committed: `_STATE/librarian/2026-09-28-librarian-first-run-op21-policy.json`
  (6 taken, reserve 0:6). `op:21` ranked first because its registry note, written in the same PR, carries
  the query terms: the ouroboros clause visible on day one.
- Seed ledger: `germinated` row for `seed-service-librarian-retrieval-policy` citing PR #613 (`a7b912e2`).

## Open (next session)
1. **Backlog row `librarian-recommend-needle` status append still owed**: the row lives on
   `origin/claude/fanout-ranks-2-7` and is not on main (grep count 0 at `7e812c6c`). Append PR #613,
   `150beb19`, and the receipt id when that branch lands; then close issue #584.
2. Calibration of the pre-score (tier steps, `tokens_per_step`=8000, stakes multipliers) has no human
   adjudication behind it yet. Reserve ratio 0:6 on the first run: no top item carries a resolvable sha.
3. `reserve_ratio` + `curation_debt` still need a consumer (Op 28 Auditor). Fold ridgeline shift rows are
   named as a defeater but no ridgeline file exists on main to read.
4. `unfold-uses-librarian` (unblocked by this chip; no issue yet).

## Lessons (in the record)
- The first thing a value-ranked librarian retrieves about itself is its own description. Rank the
  registry note as a candidate, not as ground.
- An integrity gate that fails a `_STATE` record for citing a file on the same unmerged branch is doing
  its job: the record is drifted-at-birth until the merge lands.
