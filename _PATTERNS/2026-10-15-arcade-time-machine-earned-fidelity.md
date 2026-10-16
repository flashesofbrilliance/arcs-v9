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

### Round 2 results, 2026-10-15 (`python3 scripts/era_b1_probe.py --round2`; the probe was extended in the same change as this section)

- B12 FAIL (prior 0.5). Dither vs quantize-only shifts the 64-row reading by 0.15 or more of 32 on 5 of 7 scenes (0.22, 0.25, 0.22, 0.38, 0.22; the two noisy scenes at 0.12). My pre-registration error: B12 restated a comparison round 1 had already run (the "clean" arm there was quantize-only), so the data to kill it already existed. New finding from the unquantized arm: 4-bit quantization alone moves the reading 0.53 to 0.66 of 32 on the smooth and noisy scenes (3 to 20, 7 to 28 cycles) and only 0.03 on the edge scenes. The cutoff reads quantization noise as detail where the scene has little real high-frequency energy.
- B13 SPLIT (prior 0.4). Ordering a64 < a128 < a256 held on both real images (good-fears-og 31/50/73; honest-og 32/52/89, central 256 crops of 1200x627 and 1200x630 rendered OG images, not photographs). The K4 gap FAILED on both: true 256 reads LOWER than the nearest-neighbour upscale of its 64 row (gap -28.0 and -11.0 cycles; the bar was +4.8). The kill line as I wrote it ("ordering inverts") was not tripped, but the claim also named the K4 gap, so the claim as stated is false. I am reporting it as a split, not taking the loophole. Cause not tested; a guess is that crisp one-pixel text and UI edges survive nearest-neighbour replication as broadband content, unverified.
- What this does to the surviving claim: ordering across eras holds on textured synthetic scenes and on two real rendered images. The upscale separation (K4) holds on synthetic textured scenes and fails on real rendered UI. A gate built on this statistic cannot yet refuse an upscaled frame of real UI-like content. Status: the gate stays INTENDED, not BOUND.
- Still not tested: photographs, real era art, other upscale kernels, any scene beyond 7 synthetic and 2 rendered images, a 99.9% cutoff under a pre-registered test.

### Round 3: pre-registered beliefs (written before any download or run)

Sourcing: three Library of Congress service JPEGs, approved by Zach in chat before download, kept in the session scratchpad only (not in the repo). Rights text is LoC's own ("No known restrictions"), not a formal public-domain declaration. Manifest (url, bytes, sha256, rights text) is recorded below with the results. Confounds named now: each file is a 1024-px JPEG derivative of a larger scan, so (1) the original era's resolution is not preserved, (2) it is one JPEG generation, (3) the measurement can say nothing about era-of-capture.
Files: 4a27449v.jpg (Jacksonville street car, c.1890, Detroit Publishing Co), 8a16694v.jpg (Street musicians, Maynardville TN, 1935, FSA), 4a05168v.jpg (Havana Street, c.1900, Detroit Publishing Co). Decode: macOS `sips` to PNG, central 256 crop of luma, same probe as rounds 1 and 2.
B14. Ordering a64 < a128 < a256 holds on all three photographs. Prior 0.7. Kill: ordering inverts on any one.
B15. The K4 gap (true 256 minus nearest-neighbour 4x upscale of its 64 row) is at least 4.8 cycles on at least 2 of 3. Prior 0.3 (it failed on both rendered images in round 2). Kill: under 4.8 on 2 or more of 3.
Limits stated now: three images, one crop each, 16 sampled rows; a result is a band-limit reading and says nothing about fidelity to an era.

### Round 3 results, 2026-10-15 (`python3 -I scripts/era_b1_probe.py --real <png> ...`; images decoded from the JPEGs with macOS `sips`, kept in the session scratchpad, not in the repo)

Manifest (url prefix https://tile.loc.gov/storage-services/service/pnp/, size matched the item JSON from loc.gov before download, rights text is LoC's "No known restrictions on publication"):

| file | what | bytes | sha256 |
|---|---|---|---|
| det/4a20000/4a27000/4a27400/4a27449v.jpg | Jacksonville street car, c.1890, Detroit Publishing Co, 1024x743 | 373728 | 26304854c56e1dedecdc9d0a2daed91bd78fa260f1f9aef1a7dfef4dad09d702 |
| fsa/8a16000/8a16600/8a16694v.jpg | Street musicians, Maynardville TN, 1935, FSA, 1024x733 | 322119 | e996473ba36dac125789e20d5a1fa3195945d74abc61312a15f10ae0232101b5 |
| det/4a00000/4a05000/4a05100/4a05168v.jpg | Havana Street, c.1900, Detroit Publishing Co, 805x1024 | 161609 | 378c7357c8f325ae030b1d3e36afd060d90dd87ed276c8502c2c8ee461d0bf44 |

| image | a64 / a128 / a256 | ordering | K4 gap (cycles; bar 4.8) |
|---|---|---|---|
| 1890 street car | 29 / 58 / 118 | ok | 63.0 |
| 1935 street musicians | 26 / 44 / 69 | ok | 8.0 |
| c.1900 Havana street | 25 / 55 / 107 | ok | 41.0 |

- B14 survived: ordering held on all three (prior 0.7; one crop each, so weak).
- B15 survived, against its prior (0.3): the K4 gap cleared 4.8 on 3 of 3, not merely 2. Photographs separate a true 256 frame from a nearest-neighbour upscale where the two rendered UI images (round 2) did not. The 1935 image clears the bar by only 3.2 cycles, so treat it as marginal.
- Reading: the statistic discriminates on natural photographic texture and fails on crisp rendered UI. That is a statement about content class, not about era. Confounds stand: each file is a 1024-px JPEG derivative of a larger scan, so the capture-era resolution is gone and one JPEG generation is baked in; the three images differ in subject and tone as well as in date, so nothing here can be attributed to the year.
- Not tested: the TIFF masters (13 to 26 MB each, not approved), era-of-capture effects, other crops, other upscale kernels, 99.9% cutoff, real era game art. Round 4 candidates: several crops per image for a variance estimate; the 1935 master.

### Round 4: pre-registered beliefs (written before the master was downloaded or run)

Sourcing: one file, `fsa/8a16000/8a16600/8a16694u.tif` under https://tile.loc.gov/storage-services/master/pnp/, the master scan of the 1935 FSA photograph used in round 3 (item size from the loc.gov item JSON: 12,964,154 bytes). Approved by Zach in chat ("lets approve the master") after the filename, source and size were stated in the round 3 findings. Kept in the session scratchpad, not in the repo. Rights text: LoC "No known restrictions" (FSA/OWI), not a formal public-domain declaration. Decode with macOS `sips` to PNG; 8-bit luma only (a 16-bit decode is out of scope and will be reported, not worked around).
Why: round 3's 1935 image cleared the K4 bar by only 3.2 cycles on a 1024-px derivative with one crop. The master carries the scan's native detail, and a grid of crops gives a variance estimate.
B16. Ordering a64 < a128 < a256 holds on at least 8 of 9 native-resolution 256 crops (3x3 grid across the image). Prior 0.7. Kill: ordering inverts on 2 or more crops.
B17. The K4 gap (true 256 minus nearest-neighbour 4x upscale of its 64 row) is at least 4.8 cycles on at least 6 of 9 crops. Prior 0.5. Kill: fewer than 6 of 9.
Limits stated now: one photograph, one scan, 9 crops that share a scene and tone; flat sky or blank-wall crops may read as the smooth-scene failure (3/3/3), and if so that is a pre-registered known outcome, not a surprise; the result says nothing about era.

### Round 4 results, 2026-10-15 (`python3 -I scripts/era_b1_probe.py --real <png> ...`; nine 256x256 crops cut from the master with macOS `sips -c`, kept in the session scratchpad, not in the repo)

Manifest: `fsa/8a16000/8a16600/8a16694u.tif`, 12,964,138 bytes received (the loc.gov item JSON listed 12,964,154; the 16-byte difference is unexplained and I did not chase it), sha256 628f3141619211e79d5dc742e966365a697dec2cb59c002e5475baa1cade86d2, 4252x3043, 8-bit gray, uncompressed, Leaf Aptus-II 12 per the TIFF header. Crop grid: centres at 20, 50, 80 percent of height and width.

| crop (row%, col%) | a64 / a128 / a256 | ordering | K4 gap (bar 4.8) |
|---|---|---|---|
| 20, 20 | 23 / 46 / 81 | ok | 6.0 |
| 20, 50 | 24 / 38 / 53 | ok | 4.0 |
| 20, 80 | 21 / 28 / 35 | ok | -5.0 |
| 50, 20 | 25 / 40 / 55 | ok | -6.0 |
| 50, 50 | 21 / 32 / 42 | ok | 4.0 |
| 50, 80 | 25 / 38 / 61 | ok | 6.0 |
| 80, 20 | 23 / 28 / 38 | ok | -35.0 |
| 80, 50 | 22 / 28 / 36 | ok | -30.0 |
| 80, 80 | 31 / 61 / 116 | ok | 11.0 |

- B16 survived (prior 0.7): ordering held on 9 of 9 crops.
- B17 FAILED (prior 0.5): the K4 gap cleared 4.8 on 3 of 9 crops (kill line: fewer than 6). Four crops read the true frame as sharper than the nearest-neighbour upscale by less than the bar or not at all, and two read it far below (-35.0, -30.0).
- What this changes: round 3's K4 pass on three 1024-px derivatives does not carry to the native scan. A hypothesis, untested: a 256 crop of a 1024-px derivative spans about four times more of the scene than a native crop and the derivative's downsample concentrates detail, so native crops of a heavily oversampled scan are smoother and the upscale test loses its margin. Another untested candidate: the lower crops are flat ground or wall (the smooth-scene failure again). I did not look at the crops.
- Surviving claim, narrowed again: ordering across the three resolutions holds on every real image tested (3 derivative photographs, 2 rendered images, 9 native crops). The upscale separation (K4) holds on synthetic textured scenes and three derivative photographs and fails on rendered UI and on most native-scan crops. A refusal gate built on this statistic is not supported. Status unchanged: INTENDED, not BOUND.
- Not tested: why K4 flips by scale, the sips crop offset semantics beyond matching output dimensions, a second master, a 99.9% cutoff, real era game art.

### Round 5: pre-registered beliefs (written before any round-5 run; no new downloads, same master and crop grid as round 4)

Question: why did the K4 gap pass on three 1024-px derivatives (round 3) and fail on 6 of 9 native crops (round 4)? Two candidate causes, each with a test that can fail. Round-4 numbers are already seen; both tests below use data not yet computed.
B18 (footprint). A 256 crop of a 1024-px derivative spans about 4x more scene than a native crop. Cut a 1024x1024 native region at the same 9 grid centres, box-downsample by 4 to 256, and run the same statistic. Prior 0.6. Kill: the K4 gap clears 4.8 on fewer than 6 of 9 (then footprint and oversampling do not explain the flip).
B19 (smoothness). Per-crop luma standard deviation (a statistic independent of the detector) predicts the K4 gap across the 9 native crops: Spearman rank correlation of std versus gap at least 0.7. Prior 0.5. Kill: under 0.7 (then flat content does not explain which crops fail).
Limits stated now: nine crops from one scan; if both are killed the flip stays unexplained, and that is a result.

### Round 5 results, 2026-10-15 (ground: merged in arcs-v9 PR 1352 at 77605497, receipt 2026-10-15--b1-round5-gap-flip-pr1352--ZH; `python3 -I scripts/era_b1_probe.py --down4 <1024 png> ...` and `--std <256 png> ...`; crops and 1024 regions cut from the same master with `sips`, scratchpad only; Spearman computed in a one-off inline script, not committed)

- B18 FAILED (prior 0.6). On 1024-px native regions box-downsampled 4x to 256, the K4 gap cleared 4.8 on 0 of 9 (gaps -6.0, -6.0, -8.0, 1.0, -10.0, -18.0, -12.0, 4.0, 4.0; ordering ok on 9 of 9). Matching the derivative's scene footprint did not recover round 3's pass; it made it worse. The footprint and oversampling explanation is dead. What round 3's derivative did differently (LoC's own downsample, JPEG generation, tone processing) is unknown and untested here.
- B19 FAILED, in the opposite direction (prior 0.5). Spearman of luma std vs K4 gap across the 9 native crops is -0.82, not at least +0.7. Higher-contrast crops have a WORSE gap: the crop std 3.08 (flat, noise-dominated, a256 116) gave +11.0, while std 36 to 40 crops gave -30.0, -5.0 and -6.0. The flat-content explanation is dead; the data suggest the reverse. With nine crops of one scene a strong rank correlation is suggestive, not established, and I give no significance figure.
- Untested hypothesis (from the round-1 attack by `chief-loki`, an agent report I did not re-run): the nearest-neighbour foil replicates edges and leaves spectral images, and the 99% cutoff counts them, so on edge-heavy, high-contrast crops the foil reads as sharp as or sharper than the true frame. That fits a negative correlation with contrast. Candidate B20, written now and not run: replacing the foil with a bilinear 4x upscale restores a gap of at least 4.8 on at least 6 of 9 native crops (prior 0.6; kill: fewer than 6). Chief-loki reported bilinear reading far lower than nearest-neighbour on its test images.
- The flip between round 3 and round 4 remains unexplained. Both candidate causes were killed. K4 as defined (nearest-neighbour foil, 99% cutoff) is not a robust test, and its result depends on the foil and on content contrast, not on the frame's true resolution alone.

### Round 6: pre-registered belief (written before the run; B20 as stated in round 5, with the committed script now covering the Spearman figure too)

B20. Replacing the nearest-neighbour foil with a 4x bilinear upscale (the repo's `_bilinear2x` applied twice to the 64 row) restores a K4 gap of at least 4.8 cycles on at least 6 of the 9 native crops. Prior 0.6. Kill: fewer than 6 of 9.
Honest scope: this tests the FOIL, not the gate. Passing would mean the nearest-neighbour test was the weak part; it would not mean a gate refusing real upscales exists, because a bilinear upscale is only one of the upscalers a real pipeline would use.

### Round 6 results, 2026-10-16 (`python3 -I scripts/era_b1_probe.py --r5 <nine 256 crops>`; same master crops as round 4, scratchpad only)

| crop | luma std | K4 gap, nearest-neighbour foil | K4 gap, bilinear foil |
|---|---|---|---|
| 20,20 | 8.17 | 6.0 | 57.0 |
| 20,50 | 25.77 | 4.0 | 17.0 |
| 20,80 | 39.73 | -5.0 | 8.0 |
| 50,20 | 39.23 | -6.0 | 4.0 |
| 50,50 | 25.91 | 4.0 | 17.0 |
| 50,80 | 19.15 | 6.0 | 26.0 |
| 80,20 | 29.57 | -35.0 | 15.0 |
| 80,50 | 36.00 | -30.0 | 16.0 |
| 80,80 | 3.08 | 11.0 | 5.0 |

- B20 survived (prior 0.6): the bilinear foil cleared 4.8 on 8 of 9 crops (nearest-neighbour: 3 of 9). The one miss is 50,20 at 4.0, 0.8 under the bar.
- The committed script now reproduces round 5's correlation: Spearman of std vs nearest-neighbour gap -0.824; against the bilinear gap it is -0.477 (n=9, one scene, no significance claimed). The nearest-neighbour foil's dependence on contrast is much weaker with the bilinear foil, which fits the edge-replication hypothesis but does not prove it.
- Reading: the K4 flip was mostly the nearest-neighbour foil, which is the hardest foil and reads as sharp because replicated edges leave spectral images that the 99% cutoff counts. Against a bilinear upscale the statistic separates true from upscaled on 8 of 9 native crops. This is a statement about two upscalers, not about every upscaler.
- Still not supported: a refusal gate. K4 passes against bilinear and fails against nearest-neighbour, so a gate would need a stated list of upscalers it covers, and an attacker or a pipeline can choose the one that passes. Not tested: bicubic, Lanczos, learned upscalers, other scans, era game art, 99.9% cutoff. Status unchanged: INTENDED.
