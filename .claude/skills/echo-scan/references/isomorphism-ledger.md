# The isomorphism ledger: schema and labelling test

## Row schema
| # | Field-side result | ARCS counterpart (real path) | Kind | Design rule it carries |
|---|---|---|---|---|
| I1 | one result, one sentence | file, primitive, or measured gap | MECHANISM or METAPHOR | an imperative a builder could follow |

## The labelling test
Call it MECHANISM only if all three hold:
1. **Same constraint.** Both sides are limited by the same structural thing (a rate, a
   capacity, a reversibility condition, a noise source), not just described with similar words.
2. **Rule transfers.** The field's fix, restated without its vocabulary, is a concrete instruction
   for the ARCS file named. ("Convert while the control field is on" became "write the durable
   record while the session is live.")
3. **Prediction.** If the mapping is real, something observable in ARCS follows (a failure mode
   you can find in the logs, a metric that should move). That prediction seeds the kill
   condition in stage 5.

Fails any one: METAPHOR. Keep it if it is a useful lens or a caution, and say what it is good
for. Never derive an invention from a METAPHOR row alone.

## Common false matches
- **Shared vocabulary.** "Coherence", "entropy", "resonance", "memory" appear in both worlds
  and mean different things. A word match is not a constraint match.
- **Exotic advantage.** Quantum or biological results with exponential or emergent gains rarely
  carry the gain across; often the *direction* transfers and the magnitude does not. Say so in
  the row.
- **Reverse fitting.** Starting from an ARCS feature and hunting for physics to dignify it.
  Map from the field to ARCS, not back.

## Reference rows (2026-10-03 run)
- MECHANISM: dark-state polariton transfer must be adiabatic -> write durable records during
  the session, not at its end (ADR candidate Part A, Witness).
- MECHANISM: atomic frequency comb fixes recall time at write -> receipts carry a recall date
  derived from horizon (outcome capture 2/247).
- MECHANISM: quantum Zeno effect -> re-check schedules need a ceiling as well as a floor.
- METAPHOR: negative group delay -> an aggregate metric can look impossible; inspect items.
