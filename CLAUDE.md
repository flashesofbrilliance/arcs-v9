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

# Handoff — v3.60.0 (2026-09-11)

> **720-degree brand-coherence session** (worktree `recursing-brattain-190758`, branch
> `claude/recursing-brattain-190758`). Resumed the parked pitch-us/brand arc; answered the Ahmed
> heuristics question, ran a live 6-surface coherence audit, blessed one flag, wired 4 of 6 faces.

## Shipped (merged to main)
- **Empty meta descriptions filled** on resume.arcs.care + status.arcs.care (PR #404, live). These
  shipped blank, so machines/unfurls/LLMs saw nothing (the "720 serialized-POV" hole). resume's
  h1/lede already render client-side, so only the machine-read meta was the real gap.
- **Duality backlinks** on build.arcs.care + good.arcs.care footers (PR #405): each now names the
  operator and links back to the consulting front door. Cleared one prose em-dash in build.html
  (data-placeholder `—` glyphs left as the legitimate UI idiom).
- **Pre-compaction:** SentiLink altitude-descent reorder (PR #389, exec→surgical, ask-first).
- Banked pickups + pitch bundles to `_ARTIFACTS/` (720-brand-coherence-pickup, pitch-polish-pickup,
  sentilink/mercury bundles).

## The blessed flag (SSOT, all surfaces echo)
**"Proof over promises, one operator accountable end to end."** The positioning is a coherent DUALITY
(independent consulting sprints ⇄ dedicated in-house), one operator + one method (ARCS). Building-in-
public = pre-empt the "consultant who does not ship" assumption; anti-consultant-who-ships, WITHOUT
"FDE" or leaning on "engineer". zachharris.xyz is the singular front door + identity SSOT; others echo
and backlink to it. Full context: memory [[zach-personal-brand-and-job-search-system]].

## Open (next session — pickup: `_ARTIFACTS/720-brand-coherence-pickup.md`)
1. **zachharris.xyz (separate static repo, NOT this worktree)** — fill empty meta + Case-Studies link
   to build.arcs.care (public proof, NOT prl). Exact paste-ready copy in the pickup. Run its `npm test`.
2. **LinkedIn** — 6th face, unreachable by tools; headline still "Product". Get Zach's headline+About,
   fold into the flag grammar.
3. **Dropped on purpose:** prl provenance footer (client-confidential, not a billboard).
- Ahmed's FORMAL delivery heuristics ("the Ahmed order": verdict → 3 reasons → 3 Q+A → tasks →
  evidence-behind-disclosure → depth-linked; + density budget + legibility gate) live at
  `_ARTIFACTS/ahmed-feedback-plan-2026-09-03.md` (in worktree `arcs-demo-ahmed-b0db74`). The yardstick.

# Handoff — v3.61.0 (2026-09-13)

> **Bridge index + Triune convergence session** (worktree `determined-lovelace-de940d`; every
> change landed via PR to `main`, HEAD `ad4f084f`). Every merge receipted in `decision_receipt`
> (8 rows, ids `2026-09-11--bridge-employer-index-ingest--ZH` … `2026-09-13--receipt-enums-and-receipt-cli-seed-pr421--ZH`).

## Shipped + verified
- **Bridge employer-quality index (job-search Thread 1)** — 403 verbatim names from 5 published lists
  → 133 public GH/Ashby/Lever boards (18 slug collisions dropped by eyeball) → 7,593 reqs → **578
  winnable rows live on jobs.arcs.care** as `bridge_scan` UNSCORED (Thread 2 scores). Tool
  `scripts/bridge_index_scan.py` (probe/verify/pull/ingest, `--retry-misses`; ingest never resets a
  scored row). 256 unresolved = Workday-class, re-probed in full, 0 recovered. PR #415.
  Index + funnel: `_STATE/job-search/employer-index/README.md`.
- **Triune Stream A** — 74 worktrees swept by patch-id (`git cherry`), not ahead-count: 14 prunable ·
  8 ghost-history · 33 unmerged-stale · 18 active (`_STATE/worktree-audit-2026-09-11.md`). The 3
  ADR-collision hold branches renumbered via oracle and merged: ADR-078 exogenous-forge (#409),
  ADR-079 refusal-to-overclaim (#410), ADR-080/081 Tao proverb system + ADR-041 (#413); oracle 77→81 (#408).
- **Stream B** — operators composition boundary on main (#407). **Stream C** — `scripts/scout_dossier_ingest.py`
  gates `_INBOX/evidence/` dossiers against `role-dossier-schema.json`; refused Parloa (missing
  `extraction_risk`), posted Blacksmith + TrueSeek as `perplexity_scout`. Anchor `_STATE/convergence.json`
  on `fresh-starts` at beat 6 (JTBD-002/003 LANDED, JTBD-007 = Parloa re-emit owed by Perplexity).
- **Seed bank clean** — 3 candidates planted (worktree-audit-by-patch-id, bridge-employer-index,
  scout-dossier-intake-gate) + decision-receipt-cli; 2 orphans receipted; 4 broken locals fixed
  (`local` = one path, prose → `local_note`). `seedbank_drift_check`: OK · 41 seeds · 80 receipts.
- **AGENTS.md** receipt rule now lists the `decision_receipt` CHECK enums (horizon/stakes/mode).
- **Memory** — wrap trio retired into `text-wrapping-defect-class-and-gate` (Zach-approved); abs-path
  risk folded into commit-to-main; +`bsd-sed-no-word-boundary`, +`shared-anchor-append-refetch-before-write`;
  index 17.2 KB under budget, 244 files, 0 dangling.

## Lessons booked
- BSD `sed` has no `\b`: a 375-reference renumber "ran clean" and changed nothing. Python regex + leftover count.
- Shared anchors collide on ids, not bytes: Hermes and I both appended JTBD-005/006 minutes apart. Re-fetch, read ids, then allocate.
- The naive `ahead` count is not an audit; patch-id showed 397 real off-main commits, not ~11k.

## Open (next session)
1. **Thread 2 scoring** of the 578 `bridge_scan` rows (rubric v1.0 lives on `claude/bridge-scan-rubric`); then the H1–H4 denominator reconcile in `_STATE/job-search/hypothesis-ledger.md`.
2. **Worktree pruning** — human call on 14 MERGED-prunable + the 3 now-landed hold worktrees; bundle first (`cruft-sweep`).
3. **Workday adapter** for the 256 unresolved bridge employers (seed `bridge-employer-index`).
4. **Parloa dossier re-emit** (JTBD-007, Perplexity) → `scout_dossier_ingest.py post`.
5. Outcome-capture keel (2/247) still the P1 gap; untouched this session.

