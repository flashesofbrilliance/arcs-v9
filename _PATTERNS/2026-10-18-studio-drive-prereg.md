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
(appended after the build)
