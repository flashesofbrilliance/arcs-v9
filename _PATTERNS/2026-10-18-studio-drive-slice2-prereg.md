# Studio Drive slice 2: stutter, the flash limiter, and key-to-visual mapping (2026-10-18)

Status: pre-registered BEFORE the build. Results are appended at the bottom. Builds on the slice 1 Drive pre-registration and the AnalysisFrame v1 contract note, both in PR 1550 and not yet on main.

## What it is
1. **Shared flash limiter.** Every driven control moves through a slew limit computed once per row into a per-frame curve, so the value at time t is a pure
   function of the file and t (ADR-087). A full swing takes at least 5 frames (167 ms), which caps any rise-and-fall at 3 per second at 30 fps.
2. **Stutter aspect (Tag).** A Stutter depth control and a rate (1/4, 1/8, 1/16 of the cycle) on top of the existing Stutter gate source. When the gate is high,
   it lowers fidelity and kicks plate offset together. With "Fidelity drives the grit" on, one gate moves the whole grit stack.
3. **Key map: audio effects paired with visual effects.** Keys 1 to 6 (and six hold pads for touch) turn live audio effects on while held:
   Crush, Distort, Echo, Room, Shimmer, Sweep. Each key is paired with a visual effect on a print control: Crush to the pixel mosaic, Distort to rough edges,
   Echo to plate offset, Room to spray, Shimmer to spatter, Sweep to text travel. The pairing is editable and saved with the look.
4. **Performance is a recipe.** Key presses are written to an event log (key, on or off, time). The print reads the log, never the live keyboard, so a performance
   replays exactly, scrubs exactly, and renders offline frame by frame. The audio effects themselves are live monitoring only.

## Pre-registered kills
| id | claim | kill if |
|---|---|---|
| S1 | Slew limit | any driven control changes by more than 20 percent of its range between two consecutive 30 fps frames |
| S2 | Calm | over 5 s of a 10 Hz kick with stutter depth 100 and keys mashed, the rendered print makes more than 3 luminance flashes (a rise and a fall of 12 percent of range) in any second |
| S3 | Stutter has impact | at stutter depth 100, frames with the gate high do not have fidelity at least 40 points below frames with the gate low, or the plate offset is not higher; at depth 0 any difference appears |
| S4 | Log purity | the markup at time t differs between a performance made live and the same log loaded fresh, or after seeking away and back |
| S5 | Pairing responds | holding Crush from 2.0 to 3.0 s does not raise the pixel control by at least its paired amount at 2.5 s, or it is above 10 percent of that at 3.6 s |
| S6 | Audio effects honest and consented | an effect node exists before Play is pressed, the effect is not engaged within 50 ms of key down, or it is still engaged 50 ms after key up |
| S7 | Small log | 10 minutes of key mashing (6 keys, 4 presses a second) is over 60 KB as JSON |
| S8 | Recipe carries it | Copy recipe and Saved looks do not carry the key map, the log and the stutter settings, or restoring them gives different markup |

## Not claimed
That the pairings are the right ones (they are defaults; the table is editable). That the effects sound good. That the audio effects appear in an exported video:
the exporter muxes the dry file, and that gap is stated, not hidden. Phone behaviour and the Artifact viewer are untested.

## Results
(appended after the build)
