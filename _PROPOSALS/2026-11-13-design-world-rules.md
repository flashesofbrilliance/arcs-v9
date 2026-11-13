---
version: 0.1.0
date: 2026-11-13
status: PROPOSED (rules only; DESIGN.md is not edited until Zach rules)
parent: _PROPOSALS/2026-10-30-instrument-construction-rules.md
---

# Camera, lighting and geometry rules for the ARCS world, tied to the Ziggurat

Why: Zach asked (2026-11-13) whether motion, camera and lighting rules exist, and for the design system to stay coherent across problem shapes, jobs, induced surfaces and renderings at increasing depth, true to the Ziggurat (the build atlas, claude.ai/artifact/NPmsyc96QtyByJD9gATtNg, snapshot 2026-11-12).

## What exists today (checked in the repo, 2026-11-13)

| Area | Where | State |
|---|---|---|
| Motion | `DESIGN.md` "Motion and safety"; `scripts/motion_policy_gate.py`; `--dur-*`, `--ease-out`, `--mo-*` in `_tokens.css` | Rules and a gate |
| Elevation and light | `DESIGN.md` "Elevation & Depth"; `--emboss`, `--deboss`, `--glow-*` tokens; the design system's "glow is an underlit LED, not ambient neon" | Tokens and prose, no named light direction |
| Camera | Design system README: Observatory iso tilt `perspective(1500px) rotateX(38deg)`, tilt only so tiles stay clickable. `WORLD.md`: "one isometric terrain tile" | One sentence, no rule, no gate |
| Render fidelity | `WORLD.md` render scale (weight, tracking, grain by Y state) | Rule, covers type and surfaces, not geometry |
| Geometry depth (polygons, edges, resolution) | none | Gap |
| Brand and audit | `arcs-brand-manager` command, `brand-line-producer` agent, Impeccable `audit`, `distill`, `polish`, `animate` | Exist; no routine pass over DESIGN.md or the kit |

## What the Ziggurat asks of the design system

- It is a stack: each tier rests on the one below, width = count of live jobs, the peak (income, W1 to W4) is what the rest holds up. W6 is "design atoms"; W8 base, W7 engine, W5 product and GTM. Phosphor (W9) sits beside the stack, not in it.
- Horizons NOW, NEXT, LATER, plus one-way doors, high ruin and blocked states, drawn with write-lock before commit.
- Its `look` document points at the design system but still carries an older light palette (ground `#f5f7fa`, good `#00875a`). The kit light palette is now cool slate; that dashboard needs a re-sync.

## Proposed rules (draft text for DESIGN.md, each marked with its basis)

**Camera.** One fixed isometric camera: tilt about the X axis only (the existing 38 degrees, perspective 1500px), no yaw, no roll, no dolly. Tiles stay clickable. With `prefers-reduced-motion` the camera is flat (0 degrees). Basis: stated in the design system README (existing); the no-yaw and reduced-motion clauses are proposed.

**Light.** One key light from above. A raised face carries a top-edge highlight and a bottom-edge shade (the `--emboss` tokens already do this); a recessed face is the inverse (`--deboss`). A glow is an underlit LED: tight blur at or under 16px, never a wide halo. Signal colour appears in the rim, the glyph and the label, never as a saturated fill. Basis: the tokens and the README rule (existing); "one key light from above" names what the tokens already imply (judgment).

**Depth ladder for geometry.** Fidelity follows the render scale, so a polygon-built surface draws coarser in fog and sharper at the clarity ridge: GRAIN and MOIRE tiers use few facets and hard stepped edges; DEGRADED mid-count; SHARP full count with clean edges; LOCKED adds hard edges. The counts are not set here: measure two real renderings before any number goes into DESIGN.md. Basis: the render scale (existing); the facet mapping is proposed and unmeasured.

**Stacks.** A stacked structure draws lowest tier widest, lit from above on each tier's top face, with width encoding a count (as the Ziggurat does). Colour tone on a tier is the tier's job, not decoration. Basis: the Ziggurat page (existing); proposed as a pattern.

## Lint and gate plan (cheapest check first, per gotcha 15)

1. `camera`: static check that any `rotateX` or `perspective` on a page matches the camera tokens and has a reduced-motion override. grep-level.
2. `light`: static check that a `box-shadow` glow stays at or under the blur limit and is not a saturated fill. Extend `motion_policy_gate.py` or the page gate.
3. `depth`: headless, only after two measured renderings exist.
4. Routine pass: run Impeccable `audit`, `distill`, `polish` over DESIGN.md and the kit once, record rulings in `_PROPOSALS/`, and schedule it.

## Open decisions (Zach)

1. Approve the Camera and Light paragraphs for DESIGN.md as written, or edit them.
2. Which two renderings should set the geometry numbers.
3. Re-sync the Ziggurat dashboard `look` to cool slate (its data, your artifact), or leave it.

## Ruled 2026-11-13 (Zach: approve, edit DESIGN.md)

Camera and Light went into `DESIGN.md` under "Camera and light". Two changes from the draft, both because `DESIGN.md` already said something the draft contradicted:
- **Light:** the draft leaned on the emboss bevel (a bottom shade). `DESIGN.md` already holds the Glow-Not-Shadow Rule (depth is light, never cast darkness), so the key light is now a lighter tone plus a top-edge highlight, with shade only inside a recessed well. The "blur at or under 16px" limit was dropped: the Shadow Vocabulary in `DESIGN.md` itself uses 34px and 54px blooms.
- **Camera:** added the one sanctioned second use, a `vh`-perspective floor plane (the status page presentation stage at 64 degrees), so the rule matches what ships.
First gate: `page_gate.py` check `camera` (warning), fixtures in `scripts/tests/test_page_gate_camera.py`. No light gate: nothing mechanical to check beyond the existing vocabulary. Geometry depth and Stacks stay proposals.
