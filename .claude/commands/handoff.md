# /handoff

> Runs the ARCS handoff protocol. Execute this at the END of every session before closing.
> Billing tier: SUBSCRIPTION (interactive). Zero extra cost.

## What this command does

1. Audits the current session (commits pushed, files created, decisions made)
2. Updates `MEMORY.md` with a new versioned entry at the top
3. Updates `SKILL.md` changelog if any new capabilities were added
4. Appends a new `## Handoff — vX.Y.Z` block to `CLAUDE.md`
5. Writes `.claude/arcs-session-state.md` with the current sprint snapshot
6. Outputs a one-shot pickup prompt the next session can use immediately

## Full protocol

See: `.claude/arcs-handoff-agent.md`

## Token budget

This command reads at most 5 files:
- `MEMORY.md` (to prepend new entry)
- `SKILL.md` (to check changelog)
- `CLAUDE.md` (to append handoff block)
- `.claude/arcs-session-state.md` (to overwrite)
- `git log --oneline -10` (to confirm SHAs)

Do NOT read the full codebase. Do NOT explore `node_modules`. Do NOT re-read files
already in context from this session.

## Output format

After running, produce exactly this receipt:

```
HANDOFF RECEIPT — vX.Y.Z — [date]
─────────────────────────────────
Session commits:    [SHA list]
Files created:      [list or NONE]
Files modified:     [list or NONE]
Decisions logged:   [1-line each]
Open sprint:        [issue numbers + next unblocked]
Blocking question:  [NONE or the one thing that needs human input]
Next session start: /handoff-pickup
─────────────────────────────────
```

## When NOT to run this

- Mid-session (run only at natural stopping points)
- If no commits were pushed (nothing to log)
- If you're about to hit context limit — run `/compact` first, then `/handoff`
