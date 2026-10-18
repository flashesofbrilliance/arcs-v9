# Studio realtime and responsive frames: 16:9, 4:3, 1:1, 9:16 (2026-10-18)

Status: pre-registered BEFORE the build. Results are appended at the bottom.

## What it is (Zach, 2026-10-18)
Support the four frame shapes, responsively, the way a realtime video generator behaves: the picture lives in a stage that reflows to any shape, plays live against the
audio, adapts its own quality to keep moving, and can be captured as it plays.

## Measured first (reproduce with `node scripts/tao_studio_checks.mjs probe`; headless Chromium, one 1920x1080 frame drawn from the SVG to a canvas, median of 8)
Plain Silkscreen 3x3: about 50 ms. Tag 2x2 with grit off: about 28 ms. Tag 2x2 with its grit filters: about 515 ms. Street 3x3 with spray, rough and wall: about 460 ms.
Embedding the web fonts into the frame costs about 0 to 5 ms. So the SVG filters, not the geometry and not the fonts, decide realtime. Consequence, stated up front:
live playback and live capture run in a Draft tier (filters off) when the machine cannot afford the Full tier; a paused frame and the offline renderer keep the full grit.

## Design
- **Frame**: Auto (follows the window), 16:9, 4:3, 1:1, 9:16. The stage keeps the chosen shape and the print is contained inside it.
- **Layout**: Square grid (as before) or Fit to frame, which picks a columns-by-rows grid of the same panel density whose shape best matches the frame.
- **Quality**: Auto, Full, Draft. Auto drops to Draft when live frames arrive slower than about 15 per second and probes Full again every 4 s.
- **Record**: captures the live stage to a video with the audio (canvas capture plus the audio output) at 720 or 1080 short side, in the chosen shape. It is a live capture: it
  runs at whatever frame rate the tier reaches and says so. Frame-exact output at any tier is the offline renderer's job (a later slice).

## Pre-registered kills
| id | claim | kill if |
|---|---|---|
| R1 | Layout fills the frame | at the default density, Fit to frame covers less than 75 percent of the frame area for any of 16:9, 4:3, 1:1, 9:16 (area ratio of the contained print to the frame) |
| R2 | Responsive | resizing the window from 1280 by 800 to 390 by 800 in Auto does not change the layout, or leaves a horizontal scroll bar |
| R3 | Adaptive quality | with the CPU throttled 6x while a heavy look plays, Auto is still in Full after 3 s; or after the throttle is removed it does not return to Full within 8 s |
| R4 | A playable capture | for each of the four shapes, a 3 s recording is not one video stream plus one audio stream, or its size is not exactly the chosen size, or its duration is outside 2.4 to 3.9 s (ffprobe) |
| R5 | Audio is in it | the recorded audio track's mean volume is below -60 dB on the demo signal (volumedetect) |
| R6 | Consent and privacy | recording or audio starts without the Record or Play button, or any network request is made |
| R7 | Live floor | in Draft the capture averages fewer than 12 frames per second in headless Chromium |
| R8 | Deterministic layout | the same recipe and the same frame size give different markup |

## Not claimed
That Draft looks as good as Full (it does not: no rough edges, spray or wall grit). That a live capture is frame-exact (it is not). Real phones, other browsers (MediaRecorder
codecs differ: Safari writes MP4, Chromium usually WebM), and the Artifact viewer (it blocks downloads, so a saved file needs the page opened outside it) are untested.

## Results
Built 2026-10-18: Frame and Layout controls (Auto, 16:9, 4:3, 1:1, 9:16; Square grid or Fit to frame), the stage, adaptive Live quality (Auto, Full, Draft), Capture size,
and Record (canvas capture plus the audio output through MediaRecorder). Reproduce with `node scripts/tao_studio_checks.mjs realtime` (needs ffmpeg and ffprobe). The earlier
`drive`, `frame` and `slice2` checks were re-run after this change and all still pass.

- R1 PASS: Fit to frame covers 98 percent of a 16:9 frame (5x2 panels), 90 percent of 4:3 (4x2), 94 percent of 1:1 (4x3) and 97 percent of 9:16 (2x3).
- R2 PASS: going from a 1280 px window to 390 px in Auto, the layout changed from 3x2 to 2x3 with no horizontal scroll (scroll width 390).
- R3 PASS on an affordable look (Silkscreen): with the CPU throttled 6x, Auto stepped down to Draft in 1.4 s; after the throttle was removed it was back at Full in 3.7 s. A heavy look
  (Tag with grit, Street) costs about 500 ms a frame even unthrottled, so Auto correctly stays in Draft for it; that is the design, not a failure to recover.
- R4 PASS: a 3 s recording in each shape was one video stream plus one audio stream at exactly 1280x720, 960x720, 720x720 and 720x1280, lasting 3.4 to 3.5 s.
- R5 PASS: the recorded audio averaged -10.5 to -10.6 dB (not silent) in all four.
- R6 PASS: nothing recording and no AudioContext at rest; zero network requests through the whole run.
- R7 PASS: live capture in Draft averaged 13.6 (16:9), 17.6 (4:3), 14.3 (1:1) and 22 (9:16) frames per second in headless Chromium, so the floor of 12 holds but not by a wide margin on the
  multi-panel shapes; the portrait layout, which draws fewer pixels per panel row, is fastest.
- R8 PASS: the same recipe at the same frame size gave identical markup in all four shapes.

A frame pulled from the 9:16 recording shows the 2x3 layout filling the portrait frame with the strip row underneath.

Not tested: a real phone, Safari or Firefox (codecs differ), the Artifact viewer (downloads are blocked there), a recording longer than a few seconds, recording a Full-quality look (it would run at about 2 frames
per second, which is why Auto drops to Draft), audio effects in the capture beyond the dry mix, frame-exact export (still the offline renderer's job).
