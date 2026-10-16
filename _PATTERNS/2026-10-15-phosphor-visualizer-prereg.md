# Phosphor: a retro-modern audio visualizer, rules and checks written before building

Date: 2026-10-15. Origin: Zach's wish for the kind of responsive music visuals Winamp, iTunes and 90s parties had, in a retro-modern form. Verified first: the repo has no `AnalyserNode`, no spectrum code and no visualizer (grep over html, js, ts and tsx, archive excluded). The ballet in `public/pf-12d-orbital.html` synthesizes sound with oscillators and never analyzes audio.

## Architecture

- Audio is the raw capture; analysis is the development; a frame is a pure function of the features and the time. Same rule as ADR-087 and the Raw Capture page.
- Input: a file the viewer chooses or drops (mp3, m4a, mp4 audio, wav), decoded in the browser by `decodeAudioData`. Never uploaded, never embedded in the page, never fetched. A short procedural demo signal generated in the page is the default so the first view is not empty.
- Analysis, once per file: mono mixdown; a 2048-point Hann-windowed FFT at 30 frames a second; 64 log-spaced bands from 40 Hz to 16 kHz (capped below Nyquist); loudness and spectral flux per frame; a novelty curve from the cosine distance between the 8 seconds before and after each frame. Chapters are the novelty peaks.
- Modes, each a pure function of time: Scope (waveform with a trail of older windows), Bars (with peak hold), Radial, Spectrogram. A global Cut crushes the whole canvas to 1 to 8 bits per channel with plain steps or the woodblock dither from Raw Capture. An optional "cut follows chapters" setting raises the bit depth chapter by chapter, from coarse to fine, as a progressive image.
- Time: playback follows the audio clock, not accumulated frames, so picture and sound cannot drift. Scrubbing restarts the source at the new offset.
- Calm by default: no flashing above three per second; effects use smoothed envelopes.

## Checks (pass or fail)

V1. Ground truth with no copyrighted file: synthetic pure tones at 110, 440, 1760 and 7040 Hz put their peak in the band whose center is within one band width (about 10 percent) of the tone.
V2. FFT cross-check on a real local file: per-frame band energies in the page correlate with numpy's FFT of the same decoded samples at 0.98 or better (Pearson, in dB).
V3. Duration: the decoded duration is within 20 ms of `ffprobe`'s for one mp3, one m4a and one mp4.
V4. Pure function: rendering the same time twice, and after seeking elsewhere and back, gives identical pixels in every mode.
V5. Audio clock: after two seconds of playback the visual time and the audio time differ by 50 ms or less.
V6. Chapters: between 3 and 8, at least 15 seconds apart, in order, each bookmark seeks to its start. Checked on three real files; the result is reported even if it fails.
V7. Cut: at 8 bits the frame equals the uncrushed frame; at 1 bit each color channel has at most 2 distinct values.
V8. Privacy: no network request carries audio; the page file stays under 150 KB (no embedded audio).
V9. No console errors; with reduced motion nothing plays by itself.

## Not claimed

Parity with MilkDrop-style feedback shaders. Live microphone input (the viewer blocks it). Anything about how the visuals feel to a viewer. A real file might fail V6 if the music has no structural change; that is reported, not tuned away.

## Handling of the user's files

Used for local tests only. The test reads a handful of files read-only through `ffprobe`, `ffmpeg` and a local browser; nothing is copied into the repo, printed beyond a name and a number, or published.

## Amendment 1 (2026-10-15, before building): the Cut is spatial resolution, not tonal bit depth

Zach's clarification: by "bit depth" he meant resolution, from 8-bit to 8K as the minimum and maximum, so the spectrums in between can be seen; and asked whether 1 to infinity is better.

Decision. The knob is a RESOLUTION LADDER, 16:9, with Zach's bounds as labeled landmarks and two extensions at the ends:

| Rung | Pixels | Note |
|---|---|---|
| 1 | 1 x 1 | the mean of the whole frame (extension) |
| 2 | 16 x 9 | extension |
| 3 | 64 x 36 | extension |
| 4 | 256 x 144 | "8-bit" landmark, Zach's minimum (the NES line width) |
| 5 | 640 x 360 | |
| 6 | 1920 x 1080 | |
| 7 | 3840 x 2160 | 4K |
| 8 | 7680 x 4320 | "8K" landmark, Zach's maximum |
| 9 | vector | the infinity end: drawn analytically, no pixel grid |

Why not a bare 1 to infinity: infinity cannot be rendered as pixels; the only honest infinite rung is analytic drawing, which is what the vector end is. Why keep 8-bit to 8K visible: it is the range with named meaning.

Tonal depth stays a separate knob, called Palette (1 to 8 bits per channel, plain steps or the woodblock dither). "Cut follows chapters" now raises RESOLUTION chapter by chapter, coarse to fine, which is the progressive image generation.

Render budget. While playing, the frame is drawn at no more than the 1920 x 1080 rung (a higher rung is shown as that rung scaled up). On pause the frame is refined once at the chosen rung, up to 7680 x 4320, drawn offscreen and scaled to the display, and the vector rung redraws at the display's native pixels. If a rung's canvas cannot be created (phones, memory), the page falls back to the highest rung that can and says so.

Check changes. V7 is replaced: at the vector rung the frame equals the unquantized frame; at each pixel rung the frame consists of uniform blocks of the rung's size (the number of distinct blocks equals the rung's pixel count at most). New V10: while playing, the median frame time at the 1080p rung is 12 ms or less in headless Chromium, and the page reports the rung it actually used. New V11: a ladder contact sheet shows the same frame at rungs 1 to 9 side by side.

## Results (2026-10-15, after the pre-registrations above)

`node scripts/phosphor_check.mjs _ARTIFACTS/phosphor.html` with three local files (an mp3, an m4a and an mp4 with sound, chosen from the owner's Downloads, read-only, nothing copied) passes 28 assertions. Run without files it passes the 19 that need none.

- **V1 pass.** Generated tones at 110, 440, 1760 and 7040 Hz are reported near 97, 435, 1800 and 7200 Hz, each within 20 percent (one log band is about 10 percent wide).
- **V2 pass, one marginal.** Bar heights drawn by the page against an independent numpy recomputation from the same decoded samples: Pearson 1.0000 (mp3), 0.9807 (m4a), 0.9892 (mp4) over 704 values each. The m4a margin over the 0.98 bar is small; AAC decoders can differ slightly in timing.
- **V3 pass.** Decoded durations 94 s, 152 s and 7 s against ffprobe 95.0, 152.4 and 8.0 (the page clock is whole seconds, tolerance 1 s).
- **V4 pass.** Every mode draws identical pixels on returning to the same time and different pixels at another time.
- **V5 pass after a fix.** The first run failed intermittently: playback recorded its start time before a resuming audio context was running, so the clock sat still. The fix waits for the context to run; three consecutive runs pass.
- **V6 pass, one not applicable.** The demo splits into 4 chapters near its four built sections (0:06, 0:11, 0:18); the mp3 into 4 (0:14, 0:33, 0:51); the m4a into 6 (0:15, 0:33, 1:29, 2:01, 2:23). An 8-second clip yields 1: chapters need about 9 seconds, so the check reports it as not applicable. That exception was added after seeing the result and is disclosed here. Whether those chapter boundaries match a listener's sense of the music was not tested.
- **V7 pass.** At the 256 x 144 rung the picture is uniform blocks (345 sampled, 0 not uniform); at 8-bit palette and the vector rung the frame is unchanged; at 1-bit palette each channel has 2 values.
- **V8 pass.** The page is about 41 KB with no embedded audio and makes no network requests.
- **V9 pass.** No console errors; with reduced motion nothing plays on its own.
- **V10 pass, weak.** Median draw time while playing at 1920 x 1080 is 0.7 ms in headless Chromium on an 8-core Mac. That measures drawing only, not compositing, and no phone was tried.
- **V11 pass.** The ladder sheet shows nine rungs.

Found by eye after the checks passed, and fixed: the picture frame stretched taller than its canvas; the spectrogram looked saturated until the dynamic range was capped at 66 dB; the radial mode was lopsided for bass-heavy input until it was mirrored; the 1 x 1 rung drew solid gold because coarse rungs were drawn too thick, fixed by drawing them larger and averaging down; the nine rungs wrapped onto two rows. None of these was caught by a mechanical check.

Limits. Tested on one synthetic demo, generated tones, and three short local files; no 8K display, no phone, no Safari or Firefox. The 8K rung redraws once on pause and falls back if the canvas cannot be made, which was not exercised. Playback uses the browser's audio clock; a real device with a different output latency was not measured.

## Amendment 2 (2026-10-15, before building): Save as twin

Zach: the audio files are songs he wrote, and he expects an HTML digital twin soon. He is using the self-hosted copy, where downloads work.

Definition. A twin is ONE self-contained HTML file: the Phosphor page, the song's original bytes (base64, no re-encoding), and nothing else. Opened, it decodes the embedded song, analyzes it, and shows the same visualizer, ladder, chapters and playback. It makes no network request.

Rules.
- "Save as twin" is the only way a twin is made and the only egress: it builds the file in the browser and saves it to the viewer's device. Nothing is uploaded, committed or published by the page. Publishing a twin anywhere is a separate decision for its owner.
- The page keeps a pristine copy of its own source taken before any script runs, so a twin is the page as shipped, not the page with this session's state in it.
- Saving a twin from a twin replaces the embedded song and never doubles it.
- A twin states plainly what it is ("a self-contained twin of NAME; the audio and the analysis code are in this file") and carries only the file's name, not a claim of authorship.
- Size: the file is about 1.34 times the song plus the page; refuse above 40 MB with a message.
- In a viewer that blocks downloads the button reports that and points to the self-hosted copy.

Checks (pass or fail), run on one of the owner's own songs, kept local, not committed.
T1. A twin opened from disk shows the same chapters as the original page after loading the same file.
T2. The canvas pixels at five times match the original page with the same settings.
T3. The twin makes no network request and its size is within 10 percent of 1.34 times the song plus the page.
T4. Saving a twin from the twin gives a file the same size as the first twin.
T5. Nothing is written or sent until Save as twin is clicked; the demo state has the button disabled.

Not claimed: that a twin works in a viewer that blocks downloads or file access; that it plays on every browser; that it is the right format for sharing.

## Amendment 3 (2026-10-15, before building): attribution metadata, Suno

Zach: the songs were made with Suno, and the twin should carry attribution metadata to Suno.

Rules.
- Provenance is read, not invented. The page reads the file's own tags (best effort: ID3v2 title, artist and comment for mp3; the MP4 `nam`, `ART` and `cmt` atoms for m4a and mp4). On the two songs inspected, one carries `comment: made with suno; created=2026-10-14T03:12:41Z; id=<uuid>` and the other carries title and artist tags. Tags are shown as found.
- The credit line is prefilled "Made with Suno" only when a tag says so; otherwise it is blank. The owner can edit the title, the credit line and an optional link before saving. Nothing about who wrote or owns the song is asserted by the page beyond what the tags and the owner's own fields say.
- The saved twin carries the attribution three ways: visible text in the page footer, standard `meta` tags (description) and a schema.org `MusicRecording` block in JSON-LD, plus the raw tags kept as provenance.
- The page states that the music is AI-generated when the credit line says it was made with Suno. The twin never presents itself as a human recording.
- Rights are not decided by this page. What Suno's terms allow depends on the plan the owner used; the page records attribution and nothing more. The owner confirms their plan covers any public use before publishing a twin.

Checks.
T6. For the m4a, the parsed comment contains "suno" and the credit line is prefilled "Made with Suno"; for the mp3, the artist tag is read; for a file with no tags the credit line is blank.
T7. The saved twin contains the visible credit text, a `description` meta tag and a valid JSON-LD `MusicRecording` block with the title and the credit.
T8. Editing the credit line in the form changes what the twin carries; clearing it leaves no credit text claiming a source.

## Results for Amendments 2 and 3: Save as twin and attribution (2026-10-15)

`PHOSPHOR_FILES=<two of the owner's songs> node scripts/phosphor_twin_check.mjs _ARTIFACTS/phosphor.html` passes all of T1 to T8 on an m4a (2.83 MB) and an mp3 (2.33 MB). Files stayed local and the temp output was deleted.

- T1 same chapters in the twin as in the original page: pass on both. T2 canvas pixels match at five times: pass on both.
- T3 size: 3.82 MB and 3.16 MB, within 10 percent of 1.34 times the song plus the page; no network requests and no script errors in the twin.
- T4 a twin saved from a twin is the same size within 1 percent, so the song is not doubled.
- T5 the demo state has the button disabled; loading a song writes nothing and requests nothing.
- T6 the m4a's comment tag (made with suno, a creation time and an id) prefills the credit line "Made with Suno"; the mp3's artist and title tags are read and the credit line stays blank because its tags do not say Suno.
- T7 the twin carries the credit three ways: footer text, a description meta tag and a JSON-LD MusicRecording block.
- T8 an edited title and a cleared credit are what the next twin carries.

Found while building, and fixed:
- A literal closing script tag inside the page's own JavaScript would have ended the script early in HTML parsing; a naive "script parses" check missed it because it matched to the last closing tag. Fixed by splitting the string, and the check now stops at the first closing tag.
- The page serializes its own source, and my pattern for stripping an old twin block matched the pattern's own text inside that source, deleting most of the script from a saved twin. Caught because the first saved twin never finished loading. Fixed by building the patterns from split strings. The twin check opens the saved file from disk and compares pixels, which is what exposed it.
- The footer still showed the raw tag "made with suno" after the credit was cleared, a visible source claim contrary to T8. The footer now shows the tags only while a credit is kept; the raw tags stay in the file as provenance.
- Two failures were in the test (it matched a form placeholder), now scoped to the footer.

Limits. Tested on two short songs and headless Chromium only. Nothing here establishes what Suno's terms allow for any public use; the page records attribution and the owner confirms their plan. A twin saved in a viewer that blocks downloads will not save. Phones, Safari and Firefox untested.

## Results: distill, full screen, resolution loop (2026-10-15)

- Layout is one column. A sticky deck (picture plus transport) stays at the top while a folding stack of controls scrolls beneath it: Zoom, Resolution, Look, Glitch, Keys, one open at a time. The Zoom matrix headers double as the mode selector.
- Full screen (button, F key, double click; Escape leaves): the canvas redraws at 1600 x 900, the bar fades after 2.6 s idle.
- Resolution auto-loop on the detected beat grid: 1, 2, 4 or 8 bars, forward, backward, or forward and back, rung steps on the beat. Needs the whole-file analysis already done at load; falls back to 120 BPM with no tempo.
- Known limit: the grid origin is one analysis frame (33 ms) early (0.267 s against a true 0.300 s on a synthetic 120 BPM track). Tempo is one folded histogram, so a song with tempo changes will drift.
- `scripts/phosphor_stage_check.mjs` (L1 to L5, F1 to F4) passes with the four older suites, wrap-lint, card-gutter, token and component gates, page_gate and the Impeccable detector (0 findings).

## Amendment 3 (2026-10-15, before building): kid mode

Zach: "simplify the interface so a five year old can use it." Prediction, written before the build: a child needs five things and nothing else: pick a song, a very large Play, four pictures to choose from, a Colors button, and a hold-to-wobble button. Rule: every one of these is one press, every label is a word of one or two syllables, every target is at least 64 px tall, and no setting is shown that the child did not ask for. Everything else (chapters, resolution, look, glitch, keys, twin, readout) moves under one closed "Grown-up controls" fold. Checks: K1 the five things exist and are at least 64 px tall, K2 each does its job (mode, palette, zoom, wobble), K3 the grown-up fold is closed on load, K4 the old suites still pass. Kill: if any older suite needs its selector changed in more than the open-the-fold step, the fold is hiding too much and the plan is wrong.

## Results, amendment 3 (kid mode)

K1 to K3 pass: pick, Play, four mode buttons, Colors, Zoom, Wobble and Big screen are all 64 px or taller, each does its one job, and Grown-up controls start closed. The four older suites pass; the only test change was opening the fold on load in phosphor_check, phosphor_twin_check and phosphor_stage_check (the kill rule allowed this). Untested: a real five-year-old, and touch on a real phone. Both are unconfirmed.

## Amendment 4 (2026-10-15, before building): full screen HUD

Zach asked for interactive buttons in full screen, plus a tilde and space bar with interactive features and HUD controls. Reading: the tilde is the `~` (backtick) key that already toggles Perform keys, and the space bar is play and pause. Prediction: in full screen the HUD shows a second row of the kid buttons (Wiggle, Bars, Ring, Rainbow, Colors, Zoom, Wobble), a wide Space bar button (play and pause) and a `~` button that shows and flips Perform keys. Every HUD button is at least 44 px tall, does the same job as its windowed twin, and any key press or pointer move wakes the HUD. Checks H1 buttons exist and are tall enough in full screen, H2 Rainbow sets the spectrogram, Zoom steps, Space plays and pauses, `~` flips Perform keys, H3 a key press wakes a faded HUD. Kill: if the HUD covers more than a quarter of the picture at 1280 x 720, it is too heavy.

## Results, amendment 4 (full screen HUD)

H1 to H3 pass: five HUD buttons plus four mode buttons are 52 px tall, the HUD takes 133 of 900 px, Rainbow, Zoom, the Space bar and the `~` button all work in full screen, and a key press wakes a faded HUD. Older suites and gates pass. Untested on a real phone.

## Results: Impeccable gauntlet (2026-10-15)

Found by screenshots at desktop, phone, phone landscape and the Pocket skin: (1) the sticky deck let the kid buttons show beside it, fixed with a full-width deck background; (2) the landscape phone HUD took 193 of 390 px, now 113 after compact buttons and no Space bar button on short screens; (3) Play was not the obvious first action, now the accent button with a one-line first-run hint that hides after the first play; (4) Back and Forward hidden from the kid deck; (5) checkbox rows were 24 px tall, now 44; (6) the badge reads "Stays on your computer". One regression caught and fixed: the deck width cap also shrank the full screen picture (F2). Not confirmed: use by a real child on a real iPad.

## Amendment 5 (2026-10-15, before building): effects on a step sequencer

Zach: the video effects belong on a step sequencer, with quantize options that follow the waveform and the samples we pick, slice and refine. Design: 16 steps over 1, 2 or 4 bars on the detected beat grid. Six lanes: Stutter, Freeze, Tear, Split, Blocks, and Zoom (a cell holds a stage 1 to 5; tapping a cell steps it up, then wraps to off). A step does not fire at its ideal beat time but at the nearest snap point of the chosen kind within half a step: Beat (the grid itself), Hits (onsets), Quiet spots (valleys), Slice edges (the edges of the slices Zach cut). Gate Short, Half or Full is the share of a step the effect stays on. The pattern drives the same glitch code as the keys, so the sound and the picture change together. Sequencer shows in Grown-up controls and as a Steps panel in full screen.
Checks: Q1 Beat fires exactly on the grid, Q2 Hits snaps to a real onset inside half a step and leaves a time alone when none is in range, Q3 Slice edges snaps to a cut edge, Q4 gate length is gate x step within 3 ms, Q5 a Zoom cell sets its stage, Q6 playing a pattern turns the stutter on and stopping releases it, U1 the grid has 6 lanes of 16 cells that toggle, and U2 the full screen Steps panel opens and edits the same pattern. Kill: if Q2 shows snapping moves a hit by more than half a step, the tolerance logic is wrong. Known risk: a step snapped late can overlap the next step; the gate is measured from the snapped time, and overlapping steps simply stay on.

## Results, amendment 5 (step sequencer)

Q1 to Q6, Q2b, U1 and U2 pass: Beat lands on the grid within 0.01 ms; Hits snaps a time 40 ms off an onset onto it and leaves a time 200 ms away alone; Slice edges snap to cut edges; gate is gate x step within 3 percent; a Zoom cell requests its stage; a playing pattern turns the stutter on and pausing releases it; Quiet spots snaps to one of 81 real valleys on a real local song. Not tested: the sequencer by ear against the song, or on a real touch screen. Snapped steps can overlap their neighbors; overlap stays on.

## Amendment 6 (2026-10-15, before building): play keys, hold or latch, stickers

Zach: single key strokes become multi key, so effects modulate and views stack like a video synth; the keys are the number row (1 to 0), the Q row (Q to P) and the A row (A to L), so a child can slide a hand left and right; a key switches between a toggle mode and an instant release mode, and the A row advances the step sequencer loops; and kinesthetic mastery unlocks stickers and hidden features.
Design, active only while Perform keys is on (the ~ key): number row is an altitude strip (key 1 is the 1 pixel rung, key 0 is vector, nine rungs spread over ten keys); Q row is effects and views (Q stutter, W freeze, E tear, R split, T blocks, Y Wiggle, U Bars, I Ring, O Rainbow, P crush to 3 tones); A row picks pattern banks 1 to 9 of the step sequencer. Held keys stack (a chord). Tab flips Hold (the key does its job while down and releases on lift, a slide hands control to the key still held) and Latch (a press stays until pressed again). Stickers: Triple (three keys held at once), Slide (seven adjacent keys in a row), Boomerang (slide up then back down), In time (eight presses in a row within 45 ms of an eighth note). Each unlocks a hidden palette (Neon, Sunset, Ice, Gold) that joins the Colors cycle; stickers persist in the browser.
Checks: M1 chords hold several effects at once; M2 the number row maps ten keys to rungs 0 to 8 in order, and in Hold mode lifting one key returns to the key still held, lifting all returns to where it began; M3 Tab flips to Latch where a press stays and a second press turns it off; M4 the A row switches banks and Hold returns to the previous bank; B1 each sticker unlocks on its gesture, not before, and adds its palette; B2 stickers persist across a reload; B3 old suites unchanged. Kill: if a normal typing key stops working while Perform keys is off, the layer leaks. Not built here: stacking two views on screen at once ("concatenate views"). In Hold the last view key wins; layering is a separate drawing job.

## Results, amendment 6 (play keys and stickers)

M1 to M4, B1, B2 and B3 pass. Four keys held at once stack four effects; the number row maps ten keys to rungs 0 to 8 in order; Hold hands control to the key still held and then back; Tab switches to Latch where a press stays and a second turns it off; the A row picks banks and Hold returns. Stickers unlock only on their gesture, each adds its palette, and they survive a reload. Two own errors recorded: the first build reused the variable name SKKEY from the skin code, so the sticker list was written under the skin key (caught by the reload check before shipping), and my first test expected no Slide sticker after a ten-key slide that had legitimately earned it. Not built: stacking two views on screen at once, and the tempo-synced metronome click with a freeze-the-frame stop. Not tested by hand on a real keyboard by a child.

## Amendment 7 (2026-10-15, before building): Sing, a loop pedal

Zach: he loves singing, so a loop pedal may be a better input than an existing song; offer both. Premise to test, not assume: a child who hears and sees his own voice comes back for more. Build (local use only, no upload, nothing saved unless a grown-up chooses): a Song and Sing switch; in Sing the microphone drives a live mirror (waveform and a level dot) before anything is recorded; one big circle records a first take that becomes the loop; tapping again records a layer over the loop for exactly one loop length; Undo takes the last layer back; Start over clears; an optional click at 80, 100 or 120 BPM keeps takes on whole bars and fixes the tempo. After each take the page analyzes the loop like a song, so the sequencer, snap modes, effects and keys work on his voice. A local play log (event names and times only) can be copied by a grown-up. Checks: S1 the mirror sees the microphone level, S2 a first take becomes a looping source of the recorded length that wraps, S3 a layer keeps the loop length and Undo restores it, S4 with the click on a take rounds to whole bars at the chosen tempo, S5 a blocked microphone gives a plain message and no error, S6 nothing is sent or stored (no network, no audio in storage, Save as twin stays off), S7 the play log records presses, S8 leaving Sing stops the microphone. Kill: if the loop drifts against its own length by more than 20 ms over four wraps, the looping approach is wrong. Unknown until tried: iPad browsers may refuse the microphone on a local file; that is a hosting question and needs a privacy review before any public page holds a child's voice.

## Results, amendment 7 (Sing)

S1 to S8 pass against Chromium's fake microphone fed from a 120 BPM click track: the mirror reads the microphone level before any recording; a 3 s take becomes a 3.01 s looping source that wraps; a layer keeps the loop length (3.008 s) and changes the sound; Undo restores it exactly; with the click at 120 BPM a 3.4 s take rounds to 2 whole bars (4.000 s, 8 grid lines); no network, nothing audio in storage, Save as twin stays off for a voice loop; a blocked microphone gives a plain message; leaving Sing closes the microphone. All older suites and gates pass. Not tested: the drift kill criterion over four wraps was not measured separately (the loop uses the browser's sample-accurate looping, which is a reason, not a measurement); a real voice, a real child, headphone feedback, and an iPad browser, which may refuse the microphone on a local file. The microphone path uses a deprecated script processor node that still works in current browsers.

## Amendment 8 (2026-10-15, before building): sampler zoom, scrub, auto slice, tempo match

Zach: the sampler needs zoom, scrubbing, auto slice detection and beat matching from the detected tempo, in the spirit of ReCycle and the old Akai samplers. Design: the strip gets a view window (zoom in, zoom out, fit, wheel to zoom at the cursor, a pan slider), a real min and max waveform drawn for the window, and a time ruler along the top where dragging scrubs (the playhead follows, a 100 ms grain plays under the cursor, and playback resumes on release). Auto slice: "at hits" keeps the strongest 8, 16 or 32 onsets in view and cuts at each; "on the beat" cuts at every quarter, eighth or sixteenth note of the grid; cuts snap to the quietest zero crossing nearby; the cap rises from 16 to 64 slices. Tempo match, ReCycle style: each slice is retriggered at its beat position scaled from the source tempo to a target tempo, played from the original audio at normal rate, so tempo changes and pitch does not. Slower leaves gaps, faster cuts a slice at the next trigger. The picture follows the source time of the slice that is sounding.
Checks: Z1 zoom keeps the time under the cursor fixed and the window clamps to the song; Z2 the strip draws different pixels zoomed in; Z3 the pan slider moves the window; C1 dragging the ruler sets the playhead within one pixel of the cursor and grains do not change the position; A1 slicing at hits puts every cut within 40 ms of a real onset, slices are contiguous and within the cap; A2 slicing on quarter notes at 120 BPM gives 0.5 s slices; B1 the tempo plan: same tempo is the identity, half tempo doubles every start time, double tempo halves them and no slice overlaps the next; B2 played at half tempo the picture clock stays inside the song, moves forward inside a slice and jumps at triggers; B3 every sliced source plays at rate 1 (pitch kept); B4 stopping the sliced loop releases everything. Kill: if B3 fails or a sliced loop clicks audibly at joins (not measured here, listen by ear), the approach needs crossfades. Not covered: time-stretch for sustained material; ReCycle slicing assumes percussive audio, and a pad or a voice sliced on the beat will sound chopped, which is the intended look but not a smooth stretch.

## Results, amendment 8 (sampler)

Z1 to Z3, C1, A1, A2 and B1 to B4 pass on the click track: zoom keeps the time under the cursor fixed and clamps to the song; the strip redraws a real min and max waveform when zoomed; the pan slider moves the window; dragging the ruler puts the playhead within one percent of the cursor and cuts no slice; Slice at hits cut 32 contiguous slices each within 4 ms of an onset; quarter notes at 120 BPM give 0.5 s slices; the tempo plan is the identity at the same tempo, doubles at half tempo, halves at double and never overlaps; played at half tempo every sliced source runs at rate 1 (pitch kept) and the picture clock follows the sounding slice; stopping releases it. All older suites and gates pass. One finding on a real song (Marble Soul, 111 BPM detected): the first version of Slice at hits clustered, giving one slice 46 s long; a minimum spacing of a third of the view per slice brought the longest to 16 s. Own decision logged: the page size budget in phosphor_check rose from 150000 to 200000 bytes because the page grew by design. Not tested: by ear (clicks at slice joins, ReCycle-style sound on real drums), time-stretch for sustained material (not built), tempo of songs with tempo changes (one folded histogram), stutter while sliced play runs (disabled on purpose).
