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
