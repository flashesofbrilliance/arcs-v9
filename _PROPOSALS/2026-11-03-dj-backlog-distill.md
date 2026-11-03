# dj.arcs.care backlog: audit, reconcile, distill (2026-11-03)

**Status:** PROPOSAL. Nothing in `_QUEUE/induced-backlog.jsonl` changes state until Zach rules below. Phosphor is on the back burner as of today (Zach, row `phosphor-pad-mute-choke`), so this document is the resume packet, not a call to build.

**Scope:** every backlog row whose text mentions Phosphor, dj.arcs.care or dj.html: 104 rows, 86 live (80 OPEN, 4 HOLDING, 2 HELD), 18 closed. Sources read: the backlog, `_PATTERNS/2026-10-15-phosphor-visualizer-prereg.md` (amendments 1 to 73), `_PATTERNS/2026-10-24-phosphor-child-session-outcomes.md`, `runtime/specs/phosphor-release-holds.json` (empty), the `scripts/phosphor_*_check.mjs` headers. Open PRs touching Phosphor: 0 (GitHub search, today).

## 1. The one finding that orders everything

The outcomes table (2026-10-24) says 2 of 25 child outcomes are observed, both from one child (n=1), and 11 are shipped features nobody has measured. The local play log that measures outcomes 1, 3, 4, 6, 7, 9 and 10 exists and has never been run in a real session. Meanwhile 80 build rows are OPEN. The bottleneck is evidence, not features: until one watched session runs, the order of the 80 is a guess. New row `phosphor-watched-session-1` makes that the first step on resume.

## 2. Drift found (mechanical checks, reproducible)

| Check | Result |
|---|---|
| Dangling `depends_on` / `related` / `unblocks` ids | 0 |
| `review_by` already passed | 0 |
| State says OPEN or HOLDING, note says a slice shipped or was built | 8 (table 3a) |
| Row predates an amendment that built part of it, note never updated | 5 confirmed (table 3b) |
| Paused by Zach but written HOLDING (enum: HOLDING = waiting on rows, HELD = paused by Zach) | 1 (`phosphor-pad-mute-choke`) |
| Live rows missing route, gates or trigger (not executable as written) | 13 of 86 |
| Live rows with no `priority` / no `reach` | 84 / 61 |

**Root cause.** 59 of the 104 rows were written on 2026-10-15, before amendments 13 to 73 shipped. When an amendment landed, nobody went back to the older rows it touched. The amendment log and the backlog are two ledgers with no crosswalk between them.

## 3. Reconcile (rulings for Zach, one line each)

### 3a. Slice shipped, row still open

Proposed for each: close the row as DONE at the shipped slice, and carry its "Left" list as one line in the cluster's keeper row, so the leftovers are not lost and no row stays open on the strength of a tail.

| Row | Shipped | Left (from the row) |
|---|---|---|
| `phosphor-gesture-grab-preset` | Grab, amendment 59, release 4 | per the row |
| `phosphor-flying-faders` | slice 1, amendment 61, release 5 | knobs, kid pads, bar quantize, several lanes, saving, share |
| `phosphor-smart-replay-note` | same slice as flying faders (identical note) | merge into `phosphor-flying-faders` (SUPERSEDED) |
| `phosphor-first-minute-ritual` | slice 1, amendment 68, release 7 | measurement (outcome 1) |
| `phosphor-virtual-pad-mapping` | slice 1, amendment 48 | per the row |
| `phosphor-pad-mute-choke` | slice 1, amendment 67, release 7 | groups across banks, per-group fade, mute in recipe |
| `phosphor-render-surface` | parts 1 to 3, amendments 58, 62, 64 | per the row |
| `phosphor-pattern-text-box` | built amendment 71, public release 8 (hold removed) | none named |

### 3b. Partly built by a later amendment, note stale

| Row | Already built | Still open |
|---|---|---|
| `phosphor-web-midi` | MIDI in, amendment 33 (`phosphor_midi_check.mjs`) | the iPad Safari test only; fold into `phosphor-hardware-link` |
| `phosphor-tempo-swing` | swing as Feel, amendment 19 (`phosphor_swing_check.mjs`) | the tempo slider (turtle to rabbit) |
| `phosphor-note-repeat-swing` | swing, amendment 19 | Note Repeat only; merge with the tempo slider into one row |
| `phosphor-realtime-fx-rack` | Echo, Room, Shimmer (chorus), Sweep, amendment 13; per-effect limits, amendment 38. Note says only Crush and Distort exist: stale | flanger or phaser, harmonize (needs `phosphor-granular-engine`) |
| `phosphor-dj-table-stakes` | filter sweep and echo, amendment 13; crossfader between decks, amendment 24 | 3-band isolator, 8 hot cues, loop roll, record the mix; fold into `phosphor-deck-dj-core` |

### 3c. Merge pairs (keeper first, the other becomes SUPERSEDED)

| Keeper | Folded in | Why |
|---|---|---|
| `phosphor-flying-faders` | `phosphor-smart-replay-note` | identical status notes; the row calls itself grab plus faders |
| `phosphor-deck-dj-core` | `phosphor-dj-table-stakes` | same DJ core; table stakes partly shipped (3b) |
| `phosphor-auto-loop-catch` | `phosphor-audio-retro-buffer` | the buffer row says to combine them |
| `phosphor-order-decay-pockets` | the strength dial of `phosphor-timing-correct-strength` | the row says it is the same dial; its overdub record part stays |
| `phosphor-dj-style-presets` | `phosphor-genre-kits` | both are one-tap genre bundles (tempo, look, effect, kit) |
| `phosphor-hardware-link` | `phosphor-web-midi` remainder | one input path, one iPad test |
| `phosphor-patch-bay-real-graph` | `phosphor-back-panel-cables` | the back panel is the patch bay |
| `phosphor-consonance-dissonance-budget` | `phosphor-consonance-shavasana` | same measure; the shavasana is its subtractive UI |
| `phosphor-tempo-swing` (renamed to the tempo slider) | `phosphor-note-repeat-swing` | swing is shipped; the rest is one small row |

Nine merges take the live count from 86 to 77 before any closes.

### 3d. Not builds: gates or decisions

- `phosphor-notomation-check`, `phosphor-sparse-defaults`, `phosphor-aesthetic-constitution`: these are invariants. Proposed: copy each into the `gates` of the rows that suggest or auto-apply anything (`phosphor-earned-automagic`, `phosphor-consonance-dissonance-budget`, `phosphor-detect-suite`, `phosphor-euclid-polyrhythm-quantize`, `phosphor-dj-style-presets`), then close the three as SUPERSEDED by those gates. `sparse-defaults` is already invariant 10 of the kid play surface pattern.
- `phosphor-edge-functions-stance`, `phosphor-dj-hard-parts`: decision notes whose answer is already in the row (edge functions are not for the realtime path; key lock and stems are deferred). Proposed: write the two answers as one amendment line, close DONE.

### 3e. Compost candidates (Zach's call, not mine)

- `phosphor-heading-light-rays`: Zach said table it unless cheap; the page cap is the constraint.
- `phosphor-binaural-beats`: the row itself says the evidence is limited and mixed; headphones only; a kid surface.
- `phosphor-optical-sensor-controller`: already HOLDING behind generic MIDI input; keep or compost.

### 3f. Out of scope for this backlog

- `tap-pin-portable-seed-key`: only cites `phosphor-parent-kid-access` as related; it belongs to the seed and product catalog work.
- `media-codex-atlas-ziggurat-seeds`: emits from Phosphor but is a cross-product codex. Left as is.

## 4. Distill: 84 Phosphor rows into 9 clusters

After the merges in 3c, each cluster has one keeper. The keeper is the row to open first when the cluster's turn comes.

| Cluster | Keeper | Rows |
|---|---|---|
| A. Evidence and real-device truth | `phosphor-watched-session-1` (new) | `phosphor-kid-pattern-promote`, `phosphor-webkit-eject-lock`, `phosphor-rc1-firefox-verify`, `phosphor-acoustic-sync-test`, `phosphor-simulated-user-pretest`, `phosphor-parent-learning-summary` |
| B. Clock and time (gates every speed, reverse and sync feature) | `phosphor-tempo-map-slice3` | `phosphor-tempo-detector-v2`, `phosphor-latency-worklet`, `phosphor-platter-speed`, `phosphor-reverse-tape-stop`, `phosphor-scratch-wheel`, `phosphor-slip-sync` |
| C. Sequencer and groove | `phosphor-drum-machine-rows` | `phosphor-tempo-swing`, `phosphor-note-repeat-swing`, `phosphor-303-bass-lane`, `phosphor-queued-pattern-song`, `phosphor-euclid-polyrhythm-quantize`, `phosphor-timing-correct-strength`, `phosphor-order-decay-pockets`, `phosphor-kintsugi-seams`, `phosphor-lock-a-bar`, `phosphor-glass-grow`, `phosphor-life-lane`, `phosphor-sparse-defaults`, `phosphor-pattern-text-box` |
| D. DJ core | `phosphor-deck-dj-core` | `phosphor-dj-table-stakes`, `phosphor-dj-hard-parts`, `phosphor-player-waveform-hotcuts`, `phosphor-dj-style-presets`, `phosphor-genre-kits`, `phosphor-loudness-chain`, `phosphor-song-memory` |
| E. Listening and smart offers (all carry the notomation gate) | `phosphor-rhythm-pattern-detect` | `phosphor-detect-suite`, `phosphor-auto-loop-catch`, `phosphor-audio-retro-buffer`, `phosphor-consonance-dissonance-budget`, `phosphor-consonance-shavasana`, `phosphor-seed-mash`, `phosphor-band-triggers`, `phosphor-earned-automagic`, `phosphor-notomation-check` |
| F. Inputs and hardware | `phosphor-hardware-link` | `phosphor-web-midi`, `phosphor-real-piano-bridge`, `phosphor-remote-pads`, `phosphor-numpad-finger-drum-map`, `phosphor-beam-controller`, `phosphor-optical-sensor-controller` |
| G. Controls and look | `phosphor-te-gauge-knobs` | `phosphor-te-sequencer-skin`, `phosphor-wheel-island`, `phosphor-gesture-set`, `phosphor-controller-zoo`, `phosphor-patch-bay-real-graph`, `phosphor-back-panel-cables`, `phosphor-player-dock-states`, `phosphor-four-resolution-dials`, `phosphor-light-controls`, `phosphor-phase-field-viz`, `phosphor-heading-light-rays`, `phosphor-aesthetic-constitution` |
| H. Sound: voice and effects | `phosphor-granular-engine` | `phosphor-voice-effects`, `phosphor-realtime-fx-rack`, `phosphor-embedded-lyrics-karaoke`, `phosphor-binaural-beats`, `phosphor-moon-water-presets` |
| I. Kid play, learning and trust | `phosphor-my-loops-shelf` | `phosphor-first-minute-ritual`, `phosphor-copy-me-game`, `phosphor-freeze-dance-coop`, `phosphor-codes-ladder`, `phosphor-parent-kid-access`, `phosphor-virtual-pad-mapping`, `phosphor-pad-mute-choke` |
| Closed-out by 3a (paperwork) | n/a | `phosphor-gesture-grab-preset`, `phosphor-flying-faders`, `phosphor-smart-replay-note`, `phosphor-render-surface`, `phosphor-edge-functions-stance` |

## 5. Resume order (when Phosphor comes off the back burner)

1. **`phosphor-watched-session-1`**: one watched child session with the play log on, then `python3 scripts/phosphor_playlog_summary.py`. No code. It turns outcomes 1, 3, 4, 6, 7, 9 and 10 from SHIPPED-not-measured into data, and the result decides which of clusters C to I go next.
2. **Real-device proof** (cluster A): `phosphor-webkit-eject-lock` on a real iPad (outcome 21, a child-safety claim still owed) and `phosphor-rc1-firefox-verify` (blocked only on Zach opening Nightly.app once).
3. **Apply the rulings** in section 3 (row `dj-backlog-reconcile-apply`). About 20 rows close or merge; no code.
4. **`phosphor-tempo-map-slice3`** (cluster B): the clock that platter speed, reverse, scratch and slip sync all wait on, and the only row `phosphor-pattern-text-box` depends on.
5. **`phosphor-my-loops-shelf`** (cluster I): the only outcome blocked on a missing feature (outcome 16). After that, let the session evidence pick.

Everything else waits for evidence. Ranking 70 rows by reasoning alone is the entropy-as-motion the WORLD.md enemy describes.

## 6. Rulings needed (answer by letter)

- **R1.** Close the 8 rows in 3a as DONE at the shipped slice, carrying each Left list into its keeper? (yes / no / per row)
- **R2.** Apply the 5 stale-note fixes in 3b?
- **R3.** Apply the 9 merges in 3c?
- **R4.** Turn the 3 invariants into gates and close the 2 decision rows (3d)?
- **R5.** Compost any of the 3 in 3e?
- **R6.** Change `phosphor-pad-mute-choke` from HOLDING to HELD (paused by you), and mark the rest of the Phosphor rows HELD too while it is on the back burner? Today only one row carries the pause.
- **R7.** Add a crosswalk check later (each amendment names the rows it touches; a check lists rows that no amendment cites and amendments that cite no row), so this drift cannot rebuild? Proposed only; not built while Phosphor is paused.

## Not claimed

The merges and clusters are my judgment from reading the rows; the drift counts in section 2 are mechanical and can be rerun. I did not open the built page or run the Phosphor suite, so "shipped" means the amendment log and release commits say so, not that I watched it work today.
