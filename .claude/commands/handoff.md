# /handoff

> Runs the ARCS handoff protocol. Execute this at the END of every session before closing.
> Billing tier: SUBSCRIPTION (interactive). Zero extra cost.

## What this command does

1. **Captures live machine state** into `_STATE/snapshot.json` (env, deploy, DB, git)
2. Audits the current session (commits pushed, files created, decisions made)
3. Updates `MEMORY.md` with a new versioned entry at the top
4. Updates `SKILL.md` changelog if any new capabilities were added
5. Appends a new `## Handoff — vX.Y.Z` block to `CLAUDE.md`
6. Writes `.claude/arcs-session-state.md` with the current sprint snapshot
7. Commits `_STATE/snapshot.json` alongside the session commit
8. Outputs a one-shot pickup prompt the next session can use immediately

## Step 0 — Capture machine state (run FIRST, before prose)

Run these bash commands and write results into `_STATE/snapshot.json`:

```bash
git log --oneline -5
git status --short
git rev-parse HEAD
vercel ls arcs-v9 2>&1 | head -4
vercel env ls production 2>&1 | grep -E "AUTH_|DATABASE|ANTHROPIC"
```

Write `_STATE/snapshot.json` with this schema:
```json
{
  "captured_at": "<ISO timestamp>",
  "repo": "flashesofbrilliance/arcs-v9",
  "git": {
    "head_sha": "<7-char sha>",
    "head_message": "<commit message>",
    "in_sync_with_origin": true,
    "dirty_files": []
  },
  "vercel": {
    "project": "arcs-v9",
    "latest_deploy_url": "<url>",
    "latest_deploy_status": "Ready",
    "production_alias": "https://app.arcs.care",
    "env_vars_present": ["AUTH_SECRET", "AUTH_RESEND_KEY", "DATABASE_URL", "ANTHROPIC_API_KEY"]
  },
  "database": {
    "project_ref": "xbbpiryokswwvcrcutge",
    "role": "arcs_app",
    "pooler_host": "aws-1-us-east-1.pooler.supabase.com",
    "port": 6543,
    "schema_confirmed": ["User","Receipt","PrepSession","Brief","Account","Session","VerificationToken"]
  },
  "open_adrs": ["<ADR numbers with READY status in _QUEUE/PENDING.md>"],
  "session_summary": "<one sentence — what was built this session>",
  "next_action": "<one sentence — what the next session should start with>",
  "blocking": "NONE"
}
```

Then `git add _STATE/snapshot.json` and include it in the session commit.

## Step 1 — Prose handoff (existing protocol)

See: `.claude/arcs-handoff-agent.md`

## Token budget

Reads at most 6 files:
- `_STATE/snapshot.json` (to write)
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
Deploy status:      [● Ready | ● Error] — [alias url]
Env vars:           AUTH_SECRET ✓ | AUTH_RESEND_KEY ✓ | DATABASE_URL ✓ | ANTHROPIC_API_KEY ✓
DB:                 [project_ref] / [role] / [N] tables confirmed
Open sprint:        [ADR numbers or issue numbers + next unblocked]
Blocking question:  [NONE or the one thing that needs human input]
Snapshot:           _STATE/snapshot.json committed ✓
Next session start: /handoff-pickup
─────────────────────────────────
```

## When NOT to run this

- Mid-session (run only at natural stopping points)
- If no commits were pushed (nothing to log)
- If you're about to hit context limit — run `/compact` first, then `/handoff`
