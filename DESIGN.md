---
name: ARCS Field OS
description: A dark-cockpit decision instrument — render through the fog to earned clarity.
colors:
  bg: "#020408"
  surface: "#0d1117"
  elevated: "#111827"
  obsidian: "#0A0C0D"
  border: "#1e293b"
  border-active: "rgba(122,210,255,0.38)"
  border-locked: "rgba(255,210,120,0.28)"
  fg1: "#e2e8f0"
  fg2: "#94a3b8"
  fg3: "#8593a6"
  fg4: "#707e92"
  cyan: "#00F0FF"
  green: "#00FF9D"
  gold: "#FFD700"
  orange: "#ff9d3c"
  red: "#FF4D6D"
  steel: "#94a3b8"
  violet: "#A78BFA"
  magenta: "#E879F9"
  bronze: "#BA8F65"
  jade: "#5A9E87"
  terracotta: "#B8664F"
  ivory: "#F8F5F0"
typography:
  hero:
    fontFamily: "Inter, system-ui, -apple-system, sans-serif"
    fontSize: "clamp(2rem, 5vw, 3rem)"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  h1:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1.375rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "normal"
  lead:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 500
    lineHeight: 1.6
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  instrument:
    fontFamily: "JetBrains Mono, IBM Plex Mono, ui-monospace, Menlo, monospace"
    fontSize: "0.75rem"
    fontWeight: 500
    letterSpacing: "0.08em"
  label:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "0.625rem"
    fontWeight: 700
    letterSpacing: "0.14em"
rounded:
  xs: "3px"
  sm: "6px"
  md: "10px"
  lg: "16px"
  pill: "999px"
spacing:
  s1: "4px"
  s2: "8px"
  s3: "12px"
  s4: "16px"
  s6: "24px"
  s8: "32px"
  s12: "48px"
components:
  tile:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.fg1}"
    rounded: "{rounded.md}"
    padding: "12px 14px"
  control:
    backgroundColor: "transparent"
    textColor: "{colors.fg2}"
    rounded: "{rounded.sm}"
    padding: "3px 9px"
    typography: "{typography.instrument}"
  control-active:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.cyan}"
    rounded: "{rounded.sm}"
  pill:
    backgroundColor: "transparent"
    textColor: "{colors.fg2}"
    rounded: "{rounded.pill}"
    padding: "2px 8px"
    typography: "{typography.label}"
---

# ARCS Field OS

The canonical visual world for ARCS product surfaces (app, dashboard, briefs, status,
observatory). Tokens are normative and live in `public/observatory/colors_and_type.css`
(mirrored by `src/ui/tokens.ts`, `observatory.tokens.json`, and WORLD.md's Render Scale) —
this file is their portable spec. Per-engagement canon families (e.g. the Louisville omakase
world) carry their own locked grammar and are documented per surface; they do not inherit this.

## Overview

**Creative North Star: the field instrument.** Not a SaaS dashboard — a calibrated instrument
in skilled hands, read under pressure. The register is *mission control + geological survey +
instant-replay theater*: a 2.5D isometric decision-observatory where a person arrives in fog and
the terrain clarifies as evidence arrives. Tone is **calm, precise, serious play** (Myst, not
onboarding): the interface trusts the operator and recedes; it never celebrates with confetti.

Two laws govern every screen:

- **Earned fidelity.** A surface renders only as sharply as its evidence deserves, and never lies
  about how certain it is. Confidence is a *visual channel*, not a claim — see Render Scale below.
- **Instrument, not dashboard.** Surface the reading first; detail on demand. Cut what does not
  earn its place. Color, glow, and motion each carry exactly one signal — never decoration.

## Colors

Committed **dark, single-theme** (the void `#020408`). This is a deliberate world, not a missing
light mode. Neutrals are cool, biased toward the cyan bearing.

**Surface hierarchy (depth by tone, not just shadow):** `bg #020408` (the void / outer fog) →
`surface #0d1117` (cards, modules) → `elevated #111827` (inputs, hovers, raised wells). `obsidian
#0A0C0D` is the alternate deep ground for wayfinder/marketing layers.

**The signal ramp is load-bearing and triple-mapped** — the same five hues encode three registers,
because they are the same underlying scale of coherence:

| hue | color | NCI grade | Y-gate weather | Observatory altitude |
|---|---|---|---|---|
| green | `#00FF9D` | A (≥85) — SHARP | coherent / AVERTED | L5 Executive |
| cyan | `#00F0FF` | B (70–84) | True North / active bearing | L4 Strategic |
| gold | `#FFD700` | C (55–69) | COURT / LOCKED / MITIGATED | L3 Operational |
| orange | `#ff9d3c` | D (40–54) | — | L2 Tactical |
| red | `#FF4D6D` | F (<40) — GRAIN | alert / OPEN | L1 Surgical |

`steel #94a3b8` = neutral default (SCRATCH/DELTA/DRIFT); `violet #A78BFA` = conviction shift;
`magenta #E879F9` = paradox. Because the ramp is overloaded, **a surface must not encode two of
these registers on the same visual channel at once** (e.g. don't color a mark by altitude *and*
grade — pick one; encode the other by position). `bronze/jade/terracotta/ivory` are a separate
wayfinder accent layer for luxury/marketing surfaces only; they never enter instrument screens.

Contrast targets WCAG 2.1 AA on product surfaces; `fg2/fg3/fg4` are calibrated AA on the void.

## Typography

Two families, strict roles: **Inter** for prose (hero, headings, lead/True-North statement, body)
and **JetBrains Mono** for everything instrument — labels, data, controls, stat readouts, provenance.
The mono face *is* the cockpit voice; reach for it whenever a value, coordinate, or control is shown.

Scale (4px-derived): `10px` micro instrument labels · `12px` labels/captions · `14px` UI body ·
`16px` reading body · `18px` lead · `22px` headings · `32px` stat readouts (NCI) · `48px` hero.
Tracking widens with smallness: hero `-0.02em`, labels `+0.08em`, instrument caps/pills `+0.14em`.
Weights: 400/500/600/700. Give headings `text-wrap: balance`; keep prose near 65ch.

## Layout

Centered instrument column, `min(880px, 100%)` with `16px` gutters, sticky control header over a
scrolling stage. 4px spacing base (`4/8/12/16/24/32/48`). Density is high but never cramped: lay
groups out with flex/grid + `gap`, not per-element margins. Wide content (timelines, tables, code)
scrolls inside its own `overflow-x:auto` lane so the page body never scrolls sideways. Use
`font-variant-numeric: tabular-nums` wherever digits align. Respect `prefers-reduced-motion`.

## Elevation & Depth

Depth reads as **lit glass**, never flat fills. Every raised tile pairs a surface gradient
(`--glass-surface`, a subtle 160° vertical sheen) with an **emboss** (top highlight + bottom
shadow = raised toward light) or **deboss** (pressed well). Four shadow tiers: `raised` → `elevated`
→ `floating`, plus `inset` for wells.

**Glow is the confidence channel** — the single most load-bearing depth cue. A signal glow is a
layered build: bright saturated core bloom + wide ambient halo + an inner rim highlight, over the
emboss so the tile reads dimensional. Blur and brightness **scale with conviction** — a barely-lit
tile is honestly uncertain; a bright bloom is earned. Never brighten a glow past the evidence.

## The Render Scale (earned fidelity)

The world's defining mechanic (WORLD.md): the fidelity of any surface is a function of its Y-gate
state. Higher certainty → sharper type, fuller opacity, tighter tracking, finer grain.

| Y state | fidelity | opacity · weight · tracking | grain |
|---|---|---|---|
| SCRATCH / EPHEMERAL | GRAIN | 0.70 · 300 · +0.02em | max |
| PARADOX | MOIRÉ | 0.60 · 300 · +0.03em + `::after` | dense |
| YELLOW / CONTESTED | DEGRADED | 0.85 · 400 · +0.01em | coarse |
| GREEN / HIGH | SHARP | 1.0 · 500 · normal | fine |
| LOCKED / Nucleus | SHARP+ hard edges | 1.0 · 600 · −0.01em | crystalline |

Never render a surface at higher resolution than its data deserves.

## Shapes

Radii: `3/6/10/16px` + `999px` pill. Instrument controls and dots are small-radius or circular;
tiles/cards are `10–16px`; governance/status chips are pills. Hairline borders (`#1e293b`); active
selection uses `border-active` (cyan), locked/court uses `border-locked` (gold). Risk marks are
rotated squares (diamonds); event marks are circles glyph-stamped by type; peaks wear a gold ring.

## Components

- **Instrument tile** — `surface` + `--glass-surface` gradient + `--emboss`, `radius-md`, `12×14`
  padding. The base module for cards, panels, altitude planes.
- **Control (`Ctl`)** — mono, `radius-sm`, `3×9`; inactive `fg2` on transparent, active `cyan` on
  `surface` with a cyan hairline. Prefer over native buttons in the cockpit.
- **Signal dot / node** — small circle (or diamond for risk); **color = its one signal** (type,
  grade, or altitude — chosen per surface, never doubled), **glow = confidence**, border/pulse =
  status. Star glyph + gold ring = a peak/milestone.
- **Governance pill** — `radius-pill`, mono `label` type (`+0.14em`), for Y-gate states / statuses.
- **Stat readout** — mono `32px` tabular-nums for headline numbers (NCI, counts, $).

## Do's and Don'ts

- **Do** make every hue, glow, and motion carry exactly one signal. **Don't** use color decoratively
  or encode two registers on one channel (the classic bug: color a mark by both altitude and grade).
- **Do** lead with the reading and collapse legends/help by default (data-first). **Don't** fill the
  first viewport with instructions.
- **Do** render at earned fidelity — dim the uncertain honestly. **Don't** brighten a glow or sharpen
  type past what the evidence supports.
- **Do** use mono for all data/controls, Inter for prose. **Don't** mix them arbitrarily.
- **Do** derive live surfaces from a fresh SSOT and show an explicit "as of" recency stamp. **Don't**
  hardcode counts, spans, or dates that silently go stale.
- **Do** keep it calm and precise. **Don't** add confetti, marketing gloss, or SaaS-onboarding warmth
  to an instrument surface.
- **Never** use em-dashes in user-facing copy (project-wide rule); prefer commas, colons, or the
  interpunct.
