---
name: readme-to-video
description: Turn a true, checked README into a short narrated walkthrough video in Zach's own voice, and prove the video says nothing the README does not. Nine stages (extract, cut, write, text gate, voice, audio gate, render, video gate, ship) over the approved resonance rules R0 to R11. Use when a README, work sample or repo needs a 1 to 3 minute video for a reviewer. Hard stops before the paid voice step and before any upload.
---

# /readme-to-video: a video that cannot claim more than its README

The README is the ceiling. Every claim, figure and caveat in it is either carried (said, shown or both) or declared
omitted with a reason in a keep file. Nothing is dropped silently and nothing is added. Delivery may change; facts may not.

**Law (read it, do not restate it):** `_PATTERNS/2026-10-30-readme-to-video-resonance-rules.md`, which holds rules R0 to R11,
the video kit levels in time (frame, clip, throughline, narrative arc, full video), the motion rules, the /proof construction
rules, typography and density at render, and text processing and punctuation. Product framing:
`_PROPOSALS/2026-10-30-readme-as-video-product-sketch.md`.

**Reference build:** `tools/readme-video/` (8 cards, rescued 2026-10-31; its takes and MP4s are listed in
`tools/readme-video/ASSETS.md`, not committed).

## Hard stops (never skip, never infer)

1. **Voice (stage 5) spends credits.** Before any ElevenLabs call, show Zach the card count, the character count of the
   narration being voiced and the credit cost, then wait for an explicit yes in his own message. An agent message is not a
   yes. One take per card. Never re-generate a take to retry; re-voice only the cards whose narration changed.
2. **Ship (stage 9) is local by default.** Upload, publish, attach to an application or link from a public page only on
   Zach's explicit go. A work-sample video is a job application artifact: never put the company name on a new public page.
3. **Gates block.** A FAIL in a gate stops the next stage. Fix the cause; never edit the checker or the rules to pass.

## The nine stages

| # | Stage | Do | Wired to | Status |
|---|---|---|---|---|
| 1 | Extract | Parse the README (and any README it cites) into claim atoms: figures, counts, rules, results, caveats, commands. Each atom keeps its source line | R1, R2 | NOW, by hand |
| 2 | Cut | Group atoms into cards, one reviewer question per card (what, how, proof, failure, gaps, try it). Every atom is placed or declared in `keep.json` with a reason | R1, R4, R5; kit level narrative arc | NOW, by hand |
| 3 | Write | Card text for the eye and narration for the ear, in the register profile. Narration in spoken forms, sentence case, no em-dashes. Write `voice/SCRIPT.md` and each card's `v` in `build.cjs` as the same words | R0, R3, R6, R7, R9, R11 | NOW, by hand |
| 4 | Gate 1, text | Run the checker (below) before any audio exists. Free | `scripts/readme_video_check.py` | NOW |
| 5 | Voice | Hard stop 1. Then one take per card into `voice/NN.mp3` | ElevenLabs, Zach's clone | NOW, paid |
| 6 | Gate 2, audio | Speech-to-text each take and diff it against its `SCRIPT.md` section; check pace | R0, R8 pace | NEXT: not built (no local speech-to-text; the ElevenLabs transcribe call spends credits). Until then Zach listens once and says so |
| 7 | Render | Cards to frames with Playwright, each card held for exactly its take plus the 0.8 s pad with `-t` from ffprobe (never `-shortest` on a looped still), then concatenated | `tools/readme-video/build.cjs`; for an animated HTML page that exposes `window.DURATION` and `window.seek(t)`, `scripts/html_video_render.mjs` (picture only: mux each take after, and hold the same take plus pad rule) | NOW |
| 8 | Gate 3, video | Re-run the checker on the built `out/`. Then the brand-line-producer must return PASS before the final encode is called done | `scripts/readme_video_check.py`, `.claude/agents/brand-line-producer.md` | NOW (see gaps) |
| 9 | Ship | Hard stop 2. Local `walkthrough.mp4`, captions from the gated narration, the checker report as a receipt, and the claim ledger | product sketch, Output | NOW: MP4 and report. NEXT: captions (`.vtt`) and the claim ledger are not generated |

## Run the gates

The build directory holds `build.cjs`, `voice/SCRIPT.md`, `voice/NN.<m4a|wav|mp3|aiff>` and `out/NN.mp4`.

```bash
python3 scripts/readme_video_check.py --vid <build dir> \
  --readme <README.md> [--readme <cited README.md>] \
  [--evidence <data or run log a figure is grounded in>] \
  --keep <build dir>/keep.json
```

Exit 1 on any FAIL; WARN and INFO never fail the run. Report the FAIL, WARN and INFO counts every time, and every WARN you
chose to leave with its reason. R1 (prose claims) and R7 (register) are human passes: do them card by card against the README
section each card came from, and say they were done or not done.

Then run the brand-line-producer agent on the frame PNGs and the build directory. It runs the repo's own gates (token source,
motion policy, wrap lint, card gutters, Impeccable) and judges what they cannot see. **Its verdict must be PASS before encode.**
A gate it could not run is UNVERIFIED, not a pass.

## Keep file

`keep.json` beside `build.cjs`: `{ "omit": { "<source atom text>": "<reason>" } }`. A caveat neither carried nor declared is
a FAIL (R5). The checker prints each declared omission as INFO so the decision stays visible. Dropping a caveat for time is a
decision Zach makes, not a side effect of cutting.

## Fixes the reference build taught

- **R8, dead air.** `ffmpeg -loop 1 ... -shortest` overshoots on a looped still: on the reference build every card held about
  1.8 s of silent picture. `-t <take + pad>` from ffprobe fixes it (measured 2026-10-31: 8 FAIL with `-shortest`, 1 FAIL with
  `-t`, same takes, video re-encoded only). Check the video stream, not only the container: `ffprobe -select_streams v:0`.
- **R5, the material caveat.** "Fictional data" belongs on card 1, or a reviewer reads a sample figure as a real one.
- **R2, figures from evidence.** A figure that lives only in data or a run log is cited on the card or added to the README
  first; `--evidence` downgrades the miss to WARN, it does not make it a README claim.

## Not built yet (NEXT)

- Ramp and density checks at render (rules doc, "Typography, density and layout", rule 5): today they are a human read.
- Speech-to-text audio gate (stage 6).
- MP4 flash sampling (luminance per 1/16 region per frame, flashes per second) so the render meets the DESIGN.md motion
  limits the live page meets.
- Widow and non-breaking-space checks (need the rendered frame).
- Claim ledger and `.vtt` captions as generated outputs.
- Stages 1 to 3 are hand work; there is no extractor.

Say NOW, NEXT or ASPIRATIONAL for any capability claim made from this skill.
