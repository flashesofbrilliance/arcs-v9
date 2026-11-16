# floor-light (private, local-only)

A menu-bar dot that shows how long you have held the floor on a live call.
Green under 40s, yellow 40 to 60s, red after. No LLM, no network, nothing saved.
Not for any arcs.care public surface.

**The rule.** Your turn starts when your mic carries speech while the call is quiet.
It ends when the other side speaks for 1.2s without a real pause (about 4 words).
"Mm-hmm" and "yeah" do not end it.

## Run it on the Mac (macOS 13+)

```bash
cd tools/floor-light && swiftc -O floorlight.swift -o floorlight
```

```bash
./floorlight --meter
```

The first run asks your terminal app for Microphone and for Screen & System Audio
Recording (System Settings > Privacy & Security). Grant both and run again.
`--meter` prints both channels' loudness once a second: speak, then play a video,
and check that your voice is above `--mic-db` (default -42) and the call is above
`--sys-db` (default -50) while silence is below them. Then drop `--meter`.

Menu: **Presenting** pauses the light for an invited monologue (a demo, "tell us
about yourself"). **Quit** prints the call's turn summary (n, median, p75, p90).
Headphones help; on speakers the echo guard ignores your mic while the call plays.

## Calibrate

```bash
python3 floorlight.py --self-test
```

```bash
python3 floorlight.py replay call1.txt call2.txt
```

Replay reads `m:ss SRC` lines (M = you, S = them with more than 3 words, s = them
backchannel, END = excerpt end) reduced from a Granola transcript. Keep those
files out of the repo. Proposed rule: yellow at your p75 turn, red at your p90.
First read (2026-11-16, 56 turns from the first ~9 minutes of 4 calls): median 12s,
p75 29s, p90 73s; 40s/60s would light red on about 1 turn in 8.

## Not yet

v1 (density: long AND jargon-heavy = red) waits on the projection-map pilot's P5.
If P5 is false or can't be told, v0 is the product.
