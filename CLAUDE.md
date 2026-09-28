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

# Handoff — v3.69.0 (2026-09-27, flow-state-om-metric)

> **The Flow-State axis got its first instrument.** Backlog rank 5 (`flow-state-om-metric`, GitHub #582;
> the row itself is on PR #585, not yet main). Draft PR #598, UNMERGED, awaiting Zach's go; no
> `decision_receipt` yet because nothing merged. Sibling sessions ran ranks 2-7 concurrently.

### Shavasana — handoff pause, 2026-09-27 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 64 commits, 19 merges to main, receipts in digest: 0.
- **Inhale** (what came in): 3 falsification rows today, 16 dissent markers, 7 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Breath net direction** (Maekawa; asm-009 open, read across ten handoffs): exhale 64 minus inhale 26 = +38, exhale-leaning.
- **Sycophancy check**: agreement 49 / dissent 26 (ratio 1.81) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Om** (Flow-State axis; component 7): confidence 0.33 (1 of 3 sections carry a ground return); conviction: not given (--conviction absent); om_gap: null, not imputed.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today? Give the number as `--conviction 0-10` and re-run.
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

- **Attachment release** (Claude, cold re-read): the draft's Open and Lessons sections carry no cite class
  (confidence 0.33 is the honest number for a three-section draft); nothing downgraded, nothing dropped.
- **Somatic read**: somatic: not asked (Zach absent); om_gap null, not imputed.
- **Disposition**: released as a draft PR; merge is Zach's move.

## Shipped on branch `claude/zen-pasteur-85c635` (PR #598, draft)
- `f8bd5ec3` `scripts/shavasana_handoff.py`: `confidence` (sections with a ground return / non-empty
  sections, via `scripts/altitude_canary.py`), `--conviction 0-10` (null when absent, not imputed),
  `om_gap` = |confidence - conviction/10| or null, `breath_net_direction` = exhale_n - inhale_n (signed,
  no verdict; asm-009 open), `--json`. Self-test 4 -> 15 checks; the block is asserted to have ZERO
  confidence markers by the canary's own regex. Spec `runtime/specs/operator-25-shavasana-v0.md`
  components 3/6/7 + contract; `.claude/commands/handoff.md` Step -2; `_STATE/assumptions.jsonl` asm-009 notes.
- `aafb90aa` `_STATE/2026-09-27-om-first-reading.md`: zero point of the series (conviction null, confidence 0.33, net +33).

## Open (next session)
1. Zach: merge #598 or return it; on merge, one `decision_receipt` row + append `status` on the backlog row
   once #585 lands it on main (do not duplicate the row).
2. The first reading WITH a conviction number: run Step -2 with `--conviction N` at the next handoff Zach attends.
3. v1 candidate, spec-table change not a silent one: sentence- or bullet-level claim unit for `confidence`.
4. Registry row 25 stays UNBUILT (`operators/arcs_shavasana.py` does not exist); this is the handoff-door half only.

## Lessons (in the record)
- The fifth axis is a fraction and a subtraction; the work was refusing to fill in the human's number.
- A block that describes itself as claim-free should be checked by the same regex that would catch it.


# Handoff — v3.68.0 (2026-09-27)

> **The membrane day: an external audit of the operator suite was falsified by grep, and the repo grew
> the organs that make that class of fabrication mechanically detectable.** Eleven PRs merged to main
> (#559 to #569), eleven `decision_receipt` rows, each with an honest `what_unconfirmed`. A twelfth
> (#570, the fate registry) is open. Draft-first throughout; merged only on Zach's explicit go, every
> merge behind a guard that verified the two red CI jobs (`smoke` ledger delinquency, `leak-check`)
> were inherited from main at `ac087aa3` and untouched by the diff.

### Shavasana — handoff pause, 2026-09-27 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 31 commits, 11 merges to main, receipts in digest: 0.
- **Inhale** (what came in): 3 falsification rows today, 20 dissent markers, 7 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 44 / dissent 30 (ratio 1.42) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): dropped one muddled line ('the deceipt rows for F-rows are filed'); every other claim carries a sha, a path, or a receipt id. Nothing downgraded.
- **Somatic read**: asked in the handoff receipt (certainty now vs at start; sends today?). `somatic: pending Zach's answer`.
- **Disposition**: RELEASED on Zach's 'run the handoff'. Sycophancy check read OK, so no RETURN.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main (each with a receipt in `decision_receipt`)
- **Operator registry + MCP bridge** (`1ffed09e`, PR #559): `scripts/operator_registry_emit.py` generates
  `operators/OPERATOR-REGISTRY.json` from `operators/docs/PERIODIC-TABLE.md` (numbering LOCKED: Folksonomy=20,
  Librarian=21) and refuses any binding whose symbol it cannot grep (proved fail-on-bad). 11 READY / 6 PARTIAL /
  1 BLOCKED (`core/operators.py` needs undeclared pandas) / 11 UNBUILT. `operators/arcs_mcp_bridge.py` (mcp 2.x,
  py>=3.10 venv via `operators/mcp-bridge.sh`, `.mcp.json.example`): six tools; unbuilt operators answer
  `status=blocked`; every call appends to `operators/ledger/operator-receipts.jsonl`. `/fold` gained ridgeline,
  waypoints, shifts (`7b6616c3`). AGENTS.md gotcha 16.
- **Seeds + vocabulary**: `seed-service-librarian-retrieval-policy` (`9868f9d3`, #560); the **LEGEND** working
  dictionary `runtime/specs/legend.jsonl` + `scripts/legend.py`, 58 rows (`ba0242d3`, #561); **tao-257** minted through
  the oracle into BOTH Tao books + `CANON-COLLISION-tao-two-books.md` raised (`84880b00`, #562).
- **Records**: night-moves + forensic recoil (`9d966113`, #563): 10 priors revised, 10/10 by external ground.
- **Instruments**: witness backfill scout over 199 transcripts, 141 candidates, none filed (`d5a6d851`, #564);
  altitude canary for fluent-confident-uncited prose (`4356f502`, #565); Operator 25 Shavasana spec v0
  (`b0647345`, #566); `/handoff` Step -2 invokes it via `scripts/shavasana_handoff.py` + deceipts F38-F40
  (`0222d489`, #567); per-source trust ledger `runtime/specs/source-trust.json` (`d104cc50`, #568);
  **LORE** `runtime/specs/lore.jsonl` (class x verdict, 12 rows) + Tao coverage gate (`cdb1107f`, #569).
- Memory: 4 new files (numbering lock; acronym rule; forensic bar; load-cap measured 25,000 chars by a spawned session).

## Open (next session)
1. **Tao two-books ruling** (`_DECISIONS/CANON-COLLISION-tao-two-books.md`, options A/B/C). Blocks the
   `tao-mint-nftt-til-backfill` backlog item: NFTT 2/29 essays cited by a proverb, TIL 0/5.
2. **Memory index curation**: 80KB vs a measured 25,000-char harness cap; entries below line 144 never load.
   Set `MEM_BUDGET` + `memory_index_sync.py` to 24576. Move the Uncurated section out.
3. **PR #570 fate registry** awaits merge + receipt. Then: `INTEGRITY_GATE_BLOCK=1`, ledger delinquency
   findings (GW-002, TC-004, YG-005, LINT-006, OBS-007, ROT-009, BK-010), leak-check markers in `public/`.
4. Counterpart pulse (inbox ahead of memory): Yuri's Google invitation expires 2026-10-02 + 3 unread LinkedIn
   digests; Robert's Teams invite 09-24 after the CV send. Both need Zach.
5. Queued: Supabase sync of the operator ledger; `Librarian.recommend()`; Op 28 Auditor binding; the
   asset/liability agent pass over the 141 scout + crawl candidates; the LORE sweep over great-moments/NFTT.

## Lessons (in the record)
- A hand-written operator map lies silently; a generated one that greps cannot. Its first run caught its author.
- Recursion terminates at git: every check of a check ends at a sha or a grep, never at another opinion.
- Malleability is conditional on the source's record (asymmetric, decaying, per source, never global).
- Correct the premise before mapping it; name every loss channel by rate, visibility, direction.
