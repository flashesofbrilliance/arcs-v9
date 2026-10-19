# Phosphor backlog triage: release slices and compost candidates (2026-10-19)

Status: PROPOSAL, read-only. No row in `_QUEUE/induced-backlog.jsonl` was changed. Every fate below is Zach's ruling.

Counts (from the file, 2026-10-19): 99 `phosphor-*` rows: 83 OPEN, 12 DONE, 2 HOLDING, 1 HELD, 1 SUPERSEDED. 85 rows are live (OPEN + HOLDING + HELD, minus none). Build rules: edit `_ARTIFACTS/phosphor-src/`, run `scripts/phosphor_build.py`; public copy only via `--release` (about every 5 shipped rows).

Ordering rule: fixes and foundations first, then features that consume them, then gated and speculative rows. Dependencies are taken from each row's `status_note` / `trigger` text, not inferred.

## Slice 1 (NEXT): trust the build, then the cheap light-ups
| Row | Why here |
|---|---|
| phosphor-webkit-eject-lock | Real bug found by the WebKit suite; kid lock escape |
| phosphor-webkit-bars-determinism | Real bug, WebKit check B6 fails |
| phosphor-low-band-resolution | Analysis fix; blocks consonance-dissonance-budget and helps band-triggers |
| phosphor-kintsugi-seams | Note says "cheapest light-up", existing gold token, no new logic |
| phosphor-cue-point | Note says "small"; no dependencies |

Gate: full suite on Chromium plus WebKit green, then `--release`. Note rc1 is HELD on Firefox (see Held), so release gating on Firefox stays Zach's call.

## Slice 2: rate model and tempo foundations
phosphor-tempo-detector-v2 (real-song agreement poor, 25 of 35 exact), phosphor-tempo-map-slice3, phosphor-acoustic-sync-test (closes the biggest mixer test hole), phosphor-tempo-swing, phosphor-note-repeat-swing.
Unblocks: platter-speed, reverse-tape-stop, scratch-wheel, slip-sync, deck-dj-core (all "after the pins and tempo map" / rate model).

## Slice 3: rate-envelope features
phosphor-reverse-tape-stop (builds the rate-envelope model), phosphor-platter-speed, phosphor-slip-sync, phosphor-deck-dj-core, phosphor-scratch-wheel (explicitly after reverse and tape stop).

## Slice 4: pad and sequencer instrument
phosphor-drum-machine-rows, phosphor-virtual-pad-mapping (slice 1 shipped), phosphor-pad-mute-choke, phosphor-timing-correct-strength, phosphor-queued-pattern-song. Then follow-ons phosphor-303-bass-lane (explicitly "after drum rows"), phosphor-numpad-finger-drum-map, phosphor-beam-controller (after pad mapping).

## Slice 5: record, replay, render
phosphor-gesture-grab-preset + phosphor-smart-replay-note + phosphor-flying-faders (slice 1 shipped, built together per their notes), phosphor-render-surface (parts 1 to 3 shipped; check whether anything remains, may be DONE), phosphor-audio-retro-buffer (privacy design needed before build: could hold a child's voice).

## Slice 6: orders of order (wabi-sabi family)
phosphor-order-decay-pockets, phosphor-lock-a-bar, phosphor-sparse-defaults, phosphor-notomation-check (invariant, cheap, ship before any suggestion feature), phosphor-euclid-polyrhythm-quantize.

## Slice 7: UX shell and kid surfaces
phosphor-player-dock-states, phosphor-parent-kid-access (passkey, needs secure origin), phosphor-wheel-island, phosphor-gesture-set, phosphor-my-loops-shelf, phosphor-parent-learning-summary (honesty rule: parent is told).

## Slice 8: analysis and suggestion (riskiest; pre-register accuracy first)
phosphor-rhythm-pattern-detect, phosphor-auto-loop-catch (builds on it), phosphor-detect-suite, phosphor-seed-mash, phosphor-consonance-dissonance-budget (needs low-band-resolution from slice 1), phosphor-band-triggers.

## Later or gated
- Audio engine: phosphor-granular-engine, phosphor-realtime-fx-rack, phosphor-voice-effects (pitch detection on child voices is a risk), phosphor-loudness-chain, phosphor-latency-worklet, phosphor-dj-table-stakes.
- Design system true-up group: phosphor-te-gauge-knobs, phosphor-te-sequencer-skin, phosphor-controller-zoo, phosphor-back-panel-cables, phosphor-patch-bay-real-graph, phosphor-light-controls.
- Learning and games: phosphor-codes-ladder, phosphor-earned-automagic, phosphor-first-minute-ritual, phosphor-copy-me-game, phosphor-freeze-dance-coop, phosphor-glass-grow, phosphor-genre-kits, phosphor-dj-style-presets, phosphor-moon-water-presets.
- Waits on a human event: phosphor-kid-pattern-promote (Zach's first real child session), phosphor-remote-pads (iPad risk).

## Held
- phosphor-rc1-firefox-verify: HELD until Zach opens Playwright's Nightly.app once by hand. Unchanged.
- phosphor-heading-light-rays and phosphor-optical-sensor-controller are HOLDING; leave.

## Compost candidates (proposals only)
Duplicates or overlaps (merge into the survivor, mark the other SUPERSEDED):
1. phosphor-note-repeat-swing overlaps phosphor-tempo-swing (both carry swing as every second sixteenth late). Survivor: tempo-swing; fold Note Repeat into slice 4 pad work.
2. phosphor-web-midi, phosphor-hardware-link and phosphor-real-piano-bridge share one Web MIDI input layer and one stated blocker (no Web MIDI on iPad Safari). Keep web-midi as the single row; others become checklist items under it. Also phosphor-optical-sensor-controller depends on it.
3. phosphor-gesture-grab-preset, phosphor-audio-retro-buffer and phosphor-smart-replay-note: smart-replay-note is a note, not work (its own text says it is the grab buffer plus flying faders built together). Candidate to close as a pointer.
4. phosphor-player-waveform-hotcuts overlaps phosphor-deck-dj-core (deck loops and cuts) and the existing slice strip; check before building.
5. phosphor-te-sequencer-skin and phosphor-te-gauge-knobs and phosphor-controller-zoo all fall under the design-system true-up; one row would do.
6. phosphor-embedded-lyrics-karaoke: the row's own check found lyrics in few of 190 files; low yield, candidate to compost unless Zach wants it anyway.

Speculative or evidence-poor (compost or HOLD):
- phosphor-binaural-beats: the row itself notes the evidence for effect is weak.
- phosphor-edge-functions-stance: a decision note, no build; record the decision and mark DONE.
- phosphor-dj-hard-parts: "decide later" row; keep as a single decision record, not work.
- phosphor-phase-field-viz, phosphor-life-lane, phosphor-four-resolution-dials, phosphor-consonance-shavasana, phosphor-aesthetic-constitution: research-flavored; consonance-shavasana's own note says pre-register first because "most harmonic" is a metaphor.
- phosphor-simulated-user-pretest: useful but unscoped; could attach to slice 1 gating instead of standing alone.

SUPERSEDED already: phosphor-ux-molt-levels.

## Caveats
- Read from row `jtbd`, `trigger`, `status_note` truncated views; I did not open every note in full or verify that "shipped" claims match main. Spot check before ruling, especially phosphor-render-surface and phosphor-flying-faders.
- Slice size is about 5 on purpose; slices 4 and 8 run larger because follow-ons are listed with their parent.
- Needs Zach: approve slice 1 as next, rule on each compost line (none applied).
