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

## Round 3: pre-registered beliefs (written before any round-3 run)

Scope: close B6 with natural content and a real JPEG codec, and fix the sourcing policy for real-image validation. No repo dependency added:
the codec is macOS `sips` (system tool, encode and decode), the statistic is the existing stdlib `cutoff_ratio`/`tail_ratio`. Natural content for this
probe is LOCAL ONLY: Apple's bundled photos under `/Library/Desktop Pictures/` (read in place, never copied into the repo, never redistributed;
license: Apple software license, personal use). They are already JPEG once, so "native" here means "one generation of loss", stated up front.
No file is downloaded in round 3.

B6b. Re-asking B6 on the right content: re-encoding a natural photo crop (256x256 center crop, luma) through real JPEG at low quality (sips
quality 10) drops the cutoff ratio at least 0.15 below the same crop at quality 100, and tail_ratio at least halves. Prior 0.65.
Kill: cutoff at q10 within 0.15 of q100 AND tail ratio above half of q100's. Then (a) and (tail) are robust to JPEG on natural content.
Corollary (not a separate bet): if B6b holds, the detector cannot tell JPEG loss from upscaling and "band-limited, source unknown" stays the only finding.

B6c. Monotone: ratio is non-increasing as sips quality goes 100, 60, 30, 10 (ties allowed within 0.02). Prior 0.8. Kill: a rise above 0.02 anywhere.

B8. A natural photo at native size scores cutoff above the planted 2x upscale threshold (0.7) at quality 100. Prior 0.5 (photos are 1/f; the 99%-energy
cutoff may sit low on smooth natural content regardless of loss, which would make (a) weaker on photos than on white noise). Kill: native photo under 0.7.

The detector flags band-limited, not fake. Any number below is a band-limit reading, not a verdict on the image.

## Real-image sourcing policy (for round 4; nothing downloaded under it yet)

Rank by provenance, best first. Record license, date, URL, and a sha256 per image in a manifest (`_STATE/` or the pattern note); an image without a date is excluded, not down-weighted.
1. Capture from the original software (own screen capture of a running original or an emulator of the original release; license: own capture, but the underlying art stays the rights holder's, so keep it local).
2. Dated launch-window marketing (press kit, ads, box art with a printed or archived date).
3. Dated release art from MobyGames or the developer's own site (Cyan), date as listed there.
4. Later remakes, labelled as later and never mixed into the original cohort.
5. Undated images: excluded.
Natural test pair: original Myst (1993, pre-rendered, palette under 256 colors per The Register 2013) versus a later remake. Palette quantization
and dithering are band-limit-adjacent confounds and must be named in the pre-registration for that round, not discovered after it.
Gate: Zach approves each download (filename, source URL, size, license) before it happens.

### Round 3 results, 2026-10-15 (probe script kept in the session scratchpad, not committed; stat functions are the merged `cutoff_ratio` and `tail_ratio`)

Ground: three Apple bundled photos (Flower 1, Flower 3, Mojave Day), each as 5120x2880 native and as a `sips` 1280-wide downscale, center 256x256 crop, re-encoded with real JPEG (`sips`) at q 100/60/30/10 and decoded back to PNG. Cells are (cutoff, tail).

| image | q100 | q60 | q30 | q10 |
|---|---|---|---|---|
| Flower 1 native | 0.469, 0.070 | 0.461, 0.097 | 0.430, 0.089 | 0.453, 0.091 |
| Flower 1 down4 | 0.375, 0.112 | 0.414, 0.205 | 0.320, 0.094 | 0.328, 0.075 |
| Flower 3 native | 0.789, 0.221 | 0.797, 0.244 | 0.680, 0.127 | 0.586, 0.091 |
| Flower 3 down4 | 0.844, 0.188 | 0.883, 0.260 | 0.820, 0.178 | 0.688, 0.077 |
| Mojave Day native | 0.828, 0.104 | 0.703, 0.048 | 0.797, 0.087 | 0.828, 0.124 |
| Mojave Day down4 | 0.430, 0.412 | 0.641, 0.695 | 0.281, 0.251 | 0.281, 0.257 |

- B6b FAIL as a general claim (prior 0.65). The pre-registered effect (cutoff down 0.15 or more AND tail at least halved at q10) appears in 2 of 6 rows (Flower 3 native, 0.789 to 0.586, tail 0.221 to 0.091; Flower 3 down4, 0.844 to 0.688, tail 0.188 to 0.077). Flower 1 (both) and Mojave native show no effect; Mojave down4 drops 0.149, one thousandth short. Kill condition met on 4 of 6. JPEG loss does NOT reliably flag, but it does on some content, so "JPEG is safe" is also unearned.
- B6c FAIL (prior 0.8). Ratio rises by more than 0.02 with harsher quantization in 5 of 6 rows (for example Mojave down4 0.430 to 0.641 from q100 to q60, tail 0.412 to 0.695). Re-quantizing an already-compressed image can add blocking edges that put energy back in the high band, so quality is not a monotone knob.
- B8 mixed (prior 0.5). Native q100 cutoff: Flower 1 0.469 (under the 0.7 line, kill met for that image), Flower 3 0.789, Mojave Day 0.828. A smooth, shallow-depth-of-field photograph is band-limited with zero upscaling, so the 99%-energy cutoff reads low on honest optics. This is the round-1 smooth-native false positive reappearing on a real photo.
- What this changes: on natural photos (a) is content-dependent in both directions. The cutoff alone cannot carry a verdict; it needs a same-content reference (test b) or a calibrated per-source baseline.
- Limits, stated plainly: three images, one 256 crop each, 16 sampled rows per crop, 'native' is already one JPEG generation, no repeats. The row-to-row noise (Mojave q60 vs q30) is probably within sampling variance of this setup; a repeat across many crops is needed before any rate is quoted.
- Not run: real-image validation (round 4). Needs Zach's approval per download under the sourcing policy above.

## Round 4: pre-registered beliefs (written before any capture exists; nothing downloaded or captured yet)

Pair: Myst 1993 (pre-rendered, palette under 256 colors per The Register 2013) versus realMyst: Masterpiece Edition (Cyan, released 2014-02-05, real-time 3D rebuild, per the Steam store page). The 2014 build re-renders the scenes; it is not a resample of the 1993 art. Ground for the dates: Wikipedia Myst page and Steam app 244430, both read 2026-10-15 via web search, neither a primary source.
Access status: Zach owns no copy. The engine route (ScummVM) is open source but needs the original game data files, which are commercial; no free legal data set was found. A period VM needs a licensed OS and ROM image. Both are unconfirmed here and must be checked before any plan relies on them. No unlicensed copy will be used.

B9. 1993 captures score lower cutoff_ratio than 2014 real-time captures of the same scenes. Prior 0.6. Kill: the 2014 captures score lower on the median of five matched scenes.
B10. Palette dithering in the 1993 images raises tail_ratio above the 2014 value, masking band-limiting. Prior 0.5. Kill: 1993 tail_ratio not above 2014's.
B11. Capture scale (emulator or window scaling) moves the cutoff by more than the 1993-vs-2014 gap. Prior 0.7. Control: integer scaling or native-resolution capture only; the claim is tested by capturing one scene at 1x and 2x. Kill: scale effect under half the era gap.
Limits stated now: five scenes, one capture each, 16 sampled rows per crop (round 3 showed that noise is large); a result is a reading of band-limit, never "fake" or "upscaled".

## Round 5: pre-registered beliefs (written before ScummVM or any game file was fetched or run)

Approval: Zach said "yes" in chat on 2026-10-16 to (1) ScummVM from scummvm.org, (2) `FOTAQ_Floppy.zip`, 6.8 MiB, from https://downloads.scummvm.org/frs/extras/Flight of the Amazon Queen/ (Flight of the Amazon Queen, freeware floppy build; the page lists it as freeware, licence text not on the page, Debian's copyright file describes the sibling Lure data as BSD-like and a ScummVM developer said the same for this title, neither read in full). Manifest (URL, bytes, sha256, licence text found) is recorded with the results. Captures stay in the session scratchpad, not in git.
Scope: this tests the capture method, the integer-scale control and the palette confound on real 1990s 256-colour art. It is NOT a Myst result and says nothing about era.
B21. A 2x integer-scaled capture of the same scene moves the absolute cutoff (ratio x width/2) by more than the spread between two different scenes at 1x. Prior 0.5. Kill: scale effect under the between-scene spread on 4 or more of 5 scenes (then B11's worry is not supported for this setup).
B22. The bilinear-foil K4 gap (true frame minus bilinear 4x upscale of its 64 row, bar 4.8 cycles) clears the bar on at least 4 of 5 scenes. Prior 0.4 (round 2 of the arcade note found rendered UI-like art is where the statistic fails). Kill: fewer than 4 of 5.
Limits stated now: five scenes of one game, one capture each, 16 sampled rows; the game was painted and dithered for 256 colours, so palette and dither confound the reading (detector note B10) and the result is a band-limit reading, never "fake" or "authentic".

### Round 5 results, 2026-10-16 (ScummVM 2026.4.0 running Flight of the Amazon Queen floppy build; capture key Alt+S with the window frontmost, per the ScummVM keyboard-shortcuts docs; analysis script in the session scratchpad, not committed; images scratchpad only)

Manifest. ScummVM: `scummvm-2026.4.0-macosx.dmg` from https://downloads.scummvm.org/frs/scummvm/2026.4.0/, 169,280,944 bytes, sha256 5614527fa57ffce14773c69923b96eeb7b1b135bcd96bfe74640ca341cad4598 (matches the download page). Licence: the dmg ships GPL, LGPL, BSD, MIT and other licence files; not read in full. Game: `FOTAQ_Floppy.zip` from https://downloads.scummvm.org/frs/extras/Flight%20of%20the%20Amazon%20Queen/, 7,109,570 bytes, sha256 2e59de85f708cdb32bf85c85b394ac091c05f7647e856b71f5b3ae73fde761e0; `queen.1` 22,677,657 bytes (md5 recorded in ScummVM log, not a commit). Licence: the zip's `readme.txt` permits free distribution on any medium with the readme and notices intact, and permits modification (headline terms read, not every clause).

Capture facts. A background keystroke did not save a screenshot; the same key worked once the window was frontmost under display-scope control. ScummVM's screenshot is the window output, not the game surface: 1280x1017 PNG, the game drawn 4x nearest-neighbour inside black bars (rows 108 to 908). Taking every 4th pixel recovers the 320x200 native frame exactly: 199 of 199 block-consistency checks passed on all six files. So the 1x versus 2x comparison pre-registered in B21 was NOT run; the scale confound was removed instead, by recovering the native frame losslessly. That is a design change made after seeing the output.

Deviations from the pre-registration, stated before the numbers. (1) Native frames are 320x200, so the 256-px crop could not be used; I used a 192x192 center crop with rows 192 / 96 / 48 and scaled the K4 bar by 192/256 to 3.6 cycles. (2) Six frames, not five scenes: frame 00000 was taken before the rule was fixed; 00001 to 00005 were taken on a fixed 10-second schedule. All six sit in two scenes (the credits scroll and the opening room, with different poses and captions), so the distinct-scene count is 2, not 5.

| frame | abs cutoff 48 / 96 / 192 | ordering | K4 gap vs bilinear (bar 3.6) |
|---|---|---|---|
| 00000 (credits, pre-rule) | 23 / 48 / 92 | ok | 55 |
| 00001 | 23 / 47 / 84 | ok | 58 |
| 00002 | 22 / 41 / 82 | ok | 56 |
| 00003 | 22 / 45 / 84 | ok | 57 |
| 00004 | 22 / 43 / 86 | ok | 59 |
| 00005 | 23 / 43 / 84 | ok | 57 |

- B21: NOT TESTED as written (see above).
- B22: cleared on 5 of 5 frames (prior 0.4), but the claim was "4 of 5 scenes" and only 2 distinct scenes exist, so it is not earned. The gap of 55 to 59 is more than 15 times the scaled bar, so the margin is not marginal. Plausible reasons it passed where rendered UI failed in the arcade note's round 2 (untested): painted, dithered, high-contrast sprite art with soft gradients rather than one-pixel text; and the foil is bilinear, the weaker upscaler (arcade note round 6).
- What the data cannot say: anything about era, anything about palette or dither (B10 untouched; palette not extracted), anything about other upscalers, or whether the result survives scenes beyond a room and a credits roll.
- Round 6 need: five distinct scenes means playing past the intro to different rooms, which needs real input, not a timed capture.

## Round 6: pre-registered beliefs (written before the game is played past the intro; Zach watching, Claude driving the window)

Scope: close round 5's gap (2 distinct scenes, not 5). Same game, same build (Flight of the Amazon Queen floppy, ScummVM 2026.4.0), same recovery of the native 320x200 frame by taking every 4th pixel, same 192x192 centre crop, bar scaled to 3.6 cycles.
Scene rule, fixed now: the first five distinct room backgrounds reached in play order after the intro is skipped, one Alt+S capture per room taken on arrival, no selection by me, no retakes except for a capture that failed to save. A room counts as new when its background differs, not when the characters or the caption do. If the game cannot reach five rooms in the session, I report how many and stop.
B23. Ordering abs cutoff 48 < 96 < 192 holds on all five scenes. Prior 0.8. Kill: an inversion on any scene.
B22 (re-asked). The bilinear-foil K4 gap clears 3.6 cycles on at least 4 of the 5 scenes. Prior 0.7 (round 5: 55 to 59 on two scenes). Kill: fewer than 4 of 5.
B24. Scene-to-scene spread of abs cutoff at 192 exceeds 10 cycles across the five scenes (round 5 had 82 to 92 on two scenes). Prior 0.7. Kill: spread of 10 or less (then content dependence is smaller than my round-3 reading suggested for this art).
B21b (replaces round 5's untested B21). The recovered native frame is byte-identical between two window scale factors for one scene (capture the same frame at scale 2x and 4x, recover, compare). Prior 0.85. Kill: any differing pixel (then recovery is not lossless and every number so far carries an unmeasured error).
Limits stated now: one game, five rooms, 16 sampled rows, painted and dithered 256-colour art, a reading of band limit only; nothing here is about era, palette extraction (B10 untouched) or other upscalers.
