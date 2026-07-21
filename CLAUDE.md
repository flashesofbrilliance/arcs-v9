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

# Handoff — v3.10.0 (2026-07-19)

> **For Claude Code:** active pickup point. v3.9.0 above preserved; v3.8.0 relocated to
> `_ARCHIVE/handoffs.md` per the lean-file policy. (A tracker drift observed mid-session —
> CLAUDE.md at v3.8.0 while MEMORY.md was at v3.9.0 — was healed concurrently by the
> v3.9.0 session's own handoff; noted here because it is a live receipt of the exact
> pathogen this session codified.) Full detail: `MEMORY.md [v3.10.0]`.

## What changed (this thread, 2026-07-17→19)

**The serialization pathogen family** — codified, ratified, enforced:

- **ADR-033 DECIDED** (`_DECISIONS/ADR-033-serialization-pathogen-family.md`,
  GREEN/HIGH/REVISIT, ratified by Zach 2026-07-19). One axiom: a serialized belief is a
  tuple (claim, time, scope, warrant, obligations, dictionary); each family member is one
  coordinate silently dropped. time→chronos-sequencer · scope→inductive-overfit ·
  obligation→open-loop decay · warrant→epistemic-sequencer · dictionary→etymology-sequencer.
  4-part admission gate stops taxonomy sprawl.
- **`runtime/specs/recoil-modes-v1.md` → v0.4.0** — readOrder + `[SUPERSEDED]` markers +
  always-current cover (chronos); `validityBounds` {n, conditions, stationarity} with the
  n-aware regime ladder, tails/edges excepted at any n (inductive-overfit); riskFlags
  `status` OPEN/DONE/WAIVED — closure is an explicit write, never silence (open-loop).
- **`runtime/specs/call-brief-hooks-v1.md` → v1.1.0** — read current state first; never
  quote a stratum without a superseded-marker check.
- **Detective** (`scripts/receipt_lookup.py`): superseded-skip, n-aware Read,
  validityBounds surfacing, and **`--sweep`** — first run: **52 open obligations across
  20 reports, zero ever closed** (oldest 18d; incl. a 10-day-old HIGH).
- **First documented closure:** enforcement-parity ledger (stranded unmerged 3 days;
  memory had it serialized as live law) merged as **ADR-034** (PR #63), renumbered per
  ADR-033's own rule. Jurisdictions: ADR-034 ledger = repo/audit findings; `--sweep` =
  call-ledger obligations.

## Open from this thread

1. **Sweep backlog** — 52 open riskFlags await owner `DONE`/`WAIVED` writes.
2. **ADR-032 duplicate** — two files share the number; dedupe/renumber.
3. **Epistemic + etymology members** — partial mechanisms only; dedicated enforcement
   (warrant field on banked claims; rename tombstones) not yet built.

## Last confirmed commits (this thread)

`9748048` · `15d71d8` · `9ce0dfc` · `09bb14b` · `5f181fc` (+ this handoff commit)

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → live-verify anon-share (v3.9.0 honesty flag) or run
`python3 scripts/receipt_lookup.py --sweep` and start closing the oldest flags.

---

# Handoff — v3.11.0 (2026-07-20)

> **For Claude Code:** active pickup point. v3.10.0 above preserved; v3.9.0 relocated to
> `_ARCHIVE/handoffs.md` per the lean-file policy. Full detail: `MEMORY.md [v3.11.0]`.
> Interactive (local Claude Code) session — deployed live, unlike the prior cloud sessions.

## What shipped (this thread, 2026-07-20)

- **Anon-share "Sign in to keep" persist fix (PR #121, `403d109`).** The v3.9.0 honesty-flag
  follow-up: the shared bearing was recomposed one-time but NOT carried through sign-in — "keep"
  kept nothing. Now the onramp writes `arcs_pending_save` and `ClaimAnonymousReceipts` claims it
  post-auth → user lands on `/receipt/<id>` with the bearing saved. (One-time link + recompose
  verified live by operator; the full magic-link auth leg is the standby test below.)
- **Design-system glow tuning, two passes** (`8429f2e` then `cfbc483`). Operator feedback: glow
  too hot across the board. Pass 1 — `signalGlow()` alphas halved (.55–.6 → ~.28) + bloom blur
  cut ~33% (Gauge 16→11px, Card/Badge 12→8px, recoil `_tokens.css` 12→5px). Pass 2 (eyeball) —
  gauge bloom eased back 11→13px, accent card glow reduced, `TrueNorthPanel` given real
  glassmorphism (`backdrop-filter: blur(14px)` + translucent blue fill), Field/select left as-is
  (operator confirmed correct). Every change verified against **live computed styles**, not by eye.

## Open items (operator-approved, not started)

1. **Ledger management** — give users archive + reset-reflection before hard-delete. Build order
   confirmed: **archive/reset first, hard-delete last** (WORLD.md: receipts are frozen positions;
   soft-retire preserves Observatory/lineage, true erasure is the explicit escalation).
2. **Authenticated `/recoil` index** — a ledger of internal recoil/precall briefs behind OAuth.
   Build order confirmed: **index the existing brief documents first** (data already in
   `snapshot.json → ui_artifacts`), DB-backed entities later. Also improves security posture over
   the current per-name password gates.

## Standby (needs operator go)

- **Production auth-loop test** — drive "Sign in to keep" end-to-end via the Gmail connector
  (read the magic-link email, click it, confirm `/receipt/<id>`). Closes the v3.9.0 honesty flag.
  Needs explicit go + confirm `zach.harris@gmail.com`. Authenticates a session + writes one
  `EPHEMERAL_SAVE` test receipt.
- **Glow strays** — sweep hardcoded glows the tokens didn't reach (neutral `∞` gauge still at
  rgba(160,180,210,.35), observatory page, receipt widget, loaders) for full consistency.

## Concurrency note

Another thread committed on main during/after this session (`4bf8043` sentry inchworm, `efc836a`
meta-audit) plus two untracked strays (`_DECISIONS/ADR-026-*.md`, `test_prisma_direct.js`) — NOT
this session's, left untouched. `ls _DECISIONS/` + rebase on origin/main before any push.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → start ledger-management (archive/reset) or the authenticated `/recoil` index;
or run the standby auth-loop test to close the v3.9.0 flag.

---

# Handoff — v3.12.0 (2026-07-20)

> **For Claude Code:** active pickup point. Meta/open-source session, on the
> `claude/code-skills-open-source-36bde4` worktree branch (NOT main) — did not touch the ARCS
> product. v3.11.0 above preserved. Lean-policy archive-shuffle of v3.10.0 deliberately skipped
> (this branch may not merge; shuffling CLAUDE.md's hot path here is conflict risk, not value).
> Full detail: auto-memory `project-open-source-skills-queue.md` + `_STATE/snapshot.json → open_source`.

## What shipped (this thread, 2026-07-20)

- **Resumeware track opened.** Surveyed all ~19 ARCS Claude Code skills/commands for open-source
  fitness (craft × generalizes × safe-to-publish). Ranked; picked `rca` as the fast win.
- **`rca-skill` LIVE** — extracted `/rca` (originally `.claude/commands/rca.md`), scrubbed fully
  generic (0 internal-ref leaks, 0 em-dashes per the no-em-dash rule), ran a full
  **BAR/LAB/KKL/COURT/Funhouse gauntlet** on it (only real catch = em-dashes → en-dashes),
  repackaged as a standalone root-level repo (skill at repo root → `git clone <url>
  ~/.claude/skills/rca` installs it), README with use-cases + how-to + sample run. Shipped public:
  **github.com/flashesofbrilliance/rca-skill** (local: `/Users/zharris/rca-skill`).
- **Staging convention.** `open-source/rca/` kept in this worktree (committed `0f961ee`) as the
  tracking area for future candidates.

## Open from this thread (the open-source queue)

1. **NCI trio** — `nci-scoring` + `nci-commit` + `drift-check`. Inline the ADR-035 rubric so it is
   self-contained, then extract as its own repo.
2. **teardown gauntlet + `scripts/teardown_eval.py`** — highest craft signal, heaviest scrub:
   real client names, arcs.care deploy mechanics, and the first-name password-gate scheme must all
   come out before it can ship.

## Last confirmed commits (this thread)

`0f961ee` (staging + snapshot; on the code-skills-open-source branch). The rca-skill repo has its
own history (`dea608e` initial) at `/Users/zharris/rca-skill`, pushed to GitHub.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → continue the open-source queue (NCI trio next), or return to the product
backlog (ledger-management / authenticated `/recoil` index / v3.9.0 auth-loop test).

---

# Handoff — v3.13.0 (2026-07-20)

> **For Claude Code:** active pickup point. Same branch/session as v3.12.0 — round 2 of the
> open-source track. v3.12.0 above preserved (this branch may not merge to main yet; PR #122
> open). Full detail: auto-memory `project-open-source-skills-queue.md` + `_STATE/snapshot.json
> → open_source`.

## What shipped this round

- **`fix-toolbar-comments-skill` LIVE** —
  github.com/flashesofbrilliance/fix-toolbar-comments-skill, same extract→scrub→gauntlet→publish
  pattern as `rca-skill`. Only catch: em-dashes (fixed, same as last time — worth checking by
  default on every future candidate).
- **Sauce-aware queue rerank.** Reassessed the whole open-source queue against "helpful to others
  + doesn't leak ARCS's proprietary method" instead of pure portfolio-craft:
  - **Upgraded:** state-sync bundle (`init-state-sync` + `handoff` + `handoff-pickup`) — most
    broadly useful, zero product IP once the DEWY-specific snapshot fields are genericized. Next
    candidate.
  - **Downgraded to HOLD:** the NCI trio (`nci-scoring`/`nci-commit`/`drift-check`) — these ARE
    the ADR-035 rubric (weights/thresholds), not a pattern that merely uses it. Previously
    recommended as the strong second release; that recommendation is reversed.
  - **Confirmed HOLD:** teardown/precall-brief/recoil-report family (client data + gauntlet
    operators are sauce), arcs-research/dewy-stub/receipt-book-curator (DEWY receipt shape is
    sauce; only a genericized-to-plain-ADR version would be safe).

## Last confirmed commits (this thread)

`966bce1` (this round's staging + snapshot). `36a2b8e`/`0f961ee` from the prior round. PR #122
(main ← this branch) still open from the prior round.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → genericize + extract the state-sync bundle, or merge PR #122 first if that
hasn't happened yet.

---

# Handoff — v3.14.0 (2026-07-21)

> **For Claude Code:** active pickup point. Same `claude/code-skills-open-source-36bde4` branch
> (PR #122 open) — round 3 of the open-source track + closed the own-data PII scrub. v3.13.0 above
> preserved; append-only on this branch (may not merge; no archive-shuffle). Durable state:
> auto-memory `project-open-source-skills-queue.md` + `_STATE/snapshot.json → open_source` +
> `_STATE/teleport-brief.md` (both PENDING tasks now marked DONE).

## What shipped this round

- **`token-savings-bank` LIVE** — github.com/flashesofbrilliance/token-savings-bank. Budget-mode
  operating skill (model-tier routing / batch / inline-vs-subagent / explicit checkpoint).
  **Authored fresh, zero extraction.** Renamed from "tokenmining" (Zach: reads as crypto). Ran a
  2-round adversarial gauntlet (3 agents → FIX-THEN-SHIP → 8 fixes incl. a SECURITY guardrail
  against checkpointing secrets; confirming pass caught a README regression). Local:
  `/Users/zharris/token-savings-bank`.
- **`linkedin-connections-toolkit` LIVE** — github.com/flashesofbrilliance/linkedin-connections-toolkit.
  Generic `Connections.csv` parser + plain analysis (years/companies/seniority/staleness), CLI +
  library, stdlib-only, synthetic sample. **Authored fresh (NOT extract-and-redact** — the private
  LinkedIn mining suite's method IS the sauce). 3-agent code gauntlet + confirming pass; one agent
  failed on first run (transient, zero tool calls) and was re-run; **5 real correctness bugs caught
  and fixed pre-ship** (substring seniority misclassification, vice-president bucket, staleness
  off-by-one, locale-dependent date parsing, loose header detection). Local:
  `/Users/zharris/linkedin-connections-toolkit`.
- **Own-data PII scrub (was a separate pending task): DONE on `main`** (frosty-kepler worktree,
  `0343dfb`, pushed). 5 scripts → placeholders + env-driven `CONNECTIONS_CSV`; report counts made
  dynamic; new `scripts/README.md` (how-to / runtime / deps / arcs_cli passthrough params). Current
  state only, no history rewrite. `deploy-prod.sh` local paths left intentionally.
- **Staging + state:** `open-source/token-savings-bank/` + `open-source/linkedin-connections-toolkit/`
  committed (`37bf5d5`, `a269159`), branch pushed. snapshot `open_source` now lists 5 shipped,
  queue `[]`.

## Open-source queue: EMPTY

All teleport-brief items shipped. Remaining candidates all sit in `hold_sauce_risk` (NCI trio,
teardown/precall/recoil family, arcs-research/dewy-stub/receipt-book-curator, arcs-brand-manager,
the scanner suite) — do NOT publish without a genuine genericization pass; several ARE the sauce.

## Ship-recipe lesson reinforced this round

The confirming pass after the main gauntlet earns its cost (caught a README regression on the skill;
confirmed the toolkit fixes held). And the model's own quick self-verify can miss a bug the gauntlet
then catches (a plausible-looking seniority count hid a misclassification). Gauntlet code toolkits by
*running* them, not just reading.

## Blocking

NONE. PR #122 still open (main ← this branch); merge when ready, or continue product backlog
(ledger-management / authenticated `/recoil` index / v3.9.0 auth-loop test — all on `main`).

## Next session starts at

`/handoff-pickup` → open-source queue is empty; either merge PR #122 or return to the product
backlog on `main`.
