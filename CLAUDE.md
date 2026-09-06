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

# Handoff — v3.54.0 (2026-09-06)

> **Open-loops session.** `/handoff-pickup` triage, then three loops closed on branch
> `claude/open-loops-handoff-cvgjxd` (NOT yet merged to main — open the PR): Phase 0 integrity gate,
> ADR-020 Tribune steps 1-2, ADR-006 repo-side half. Zach closed loop "sean-wing" by decision.

## Shipped (on the branch)
- **`scripts/integrity_gate.py`** (ADR-075 GATE organ): every ADR / commit sha / repo path a record
  cites must exist on `origin/main`. OK / WARN (index drift, unknown sha, gitignored) / FAIL (missing
  ADR, unmerged sha, vapor path). `--staged` for the hook (staged files count as existing). Wired into
  `scripts/git-hooks/pre-commit` as **warn-then-block**: warns by default, `INTEGRITY_GATE_BLOCK=1`
  enforces. First run found real drift: ADR-042 gap, `runtime/specs/routing-manifest.json` vapor,
  **9 retired `public/*.html` briefs still listed in `_STATE/snapshot.json` `ui_artifacts`** (labella,
  peter, token, chase-intro, chris-intro, cj-brief, fanatics, growth-intel, kelly-interview).
  CBA ledger row 0 filled (~0.5 hr actual vs 1 est).
- **ADR-020 Tribune** steps 1-2: `POST/GET /api/tribune` (auth+owner, rate limit, lazy per-phase
  upsert, Proactive silent below threshold, Posterior needs an Outcome, baton write), `Tribune` model +
  `Receipt.batonId` + migration `20260906000000_tribune`, `src/lib/tribune.ts` pure helpers (18 unit
  assertions; compiled via `npx tsc` to scratch, no tsx in repo). `npm run build` green.
- **ADR-006** repo half: `.github/workflows/preview-db-migrate.yml` — migrations-from-zero on a
  Postgres 17 service + `prisma migrate diff --exit-code` on every `prisma/**` PR; `migrate deploy` to
  `PREVIEW_DATABASE_URL` when the secret exists. ADR-006 amended (live ref is `xbbpiryokswwvcrcutge`,
  not the INACTIVE `owdiiy…` the connector sees; branch ~$0.0134/hr on the visible org).

## Open (next session)
1. **Open + merge the PR** for this branch; then run `INTEGRITY_GATE_BLOCK=1` for a week before flipping
   the hook default. Migration `tribune` applies on the Vercel deploy path (`migrate deploy`); verify.
2. **ADR-006 dashboard half (Zach, spend):** confirm branch price on the live org, enable Branching on
   `xbbpiryokswwvcrcutge`, set `PREVIEW_DATABASE_URL` in GitHub secrets.
3. **Tribune step 6:** panel on receipt detail (SIMPLE = 1 line/phase); persist `driftState` on Receipt
   (topology is the proxy today); fire Posterior from the Outcome handler when it exists.
4. **Snapshot hygiene:** prune the 9 retired briefs from `ui_artifacts`; refresh `git.head_sha` after merge.
5. Still Zach-gated: Desk shape brief "go" (`_SPECS/desk-shape-brief-v1.md`), tao-backfill-066-067,
   orphan-seeds, six PRL Zapier tasks, Todd's nod, gh-actions-billing, worktree prune.
6. Unclaimed trail: worktree `linkedin-alerts-scraper-a97535` (Mac, merged as PR #293) never ran `/handoff`.

# Handoff — v3.53.0 (2026-09-04)

> **The Reading Room session: the Almanac, the library taxonomy, ADR-075, and the locked build plan.**
> Started as Blacksmith polish plus a Google (growth-ai) family stand-up; became the corpus-metabolism
> architecture. Worktree `claude/blacksmith-staff-engineer-role-7266bf`. Everything on main. Oracle at 75.

## Shipped (all on main)
- **growth-ai.arcs.care family LIVE**: landing + /forge + /resume, Zach's real resume/cover/ATS PDFs
  (2pp/448KB, not the 5pp render), air-gap clean (referrer off-page, employer named once), persona-gauntlet
  hardened then realigned to "production" per the canonical docs. Blueprint run: ~40 min to standup, ~2h
  to hardened. `tests/growth-ai.spec.ts` added. SEND stays human.
- **recruithaus ammo tier gated + live** at `/ammo`: passcode `RECRUITHAUS_AMMO_PASSWORD` (Vercel env),
  SHA-256 httpOnly cookie, host-independent gate in `src/proxy.ts` (closes the app.arcs.care/<file>
  bypass), `src/lib/ammo-gate.ts` + `/api/recruithaus/unlock`. Mobile PDF panel fixed.
- **Blacksmith polish**: nav brand -> universal ARCS Field OS wordmark (also good/build/status), domain-map
  slider glitch -> 2-col table (+blueprint note), hero left-edge aligned (.hero padding), lede spans the
  lane (max-width:none, the 660px mode-4 bug), pill "Code as Receipts Era", build.html tofu banners removed,
  growth-ai generic favicon (rewrite excludes .ico).
- **The Almanac** (`scripts/research_render.py` -> `_ARTIFACTS/atlas/atlas-almanac.html`): 264 nodes,
  full-temporal Apr->Sep, every node epoch-tagged (4 digests re-curated by Curator agents; Skeptics
  correctly REFUSED to author). Read through the Reader at 3 altitudes (Skim/Scan/Trenches); two-shelf
  Required Reading (Foundational by canon + Load-bearing by in-degree: in-degree structurally cannot
  surface foundations); dataviz-validated palette; per-row self-contained export. LOCAL only.
- **ADR-075 The Metabolic Router**: witnessed live -> DEWY -> ADR -> wisdom in one session (oracle-minted
  75; `_STATE/witness/2026-09-04.jsonl` promoted, `_STATE/2026-09-04-session-decisions.dewy.json`). Mechanical
  fan-out is automatable, judgment never; integrity gate = every cited ADR/commit/script must exist on
  origin/main. Specs: `_SPECS/metabolic-router-v1.md`, `_ARTIFACTS/atlas/cache-manifest.spec.md`.
- **Locked build plan** `_SPECS/reading-room-build-plan-v1.md`: spine first (Desk + Reader + cache),
  tenants cheap (Concordance/Chronicle/Lexicon), token-savings-bank levers per phase, CBA ledger seeded.
  Library taxonomy: Alexandria = index, Atlas = map (space), Almanac = dated state (time), missing =
  Concordance, Chronicle, Lexicon, the Desk (intent router). Public room = lawful projections of private.
- **Drift swept**: ADR-074 into index.json + oracle 73->74; 2 stale CLAUDE.md claims (Observatory IS on
  main; canon-cron IS armed). False "ADR-075"/"ADR-042" claims de-claimed in the memory index + the
  legibility-gate memory (specified, not wired). Memory index compacted to 18.2KB (~0.8KB over target).

## Open (next session)
1. **Phase 0 integrity gate** `scripts/integrity_gate.py` (cites exist on origin/main): build first, zero
   judgment, then wire into pre-commit.
2. **The Desk**: Stage 1 shape brief presented as a compact confirmation (job / audience / one thing /
   direction / anti-goals / open decisions: route name `/library` vs `/reading-room`, freshness on the
   front door). Awaiting Zach's one correction or "go", then polish -> `/dual-bar-raiser` -> brand-manager
   persona gauntlet -> kintsugi -> build (admin-gated, reuse the `/recoil` Auth.js + ADMIN_EMAILS gate).
3. **Loop locked until complete**: Desk -> Almanac wired -> Concordance -> Chronicle -> Lexicon.
4. Two clean AGENTS.md fixes queued: `RECOIL_PASSWORD` row is stale (retired -> Auth.js/ADMIN_EMAILS);
   operators census is wrong (recounted 2026-09-04: 52 top-level .py, 52 .py total, 62 tracked, 22,171
   LOC). Judgment calls for Zach: `_CANON/index.md` "Book II Complete I-VI" self-contradiction (Part IV
   deleted); `fanatics.arcs.care` routes to a missing file (live 308).
5. MEMORY.md one more trim pass; router v1 wiring after the spine; growth-ai send to Yuri stays human.

## Minted / receipts / memories
- ADR-075 (oracle). Witness stub promoted=ADR-075. DEWY receipt 2026-09-04. Memories:
  `metabolic-router-mechanical-judgment-split`, `proactive-spec-jtbd-reverse-lookup-flag`,
  `research-render-three-altitude-delivery-grammar`; `recruiter-enablement-two-tier-tear-sheet` updated
  (gate LIVE). CBA baseline lesson: match agent role to job class (Skeptic verifies, Curator authors).

> _v3.52.0 relocated to `_ARCHIVE/handoffs.md` on 2026-09-06._
