---
name: state-sync
description: Scaffolds a two-surface state sync pattern for any repo – a committed snapshot.json that lets any session (local or cloud) restore ground-truth project state cheaply instead of re-deriving it. Run once per project.
---

# state-sync

Scaffolds the two-surface state sync pattern for any repo. Run once per project. Takes about
five minutes.

## What this does

1. Creates `_STATE/snapshot.json` with an initial schema in the current repo.
2. Outputs the setup-script line to add to your cloud/CI environment, if you use one.
3. Outputs the env var to add alongside it.
4. Creates or updates a pickup command for this repo.
5. Commits everything.

## Why

A session that starts cold (a new cloud sandbox, a teammate's first run, you three weeks later)
has to re-derive project state from scratch: what's deployed, what's in sync, what was decided
last. That's expensive and error-prone. A single committed JSON file as **ground truth** – updated
at the end of a working session, read at the start of the next one – turns that into a cheap file
read instead of a multi-step investigation.

## Step 1 – Gather project facts

Before writing anything, confirm what you're dealing with:

```bash
git remote -v                          # org/repo name
cat .vercel/project.json 2>/dev/null   # deploy project ID + name, if using Vercel
vercel ls 2>&1 | head -3                # latest deploy URL + status, if applicable
vercel env ls production 2>&1 | head    # which env vars are set, if applicable
```

Adapt these to your actual deploy target (Vercel, Netlify, a plain server, etc.) – the schema
below is deploy-target-agnostic; fill in whatever applies.

## Step 2 – Create `_STATE/snapshot.json`

```bash
mkdir -p _STATE
```

Write `_STATE/snapshot.json` with this schema (fill in from Step 1):

```json
{
  "captured_at": "<ISO timestamp now>",
  "repo": "<org/repo>",
  "git": {
    "head_sha": "<git rev-parse --short HEAD>",
    "head_message": "<git log --oneline -1, message only>",
    "in_sync_with_origin": true,
    "dirty_files": []
  },
  "deploy": {
    "target": "<vercel | netlify | server | none>",
    "project": "<project name>",
    "latest_deploy_url": "<url>",
    "latest_deploy_status": "Ready",
    "production_alias": "<custom domain or blank>",
    "env_vars_present": ["<list of env var names, never values>"]
  },
  "database": {
    "note": "fill in if the project uses a database, else remove this block"
  },
  "open_decisions": [],
  "session_summary": "state sync initialized",
  "next_action": "TBD – fill in at the end of the first real session",
  "blocking": "NONE"
}
```

Make sure `_STATE/` is not in `.gitignore`:

```bash
grep "_STATE" .gitignore && echo "WARNING: remove _STATE from gitignore"
```

**Never write a raw credential value into this file.** `env_vars_present` lists variable *names*
only, never their values.

## Step 3 – Output cloud environment config (optional)

If you run cloud/CI sessions that need this state at boot, print these two blocks for the user to
copy into their environment settings:

**Add to the setup script:**

```bash
curl -s "https://raw.githubusercontent.com/<ORG>/<REPO>/main/_STATE/snapshot.json" \
  > /tmp/<REPO>-snapshot.json \
  && echo "<REPO> snapshot loaded" \
  || echo "<REPO> snapshot fetch failed (non-blocking)"
```

**Add to environment variables:**

```
<REPO_UPPER>_SNAPSHOT_PATH=/tmp/<REPO>-snapshot.json
```

## Step 4 – Create a pickup command (if one doesn't exist)

Create `.claude/commands/state-pickup.md` (or your equivalent skill/command mechanism) with:

```markdown
# /state-pickup

## Step 0 – Load snapshot (run FIRST)

**If running locally:**
\`\`\`bash
cat _STATE/snapshot.json 2>/dev/null || echo "NO SNAPSHOT – run /state-sync first"
git log --oneline -1
\`\`\`

**If running in a cloud session:**
\`\`\`bash
cat "${<REPO_UPPER>_SNAPSHOT_PATH:-/tmp/<REPO>-snapshot.json}" 2>/dev/null \
  || curl -s "https://raw.githubusercontent.com/<ORG>/<REPO>/main/_STATE/snapshot.json"
\`\`\`

## Output format
Surface: last commit, deploy status, next_action, blocking.
Ask ONE clarifying question if ambiguous. Then wait.
```

## Step 5 – Commit

```bash
git add _STATE/snapshot.json .claude/commands/state-pickup.md
git commit -m "feat(sync): init two-surface state sync pattern"
git push origin main
```

## Done

Report:

```
STATE SYNC INITIALIZED
─────────────────────────────────
Repo:           <org/repo>
Snapshot:       _STATE/snapshot.json committed ✓
Setup script:   <line to add to cloud env, if applicable>
Env var:        <REPO_UPPER>_SNAPSHOT_PATH
Pickup command: .claude/commands/state-pickup.md ✓
─────────────────────────────────
Next: add the setup script + env var to your cloud environment settings, if used.
Then: new cloud sessions auto-load the snapshot at boot.
```

## Notes

- `_STATE/snapshot.json` should be updated at the end of every working session, not just once –
  pair this with your own end-of-session habit (a `/handoff`-style command, or just a reminder).
- The snapshot is ground truth. Prose in a `CLAUDE.md`/`AGENTS.md`/README is context, not state –
  don't let the two drift; when they disagree, the snapshot wins and the prose gets corrected.
