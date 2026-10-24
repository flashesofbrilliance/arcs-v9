# Gravity-well POLARIZE wiring: findings and hold (2026-10-20)

Row: `gravity-well-polarize-wiring`. Pre-registered before counting: FORK_SCORE_MIN = 16, FORK_MASS_MIN = 5; if a dry run would flag more than 5 clusters, stop and bring Zach the list (a threshold change needs a dated amendment and his OK). Thresholds were never changed. Nothing was emitted to `_INBOX/canon-propagation-queue.json`; nothing is wired into `scripts/canon_propagation_nightly.sh`.

## Rounds (all dry, no --emit)
1. Static snapshot `_ARTIFACTS/forensic-recoil-2026-08-27/folksonomy.json`: 12 flagged (limit 5). It is a one-time harvest with no generator.
2. JTBD graph, one cluster per job node (members = 1-hop neighbours, gravity = distinct path domains): 10 of 394 flagged. They are busy backlog rows (HUD, catalog regen, jtbd-graph s4/s5), which already have rows and specs, so a fork nudge is noise.
3. JTBD graph, folksonomy nodes only (`job:memory`, `job:pattern`, 51 nodes) with prototype edges from tool paths each note cites: 2 flagged (operator20-archaeology 7x3, jtbd-system-architecture 10x2), both architecture write-ups that already are their own documents. 21 of 51 nodes get any edge.

## Why held
- Operator 20's report has no repo or domain field, so it cannot feed the scan's gravity.
- Memory and pattern nodes have zero edges in the graph today; citing tool paths is not what makes a folksonomy cluster (themes and tags are).
- Real fix needs a new mined edge rule, amendment 11 to the graph pre-registration and a re-baselined `--check`: too heavy for a thin signal.

## Resume condition
A tag- or theme-based edge type for memory and pattern nodes (what the note says, not which scripts it cites). Then re-run the scan dry at the same thresholds; wire into the nightly script only if it flags 5 or fewer.
