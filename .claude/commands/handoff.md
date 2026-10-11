---
description: Run the ARCS end-of-session handoff protocol (writes a handoff fragment)
disable-model-invocation: true
---

# /handoff

> Runs the ARCS handoff protocol. Execute this at the END of every session before closing.
> Billing tier: SUBSCRIPTION (interactive). Zero extra cost.

## What this command does

1. **Captures live machine state** into `_STATE/snapshot.json` (env, deploy, DB, git)
2. Audits the current session (commits pushed, files created, decisions made)
3. Updates `MEMORY.md` with a new versioned entry at the top
4. Updates `SKILL.md` changelog if any new capabilities were added
5. Writes a **handoff fragment** (`_HANDOFFS/fragments/<utc-ts>--<branch>.md`, one new file per session) via
   `scripts/handoff_fold.py new`. It does NOT edit `CLAUDE.md` and does NOT pick a version number.
   Fragments are raw material. A later `handoff_fold.py molt` (one session, ideally holding the main
   write-lock) synthesizes ALL fragments into ONE arc block, numbered by `oracle.py next handoff`
   (ADR-085 part (d) amendment, 2026-10-06)
6. Writes `.claude/arcs-session-state.md` with the current sprint snapshot
7. Commits `_STATE/snapshot.json` alongside the session commit
8. Outputs a one-shot pickup prompt the next session can use immediately

## Step -2 — Shavasana (run BEFORE anything else; Operator 25 at the handoff door)

The handoff is the session's last one-way door: once the block is written and the worktree parks,
the claims stop being editable by the mind that made them. That is the level trigger Operator 25
fires on (spec: `runtime/specs/operator-25-shavasana-v0.md`). Not a timer. The pause adds NO claim.

1. Draft the handoff block to a scratch file first (do not write CLAUDE.md yet).
2. Run the mechanical half and paste its output as the FIRST sub-block of the handoff, above the delta prose:
   ```bash
   python3 scripts/shavasana_handoff.py --draft /path/to/draft-handoff.md
   ```
   It reports the breath (exhale: commits/merges/receipts; inhale: falsifications/dissent/unconfirmed),
   the sycophancy check (agreement with no dissent on record → RETURN), and the cold re-read
   (altitude canary on the draft: sections with no ground return).
3. Attachment release (judgment, yours): re-read each claim in the draft cold. If it does not survive
   without the session's momentum, downgrade it to `what_unconfirmed` or drop it, and say which.
4. Somatic read (human, one question, only if Zach is present): certainty now vs at session start;
   any sends today? If not present, write `somatic: not asked`.
5. Disposition: release the handoff, or return it to `_QUEUE/induced-backlog.jsonl` with the block attached. Rows carry `state` (enum, `runtime/specs/backlog-status.json`) + `status_note` (prose); `python3 scripts/backlog_status_check.py` gates it.
   A block that verdicts RETURN and a handoff that ships anyway must say so in the block.

Self-test of the rule the block enforces on itself: `python3 scripts/shavasana_handoff.py --self-test`
(the block must pass the altitude canary: no confidence markers, ground returns present).

## Step -1 — Fold the progressive ledger (run FIRST)

The global Stop/PreCompact/SessionEnd hook (`~/.claude/hooks/progressive-handoff.sh`) has been
appending mechanical checkpoints to `_STATE/handoff-progress.jsonl` and you may have written
`## Delta` blocks to `_STATE/handoff-progress.md` at each compaction. Read both — they are the
session's own trail and beat reconstruction from memory:

```bash
cat _STATE/handoff-progress.md 2>/dev/null
tail -n 5 _STATE/handoff-progress.jsonl 2>/dev/null
```

Use them as the source for the handoff block below. Do NOT re-derive what they already record.

## Step 0 — Capture machine state (run before prose)

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

### Redaction rule (MANDATORY)

NEVER write a raw credential value into `_STATE/snapshot.json`, `MEMORY.md`, `CLAUDE.md`,
or any handoff prose — not even a rotated/dead one, and not even when *describing* a purge.
Mask to `prefix****` form and label what it was:
- Resend key → `re_***` ("Resend key")
- DB password → `ArcsApp****` ("arcs_app DB password")
- API keys / tokens → first 4 chars + `****`

A dead secret quoted in a handoff note becomes the cleanest-surviving copy of that token in
git history. Mask first, write second. If a prior note already spells one out, mask it in passing.

## Step 1 — Write the fragment (headed sections)

The fragment schema (`scripts/handoff_fold.py` docstring; `new` WARNS on a missing section, never blocks):

```markdown
> one-paragraph lead: what this session did
## Goal          the arc's true north (optional per fragment; molt needs one somewhere)
## Changed       - #NNN merged (`sha`); receipt 2026-10-06--slug--ZH   <- PRs/receipt ids, or it is a bookend
## State         what is true now
## Decisions     - decision made, and why
## Open          1. Zach: <decision waiting on him>   2. <other open item>
## Next action   ONE action
## Cold-start    exactly how a no-context session resumes: files, commands, tracker view
```

Debt is NOT restated: link the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection).

```bash
python3 scripts/handoff_fold.py new < /path/to/fragment.md   # prints the fragment path
git add _HANDOFFS/fragments/ && git commit ...                  # commit it with the session
```

Never write a `# Handoff — vX.Y.Z` block into `CLAUDE.md` yourself and never pick a version
(pre-commit warns). To molt (any one session, at a quiet moment, holding
`python3 scripts/write_lock.py lock acquire` if other sessions are active):

```bash
python3 scripts/handoff_fold.py list
# optional: a short arc summary / overrides in the same headings, plus ## Summary
python3 scripts/handoff_fold.py molt --input summary.md --dry-run
python3 scripts/handoff_fold.py molt --input summary.md
git add CLAUDE.md _ARCHIVE/handoffs.md _HANDOFFS/fragments/ _SEEDS/_oracle.json && git commit -m "docs(handoff): molt N fragments into vX"
```

Molt REFUSES a bookend: no Goal, no PR/receipt in What changed, not exactly one Next action, or no
Cold-start recipe. On a non-ff push rejection someone took the number: `git fetch && git reset --hard
origin/main`, re-write your fragment(s), molt again. `fold` is a deprecated alias of `molt`.

## Token budget

Reads at most 6 files:
- `_STATE/snapshot.json` (to write)
- `MEMORY.md` (to prepend new entry)
- `SKILL.md` (to check changelog)
- `_HANDOFFS/fragments/` (to write this session's fragment; CLAUDE.md is not edited)
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

## Step Ω — Claim the ledger (run LAST)

Mark the progressive trail as folded so the next session's global SessionStart hook does not
flag it as an UNCLAIMED checkpoint, then clear the prose deltas (they now live in the fragment):

```bash
python3 -c "import json,datetime; print(json.dumps({'ts':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'event':'handoff','handoff_done':True,'head':'$(git rev-parse --short HEAD)'}))" >> _STATE/handoff-progress.jsonl
: > _STATE/handoff-progress.md
```

