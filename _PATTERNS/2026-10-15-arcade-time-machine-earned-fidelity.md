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
