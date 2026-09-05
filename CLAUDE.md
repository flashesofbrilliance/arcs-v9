@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
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

# Handoff — v3.52.0 (2026-09-02)

> **Blacksmith application + recruiter-enablement session.** Built and shipped the full Blacksmith
> candidate bundle, then a recruiter-facing enablement system for Amy at RecruitHaus. Everything live
> is verified. Worktree `claude/blacksmith-staff-engineer-role-7266bf`. Long session, converged under
> the 5-hour limit.

## Shipped + live (verified)
- **blacksmith.arcs.care**: hero **ship-clock frozen to `v0 · 1h 22m`** (git-true; live counter was
  undercutting the flex), **The Forge** with **6 between-stage CI gates** (ADR-068 print schedule;
  final gate names the real CI: lint + next build + air-gap-leak-check-as-test + security scan +
  auto-rollback, 7 workflows), **domain-map rebuilt as a connection visual**, cover security nod,
  "director's cut"→"the forge". Air-gap test retuned (recruiter credit allowed; founders hard-gated,
  added Aditya/Maru).
- **status/build false-zero bug fixed** — degraded `/api/pulse` overwrote the curated floor with
  0/0/0/1 over a full board; guard + curated fallback + honest stamp. FM banked
  ([[live-counts-overwrite-static-floor-with-false-zeros]]).
- **recruithaus.arcs.care** LIVE — public candidate-positioning page (two-hires-in-one, role pills,
  why-multi-threaded, compounding). Air-gap clean (leak=0; orphan CSS stripped). proxy.ts SUBDOMAIN_MAP
  + `/_vercel` exclusion (analytics fix for all subdomain hosts).
- **Kintsugi receipt** `_STATE/2026-09-02-blacksmith-kintsugi.json` (healthy + golden-seam ledger).

## Private (`_ARTIFACTS/resume-blacksmith/`, not served)
- `counterpart-application-forge.blueprint.md` (parameterized factory), `tear-sheet-amy.html`+`.pdf`
  (**gated ammo**: comp logic, 3-lens battle cards w/ nested 1st/2nd/3rd-order objection handling,
  best/base/worst, ARCS circuit breakers; founders by lens not name), `recruiter-recoil-report.html/.md`,
  `dyor-blacksmith-recon.md`, `design-critique-personas.md`, `founder-gauntlet.md`, `intel-bundle.md`.
- Pattern banked: [[recruiter-enablement-two-tier-tear-sheet]].

## Open (next session)
1. **Gate + host the ammo tier** + a `/resume`-style PDF-download viewer behind a passcode
   (RECOIL_PASSWORD cookie retired; recoil now Auth.js/admin-email = not Amy-accessible; no qpdf/pikepdf
   for PDF encryption). 2. **Impeccable audit/polish/refine/distill pass** on recruithaus (user queued
   it "after deploy"). 3. **Amy-facing recoil recap** (warm call-recap, not the reverse-listening).
   4. **Named founder battle cards** — offline file only, never hosted. 5. `/consolidate-memory` (index
   21KB > 17KB). 6. Deep-recon vs raw Granola transcript `1831d31e` to re-verify every attribution
   before any ammo is hosted.

## Candidates to mint via oracle (do NOT infer numbers)
- **ADR:** two-tier counterpart-artifact doctrine (pitch open / ammo gated; founders-by-lens; comp-talk
  never on open web). **ADR:** battle-cards-as-objection-filters + nested N-order handling.
- **Seed:** recruiter-enablement tear-sheet as a productizable surface of the counterpart-forge.
- **DEWY:** session-decisions receipt still owed (kintsugi receipt already appended).

> _v3.51.0 / v3.49.0 (Möbius) to relocate to `_ARCHIVE/handoffs.md` next session; kept 3 live under the time limit._

> _v3.50.0 (canon-governance) + v3.49.0 (Möbius) relocated to `_ARCHIVE/handoffs.md` on 2026-09-04; v3.52.0 kept live one more cycle._
