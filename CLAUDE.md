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

# Handoff — v3.7.0 (2026-07-17)

> **For Claude Code:** active pickup point. v3.6.0 above is preserved for history.

## What changed since v3.6.0

### chan.arcs.care built end-to-end — Prophet/Chan Suh discovery-call artifact

Iterated across ~20 commits in one session, starting from an `/ultrareview`-style audit of
the existing page against the Mike Lemon recoil report:

- **Player/Coach/Pacecar** identity frame + prior-terrain (pre-ARCS) résumé receipts, visually
  separated from the ARCS-build era
- **Instrument-panel section** — 12 design principles (traceability, anti-hallucination,
  anti-sycophancy, provenance, etc.), each stating where it's actually enforced, plus a
  hand-authored SVG of the real compounding architecture loop (question → L0–L5 pipeline →
  receipt → outcome → calibration → sharper next decision)
- **Conductor-lane telemetry** — real git-trailer data (which Claude model authored each
  week's commits) as a tabbed view against commit cadence, with click-to-unlock narrative
  cards (the 5 quiet design weeks; "building at the edge" model-rotation story)
- **16-slide presentation mode** — SEEN/HEARD/VIBE-CHECK discovery structure, provenance-graded
  per slide (glow = confidence, using the canonical `--glow-*` tokens), Maya Lin-style
  pointer-terraformed moiré topography, 2.5D isometric floor, a left-edge "fathom" progress
  rail, chrome that auto-hides after 2.6s idle, right-click on the closing slide as an escape
  hatch back to slide 1. A wireframe Möbius-strip opening flight was built, then **removed**
  on explicit budget-conscious direction — land-the-plane took priority over the animation.
- **Full design-system conformance pass** — pulled the canonical token file
  (`colors_and_type.css`) live from the "ARCS OS - Design System" Claude Design project via
  `DesignSync`, migrated all 81 freehand font-sizes onto the canonical 8-step `--text-*`
  scale, swapped fonts to Inter + JetBrains Mono (the only two the project's own adherence
  linter permits), tokenized radii to the canonical 3/6/10/16/999 scale
- **Progressive disclosure** — FOCUS-mode-by-default (only section 1 open, rest collapsed to
  headline + one-line TL;DR), EXPAND ALL as the alternate control
- **PII removed** (email + phone from the footer); `noindex, nofollow` confirmed already
  present, no `robots.txt` override exists on either domain

### status.arcs.care — standalone fork

Forked from `chan.html` via anchor-based excision (not hand-editing): Prophet-specific
content (echo-map, Player/Coach/Pacecar frame, prior-terrain creds) and the entire
presentation deck (~250 lines of JS/DOM/CSS) surgically removed; sections renumbered 01–07.
Routed via `next.config.ts`. **Gotcha:** the deploy script's domain pre-flight reported
`status.arcs.care` already assigned when it wasn't — had to attach it to the Vercel project
directly via the API (`POST /v10/projects/{id}/domains`) before it would resolve.

### Two real mobile bugs — found only from actual device photos, not simulator resizing

The user sent 3 HEIC screenshots from a real iPhone. **The Read tool cannot render HEIC
directly** (returns raw container metadata) — converted via `sips -s format png` first, every
time, before they could actually be viewed.

1. `.echo-mid`'s mobile rule used `transform: rotate(90deg)` on a full-width flex box to turn
   "↔" into "↕" on the stacked single-column mobile layout. **CSS transforms repaint an
   element in its rotated orientation but do not change its layout footprint** — the rotated
   glyph + its border lines visually overflowed above/below the short-wide box they still
   occupied, reading as a disconnected floating icon with odd gaps. Fixed by dropping the
   rotation entirely and swapping the glyph via `font-size:0` + `::after` content instead.
2. The architecture-loop SVG diagram is legitimately wider than a phone screen and
   horizontally scrollable (`overflow-x: auto`), but mobile Safari hides scrollbars until an
   active drag, so the hard-truncated right edge read as broken content. Added a right-edge
   fade mask + explicit "SWIPE FOR THE FULL LOOP" hint, mobile-only, gated so it only shows
   when the container is actually scrollable.

Also fixed in the same pass (caught from a desktop screenshot, before the mobile-photo
round): presentation chrome (top/bottom bars) was drifting left/right slide-to-slide because
`flex; justify-content: space-between` centers the middle block *relative to the width of its
flanking siblings*, not true viewport center — act-labels and chips vary a lot in text length
slide to slide, so the centered readout visibly jumped. Converted both bars to CSS grid
(`1fr auto 1fr`) with **explicit `grid-column` pins** — required because mobile hides some
children via `display:none`, and grid auto-placement would otherwise shove the survivors into
the wrong column. Verified across all 16 slides: identical center x-coordinate every time.
Also: the isometric floor's `perspective(560px)` was a fixed px value that broke down on an
ultrawide monitor and at high browser zoom (a fixed focal length against a much-wider element
swings the far edges out past the frame) — changed to `perspective(70vh)` so it scales with
viewport height regardless of width or zoom.

## Session pattern worth repeating

Every fix in this session was verified against the **live production domain** via direct
`curl` grep for the specific CSS rule / string that changed — not just "deploy succeeded."
Several deploys landed on a stale `main` mid-session because another concurrent session
pushed commits in between fetch and merge; the fix each time was `git fetch origin main -q
&& git rebase origin/main` on the feature branch before re-attempting the fast-forward merge,
never a force-push over the other session's work.

## File status

```
public/chan.html    ✅ ~20 commits, fully verified live on chan.arcs.care
public/status.html  ✅ NEW — forked from chan.html, verified live on status.arcs.care
next.config.ts      ✅ status.arcs.care route added
```

## Last confirmed commit (arcs-v9 main)

`c536792` — fix(chan): mobile echo-mid connector no longer overflows its row; scroll cue on
the architecture diagram [NCI:SKIP]

## Blocking

NONE. Two untracked files sit in the main worktree from unrelated prior work
(`_DECISIONS/ADR-026-debrief-calendar-invite-vs-email.md`, `test_prisma_direct.js`) — not
touched this session, flagged for whoever owns that thread to commit or discard.

## Next session starts at

`/handoff-pickup` → no open thread on chan/status.arcs.care (last ask was mobile QA, verified
live). Otherwise: julia.arcs.care drill feature OR governance backlog #3 (log consolidation,
unblocks #6 DEWY commit stamp) remain open from prior sessions.

---

# Handoff — v3.8.0 (2026-07-19)

> **For Claude Code:** active pickup point. v3.7.0 above is preserved for history; v3.6.0 and older were
> relocated to `_ARCHIVE/handoffs.md` per the lean-file policy this session established.
> Branch `claude/token-efficiency-audit-ip3l3x` — **MERGED to main** (verified 2026-07-19: main contains
> the lean CLAUDE.md ≈3.7k tok + MEMORY.md ≈6.5k tok; branch is an ancestor of `main`).

## What this session did (17 commits, `c2eaf80`..`117fcf0`)

A token/budget efficiency audit that turned into a fix chain. Full narrative in `MEMORY.md [v3.8.0]`;
per-topic detail in the `_PATTERNS/2026-07-19-*` docs.

- **Audit + Fix #1/#2:** the real #1 token drain was the append-forever CLAUDE.md/MEMORY.md loaded every
  session (~24.6k–39k tok), not the Sentinel. Split dead history to `_ARCHIVE/`; CLAUDE.md 19.8k→3.6k,
  MEMORY.md 14.8k→5.8k; amended the append-only policy to lean-working-file + archive.
- **ADR-035:** ratified the real Commit-NCI rubric (5 lenses); wired `nci-scoring` skill + `/nci-commit` +
  `/drift-check`. Added `/rca` (triage-gated root-cause command).
- **Tech-debt batch** (`_PATTERNS/2026-07-19-tech-debt-batch.md`): A1 console cleanup, A5/A6 fixes, B1
  diagnosed clean, A2/A3/A4 triaged out. **B4** build-red root-caused to shell `NODE_ENV=development` →
  pinned `NODE_ENV=production` in the build script (use `npm run build`, not bare `npx next build`).
- **B2:** implemented the spec 5-lens `nci_by_lens`/`nci_grade` (additive), surfaced weak-lens in the brief,
  added a `stop_reason` truncation guard.
- **Security:** `_PATTERNS/2026-07-19-threat-assessment.md` + `src/lib/sanitize.ts` (unit-tested 8/8) —
  trust boundary at every recursive rung against injection cascade.

## Open items (also in `_QUEUE/PENDING.md`)

- ~~**Merge this branch to main**~~ ✅ DONE 2026-07-19 — merged; lean CLAUDE.md/MEMORY.md confirmed on main.
- **Out-of-band** (`_PATTERNS/2026-07-19-out-of-band-actions.md`): Sentinel — DISABLED 2026-07-19; rebuild
  **report-only** from the `arcs-decision-receipts` env using the full recipe in
  `_PATTERNS/sentinel-rebuild-spec.md`. Also: SageTrace RLS (Supabase CLI), connector/env/DNS/key items,
  Dan Pascone gate.
- **In-repo follow-ups:** cadence lens from time-ROM; HOLD gate at NCI<40 (overlaps the Calibrate HOLD gap).

## Honesty flag

All compass-side changes are build + typecheck + unit-tested, but **NOT driven via a live compass call**
(no `ANTHROPIC_API_KEY` in the cloud session). Verify end-to-end after merge/deploy.

## Last confirmed commit

`117fcf0` — feat(security): trust boundary at every recursive rung.

## Next session starts at

`/handoff-pickup` → merge is done; pick an out-of-band item (Sentinel rebuild, SageTrace RLS) or the
B2 cadence/HOLD-gate follow-up.

---

# Handoff — v3.10.0 (2026-07-19)

> **For Claude Code:** active pickup point. v3.8.0 above is preserved for history.
> Version realignment: CLAUDE.md was at v3.8.0 while MEMORY.md was at v3.9.0 (two
> concurrent sessions, one tracker each — the pathogen this very session codified).
> Both realigned at v3.10.0. Full detail lives in `MEMORY.md` `[v3.10.0]`, not
> repeated here.

## What changed since v3.8.0

**The serialization pathogen family** — codified, ratified, and enforced in one arc:

- **ADR-033 DECIDED** (`_DECISIONS/ADR-033-serialization-pathogen-family.md`,
  GREEN/HIGH/REVISIT, ratified by Zach 2026-07-19). One axiom: a serialized belief
  is a tuple (claim, time, scope, warrant, obligations, dictionary); each family
  member is one coordinate dropped. Five members registered with receipts +
  enforcement points; 4-part admission gate stops taxonomy sprawl.
- **`runtime/specs/recoil-modes-v1.md` → v0.4.0** — three mandates: `readOrder` +
  `[SUPERSEDED]` markers + always-current cover (chronos); `validityBounds` with
  n-aware regime ladder, tails/edges excepted at any n (inductive-overfit);
  riskFlags `status` field, closure-is-an-explicit-write (open-loop).
- **`runtime/specs/call-brief-hooks-v1.md` → v1.1.0** — Task A/B read current
  state first; never quote a stratum unchecked.
- **Detective (`scripts/receipt_lookup.py`)** — superseded-skip, n-aware Read,
  validityBounds surfacing, and **`--sweep`**: first run found **52 open
  obligations / 20 reports / 0 ever closed** (oldest 18d, incl. a 10d-old HIGH).
- **First documented closure:** enforcement-parity ledger (stranded unmerged
  3 days; memory had it serialized as live law) merged as **ADR-034** (PR #63),
  renumbered per ADR-033's rule. Jurisdictions: ADR-034 ledger = repo/audit
  findings; `--sweep` = call-ledger obligations.

## Open from this thread

1. **Sweep backlog** — 52 open riskFlags await owner `DONE`/`WAIVED` writes.
2. **ADR-032 duplicate** — two files share the number; dedupe/renumber.
3. **Epistemic + etymology members** — registered with existing partial mechanisms
   only; dedicated enforcement (warrant field on banked claims; rename tombstones)
   not yet built.

## Last confirmed commits (this thread)

`9748048` · `15d71d8` · `9ce0dfc` · `09bb14b` · `5f181fc` (+ this handoff commit)

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → run `python3 scripts/receipt_lookup.py --sweep` and start
closing the oldest flags, or pick up any v3.8.0/v3.9.0 open item.
