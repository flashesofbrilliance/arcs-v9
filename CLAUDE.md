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

# Handoff — v3.73.0 (2026-10-04)

> **Stopped-light research → ARCS design rules, a nested skill, an oracle fix, and an NFTT essay with a
> go-deeper companion.** Two PRs merged on Zach's explicit go: #683 (`5d64551`) and #686 (`44b80d1`);
> receipts `2026-10-03--stopped-light-echo-scan-oracle-nftt-pr683--ZH` and
> `2026-10-04--nftt-research-companion-tao284-pr686--ZH`. Both served from the Vercel deployment URL;
> the pretty good.arcs.care routes are unconfirmed (the cloud egress proxy blocks good.arcs.care).


### Shavasana — handoff pause, 2026-10-04 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main, receipts in digest: no digest file. (Script counts 2026-10-04 UTC only; the session spanned 2026-10-03/04 with 8 session commits, 2 merges #683 #686, 2 receipts.)
- **Inhale** (what came in): 0 falsification rows today, 3 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale) on the 10-04 window; breathing across the full session.
- **Sycophancy check**: agreement 4 / dissent 3 (ratio 1.0) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): "live-verified" narrowed to "served from the deployment URL"; the pretty good.arcs.care routes stay unconfirmed (egress block). "Cheapest high-value fix" downgraded to "a one-line hook change". Nothing dropped.
- **Somatic read**: not asked.
- **Disposition**: RELEASED on Zach's '/handoff'.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **Research:** `_PATTERNS/2026-10-03-stopped-light-quantum-memory-isomorphisms.md`: claim check of a
  LinkedIn post on Hau's stopped light, 2026 state of the art, 15 isomorphisms labelled MECHANISM or
  METAPHOR, 5 inventions each with a pre-registered kill condition. Top 3 in the induced backlog
  (`freshness-zeno-ceiling`, `echo-scheduled-receipts`, `memory-seven-axis-scorecard`).
- **Skill:** `/echo-scan` (`.claude/skills/echo-scan/`), the working form of ROM primitive 5, with a
  nested `claim-check` module (`references/claim-check.md`) also callable standalone. A fresh-agent run
  of the module found 7 gaps and a wrong expected verdict in its own eval; all fixed in `c04c21f`.
- **Oracle fix (`4583555`):** `scripts/oracle.py` matched only argv[0..1], so `next seed --dry-run`
  allocated for real and stamped a pulse beat. Now strict parse (unknown flag, extra arg, missing value
  -> exit 2), a real `next <ns> --dry-run`, and `--self-test` 12/12 wired into pre-commit.
- **NFTT:** "Light at Thirty-Eight Miles an Hour" (the session's own story, including the false herald it
  refused to commit) + companion `/research` page (go-deeper, tao-waiver as a companion) + `tao-284`.
- Shareable artifact of the research: https://claude.ai/artifact/SgSCnSBsyxjxzUQ3xP1tn8 (private).

## Open (next session)
1. Seeds planted this handoff (candidate): `seed-gate-hookspath-bootstrap`, `seed-pattern-strict-cli-args`,
   `seed-skill-echo-scan`. The first is a one-line hook change: nothing sets `core.hooksPath`, so
   every fresh clone skips the whole pre-commit chain.
2. Suggested tasks queued as cards: resync `scripts/nftt_index_build.mjs` (8 posts stale; running it drops
   posts), and Tao backfill for the 4 NFTT posts still uncovered.
3. `/echo-scan` full with/without benchmark not run (only claim-check mode exercised).
4. Backlog inventions untouched; each carries its kill condition.

## Lessons (in the record)
- A preview flag a tool does not recognize turns a look into a touch. 61 of 63 `scripts/*.py` that read
  argv parse it by hand (38 of those write files); the oracle was one instance of the class.
- A herald must come from the write it reports. The pulse beat from a reverted allocation was refused;
  the beat from the real tao-284 allocation was committed.
- `core.hooksPath` unset in this clone: commits `43a3ff9` and `248036c` ran no gates, and the essay
  shipped without the tao-coverage check until `08233e4`.

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
