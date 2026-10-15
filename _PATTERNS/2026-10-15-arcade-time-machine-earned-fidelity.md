# Arcade time machine: the same scene at each era's earned fidelity

Date: 2026-10-15. Origin: Zach's idea, same day. Status: concept note only. Nothing is built and nothing will be until B1 below is run.

Prior art: ran /prior-art (`scripts/prior_art.py`). Top hits used: `_PATTERNS/2026-10-15-unearned-sharpness-detector.md` (the detector, rounds 1 to 4),
WORLD.md "THE RENDER SCALE", memory `earned-fidelity-not-maximal-diamond-cut`, `_PATTERNS/2026-10-15-cyan-linking-structure-audit.md` (same Myst-era pair). No existing arcade or time-dial surface in the repo.

## The idea

A booth. The player dials a year. The same scene renders at that era's earned fidelity: palette, resolution, dithering. A 1993 dial gives a sub-256-color,
dithered, low-resolution render; a 2014 dial gives full real-time 3D. The unearned-sharpness detector is the golden-ticket gate: before a frame is shown,
it checks that the frame is no sharper than the dialed era's information content supports, and refuses it if it is.

## Parts, labelled

| Part | Label | Why |
|---|---|---|
| Era table: year to palette size, pixel grid, dither kernel, bit depth | MECHANISM | Plain lookup; each row can cite a dated source (sourcing policy, detector note round 3). |
| Renderer that downsamples, quantizes and dithers one scene per row | MECHANISM | Deterministic image ops; the planted-fault pattern already exists in `scripts/sharpness_cutoff.py`. |
| Gate: `sharpness_cutoff.py` cutoff and tail statistics on the output frame vs the era row | MECHANISM, with a stated weakness | Runs today. It reads band-limit only (see Honesty). |
| Dial as a control, booth door, ticket stub | METAPHOR | Interface skin; carries no claim. |
| Xavier Riddle's time-travel museum (visit a period, see it as it was) | METAPHOR | Framing for "era-true view"; no mechanism borrowed. |
| Bill and Ted's phone booth (dial a number, arrive) | METAPHOR | Same: the input is a year. |
| Willy Wonka's glass elevator and factory gate | METAPHOR | The elevator is the transition animation. |
| Golden ticket | METAPHOR for the gate; MECHANISM only in the sense that the gate returns pass or refuse | A frame without a passing reading does not enter. |
| Mapping to WORLD.md THE RENDER SCALE: era ladder as the fog ladder | METAPHOR until B2 | The scale ties fidelity to Y-gate state; here fidelity would tie to year. Different axis, same "never above the data" rule. Untested that the two compose. |

Tie to THE RENDER SCALE: that table says fidelity is earned, never above what the data deserves, and that text stays readable at every depth (fog by weight and
grain, never by dimming). The booth reuses both rules. The era sets the resolution ceiling; legibility is not allowed to fall with it.

## Honesty: what the gate can and cannot say

The detector flags band-limited, not fake. Rounds 1 to 3 of the detector note found: a smooth honest native image reads low (known false positive), JPEG loss does not
reliably flag, and quality is not a monotone knob. So in this booth the gate can only refuse a frame whose measured band limit is ABOVE what the era row allows
(too sharp for the year). It cannot certify that a passing frame is authentic to the era, and a frame of a naturally smooth scene may pass for the wrong reason.
"Refuses fidelity above the era" is the claim; "proves it looks like 1993" is not.

## Pre-registered belief (written before any build)

B1. Claim: for one planted scene, rendering it at three era rows (for example 64x64 / 16 colors, 128x128 / 64 colors, full 256x256) and measuring
`cutoff_ratio` after the era's downsample, the cutoff is monotone non-decreasing with era resolution, and an over-sharp frame (the full-resolution render submitted
under the lowest era row) reads at least 0.15 above that row's honest frame. Prior 0.6. The risk is that dither adds broadband noise that props the cutoff up
(detector note B10 raised the same worry).
Test (about 30 lines, stdlib, reuses `cutoff_ratio` and the box downsample): render, measure, compare.
Kill: any inversion in the three-row ordering, OR the over-sharp-vs-honest gap under 0.15. On a kill the gate is not trusted for this use, the metaphor stays a
skin, and the note is closed as "gate cannot arbitrate era fidelity".

Not tested, said now: real era art, the Myst pair (blocked on licensed data per detector note round 4), natural photographs, any claim about authenticity.

## Next action

Zach decides whether to run B1. Until then: no code, no assets, no downloads.

## Kintsugi seam, 2026-10-15 (added after merge; the original B1 above is kept, not rewritten)

B1 as written is mis-specified. Ground: `scripts/sharpness_cutoff.py` `cutoff_ratio` returns `k / half`, so it is normalized to each image's own Nyquist. A rendering at lower resolution can therefore read a HIGHER ratio than the same scene at higher resolution, and "monotone non-decreasing with era resolution" fails for a structural reason, not an empirical one. One read-only run on a single planted scene (one agent, not re-run by me) gave ratios 0.75 / 0.594 / 0.562 at 64 / 128 / 256 px, and absolute cutoff (ratio times width/2) of 24 / 38 / 72, which orders correctly. Treat that as evidence the test needs rewriting, nothing more.

Replacement kill hypotheses (written before any run):
- K1: absolute-cutoff ordering holds across 64 / 128 / 256 on three scenes; kill on any inversion or an over-sharp-minus-honest gap under 0.15 in absolute terms.
- K2: dither does not move the reading by 0.15 or more (the single run showed 0.812 to 1.0 on raw ratio); kill otherwise.
- K3: a smooth analytic scene does not pass an over-sharp frame; kill otherwise.
- K4: a full-resolution render submitted under the lowest era row is separable from an honest low-era frame without knowing the claimed grid; kill otherwise.
- K5: some route exists for a frame to reach the gate without passing the era renderer; kill if the list is empty (then the gate only tests the renderer against itself).
- K6: no "era-true", "authentic" or "proves" in any new surface; kill on any hit.
- K7: era axis composes with the Y-gate axis (B2); parked until K1 to K4 pass.

Scope corrections to the concept-note round (PR 1322 and the follow-on work):
- The "chiefs gauntlet" that ranked these paths used CEO, CTO, CISO, CFO, design, COO and Skeptic roles. Those are not the repo's Staff of Chiefs (Loki, Devil's Advocate, Conductor, Bayesian, Meta-Operator; `runtime/specs/effort-policy.json`). The ranking is a reading by non-canonical roles.
- The three scenario agents said they had not read ADR-058 or WORLD.md in full, so "ran an I.D.E.A. loop" is looser than it sounds.
- The eight seed agents (PR 1324) are untested: no ledger row has a recorded use. The pre-commit hook was probably armed but was not exercised with a deliberately bad seed.
- `idea-curator-taxonomist` misdescribed the Curator (keep or cut) and was re-scoped to `idea-curator` in PR 1333. The Curator (`operators/arcs_operators_curator.py`) offers one orthogonal reframe.
- The Folksonomy "100 receipts" gate in the registry note is not the same constant as `MIN_CORPUS_SIZE = 5` in `operators/arcs_operator20.py`; where the 100 is enforced was not found.

## B1 result, 2026-10-15 (`python3 scripts/era_b1_probe.py`; kill lines K1 to K4 were fixed in the script header before the run)

Ground: merged in arcs-v9 PR 1336 at cdd7a274 (probe `scripts/era_b1_probe.py`, receipt 2026-10-15--b1-result-first-seed-uses-pr1336--ZH; the table below is the probe's stdout on that commit). Method: absolute cutoff = `cutoff_ratio` x width/2, three seeds each of an edge scene and a noisy-smooth scene, one analytic smooth scene, box downsample from a 256 master, 4x4 Bayer dither at 16 levels, nearest-neighbour 4x upscale of the 64 row. Results are from the committed probe; limits: one dither kernel, my own scenes, 16 sampled rows.

| Scene | abs cutoff 64 / 128 / 256 | K1 | K2 (dither shift / 32) | K4 gap (cycles) |
|---|---|---|---|---|
| edge, 3 seeds | about 24 / 41 / 75 to 83 | pass | fail (0.22 to 0.25) | pass (14 to 22) |
| noisy, 3 seeds | 7 / 43 to 48 / 117 | pass | 2 pass, 1 fail | pass (about 109) |
| smooth analytic | 3 / 3 / 3 | fail | fail (0.38) | fail (0.0) |

Verdict: B1 as pre-registered is killed (any single failure kills it). Attack by `chief-loki` (numpy re-implementation matched the stdlib cutoff) changed how to read it:
- K1 and K4 hold on textured scenes and are robust: the K4 foil (nearest-neighbour) is the hardest of the upscalers, gaps are 3 to 20 times the bar. The smooth-scene failure is real and not a window or sampling artifact (3/3/3 under Hann, detrend and all 256 rows); the script's own docstring lists it as a known false positive.
- K2 failed as pre-registered, but the reading "dither defeats the sharpness check" is wrong. The control arm was already 4-bit quantized, so the test measured quantization against quantization plus dither. Random dither fails too, and at 8-bit K2 passes 7 of 7. At a 99.9% cutoff it also passes 7 of 7. The finding is: the 99% cutoff cannot see through 4-bit quantization noise, because a Nyquist tone carries over 1% of the energy.
- Not a rescue: moving the cutoff to 99.9% is a post-hoc change and does not loosen K2. It needs the round-2 test below.

Surviving narrower claim (not yet earned): on textured scenes the absolute-cutoff statistic orders era resolution and separates a true high-resolution frame from a nearest-neighbour upscale. A smooth scene cannot discriminate era with this statistic.

### Round 2: pre-registered beliefs (written before any round-2 run)
B12. With an unquantized control, 4-bit quantize-only and quantize-plus-dither shift the 64-row reading by under 0.15 of 32 relative to each other. Prior 0.5. Kill: 0.15 or more on 2 or more of the 7 scenes.
B13. The three-row ordering and K4 gap hold on at least 2 real rendered images (screenshots, not photographs) at the same scale. Prior 0.4. Kill: ordering inverts on either.
Not tested: real era art, photographs, other kernels.
