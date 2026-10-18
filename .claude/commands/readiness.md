---
description: Tier-4 readiness card for an induced-backlog row (door, prepared, unconfirmed, trigger, abort and undo, om gap)
---

# /readiness: how prepared is this act, before you take it

> Read-only. Wraps `scripts/readiness_packet.py`. It labels preparation and never blocks the act
> (NOTOMATION): the human releases or returns it. Only MEASURED lines are evidence.

## Do this

1. Parse the argument:
   - a row id (for example `/readiness adr-085-acceptance-redecide`): one card
   - `queue`: the ranked list of rows that reach a human
   - an optional `conviction N` (0 to 100): the human's felt certainty, used for the om gap line
2. Run one of:
   - `python3 scripts/readiness_packet.py <row-id> [--conviction N]`
   - `python3 scripts/readiness_packet.py --queue`
   Run it from your own worktree, not by the main checkout path (AGENTS.md gotcha 14).
3. Show the card as printed. Do not soften a GRAIN verdict or promote a CUE or DECLARED line to fact.
4. If no conviction was given, ask for it ONCE, as a number from 0 to 100, because the om gap line
   is UNCONFIRMED without it. Never invent it.
5. Close with ONE nudge: the cheapest missing line, named, with the single edit that fills it
   (usually `abort` or `rollback` on the row). Offer the edit; do not make it unasked.

## Row fields it reads

`door` (`one-way` or `two-way`), `abort`, `rollback`, plus the fields every row already has
(`trigger`, `gates`, `route.tool`, `depends_on`, `consent`). The optional three are specified in
`runtime/specs/backlog-status.json` under `optional_fields`. An absent field prints UNCONFIRMED.

## Verdicts

- READY: no UNCONFIRMED line, the trigger is RIPE, and the prepared, trigger and om gap lines are MEASURED
- PARTIAL: at most 2 UNCONFIRMED lines
- GRAIN: anything less. The card lists what is missing.

The suggested tier is a keyword cue, not a rule. A human-decision row can still come out as tier 2.
Run `python3 scripts/readiness_packet.py --self-test` to check the tool itself (10+ fixtures, no network).
