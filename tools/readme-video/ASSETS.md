# Assets not committed

The audio takes and rendered MP4s for the walkthrough stay out of git (they are large, and the takes are paid ElevenLabs
generations in Zach's voice clone). They live in a Claude scratchpad on Zach's Mac, which macOS can clear:

`V=/private/tmp/claude-501/-Users-zharris-arcs-v9--claude-worktrees-ai-product-ownership-roadmap-78910c/126fc091-1930-4fec-bbae-21b65ae1b1a7/scratchpad/vid`

Copy `$V/voice/` somewhere durable before it goes. Regenerating the takes spends credits.

## The walkthrough this folder builds (8 cards)

| Path under `$V` | Bytes | What |
|---|---|---|
| voice/01.mp3 | 293440 | take, card 1 (17.20 s) |
| voice/02.mp3 | 339415 | take, card 2 (20.08 s) |
| voice/03.mp3 | 292186 | take, card 3 (17.12 s) |
| voice/04.mp3 | 395840 | take, card 4 (23.60 s) |
| voice/05.mp3 | 321443 | take, card 5 (18.96 s) |
| voice/06.mp3 | 339415 | take, card 6 (20.08 s) |
| voice/07.mp3 | 326876 | take, card 7 (19.28 s) |
| voice/08.mp3 | 158857 | take, card 8 (8.80 s) |
| out/01.mp4 to out/08.mp4 | 289445 to 745849 each | per-card segments, built 2026-10-31 04:57 with `-t` |
| out/walkthrough.mp4 | 4659911 | the 8-card cut, 151.56 s |
| ws/ | 132K total | the source READMEs, data and MCP server the cards cite (SAMPLE-README.md, mcp/README.md, data/rfp_sample*.txt) |

Takes durations are from ffprobe, 2026-10-31.

## Other cuts in the same scratchpad (built by `variants/`)

| Path under `$V` | Bytes | What |
|---|---|---|
| out/walkthrough-recut.music70.mp4 | 3403192 | 1:06 recut; the same bytes as `media/walkthrough.mp4` in ret-rfp-intelligence commit 20c44fd |
| out/walkthrough-fluid.music70.mp4 | 7537507 | fluid-timed blueprint cut with music |
| bench/out/bench.music70.mp4 | 7142528 | bench cut with music |
| out/makingof-v2-fluid.music70.mp4 | 7183945 | making-of cut with music |
| bench/voice/ | 18M | bench takes |
| makingof/ | 6.0M | making-of takes |
| recut/voice/, capture/voice/ | 1.0M, 644K | recut and capture takes |
| out/, bench/out/ | 135M, 54M | all frames and segments |

The music bed (`Ephemeral Beauty (1).mp3`, read from ~/Downloads by `variants/mix.sh` and `variants/fluid-card.cjs`) is
not in the repo either.

## R8 fix, measured 2026-10-31

The same PNGs and takes, video re-encoded only (no audio regeneration), checked with `scripts/readme_video_check.py`:

| Build | FAIL | WARN | INFO | Runtime |
|---|---|---|---|---|
| `-shortest` on the looped still | 8 | 10 | 13 | 164.3 s |
| `-t <take + 0.8 s>` (this build.cjs) | 1 | 10 | 13 | 151.6 s |

The 7 R8 FAILs (cards 1 to 7, about 1.8 s of silent picture each, 12.7 s in all) are gone. The one FAIL left is R2 on card 6: the narration
says "twenty-four" questions, which neither README states at this snapshot. It is a content fix (add the real-model run to the
README, or pass the eval log as `--evidence`), not a render fix.
