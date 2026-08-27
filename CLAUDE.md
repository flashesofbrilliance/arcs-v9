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

# Handoff — v3.46.0 (2026-08-27)

> **Active pickup point — the receipt-surface session** (same working day as v3.45.0; this block
> covers the arc after the close-out: surface -> canon -> gauntlet -> board -> rollout). All merged
> to main (#180 squash 59cef5b0, #184 ba6c15bb), prod deploy Ready, routes verified live.

## Shipped (all live)
- **prl.arcs.care/status/receipt** — the closed 1.2 receipt as data-driven story: BLUF, 3 headline
  tiles, expected-vs-actual band chart (SVG, honest-scale range, mobile scroller + punchline
  auto-scroll), directional hours bars, scorecard, 1.3 recommendation-voice setup, losing-receipt
  section, fine-print method. Stamped via prl-page-factory + bespoke organisms; impeccable
  distill/polish passes; dataviz palette validated. **Gates run in full:** fact-check vs baseline
  CSVs (all headline numbers trace) + counterpart-gauntlet (6 facets, 7 agents, 865K tok):
  14 verified findings ALL fixed (2 pathogens on the four-hour row: no separate assignment
  timestamp; reminder goes to Zach not rep — pill now "live · rep alert staged"), 4 over-flags
  rejected. Run banked in `_STATE/gauntlet-runs.jsonl`.
- **ADR-069** (minted in-session, oracle audit PENDING — flag on next oracle pass): first closed
  client receipt => precedent-shaped expectation management. Four-in-one print: witness stub
  (`_STATE/witness/2026-08-26.jsonl`) + ADR + DEWY (`_STATE/2026-08-26-session-decisions.dewy.json`)
  + wisdom. build.html ADR stat 63->64 (tripwire caught its own mint, again).
- **Instrument Board** — `scripts/warroom_board.py`, SECOND sovereign-projection-service instance:
  stdlib-only factory, adapter-per-JSONL-ledger (gauntlet-runs + falsification-ledger snapped on),
  typed print + spark-plug germination sidecar, served admin-gated at **/warroom/gauntlet** (404s
  anonymous — verified). Regenerate after every gauntlet; keep findings machine-parseable
  ("N pathogen, N crack, N nit" + "N over-flags rejected").
- **Receipt pill on all 8 PRL pages** + gold jumplink on the prl.arcs.care homepage nav; factory
  SEGS updated so future stamps inherit it (#184). Tripwire real-name/dead-link flags adjudicated
  as pre-existing main content in the commit message (not silently bypassed).
- **4-hour rule reframed per Zach ruling:** closes mechanically (creation==assignment timestamp,
  elapsed-window reminder); Todd's written ack demoted to nice-to-have FYI across page + drafts.
- Merge hygiene: v3.44.0/v3.45.0 handoff collision resolved (parallel Ahmed session), squash-merge
  branch reset to main (rebase-replay aborted — tree was identical).

## Open (next session's first work)
1. **Human-gated PRL installs** — zap kit paste order (`_ARTIFACTS/prl-zap-kit/README.md`,
   task8 filter first) + empty-email e2e widget chat (delete created lead after, receipt).
2. **Close-loop CALL with Todd** — walk `_ARTIFACTS/prl-1-2-close-loop/2026-08-26-close-loop-onepager.md`
   + the live /status/receipt page; send or fold in the two-confirmations email draft; chase
   ZoomInfo contact + Bill/territory. 1.3 kickoff = Todd's call, $4,000 with precondition batch.
3. **Sean Wing close-loop window ends 2026-08-30** — /recoil-close vs `2026-08-23-sean-wing.json`;
   counterpart-gauntlet the parked note before any send.
4. **1.2-A stays PAYMENT-GATED** (invoice #NYQRTJPQ-0004; Stripe MCP needs auth to verify).
5. Carried: orphan seeds curation (human) · GH Actions billing (Zach-only) · ADR-069 oracle audit ·
   ziggurat trailhead/key-0 · tao proverbs 066/067 · lattice --regenerate (human-owned).

# Handoff — v3.45.0 (2026-08-27)

> **Active pickup point — the PRL close-out session (renumbered from v3.44.0 after collision with the Ahmed handoff on main)** (non-interactive). Folded the cross-session
> PRL sweep into one run. Route reality: no Zapier MCP, no human at keyboard, Stripe MCP
> unauthorized — so Zap-kit installs + widget e2e stayed STAGED (verified), everything inline
> got executed. Full receipt: `runtime/recoil/generated/2026-08-26-prl-close-out-session.md`.

## Shipped (this branch, draft-first — nothing deployed or sent)
- **PRL 1.2 close-loop CLOSED + prospecting pass 1 (was overdue Aug-24):** wrong-if fired,
  ~2.1x central multiplier vs the 20h bet (7 work days / 109 PRL commits, method disclosed);
  cap held. Math + Todd one-pager + extraction ranking: `_ARTIFACTS/prl-1-2-close-loop/`.
  Re-pricing happens WITH Todd on the call (gate honored). Rec: 1.3 stays $4,000 with a
  precondition input-batch before the clock starts.
- **Drafts for Zach (never auto-sent):** three-confirmations email (ex three-scenario), 4h-proxy
  decision paragraph, chase list (sandbox-written-approval · anti-ICP list · territory via BILL
  GALLA · ZoomInfo contact), status/progress draft diff (apply + deploy only on Zach's "ship",
  from MAIN worktree).
- **Judgment memos:** Lyro-races-flow → rec accept-for-pilot, natural 1.5 scope; read-more links
  → /contact/ to manual Q&A only, rest parked 1.3. Analytics audit CLOSED (all 8 pages have
  the snippet). 1.4 SEM prep verified ALREADY DONE (Aug-18 template + 5 instances + runbook).
- **NEW: /status/receipt surface** — the closed 1.2 receipt as data-driven storytelling
  (`public/prl-status-receipt.html`, stamped via prl-page-factory + bespoke band-chart/tiles
  organisms, 4-width sweep verified; wired in proxy.ts + next.config.ts; DEPLOYS ON MERGE —
  merging the PR is the ship gesture). **ADR-069 minted** (first closed client receipt =
  precedent-shaped expectation management; oracle audit pending) + witness stub 2026-08-26 +
  DEWY receipt — the four-in-one print, per Zach's live witness call.
- Backlog statuses annotated in `_QUEUE/induced-backlog.jsonl` (prospecting-pass-1 DONE;
  zap-kit items open/staged-human-gated).

## Open (next session's first work)
1. **Human-gated PRL installs:** zap kit paste order per `_ARTIFACTS/prl-zap-kit/README.md`
   (task8-filter first), then empty-email e2e widget chat (delete created lead after, receipt).
2. **Close-loop CALL with Todd:** walk the one-pager; get written acks (sandbox, competitor,
   4h proxy); chase ZoomInfo contact + Bill/territory. Zach sends the drafted email or folds
   into the call.
3. **1.2-A stays PAYMENT-GATED** — verify invoice #NYQRTJPQ-0004 (Stripe auth needed) before touching.
4. **Sean Wing close-loop window** ends 2026-08-30 — /recoil-close vs `2026-08-23-sean-wing.json`;
   counterpart-gauntlet the parked note before any send.
5. Carried: 3 orphan seeds (human curation) · GH Actions billing (Zach-only) · ziggurat
   trailhead/key-0 (~10 lines) · tao proverbs 066/067 · lattice --regenerate (human-owned).

||||||| fae582fb

> _v3.44.0 (Ahmed) relocated to `_ARCHIVE/handoffs.md` on 2026-08-27; v3.43.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-27; v3.42.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-26; v3.41.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-26; v3.40.0 on 2026-08-23; v3.39.0 + v3.38.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-19; v3.37.0 (Comet resume) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
