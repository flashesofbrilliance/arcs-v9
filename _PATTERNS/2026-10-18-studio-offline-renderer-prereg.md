# Studio offline renderer: frame-exact video in four shapes with the audio muxed in (2026-10-18)

Status: pre-registered BEFORE the build. Results are appended at the bottom.

## Why
The live capture is honest but modest: it runs at whatever rate the screen can reach and, for the grit looks, only in the Draft tier (the filters cost about 500 ms a frame).
The studio is a pure function of (recipe, analysis, time), so a video can instead be built one exact frame at a time, as slowly as the filters need, at any shape, and then
joined to the original audio. That is the full-quality path; the live capture is the draft path.

## Design
- The studio page gets a stage-only mode (`?stage=1`): every control is hidden and the stage fills the viewport exactly, so the viewport size is the video size.
- A renderer script drives that page headless: it loads the recipe (a preset, or the text from Copy recipe) and the audio file, then for frame i sets the time to i divided by the
  frame rate, waits for the paint, captures the stage, and streams the frames to ffmpeg. A second ffmpeg pass joins the audio. Quality is forced to Full.
- Shapes: 16:9, 4:3, 1:1, 9:16 at 720 or 1080 on the short side, using the same sizes as the live capture. The layout fits the frame.
- Local only: audio is read from a path you give, nothing is uploaded, no network. It refuses to overwrite an existing output without a flag.
- Not included: the live audio effects. The mux uses the original file, so the key presses show in the picture (they are in the log) but not in the sound.

## Pre-registered kills
| id | claim | kill if |
|---|---|---|
| O1 | Frame exact | the same frame index rendered twice, or after rendering other frames in between, gives different pixels |
| O2 | Right files | a render in any of the four shapes does not have exactly one video stream and one audio stream, the exact chosen size, and a video duration within one frame of the requested length |
| O3 | Audio is the track | the video's audio duration differs from the video duration by more than 50 ms, or its mean volume is more than 1 dB from the source file over the same span |
| O4 | Full quality | a frame from the renderer differs from the studio's own paused Full-quality capture at the same time and size by more than 1 percent mean absolute pixel difference, or a Draft capture matches it as closely on a grit look |
| O5 | Starts together | the audio and video streams start more than 20 ms apart |
| O6 | Private and safe | the render makes any network request, writes outside the output path and its temporary folder, or overwrites an existing file without the force flag |
| O7 | Fills the shape | at any of the four shapes, the stage leaves a margin: the outermost pixel rows and columns are not the print's own colours (the layout does not reach the frame edge) on more than 5 percent of the border |

## Not claimed
Speed (it is reported, not killed: a full-grit frame can take most of a second). Safari or Firefox rendering. That ffmpeg builds without H.264 behave the same (the script uses
whatever ffmpeg encoder is available and says which). Lyrics and captions, which are the next slice.

## Results
Built 2026-10-18: stage-only mode in the studio (`?stage=1`), `scripts/tao_studio_video.mjs`, and an elastic layout (see O7). Reproduce with
`node scripts/tao_studio_checks.mjs offline` (needs ffmpeg, ffprobe, python3 with PIL; about 35 s). The earlier `realtime` checks were re-run after the layout change and still pass,
and every shape now fills its frame exactly (Fit to frame fill 100 percent in all four).

- O1 PASS: the same frame (1.0 s, Tag, full grit) captured twice with two other times rendered in between was byte-identical.
- O2 PASS: for each of 16:9, 4:3, 1:1 and 9:16 at 720 short side the file has one video stream and one audio stream at exactly 1280x720, 960x720, 720x720 and 720x1280, 2.000 s long.
- O3 PASS: audio and video durations differ by 0 ms; the output audio averages -10.7 dB against -10.6 dB for the source over the same span.
- O4 PASS: a frame from the renderer differs from the studio's own paused Full-quality capture by 0.0000 percent mean absolute pixel difference (identical), while a Draft capture of the same
  moment differs by 1.7 percent, so the renderer really is at Full.
- O5 PASS: audio and video start together (0 ms apart) in all four.
- O6 PASS: zero network requests blocked, a second run to the same file without the force flag exits with code 2 and leaves it alone, and no temp folder was left behind.
- O7 FAIL as registered, PASS on the direct test. The registered measure (border pixels in the stage colour, at most 5 percent) read 8.3 percent at 16:9 and 8.8 percent at 9:16 for Brainwash.
  That measure also counts the legitimate gaps between panels, which are stage-coloured by design, so it cannot reach 5 percent while the panels have gaps. The real defect it was
  after, letterbox bars, was present in the first run (the contained print left bars at 9:16 and 4:3) and is now fixed: the gaps between panels stretch independently, horizontally and
  vertically, so the print meets the frame edges exactly. The direct test (whole border rows or columns in the stage colour) finds 0. The trade-off: in some shapes the gaps are uneven
  (for example 6 units across and 37 down at 4:3). The registered result stays recorded as a fail.

Speed, reported not killed: 0.10 to 0.25 s per full-grit frame at 720 short side on this machine (16:9 slowest), so a 30 s clip at 30 fps is roughly 1.5 to 4 minutes.

Not tested: 1080 short side, a real song and long clips, Safari or Firefox rendering, encoders other than libx264, a machine without ffmpeg, the live key effects in the sound (not included by design).
