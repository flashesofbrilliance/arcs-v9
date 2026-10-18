# Algo Andy mark in the Tao print studio (2026-10-18)

Status: built and checked the same day (a small, reversible control, so the kills below were written with the build, not before it; they are recorded as such).

## What it is
The brand mark Zach described for the "AI tag artist": a capital alpha, a DNA double helix, and a capital omega, as one graffiti-tag lockup. The helix stands where the infinity sign would
be, turned to an angle and made taller than the letters. It is DNA, not RNA: two strands joined by rungs. Each strand is cut from small quadrilaterals split into two triangles
with different shades, so the facet edges show. Where a strand passes in front it is wide and solid; behind, it is narrower and softer.

In the studio: Tag mark, Mark control. "Handle (loop and name)" is the earlier mark and stays the default; "Algo Andy lockup" draws the new one. The Tag preset now uses the lockup. The letters and
underline go through the same grit filter as the rest of the tag; the helix is drawn crisp so its facets stay readable.

## Checks (run on the build, not pre-registered)
| id | claim | result |
|---|---|---|
| M1 | Same input, same markup | PASS: the same time gives byte-identical SVG, and toggling to the old mark and back restores it |
| M2 | The two marks are different options | PASS: the markup differs between them, and only the lockup carries the helix transform |
| M3 | It reads at panel size | seen by eye in a 1000 px render: the helix, alpha and omega are legible and separate from the ring behind them; the first version (thin, three turns, grit on) was not, and was changed |
| M4 | Earlier suites unaffected | lyrics L1 to L8 pass when run alone after the change. In one run under heavy machine load L2 (state after a reload) failed, then passed alone; treated as load, not proven. drive and slice2 were not re-run after the change (stopped to run lyrics alone) |

## Not claimed
That the lockup is final: the proportions, the helix angle (24 degrees) and the strand weight were set by eye in one render. Legibility on every palette (a strand can sit on a ring of its own
colour; a thin dark edge helps, it does not solve it). A printed or vector-export version. That it is a trademark or has been cleared for any use.
