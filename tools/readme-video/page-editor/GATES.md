# Gate report: live page editor walkthrough

Source (the ceiling): `src/ui-kit/tabbed-brief/README.md`, "Tuning by hand (internal only)", as hardened in PR 2136.
Six cards, 114.9 s, in Zach's voice clone (takes in `voice/TAKES.md`).

| Gate | Result |
|---|---|
| Text checker (`scripts/readme_video_check.py`, R0 to R11), on the timed takes | 0 FAIL, 0 WARN, 11 INFO |
| Brand-line-producer | PASS (wrap-lint, tokens, motion, card-gutter, Impeccable, 0 em-dashes), after two BLOCK rounds |
| R1 prose claims, human pass | Done card by card against the README section; every line traces to it |
| R7 register, human pass | Done: no royal we, no hype, sentence case |
| Stage 6 audio gate | NEXT: not built; Zach listens once and says so (not done yet) |

R8: every card's video stream equals its take plus the 0.8 s pad (measured with ffprobe, v:0).

INFO: R3 numbers on screen but not said (route labels, port 8799, list counts); R6 acronyms JSON, CSS, URL to confirm by ear;
R2 narration stems not in the README (both, depends, flag, itself, land, local, puts, style, them, your), read as wording, not
new claims; R10 runtime; and each declared omission in `keep.json`.

Brand-gate rounds: (1) BLOCK, h1 tight leading and `--fs-meta` as a fifth size. The h1 was fixed. The `--fs-meta` finding was
disputed: the rules doc, rule 1, allows it for references, and Zach's 2026-11-01 ruling exempts the citation. The gate withdrew it.
(2) BLOCK, the lede inherited a tight line height in Impeccable's reading. Fixed with `line-height: 1.5`. (3) PASS.
Seam: the template `tools/readme-video/arcs-v9/build.cjs` has the same h1 1.15 and the same lede with no line height.

Names: Gravity and Louisville appear only as example builders; the My Ally hub is left out (declared in keep.json).
