---
spec: phosphor-adopt-vs-build
version: 0.1
status: DRAFT (system-design pass 2026-10-16; Zach approved adding open-source dependencies in principle; nothing adopted yet)
date: 2026-10-16
---

# Phosphor: adopt vs build

Goal (Zach, 2026-10-16): get Phosphor to a polished state faster by taking out-of-the-box, open-source pieces and writing less custom code. Zach accepts the trade-off that this adds dependencies (the repo rule "no new dependencies without asking" is now answered for this list, one adoption at a time).

## Requirements and constraints that decide the table

Functional: play and mix two songs, detect tempo and beat grid, sync without wrecking pitch, loop with slip, show the picture, run on a person's own device.
Non-functional: **offline and private** (a core check asserts no network request; the song never leaves the device); **single file** (the page and the "twin" are one HTML file, so any library is inlined, not linked); a page-size cap (now 260,000 bytes; the page is 248,171); real-time audio on the main thread.
Hard filter: the twin hands the file to other people, so a library must be **permissively licensed or file-level copyleft (MIT, Apache-2.0, BSD, MPL-2.0)**. LGPL, GPL and AGPL are out unless the licensing is reviewed (relink and network clauses are awkward in a single inlined file).
Every row's decision rule: adopt only if it beats the custom code on a **measured** harness we already have, or removes custom code with no loss on the existing checks.

## Adopt-vs-build table

Sizes are "unpacked on npm" from `npm view` on 2026-10-16 (not the minified size that would be inlined). Licenses are as the registry reports them; confirm before adopting.

| Capability | Today (custom) | Candidate | License, size | Single-file and offline fit | How to decide (measured) | Verdict |
|---|---|---|---|---|---|---|
| Test runner | 24 hand-written node scripts with my own `check()` | `@playwright/test`, **already a devDependency** (`^1.63.0`) | Apache-2.0, 28 KB | dev-only, not in the page | convert one suite (waypoint) and one flaky one (stage); keep if retries and traces remove the F-key flake | **Adopt now, zero new dependency** |
| Accessibility | page_gate (axe through the repo's own matrix), custom reach check | `@axe-core/playwright`, **already a devDependency** (4.13.0) | MPL-2.0, 47 KB | dev-only | run axe inside the same Playwright tests at each level and size | **Adopt now, zero new dependency**; keep the reach check (no standard tool hit-tests every control against a sticky header) |
| Flash and photosensitivity guard | custom, with measured results and a visible limit | none found that is open source and offline | n/a | n/a | n/a | **Keep custom** (it is the safety claim) |
| Tempo and beat detection | `detectTempo` (25 of 35 exact on synthetic tracks; real songs disagree with an independent estimator) | `realtime-bpm-analyzer` | Apache-2.0, 156 KB, no runtime dependencies | inlines as one bundle; browser Web Audio | run it through `scripts/beat_eval.mjs` and the real-song table; adopt only if exact-match on the 35 tracks rises above 25 and real songs agree better | **Bake-off, then decide** |
|  |  | `web-audio-beat-detector` | MIT, 41 KB, but depends on a broker and a **worker** package plus two runtime libraries | the worker makes it a poor fit for one HTML file | same harness | **Skip unless the harness shows a large win** |
|  |  | `essentia.js` | **AGPL-3.0**, 9.9 MB, last update 2022 | no | n/a | **Reject** |
| Time-stretch and key lock | none (Sync is varispeed) | `@soundtouchjs/core` (2.1.1) | **MPL-2.0**, 219 KB unpacked (about 44 K characters of source before minifying, so roughly 25 to 35 KB inlined; one small dependency, the Lanczos strategy) | file-level copyleft is manageable: keep the library in its own marked block with its notice | build the sync check on real songs: after Sync with the stretcher, pitch of a held note must not move (measure with an FFT peak); compare CPU cost and artifacts against varispeed | **Adopt the core, behind a Sync option**, after the real-song trial |
|  |  | `soundtouchjs` 0.3.0 | **LGPL-2.1**, 1.8 MB | licensing awkward for a shared single file | n/a | **Reject in favor of `@soundtouchjs/core`** |
| Key detection | none in the page (a numpy scan script only) | write about 40 lines (chroma plus Krumhansl profiles), or `meyda` (MIT, 543 KB, unmaintained since 2024) | MIT | meyda is large for one feature | score on the Downloads scan against hand-labelled keys | **Build** (small, deterministic) unless a labelled test says otherwise |
| Loops with slip | Sing loop pedal and sampler slices | none specific; the Web Audio `loop`, `loopStart`, `loopEnd` already exist | platform | native | acoustic render test: loop and slip timeline | **Build on the platform** (no library) |
| Audio graph and mixer | hand-built nodes (Deck gains, bus, limiter) | `tone` | MIT, 5.3 MB unpacked | far too large to inline for what we use; would replace code that works | n/a | **Do not adopt** (adds size, replaces working code) |
| Waveform drawing | custom canvas strips | `wavesurfer.js` | BSD-3-Clause, 1.5 MB | large, imposes its own UI | n/a | **Do not adopt** |
| Release | `ship_docs.sh`, receipts (manual), artifact versions | the repo's existing flow plus the `shipping-and-launch` checklist | n/a | n/a | n/a | **Reuse what exists; log the owed receipts** |

## Boundaries: single file vs the `arcs.care/hud` embed

```
                 +-------------------------------+
  mp3 / mp4 ---> |  Phosphor (single HTML file)  |  stays on the device
                 |  analysis, mixer, picture     |
                 +---------------+---------------+
                                 | emits (only on a click)
                                 v
                        waypoint text  (built)
                        media-atlas.v1 (draft: runtime/specs/media-codex-spec.md)
                                 |
                                 v
                 +-------------------------------+
                 |  arcs.care/hud (Next.js)      |  reads the file; never receives audio
                 +-------------------------------+
```

- **Contract:** the waypoint text now, the `media-atlas.v1` JSON later. The HUD reads it; the HUD never receives audio, and Phosphor never needs the HUD to run.
- **Why not merge the code:** Phosphor must stay a single offline file; the HUD is a server-rendered Next.js page. Sharing a data format keeps both simple.
- **Not decided:** whether the HUD embeds Phosphor in a frame or only reads an Atlas. `HudClient.tsx` has not been read.

## Trade-offs, plainly

- Each adopted library is inlined, so the page grows (about 25 to 35 KB for the stretcher) and the cap moves again. That is a visible cost; the alternative (a CDN script) breaks the no-network check and the twin.
- MPL-2.0 requires keeping the library's source file and notice intact; the inlined block must be marked so the sync check can see it.
- A library does not remove the need to test: every adoption goes through a measured check, or it is not adopted.

## Order (least regret first)

1. **Move the test suites onto `@playwright/test` and add axe to them** (no new dependency; removes the hand-rolled runner and the flake).
2. **Beat-detector bake-off** with `realtime-bpm-analyzer` against `beat_eval.mjs` (no adoption until it wins).
3. **Time-stretch with `@soundtouchjs/core`** behind a Sync option, after step 2, because stretch needs a trustworthy tempo.
4. Key detection (small custom function), then deck loops with slip on the platform.

## What I would revisit as it grows

The page size cap, the one-file rule (a build step that inlines vendored blocks would make this cleaner), and whether the Atlas becomes the shared contract between the decks and the HUD.
