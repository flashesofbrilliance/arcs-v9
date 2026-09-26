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

# Handoff — v3.67.0 (2026-09-26)

> **Built a four-layer anti-slop + provenance eval CoE, landed it on main, dogfooded it on the Success
> Academy resume, and forked two follow-on initiatives.** Branch claude/success-academy-ai-pm-5bf0d9
> (HEAD 5ae8d0fb, pushed, NOT merged). Heavy cross-session coordination with the good.arcs.care thread.
> Nothing published; nothing on main except the eval suite (PR #509).

## Shipped to main (PR #509)
Eval suite: `scripts/slop_lint.py` (style hard-fail + `--metrics` organically-human baseline: burstiness>=6,
per-mode specificity floors incl. evidence-aware `--mode essay` @10%), `scripts/slop_eval.py` (judgment tier,
Anthropic over stdlib urllib, no dep), `scripts/provenance_lint.py` (every metric cites an evidence.jsonl ledger),
`_PATTERNS/slop-free-rubric.md`, + pre-commit slop+provenance guards. All four layers have fail-on-bad+pass-on-good
`--self-test`. Receipt: `2026-09-26--slop-eval-suite-to-main--ZH`.

## On this branch (pushed, not merged)
- **Success Academy conventional resume** (`_ARTIFACTS/forge-success-academy-ai-pm/Zach-Harris-Resume-conventional.{html,pdf,docx,txt}`):
  human/not-AI-slop, 1 page, 0 em-dashes, New York Metro, verified metrics only (cut untraceable "40+ demos/75% pilot",
  kept Zach-confirmed $850K), ATS-verified, gates pass. **READY TO SEND to Brian.** Call brief refreshed for the
  **Tue 2026-09-30 3:30 PM EST** interview (`_STATE/job-search/success-academy-ai-pm-brief.md`): PM-first, discovery-led,
  3 loaded answers (degree bridge / ARCS-solo "The Arc" / 2019-20 gap).
- **Honesty catches:** a fabricated metric was caught only when Zach asked -> built the provenance gate as the factual
  twin; corrected a FALSE "rule:null" claim in the kintsugi seam + to the peer (impeccable findings key on `antipattern`;
  config exemptions DO work). Memory: `provenance-gate-every-metric-cites-evidence`.

## Two forked initiatives (idle; not merged)
- **resume-tailor SSOT bundle** — branch `claude/slop-gate-consolidate-dist-a34d1c` (PUSHED): `tools/slop-gate/` npm+Homebrew
  scaffold. Decisions LOCKED: `@arcs-care/slop-gate`, MIT, npm-first (Homebrew deferred to EXISTING `flashesofbrilliance/homebrew-tap`).
  **ADR-82** write-lock gates `npm publish`; package.json keeps `private:true`; publish = 4 user-gated commands.
- **design-system ui-kit normalization** — branch `worktree-agent-a9c05965613c705e2` (LOCAL): `src/ui-kit` atomic extraction +
  `templates.json` (template<->slop-mode registry) + `scripts/component_source_gate.py` (visual twin of token_source_gate) +
  impeccable **brand profile** (recoil-report + good.arcs.care NFTT globs; brand findings->0, debt live) + 1 PoC migration +
  `_PATTERNS/2026-09-26-ui-kit-migration-plan.md` (7 waves) + **ADR-83**. Inventory: 225 surfaces, 135 re-author the palette,
  101 fail token_source_gate.

## Open (ALL user-gated; nothing fires without Zach)
1. Review the 7-wave migration plan -> land design-system branch to main (unblocks ui-kit migrations + the peer's NFTT visual gate).
2. Open bundle -> main PR (governance-first per ADR-82).
3. Run the 4 gated npm publish commands (create @arcs-care org + npm login).
4. Token-canonicalization fork: `_tokens.css` (Geist/Instrument) vs `DESIGN.md` (Inter/JetBrains) — the root divergence.
5. SEND the resume to Brian.

## Cross-session state
good.arcs.care peer ("Build cold-reconstruction incident report") wired slop_lint into `nftt-gates.sh` (#510); waiting on
the design-system branch landing on main to re-run the brand profile + add the detector step. ADR-82 (Track-B) vs ADR-83
(design-system) resolved a same-number oracle collision; reconcile `_oracle.json` at merge time (normal).

# Handoff — v3.68.0 (2026-09-26)

> **Landed the design-system + two follow-ons on main and CLOSED the good.arcs.care cross-session thread.**
> Continues v3.67.0. This branch (`claude/success-academy-ai-pm-5bf0d9`) is unchanged at `bfd1a487`; all net-new
> work landed on **main** via focused branches (the eval-suite pattern), each receipted. Four main PRs this
> session: #509 (eval suite), #526 (design-system), #527 (site resume swap), #528 (low-contrast ratchet).

## Landed on main since v3.67.0
- **#526 design-system ui-kit** (`8595ed3e`): `src/ui-kit` atomic SSOT + `templates.json` (template<->slop-`--mode`)
  + `scripts/component_source_gate.py` + impeccable **brand profile** (recoil-report + good.arcs.care NFTT globs)
  + **ADR-083** + `_PATTERNS/2026-09-26-ui-kit-migration-plan.md` (7 waves). Re-synced to a moving main twice
  (deduped-union config, kept main's `--dim:#748699` + notomation post). Receipt `2026-09-26--ui-kit-design-system-to-main--ZH`.
- **#527 site resume swap** (`7df70b2f`): success-academy.arcs.care `/resume` + PDF + ATS now serve the CONVENTIONAL
  resume Zach emailed Brian (146811 bytes, New York Metro, **verified live**); the designed Vico resume is no longer
  served anywhere. Receipt `2026-09-26--sa-site-serve-conventional-resume--ZH`.
- **#528 NFTT low-contrast ratchet** (`12a50cb0`): `scripts/nftt_contrast_ratchet.py` + `_STATE/nftt-contrast-baseline.json`
  (240 findings frozen as a labeled DEFERRAL). Honest middle (Zach call C): runs the detector `--no-config` so it's
  independent of the config exemption + the kintsugi total-count ratchet; FAILS only on NEW low-contrast above baseline;
  self-tested. Receipt `2026-09-26--nftt-low-contrast-ratchet-to-main--ZH`.

## rule:null correction (banked)
I asserted twice (kintsugi seam + to the peer) that impeccable findings carry `rule:null` so config exemptions can't
apply. FALSE — they key under `antipattern`; exemptions work (proven A/B, 120->76). Corrected the seam (`5ae8d0fb`) +
re-notified the peer. Lesson: A/B-test an exemption mechanism before declaring it broken (verify-don't-assert, the
other direction — I called a working control broken).

## good.arcs.care thread: CLOSED
Peer wired `slop_lint` into `nftt-gates.sh` (#510); brand profile + contrast ratchet now on main with the exact
invocation relayed (`python3 scripts/nftt_contrast_ratchet.py <file>`; `--no-config`; `--update-baseline` to re-snapshot).
Peer to wire the detector step + re-arm. **artifact-vs-real settled:** the 3 named posts are white-bg detector artifacts
(+ `#000000`-on-dark are artifacts too, no literal `color:#000` in markup); the only genuine debt is `--dimmed #64748b`
on `#161b22` = 3.63:1, concentrated on `take-home-trap-dossier` (peer filing a fix task; fixing + `--update-baseline`
drops it from the ratchet). Sampling-before-freezing kept a genuine-debt exemption from shipping as a silent clean bill.

## Open (USER-GATED; nothing fires without Zach)
1. **npm publish `@arcs-care/slop-gate`** — 4 gated cmds (create `@arcs-care` org + npm login, remove `private`, `build.sh`,
   `npm publish --access public`). Governed by **ADR-82** write-lock. Bundle branch `claude/slop-gate-consolidate-dist-a34d1c` (pushed).
2. **Bundle -> main PR** (governance-first per ADR-82) if landing the bundle before/with publish.
3. **Token-canonicalization fork** — `_tokens.css` (Geist/Instrument) vs `DESIGN.md` (Inter/JetBrains): the root divergence.
4. **`take-home-trap-dossier` `--dimmed` contrast fix** — the peer's follow-up (real sub-4.5:1 debt).

## SA engagement
Conventional resume SENT to Brian for Jarrod; **interview Tue 2026-09-30 3:30 PM EST**; site serves the same resume;
call brief refreshed (PM-first, discovery-led, 3 loaded answers). Memory: `project_jarrod_wolf_success_academy`.
