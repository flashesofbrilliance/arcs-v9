@AGENTS.md
@WORLD.md

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

# Handoff — v3.6.0 (2026-07-08)

> **For Claude Code:** active pickup point. v3.5.0 above is preserved for history.

## What changed since v3.5.0

### Consolidation audit — arcs-decision-receipts → arcs-v9 COMPLETE

Two commits on main:

**`cf8b084`** — initial consolidation:
- `runtime/specs/field-os/` — 9 field OS spec files from arcs-decision-receipts (artifacts 01–07, jtbd-master-map, arcs-thread-master-report, DRIFT_LOG)
- `next.config.ts` — added missing fanatics.arcs.care and token.arcs.care subdomain rewrites
- `public/templates/call-brief-template.html` — canonical parameterized template with `{{PLACEHOLDERS}}` and authoring workflow comment header
- `_STATE/snapshot.json` — added `ui_artifacts` section (13 active call briefs + ui-kit inventory) and `memory_shards` section

**`b7883fb`** — bar-raiser corrections (3 flags resolved):
- `scripts/kryptonite_scorer.py` → `operators/kryptonite_scorer.py` (atomic decision component, not utility; operator contract header added)
- `scripts/waveform_optimizer.py` → `operators/waveform_optimizer.py` (same)
- `_CANON/arcs-v9-additional/{4 docs}` → `_CANON/living/` (primary doctrine promoted out of supplement folder)
- `_MEMORY/` created with 5 git-tracked product intelligence shards (replaces `~/.claude/projects/` which is machine-local / invisible to cloud sessions)

### Decisions locked (bar-raiser review)

- **monomath-compiler** + **gold-coast**: separate standalone repos, NOT arcs-v9 (different products, would balloon monorepo scope)
- **index.html / deep-activate.html**: audit provenance before porting — unknown active use case
- **field-os specs**: `runtime/specs/field-os/` (not `_ARCHIVE/`) — still-relevant reference spec, not dead history
- **arcs-decision-receipts**: do NOT archive yet — confirm nothing missed first

## File status

```
public/templates/call-brief-template.html       ✅ NEW — canonical template with {{PLACEHOLDERS}}
runtime/specs/field-os/                          ✅ NEW — 9 field OS spec files
_CANON/living/ARCS-v9-Canon-Operational.md      ✅ PROMOTED (was arcs-v9-additional/)
_CANON/living/ARCS-Codex-v8.5.md               ✅ PROMOTED
_CANON/living/ARCS-Positioning-JTBD.md          ✅ PROMOTED
_CANON/living/ARCS-Technical-Overview-April2026.md ✅ PROMOTED
_MEMORY/                                         ✅ NEW — 5 git-tracked intelligence shards
operators/kryptonite_scorer.py                   ✅ MOVED from scripts/
operators/waveform_optimizer.py                  ✅ MOVED from scripts/
_STATE/snapshot.json                             ⚠️ 6 DAYS STALE — run /init-state-sync
```

## Last confirmed commits (arcs-v9 main)

```
b7883fb — chore(consolidation): bar-raiser corrections — operators/, _CANON/living/, _MEMORY/ [NCI:SKIP]
cf8b084 — chore(consolidation): port arcs-decision-receipts unique content [NCI:SKIP]
```

## Next session starts at

`/handoff-pickup` → `/init-state-sync` to refresh stale snapshot → then: julia.arcs.care drill feature OR governance backlog #3 (log consolidation, unblocks #6).

---

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
