# ARCS Session State

**Last updated:** 2026-07-17 (v3.7.0)
**Environment:** Claude Code (local), worktree `chan-arcs-card-milestones-5f7790`
**Branch:** `claude/chan-arcs-card-milestones-5f7790`, merged to `main`, pushed to `origin/main`
**Last commit (arcs-v9):** c536792 — fix(chan): mobile echo-mid connector no longer overflows its row; scroll cue on the architecture diagram

## v3.7.0 delta (this update) — see MEMORY.md [v3.7.0] for full detail

- **chan.arcs.care built end-to-end** — Prophet/Mike Lemon/Chan Suh (CDO) discovery-call
  artifact. Player/Coach/Pacecar frame, instrument-panel (12 principles + architecture-loop
  SVG), conductor-lane telemetry (real git-trailer data on which Claude model wrote each
  week's commits), 16-slide SEEN/HEARD/VIBE-CHECK presentation mode (moiré topography,
  isometric floor, fathom rail, auto-hiding chrome), full ARCS-OS design-system conformance
  (Inter/JetBrains Mono, 8-step type scale, canonical tokens pulled live via `DesignSync`),
  FOCUS-default progressive disclosure with per-section TL;DRs.
- **status.arcs.care forked** from chan.html — Prophet content + presentation mode
  surgically removed for standalone build-status use. Domain had to be attached to the
  Vercel project directly via API; the deploy script's pre-flight falsely reported it
  already assigned.
- **PII removed** (email/phone from both footers). `noindex, nofollow` confirmed on both,
  no `robots.txt` override exists.
- **Two real mobile bugs found from actual iPhone photos** (HEIC — Read tool can't render
  it directly, converted via `sips` first): (1) a `transform: rotate(90deg)` connector
  visually overflowing its own grid row because CSS transforms don't change layout
  footprint — fixed via `font-size:0` + `::after` glyph swap instead of rotation; (2) the
  architecture SVG cutting off with no scroll affordance on phone widths — added a fade
  mask + explicit swipe hint, gated to only show when actually scrollable.
- **Presentation chrome drift fixed** — top/bottom bars used `flex space-between`, which
  centers content relative to flanking-sibling width, not true viewport center; slide-to-
  slide the readout visibly jumped as act-label/chip text length varied. Converted to CSS
  grid (`1fr auto 1fr`) with explicit `grid-column` pins (needed because mobile hides some
  children via `display:none`, and grid auto-placement would otherwise misplace the
  survivors). Verified: identical center x-coordinate across all 16 slides.
- **Isometric floor perspective fixed for ultrawide/zoom** — was a fixed `perspective(560px)`,
  which produces degenerate distortion against a much-wider-in-px element (ultrawide monitor)
  or a zoomed-in effective viewport; changed to `perspective(70vh)` so it scales with
  viewport height regardless of width or zoom level.
- Every fix in this session was verified against the **live production domain** via direct
  `curl` grep for the specific changed string/rule, not just "deploy succeeded."

## Open items carried forward (unrelated to this session)

- Two untracked files in the main worktree from other work, not touched this session:
  `_DECISIONS/ADR-026-debrief-calendar-invite-vs-email.md`, `test_prisma_direct.js`.
- julia.arcs.care drill feature (interaction model + who Jack/Jill/Boardy are still
  unclarified) — open since v3.5.0/v3.6.0.
- Governance backlog #3 (log consolidation, unblocks #6 DEWY commit stamp) — open since
  v3.1.0/v3.2.0.

## Blocking

NONE.

## Next session starts at

`/handoff-pickup` → no open thread on chan/status.arcs.care. Otherwise: julia.arcs.care
drill feature or governance backlog #3.
