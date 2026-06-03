# Two-Surface Protocol
### Architect ↔ Implementor State Sync

> *Version: 1.0.0 — extracted from arcs-v9 session 2026-06-03*
> *Tone: instrument, not dashboard. Read WORLD.md first.*

---

## What this is

A lightweight, zero-infrastructure pattern for maintaining stateful context between two Claude Code surfaces — one operating as **Architect** (decision authority, cloud session) and one as **Implementor** (execution authority, local session) — without re-deriving system state on every session start.

No external database. No MCP server. No auth. Just files in git and a GitHub raw URL.

---

## The primitives

### 1. `_STATE/snapshot.json` — ground truth

A machine-readable file committed to the repo's `main` branch after every session. Contains the live system state the Implementor verified: git SHA, deploy URL/status, env vars present, DB project/role/tables, next action, blocking question.

```json
{
  "captured_at": "ISO timestamp",
  "repo": "org/repo",
  "git": {
    "head_sha": "abc1234",
    "head_message": "last commit message",
    "in_sync_with_origin": true,
    "dirty_files": []
  },
  "vercel": {
    "project": "project-name",
    "latest_deploy_url": "https://...",
    "latest_deploy_status": "Ready",
    "production_alias": "https://your-domain.com",
    "env_vars_present": ["KEY_1", "KEY_2"]
  },
  "database": {
    "project_ref": "supabase-ref",
    "role": "app_role",
    "pooler_host": "aws-region.pooler.supabase.com",
    "port": 6543,
    "schema_confirmed": ["Table1", "Table2"]
  },
  "open_adrs": ["ADR-NNN description"],
  "session_summary": "one sentence — what landed this session",
  "next_action": "one sentence — what the next session starts with",
  "blocking": "NONE or description"
}
```

### 2. Cloud environment Setup script — injection point

Runs before Claude Code launches in every new cloud session. Fetches the snapshot and saves it to a known path:

```bash
curl -s "https://raw.githubusercontent.com/ORG/REPO/main/_STATE/snapshot.json" \
  > /tmp/REPO-snapshot.json \
  && echo "snapshot loaded" \
  || echo "snapshot fetch failed (non-blocking)"
```

### 3. `$SNAPSHOT_PATH` env var — pointer

```
REPO_SNAPSHOT_PATH=/tmp/REPO-snapshot.json
```

Set in the cloud environment's Environment Variables. Any command reads `cat $REPO_SNAPSHOT_PATH` instead of running curl.

### 4. `/handoff` — Implementor closes session

1. Runs bash to capture live state
2. Writes `_STATE/snapshot.json`
3. Commits + pushes to `main`
4. Writes prose to CLAUDE.md + session-state.md

### 5. `/handoff-pickup` — both surfaces open session

**Implementor (local):**
```bash
cat _STATE/snapshot.json
git log --oneline -1
```

**Architect (cloud):**
```bash
cat "${SNAPSHOT_PATH:-/tmp/snapshot.json}" \
  || curl -s "https://raw.githubusercontent.com/ORG/REPO/main/_STATE/snapshot.json"
```

Falls back to curl for resumed sessions where the setup script didn't re-run.

---

## Deployment topology

```
Implementor session ends
  └─ /handoff
       ├─ captures: git SHA, vercel status, env vars, DB tables
       ├─ writes: _STATE/snapshot.json
       └─ commits + pushes → origin/main

                         ↓ GitHub

Architect session starts (new container)
  └─ Setup script fires
       └─ curl → raw.githubusercontent.com/ORG/REPO/main/_STATE/snapshot.json
            └─ saves → $SNAPSHOT_PATH

  └─ /handoff-pickup
       └─ cat $SNAPSHOT_PATH
            ├─ reads: next_action, blocking, deploy status, env vars
            └─ orients without re-deriving anything
```

---

## Replication — wiring a new project

**Step 1: Add `_STATE/snapshot.json` to the repo**
```bash
mkdir -p _STATE
echo '{"captured_at":"","repo":"ORG/REPO","session_summary":"initial","next_action":"TBD","blocking":"NONE"}' \
  > _STATE/snapshot.json
git add _STATE/snapshot.json
git commit -m "feat(sync): init state snapshot"
git push
```

**Step 2: Update cloud environment Setup script**
Add one line per project:
```bash
curl -s "https://raw.githubusercontent.com/ORG/REPO/main/_STATE/snapshot.json" > /tmp/REPO-snapshot.json
```

**Step 3: Add env var**
```
REPO_SNAPSHOT_PATH=/tmp/REPO-snapshot.json
```

**Step 4: Update your pickup command**
```bash
cat "${REPO_SNAPSHOT_PATH:-/tmp/REPO-snapshot.json}" 2>/dev/null \
  || curl -s "https://raw.githubusercontent.com/ORG/REPO/main/_STATE/snapshot.json"
```

Done. New sessions for this project now start with verified live state.

---

## Constraints and known limits

| Constraint | Detail |
|---|---|
| Read-only from Architect | No GitHub MCP → Architect can read snapshot, can't commit back to the repo |
| Stale on resumed sessions | Setup script only fires at container creation. Resumed sessions fall back to curl. |
| Snapshot lag | Snapshot reflects the *end* of the last Implementor session, not real-time state |
| CLI `vercel env pull` bug | v53.1.0 returns empty for encrypted vars — upgrade to 54.7.1+ via Homebrew |
| `_STATE/` must not be gitignored | Easy mistake — verify after adding |

---

## When GitHub MCP goes GA

Add to cloud environment:
```bash
claude mcp add --scope user --transport http github "https://mcp.github.com/mcp"
```

This gives the Architect surface native read/write on any authorized repo — the snapshot becomes the *fallback* rather than the *primary* mechanism. The pattern still works; it just gains bidirectional write capability.

---

## Pattern registry

This pattern is registered in `_PATTERNS/` in `arcs-v9`. To apply it to a new repo, run:
```
/init-state-sync
```
(see `~/.claude/commands/init-state-sync.md`)
