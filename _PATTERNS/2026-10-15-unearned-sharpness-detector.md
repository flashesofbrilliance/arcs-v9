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

## Round 2: pre-registered beliefs (written before any round-2 code or run)

Ground: tests live in `scripts/sharpness_cutoff.py` `--self-test` (arcs-v9 PR 1315, branch claude/affectionate-williams-5808c3); this section was committed in the same PR as its code, written first in the working tree and unrun-against until the results below. Round 1 ground: PR 1313 at 97b31f7c.

B3. Test (b) round trip: box-downscaling a faithful 2x upscale returns the source; a 2x "upscale" built from different content does not.
Prior 0.9. Test: `--self-test` planted faithful vs planted wrong-content. Kill: error ratio under 3x between them.

B4. Round trip ALONE cannot catch invented detail that averages to zero inside each source block (it passes the round trip). A residual
check, claimed minus bilinear-up(source), does catch it. Prior 0.8 that both halves hold. Kill: round trip fails the injected case
(then B4's first half is wrong and round trip is stronger than I think) OR residual misses it.

B5. Noise-floor statistic (tail energy relative to mid-band energy) rescues the smooth native image that fooled test (a) in round 1,
provided the native image carries a white noise floor. Prior 0.6. Kill: smooth+noise native tail ratio below the upscale's, or the
upscale's above 0.3. Expected limit, stated now: a smooth native with NO noise floor (pure analytic) is indistinguishable from an upscale.

B6. JPEG-like 8x8 DCT quantization of a native image false-positives under test (a) like the smooth case. Prior 0.7. Test: stdlib DCT
quantizer as a stand-in (no JPEG decoder in stdlib). Kill: cutoff ratio stays above 0.85 after quantization (then (a) is robust to it).

B7. Test (c) as a TOY mechanism: held-out/training error ratio separates an overfit 1D "splat" fit (bump width below sample spacing)
from a well-fit one. Prior 0.9, and it proves nothing about real Gaussian splats, only that the gap statistic works on a planted overfit.
Kill: ratio gap under 3x.

Real photos: observation only, no claim. If the repo holds none, say so.

### Round 2 results, 2026-10-15 (`python3 scripts/sharpness_cutoff.py --self-test`, exit 0; B2 and B6 are reported findings, not gates)

- B3 PASS. Round-trip mse vs source: faithful 1392.5, wrong content 7906.9 (5.7x). The absolute faithful figure is large only because the planted
  source is white noise; the ratio is the evidence.
- B4 PASS, both halves. Injected zero-mean detail: round-trip mse 1416.4 (indistinguishable from faithful 1392.5), residual vs up(source) 393.2
  (faithful 0.0). So round trip alone is blind to invented detail that averages out per block; the residual catches it. Limit: the residual
  assumes the claimed image used the SAME interpolation as `_bilinear2x`; a real pipeline with a different kernel gets a nonzero floor. Untested.
- B5 PASS. tail_ratio: native 1.041, 2x upscale 0.008, smooth+noise native 1.159. The noise floor separates what the cutoff statistic could not.
- Predicted limit NOT reproduced (my prediction was wrong): a smooth analytic image with no deliberate noise scored tail 0.339, above the upscale,
  because 8-bit rounding is itself a noise floor. The no-noise-floor blind spot likely exists only for float or heavily smoothed sources. Unchecked.
- B6 FAIL (prior 0.7). JPEG-like quantization at q=40 left the cutoff at 1.000. A post-hoc probe at q=400 (not B6, added after seeing the failure)
  also stayed at 1.000, because quantization noise on a white-noise texture is itself broadband. The probe image was wrong for the question: real JPEG
  false positives come from natural 1/f content losing its weak high band. Status: UNRESOLVED, needs a natural-content image and a real JPEG.
- B7 PASS, as a toy only. Held-out/train mse: overfit 30480741 vs well-fit 0.95. The overfit figure is degenerate (isolated bumps drive train error
  to the 1e-9 floor), so the 3x kill line was never at risk. This shows the gap statistic works on a planted overfit; it says nothing about real Gaussian splats.

Real-image observation (no claim): public/good-fears-og.png cutoff 1.000 tail 0.000; honest-og.png 0.938 / 0.147; icon-192.png 0.729 / 0.144;
_ARCHIVE/fanatics-pages/arcs_recoil_cj_masopust.png 0.953 / 0.425 (central 256-px crops). All four are rendered graphics, not photographs. Crisp
rendered text and UI are sharp by construction, the same class as auto-traced vectors; this detector cannot judge them and the numbers above are not a verdict.

Still open: natural photos, real JPEG decode (no stdlib decoder), non-bilinear source kernels, a true splat renderer (test c beyond the toy),
auto-trace vectors, too-clean inliers.
