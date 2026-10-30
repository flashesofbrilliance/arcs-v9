# README to video: rhetorical resonance rules for a lossless translation (2026-10-30)

Prior art: memory `adaptive-rhetorical-resonance` (facts invariant, only delivery varies), `mechanical-pass-first-vibes-last`,
`context-compression-taxonomy-redactive-referential` (a video is extractive compression: lossy by omission, so every omission
must be declared), `_PATTERNS/2026-10-18-studio-offline-renderer-prereg.md` (audio-is-the-track timing checks).

Reference case: the Dioptra work sample walkthrough (8 cards, 2:40, narration in Zach's ElevenLabs voice clone, one take per card,
`build.cjs` renders cards with Playwright and times each card to its take).

## What "lossless" means here

A video cannot carry every line of a README in 2:40. Lossless therefore means: every claim, figure and caveat in the README is
either **carried** (said, shown, or both) or **declared omitted with a reason** in a keep file. Nothing is dropped silently, and
nothing is added. The register (word choice, cadence, emphasis) may change; the facts may not.

Three layers, one direction: README (the source of truth) to card text (what the eye reads) to narration (what the ear hears).
A later layer may compress an earlier one; it may never contradict or extend it.

## The rules

Each rule names its mechanical check in `scripts/readme_video_check.py` where one can be written, and says plainly where only a
person can judge.

| # | Rule | Check | Level |
|---|---|---|---|
| R0 | **One narration source.** The words in `SCRIPT.md` are the words the voice says and the words the build's fallback says. | Per card, `SCRIPT.md` text equals `build.cjs` `v` after acronym spacing is normalized. | WARN |
| R1 | **Every claim carried or declared.** Each README claim lands on a card, in the narration, or in the keep file with a reason. | Figures: see R2/R3. Caveats: see R5. Prose claims beyond figures and caveats: **human pass**, card by card against the README section it came from. | (human) |
| R2 | **No new claims.** Every figure spoken or shown exists in the source. A figure that exists only in the data or a run log (not the README) is cited on the card or added to the README first. | Numbers in narration (words parsed to digits) and on cards (digits, section labels ignored) must appear in the README; `--evidence` files downgrade a miss to WARN. Content words absent from the README are listed for a human to read as wording or new claim. | FAIL / WARN / INFO |
| R3 | **Eye and ear agree.** A figure said aloud is on the card; a count said ("six rules", "three steps") matches the list on screen. | Said-but-not-shown numbers are WARN; list items and table rows count as a shown number. Shown-but-not-said is INFO (labels, dates and code values are fine). | WARN / INFO |
| R4 | **One idea per card.** A card answers one question a reviewer would ask (what is it, how does it work, what did it do, what failed, what is missing, how do I try it). | Ceiling of 60 words or 6 sentences of narration per card. A list card (six rules) can trip it legitimately; a person confirms. | WARN |
| R5 | **Caveats travel with their claims.** Every limitation, every "not run", every "fictional data" note is carried, ideally on the same card as the claim it qualifies. Gaps are stated plainly, never softened ("not run", not "pending validation"). | Every bullet under a gaps or limitations heading, plus any sentence saying "fictional", "not a pass" or "stand-in", must be matched in the narration or cards (more than half its content words) or declared in the keep file. | FAIL |
| R6 | **Spoken forms.** Narration is written as it is said: numbers in words ("thirty five thousand dollars"), no symbols ($ % § / #), acronyms either expanded or in a pronunciation lexicon. | Any digit or symbol in narration is FAIL; every acronym is listed for the lexicon. | FAIL / INFO |
| R7 | **Register: the reader's, not ours.** Plain, declarative, calm; claims sized to the evidence; no hype words, no royal we. For a hiring panel: show what ran, what did not, and how to check. | **Human pass** (the register gauntlet). Mechanical floor: R9 plus a banned-word list if the register has one. | (human) |
| R8 | **Card time is set by narration.** Each card is on screen for its take plus a fixed tail pad, never longer, never cut. The segment is rebuilt whenever its take changes. Pace stays listenable. | Segment duration equals take duration plus pad (within 0.15 s); segment newer than its take; 1.8 to 3.4 words per second. | FAIL / WARN |
| R9 | **No em-dashes** anywhere in narration or card text. | Character scan. | FAIL |
| R10 | **Runtime fits the ask.** Total length is reported against the brief (2:40 here). | Reports total seconds and card count. | INFO |

## Run on the Dioptra case (2026-10-30)

```bash
V=<scratchpad>/vid
python3 scripts/readme_video_check.py --vid $V --readme $V/ws/SAMPLE-README.md --readme $V/ws/mcp/README.md \
  --evidence $V/ws/data/rfp_sample.txt --evidence $V/ws/data/rfp_sample_amendment_1.txt
```

Result: 10 FAIL, 3 WARN, 11 INFO. What each means:

1. **R8, cards 1 to 7: every card holds about 1.9 s of silent picture.** The audio stream is right (take plus the 0.8 s pad;
   card 1: 15.76 s), but the video stream runs 17.63 s. `ffmpeg -loop 1 ... -shortest` overshoots on a looped still image, so
   the picture outlives the narration on every card: roughly 13 s of dead air in a 2:40 cut. Fix in `build.cjs`: replace
   `-shortest` with `-t <take + pad>` from ffprobe. That re-encodes video only; it does not touch the takes or spend credits.
2. **R5: three source caveats are not carried and not declared.** "The documents are a short fictional RFP and amendment
   written for this sample" (the most material one: a reviewer could read the bid deposit card as a real solicitation),
   "Documents load at start-up only", and "stdio only, one client at a time, no auth". Either add a line (the fictional-data
   caveat fits on card 1 or 3) or declare them in a keep file with a reason (the two server limits are reasonable to omit for
   time, but it should be a decision).
3. **R2 WARN, card 3: $35,000 is not in either README.** It comes from the amendment text and the live server output shown on
   the card, so it is grounded, but a reviewer reading the README cannot find it. Adding "(the deposit rises from $20,000 to
   $35,000)" to the README's results line closes it.
4. **R4 WARN, card 4:** 7 sentences because it lists six rules. One idea (the trust rules); acceptable.
5. **R3 INFO:** $20,000 is shown but not said on card 3 (fine: the narration says "the amendment that replaced it"); "10" and
   "29" are the date on card 6.
6. **R6 INFO:** RFP, MCP, API in narration. The ElevenLabs voice says them as letters; confirm by ear once and record them in
   the lexicon.
7. **R0:** passed. `SCRIPT.md` and `build.cjs` say the same words.
8. **Not checked mechanically:** whether each take actually says its `SCRIPT.md` text (needs speech-to-text; no local ASR here,
   and the ElevenLabs transcribe call spends credits, so it was not run), and R1/R7 prose judgment.

## Keep file

Declared omissions live next to the build, for example `vid/keep.json`:

```json
{ "omit": { "stdio only": "server deployment limit; out of scope for a 2:40 walkthrough, stated in mcp/README.md" } }
```

The checker prints each declared omission as INFO so the decision stays visible.
