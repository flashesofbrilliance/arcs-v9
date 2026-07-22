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
6. **EXOGENOUS FORGE** — no agent self-validates; hardened claims ground against something *external to the lattice*, never its own coherence (diamonds validating diamonds = capture); controls that police the agent are owned by *not-the-agent*; signal = derivation-independence graded by substrate-disjointness; lens-plural but not relativist. Subordinate to NOTOMATION. Full always/sometimes/never guardrails: `_DECISIONS/ADR-038-exogenous-forge.md`

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: the interactive page is **LIVE on main** — `src/app/observatory/page.tsx`
(commit 4460bce), a real App Router page. NOTE: it uses hardcoded data arrays, not the
`datasets.json` hot-swap ingestion that lives ONLY in the static `public/observatory/` demo; the old
static-demo rewrite was removed (see `next.config.ts:6-7`). Hosting new telemetry on it needs
ingestion code, not free reuse.

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

# Handoff — v3.12.1 (2026-07-21)

> **For Claude Code:** active pickup point. v3.12.0 above preserved. Closes the v3.11.0 /
> v3.9.0 standby auth-loop test — full history now in `_ARCHIVE/handoffs.md`.

## What shipped (this thread, 2026-07-21)

**Production auth-loop test — closed, verified live, full loop.** The standby item from
v3.11.0 (drive "Sign in to keep" end-to-end, confirm the anon-share persist fix from PR
#121 actually lands a user on `/receipt/<id>`) is done:

- First attempt used the Claude Browser pane + the Gmail MCP connector. Auth itself worked
  (operator clicked the real email link, landed on `/dashboard`), but the Gmail MCP tool's
  text extraction **deterministically corrupts the `=` immediately before the `token=`
  query param** on every send (verified twice, reproducible, unrelated to token content —
  looks like a quoted-printable line-wrap decoding bug in that connector, not an
  arcs.care/Resend send-side defect). This broke the magic-link URL and, separately,
  because the operator opened the link in a different browser context than the one that
  viewed the share link, the `arcs_pending_save` localStorage flag wasn't present there
  either — so that run only proved auth, not the claim path.
- Full reproduction done via the **Claude-in-Chrome MCP** (operator's real Chrome, already
  signed into Gmail) instead: visited the `/brief/share#...` link → "Sign in to keep" →
  entered email → sent magic link → opened Gmail natively (no text-extraction step,
  clicked the real DOM anchor) → landed authenticated on
  **`/receipt/cmrupjbyk000104ljq1swek49`**, rendering the exact shared test bearing.
  Same-tab-group continuity kept `arcs_pending_save` intact, so `ClaimAnonymousReceipts`
  (`src/components/ClaimAnonymousReceipts.tsx`) fired correctly end-to-end — confirms PR
  #121 works exactly as designed, not just by code inspection.
- **Note for anyone touching Gmail-via-MCP for arcs.care emails going forward:** prefer
  driving Gmail through a real browser tool (Claude-in-Chrome or the operator's own client)
  over parsing email body text through the Gmail MCP connector when a URL/token in the
  body matters — the corruption above is silent (no error, just wrong characters) and easy
  to miss.

## Open from prior handoffs (untouched this thread)

- v3.11.0 items 1–2 (ledger management archive/reset-first; authenticated `/recoil` index)
  — still open, operator-approved, not started.
- v3.11.0 "glow strays" sweep — still open.
- Todd Hotes / PRL Resins (v3.12.0) — still awaiting his post-Wednesday reply, untouched.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → check for a reply from Todd post-Wednesday (see v3.12.0). No other
gating work; ledger-management and the authenticated `/recoil` index remain the next
build-ready items whenever picked up.

---

# Handoff — v3.13.0 (2026-07-22)

> **For Claude Code:** active pickup point. v3.12.0 (Todd Hotes) relocated to
> `_ARCHIVE/handoffs.md` per the lean-file policy; v3.12.1 preserved above. **Version note:** a
> `v3.14.0` label appears in an earlier commit message (`a6d4c20`, a divergent branch) but never
> entered this worktree's handoff chain — this file's chain is monotonic at v3.13.0; reconcile the
> numbering at next consolidation. Full session proof: the two live Artifacts + `_DECISIONS/ADR-038`.

## What shipped (this thread, 2026-07-22)

**ROM Primitive #6 — THE EXOGENOUS FORGE — inscribed, dogfooded, committed** (`902fb86`, on branch
`claude/harness-build-optimization-f52489`, pushed; preview-only, production untouched).

Origin: a "look at this repo (`harness-engineering`), anything useful for ARCS?" scout that
excavated — via a long adversarial dialectic — a constitutional invariant rather than a build.
Diagnosis: the agent's opening build-list *was* the failure mode; symptom → mechanism
(proxy-reward-hacking) → **disease: groundlessness + trained helpfulness-compulsion** (tell:
recurrence-in-new-costumes).

- **ROM #6 in CLAUDE.md** + full always/sometimes/never guardrails in
  `_DECISIONS/ADR-038-exogenous-forge.md`. Law: *no agent self-validates; hardened claims ground
  against something external to the lattice; controls that police the agent are owned by
  not-the-agent; lens-plural but not relativist.* Subordinate to NOTOMATION.
- **Dogfood — PASS.** Forged the CLAUDE.md domain-topology claim against `get_deployment(arcs.care)`:
  the 4 documented domains are served, but reality returns **~30 aliases** — the doc had drifted by
  omission. External grounding caught it; ADR-038 records the run.
- **`/thread-recoil` skill** (`.claude/skills/thread-recoil/SKILL.md`) — session belief-update
  ledger, `simple|rich|deep` depth pass-through; self-guards against the disease (only counts
  externally-forced belief changes). Queued for open-source (pending genericization).
- **3 memories banked** (auto-memory): `control-integrity-described-vs-wired`,
  `cognitive-division-of-labor-pruned-lattice`, `external-artifact-eval-ground-and-skeptic-route`.
- **2 live Artifacts:** Exogenous Forge architecture diagram + belief-update ledger (proof that
  7/7 priors moved on external data, 0 on internal re-coherence).

## Open from this thread

1. **ADR-038 dogfood** — done on (a) domain-topology; operator may add targets (selection-receipt
   spec / a handoff claim). Not gating.
2. **`/thread-recoil` open-source** — queued; needs a genericization pass (strip ROM/ADR/DEWY/
   arcs.care refs) + em-dash/sauce gate before publish. Held (irreversible).
3. **Version-numbering drift** — `v3.14.0` (git-log) vs `v3.13.0` (this chain); reconcile.
4. **PR** — feature branch pushed; no PR opened.

## Open from prior handoffs (untouched)

- Todd Hotes / PRL Resins (archived v3.12.0) — still awaiting his post-Wednesday reply.
- v3.11.0 ledger-management + authenticated `/recoil` index — still open.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup`. This session's work is committed + pushed on the feature branch (not merged, not
deployed). If continuing: pick a further ADR-038 dogfood target, or run the `/thread-recoil`
genericization pass for open-source. Otherwise Todd's reply remains the standing client thread.
