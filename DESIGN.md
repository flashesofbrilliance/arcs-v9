---
name: ARCS
description: Render through the fog to earned clarity — a dark-cockpit decision instrument.
colors:
  obsidian-bg: "#020408"
  panel: "#0d1117"
  elevated: "#111827"
  border-subtle: "#1e293b"
  text-primary: "#e2e8f0"
  text-secondary: "#94a3b8"
  text-muted: "#475569"
  text-dimmed: "#64748b"
  true-north-cyan: "#00F0FF"
  coherent-green: "#00FF9D"
  locked-gold: "#FFD700"
  warning-orange: "#ff9d3c"
  ruin-red: "#FF4D6D"
  conviction-violet: "#A78BFA"
  paradox-magenta: "#E879F9"
typography:
  display:
    fontFamily: "'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif"
    fontSize: "clamp(1.5rem, 4vw, 2.4rem)"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  body:
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    fontSize: "0.925rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0em"
  label:
    fontFamily: "'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace"
    fontSize: "0.625rem"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "0.14em"
rounded:
  xs: "3px"
  sm: "6px"
  md: "10px"
  lg: "16px"
  pill: "999px"
spacing:
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "6": "24px"
  "8": "32px"
  "12": "48px"
components:
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "20px 22px"
  button-ghost:
    backgroundColor: "{colors.obsidian-bg}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.xs}"
    padding: "8px 12px"
  chip:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.xs}"
    padding: "3px 8px"
  input:
    backgroundColor: "{colors.elevated}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "10px 14px"
---

# Design System: ARCS

## Overview

**Creative North Star: "Render Through the Fog"**

ARCS renders at *earned fidelity*. Every surface is only as sharp as the evidence deserves, and it never lies about how certain it is. Clarity is not granted at load; it is earned as the fog lowers and the terrain resolves. This is the organizing law of the entire visual system: a coarse, honest reading always beats a confident fabrication. The screen obeys the same physics the product asks of its user, so the interface is not a container for the idea, it is the idea, drawn.

The world is obsidian and single-theme by design, a dark cockpit read under pressure. It is calm, precise, and serious play: instruments in skilled hands, not a SaaS dashboard. Color is never ornament; each hue is a *state*, and its rarity is what makes it legible. Depth is made of light, not cast shadow, because the goal is light through fixed form. The register is Myst, not onboarding: the world trusts the reader and expects them to rise to it.

The signature is the mark itself. **The ARCS mark is a Möbius strip emerging from a fog field onto a clean gold horizon line.** The Möbius is the house glyph, the tilde extruded: take the `~` (an approximate, a placeholder, a reserved vessel) and sweep it through the decision manifold with a half-twist, and you get an arrow-less, non-orientable surface made of arcs. The fog buries the horizon; lowering it earns the bearing. The mark animates the tagline, and everything else in the system is a still frame of that motion.

**Key Characteristics:**
- Earned fidelity: four render states (SHARP / DEGRADED / GRAIN / MOIRE) that degrade legibility to match evidence.
- Obsidian, single-theme, dark-cockpit; no light mode.
- Semantic color: every accent is a state, used on ≤10% of a screen.
- Glow, not shadow: depth is luminance, not cast darkness.
- Mono for instruments, serif for canon, sans for the body.
- The tilde (`~`) is the atomic glyph and the honesty marker.

## Colors

An obsidian ground carrying a small set of high-chroma signal colors, each of which *means* something. The palette is mostly neutral; the signal hues are rare on purpose.

### Primary
- **True North Cyan** (#00F0FF): the active bearing, the compass direction, selected/active state, the SHARP-state strip. The color of "this way is uphill."

### Secondary
- **Coherent Green** (#00FF9D): coherence and the GREEN Y-gate; a clarity-ridge, high-conviction reading. Rendered SHARP.
- **Locked Gold** (#FFD700): Court / LOCKED / one-way-door / the earned horizon line in the mark. Gravity, commitment, the bearing you can trust.
- **Ruin Red** (#FF4D6D): alert, the RED free-solo/ruin-exposure topology, the GRAIN state. Never used decoratively; it inverts meaning if misapplied.

### Tertiary
- **Warning Orange** (#ff9d3c): warnings and macro-tags, one step below ruin.
- **Conviction Violet** (#A78BFA): the DELTA state, a shift in conviction.
- **Paradox Magenta** (#E879F9): PARADOX / the Curator; the MOIRE render state's tint.

### Neutral
- **Obsidian** (#020408): the page ground. The world's floor.
- **Panel** (#0d1117): cards, modules, instruments.
- **Elevated** (#111827): inputs and hover states.
- **Border Subtle** (#1e293b): dividers, card strokes.
- **Text Primary** (#e2e8f0): primary reading.
- **Text Secondary** (#94a3b8): supporting copy.
- **Text Dimmed** (#64748b) / **Text Muted** (#475569): metadata and mono labels.

**The Semantic Color Rule.** Color is state, never decoration. Cyan is bearing, green is coherence, gold is locked, red is ruin, violet is conviction-shift, magenta is paradox. If a color would not survive being read as its state, it does not belong on the screen.

**The One Voice Rule.** Any single signal color occupies ≤10% of a screen. Rarity is the legibility. A screen lit up in cyan says nothing; one cyan bearing says everything.

## Typography

**Display Font:** Iowan Old Style / Palatino (serif) — the canon and oral-history register (proverbs, the Tao, load-bearing quotes).
**Body Font:** Inter (with system-ui fallback) — all prose and reading.
**Label/Mono Font:** JetBrains Mono (with IBM Plex Mono) — instrument labels, section indices, gauges, metadata.

**Character:** Three voices, strictly separated by job. Mono is the instrument legend (cold, tracked, uppercase). Sans is the calm reading voice. Serif is reserved for wisdom in transmissible form — the things meant to be carried in the mouth to the next person.

### Hierarchy
- **Display** (serif, 500, clamp(1.5rem, 4vw, 2.4rem), 1.2): proverbs, canon headers, load-bearing quotes.
- **Headline** (Inter 600, 1.15rem, 1.25): section titles.
- **Title** (Inter 600, 0.95rem): card and panel titles.
- **Body** (Inter 400, 0.925rem, 1.6, max ~70ch): all prose.
- **Label** (JetBrains Mono 700, 0.625rem, +0.14em, UPPERCASE): instrument labels, section indices, gauge units.

### Named Rules
**The Graded-Legend Rule.** Mono labels use six graded tiers (t1–t6): as a tier rises, size increases and tracking decreases while weight holds, so a section heading never reads like a field label. Color stays caller-controlled because it is semantic.

**The Three-Voice Rule.** Mono = instrument, Sans = reading, Serif = canon. Never cross them: a proverb never renders in mono, a gauge label never in serif.

## Layout

Centered single-column documents on the obsidian ground: `max-width: 960px` for documents (760px for reading-dense surfaces like the Tao, 640px for forms). Container padding steps from 1rem (mobile) to 1.5–2rem. The spacing rhythm is a 4px base (steps 1–12). Instruments cluster in a sticky "control deck" at the top (blurred obsidian, `backdrop-filter: blur(10px)`, a single hairline border-bottom). Wide content (tables, timelines, manifolds) scrolls inside its own `overflow-x: auto` container; the page body never scrolls sideways. Density is instrument-tight, not airy: this is a cockpit, read at a glance.

## Elevation & Depth

Depth is **luminance, not cast shadow.** Surfaces are flat panels on the obsidian ground; separation comes from a one-step tonal lift (bg → panel → elevated) and a hairline border, not from drop shadows. The one exception is the **glow**: an active or locked instrument emits a restrained bloom of its own signal color.

### Shadow Vocabulary
- **Signal glow** (`box-shadow: 0 0 34px rgba(0,240,255,.07)` and kin): a present-but-restrained bloom under an active bearing or a locked panel. Alphas ~.07–.28, deliberately dialed down from hotter earlier values.
- **Locked bloom** (`box-shadow: 0 0 54px rgba(0,240,255,.16); border-color: rgba(0,240,255,.6)`): the crystalline "superionic" state — light through fixed form.

**The Glow-Not-Shadow Rule.** Depth is made of light, never of cast darkness. A surface at rest is flat. Elevation is a signal-colored glow that appears as a *response to state* (active, locked, focus), not an ambient default. Cast drop-shadows are banned.

## Shapes

Soft-tech corners: `xs 3px` (chips, ghost buttons), `sm 6px` (cards, inputs, most instruments), `md 10px` (feature panels), `lg 16px` (rare hero containers), `pill 999px` (toggles). Borders are single hairlines (`1px solid #1e293b`); the active/locked states shift the border color to a signal tint rather than thickening it. The recurring silhouette is the **arc** — the compass sweep, the gauge arc, the Möbius strand, the fog gradient band. Straight rules exist only as the horizon line and section dividers (a cyan-to-transparent gradient hairline). The house is made of arcs and one honest horizon.

## Components

### The Mark (signature)
- **Form:** a Möbius strip (arrow-less, non-orientable, drawn as interfering strand families) rising from a layered fog field onto a single gold horizon line at ~62% height.
- **Construction:** the tilde extruded — the `~` swept through the manifold with a half-twist. Two strand families (cyan `rgba(0,240,255,.30)` + gold `rgba(255,215,0,.16)`) offset by a moiré Δ; the interference pattern belongs to neither, which *is* the PARADOX/MOIRE state.
- **Behavior:** the fog is a variable. Lowering it earns the horizon (the bearing) — clarity is never granted at rest. Drift (slow rotation) is the default idle; reduced-motion holds a still frame.
- **Wordmark:** `ARCS` in JetBrains Mono 700, +0.16–0.42em tracking, with the `A` or the leading glyph in True North Cyan. Never set the wordmark in serif or sans.

### Buttons
- **Shape:** `xs 3px` radius, ghost by default.
- **Ghost (primary usage):** transparent on obsidian, `1px solid #1e293b`, mono 700 uppercase label in text-secondary. Hover/focus shifts border and text to True North Cyan (`border-color: #00F0FF; color: #00F0FF`).
- **Active/On:** border + text in the relevant signal color with a faint tinted fill (`background: rgba(0,240,255,.08)`).
- **Focus:** `outline: 1px solid #00F0FF; outline-offset: -1px` — always visible, never removed.

### Chips
- **Style:** panel background, hairline border, mono micro-label (t1/t2). Status chips tint border + text to the signal color (`c-ok` green, `c-part` gold, `c-stale` red) with a ~7% tinted fill.

### Cards / Panels
- **Corner:** `sm 6px` (`md 10px` for feature panels).
- **Background:** panel (#0d1117) on obsidian; elevated (#111827) for nested inputs.
- **Border:** hairline #1e293b; active/locked shifts to a signal tint. Depth via glow (see Elevation), never drop-shadow.
- **Title:** mono 700 uppercase in a signal color; body in Inter.

### Inputs / Fields
- **Style:** elevated background, `sm 6px`, hairline border.
- **Focus:** border shifts to True North Cyan with a faint cyan glow; `accent-color` on ranges is cyan (gold for interference/offset controls).

### Gauges / Instruments (signature)
- **Form:** a numeric readout in mono tabular-nums with a mono unit label above; value colored by state (green≥70, gold≥45, red<45 for NCI-style). Arc gauges sweep the signal color.
- **Honesty:** assessed values render with a leading `~` and are dimmed one step. Measured values never carry the tilde.

### The Render-Scale (the system's defining behavior)
Every surface can render at four earned-fidelity states, mapped from the Y-gate:
- **SHARP** (GREEN/LOCKED): `opacity 1.0, weight 500, tracking 0`. Full contrast, fine grain.
- **DEGRADED** (YELLOW/FORK): `opacity 0.85, weight 400, tracking +0.01em`.
- **GRAIN** (SCRATCH/DELTA/DRIFT/RED): `opacity 0.70, weight 300, tracking +0.02em` + sparse speckle.
- **MOIRE** (PARADOX): `opacity 0.60, weight 300, tracking +0.03em` + interference overlay.

## Do's and Don'ts

### Do:
- **Do** render at earned fidelity: match the surface's sharpness to the evidence (SHARP only when GREEN/LOCKED).
- **Do** keep assessed values marked with a leading `~` and dimmed one step (the honesty invariant).
- **Do** use color as state only, on ≤10% of a screen (Semantic Color + One Voice Rules).
- **Do** convey depth with signal-colored glow as a response to state; keep surfaces flat at rest.
- **Do** separate the three voices strictly: mono for instruments, sans for reading, serif for canon.
- **Do** keep the world obsidian and single-theme.
- **Do** give every interactive element a visible cyan focus ring (WCAG 2.1 AA target).

### Don't:
- **Don't** render SHARP on thin evidence; a coarse honest reading beats a confident fabrication.
- **Don't** use a signal color decoratively, or let one flood the screen.
- **Don't** use cast drop-shadows for elevation.
- **Don't** set the wordmark or a proverb in the wrong voice (no serif wordmark, no mono proverb).
- **Don't** use em-dashes anywhere (plain-language rule wins even over canon voice; prefer commas, colons, periods, or the interpunct · ).
- **Don't** introduce a light theme.
- **Don't** let a per-engagement canon family's locked house grammar (e.g. the Louisville omakase world) leak into product surfaces.
