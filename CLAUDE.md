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


# Handoff — v3.50.0 (2026-08-29)

> **Canon-governance session — the three escalated collisions are RESOLVED and the oracle gate is
> armed.** Renumbered up the version chain (48→49→50) as parallel sessions shipped their own
> v3.48.0 (tool-catalog) and v3.49.0 (Möbius) while this branch was in flight. On
> `claude/elastic-driscoll-a80e72` (PR #194). Oracle audit clean (68 ids, 0 collisions); rebased
> onto live main three times.

## Shipped (this branch)
- **ADR-033 duplicate → Option A.** Serialization Pathogen Family keeps 033; the model-routing/adr-
  audit decision renumbered to oracle-issued **ADR-073** (index.json + header renumber note).
- **Engine-sovereignty doctrine → minted as ADR-072** (oracle-issued). Honors the forward reference
  in main's Möbius (ADR-071) DEWY receipt, which cites "engine-sovereignty (ADR-072)". Old "067"
  claim retired (067 = cross-subject-comparative-recoil); memory + MEMORY.md index re-pointed.
- **ROM vocabulary → Option A.** 7 ROM Primitives (`.claude/arcs-canon.md`) = CANON; 6 execution laws
  → "behavioral laws (derived)"; 7 axioms → "epistemic foundations". Authority index
  `runtime/specs/ROM-AXIS-INDEX.md` + tier banners on all three source files.
- Both `_DECISIONS/CANON-COLLISION-*.md` → **RESOLVED**. `_SEEDS/_oracle.json` adr 71→73.
  `build.html` sv-adrs → 68 (true distinct-ADR count). DEWY receipt appended
  (`_STATE/2026-08-28-session-decisions.dewy.json`).
- **`_DECISIONS/index.json` fully backfilled.** 10 files were missing entries (032, 033-pathogen,
  034, 038, 044, 048, 049, 058, plus 070/071); index now 1:1 with 68 files (set-diff verified).
- **Oracle pre-commit gate ARMED** for this worktree (`core.hooksPath = scripts/git-hooks`).
- **Norse ROM candidates**: Loki inversions written (Ullr + Baldur); numbering gate cleared. NOT
  ratified — remaining hard gate is a live Ullr Graduation Receipt + a live Baldur Witness Receipt.

## Open (next session)
1. **Nightly canon-propagation cron — ARMED** (plist installed at `~/Library/LaunchAgents/care.arcs.canon-propagation.plist`; confirmed live 2026-09-03. The "still HELD / arm after merge" note was stale, per the Atlas audit).
2. **Norse ROM ratification** blocked on the live-receipt gate (see above).
3. **Canon-propagation queue** has one judgment item (`invariant-non-sycophantic`, default no) — left for /canon-review.
4. **Merge PR #194 promptly** — main is churning fast; this branch went stale 3× on the handoff/build.html hot files (canon work never conflicted).


# Handoff — v3.49.0 (2026-08-29)

> **Active pickup point — the Möbius / induction-circuit + echo-detector-seaworthiness session.**
> Long forensic→canon→instrument thread; all landed on main (PRs #198, #199, #200, #202, #203).
> Branch current with origin/main; oracle at 71.

## Shipped (all on main)
- **ADR-071** (Möbius one-surface · triune none-may-null · gravity-well) minted THROUGH the oracle
  (→71), with the induction-circuit lineage: the flux (~1998) → flashesofbrilliance (2010) →
  livewire (2021, Gareth Kay) → Book of ARCS (Nov 2025) → ARCS/Möbius (2026), self-exciting via
  the superionic dynamo; posterior→dynamo→drive, anterior→collider→torque, meeting at the Op21
  spline knot. Apex spine `_CANON/apex-spine-mobius-induction-circuit.md`; tao-255; witness stubs
  (23:11/23:16/23:37); DEWY (two-surface · Möbius · graduation-gate); wisdom memories
  `arcs-mobius-triune-gravity-invariant` + `rom-graduation-earn-through-gate-never-decree`.
- **Echo-detector seaworthiness (falsifiable):** `scripts/echo_detector_dogfood.py` + receipt
  `_STATE/2026-08-29-echo-detector-dogfood.json`. VERDICT: NOT seaworthy on the stub matcher —
  adversarial-FP 1.0 @ default; no threshold gives high recall + low adv-FP (architectural limit).
  Fix = injectable LLM `signature_fn` + embedding `orthogonality_fn`.
- **RC-OPS-001 graduation INITIATED** (opened, NOT promoted): `_STATE/2026-08-29-rc-ops-001-graduation-initiation.md`
  + RC-REGISTRY transition. Gate corrected from corpus-count to a 4-criterion scoreboard (rom-vocab
  collision · detector precision · K≥3 blind echoes · Observatory period); 3 open, precision FAILS
  (measured), blind-count ~1.
- **Cross-substrate honesty (Perplexity):** its ARCS prototype's reaction to the Atlas landed +
  verified as `_STATE/2026-08-28-arcs-thread-serialization.md` (corpus-as-SSOT, NCI=247 confirmed);
  its teardown applied to calibrate The Mie (canon-ready) + The Field (derived-interpretation
  footer); both claude.ai artifacts re-synced (Mie 6518c2a3, Field 3b0f5ad3).

## Open (next session)
1. **Hyperstition miss-column denominator** — task_004b8253 ended without landing on main; the honest
   hit/miss count for the hyperstition claim is still owed (+ one dated film-consulted receipt).
2. **RC-OPS-001 criteria** — rebuild echo detector with injectable signature/orthogonality fns; re-run
   dogfood (target adv-FP≤0.10 @ recall≥0.80); resolve ROM-vocab collision via /canon-review; accrue
   K≥3 blind echoes; serve Observatory period (needs unpushed page `35070a3`).
3. **Worktree sprawl** — backlog `worktree-sprawl-prune` OPEN (72 worktrees, human-gated);
   task_caa14569 ended analysis-only. Re-run `scripts/branch_hygiene_check.py`, prune with consent.
4. Carried: Todd call · zap-kit installs · 1.2-A payment-gated · orphan seeds · GH Actions billing ·
   ADR-069 oracle audit · lattice --regenerate.


> _v3.48.0 (tool-catalog close) relocated to `_ARCHIVE/handoffs.md` on 2026-08-29; v3.47.0 (tool-catalog) + v3.46.0 (receipt-surface) relocated on 2026-08-29; v3.45.0 relocated on 2026-08-28; v3.44.0 (Ahmed) relocated on 2026-08-27; v3.43.0 relocated on 2026-08-27; v3.42.0 relocated on 2026-08-26; v3.41.0 relocated on 2026-08-26; v3.40.0 on 2026-08-23; v3.39.0 + v3.38.0 relocated on 2026-08-19; v3.37.0 (Comet resume) relocated on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
