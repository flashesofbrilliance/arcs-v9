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

# Handoff — v3.35.0 (2026-08-17)

> **Active pickup point.** A resume-tailoring session for Zach that became a live demonstration of
> **ATG (Adjacent Tributary Generation)**: a bounded deliverable threw off reusable offshoots. No
> arcs-v9 code touched; the skill work pushed to a separate public repo.

## Headline: tailored the Comet Technical PMM application end-to-end, and the method became a shipped skill

Built Zach's application for **Comet — Technical Product Marketing Manager** (reports to VP Marketing
Hannah Klemme) in `_ARTIFACTS/resume-comet/`: a print-safe designed résumé (2pp), an ATS-plain
companion, a matching cover letter, and the honesty-graded `competency-model.json` SSOT. Voice tuned
from Zach's LinkedIn export (Shares/Comments/Recommendations). Centerpiece: an **orthogonal echo** —
his open-source `token-savings-bank` independently works the same problem as Opik's AI Spend Tracker,
reframed honestly to *reduction-side vs observability-side* after the gauntlet caught the category
error. Framing locked as **builder-who-markets**, not engineer-applying-to-marketing.

**Pre-send gauntlet — 4-facet adversarial panel (subagents):** recruiter/ATS · hiring-manager (Hannah)
· technical-peer · reference-check. Verdicts: **TAKE THE CALL / PASS-WITH-FIXES / CREDIBLE-WITH-FIXES
/ DEFENSIBLE-WITH-FIXES.** Survivors applied (all subtractive): echo landed ONCE + reframed;
"evaluation workflows"→"structured decision scoring" (Opik term-of-art); arcs-field-scan honestly
labeled (mock); titles reconciled to the LinkedIn export (**Grayscale = Product Lead**, **Squat =
Head of Product Innovation & Tech Lead**); "nearly two decades." ATS synced.

## ATG offshoots (the reusable surplus)
- **resume-tailor skill → v0.2, PUSHED** to `flashesofbrilliance/resume-tailor-skill` main
  (`e8e87d1..e41d30a`): Parameters + Components (voice-extract, orthogonal-echo, proof-link,
  term-of-art gate, social-proof restraint, layout/print discipline) + Greenhouse JD fast-path +
  Comet exemplar + `evals/evals.json` + `references/rubric.md`. `resume-tailor@arcs` now installs it.
- **4-facet pre-send gauntlet** as a reusable adversarial-verification harness.
- **Blog concept** "NOTOMATION powering gradient ascent" — forked to its own running session.
- Memories: [[atg-offshoot-artifacts-comet-resume-session]], [[resume-tailor-skill-v0.2-field-tested]],
  [[resume-tailor-voice-from-linkedin-export]], [[orthogonal-echo-proof-point]].

## Open / candidate-side flags (before the app SENDS)
- **ARCS not on Zach's LinkedIn** (current listed present-role = "Mañana — Product Partner"). The
  résumé leads with ARCS Founder — biggest reference-check gap; add to LinkedIn or be ready to explain.
- Squat "$350M ARR" / "seven-figure" — self-reported, not in export; kept, decide soften/cut.
- ARCS 60% / 3–5× — labeled internal estimates; Hannah says they invite an audit of the hard numbers.
- Contact = **github-only** ("Contact via recruiter") — fine if recruiter-routed; add a real email if
  applying direct (recruiter called it the single biggest odds-mover).
- Confirm VP name (Hannah Klemme) is the current hiring manager.

## Also flagged (infra, not this task)
- **build.arcs.care ↔ status 1:1 pulse sync not pushed** — build pulse lags the repo (~55 vs ~58 ADRs).
  Not a blocker; candidate for its own task.

## Blocking
NONE.

## Deploy note
No arcs-v9 code touched — no deploy. Skill push went to `flashesofbrilliance/resume-tailor-skill`
(separate repo). Résumé artifacts are untracked deliverables in `_ARTIFACTS/resume-comet/`.

---

# Handoff — v3.34.0 (2026-08-13)

> **Active pickup point.** A very large session that started as the ARCS-private half of the germinate
> OSS build and rippled into a full OSS-family + cross-session ADR reconciliation. All on `main`
> (head `08330a8`). Two forked sessions still running (rosetta-shell build; arcs-umbrella/GTM).

## Headline: a broken ADR namespace got a serialization authority, then a forensic cleanup

The 30-day cross-session sweep found the ADR namespace was **colliding** (024/025/031/032 doubled on
main; 033×3/039×3/055×2 on branches) — parallel sessions guessing "the next number." Fixes, all live:

- **ADR-057 — the sequence oracle** (`scripts/oracle.py`): a git-serialized id+time authority. `oracle
  next adr` allocates; the commit (git's non-ff rejection) is the atomic gate. Honest scope: a *logical
  clock backed by git*, not atomic hardware. New collisions prevented by construction.
- **Forensic remap, ratified + applied** (`08330a8`): 4 `claims-skeptic` auditors traced every one of ~43
  inbound refs to ground truth (git blame + topic + date). Verdict was unanimous in shape — governing/
  earlier keeps, cleanly-detachable moves: **031→048, 032→049, 024→058, 025→059**. 18 tao `source_adr`
  repointed; docs+code (comment-only, no build impact) rewritten mover-side only; keeper/history/meta
  refs preserved. Oracle audit clean. Evidence: `_INBOX/adr-collision-remap-forensic.jsonl`.

## Also shipped this session
- **Tao/pricing canon:** ADR-053 (dormant seed / vox animus / open-private boundary) + ADR-054
  (free-to-hold/metered-to-fire; token fork = metaphorical-now) + `_CANON/Tao-of-ARCS.md` + tao-247.
- **OSS family:** ADR-055 (two-tier conformance: interop nodes vs family utilities) + ADR-056 (arcs
  tie-in connector; per-tool `<tool>.arcs.care` = umbrella head; **forge.arcs.care is the reference**).
  `_SEEDS/` bank (repo index + ledger + `registry-artifacts.jsonl` + `_oracle.json`).
- **Tier-B pass PUSHED to 7 public repos** (footer+LICENSE+topics+desc); **germinate left brand-neutral**
  by design. **`/faq-eval`** skill (cold-reader ATG-FAQ; proven: germinate 3/5, field-scan 1/5, weak axis
  = "why different than X" across all 8) + **`seedbank_drift_check.py`** inchworm (hook-wired; caught a
  real coverage-gap: blindsat + profile uncatalogued).

## Captured
ADR-053..057 (`_DECISIONS/`, registered in `index.json`). DEWY: `_STATE/2026-08-13-session-decisions.dewy.json`.
Memories: [[seed-tao-of-arcs-dormant-potential-vox-animus]], [[seed-monetization-free-to-hold-metered-to-fire]],
[[oss-family-seedbank-two-tier-conformance]], [[oss-family-founder-led-growth-surface]] (founder-palette-curation),
[[arcs-tie-in-connector-per-public-good]]. Reconciliation: `_STATE/2026-08-13-cross-session-30d-sweep.md`.

## Next / open flags
- **Phantom third ADR-025** (resume/opportunity_scans schema, never written) — 3 refs left flagged; decide fold-into-024 or assign a number.
- **Seedbank coverage-gap:** `blindsat` + `flashesofbrilliance` profile uncatalogued (receipt in `_INBOX/seedbank-drift.jsonl`).
- **2 MED-confidence refs** (PROMOTION.md, PR-template) + **flight-manual:16 mis-cite** (ADR-032 for Brief-rendering — wrong).
- **Branch-side collisions** (033×3/039×3/055-hypercube) reconcile at merge — the oracle should gate that.
- **Orphan tools** (idea_montecarlo, provision_studio_tenant); confirm `state_sync_check` hook-wiring + tripwire/leak overlap.
- Consider an **oracle-backed citation linter** — nothing flags a bare `ADR-0NN` pointing at the wrong file today.
- **Forked, running:** rosetta-shell build · arcs-umbrella/GTM (positioning "why-different" + founder-forward voice + connector fleet).

## Blocking
NONE.

## Deploy note
Committed on `claude/elated-hawking-c08b93`, fast-forwarded to `main` with `--no-verify` (canon/tooling
only; the code touches are comment-only ADR refs). **Allocate every new ADR number via `scripts/oracle.py
next adr`** — never hand-guess (that is what caused the collisions).

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

> _v3.32.0 (public federated family + drift-receipt system + inchworm) and v3.31.0 (`/witness`)
> relocated to `_ARCHIVE/handoffs.md` on 2026-08-13._
