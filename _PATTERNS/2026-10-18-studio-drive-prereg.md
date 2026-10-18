# Studio Drive: audio features drive the print controls (2026-10-18)

Status: pre-registered BEFORE the build. Results are appended at the bottom.

## What it is (Zach, 2026-10-18)
Keep the print studio as the image. Add a "Drive" panel that moves the studio's own controls from audio, using the same analysis
Phosphor already uses (`_ARTIFACTS/phosphor-src/app.js`: 2048-point FFT at 30 frames a second, 64 log bands, loudness, spectral flux,
the calm envelope). The print is still a pure function of (recipe, time): `state = f(recipe, drive map, features, t)` (ADR-087 and the
Phosphor prereg rule). No new dependency, no network, audio never leaves the page.

## Design
- Sources: Low, Mid, High band, Loudness, Onset (flux with fast attack and slow release), Cycle ramp, Cycle sine (period set by the user).
- Targets: any numeric studio control (fidelity, slip, dropout, grain, rough, spray, drips, spatter, edge amount, wall, splat, halftone,
  view rotation, outline, horizon, size) plus a new "Text travel" control that moves the proverb around the ring.
- Matrix: six rows of (target, source, amount from -100 to 100 percent of the control's range). Effective value = base + amount x range x source, clamped.
- Smoothing is precomputed into per-frame curves (Calm = Phosphor's attack 0.07 and release 0.045 per frame; Snap = fast), so a value at time t
  is a pure function of the file and t, and scrubbing is exact.
- With "Fidelity drives the grit" on, driving fidelity moves every grit value together: the one dial gets a signal.
- A built-in demo signal (kick, hats, bass, pad) means the page works with no file. Files are decoded locally.
- Offline contract for the existing video renderer: `window.DURATION` and `window.seek(t)`.

## Pre-registered kills
| id | claim | kill if |
|---|---|---|
| D1 | Pure function | the print markup at time t differs between two calls, or after seeking elsewhere and back |
| D2 | DSP ground truth | synthetic tones at 110, 440, 1760 and 7040 Hz do not put their energy in Low, Mid, High as expected (110 Hz: Low > Mid and High; 7040 Hz: High > Low and Mid) |
| D3 | Mapping responds | with slip driven by Low at +100, the effective slip on the 110 Hz tone is not at least 3 times the value on the 7040 Hz tone |
| D4 | Calm | on the demo drum loop the print flashes (frame luminance jumps by more than 12 percent of range between consecutive rendered frames) more than 3 times in any second |
| D5 | Frame budget | median markup build for a 2x2 Tag over the demo exceeds 40 ms in headless Chromium (phone proxy; paint cost not measured) |
| D6 | Reduced motion and consent | anything plays or moves before the viewer presses Play |
| D7 | Private | any network request carries audio, or the page makes any request at all after load |
| D8 | Scrub exactness | scrubbing to t and calling seek(t) give different markup |

## Not claimed
That it feels musical. That fidelity-from-loudness is the right default (it is a default, change it). Anything about real phones. Video export is a
separate slice (frame-by-frame render with the existing renderer, then mux the audio).

## Results
Slice 1 built 2026-10-18 (Drive panel: analysis port, six-row matrix, transport, demo signal, Sweep and Tag stutter presets, Text travel control, `window.seek`/`DURATION`). Headless Playwright run (script not committed; it reads `window.TaoDrive`):

- D1 PASS: markup at t=2.5 is identical before and after seeking to 7.25 and back; the two times differ.
- D2 PASS: 110 Hz puts Low above Mid and High, 440 Hz puts Mid above the others, 7040 Hz puts High above Low and Mid.
- D3 PASS with base slip set to 0 (with the default base of 100 a 3x ratio is impossible by construction): slip 103 on 110 Hz against 0 on 7040 Hz.
- D4 PASS on this measure: 0 luminance jumps over 12 percent of range per second across 4 s of the Tag stutter map (mean luminance stayed between 65 and 82). Measured on the print element only, at 20 fps, so it does not cover a full-screen flash.
- D5 PASS on JS only: median 4.6 ms to rebuild a 2x2 Tag per seek. Paint cost of the SVG filters is not measured and is likely the real cost.
- D6 PASS: nothing playing, no AudioContext created, markup unchanged over 1.2 s at rest.
- D7 PASS: zero network requests after load.
- D8 PASS: scrubbing to 2.5 equals seek(2.5).

Not tested: a real audio file through the file picker, playback in the Artifact viewer, a real phone, long-running drift between the audio clock and the render loop.
