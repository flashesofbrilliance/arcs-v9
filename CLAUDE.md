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

# Handoff — v3.99.0 (2026-10-06)

> **Job Factory session, third part: the Upside application gauntleted and on main, and ATS-safe companions for
> every tailored resume.** Merged on Zach's asks with receipts: #870 (`1fa411ff`, `2026-10-05--upside-cover-gauntlet-pr870--ZH`)
> and #886 (`d5652d48`, `2026-10-06--ats-companions-all-pr886--ZH`). Oracle handoff=47.

## Shipped + on main
- **#870 Upside Staff FDE bundle:** cover letter READY on `jobs_prose_gate.py` (slop-eval unchecked: API cap), gauntlet.json,
  evidence.jsonl, ex-ante. 6-facet gauntlet fixes: "evaluations designed from the start" was false against git (the eval
  harness `scripts/brief_eval.mts` landed 2026-09-30), now names the real checks; stack row added; Squat "tech lead /
  rebuilt end to end" from the vetted master; Grayscale handoff cut; CTF 20% outcome added.
- **#886 ATS companions:** `scripts/resume_ats_render.py` read only the card layout and silently dropped Experience,
  Education, pillars and OSS on every forge print-base resume. Now reads both layouts (resume-general content unchanged).
  87 new `-ats.html/.pdf`, 86 at 2 pages (vico master 3). Pre-commit kintsugi design gate skips pages carrying the
  renderer's generated ATS header (Zach's call). "leverage" cut from Beacon, Sequence Holdings, Venn.
- iCloud: `ARCS/resumes/ATS/` holds 96 ATS PDFs; per-role folders carry `-ATS.pdf` too.

## Open (next session)
1. **Zach to send:** Upside (confirm the new titles "Forward-deployed engineer and AI builder" / "Founder and engineer"
   first) and Tenex Senior FDE (fill the founder's first name in the note).
2. Upside page-1/page-2 PNG previews are stale (pre-gauntlet); the PDFs are current.
3. API workspace cap still blocks every model route (slop-eval, the 11 shortlist resume cuts) until raised or 2026-11-01.
4. No ATS PDF has been run through a real portal parser; Blacksmith and Vico ATS omit the design-only strengths panel.

## Lessons (in the record)
- A generator's coverage warning is the gate: 50% of words missing meant whole sections were gone, not noise.
- A fix the gauntlet "verified" can still carry a timing claim; check claims about "since when" against git log.

# Handoff — v3.98.0 (2026-10-05)

> **Prod deploys now run `prisma migrate deploy` (production only).** #840 (`942b0f46`) + hotfix #857
> (`f5fab907`), both merged without CI (Actions billing block; Zach's go on #840). Receipts
> `2026-10-05--vercel-migrate-per-service-pr840--ZH`, `--migration-lock-postgres-pr857--ZH`, `--direct-url-redeploy--ZH`.

## Done
- **Root cause:** under `experimentalServices`, Vercel ignores a top-level `buildCommand`; each service uses its own.
  #830's prod log ran plain `npm run build`. Command now lives at `experimentalServices.web.buildCommand`.
- `scripts/vercel-migrate-deploy.sh`: migrates via `DIRECT_URL` (set on arcs-v9 Production by Zach, session pooler
  :5432), else rewrites :6543 to :5432; logs host:port; refuses :6543. Preview logs "skipping migrate deploy".
- **Regression, fixed:** the first real run failed P3019 (`migration_lock.toml` said sqlite). #857 set postgresql.
  Prod deploys #847/#850 errored in between (~10 min); prod kept serving the last READY build.
- Prod `_prisma_migrations` = all 22 `prisma/migrations` by sha256 (incl. the hand-applied brief_share, prep_session_owner).
  Proof log: `migrate target …:5432 · 22 migrations found · No pending migrations to apply`.

## Open (next session)
1. GitHub Actions billing/spending-limit block: no CI job starts on any PR or main (human).
2. `experimentalServices` is deprecated in favour of `services` (needs `root`; not migrated).
3. Two Vercel projects named arcs-care (team + personal `prj_cVMj…`): the personal one caught an env var; delete or relink it.

## Lessons (in the record)
- A wired-but-never-run step hides every latent bug behind it: the first real run surfaced a months-stale lock file.
  Watch the FIRST prod log after enabling any deploy-time step.
- `vercel env ls` names its project in the header line: read it before trusting "it's set".
