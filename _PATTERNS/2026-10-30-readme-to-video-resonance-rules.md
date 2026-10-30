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

## The video kit: levels in time (APPROVED 2026-10-30, Zach)

Zach's direction: the real Field OS components induce a video UI kit with the same atomic pattern, from frame to full
video, each level a responsive, animatable element that plays in the browser and renders to MP4 from the same source
(memory `video-ui-kit-atomic-frame-to-full-video`).

The kit has two axes. **Space** is the existing kit: chips (the grammar-chips spec) up to cards and
pages. **Time** is the new one. A frame is the time atom, but in space it is already an organism (a card holding
chips). So the time levels compose space organisms; they do not replace the chip atoms.

| Time level | Atomic role | What it holds | Rule it carries | Check |
|---|---|---|---|---|
| Frame | atom | One card at one fidelity state (chips, card, render scale) | R3 eye and ear agree, R6 spoken forms, R9 | text checks per card |
| Clip | molecule | Frames plus transitions, timed to one narration take | R8 card time is the take plus the pad | segment equals take plus pad |
| Throughline | organism | The clips under one claim: SAY, SHOW and LIMIT, plus VO and music cues | R4 one idea, R5 the limit travels with its claim | strip with SAY and no LIMIT renders FAIL |
| Narrative arc | template | The order of throughlines: the six reviewer questions | R1 every claim carried or declared | claim ledger, keep file |
| Full video | page | One arc filled with one README's content | R2 no new claims, R10 runtime | the readme video checker |

Fidelity is the one cross-axis rule: a frame renders at the Y-state its evidence earns, and a clip can animate a
frame from GRAIN to SHARP only when the evidence chip arrives (the "show, don't tell" beat).

### Motion rules at every time level (DESIGN.md "Motion and safety")

- Transitions use only --dur-fast (120ms), --dur-base (240ms), --dur-sweep (1500ms) and --ease-out; no literal times or curves.
- Flash limits hold at every level: --mo-flash-max 3 per second (whole frame or any 1/16 region), --mo-lum-swing 0.10,
  --mo-pose-rate 8, --mo-hold-min 180ms, --mo-loop-min 170ms. A hard cut between clips admits the new picture over
  --mo-shutter-ms (650ms), never as a raw flash.
- Reduced motion degrades every level to held still frames: a clip becomes its last frame, a throughline its frames in order.
- Gates: motion_policy_gate.py and phosphor_guard_check.mjs on the live page; for the MP4, a frame-sampling check
  (luminance per 1/16 region per frame, flashes counted per second) so the render meets the same limits as the page.

**Ruling (Zach, 2026-10-30, "arcs-mini adopts tokens"):** arcs-mini adopts this repo's DESIGN.md motion: the --dur-fast,
--dur-base and --dur-sweep durations, the one --ease-out curve and the --mo flash limits. Its `arcs-pulse` becomes a weight or
underlight pulse, never an opacity fade. The change to @arcs/theme and @arcs/kit is backlog row arcs-mini-adopt-design-md-motion
(READY), not part of this document.

### Construction rules: /proof is the reference (Zach, 2026-10-30)

/proof (public/proof.html, generated by scripts/proof_emit.py from runtime/specs/proof-claims.json) is the model for type,
layout, density and hierarchy. It already reads as four zoom levels, and the video uses the same four:

| /proof zoom | What it shows | Video level | Rule carried into video |
|---|---|---|---|
| z0, the 5-second card | Name in mono display, one serif lede, a three-up score of mono numbers, each with a status LED | Opening frame (the hook) | One card, at most three numbers, readable in 5 seconds; the score row is the only infographic on it |
| z1, questions | The reviewer's questions as rows, a status pip per row | Narrative arc (template) | The arc is the list of questions; each question is one throughline |
| z2, claims | One bordered claim per row, date at right | Throughline (organism) | One claim per throughline, with its status shown before the evidence |
| z3, the record | Entries with a gold left rule, the evidence itself | Frames inside the clip | Evidence is shown as the record (a quote, a diff, a terminal line), never paraphrased on screen |

Type, the balance between the rhetorical NFTT voice and the monotype instrument voice, as /proof does it: mono for the
name, numbers, labels, dates and references; the serif display face (--ds-font-display) for the one lede sentence that
carries the argument; sans for every reading line. One serif sentence per screen at most, so the rhetoric lands and
the instrument stays legible. Sizes come only from the four-step ramp plus --fs-meta (0.8125rem) for references.

Layout and density: one centred card per frame at z0; full-lane rows below it; one 720px measure; hairline rules between
rows only. Information density rises one zoom level at a time and never two in a single cut.

Status vocabulary (/proof, from the kit's Y-state glyphs): ▲ shown (green), ◆ on request (cyan), ~ not yet shown (gold,
the honesty tilde). Shape carries the state; colour never does alone.

The Ahmed heuristic (memory project_ahmed_elsamadisi_polyform: "lots of information but hard to follow"): teach the
reader how to read before showing the hardest artifact. In video: the z0 card first, a legend the first time a chart or
status glyph appears (anchored to it, said aloud once), progress rather than pressure (no countdowns), and the densest
frame never first.

**Ruling (Zach, 2026-10-30, option A):** the chip grammar adopts /proof's status vocabulary: ▲ shown green, ◆ on request
cyan, ~ not yet gold. Say became ▸ (text colour), Limit ⚑ (orange), Shift Δ. The emitter's check fails if the spec and
/proof ever disagree again.

### Typography, density and layout at render (APPROVED 2026-10-30, Zach)

Today's renders do not follow these: the frame builder hard-codes seven literal px sizes (68, 34, 30, 26, 24, 22, 18) with
no _tokens.css, no ramp and no layout targets. Every rule below has a check that can fail the render.

1. **Ramp, one root.** Sizes come only from DESIGN.md's four steps: label 0.6875rem, body 0.925rem, headline 1.15rem,
   display clamp(1.5rem, 4vw, 2.4rem). The /proof reference value --fs-meta 0.8125rem is allowed for references only. A frame
   sets ONE root font size per render target (the frame scale, so 1rem fills the same share of the frame at every target);
   every size is rem from it. No literal px on any element.
2. **Roles.**
   - H1 is display. One per frame, and only on title and arc-opening frames. Mono, as /proof sets the name.
   - H2 is headline, sans 500.
   - H3 and H4 are mono labels: 700, uppercase, 0.12 to 0.16em tracking, short text only.
   - The lede is one sentence, at full width matching its heading (DESIGN.md, AGENTS.md gotcha 13). It is headline size
     in the secondary colour, as Phosphor's lede is, or the serif display face as /proof sets it, with at most one serif
     sentence per frame. Correction to the proposed rule: a lede is not body size, because neither reference sets it there.
   - Body is sans at body size.
   - Code is mono at body size in a recessed panel (elevated surface, hairline border).
   - Citation follows /proof's .ref: mono at --fs-meta in the dimmed colour, led by its status glyph (▲ shown, ◆ on request,
     ~ not yet) and the clause id, for example "▲ RFP 7.1 + A1.2". It is never italic serif. Correction: it does not use the
     say tone, which is now the text colour and means a stated claim, not a source.
   - All text at full opacity.
3. **Density.** At most about 45 words on screen per frame (memory lean-deck-one-headline-one-organism), at most 3 type sizes,
   at most 7 body lines. The on-screen reading time, at about 4 words per second, must fit inside the frame's narration take
   (R8). Density rises one zoom level per cut, never two (the /proof rule above).
4. **Layout types and breakpoints.** A frame is a responsive element with named render targets: 16:9 at 1920x1080 (the
   default), 9:16 at 1080x1920 and 1:1 at 1080x1080. The live page is swept at 360, 790, 1280 and 1440. One px --measure is set
   per target from the frame scale. Title-safe margins are 5 percent on every edge. Card edges follow AGENTS.md gotcha 13:
   a card ends where its siblings end, and the lede matches its heading.
5. **Gates at render, before encode.**
   - token_source_gate.py and the Impeccable detector run on each frame's HTML.
   - A ramp check fails any font-size that is not a ramp token or --fs-meta.
   - A density check counts words, sizes and lines per frame against rule 3.
   - motion_policy_gate.py runs on any animated frame.
   - The brand-line-producer verdict must be PASS (the apex design audit, PR 1875).
   - Not built yet: the ramp and density checks. They extend the readme video checker, which already reads the frame text.

### Text processing and punctuation (APPROVED 2026-10-30, Zach: "a professional polish for the video too")

Checked against DESIGN.md, /proof and the house copy before adding. One correction: the house copy does not use the serial
comma (/proof: "FINRA, HIPAA and GDPR"), so rule 6 keeps that.

1. **Case.** Sentence case for every heading, title and button ("Six rules, enforced in code"), never Title Case. Caps come
   only from CSS text-transform on short mono labels; the source text stays in sentence case, so captions, transcripts and
   screen readers get normal text (the chip grammar already stores tags this way: "On request", shown uppercase). No typed
   ALL CAPS anywhere.
2. **Quotes.** Curly quotes and apostrophes in rendered text; straight quotes only inside code. One ellipsis character, never
   three dots.
3. **Dashes.** Zero em-dashes (house rule). Ranges are written with "to" ("360 to 1440"). Hyphens only inside compound words.
4. **End punctuation.** Full sentences end with a period; labels, chips, table cells and stat captions do not. Never two
   spaces, never a space before punctuation.
5. **Numbers.** One format everywhere ($35,000, 12%, 5 of 5), with a non-breaking space between a number and its unit or word
   ("8 faults"). Spoken forms can differ (R6); the screen keeps the canonical form.
6. **Lists.** No serial comma ("amounts, dates and percentages"), matching the house copy; parallel grammar across siblings.
7. **Line breaks.** No widow in headings or ledes; text-wrap balance on headings and pretty on body (already in
   _PATTERNS/arcs-artifact-css-base.css).
8. **Acronyms.** Expand on first use per video, or keep them to on-screen labels people already know; spoken form per R6.
9. **Gate (R11, built).** The readme video checker now fails a frame on typed ALL CAPS runs, straight quotes outside code,
   three-dot ellipses, double spaces, a space before punctuation and Title Case headings; em-dashes stay under R9. Widows and
   non-breaking spaces need the rendered frame and are not checked yet. R11 and the brand-line-producer must both PASS before
   encode. First run on the Dioptra build: one real finding, straight quotes around the example question on card 8.
