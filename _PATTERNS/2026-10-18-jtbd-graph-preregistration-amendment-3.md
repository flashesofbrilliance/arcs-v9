# JTBD graph pre-registration, amendment 3 (2026-10-18)

Amends the s2 counter-agent rule in amendment 2. No threshold changes. Written before round 7 was drawn.

## What was seen first
Round 6 (seed 20261023, 572 edges) passed 20/20. Its exhaustive checks listed 7 route-role edges with the
wrong role. Zach asked for those fixed before merge, so the rules changed after a passing round.

## Rule
Any rule change after a counter-agent round, passing or failing, voids that round for the shipping graph.
The next round uses the previous seed + 1 (round 7: 20261024) over the regenerated graph. Same draw, same
all-20 bar. The shipping graph is the one the last passing round drew from.
