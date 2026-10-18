# Tag exemplar: one idea, cut to it (2026-10-17)

Status: pre-registered BEFORE the build. Kills below were written first; results are appended at the bottom.
Goal (Zach): take one style to "s-tier diamond cut, superionic, wuwei". In this repo, diamond cut means earned fidelity,
not maximal (memory `earned-fidelity-not-maximal-diamond-cut`): cut until every element is load-bearing. Superionic is
structure and flow fused (WORLD.md). Wuwei is effortless: one dial makes the whole look.

## The one idea
The proverb travels the Möbius strip. The sentence runs along the ring, and where the strip twists the letters flip
to their mirrored back face. Wear is the only other thing the print says: grit, drips, overspray and spatter all
come from (1 minus fidelity), so a sharp proverb prints crisp and a worn one prints dirty.

## What the cut removes from the old Tag preset
The label slab / throw-up label (the words now live on the strip, not on top of it), the Möbius strip row, flat ink
grounds, splatter, halftone, wall grit as a free slider, the horizon line. Kept: the ring, four-ink facets, the marker
outline, the tag mark (it is the artist's signature, so it carries identity), and one fidelity dial.

## Wuwei rule
With "Fidelity drives the grit" on, rough edges, spray, drips, spatter, edge drip and wall grit are computed from
fidelity. The grit sliders lock. At fidelity 1 every grit value is zero.

## Pre-registered kills
| id | claim | kill if |
|---|---|---|
| T1 | Words ride the strip | at fidelity 1, fewer glyphs render than non-space characters in the panel's run, or the run is not in reading order along the ring |
| T2 | The twist is visible | in fewer than 3 of 4 panels does the run contain both an upright glyph and a mirrored glyph |
| T3 | One dial | any derived grit value rises as fidelity rises, or any is non-zero at fidelity 1 |
| T4 | Legible | smallest glyph under 11 px at the 900 px export width, at fidelity 1 |
| T5 | Cut earns its place | in an ablation view (no tag mark / no spatter / no outline) Zach cannot tell the ablation from the full Tag: that element is cut |
| T6 | Encoding is perceivable | blind ranking of 6 Tag prints by clarity: Zach mis-ranks 2 or more adjacent pairs. Machine proxy first, human decides |
| T7 | Light enough | a 2x2 Tag render takes over 2.5 s in headless Chromium (phone proxy) |

## Results
(appended after the build)
