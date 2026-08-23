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

# Handoff — v3.41.0 (2026-08-19)

> **Active pickup point — the loaf-cooling handoff.** Caps the v3.40.0 session's second arc:
> design-system unification across 8 surfaces, the page factory, ADR-066, and the live-culture
> naming. Oracle-numbered (41). Read v3.40.0 below for the open bugs — they are STILL the next
> session's first work.

## What landed after v3.40.0 (all pushed, all verified live)
- **One design system, 8 surfaces, zero exceptions:** prl.arcs.care root = Overview (masked
  todd-call content); /status/{progress,crm,troubleshooting,tidio,atlas,build}. Sticky pill nav
  (Overview-first) + identical global footer on every page; 916px wrap; glass panels, no hard
  dividers; balanced h1s; every mobile/layout defect fixed live (~20) — each now a rule in the
  factory SKILL.md. Mechanical audit script proves conformance (in-session pattern, re-runnable).
- **prl-page-factory skill** (`.claude/skills/prl-page-factory/`): atoms.css extracted from the
  live reference page + zero-dep generator; new page = ~20-line spec.json. Smoke-tested.
- **ADR-066 Generative Recoil** minted from a witnessed naming moment (witness stub GREEN,
  promoted): recoil is bidirectional — audit AND compose session residue into instance → class →
  invariant. Falsifiable: next PRL page must cost a spec, not a session. Build.html ADR stat
  61 (tripwire caught its own mint again, fixed the surface, never --no-verify).
- **Live-culture / ancient-starter doctrine** (Zach's naming): feed artifacts from the deployed
  instance, never parallel-maintain. Both claude.ai artifacts (atlas + ssot) rebuilt
  instance-first from the deployed page and republished to their same URLs.
- **Apex spine v15** added (generative-recoil-live-culture). **Seeds planted:**
  `live-culture-artifacts`, `page-factory-from-session` (+ earlier: `engagement-universe-doll`).
  **Memory minted:** [[generative-recoil-live-culture]] incl. 3 tao proverbs.
  **Parked for Aug-24 close-loop:** evidence-anchored re-pricing of 1.3–1.5 (1.4 highest
  exposure — attribution is ground-truth-verification work, the category that ran 3x).
- **Reading-room candidates (Alexandria):** ADR-066 + the starter framing join apex-spine as
  center-room candidates — placement idea only, not integrated.

## Register decision made and to hold
No src/ UIKit for PRL — the factory IS the UIKit at the right weight; React-ification only on a
third interactive surface family (rule of three). Don't blur into the app's FieldOS system.

## Next session (unchanged from v3.40.0, plus)
1. Co-pilot Task 1: empty-email filter + Roger Lamarre repair (CRITICAL, before more demo traffic).
2. Test-lead cleanup · rep notification · SLA sweep · baseline pull (briefs/meta-prompts ready).
3. UAT selector debug run · SEM template Phase 0 (fill 2 node schemas via export).
4. Aug-24 1.2 close-loop: expected-vs-actual + the parked re-pricing conversation with Todd.

# Handoff — v3.42.0 (2026-08-23)

> **Active pickup point — the Wing engagement session.** One inbound (Sean Wing asked for "the
> good, the bad, and the ugly" on his essay) run end-to-end through the full stage-print arc,
> throwing off a class, an invariant, and repo-wide gate hardening. 14 PRs merged (#153-#166),
> all deployed + verified live.

## Shipped (all live)
- **wing.arcs.care** — S-tier diamond teardown of Wing Financial for Sean Wing: claim-vs-record
  echo map, 7-gauge panel, forensic CRD timeline (Nathan Wing question), objection map,
  pre-mortem, gauntlet, shavasana. Read-at-any-depth (collapsed-H2 deks = exec), 15-slide
  PRESENT deck (good/bad/ugly, earned-fidelity render, FINISH exits to page), touch-native
  inline term definitions, whole-eyebrow copy-link, legend jump, Wing favicon, noindex meta +
  X-Robots-Tag header, custom analytics events (pres_open/complete/exit, legend_jump,
  term_hover, copy_link + dwell). Zero em-dashes (now a mechanical gate).
- **teardown-page-factory skill** (`.claude/skills/teardown-page-factory/`) — the class print:
  spec params, component mapping, SLIDES schema, six blocking ship-gates, efficiency contract
  (~1/3 spend on next run), four-width pixel sweep. wing.html frozen as reference instance.
- **Stage-print invariant** — `_PATTERNS/2026-08-23-verb-altitude-gate-matrix.md`: five verbs ×
  gates × fates, altitude orthogonal; forge-pattern/forge-cut cited as precedent pair.
- **Ex-ante receipt filed** — `runtime/recoil/generated/2026-08-23-sean-wing.json`, honest
  provenance (post-link-send, pre-response). Zach SENT wing.arcs.care to Sean 2026-08-23.
  Six outcome estimates, 72h kairos window, YELLOW conviction, close-loop rubric.
- **Wrap-regression class killed at the root** (recurred 3x in-session: page column, stat strip,
  deck): root measure tokens not selector literals, auto-fit grids, four-width sweeps. Banked in
  PRODUCT.md "Known design failure modes" (impeccable loads it every design pass) + memory + skill.
- **CI parity while GitHub Actions is billing-dead**: 6 workflows disabled (Dependabot left on);
  leak-check + tripwire wired into the machine-local pre-push hook (with fetch-fresh base);
  leak-check ANALYTICS debt paid (18 pages got the insights snippet); family-roster.json
  allowlisted. NOTE: squash merges require branch rebase before the hook's tripwire diff narrows.

## Open (next session's first work)
1. **GitHub Actions billing** — Zach-only fix (Settings → Billing); re-enable 6 workflows after
   (one-liner in session log / `gh workflow enable`).
2. **Sean close-loop** — trigger: any reply, 7 days silence (2026-08-30), or his next public
   note. Run /recoil-close against the SSOT. Long-form note draft parked in
   `_ARTIFACTS/wing-sean-linkedin-draft.md`; if sending, run counterpart-gauntlet first (the
   one un-run gate).
3. **Two forked sessions in flight**: legacy tripwire-flag cleanup (4 pages) + verb-matrix
   germination (ADR promotion + wiring gates into skills). Don't duplicate their work.
4. **Roadmap seed planted**: [[seed-recap-rewind-surface]] — teardown factory pointed inward
   (user's own receipts/scans/briefs as a rewind surface) + save-to-ledger PLG onramp. NOT now.

> _v3.40.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-23; v3.39.0 + v3.38.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-19; v3.37.0 (Comet resume) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
