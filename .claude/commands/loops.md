# /loops: one front door for every open loop

> Zach (2026-10-04): "my memory goes faster than my mind can index." Capture is not the gap; ARCS
> already keeps ~8 stores. This is the single read over all of them. Read-only, no new store.

## Do this

1. Call `list_scheduled_tasks` (scheduled-tasks MCP). Write its result as JSON to
   `$SCRATCHPAD/scheduled.json` (the task store has no on-disk fire times, so this snapshot is
   the only honest source for "Coming up").
2. Run `python3 scripts/open_loops.py --scheduled $SCRATCHPAD/scheduled.json` and show the page
   as-is. Args: `spoken` -> add `--spoken` (about 60 seconds read aloud); `all` -> `--cap 50`;
   `json` -> `--json`.
3. Close with ONE nudge: the top item of section 1 or 2, named, with the one action that closes it.
   Never open a new loop from this command (memory `always-nudge-to-close-the-loop-before-opening-new`).
4. If the page names a "Not read:" source, say so. A silent empty section is a false zero.

## Sections (capped at 5 each, with a count of the rest)

1. Waiting on your go: open PRs mergeable with no failing check; drafts needing review
2. Closable in under 15 min: open backlog rows with `cost_prior` <= 15 min
3. Rotting: backlog past `review_by` (or no date in 21d), unclaimed checkpoints > 7d, conflicting PRs > 14d
4. Captured today, not filed: seeds planted today, `/witness` stubs not promoted
5. Coming up: one-time scheduled reminders from the snapshot

## Capture inbox rule (proposed, pending Zach)

Any idea that surfaces mid-turn becomes a `spawn_task` chip or a `/witness` stub inside the same
turn. Nothing lives only in chat. Section 4 is where those land the same day.
