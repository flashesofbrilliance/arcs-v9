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

# Handoff — v3.48.0 (2026-08-29)

> **Active pickup point — hyperstition close-out + engagement truing + molt reframe.** Continuation
> of the v3.47.0 evidence session. Everything below is on branch `claude/happy-cori-d4faaf`,
> [PR #193](https://github.com/flashesofbrilliance/arcs-v9/pull/193) OPEN (Zach merges = deploy of the
> post-3 miss-count update). Atlas republished (same artifact URL 9c336f5c).

## Shipped (this branch)
- **Ledger triage fold** — the 79-concept honesty ledger's 33 unbuilt rows sorted 4 ways
  (`_ARTIFACTS/vision-films-hyperstition/ledger-triage.md`): **5 BUILD** appended to
  `_QUEUE/induced-backlog.jsonl` (now 24 rows: R·C·S surfaces, validation probe ADR-059, IDEA loop
  ADR-058, kill-gate enforcement, adaptive presentation) · 4 FINISH · **9 MOLT** · 15 canon-resident.
- **Molt reframe (Zach ruling):** the 9 are not "retired" — they are **molted** (ADR-041 considered-molt
  + ADR-066 instance->class->invariant). The invariant re-manifested sharper (Signal Engine->recoil;
  own-the-engine->own-the-record; Rule-of-Fives->Y-gate; 101/201/301->graduation invariant). A molted
  shell is still provenance, not a retcon (witness 2026-08-23). Atlas SEDIMENT + triage reframed.
- **Two memory reflexes banked:** `pre-register-rule-before-counting` (commit the count-rule BEFORE
  reading the corpus — forking-paths guard, proven by the 19% hit-rate) and
  `molting-protocol-outgrow-scaffolding-not-retire` (molt-test before marking anything dead).
- **Engagements trued vs Gmail (pulse-check):** **Prophet CLOSED-LOST** (other candidate; went dark
  after Zach's Aug 4 follow-up). Closing note to **Cassandra Riley (criley@prophet.com)** DRAFTED as a
  Gmail draft ("Thank you, and closing the loop") + one-time reminder task set for **Fri Sep 4 10am ET**
  (`remind-send-prophet-close-note`) — review-and-send-yourself, NOT auto-sent. **Fanatics CLOSED-WARM**:
  **CJ Masopust (cmasopust@collectfanatics.com)** via **Chris LaMontagne** intro; role-design/timing
  miss (Boardy read: liked the work, no matching mandate — not a fit loss); loop already closed, door
  open (Growth+1). No owed reply. Both memory files updated.
- Commits: 58301a83 (pre-reg rule) · f50ecf48 (evidence completion) · 54a8ad5d (v3.47.0 handoff) ·
  bc3e4034 (triage) · 95426067 (molt reframe). Prior evidence work (ledger/null/phase-lock) from v3.47.0.

## Open (next session's first work)
1. **PR #193 merge** (Zach) — lands post-3 miss-count appendix + atlas edits + ledger/triage + molt.
2. **MEMORY.md is co-edited + ~1k over the soft budget** — a PARALLEL same-day session added ADR-071
   Möbius/triune/gravity + ROM-graduation memories concurrently (untracked shared state = advisory;
   did NOT fight the race). Owed: one single-owner `/consolidate-memory` pass to bring it back under
   17408B. All this session's additions verified present in the merged index.
3. Prophet close-note fires Sep 4 (draft staged); if that week slides it's low-stakes.
4. `lattice --regenerate` still owed (ADR count lattice 63 vs repo 66, epoch stale) — human-owned.
5. Carried from v3.47.0: human-gated PRL installs · Todd close-loop call · Sean Wing window (was
   2026-08-30) · 1.2-A payment-gated · orphan seeds · GH Actions billing · ADR-069 oracle audit ·
   ziggurat trailhead · tao 066/067.

# Handoff — v3.47.0 (2026-08-28)

> **Active pickup point — hyperstition evidence-completion session.** Ran the war-game panel's
> three settling exercises (wf_3ac81615-7e1). All three closed same-day; atlas republished to the
> SAME artifact URL; post-3 miss-count appendix rendered; branch claude/happy-cori-d4faaf, PR open.

## Shipped
- **Formal denominator:** extraction rule pre-registered + committed (58301a83) BEFORE reading
  transcripts; agent-classified vs live repo. **79 concepts: 15 MANIFESTED / 31 PARTIAL /
  26 SPEC-ONLY / 7 DEAD -> 19.0% headline, 58.2% with partials.** Ledger:
  `_ARTIFACTS/vision-films-hyperstition/concept-ledger.jsonl`. Atlas SEDIMENT tier + count strip +
  footer updated to counted truth (energy-scan row removed — it's LIVE at /scan, was mislabeled).
- **Dated-receipt search: NULL** (git log --all + full-text sweep, all film titles). Causation is
  now searched-and-not-found; common-cause null stands. Method: `dated-receipt-search.md`.
  Atlas strange-loop section records it.
- **Phase-Locked UPGRADED:** ADR-069 (PRL 1.2 closed receipt) IS the external/market vantage —
  row now "EXTERNAL VANTAGE BANKED · MEASURED OUT-OF-PHASE" (~2.1x; instrument real, lock not claimed).
- **NFTT post-3:** "Update, one day later: the miss count came in" appendix + fine-print amended;
  re-rendered via story_render (0 em-dashes). Deploys when Zach merges the PR.
- DEWY receipt: `_STATE/2026-08-28-hyperstition-denominator.dewy.json` — tier resolution:
  candidate-hyperstition -> RESOLVED MUNDANE on causation; the family owns the eight-month naming
  lag + honest 19%. ADR-070 falsifier: orthogonal, untouched, still awaiting its season.

## Open
1. **Merge the PR** (Zach) — post-3 update + atlas edits + ledger land on main, deploy is the merge.
2. Carried from v3.46.0: human-gated PRL installs · Todd close-loop call · Sean Wing window ends
   2026-08-30 · 1.2-A payment-gated · orphan seeds · GH Actions billing · ADR-069 oracle audit ·
   ziggurat trailhead · tao 066/067 · lattice --regenerate.
3. Memory index over budget (session-start warning) — run /consolidate-memory when convenient.

> _v3.46.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-29; v3.45.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-28; v3.44.0 (Ahmed) relocated to `_ARCHIVE/handoffs.md` on 2026-08-27; v3.43.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-27; v3.42.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-26; v3.41.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-26; v3.40.0 on 2026-08-23; v3.39.0 + v3.38.0 relocated to `_ARCHIVE/handoffs.md` on 2026-08-19; v3.37.0 (Comet resume) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
