# /handoff-pickup

> Runs at the START of a new session to orient quickly without re-reading everything.
> Billing tier: SUBSCRIPTION (interactive). Zero extra cost.

## What this command does

1. **Reads `_STATE/snapshot.json`** — machine-readable ground truth (env, deploy, DB, git SHA)
2. Reads `.claude/arcs-session-state.md` — prose sprint state
3. Reads the latest `## Handoff — vX.Y.Z` block in `CLAUDE.md` only
4. Confirms live state matches snapshot: `git log --oneline -1` + `vercel ls arcs-v9 | head -3`
5. Reads `_QUEUE/PENDING.md` — surfaces READY items
6. Reports: what's done, what's next, what's blocked, what the live system looks like
7. Asks exactly ONE clarifying question if anything is ambiguous — then waits

## Step 0 — Load snapshot (run FIRST)

```bash
cat _STATE/snapshot.json 2>/dev/null || echo "NO SNAPSHOT — run /handoff first"
git log --oneline -1
vercel ls arcs-v9 2>&1 | head -3
```

Compare `snapshot.git.head_sha` to live `git log`. If they differ, note the drift.
Compare `snapshot.vercel.latest_deploy_status` to live `vercel ls`. Flag if Error.

## Token budget

Reads at most 5 files:
- `_STATE/snapshot.json` (machine state — primary source)
- `.claude/arcs-session-state.md` (prose sprint state)
- `CLAUDE.md` (last handoff block only — scan from bottom)
- `git log --oneline -5`
- `_QUEUE/PENDING.md` (READY rows only)

Do NOT read `MEMORY.md`, `SKILL.md`, or `WORLD.md` unless session-state flags a dependency.
They are on-demand only.

## Output format

After running, produce exactly this orientation brief:

```
ORIENTATION BRIEF — [date]
─────────────────────────────────
Last commit:     [SHA] — [message]
Deploy:          [● Ready | ● Error] — [alias url]
Env vars:        AUTH_SECRET ✓ | AUTH_RESEND_KEY ✓ | DATABASE_URL ✓ | ANTHROPIC_API_KEY ✓
DB:              [project_ref] / [role] — [N] tables
Snapshot drift:  [NONE | <what changed since last snapshot>]
Active sprint:   [ADR or issue — title]
Next action:     [one sentence — what to do first]
Blocked on:      [NONE or description]
─────────────────────────────────
Ready. What are we building?
```

## Dual-agent workflow

This project uses a two-surface protocol:
- **Architect** (Perplexity Space / cloud) — owns decisions, ADRs, canon, upstream audits
- **Implementor** (Claude Code local) — owns edits, commits, execution receipts

The snapshot bridges them: Architect reads `_STATE/snapshot.json` to know live system state
without re-deriving it. Implementor reads it to pick up exactly where the last session ended.

After the orientation brief, surface any drift between snapshot and live state:
> **Snapshot vs live:** [in sync | N commits ahead | deploy status changed | env drift]

Run `/dual-bar-raiser` to classify the current task and route it correctly.

## What NOT to do at pickup

- Do NOT read the full `MEMORY.md` history
- Do NOT re-read files already mapped in `CLAUDE.md`
- Do NOT explore the repo structure unless session-state flags a gap
- Do NOT ask more than one question before starting work
- Do NOT skip the snapshot read — it is the ground truth, not CLAUDE.md prose
