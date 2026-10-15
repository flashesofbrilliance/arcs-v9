# A 5D step sequencer with magnetic snap points: design and checks, written before building

Date: 2026-10-15. Origin (Zach): slicing and sampling with magnetic snap points; glitch controls and keyboard browsing for finger-drumming in real time; "think about this as a 5D step sequencer"; "a Rubik's cube of sorts where the sides snap together based on coherence and magnetic and gravitational pull"; and a YouTube video for it. Builds on Phosphor (`_ARTIFACTS/phosphor.html`), the 5x5 grid already used for decision geometry, and the take model in ADR-087 rule 10.

## Mechanism and metaphor, kept apart

Mechanism (computed, testable): slices, magnets, a coherence score, a mass, a greedy arrangement, a 5-axis step, twists as arithmetic on step digits, sample-accurate triggering.
Metaphor (a way of seeing it): the cube, its faces and its "solved" state. The cube is a view over the mechanism and is built last.

## Slices and magnetic snap

A slice is a region [start, end] of the loaded song. A magnet is a time the slice edge is pulled toward, with a weight:
- chapter boundary (novelty peak), weight 1.0
- onset (a spectral-flux peak above its local mean), 0.8
- loudness valley (a local minimum of level), 0.6
- zero crossing within 5 ms of the point being snapped to, 0.4 (makes the cut click-free)
- an existing slice edge or grid line, 0.5

Pull radius: Soft 60 ms, Medium 120 ms (default), Strong 200 ms. A dragged edge at time x snaps to the magnet m that maximizes weight x (1 - |m - x| / radius) among magnets inside the radius, then to the nearest zero crossing within 5 ms of m. Alt held, or snap Off, bypasses it. Magnets are drawn on a strip under the scrubber.

## Coherence and gravity

Coherence of slice A flowing into slice B, c(A to B), is a number from 0 to 1 over the last 120 ms of A (its tail) and the first 120 ms of B (its head): 0.5 x cosine similarity of the 64-band spectra + 0.3 x (1 - |level difference|) + 0.2 x boundary match (the two edge samples are close and the waveform slope has the same sign). Two slices lock when c is at least 0.7.
Mass of a slice: duration x mean level x (1 + novelty at its start). Gravity is a use of mass, not a force simulation: the heaviest slice is the anchor of an arrangement.
Greedy arrangement ("solve"): start from the heaviest slice; repeatedly append the unused slice with the highest c from the current tail, ties to the heavier. The score of an arrangement is the mean c along it.

## The 5D step

A step is five digits, each 1 to 5, which makes 3,125 cells (the 5^5 space used elsewhere in ARCS). A pattern is 16 steps in a 4 x 4 grid.
1. Slice: which of five slices plays (a bank of five).
2. Glitch: clean, stutter, reverse, freeze, tape-stop.
3. Rate: x0.5, x0.75, x1, x1.5, x2 (pitch moves with rate).
4. Gate: 1/16, 1/8, 1/4, 1/2 or all of the step.
5. Cut: visual resolution rung, 16 x 9, 64 x 36, 256 x 144 (8-bit), 1920 x 1080 or vector.
Tempo is estimated from the song (the most common spacing between onsets) and can be overridden.
A twist is an operation on a pattern: for the steps whose digit on axis a equals v, add 1 modulo 5 to their digit on axis b (b is not a). Five twists of the same kind return the pattern. This is the cube's rotation, defined as arithmetic.

## Keyboard (no mouse needed)

Tab toggles Perform and Browse. Browse: comma and period jump to the previous and next magnet; Enter marks a slice start, then end; Escape cancels. Perform: sixteen pad keys (1234, QWER, ASDF, ZXCV) trigger the 5D cell under the cursor for as long as the key is held; five pairs of keys step each axis down and up; the cursor shows the five digits. Existing keys (1 to 4 for mode, space, brackets) keep working in Browse.

## Checks (pass or fail)

S1 Snap: inside the radius an edge lands on the best-scoring magnet; outside it stays put; Alt or Off bypasses it; a heavier magnet beats a nearer lighter one only when its score is higher.
S2 Click-free: on two real songs, slices snapped to a magnet have an edge sample magnitude under 0.01 on at least 90 percent of snaps.
S3 Coherence has meaning: cut a song into 12 slices at onset magnets. For at least 80 percent of true neighbor pairs, c is above the median c of non-neighbor pairs. Kill: under 60 percent, and coherence is reported as not meaningful.
S4 Arrangement recovery: the greedy chain from the heaviest slice recovers at least 40 percent of the true adjacent pairs (a random order recovers about 9 percent for 12 slices). Kill: under 25 percent.
S5 Timing: a pad press starts its sound within 20 ms of the key event; a stutter retrigger period is within 2 ms of the intended.
S6 Determinism: the same pattern rendered twice offline produces identical audio.
S7 Twists: five applications of one twist restore the pattern; twists whose a and b axes are disjoint commute.
S8 Keyboard: every function is reachable without the mouse, focus is never trapped, and Perform keys never fire while a text field has focus.
S9 Glitch visuals are a pure function of time and the recorded events: the same pixels on replay.
S10 Photosensitivity: no luminance flash faster than three per second in glitch visuals, measured frame to frame.

## Video

A take (the recorded key events) can be rendered offline into a video: frames from the page at 30 per second, audio from an offline render of the same take, joined with ffmpeg. Checks: frame count equals duration times 30; audio length matches within one frame; rendering twice gives identical frames. The video is saved to a local file. Uploading it anywhere, YouTube included, is the owner's separate decision and is not done here.

## Order of work

1. Slices, magnets, snap, coherence and arrangement, with S1 to S4, S2 on the owner's own songs, kept local.
2. Keyboard browsing and the sampler pads with sample-accurate playback, S5, S8.
3. The glitch engine, the 5D pattern, recording and twists, S6, S7, S9, S10.
4. The cube view.
5. The offline video render.

## Not claimed

That the arrangement "sounds good", that coherence matches a listener's sense of flow, that the pad latency in a real browser with real hardware is within 20 ms (it is measured headless), or that any of this is the right feel for finger-drumming; that needs the owner's hands. Publishing remains separate from building. Suno's terms for any public use of the songs are the owner's to confirm.

## Results, phase 1: slices, magnets, coherence, arrangement (2026-10-15)

`PHOSPHOR_FILES=<two songs> node scripts/phosphor_slice_check.mjs _ARTIFACTS/phosphor.html`, thresholds as pre-registered above.

| Check | Song A (m4a) | Song B (mp3) |
|---|---|---|
| S1 snap matches an independent reference | pass, 0 of 417 mismatches; outside the radius 33 of 33 stay put; bypass 450 of 450 | pass, 0 of 392; 58 of 58; 450 of 450 |
| S2 click-free, first version (nearest zero crossing) | FAIL, 368 of 417 (88 percent) | FAIL, 248 of 392 (63 percent) |
| S2 click-free, after refinement (quietest crossing within 5 ms) | pass, 405 of 417 (97 percent) | pass, 392 of 392 (100 percent) |
| S3 true neighbors beat the median non-neighbor | pass, 9 of 9; mean 0.847 vs 0.657 | pass, 8 of 9 (0.89); mean 0.861 vs 0.770 |
| S4 greedy arrangement recovers true adjacent pairs | pass, 7 of 9 (0.78); random about 0.11 | FAIL the 0.40 target at 3 of 9 (0.33), above the 0.25 kill |

The S2 criterion was not changed. The first version failed it, the snap was refined after seeing why (the nearest sign change can still sit on a large sample for bright, loud material), and both rounds are reported. S4 on song B is a miss against the target and not a kill; the arrangement rule was not tuned afterward. Coherence therefore carries real information on these two songs (S3 passes on both). Limits: two songs, 10 slices each, cut at onsets; no listening test.

## Amendment 1 (2026-10-15, before building): Look and Glitch controls

Zach: log curve controls, color inversion and palette swap, and glitch controls like stutter.

Look chain, applied to the picture after the scene is drawn, as one lookup-table pass so it stays cheap:
- Curve (Linear, Log, Exp, S) with an Amount from 0 to 100. Log lifts shadows like a camera log profile: y = log(1 + k x) / log(1 + k) with k = 1 + 63 x amount. Exp is the inverse family and sinks shadows. S blends toward a smoothstep. Amount 0 is the identity.
- Invert, a plain toggle.
- Palette: Original, or a gradient map of brightness onto ARCS (obsidian, cyan, gold), Phosphor (black to green), Amber (black to amber), Indigo and paper, Heat (black, red, yellow, white), Mono. Invert runs on brightness before the gradient, or as the RGB complement for Original.

Glitch, as momentary effects held on keys in Perform mode (Tab toggles it):
- Stutter: while held, the last L of the song loops. Visual: the time used to draw is looped inside the window. Audio: the playing source is replaced by a sample-accurate loop of that window; the song position keeps advancing underneath and the main source rejoins at the true position on release. L is 1/16, 1/8 or 1/4 of a beat (the estimated beat, or 120 BPM if none was found).
- Freeze: stutter with a 60 ms window.
- Tear, RGB split and Block shuffle: pixel effects seeded by the frame number so a frame is repeatable.
- No effect flashes. Invert is a toggle, not a momentary flash.

Checks.
L1 Curve: Log lifts mid-gray (LUT[128] above 128), Exp sinks it, both keep 0 and 255; Amount 0 leaves the picture byte-identical; the log LUT is monotone.
L2 Invert twice returns the picture byte-identical; Original with Invert is the RGB complement.
L3 Palettes: each gradient maps brightness 0 and 255 to its end colors; every pixel's color lies within 4 levels of the gradient.
L4 Stutter visual: with stutter held, frames at times inside one window are identical and differ from the unglitched frame. Stutter audio: the active loop's start and end differ by L within 2 ms and its start is the held time.
L5 Keyboard: Tab toggles Perform; holding the key starts the effect and releasing ends it; keys are ignored while a text field has focus; the page works without the mouse.
L6 Photosensitivity: with all glitches on, the mean luminance change between consecutive frames stays under 0.1 over 60 frames.
