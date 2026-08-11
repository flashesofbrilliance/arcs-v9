# Basin Distiller — Proof Epoch (2026-08-11)

**What this is.** First run of the ratcheting attractor-basin distiller (a chief-of-staff Workflow:
6 blind multi-modal readers → density-condense → adversarial defensibility-verify → basin-floor synth).
Scope: ARCS canon/corpus + arcs-v9 6-month git. This file is the **residue deposit** — the run's dense∩defensible
floor **plus its negative results** — so no future run (or cheap-model executor) re-buys this learning.
Method + principle: [[tool-fit-marker-convention]], [[throwaway-context-not-throwaway-learning]], [[prepaid-reflexes-tier-descent]].

**Run stats.** 14 agents, 0 errors, 851,902 tokens, ~6m52s. 61 raw particulates → 6 candidates → **6 survivors, 0 refuted**.
Two structural spines emerged: a **governance layer** (ADR-032 zero-trust · ADR-033 serialization-pathogen family ·
ADR-035 commit-NCI — all ratified 2026-07-19) and a **product/trust layer** (app-level user isolation + two-tier no-write
trust contract), with the **counterpart-forge pipeline** as the dominant operational activity above both.

## Basin floor (ranked; density / defensibility)

1. **Recoil/forge counterpart pipeline** (92 / CONFIRMED) — per-counterpart SSOT → gauntlet ladder → air-gapped internal
   war-room + sanitized external suite, hardened by adversarial gauntlet + heal/kintsugi pre-send. Anchors: `runtime/recoil/generated/`=56 SSOTs; `git log heal(`=8 (all Yuri-family); `.claude/workflows/counterpart-gauntlet.js` + `.claude/skills/forge/SKILL.md` (9-phase); CLAUDE.md v3.29.0. *Drift is conservative — true footprint 138 recoil commits, understated as 98.*
2. **Serialization-pathogen family** (82 / CONFIRMED) — append-only ledgers as one governed family (6-tuple axiom + membership registry); closure is an explicit dated write, never silence. Parent frame for ADR-034 + ADR-044. Anchor: `_DECISIONS/ADR-033` (ratified 2026-07-19).
3. **App-layer user isolation** (79 / CONFIRMED) — Auth.js session + `userId` filter in every Prisma query; Prisma = postgres superuser, BYPASSES RLS (`auth.uid()` NULL); RLS is deny-all backstop for the anon/PostgREST surface only. Anchors: `scripts/rls-policies.sql` L5-18; ADR-008; `_PATTERNS/durable-gotchas.md` L13-15.
4. **Two-tier trust contract** (74 / CONFIRMED) — anonymous compass+prep never persists ("no auth = no write"); history/brief-SHARE need a magic-link session; anonymous briefs shared statelessly via URL-fragment, zero server write. Anchors: `src/app/api/prep/route.ts:29-33`, `compass/route.ts:385-386,456`, `src/lib/shareLink.ts`, ADR-016/037. *Precision: brief is publicly viewable; only brief SHARE is gated.*
5. **Commit-NCI rubric (ADR-035)** (80 / PARTIAL) — ratified 5-lens 0–100 code-quality rubric (Correctness30/Coherence25/Consequence20/Clarity15/Craft10), distinct from product `nci_score`, SSOT for the nci-scoring skill — **gate is de facto dormant**. PARTIAL: only ~94 genuine rubric scores exist (not ~360); the rest are julia-scope sequence counters 101–227.
6. **Zero-Trust (ADR-032) governing law** (76 / PARTIAL) — every input untrusted (incl. the model's own prior output); model tier = difficulty×trust×blast-radius; egress is a control; conformance checklist for later ADRs. PARTIAL: "invoked by ADR-044" is false; a duplicate ADR-032 number exists.

## Dropped sub-anchors (defects that must not be re-bought)
- "MEMORY v3.10.0" label under ADR-033 is stale (was v3.11.0 at run time). Keep the decision, drop the version.
- ADR-033 is NOT the live enforcement-parity ledger — that's **ADR-034 / `_PATTERNS/ledger.json`** (CI-gated). ADR-033's own header warns an earlier "ledger as live law" memory was stranded on an unmerged branch.
- `[NCI:SKIP]` is **defined** by ADR-035 (L28 format, L57-61 legitimacy) — not an undefined emergent trailer.
- Commit-NCI "~360 scored" is inflated: ~258 of ~352 numeric trailers are sequence counters; ~94 real scores.
- Zero-trust "invoked by ADR-044" is false; duplicate ADR-032 = known dedupe-backlog artifact.
- RLS project-id labels disagree across sources (cosmetic; doesn't touch the principle).

## Negative results — liveness SoT rules (the expensive learning; do not re-derive)
- **Per-file `Status:` headers are the liveness source of truth — NOT `index.json`** (which is stale: missing y_state/stability, omits duplicates + ADR-044).
- **Duplicate ADR numbers (024, 025, 031, 032) are known drift, not conflicting canon.** ADR-021 is an unused number, not a missing file.
- **`[NCI:NNN]` values ≥100 are receipt/decision SEQUENCE IDs, not commit-quality scores** (rubric caps ~68–99). Treating them as scores overstates code quality badly.
- **NOT built despite canon prose:** L6/L7, ATG, **Kairos detection**, blockchain/ordinal registry, Vector Collision microservice. **Observatory is a STATIC demo only** (`public/observatory/` via next.config rewrite); WORLD.md "live" = aspirational. Don't read spec prose as implemented behavior.
- **Settled bootstrap, not live drivers:** ADR-002 (SQLite/Supabase), ADR-005 (env injection, self-superseding), ADR-007 (db push vs migrate).
- **Explicitly NOT-decided (excluded):** ADR-018 HELD, ADR-024-CALIBRATE DRAFT, ADR-025 provisional, ADR-027 "do not treat as canonical", ADR-038 RC, ADR-040 DRAFT.
- **Drift Sentinel daily-Sonnet routine was disabled 2026-07-19** and fires against stale JTBDs — not live.
- **`_PATTERNS` = 32 files but most dated ones are point-in-time PLANS, not durable gotchas.** `durable-gotchas.md` is the reliable recurring-lesson file.
- **`vercel.ts` migration never landed** — `vercel.json` remains canonical. **AGENTS.md co-author still pins "Claude Sonnet 4.6"** — likely a stale pin.
- **Emergent-looking vocab is already logged, not net-new:** chi/ma/wuwei/hyperstition/"om" = F2 glossary-backfill gap; BAR collision reconciled; recoil/temporal-provenance/NCI each formally owned (ADR-038/044/035). **DEWY has NO written expansion anywhere** — opaque proper noun; that undefined-but-load-bearing status IS the finding.
- **operators/ pantheon:** mostly single-purpose modules without cross-corpus recurrence; only **Loki/Kairos/Inchworm/Kintsugi** surface as genuinely emergent vocabulary beyond their own files.
- **Commit cadence is not steady** (771 in 2026-07 vs 144 in 08); July was an outlier — don't read velocity from one month. `heal` is a rare Yuri-family ritual (8), not a broad category like `fix` (384).
- **Environment blind spot:** this env blocks `*.arcs.care` at the CONNECT tunnel (403) — all live-lockdown/analytics/domain claims are repo-side only, unconfirmed against production. `snapshot.json` (captured 2026-08-08) is point-in-time, not current working state.

## ROM candidates (not confirmed ROM) — await Observatory validation
- RC-III-001 relief-vs-disappointment Court heuristic · RC-II-003 "analysis at the wrong moment = most common failure."
- Litepaper/Manifesto/YellowPaper/Phenomenology are REFERENCE-tagged, not governing canon.

---
*Calibration verdict: the density/defensibility bars held — 6/6 survivors grounded in code/git, adversarial pass caught real drift without false-refuting the core claims. Approach validated for the full multi-repo + design-system sweep. Next deposit appends here (or a dated sibling); the basin only deepens.*
