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

# Handoff — v3.63.0 (2026-09-15)

> **arcs-algorethics E2E / benchmarks / kabuki audit session** (worktree `arcs-e2e-benchmarks-cicd-0369bd`,
> branch `claude/arcs-e2e-benchmarks-cicd-0369bd` = arcs-v9 PR #446, deliberately UNMERGED). The work
> product lives mostly in the separate repo `flashesofbrilliance/arcs-algorethics` (PRIVATE, no canonical
> local clone; sessions clone to scratch). Every merge receipted in `decision_receipt` (10 rows:
> `2026-09-15--algorethics-e2e-benchmarks-cicd-pr1--ZH` … `2026-09-15--arcs-v9-queue-algorethics-in-scope-benchmark-pr449--ZH`).

## Shipped + verified (arcs-algorethics, PRs #1–#8 squash-merged, main `a3ae0c3`, CI green)
- **Found broken on pickup:** `code/` shadowed stdlib `code` (tests uncollectable); `server.py` imported
  non-existent classes. Both fixed (#1). The Perplexity-authored handoff had four false premises.
- **Live E2E suite** boots the daemon when no gateway URL is set; asserts 423/MORTAL, 423/CARDINAL,
  200/VENIAL under a warmed best-of-3 latency SLA (#2), fail-closed entropy, append-only ledger, keyed
  Edge 401 (#3), and Ed25519-signed resume over real HTTP (#6).
- **Benchmarks, honest:** hendrycks/ethics (parquet branch; datasets 5 refuses the script) recall 0,
  JailBreakV-28k (split `JailBreakV_28K`) 0/200, **AgentHarm 0/176 harmful and 0/176 benign in both
  fn and fn+prompt modes (#8)**. Nightly runs commit to `benchmarks/history/` (#7).
- **Ops + SSOT (#4):** `arcs ops status|migrate|keys|promote` (dry-run default, prompts, secrets never
  printed); `specs/invariants.json` loaded by Python + JS, parity-checked against the arcs-v9 route.
- **Ledger renamed `algorethics.gate_receipts` (#5)** + `db/preflight.sql`: the originating Perplexity
  thread claims `algorethics.decision_receipts` already exists as a uuid hypercube receipt, plus four enum
  types stranded in `public`. Unverified; the rename avoids the collision either way.
- **Kabuki removed (#6):** `manifold.py`, notebook, TS middleware deleted (unimported). Resume now verifies
  a registered operator's Ed25519 signature (`ARCS_OPERATOR_KEYS`, private key only on the operator machine
  via `scripts/operator_keys.py`). README leads with an honest inventory; theology demoted to appendix.
- **arcs-v9:** Edge route `src/app/api/v1/gate/evaluate/route.ts` (PR #446): fail-closed `ARCS_GATE_KEY`
  bearer gate, constant-time compare, scope declaration, writes `gate_receipts`. Build green. Empty
  Perplexity branch `feat/algorethics-prisma-model` deleted (0 commits). Queue items shipped via #448/#449.

## Lessons booked
- **Assume the spec is stupid first** (Zach): falsify every handoff premise live before building.
- Perplexity's Supabase connector reaches ARCS_v9 (Vercel-Marketplace org); ours does not. Its DB claims
  carry zero evidentiary weight until reproduced. `vercel env pull` returns sensitive values EMPTY.
- The gate's purpose (settled with Zach after reading the full 350KB thread): a narrow fail-closed brake
  on three one-way-door classes, not a general harm classifier. AgentHarm was the wrong yardstick.

## Open (next session)
1. **Zach's three operational moves** (not mine): apply migration 001 in the ARCS_v9 SQL editor + expose
   `algorethics`; set `ARCS_GATE_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` on Vercel and
   `ARCS_GATE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `VERCEL_GATE_URL` in algorethics Actions; merge PR #446
   and dispatch the workflow. `arcs ops` automates all three given a Supabase personal access token.
2. **Queue `algorethics-in-scope-benchmark`** (P3): ~150 harmful tool calls + benign twins across the
   three classes in real tool phrasing; measure recall/FPR. Do not reopen "widen to broad harm".
3. Joe Schriner follow-up + resume-tailor skill fold-back + State-of-the-Union dashboard (carried from v3.62.0).

# Handoff — v3.64.0 (2026-09-17)

> **PRL/Todd 2pm-call wrap + an epistemics-of-warrant thread that hardened the tooling** (this
> worktree `arcs-e2e-benchmarks-cicd-0369bd`, session across branches prl-land-plane / prl-uat-note /
> defeasible-codec-seeds / prl-wrap-page / prl-phase-map / handoff). All PRL surfaces air-gapped,
> wrap-lint clean, em-dashes 0. 8 PRs merged (#469–#476), 4 decision receipts filed.

## Shipped (merged to main, live)
- **prl.arcs.care overview** (PR #475): payment history (1.1 $1,552.51 + 1.2 $4,500 + **Paid-to-date $6,052.51**),
  **1.2 flipped to LANDED** cited to a filed close receipt, honest freshness sweep (killed stale
  Aug-18 todos a relabel would have shipped as false-fresh), deferred-routing **outcome flag** (lose
  auto-attribution → manual assign + the fix), reCAPTCHA v2/v3 fact-check fix, full **ELI5 pass**
  (jargon glossed + a **Bottom line** punchline per section). New exec **/status/runbook** (#469/#473).
- **Internal (#470/#471/#473/#476):** induced backlog + completeness audit; belief-linked
  `prl-dependency-map.json` + `prl_depmap_check.py` eval with a **P-1 investigation-prework gate**
  that hard-fails until the doc corpus is exhausted; runtime `prl_uat_harness.py` (corpus-anchored,
  `--self-test`, reuses task7 test + STATE-OF-SUGAR schema); per-phase **systems/dependency map**.
- **Receipts filed** (Supabase `decision_receipt`): `2026-09-17--todd-prl-recoil-close-pr463`,
  `--prl-runbook-overview-ship-pr469`, `2026-08-26--prl-phase-1.2-close` (backfill),
  `2026-09-17--prl-overview-wrap-ship-pr475`.
- **Seeds + ADR-candidate (#474):** redactive-referential context codec + kinematic-adaptive
  freshness gate (compose LLMLingua+Letta, don't rebuild). 7 witness stubs
  `_STATE/witness/2026-09-17.jsonl`. 3 new epistemics memories (indexed).

## Fact-check landed (KNOW, cited)
For-IT DNS block **re-verified LIVE 2026-09-17**: SPF `include:outlook + mailgun`, DMARC `p=reject`,
`mg.prlresins.com` SPF/MX/DKIM, M365 selector1/2 DKIM, Barracuda MX — all confirmed, no drift.

## The epistemics thread (it hardened the tooling, not just the vocabulary)
Defeasible warrant: a warranted null is time-indexed and decays; carry a freshness horizon + named
defeater-triggers, kinematic-paced (Kairos / Operator21 knot-detection / Nyquist floor). Two-axis
**claim-exit lattice**: falsification (null-flip ¬X→X OR its inverse **exoneration** X→¬X) vs
**mootness** (superseded/vacated). think→know = acquiring **citable** justification; overclaim queues
a self-exoneration. **Corpus-exhaustion is a PRE-WORK GATE on the plan**, not a step in it. Compression
taxonomy: abstractive vs extractive/redactive vs referential (lossless = externalize+reference).
Actor-level: pattern-of-defeated-nulls = believability sorting, but **triage-not-verdict**, level-aware
(apple vs barrel), freshness-gated. Overclaim mislabeled as overconfidence(calibration) when often
under-informed(coverage) — orthogonal axes; receipts are the diagnostic.

## Open (next session)
1. **PRL phase cards (1.2-A/1.3/1.4/1.5 + analytics/tagging) HELD** pending 3 decisions the systems/deps
   map surfaced: **(a)** 1.3 real net-new scope (its recognition engine already shipped under 1.1) or an
   honest reframe; **(b)** 1.5 ongoing Lyro-curation owner (the real company-side "training-agent" dep,
   currently unnamed); **(c)** analytics/attribution plan (only a `gad_source` check exists). Do NOT
   stamp invented scope on the client page.
2. **Tidio→Sugar pipeline: built + staging-proven, NOT prod-verified.** Staging→prod path documented
   (publish drafted zaps in zap-kit order; prove old zap `series_376761228` OFF; 4 acceptance tests via
   the UAT harness; then the 3-step cutover). Two teed-up sandbox jobs (full chat into ticket +
   spec-code cross-ref) **staged for Chrome/Comet on Zach's go** (HITL, sandbox only).
3. **Deep memory dedup pass** — index over the soft budget across 263 files; needs per-file review.
4. Joe Schriner follow-up + resume-tailor skill fold-back (carried from v3.62/63).
