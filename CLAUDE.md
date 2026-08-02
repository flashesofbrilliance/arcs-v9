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

# Handoff — v3.20.0 (2026-08-01)

> **For Claude Code:** active pickup point. Louisville build is DONE and the email is SENT.
> Default posture now is STOP, not continue. Read [[deploy-antipattern-grep-verified-ui]].

## What shipped (2026-08-01) — Louisville universe complete + follow-up sent

Full three-surface family, self-hosted on arcs.care (main @ `47b5700`):
- **L1** louisville.arcs.care (pitch suite) → **L2** /omakase (the evening, 9 courses) →
  **L3** /omakase/atom ("The Seed, Told Whole", 7 chapters). Host-agnostic rewrites; also
  omakase.arcs.care. Navigable both directions; leak_check orphan-gate enforces it.
- Tea house: 序 foreword (acknowledgement, not thank-you), Justin's milled live receipt +
  JSON download, seal-before-October CTA. Scroll+arrows (present mode removed).
- Evening: tea offered after dessert (the one open door), receipt in the take-home box.
- Suite eggs distilled to 🧧 + 🧾. Broker figures milled; canon-manifest pulled off public
  (RUIN leak, earlier commit); seed sentence consonant across surfaces.
- **Email SENT** to Justin, subject "One evening" (Zach edited a variant + sent). Deep-listen
  golden thread = "Lonely Mouth Social Club" P.S. (kuchisabishii). **Justin accepted the
  LinkedIn invite within minutes.**

`leak_check.sh` now carries ~13 gates, each a scar from a real incident this session
(withholding-vocab, decoded-payload, dead-anchor, orphan, seed-sentence, etc.).

## Open / next

1. **Louisville: let it breathe.** No follow-up assigned. If Justin replies / proposes a time,
   /recoil-close the ex-ante at the session. Do NOT pursue or self-assign polish.
2. Prior untouched: Todd Hotes Zapier (blocked on Tidio plan), Ahmed ext send, showcase mirror.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New load-bearing memory: [[deploy-antipattern-grep-verified-ui]] (screenshot
before push; stop when done; don't build verification machinery for what one look answers).

---

# Handoff — v3.21.0 (2026-08-01)

> **For Claude Code:** active pickup point. Short, surgical session: closed a Vercel
> build-cost leak, generalized it, and formalized it as ADR-039. No counterpart work.

## What shipped (2026-08-01)

**Vercel deploy-cost leak closed + generalized + ADR'd.**

- **Root cause:** every commit to `main` was building — including docs-only. Logic was NOT
  inverted this time (that was the Jul-25 incident); the `commandForIgnoringBuildStep` exclude
  list was just **incomplete**. `docs(handoff)` commits touch `.claude/arcs-session-state.md`,
  and `.claude/` wasn't excluded (confirmed: `953effc docs(handoff): v3.20.0` built READY).
- **Fix:** added `":(exclude).claude"` to the ignore-step via `PATCH /v9/projects`. Full
  excludes now: `_MEMORY _PATTERNS _ARCHIVE _STATE .claude CLAUDE.md MEMORY.md AGENTS.md WORLD.md`.
- **Verified live:** docs-only commit `a1fed75` (`_PATTERNS/` only) → deployment **CANCELED**
  (skipped, no build); `public/` changes still build **READY**. Kept path-based, not
  `[NCI:SKIP]`-based — a `[NCI:SKIP]` polish commit can still touch shippable `public/`.
- **Vercel Agent audit:** both on-demand billing burners already OFF, read via
  `GET /v2/teams/<id>`: `agent.codeReview.auto.enabled=false`, `alertInvestigation.enabled=false`
  ("Investigate Anomalies Automatically" — the v3.18.0 "still ON" flag is now stale/corrected).
- **Generalized** into the impeccable skill as cost-discipline (SKILL.md → Cost discipline,
  v4.1.0; reference/init.md captures deploy-cost into PRODUCT.md; reference/live.md frames local
  iteration as the cost-correct loop).
- **ADR-039** (DECIDED, GREEN) — path-based ignored-build-step guardrail; index.json updated.
- **Memories consolidated** (updated, not duplicated): [[vercel-ignored-build-step-was-inverted]]
  (added the `.claude/` incident + live verification), [[vercel-config-via-cli-token-rest-api]]
  (agent toggles ARE API-readable — corrected "dashboard-only"), [[cost-efficiency-global-goal]]
  (path-not-message rule + local-iteration rule).

## Also cleaned up (leftover main-worktree working state, 2026-08-01)

Reviewed the three uncommitted items that had been sitting in the `main` worktree:
- **`ADR-026-debrief-calendar-invite-vs-email.md`** (untracked DRAFT, collided with tracked
  ADR-026 Debrief Delivery Fix) → renumbered to **ADR-040**, cross-linked, added to index. Still
  DRAFT (Decision pending Zach; calendar-invite-vs-email-only for the debrief close-the-loop).
- **`_ARTIFACTS/arcs-meta-audit-roadmap.html`** (+93 lines) → committed: a print-only "silkscreen
  on paper" stylesheet (inverts the dark cockpit to ink densities that survive a laser printer,
  forces SHARP fidelity on paper). Extends [[souvenir-ship-ritual]] to the roadmap deck.
- **`.impeccable/critique/…omakase.md`** (dual-agent critique, 18/36) → durable lesson banked as
  [[author-cosmology-over-guest-design-risk]]; its P0/P1 items were already resolved in the
  v3.20.0 omakase distillation. Critique file committed as the dated record.

## Also built this session (skills + code-verified ADR)

- **`/meta-audit` skill** (`.claude/skills/meta-audit/SKILL.md`) — codifies the 8-section Drift
  Sentry protocol from `_STATE/meta-audit-roadmap-v1.md` so any session runs one epoch
  consistently (Recoil → code-verified parity → gauntlets → Chi/Ma/Wuwei → stack-rank → append
  §8). Bakes in the hard-won non-negotiables (main-reachable epoch anchor, honesty gauge,
  weekly-and-small, verify-parity-from-code). Chose skill only; routine/workflow deferred.
- **Omakase critique → assembly rules.** Folded the omakase dual-agent critique into
  `.claude/skills/omakase-pipeline/SKILL.md` as a "Composition & assembly rules (the guest test)"
  section + wired into Step 4 (assemble against them) and Step 7 (guest-test lens) + anti-goal.
  The critique is now reusable rules, not a one-off. See [[author-cosmology-over-guest-design-risk]].
- **ADR-040 code-verified.** The debrief close-the-loop JTBD is **already shipped** (Option C,
  Stage 1): in-app `/debrief/[receiptId]` + `/api/receipts/[receiptId]/outcome` + scheduled
  Resend send (compass-time + long-horizon cron, loud logging, opt-in). NOT built: `.ics`,
  Google Calendar API. ADR-040 corrected to reflect this — the live question is only whether to
  add a calendar mechanism on top, at lower urgency than the original framing.

## Open / next

1. **Tao hosting work** — now safe to iterate; the leak that made every push a build is closed.
2. **ADR-040 is DRAFT** — the loop already closes via email+in-app; decide whether a calendar
   mechanism (.ics or Google Calendar) is worth adding, once there are ≥20 real (non-dev-test)
   debrief opportunities to measure against.
3. **Optional: schedule `/meta-audit` as a weekly routine** — deferred (needs a human toggle;
   a prior claude.ai "Drift Sentinel" routine was DECIDED-disabled; scheduled runs add spend).
3. Prior untouched: Louisville let-it-breathe (no follow-up unless Justin replies); Todd Hotes
   Zapier (blocked on Tidio plan); Ahmed ext send; showcase mirror.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. New: ADR-039 (deploy cost guardrail). The ignored-build-step exclude list is
path-based — add a path when a new non-shipping file class enters the repo.
