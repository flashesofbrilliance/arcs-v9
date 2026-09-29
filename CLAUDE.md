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


# Handoff — v3.70.0 (2026-09-28)

> **Chip rank 2 closed: the falsification count is on the public surface, stamped from the ledger.**
> One PR (#591), one merge (`740aa55f`), one receipt, live-verified on good.arcs.care. Draft-first;
> merged on Zach's explicit go; the two red CI jobs on the PR (`smoke` ledger delinquency, `leak-check`)
> were the same two red on main's own run and untouched by the diff.


### Shavasana — handoff pause, 2026-09-28 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 19 commits, 7 merges to main, receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 3 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 12 / dissent 3 (ratio 3.0) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): every claim carries a sha, a path, or a receipt id. Nothing downgraded, nothing dropped.
- **Somatic read**: asked in the handoff message (certainty now vs at start; sends today?). `somatic: higher than at start; no sends today` (Zach, 2026-09-28).
- **Disposition**: RELEASED on Zach's 'run the full handoff with the operator 25 pass'. Sycophancy check read OK, so no RETURN.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + LIVE (verified with `get_deployment` + curl, not from the diff)
- **good.arcs.care/audit** carries a card, "We keep our own ledger": the count of falsified beliefs (40 at
  merge), the date of the latest (2026-09-27), and a link to the belief log at status.arcs.care/beliefs
  (HTTP 200 before linking; no proxy change needed). Branch commit `06ca7c8e`, merge `740aa55f`.
- **The count is never typed by hand.** `scripts/belief_log_emit.py` gained two outputs: it re-stamps only the
  block between `<!--ledger-stamp:start-->` and `<!--ledger-stamp:end-->` on the audit page (count of
  `verdict=FALSIFIED` rows + max `ts`; a future HELD row cannot inflate it), and rewrites the one generated row
  of `public/good-agent-receipts-audit.evidence.jsonl` so `case_evidence_lint` traces the stamped digits to
  the belief log's summary line. `--check` (the existing hard CI `belief-log` job) fails when either lags the
  ledger. Fail-on-bad proved: count edited to 41 -> exit 1; evidence row edited to 39 -> exit 1.
- Gates from this worktree, all green for the page: `artifact_wrap_lint`, `token_source_gate` (tokens inlined
  verbatim), `altitude_canary` GROUNDED, `case_evidence_lint`, `provenance_lint`; `leak_check` 0 hits on the
  file. Sweep 360 / 790 / 1280: the 790 pass caught the date breaking at its hyphen; fixed with
  `white-space:nowrap` on the stamped date.
- Receipt `2026-09-28--audit-page-falsification-count--ZH` in `decision_receipt`. Waypoints commented on
  PR #591 and issue #579.

## Open (next session)
1. **Backlog row `kintsugi-public-falsification-count`** (issue #579) is on PR #585's branch
   (`claude/fanout-ranks-2-7`), not main. After #585 lands: append `live · 740aa55f · receipt id` to its
   `status`, then close #579. Not added to main here because it would conflict with #585 line-for-line.
2. Inherited red on main, untouched: `smoke` ledger delinquency (`scripts/ledger_check.py`) and six
   `leak_check` hits (two NFTT posts, three war rooms, observatory index).
3. The pre-commit `case-evidence` gate was the round-2 surprise: it covers every digit on any page with a
   sibling `.evidence.jsonl`, so a generated number needs a generated evidence row. Pattern now lives in the
   emitter; reuse it before hand-stating any number on a gated page.

## Lessons (in the record)
- A number on a public page that a script can compute must be stamped by that script and covered by the
  script's own `--check`. Hand-stating it would have passed every gate and drifted on the next ledger append.
- The gate that blocked the commit was not one of the four the chip listed. Run the pre-commit hook path,
  not only the named gates, before calling a page clean.
