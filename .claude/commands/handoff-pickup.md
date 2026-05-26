# /handoff-pickup

> Runs at the START of a new session to orient quickly without re-reading everything.
> Billing tier: SUBSCRIPTION (interactive). Zero extra cost.

## What this command does

1. Reads `.claude/arcs-session-state.md` (single source of truth for where we left off)
2. Reads the latest `## Handoff — vX.Y.Z` block in `CLAUDE.md` only
3. Confirms the last commit SHA with `git log --oneline -1`
4. Reports: what's done, what's next, what's blocked
5. Asks exactly ONE clarifying question if anything is ambiguous — then waits

## Token budget

Reads at most 3 files:
- `.claude/arcs-session-state.md`
- `CLAUDE.md` (last handoff block only — scan from bottom)
- `git log --oneline -5`

Do NOT read `MEMORY.md`, `SKILL.md`, or `WORLD.md` unless the session-state file
explicitly flags a dependency on them. They are on-demand only.

## Output format

After running, produce exactly this orientation brief:

```
ORIENTATION BRIEF — [date]
─────────────────────────────────
Last commit:     [SHA] — [message]
Active sprint:   Issue #[N] — [title]
Next action:     [one sentence — what to do first]
Blocked on:      [NONE or description]
Billing tier:    SUBSCRIPTION
─────────────────────────────────
Ready. What are we building?
```

## What NOT to do at pickup

- Do NOT read the full `MEMORY.md` history
- Do NOT re-read files already mapped in `CLAUDE.md`
- Do NOT explore the repo structure unless the session-state flags a gap
- Do NOT ask more than one question before starting work
