# README as video: product sketch (2026-10-30)

Status: PROPOSED. Reference build: the Dioptra walkthrough. Rules: `_PATTERNS/2026-10-30-readme-to-video-resonance-rules.md`.

## The job

A builder has a README that is true and checked. A reviewer (hiring panel, buyer, maintainer) will give it three minutes and would
rather watch than read. Today the builder re-tells the README by hand into slides and a voiceover, and facts drift on the way: a
caveat falls off, a number gets rounded, a claim grows. The product turns the README into a short narrated video in the builder's
own voice, and proves the video says nothing the README does not.

## Inputs

- The README (and any linked README it cites), as the only source of claims.
- Optional evidence files (data, run logs, eval output) a figure may be grounded in.
- A voice: the builder's clone (ElevenLabs voice id) or their own recorded takes; system voice only for drafts.
- A register profile: audience, length target, banned words, pronunciation lexicon.
- A keep file: what is deliberately left out, with a reason.

## Stages

1. **Extract.** Parse the README into claim atoms: figures, counts, rules, results, caveats, commands. Each atom keeps its source line.
2. **Cut.** Group atoms into cards, one reviewer question per card (what, how, proof, failure, gaps, try it). Every atom is placed or
   put in the keep file; nothing is unplaced.
3. **Write.** Draft card text (for the eye) and narration (for the ear) per card in the register profile. Narration in spoken forms.
4. **Gate 1, text (free, before any audio).** Run the checker: no new figures, caveats carried, eye and ear agree, spoken forms, no
   em-dashes, word budget per card. Fails block the next stage.
5. **Voice (paid, human go).** Generate one take per card. Shows the credit cost first and waits for an explicit yes.
6. **Gate 2, audio.** Speech-to-text each take and diff it against its narration (catches skipped or invented words); check pace.
7. **Render.** Cards to frames (Playwright), each card held for exactly its take plus a pad, concatenated.
8. **Gate 3, video.** Segment duration equals take plus pad, segments newer than takes, total runtime against the target, captions
   generated from the gated narration.
9. **Ship (human go).** Local file plus a claim ledger; upload or publish only on the builder's explicit go.

## Output

- `walkthrough.mp4` and captions (`.vtt`) from the gated narration.
- A claim ledger: every README atom with where it landed (card, said, shown) or why it was omitted. This is the differentiator: the
  reviewer can audit the video against the README in one page.
- The checker report (FAIL/WARN/INFO) as a receipt.

## Why it could stand alone

Existing tools make videos from text; none treat the source as the ceiling on what the video may claim. The ledger and gates make
the video trustworthy to a skeptical reviewer, which is the reason a builder would choose it over a screen recording.

## Not built yet

Stages 1 to 3 are hand work today (the Dioptra cards and script were written by hand). Gate 1 and Gate 3 exist as
`scripts/readme_video_check.py`. Gate 2 needs a local speech-to-text model. No pricing, hosting or multi-user design.
