# Studio lyrics, animated text and captions (2026-10-18)

Status: pre-registered BEFORE the build. Results are appended at the bottom.

## What it is (Zach, 2026-10-18)
Lyrics and closed captions synced to the track, and animated text to lyrics. The print studio already puts a text on the Mobius strip and the panels; this makes that text the
current lyric line, and adds a caption layer.

## Design
- **Input**: paste lyrics or load a file. Formats read: LRC (with several timestamps per line, and enhanced word tags), SRT, WebVTT, and plain text.
- **Timing for plain text** (no timestamps): Even (equal windows across the clip), On the beat (each line starts at the strongest onset in its window, taken from the analysis the page
  already has), or Tap (press a button or the T key as each line is sung). There is no speech recognition: it would need a model or a service, and audio does not leave the page.
  Timing comes from the file, from your tap, or from the beat, and the interface says which.
- **Text source**: Proverb (as before) or Lyrics. With Lyrics the current cue is spread over the panels, and on the strip style it rides the ring.
- **Reveal**: Whole line, Word by word (words appear as they are sung), or Karaoke (the line stays, the sung word lights up). Word times come from the file when it has them,
  otherwise they are split across the cue by letter count.
- **Captions**: a burn-in caption band drawn inside the print itself (so the screen, the PNG, the live capture and the offline render all carry it), at the bottom, middle or top, wrapped to at
  most two lines. A separate soft caption track (a real closed-caption stream the player can switch off) is muxed by the offline renderer, plus SRT and WebVTT text from a Copy button.
- Everything stays a pure function of (recipe, lyrics, analysis, time). Lyrics are stored in the recipe, so they save, replay and scrub exactly.

## Pre-registered kills
| id | claim | kill if |
|---|---|---|
| L1 | Parsers are right | a fixture in LRC (with a multi-timestamp line and enhanced word tags), SRT and WebVTT does not parse to the exact expected cues, or SRT exported from the cues and parsed back is not equal |
| L2 | Pure function | the lyric state (line, word index) at time t differs between calls, after seeking away and back, or after a reload from saved settings |
| L3 | Cue boundaries | with a cue starting at T, the line shows at T plus 50 ms but not at T minus 50 ms, for every cue in the fixture |
| L4 | Auto timing | On the beat does not give strictly increasing, non-overlapping cues each starting within 100 ms of an onset peak in its window; or Even does not give equal windows |
| L5 | Reveal and karaoke | Word by word shows other than exactly the words already sung; Karaoke highlights other than exactly the current word |
| L6 | Captions fit | at 16:9, 4:3, 1:1 and 9:16 the burn-in caption text is not fully inside the frame, runs over 2 lines at the default size, or is below 11 px at 720 short side |
| L7 | Soft track and burn-in | the rendered mp4's subtitle stream text and times differ from the exported SRT by more than 20 ms, or a frame with captions on does not differ from the same frame with them off in the caption region |
| L8 | Private and honest | any network request is made, or the interface implies it transcribes audio |

## Not claimed
Automatic transcription (not built, on purpose). That the lyrics are right, or that you have the right to show them: you supply the text, and publishing someone else's lyrics is
your call and their copyright. That On the beat lands on the sung word (it lands on a strong onset, which is often not a vocal). Karaoke accuracy for lyrics without word timings (letter-count
estimate only). Right-to-left and complex scripts. Phones and the Artifact viewer.

## Results
(appended after the build)
