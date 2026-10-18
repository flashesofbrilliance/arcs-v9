#!/bin/bash
# SessionStart hook — ARCS v9
# Cloud containers boot with an empty node_modules. Install deps so the
# build, dev server, linter, and type-checker work without manual setup.
# Idempotent: npm install is a no-op when the tree already matches the lockfile.
# `postinstall` (prisma generate) runs automatically as part of npm install.
set -euo pipefail

# --- Session grounding (runs always, local + cloud; guarded to never fail the hook) ---
# (1) Ground the clock so a resumed session never confabulates the time/date.
# (2) Memory 1-1 audit: flag orphan memory files (on disk, missing from MEMORY.md index)
#     at pickup instead of discovering drift several turns in.
echo "session-start: $(date '+%Y-%m-%d %H:%M %Z')"

# (0) Never block on a prompt (2026-10-04). Desktop-launched sessions run this hook with no
#     terminal, so a git call that wants an SSH passphrase, a host-key "yes", or an HTTPS login
#     waits forever and the session never gets past the spinner. Fail fast instead: every git call
#     below (fetch, the memory timecapsule) inherits these. Existing user values are respected.
export GIT_TERMINAL_PROMPT=0
export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh -o BatchMode=yes -o ConnectTimeout=10}"
export GIT_HTTP_LOW_SPEED_LIMIT="${GIT_HTTP_LOW_SPEED_LIMIT:-1000}"
export GIT_HTTP_LOW_SPEED_TIME="${GIT_HTTP_LOW_SPEED_TIME:-15}"

# (3) Arm the pre-commit gate chain (seed-gate-hookspath-bootstrap, germinated 2026-10-04).
#     Fresh clones and every cloud container start with core.hooksPath unset, so the whole
#     scripts/git-hooks chain silently never ran (2026-10-03: commits 43a3ff9 and 248036c went in
#     ungated and an NFTT post skipped tao-coverage). Gotcha 12 said "install once" by hand; this
#     makes it automatic. Idempotent, never overrides a deliberate value, never fails the hook.
#     2026-10-05: the desktop app writes an ABSOLUTE main-checkout hooksPath into every worktree's
#     config.worktree, so worktrees ran main's (stale) gates. scripts/hookspath_arm.sh repoints that
#     per-worktree to the relative path (self-test: scripts/hookspath_arm.sh --self-test). Armed for
#     both the project dir and the session cwd, since a worktree session's cwd is the worktree.
for _d in "$CLAUDE_PROJECT_DIR" "$PWD"; do
  [ -x "$_d/scripts/hookspath_arm.sh" ] && "$_d/scripts/hookspath_arm.sh" "$_d" 2>/dev/null || true
  # (3b) Project skills/commands load from the MAIN checkout; warn when it drifts from origin/main.
  [ -x "$_d/scripts/project_skills_drift.sh" ] && "$_d/scripts/project_skills_drift.sh" "$_d" 2>/dev/null || true
  [ -f "$_d/scripts/sentries.py" ] && python3 "$_d/scripts/sentries.py" 2>/dev/null | head -12 || true
  [ "$PWD" = "$CLAUDE_PROJECT_DIR" ] && break
done

# Cloud sessions run in throwaway containers, so the receipts and snapshot refresh written
# below are discarded with the container. Writing them there only dirties tracked files and
# trips the environment's stop-hook ("uncommitted changes") on every turn. In cloud: still run
# every check and print the readout, then restore each of these files that was clean when the
# hook started; a file already edited this session (e.g. by /handoff) is left alone. Local
# machines keep writing them as before, since there they are the real ledger.
_HOOK_STATE_FILES="_INBOX/pulse.jsonl _INBOX/lattice-drift.jsonl _INBOX/seedbank-drift.jsonl _STATE/pulse.json _STATE/snapshot.json runtime/specs/knowledge-lattice-v1.json"
_CLEAN_AT_START=""
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
  for _f in $_HOOK_STATE_FILES; do
    git -C "$CLAUDE_PROJECT_DIR" ls-files --error-unmatch -- "$_f" >/dev/null 2>&1 \
      && git -C "$CLAUDE_PROJECT_DIR" diff --quiet HEAD -- "$_f" 2>/dev/null \
      && _CLEAN_AT_START="$_CLEAN_AT_START $_f"
  done
  _restore_hook_state() {
    for _f in $_CLEAN_AT_START; do
      git -C "$CLAUDE_PROJECT_DIR" checkout -- "$_f" 2>/dev/null || true
    done
  }
  trap _restore_hook_state EXIT
fi

# Pulse — the global heartbeat (Phase 0). The wall-clock twin of the git-backed oracle:
# derives each subsystem's freshness from git commit timestamps (tamper-evident OT layer),
# runs the pulse<->oracle mutual check, and ALARMS on flatline. This is the fix for the
# drift-sentry that went stale 5 days silently — a quiet operational layer now surfaces at
# pickup instead of rotting. Guarded to never fail the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/pulse.py" check 2>/dev/null || true

# Inchworm auditor — OPEN end (orient / red thread). Check the orphaned knowledge
# lattice for drift and emit a receipt; do NOT advance here (regeneration is the
# CLOSE end, in pre-compact). Guarded to never fail the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/lattice_drift_check.py" 2>/dev/null || true

# Seed-bank inchworm — OPEN end (ADR-055/056). Check the _SEEDS registry invariants
# (valid JSONL, orphan seeds, broken local paths, staleness, repo-coverage gap) and
# emit a receipt; curation stays human-owned. Guarded to never fail the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/seedbank_drift_check.py" 2>/dev/null || true

# Findings gait — the pace line (ADR-086 part E). Read-only: prints the EXTEND/CONTRACT phase,
# open findings, displacement and the next aid station from _STATE/findings.jsonl so the
# detectors above have a place where findings get a fate and a close. Never fails the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/findings_gait.py" status 2>/dev/null | sed 's/^/findings-gait: /' || true
# model drift: flag a newer Claude model per role in src/lib/claude-models.ts (advisory; free
# GET /v1/models with ANTHROPIC_API_KEY, else silent skip). Never switches a model.
python3 "$CLAUDE_PROJECT_DIR/scripts/model_drift_check.py" 2>/dev/null || true

# Memory-index inchworm — self-cataloging: orphan files auto-append into an
# "Uncurated (auto)" band rendered from their own frontmatter description (the
# SSOT for an index line). Detection + append are mechanical; curation (grouping,
# merging, retiring, size trims) stays human-owned — the script only ever ADDS.
# Replaces the old inline comm check, whose regex missed dotted filenames
# (*-v0.2-*.md) and false-positived ORPHANS. Guarded to never fail the hook.
# PINNED to origin/main's copy (2026-09-27): the hook runs from whatever worktree the session
# starts in, and 34 stale worktrees carried a pre-bare-slug script that re-catalogued all 274
# indexed memories into a 63KB Uncurated band 21 minutes after it was deleted. Falls back to the
# local copy only if origin/main is unreadable.
_MIS=$(git -C "$CLAUDE_PROJECT_DIR" show origin/main:scripts/memory_index_sync.py 2>/dev/null)
if [ -n "$_MIS" ]; then printf '%s\n' "$_MIS" | python3 - --append 2>/dev/null || true
else python3 "$CLAUDE_PROJECT_DIR/scripts/memory_index_sync.py" --append 2>/dev/null || true; fi

# Snapshot auto-refresh (mechanical fields only — local file, never committed/pushed
# by this hook). Narrative fields (session_summary, next_action, nci_counter,
# active_briefs) are NOT touched here; those require /handoff (a judgment call).
SNAPFILE="$CLAUDE_PROJECT_DIR/_STATE/snapshot.json"
if [ -f "$SNAPFILE" ]; then
  HEAD_SHA=$(git -C "$CLAUDE_PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo "")
  HEAD_MSG=$(git -C "$CLAUDE_PROJECT_DIR" log -1 --pretty=%s 2>/dev/null || echo "")
  DIRTY=$(git -C "$CLAUDE_PROJECT_DIR" status --porcelain 2>/dev/null | awk '{print $2}')
  git -C "$CLAUDE_PROJECT_DIR" fetch origin main --quiet 2>/dev/null || true
  AHEAD_BEHIND=$(git -C "$CLAUDE_PROJECT_DIR" rev-list --left-right --count HEAD...origin/main 2>/dev/null || echo "0	0")
  IN_SYNC="true"
  [ "$(echo "$AHEAD_BEHIND" | awk '{print $1+$2}')" != "0" ] && IN_SYNC="false"

  python3 -c "
import json, datetime, sys

path = '$SNAPFILE'
head_sha = '''$HEAD_SHA'''
head_msg = '''$HEAD_MSG'''
dirty = [l for l in '''$DIRTY'''.strip().splitlines() if l]
in_sync = $( [ "$IN_SYNC" = "true" ] && echo "True" || echo "False" )

try:
    d = json.load(open(path))
except Exception:
    sys.exit(0)

g = d.setdefault('git', {})
changed = (g.get('head_sha') != head_sha or g.get('dirty_files') != dirty or g.get('in_sync_with_origin') != in_sync)
g['head_sha'] = head_sha
g['head_message'] = head_msg
g['dirty_files'] = dirty
g['in_sync_with_origin'] = in_sync
g.pop('in_sync_note', None)

# git_refreshed_at is separate from captured_at: captured_at marks when the
# narrative fields (session_summary/next_action/nci_counter) were last set by
# /handoff, and must NOT be reset just because a mechanical field changed —
# otherwise every new commit would silently mask stale narrative content.
if changed:
    d['git_refreshed_at'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(path, 'w') as f:
        json.dump(d, f, indent=2)
        f.write('\n')
    print(f'snapshot: mechanical fields auto-refreshed (head={head_sha}, in_sync={in_sync})')
else:
    print('snapshot: mechanical fields already current')
" 2>/dev/null || echo "snapshot: mechanical refresh skipped (non-blocking)"

  narrative_age=$(python3 -c "
import json, datetime
try:
  d = json.load(open('$SNAPFILE'))
  cap = d.get('captured_at', '')
  cap_dt = datetime.datetime.fromisoformat(cap.replace('Z', '+00:00'))
  print((datetime.datetime.now(datetime.timezone.utc) - cap_dt).days)
except Exception:
  print('?')
" 2>/dev/null)
  if [ "$narrative_age" != "?" ] && [ "$narrative_age" -gt 3 ]; then
    echo "snapshot: narrative fields (session_summary/next_action/nci_counter) may be stale — run /handoff to refresh"
  fi
fi

# Night-moves reminder (NOT automation): prints a days-since-last-digest observation at
# pickup. Never invokes the skill itself — the digest stays something the owner chooses to
# generate. Read-only git-mtime check over _STATE/night-moves/*.md; guarded to never fail.
python3 -c "
import glob, datetime, os, re

files = glob.glob(os.path.join('$CLAUDE_PROJECT_DIR', '_STATE/night-moves/*.md'))
dates = []
for f in files:
    m = re.search(r'(\d{4}-\d{2}-\d{2})\.md$', f)
    if m:
        try:
            dates.append(datetime.date.fromisoformat(m.group(1)))
        except ValueError:
            pass

if not dates:
    print('night-moves: no digests found yet')
else:
    last = max(dates)
    days = (datetime.date.today() - last).days
    if days >= 2:
        print(f'night-moves: {days} days since last digest ({last}) — run /night-moves?')
" 2>/dev/null || true

# Tool install-state: ONE line (wired / available-not-installed / unused / duplicates / broken)
# from the cached audit. No scan and no network here (~0.1s); a cache older than 24h kicks a
# detached background refresh (the gh public-repo list is itself cached daily). Exists because
# flashesofbrilliance/token-savings-bank sat published-but-uninstalled for 7 weeks unnoticed.
python3 "$CLAUDE_PROJECT_DIR/scripts/tool_orphan_audit.py" --line 2>/dev/null || true

# (7) Timecapsule — per-session build-log commit of the memory dir (no-op if unchanged; absent-safe on other machines).
if bash /Users/zharris/.claude/projects/-Users-zharris-arcs-v9/memory-snapshots/git_autocommit.sh 2>/dev/null; then
  _tc=$(git -C /Users/zharris/.claude/projects/-Users-zharris-arcs-v9/memory rev-parse --short HEAD 2>/dev/null || true)
  [ -n "$_tc" ] && echo "timecapsule: memory build-log @ $_tc"
fi

# Only the dependency bootstrap below is remote-only; the grounding above runs everywhere.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

if [ ! -d node_modules ] || [ ! -x node_modules/.bin/next ]; then
  npm install
fi
