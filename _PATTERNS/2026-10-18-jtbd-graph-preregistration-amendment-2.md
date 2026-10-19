# JTBD graph pre-registration, amendment 2 (2026-10-18)

Amends the s2 section of `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md`. No threshold changes.
Written after counter-agent round 2 failed and before round 3 was drawn or judged.

## What was seen first
- Round 1 (seed 20261018, 1184 edges): 1 of 20 refuted (a `service` edge on a guarded `gh` call). Fail.
- Round 2 (seed 20261019, 896 edges, after the class fix): 4 of 20 refuted (cite direction x2, a route.tool
  surface that is a target not a tool, plus a guarded service class). Fail.

## Gap this closes
The original names a fresh seed (20261019) for one re-draw only. It does not say what seed a further round
uses, so choosing one after a failure would be an unregistered choice.

## Rule
Each further round after a failure adds 1 to the previous seed: round 3 uses 20261020, round 4 20261021,
and so on. Same draw method (sorted (from, type, to), stratified by inferred share). All 20 must be
confirmed; one refutation fails the round and the fix goes to the rule, never to the instance.
Every round's seed, verdicts and refutations are listed in the s2 PR body, including failed rounds.
