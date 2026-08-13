@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
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

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). A full interactive Next.js page exists but was never pushed — recoverable via cherry-pick
from a stale local clone, see `_STATE/snapshot.json` → `observatory.status`.

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

# Handoff — v3.33.0 (2026-08-13)

> **Active pickup point.** The ARCS-private half of the germinate OSS build session. germinate
> (the open MIT toolkit at `~/germinate`) is built/committed-local but NOT published — owner-gated.
> This session canonized what stays *private* to ARCS. PR #136 MERGED to `main`.

## Headline: the Tao of ARCS is canon — dormant seed vs animating spark, and the meter runs only on the spark

The germinate build forced the boundary question: if the seed bank is open MIT, what is ARCS?
The genesis seed `adam == atom` answers it, and it's now canon.

**Canonized (PR #136, merged `2a6d2ea`):**
- **ADR-053 — The Tao of ARCS.** A seed is *dormant potential energy* (engineered to survive harsh
  conditions; never garbage-collect on staleness — dormancy is the feature). ARCS is the **vox
  animus** — the spark that converts potential→kinetic via *ripeness judgment* at Kairos. The
  open/private boundary is **one seam, four faces**: bank/spark · public-method/private-rosetta ·
  dormant/animating · free-to-hold/metered-to-fire. The moat is the spark, so open-sourcing the
  bank surrenders nothing. Y=GREEN.
- **ADR-054 — Free to hold, metered to fire.** Free forever (in germinate): mint/plant/water/hold/
  mechanical-sprout/manifest/handoff. Metered (the gas, ARCS-side): ripeness judgment · Kairos
  activation · rosetta-primed synthesis. **Bill per activation** (one vox-animus firing) — not per
  seed/seat/GB. Token fork **DECIDED metaphorical-now** (credits + usage-metered billing); literal
  on-chain deferred until the blockchain registry + hash-chaining exist AND a cross-party provenance
  need is shown. Y=YELLOW — willingness-to-pay for the ride is unvalidated.
- **`_CANON/Tao-of-ARCS.md`** (doctrine, registered in `_CANON/index.md`) + proverb **tao-247**.
- **`_STATE/2026-08-13-activation-service-kairos-sketch.md`** — kairos (public-good #2, "conditional
  cron") = the open socket ("could it fire"); ARCS = the private current ("should it, now, for you").
  Crispness rule: kairos runs fully without ARCS priors; ripeness is a pluggable metered layer on top.

**Boundary discipline held:** nothing was written to `~/germinate`. All ARCS doctrine, the rosetta,
and ripeness priors live only in arcs-v9 (ADR-053 encodes the no-inline rule).

## Also (housekeeping)
- `_DECISIONS/index.json`: backfilled ADR-050/051/052 (missing from a prior session) + registered 053/054.
- Lattice advanced **44→51** via `scripts/lattice_drift_check.py --regenerate` (mechanical countable;
  judgment layer left human-owned per ADR-052). Next session's session-start hook should read drift-clean.

## Captured
- **ADR-053 / ADR-054** (`_DECISIONS/`). **DEWY** — `_STATE/2026-08-13-session-decisions.dewy.json` (2).
- **Memories** — orphans indexed into `MEMORY.md`: [[seed-tao-of-arcs-dormant-potential-vox-animus]]
  (genesis, now PROMOTED), [[seed-monetization-free-to-hold-metered-to-fire]] (PROMOTED). Both seed
  files stamped PROMOTED 2026-08-13 so they don't re-promote.

## Next / backlog (designed, not built)
- The **ARCS activation service** (vox animus / ripeness judgment) and **kairos** (public-good #2) —
  boundary sketched, interfaces are the open questions in the sketch file.
- **Do NOT publish germinate** (or any public repo) without explicit owner authorization.
- ADR-054 care-note: validate WTP for *the ride*, not the bank, before hardening prices / billing infra.

## Blocking
NONE.

## Deploy note
This session committed on the worktree branch `claude/elated-hawking-c08b93` and merged via PR #136
(GitHub merge commit). Canon/ADR/state changes only — no deploy-affecting code. `--no-verify` used on
push per repo convention.

---

# Handoff — v3.32.0 (2026-08-11)

> **Active pickup point.** Concurrent with the v3.31.0 `/witness` session (kept live below). This
> session shipped the public federated family + the drift-receipt system + the inchworm auditor.

## Headline: the family is public on arcs.care, and drift now becomes receipts

**Live, tripwire-clean, E2E-verified (15/15):** `playground.arcs.care` (hub) + 4 performers as sub-pages
(`/12d-orbital · /knowledge-lattice · /alexandria · /moire`) + `monolith.arcs.care` (3 heads + Moiré
filter; meta-audit head dropped for public). Joins the sibling's `forge`/`forge-cut`. Two-layer
architecture (**ADR-050**): SSOT truth (meta-audit · Tao · status · registry) ↔ air-gap (the tripwire) ↔
prospect-safe public faces.

**Drift-receipt system (ADR-051), on main:** PR-time `scripts/tripwire.sh` + `.github/workflows/family-tripwire.yml`
(gates the diff); deploy-time `tests/family.spec.ts` in `deploy-verify.yml` (fail → rollback + Issue);
`.github/pull_request_template.md` + `docs/PROMOTION.md`. It caught its first receipt: jargon in the forge pages.

**Inchworm auditor (ADR-052):** `scripts/lattice_drift_check.py` wired to both hooks — OPEN
(`session-start`) orients/receipts, CLOSE (`pre-compact`) advances/regenerates countables idempotently.
Gave the orphaned knowledge-lattice an owner; fixed stale "32 ADRs" → 44 through SSOT → re-embed → redeploy
→ live-verified.

## Also built
- **Invariant envelope** (`_STATE/schema.md`) + **artifact registry** (`_STATE/artifact-registry.jsonl`, 52 rows).
  Tao extracted to `_CANON/tao-proverbs.jsonl` (now **246**; +5 minted from this session's ADRs, tao-242..246).
  Full-staff gauntlet over the 5 performers (`_INBOX/performer-gauntlet-*`). Journey-map souvenir:
  https://claude.ai/code/artifact/bf7867b9-01ee-4dc1-88f1-809218a99739

## Captured
- **ADR-050/051/052** (`_DECISIONS/`). **DEWY** — `_STATE/2026-08-11-session-decisions.dewy.json` (3).
  **Memories** — [[drift-receipt-loop-and-inchworm]], [[per-tenant-field-truth-inward-client-facing]].

## Next / backlog (designed, not built)
- **Per-tenant field-truth pages** — client-facing counterpart to the internal meta-audit.
- **HITL calendar-recoil loop** — no Ahmed/Yuri/Rayan meetings booked (checked); close loops = send built
  Ahmed/Rayan seeds / await Yuri.
- Branch protection: `gh` command in `docs/PROMOTION.md` (needs admin + first PR run of the check).

## Blocking
NONE.

## Deploy note
Pushes from `main-wt2`, `--no-verify`. arcs.care subdomains route via `arcs-v9` project `next.config.ts`
host rewrites + `vercel domains add <sub> --scope arcs-care`. Write-lock (`rev-list HEAD..origin/main` == 0)
before commit — concurrent sibling on main. **ADR numbering drifts across sessions: verify the max on main
before assigning (this session's ADRs slid 045→050 after a live check).**

> _v3.31.0 (`/witness`) relocated to `_ARCHIVE/handoffs.md` on 2026-08-13._
