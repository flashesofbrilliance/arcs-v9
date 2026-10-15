# Unearned sharpness: a detector idea for visual signal layers

Date: 2026-10-15. Origin: Zach's proposal, same day. Status: note plus one tiny script (`scripts/sharpness_cutoff.py`).

Prior art: no direct hit. Used: WORLD.md "THE RENDER SCALE" (fidelity is earned, never above the data), memory
`earned-fidelity-not-maximal-diamond-cut`, `scripts/page_gate.py` (the existing "does it render honestly" gate, layout only, no pixel-information check).
The planted-fault `--self-test` pattern named in the brief lives in scripts not yet on origin/main as of this note, so the
planted-fault shape here (plant known-bad and known-good, require separation) is rebuilt from the brief's description, not copied.

## Principle

Rendered sharpness must not exceed information content. A detector for this flags UNSUPPORTED sharpness: pixels crisper than anything
upstream could have supplied. It does NOT separate fiction from non-fiction: a native photo of a staged scene passes, an honest
low-resolution upscale of a true image can still flag only if it claims more resolution than it has. The finding is "claimed resolution
exceeds supported resolution", never "fake".

Targets: generative or gradient-descent upscaling slop, auto-traced vectors (crisp edges, no added information), Gaussian splats
overfit to training views, too-clean inliers.

## Three candidate tests

| Test | What it checks | Label |
|---|---|---|
| (a) Spectral cutoff vs claimed resolution | Energy above a cutoff frequency in an image that claims N pixels. A true N-pixel capture has broadband energy up to near Nyquist; a k-times upscale has almost none above Nyquist/k. | MECHANISM (Fourier sampling theorem; checkable stdlib-only) |
| (b) Downscale-then-compare vs the source | Downscale the claimed image to the source size and compare. Faithful upscale returns the source; invented detail does not round-trip. Needs the source. | MECHANISM (needs source access; not built) |
| (c) Held-out-view consistency for splat-like scenes | Render a held-out camera view and compare to a real capture. Overfit splats are sharp on training views and fail held-out ones. | MECHANISM in principle, METAPHOR here (no splat scene or renderer in this repo) |

"Too-clean inliers" as a statistical analog of the same idea (variance below the measurement floor) is a METAPHOR until a measurement floor is defined.

## Pre-registered beliefs (written before any test run)

B1. Claim: a spectral-cutoff statistic separates a planted 2x bilinear upscale from a planted native texture of the same output size.
Prior: 0.85. Test: `--self-test` in `scripts/sharpness_cutoff.py` (planted upscale, planted native). Kill: the upscale's cutoff ratio is
not below 0.7 and the native's not above 0.85, OR the two overlap, in which case the detector is not trusted and the script is removed.

B2. Claim: the same statistic does NOT flag a smooth but honestly native image (low-contrast gradient with mild noise) as an upscale
when its claimed resolution equals its real resolution, i.e. the detector keys on sampling mismatch and not on blur alone.
Prior: 0.45 (a blurry native image looks band-limited, so a false positive is likely). Test: third planted case in `--self-test`
(smooth native). Kill: if the smooth native scores under the upscale threshold, record it as a KNOWN FALSE POSITIVE in this note and
the script's docstring; the detector then only supports "band-limited, source unknown", not "upscaled".

## Result (filled after the run)

See the end of this file.

### Run, 2026-10-15 (`python3 scripts/sharpness_cutoff.py --self-test`, merged in arcs-v9 PR 1313 at 97b31f7c, receipt 2026-10-15--unearned-sharpness-detector-pr1313--ZH)

Ground: output reproduced from `scripts/sharpness_cutoff.py` on the PR 1313 head; Vercel status on 97b31f7c = success; receipt row read back from public.decision_receipt.

cutoff_ratio (99% of AC energy, fraction of Nyquist): native 1.000, planted 2x upscale 0.688, smooth native 0.406.

- B1 survived, narrowly: separation is wide (1.000 vs 0.688) but the upscale sits 0.012 under the 0.7 line I pre-registered. One
  texture, one seed, one interpolation (box-style 2x). Do not trust the 0.7 threshold on other content; the gap, not the line, is the evidence.
- B2 FAILED as predicted (prior 0.45): a smooth honest native image scores 0.406, below the upscale. Recorded KNOWN FALSE POSITIVE.
  Consequence: this statistic supports "band-limited, source unknown", never "upscaled" or "fake". It needs a native-capture noise
  floor or the source (test b) to turn band-limited into unsupported.
- Not tested: test (b), test (c), vector-trace and too-clean-inlier cases, real photos, JPEG-compressed inputs (JPEG zeroes high
  frequencies and will also flag). Those stay open.
