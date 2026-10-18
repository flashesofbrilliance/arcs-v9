---
paths:
  - "src/**"
  - "public/**"
  - "_ARTIFACTS/**"
---

<!-- Moved verbatim from WORLD.md on 2026-10-17 (WS1 slice 3). Loads when Claude reads, writes or edits a matching file. -->

# WORLD.md render sections: the render scale (full), progression, brand identity

## THE RENDER SCALE

The brief and all UI sections render at **earned fidelity** — never at higher resolution than the data deserves.

| Y State | Fog density | renderResolution | Visual treatment |
|---------|-------------|-----------------|-----------------|
| SCRATCH / EPHEMERAL | Pea soup | GRAIN | weight: 300, tracking: +0.02em, grain overlay |
| PARADOX | Dense fog | MOIRE | weight: 300, tracking: +0.03em + CSS ::after |
| YELLOW / CONTESTED | Clearing | DEGRADED | weight: 400, tracking: +0.01em |
| GREEN / HIGH | Clear | SHARP | weight: 500, tracking: normal |
| LOCKED / Nucleus | Crystal | SHARP + hard edges | weight: 600, tracking: -0.01em |

Text always renders at full opacity (Zach, 2026-10-11). Fog is shown through weight, tracking and the grain overlay, never by dimming the words: a fog you cannot read fails the contrast floor, and the brief must stay legible at every depth.

**Earned fidelity has a floor: coherent wrapping.** Fidelity is the *resolution* of the render, never a licence for a ragged one. BODY reading text on a surface shares ONE measure (a single px `--measure`, never per-element `ch` caps); bordered callouts carry that measure on the box so every right edge lines up. But a LEDE is not body text: a hero or section lede spans the full lane, edge-to-edge with its heading — a lede pinched to the narrow body measure leaves a dead right gutter that reads as broken and abridged, the fog leaking back in from the other side. Both failures are the same sin (a text block whose width lies about its role), and the narrow one is invisible to overflow gates — so eyeball the lede against its heading, not just the sweep. Verify across the full width band (360–1440, especially 700–1000) with the surface's own gate before calling anything SHARP. Canon: `_PATTERNS/arcs-artifact-css-base.css`; enforcement in AGENTS.md gotcha #13; preference in memory `design-full-width-lede-matches-heading`.

---

## THE PROGRESSION

Receipts earned → fog retreats → terrain readable → nucleus approaches.

Early: heavy fog, coarse briefs, Y gates firing yellow often.
Mid: patterns surface in Observatory, compass gets faster, NCI climbing.
Late: navigating from clarity ridge. Receipt history becomes a personal atlas.
Superionic: structure of clarity + fluidity of instinct. Decisions move through you like charge through crystal — fast, directional, lossless.

---

## BRAND IDENTITY

**Name:** ARCS  
**Tagline:** *Navigate to clarity. Survive the pressure. Find the flow.*  
**Visual world:** 2.5D isometric decision observatory — mission control + geological survey + instant replay theater

**Tagline system:**
- Primary: *Navigate to clarity.*
- Secondary: *Render through the fog.*
- Mechanic: *Survive the pressure. Find the flow.*
- Observatory: *Every decision, recorded. Every path, replayable.*
- Nucleus: *Superionic: where structure meets flow.*

---

