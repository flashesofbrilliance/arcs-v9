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

# Handoff — v3.43.0 (2026-08-26)

> **Active pickup point — the germination + genesis-riff session.** Opened as the verb-matrix
> germination fork (v3.42.0 open item 3 — now CLOSED); became the day the canon named its own
> physics. PR #167 MERGED to main 2026-08-26 (12 commits), prod deploy Ready. Oracle-numbered (43;
> adr + handoff counters both reconciled — they drift when sessions mint off-oracle).

## Shipped (all merged + live)
- **ADR-068** (verb x altitude gate matrix, oracle-allocated): five-verb print schedule — every
  stage cut prints an artifact through a gate to a fate; altitude orthogonal. Mandatory blocking:
  ex-ante-receipt-before-send · pre-send counterpart-gauntlet · close-loop-on-response. Advisory:
  witness stub, handoff. **Wired into 7 skills** (teardown-page-factory Pre-send gates section;
  forge phase-8 ex-ante check; recoil-ship Step 5b; recital in omakase/recoil-new/prep/close).
  `_DECISIONS/index.json` backfilled (066/067 were missing); build.html ADR stat 63 (tripwire
  caught its own mint again); matrix pattern doc carries the promotion pointer.
- **Seed bank, 4 new seeds ALL with ledger receipts** (no new orphans): `projection-family-registry`
  (omakase/teardown/atlas/codex/war-room/receipt = induced projections of one corpus; atlas =
  next factory, gated on third demanded instance), `extraction-prospecting` (rank extraction
  candidates from banked cost-receipts; first pass queued on the PRL close-loop multiplier),
  `sovereign-projection-services` (each factory a sovereign micro-service; spark plug =
  germination block on prints; pilot ladder = honest resume, scan-first), `pollinate` (sister to
  germinate: pollen=invariant stripped of instance flesh via doll_export gate; self-pollination =
  inbreeding = author-cosmology; pedigree fields queued).
- **Witness file 2026-08-23 = the day's spine, 8 stubs**: registry naming → rare-earth
  prospecting → spark plug → inheritance capstone (kid inherits judgment canonically; BAR
  tuition split: ruin inherited, skill personally paid) → tikkun olam ORIGIN (GREEN; absent from
  all of _CANON until witnessed) → molt amendment (lineage: drop → polyform survey → buddhist
  convergence) → tree-fall koan CLOSED (germination = retrospective witness; stubs are for
  sounds that cannot seed themselves) → frame-geometry (PROMOTED same session).
- **Canon: Tao of ARCS v1.1.0** — §V "One field, sovereign zeros, lawful transforms, preserved
  invariants" (Zach: "I'll allow it"); tao-250 + tao-251 minted; genesis note gains the
  four-deep root (adam·adamah·adom·dam) and **Eve identified: chava==anima = the vox animus**
  (bank=Adam, spark=Eve, §III seam = the pairing).
- **Design rulings (approved, unbuilt)**: ziggurat walk starts at null point, first arrow-press
  ignites at trailhead (base terrace, highest indegree), key 0 = return-to-null; observatory
  rebuild seeds T0 ground from atlas topography at that timestamp (terrain = integral,
  replay = derivative).

## Open (next session's first work)
1. **Prospecting pass + PRL 1.2 close-loop** — was parked for Aug-24, now overdue. One
   computation, two customers: actual-vs-expected multiplier from banked receipts → Todd
   re-pricing conversation + the extraction queue ranking.
2. **Sean Wing close-loop window** ends 2026-08-30 (7-day silence trigger) — /recoil-close vs
   `2026-08-23-sean-wing.json`; counterpart-gauntlet the parked note before any send (v3.42.0).
3. **3 orphan seeds** still missing ledger receipts (engagement-universe-doll,
   live-culture-artifacts, page-factory-from-session) — hand curation, hook flags every start.
4. **Backlog, cheap**: ziggurat trailhead/key-0 wiring (~10 lines); tao proverbs for ADR-066/067
   (jsonl has none); lattice --regenerate (human-owned); sacred-geometry echo-map workflow
   (mini-pass done in-thread: 5.5/8 convergent; full blind pass on ask); GitHub Actions billing
   (Zach-only) then re-enable 6 workflows.

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

> _v3.41.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-26; v3.40.0 on 2026-08-23; v3.39.0 + v3.38.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-19; v3.37.0 (Comet resume) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
