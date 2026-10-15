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
