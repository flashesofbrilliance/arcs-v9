# Studio realtime and responsive frames: 16:9, 4:3, 1:1, 9:16 (2026-10-18)

Status: pre-registered BEFORE the build. Results are appended at the bottom.

## What it is (Zach, 2026-10-18)
Support the four frame shapes, responsively, the way a realtime video generator behaves: the picture lives in a stage that reflows to any shape, plays live against the
audio, adapts its own quality to keep moving, and can be captured as it plays.

## Measured first (headless Chromium, one 1920x1080 frame drawn from the SVG to a canvas, median of 8)
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
(appended after the build)
