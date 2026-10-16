---
spec: media-codex
version: 0.1
status: DRAFT (Zach asked 2026-10-16; nothing built; every number below is a proposal)
date: 2026-10-16
---

# Media Codex: mp3 or mp4 to Atlas, Ziggurat and Decomposed Seeds

Zach, 2026-10-16: a codex that translates an mp3 or mp4 into an Atlas, a Ziggurat and Decomposed Seeds, with interoperability and reconstitution rules. This is the proposal for that, built on what Phosphor already computes (`_ARTIFACTS/phosphor.html`: 64 bands at 30 frames a second, onsets, tempo grid, per-beat DNA and RNA codons, waypoints with a song fingerprint). It reuses the grammar of `runtime/specs/atlas-bundle-observatory-spec.md` (a bundle file, Ziggurat tiers as topological depth) and does not invent a second one.

## The three objects

**Atlas** is the whole map of one media file: one JSON file, `media-atlas.v1`, holding every tier below plus the file's identity. It is the interchange object. Two programs that agree on this file agree on the song.

**Ziggurat** is the tier structure inside the Atlas. A tier is built only from tiers beneath it (depth is the topological level, as in the atlas-bundle spec), so each tier can be checked against the one below:

| Tier | Holds | Built from | Lossless? |
|---|---|---|---|
| 0 Signal | file hash, duration, sample rate, channels, container tags, fingerprint (hash of the whole-song DNA and duration) | the file | identity only, not the audio |
| 1 Frames | 64 band energies, level, spectral flux, centroid per frame at 30 fps | tier 0 | no (lossy summary) |
| 2 Events | onsets, valleys, chapters, tempo and grid origin with confidence, swing | tier 1 | no |
| 3 Beats | one DNA codon (3 bases, quartile ranks of low weight, brightness, onset density) per beat | tiers 1 and 2 | no, by design (quartiles) |
| 4 Form | phrases, bars, sections, key estimate, density arc | tier 3 | no |
| 5 Recipe | the look: settings snapshot, RNA codons as played, level, swing, waypoint text | any tier, plus the player | yes (it is a set of settings) |

For mp4 the picture track adds a parallel strand: tier 1 frame luminance and motion per frame, tier 3 a per-beat picture codon. The audio tiers are unchanged.

**Decomposed Seeds** are the smallest sets that can regrow a tier, one seed family per tier, each with its own `seed_id` and the tier it regrows:
- Frame seed: the band envelopes, quantized to 8 bits and run-length coded.
- Event seed: onset times and strengths, tempo and grid origin.
- Beat seed: the DNA strand (a text string of letters).
- Form seed: the chapter boundaries and the key.
- Recipe seed: the settings JSON.
Seeds are independent files so a program can carry only the ones it needs (a mixer needs the Event and Beat seeds, not the Frame seed).

## Reconstitution rules (what can and cannot come back)

1. **The picture regrows exactly from tier 1 plus a Recipe seed.** Phosphor draws the picture as a function of tier 1 and the settings, so the same Atlas gives the same frames (check: pixel hash at five times, as the twin check already does).
2. **The sound does not regrow from seeds.** Seeds are features, not audio. Regrowing sound means resynthesis (clicks on onsets, noise shaped by the band envelopes), which is a sketch of the song, never the song. The codex must label any resynthesis "sketch" and never present it as the original.
3. **Earned fidelity:** a tier may claim only the fidelity its seeds carry. A Beat seed alone regrows a rhythm and density pattern, not a melody.
4. **Lossless invariants:** the fingerprint, duration, tempo grid, onset times (to a frame), and the DNA strand survive every round trip. A reconstituted Atlas whose invariants differ from the source is rejected, not repaired.
5. **Kintsugi:** a failed reconstitution shows the break (which tier, which invariant) and never patches it silently.
6. **Write-lock:** an Atlas is immutable once its fingerprint is minted; edits create a new Atlas that names its parent (lineage), like a Receipt.

## Interoperability rules

1. One file format (`media-atlas.v1`, JSON, UTF-8), a `version` field, and a `tiers` map, so a reader can ignore tiers it does not know.
2. Atlases are compared by tier: two songs are **tempo-compatible** when the tempo ratio is 1, 2 or 1/2 within 4 percent (the mixer's sync rule) and **key-adjacent** when the keys are the same, a fifth apart, or relative major and minor.
3. A **waypoint** (Phosphor's copy-and-paste text) is the Recipe seed plus the fingerprint, so it applies to any Atlas with the same fingerprint and never moves the playhead on a different one (already built).
4. Nothing in an Atlas is uploaded: the file is made and kept on the person's own device; any sharing is a deliberate act.
5. Rights: an Atlas of a song holds features, never the audio; it does not grant rights to the song, and the codex records no claim about ownership beyond what the person states.

## Open questions

1. Key estimation is not in the page yet (only in the scan script); the Form tier needs it.
2. Stems (drums, bass, voice) need source separation, a heavy dependency; until then seeds are whole-mix.
3. Where Atlases live: a local folder, the waypoint text, or a private store; nothing is decided.
4. Whether the mp4 picture strand belongs in the same Atlas or a paired one.

## First build (proposal)

Emit `media-atlas.v1` from the page for the loaded song (tiers 0 to 3 and 5 already exist in memory), read one back, and check the reconstitution rules 1 and 4 with a new `phosphor_atlas_check.mjs`. The mixer's two decks would then exchange Atlases instead of sharing page globals.
