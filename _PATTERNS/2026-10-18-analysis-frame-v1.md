# AnalysisFrame v1: one file shared by Phosphor and the Tao print studio (2026-10-18)

Status: contract and kills pre-registered BEFORE the build. Results are appended at the bottom.

## Why
Phosphor analyses a song (2048-point FFT at 30 fps, 64 log bands, loudness, spectral flux, tempo, chapters, a DNA/RNA genome of codons per beat).
The studio's Drive panel ported that analysis and maps it onto print controls. Two copies of the same analysis drift. A third party (a video renderer,
a lyric layer) would need a third copy. The weld is one small data shape that either page can produce and either can consume, with no new
dependency and no audio in it. Phosphor stays the performer; the studio prints from the file.

## Shape (JSON)
```
{ "v": 1, "kind": "tao.analysis", "src": "phosphor" | "studio",
  "fps": 30, "nfft": 2048, "nb": 64, "nf": <frames>, "dur": <seconds>, "sr": <Hz>, "name": "<label>",
  "fmin": 40, "fmax": <Hz>,
  "bands": "<base64 of nf*nb uint8, band-major per frame, value/255 in 0..1>",
  "lev":   "<base64 of nf uint8, loudness 0..1>",
  "flux":  "<base64 of nf uint8, spectral flux divided by fluxMax>", "fluxMax": <number>,
  "bpm": <number or null>, "grid0": <seconds or null>,
  "chapters": [<frame indexes, ascending>], "chapterLabels": ["..."],
  "dna": [[fid,dep,dis] codon indexes 0..3 per beat, or null], "dnaP": <seconds per beat>, "dnaBase": <seconds> }
```
Quantised to uint8 on purpose: both producers quantise the same way, so a value read from a file equals the value used by the producer's own visuals.
No audio samples are ever in the file. A 4-minute song is about 600 KB.

## What each side does
- Phosphor: one new always-available getter `window.PhosphorFrame()` that returns the object above from state it already holds. No new UI, no new analysis.
- Studio: `loadFrame(obj)` replaces the analysis step; its own analysis now ends in the same quantised frame; new sources Beat pulse and Genome fidelity,
  depth and distortion read bpm, grid0 and dna; a silent clock lets a frame play with no audio loaded.

## Pre-registered kills
| id | claim | kill if |
|---|---|---|
| F1 | Round trip | studio analysis, exported and re-imported, gives different source values at any of 40 sampled times, or different print markup at any of 5 times |
| F2 | Parity | on the same decoded fixture file, Phosphor's frame and the studio's frame differ by more than 1 level of 255 in any band, loudness or flux value, or have different nf |
| F3 | Valid contract | a frame fails: v is 1, byte lengths match nf and nb, chapters ascend, codons are 0..3 |
| F4 | Small | a 4-minute frame is over 700 KB as JSON |
| F5 | No audio, no network | the JSON contains PCM-length data, or loading a frame makes any request |
| F6 | Phosphor stays whole | phosphor.html grows past 320,000 bytes, `phosphor_build.py --check` fails, or the static review fails after the change |
| F7 | Source of truth | the studio can still produce a different value for a given frame than the one in the file (no hidden second analysis path once a frame is loaded) |

## Not claimed
Anything about how it feels. That the uint8 quantisation is audible or visible. Genome codons carry meaning for the print beyond what the matrix rows make of them.

## Results
Built 2026-10-18. Phosphor side: `window.PhosphorFrame()` (+22 lines in `_ARTIFACTS/phosphor-src/app.js`, rebuilt `phosphor.html`, branch `claude/phosphor-analysis-frame`).
Studio side: analysis now ends in the same uint8 frame; `Copy analysis`, `Load analysis`, `TaoDrive.frame()` and `TaoDrive.loadFrame()`; sources Beat pulse and Genome
fidelity, depth and distortion; a silent clock plays a frame with no audio. Run headless (Playwright, script not committed) against a deterministic 10 s fixture WAV
(kick, hats, bass, pad at 120 BPM, 16-bit mono 22,050 Hz):

- F1 PASS: 40 sampled source values and 5 print markups are identical after export and re-import.
- F2 PASS, and exactly: on the same decoded fixture, Phosphor and the studio produced the same frame count (299) and 0 differing values out of 19,136 band values, 299 loudness values and 299 flux values (maximum difference 0 of 255). The ported analysis is bit-for-bit Phosphor's.
- F3 PASS: the studio's frame validates (version, byte lengths, ascending chapters).
- F4 PASS: a 16 s frame is 42 KB; projected 4 minutes is about 621 KB, under the 700 KB limit.
- F5 PASS: zero requests after load, and no field the size of audio samples.
- F6 PASS: `phosphor.html` is 287,438 bytes (cap 320,000), `phosphor_build.py --check` matches, `phosphor_static_review.py` reports 0 findings.
- F7 PASS: after loading a frame with loudness doctored to 255, every sampled loudness source value followed the file (above 0.9).
- Bonus: a Phosphor frame loads into the studio and drives it. On the fixture Phosphor reported 120 BPM, 2 chapters and 20 genome beats, and the Beat pulse and Genome fidelity sources read them.

Not tested: a real song through both pages, mp4 audio, a frame larger than 4 minutes, Phosphor's full check suite beyond build and static review, a real phone, the Artifact viewer.
