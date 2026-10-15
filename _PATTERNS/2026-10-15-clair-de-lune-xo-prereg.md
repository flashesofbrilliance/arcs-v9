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
