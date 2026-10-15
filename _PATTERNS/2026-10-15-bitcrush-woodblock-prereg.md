# Bitcrush with a woodblock mode: pre-registration

Date: 2026-10-15. Written BEFORE the feature was built or run. Origin: Zach's idea of crushing 8K down to 8-bit while keeping the layered, atmospheric quality of a ukiyo-e woodblock print. Subject: the Raw Capture instrument (`_ARTIFACTS/raw-capture.html`), whose synthetic terrain has five ridge layers receding into haze plus a sky, which stands in for atmospheric depth.

## Claim to test

Flat quantization destroys depth cues because neighboring layers fall onto the same few tones. An ordered dither preserves each region's average tone, so the layers stay separable even at very low bit depth. A woodblock print builds tone from a few flat plates and wet gradients; the dither is the mechanical stand-in, not a claim about printmaking technique.

## Measure (fixed now)

- Regions: sky plus the five ridge layers, six regions, five adjacent boundaries.
- A boundary is separable if the mean tone of the two regions differs by at least 10 of 255 levels.
- Count only boundaries that are separable BEFORE crushing. "Kept" is how many of those are still separable after crushing, for plain steps and for the dithered woodblock mode, at the same bit depth.
- The detail readouts describe the development before crushing. Dither adds high-frequency noise that would otherwise read as unearned sharpness.

## Predictions and kills

P1. At 2 bits, plain steps keep 3 or fewer of the boundaries and woodblock keeps strictly more. Prior 0.7. Kill: woodblock does not beat plain by at least 1 boundary at 2 bits, so the preservation claim fails and the feature is reported as a failed idea.
P2. At 1 bit, woodblock keeps at least 4 boundaries. Prior 0.5. Kill: fewer than 4.
P3. At 8 bits the feature is off and the page equals the static page (the rest invariant in ADR-087 still holds). Kill: any readout differs from baseline.

## Not claimed

That the result looks like a woodblock print. Only the depth-separation measure is tested here. A visual judgment needs a human eye.

## Results (2026-10-15, run after the pre-registration commit)

Run with Playwright against `_ARTIFACTS/raw-capture.html`: three captures, exposures +1 and +3, bit depths 1 to 4 and 8. Separable layer boundaries kept, plain steps against woodblock dither:

| Capture and exposure | Boundaries separable before crushing | 1 bit plain / wood | 2 bit plain / wood |
|---|---|---|---|
| Wide range, +1 EV (default) | 5 | 3 / 5 | 3 / 5 |
| Wide range, +3 EV | 3 | 1 / 3 | 3 / 3 |
| Clipped, +1 EV | 3 | 1 / 3 | 3 / 3 |
| Clipped, +3 EV | 1 | 0 / 1 | 1 / 1 |
| Dim, +1 EV | 1 | 0 / 1 | 0 / 1 |
| Dim, +3 EV | 2 | 1 / 2 | 1 / 2 |

- **P1 (2 bits, woodblock strictly beats plain): holds on the default case** (3 of 5 against 5 of 5). Across all six cases woodblock is never worse and strictly better in 3 of 6, tied in the other 3.
- **P2 (1 bit, woodblock keeps at least 4): holds on the default case** (5 of 5). The other cases have fewer than 4 separable boundaries to keep; woodblock kept all of them in all six cases, plain did not.
- **P3 (8 bits is off, rest invariant intact): holds.** `scripts/raw_capture_anim_check.mjs` passes with the feature present.
- **Image sanity:** the canvas holds at most 2^bits distinct tones (plain 2, 4, 7 at 1, 2, 3 bits; woodblock 2, 4, 8).
- **Visual read:** at 2 and 1 bit the plain version collapses the ridges into a flat slab; the woodblock version keeps the receding layers, haze and the sun's glow.

Caveats. The win is close to a mathematical property of ordered dithering, which preserves an area's average tone, so it confirms a mechanism and is not a discovery about printmaking. The result reads as a retro halftone with atmospheric depth, not yet as ukiyo-e, which uses flat color plates, wiped gradients and a keyline. The metric is on one synthetic terrain with a known layer map; a real photograph has no such map. A real 8K input was not tested.
