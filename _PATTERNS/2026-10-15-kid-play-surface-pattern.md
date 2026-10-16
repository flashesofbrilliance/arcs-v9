# The kid play surface: an instrument, not a lesson (instance: Phosphor)

Status: DRAFT pattern, lifted from one instance (`_ARTIFACTS/phosphor.html`). Written 2026-10-15 after Zach's direction: take the whole artifact as a design pattern for a new kind of play for parents and kids, built on applied physics and kinesthetic learning, pulled by the child's own curiosity and imagination, not pushed. Ladder position (ADR-066): instance (Phosphor) to class (this note) to invariant (the rules below). Related memory: met-at-your-level-onramp-design-principle, adaptive-rhetorical-resonance. Engine this adapts: `operators/arcs_lte.py` (altitude detector, lossless codex, rhetorical resonance engine).

## The pattern in one line

An instrument, not a lesson: physical quantities as controls, immediate response to every action, the child's own signal as the material, mastery that opens more play, and nothing that asks for attention the child did not give.

## Invariants (what must survive any new instrument)

1. **Physics is the interface.** Every control is a real quantity (frequency, loudness, time and tempo, resolution as sampling, loop length, quantizing). The hidden curriculum is discovered by manipulation, never taught as a screen of text.
2. **No dead keys, no wrong answers.** Any input does something; presses snap to the beat so they cannot sound wrong.
3. **Response inside about 100 ms, in picture and sound together.**
4. **His own signal.** His voice, his rhythm, his choices are the material. Ownership comes from making, not from receiving content.
5. **Mastery opens more play, never points.** Stickers unlock capability (new colors, new reach), not scores, ranks, or streaks.
6. **The child ends it.** No timers, autoplay, notifications, nags or countdowns. A moment he likes can be kept (freeze).
7. **Down-res removes choices, never truth.** The kid surface can make what the grown-up surface can make, with fewer dials; the seam (Grown-up controls) stays visible.
8. **Local first.** Processing stays on the device; nothing is sent; nothing is kept unless a grown-up saves it. The page makes no network request and says so plainly. This is a design fact to verify, not a legal claim.
9. **Parent as co-player.** Any summary for a parent is created on the device, plain language, and about what he explored, not about surveillance.
10. **Sparse by default, density earned.** Glitch is post-minimal and lo-fi: silence and empty space are material, one effect at a time, rare hits on accents, slow decay, a thin line on a dark ground. More events, layers and effects are unlocked by mastery, not shown by default. Less is more is also the safer setting for flashing and loudness. (Zach, 2026-10-15.)
11. **Guardrails are features:** photosensitivity (no more than three flashes in any second), loudness (a ceiling for kids), and plain-language microphone handling.

## Pull versus push, as tests

Pull is child-initiated and child-ended. Signals we can measure from the local play log (names and times only): returns without a prompt, time he directs himself, new gestures per minute, repeats of something he liked, and whether he shows someone. Push to refuse: streaks, timers, notifications, autoplay, variable rewards, leaderboards, points that outlive the play.

## The family

One engine (signal in, physical controls, local only) with different instruments on top: Sing (loop pedal), Rhythm (steps and keys), Light (the visualizer), and later others. Instruments share the invariants; they differ in the quantity they let a child explore.

## What would disprove it

- A child at the right age does not return without a prompt, or stops within two minutes on every try.
- Behavior does not differ by altitude (age or attention), so an altitude dial is not doing work.
- The kid surface cannot produce something the grown-up surface can (the lossless set is broken).
- Stickers become the goal and the music is ignored (the reward has turned into push).
- Any guardrail fails on the shipped build.
- Learning claims: none are made. This pattern is a design bet. Evidence of learning outcomes would need a proper study and is not part of this note.

## Pre-registered checks (written before running them)

Prediction, before the first run: **G1 (flash rate) will fail** on at least one effect at 1/16-beat stutter or Blocks, because nothing limits how fast the picture can change; **G2 (loudness) will fail**, because audio goes straight to the speakers with no ceiling and layers are summed and hard-clipped; **G3 (no push features) will pass**.
- **G1.** Over 3 s of each worst-case scenario (each effect on its own, all effects together, the sequencer with every lane on, 1-bit tones, mashed keys) the frame's mean relative luminance changes by 10 percent or more in opposite directions no more than three times in any one second (the general flash threshold in WCAG 2.3.1, measured on the whole frame, which is a conservative proxy for the area rule).
- **G2.** Full-scale input never leaves the speakers louder than 0.5 of full scale (minus 6 dB) in kid mode, and a Grown-up checkbox turns the limit off.
- **G3.** The page uses no Notification API, service worker, or push; contains no words for points, streaks, leaderboards or countdowns; and makes no network request.
Kill: G1 or G2 failing is a stop-the-line finding, fixed before any new feature ships.

## Results: guardrails on the shipped build (2026-10-15)

Predictions written before the first run: G1 would fail on at least one effect; G2 would fail; G3 would pass. Outcome: **G2 failed as predicted** (audio went straight to the speakers; a layered loop hard-clipped), **G3 passed**, and **G1 was half right**. The first run read 0 flashes everywhere, which I distrusted, so I added a positive control (mashing the I key flips the whole picture). My own detector had a bug (a state machine that never registered a swing); after rewriting it the control read 6 flashes in a second, above the limit of 3, and every effect scenario still read 0 because the picture is mostly black thin lines (full-frame luminance never swings 10 percent). The real hazard was the invert key and checkbox, not the glitch effects. Fixes: invert is rate limited to one change per 340 ms (mashing now reads at most 2 flashes in any second) and all audio goes through a limiter, a kid volume gain and a tanh soft ceiling at 0.5 of full scale (a full-scale square measured 0.494; the Grown-up checkbox "Full volume" lifts it, measured 1.253). Second own error: the first throttle started at time 0, so on a page less than 340 ms old the first invert was ignored, which made a look test flaky; fixed by starting from minus infinity. Findings still open: the flash measure is the whole-frame proxy, not the WCAG area rule or the red-flash rule; the loudness ceiling is relative to full scale, not a measured sound pressure level at the child's ear (headphones and device volume still decide that); the invert limit does not stop a child tapping a different brightness-changing control at the same time, none of which exists today.
