# RFP engine videos: crit and gauntlet record (2026-10-31)

Five videos for the Dioptra work sample. The MP4s, thumbnails and the upload sheet live in
`~/Movies/rfp-engine-videos/FINAL-2026-10-30/` and are not committed. The build sources are in
`tools/readme-video/` on PR 1894. The breaks and their fixes are in `kintsugi.json` next to this file.

## Gates run on every video

- `scripts/readme_video_check.py` (the README-to-video rules, R1 to R8)
- the `brand-line-producer` agent (voice, earned fidelity, kit level, cross-surface consistency)
- frame sampling: one frame every 3 s, tiled 2x2 into contact sheets, read by eye

## Results

| # | File | Length | First re-check | Final re-check | What changed |
|---|---|---|---|---|---|
| 1 | 1-walkthrough-1m05.mp4 | 1:07 | PASS | PASS | none |
| 2 | 2-a3-safe-but-strict-0m51.mp4 | 0:51 | PASS | PASS | none |
| 3 | 3-making-of-2m32.mp4 | 2:23 | BLOCK: no credits on end card | PASS | credits moved to the description (Zach's ruling) |
| 4 | 4-bench-2m12.mp4 | 2:44 | BLOCK: card 04 stale, card 06 safe outcomes in red | PASS | card 04 re-voiced to cite d67294d; outcomes gold with CAUGHT stamps |
| 5 | 5-walkthrough-long-2m52.mp4 | 2:52 | BLOCK: card 01 "real-world based" | PASS | card 01 says fictional; README gate 0 FAIL |

## Facts the cards rest on

- Real-model run d67294d: 11 correct, 12 withheld, 1 wrong out of 24. The target was 0 wrong, set in advance, and was missed.
- Checked by hand at 046e1c0: 14 of 24 correct (3 withheld answers were right; the figure check was too strict).
- Deterministic cases: 5 of 5. Injected faults: 8 of 8 caught.

## Not covered by any gate

- **Audio.** No gate listens. Bench card 04 and the making-of "What broke" card were re-voiced and have not been heard.
- **Typography.** The builds use hand-set pixel sizes, not the DESIGN.md scale. The brand gate does not check type.

## Optional tweaks the final check flagged

- Bench card 04 gives 11 / 12 / 1 without saying the zero-wrong target was missed. The walkthrough does say it.
- The arrow on making-of card 02 can read as going straight to the reviewer instead of as a sequence.
