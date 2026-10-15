# Clair de Lune as XO: design rules and checks, written before building

Date: 2026-10-15. Premise (Zach): XO tic-tac-toe, hugs and kisses, and a warm receipt close like an embrace. Builds on the ballet's MIDI mapping in `public/pf-12d-orbital.html` (`parseMidi`, `buildForms`, `formAt`) and the animation engine in ADR-087.

## Mapping (fixed now)

- Two players, the two hands. A note at or below the median pitch of the whole piece is X, a hug, the left hand. A note above the median is O, a kiss, the right hand. The median makes the two players balanced by construction; it is not a claim about which hand played which note.
- A three by three board. Columns are the thirds of the piece in time. Rows are pitch terciles, high at the top.
- Every note onset adds one unit of ink for its player to its cell. A cell shows an X when X has ink, an O when O has ink, and an embrace ring when both do. Glyph strength is ink divided by the largest final cell count for that player, so marks grow as the piece plays.
- The form label (Moonrise, Pas de Deux, Epoch Waves, Diamond, Coda) comes from the ballet's `buildForms`, unchanged. The coda warms the board.
- Red stays out: DESIGN.md reserves it for alert. X is cyan, O is gold.
- The receipt prints only what was computed: counts, embraces, and which player, if any, owns three cells in a line.

## Checks (pass or fail)

C1. Every note is counted once: X plus O equals the number of parsed events (1,466).
C2. Determinism: the board and receipt at t = 1 are identical whether reached by scrubbing or by playing to the end.
C3. Monotonic: total ink never decreases as t increases.
C4. Rest invariant (ADR-087): the page loads at rest and equals the t = 1 state.
C5. Reduced motion: Play is hidden, stepping works, nothing plays on its own.
C6. No console errors.

## Not predicted

Whether anyone wins a line. The receipt reports it either way. The result is whatever the data gives, and a line for one hand is as acceptable as none.

## Not claimed

That the board shows musical structure well, or that viewers feel an embrace. Those need a human eye. Licensing: the composition is public domain, the performance is Bernd Krueger's under CC BY-SA 3.0 DE, and the page carries the attribution; whether ShareAlike reaches this page is unresolved.

## Amendment 1 (2026-10-15, before building): rights-clean MIDI, chapters, progressive cuts

Source swap. The Krueger performance is CC BY-SA 3.0 DE. The candidate replacement is the Mutopia Project entry "Suite Bergamasque: Clair de Lune" (piece 1778): "Copyright: Public Domain", badge "CC: No rights reserved", source edition E. Fromont 1905, maintainer Keith OHara, typeset with LilyPond 2.12.3, MIDI offered. The typesetting is not separately licensed on the page. The MIDI was downloaded once into a scratch folder (12,476 bytes, SHA-256 prefix 4eee9a1546ffde1f) and parsed read-only; nothing is committed until the owner approves the license.

Measured on that file: format 1, 3 tracks named "control track", "upper", "lower"; 1,468 note-ons; ONE distinct velocity (90) and ONE tempo (60 BPM); 9/8 time, 72 bars of 4.5 s; pitch range 27 to 97, the same as the Krueger performance.

Consequences, decided now:
- The ballet's `buildForms` cannot be used unchanged: its Diamond and Pas de Deux classes come from velocity, which is flat here. The XO page does not use velocity.
- The hands are real: X is the "lower" track, O is the "upper" track. This replaces the median-pitch split above.
- Time is the score's own: constant 60 BPM, so a note's time is its tick over 384. A rubato performance is not claimed.

Chapters are cut where the bar-level texture changes most, not from remembered bar numbers. Measure: per bar, the note count and the mean pitch. A boundary score at bar b is the change in the 4-bar mean note count (as a share of the earlier mean) plus the change in 4-bar mean pitch divided by 12. Take the top boundaries at least 5 bars apart. From the data the boundaries are bars 5, 15, 27, 35, 42, 49, 55 and 68; the six chapters used are the segments between 1, 15, 27, 42, 49 and 59, giving bars 1 to 14, 15 to 26, 27 to 41, 42 to 48, 49 to 58 and 59 to 72. Chapter names stay neutral (numerals plus a measured character such as "sparse, high register") until the score's own markings are read, which needs the LilyPond file and the owner's approval to fetch it.

Progressive cuts. Each chapter fixes one quantized cut of the board image, a bit depth and a method, from coarse to fine: chapter 1 at 1 bit, 2 at 2, 3 at 3, 4 at 4, 5 at 6, 6 at 8, with the woodblock dither on through chapter 5 and the full 8-bit cut at the close. The close is the warm embrace. The mapping is by position in the piece (a progressive refinement), not tuned to the data.

New checks.
C7. Six chapters cover bars 1 to 72 with no gap and no overlap, and each chapter's start time is the bar's tick over 384.
C8. Chapter bookmarks are keyboard-reachable and seek the scrubber to the chapter's start; the board at a chapter's start equals the board reached by playing to that time.
C9. Bit depth is non-decreasing across chapters, and at the close the cut is 8 bit (no quantization), so the final board equals the static rest page.
C10. The page contains the Mutopia attribution (source, edition, maintainer) and no performance data from the Krueger file.
