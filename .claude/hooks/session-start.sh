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
  # (3a) Backlog merge driver (backlog-merge-driver-by-id, 2026-11-12): .gitattributes names
  #      merge=backlog-by-id for _QUEUE/induced-backlog.jsonl; arm its command the same way, unset -> set,
  #      a deliberate value left alone. Command lives in the script (DRIVER_CMD) so the self-test arms the same one.
  if [ -f "$_d/scripts/backlog_merge_by_id.py" ] && [ -z "$(git -C "$_d" config --get merge.backlog-by-id.driver 2>/dev/null)" ]; then
    _cmd=$(cd "$_d" && python3 -c 'import importlib.util as u;s=u.spec_from_file_location("m","scripts/backlog_merge_by_id.py");m=u.module_from_spec(s);s.loader.exec_module(m);print(m.DRIVER_CMD)' 2>/dev/null)
    [ -n "$_cmd" ] && git -C "$_d" config merge.backlog-by-id.name "backlog rows by id" 2>/dev/null \
      && git -C "$_d" config merge.backlog-by-id.driver "$_cmd" 2>/dev/null && echo "hooks: armed merge.backlog-by-id.driver"
  fi
  # (3b) Project skills/commands load from the MAIN checkout; warn when it drifts from origin/main.
  [ -x "$_d/scripts/project_skills_drift.sh" ] && "$_d/scripts/project_skills_drift.sh" "$_d" 2>/dev/null || true
  [ -f "$_d/scripts/sentries.py" ] && python3 "$_d/scripts/sentries.py" 2>/dev/null | head -12 || true
  [ "$PWD" = "$CLAUDE_PROJECT_DIR" ] && break
done

# Since 2026-10-20 the receipt logs are gitignored and pulse/snapshot are no longer rewritten here;
# only `lattice_drift_check.py --regenerate` (not run by this hook) can touch the file below.
# Cloud sessions run in throwaway containers, so anything written below is discarded with the container. Writing them there only dirties tracked files and
# trips the environment's stop-hook ("uncommitted changes") on every turn. In cloud: still run
# every check and print the readout, then restore each of these files that was clean when the
# hook started; a file already edited this session (e.g. by /handoff) is left alone. Local
# machines keep writing them as before, since there they are the real ledger.
_HOOK_STATE_FILES="runtime/specs/knowledge-lattice-v1.json"
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
# scrum master: one line only when the weekly groom is overdue (.claude/skills/scrum/SKILL.md)
python3 "$CLAUDE_PROJECT_DIR/scripts/scrum.py" nudge 2>/dev/null || true
# daily boot (2026-11-16): first session of the day gets the ritual, every thread gets the per-thread boot
python3 "$CLAUDE_PROJECT_DIR/scripts/daily_boot.py" 2>/dev/null || true
python3 "$CLAUDE_PROJECT_DIR/scripts/pulse.py" check 2>/dev/null || true

# Inchworm auditor — OPEN end (orient / red thread). Check the orphaned knowledge
# lattice for drift and emit a receipt; do NOT advance here (regeneration is the
# CLOSE end, in pre-compact). Guarded to never fail the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/lattice_drift_check.py" 2>/dev/null || true

# Seed-bank inchworm — OPEN end (ADR-055/056). Check the _SEEDS registry invariants
# (valid JSONL, orphan seeds, broken local paths, staleness, repo-coverage gap) and
# emit a receipt; curation stays human-owned. Guarded to never fail the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/seedbank_drift_check.py" 2>/dev/null || true

# Universe snapshot — OPEN end. Read-only: is the committed HUD field data stale against the tracked
# tree (the emitter's own --check), how old is its last regeneration, does the history stamp exist?
# Prints one line and appends a receipt to _INBOX/universe-snapshot-drift.jsonl (gitignored).
# Regeneration and `--refresh` (which pushes to origin/main) stay human-gated. Never fails the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/universe_snapshot_drift_check.py" 2>/dev/null || true

# PR briefs: big open PRs with no _PROPOSALS design brief, and briefs whose status contradicts their
# PR's real state (scripts/pr_brief_check.py). Read-only, one gh list plus one view per linked PR; silent when clean.
python3 "$CLAUDE_PROJECT_DIR/scripts/pr_brief_check.py" --line 2>/dev/null || true
# Findings gait — the pace line (ADR-086 part E). Read-only: prints the EXTEND/CONTRACT phase,
# open findings, displacement and the next aid station from _STATE/findings.jsonl so the
# detectors above have a place where findings get a fate and a close. Never fails the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/findings_gait.py" status 2>/dev/null | sed 's/^/findings-gait: /' || true
# JTBD graph pulse (row jtbd-graph-s3-gates): counts only, read from the last --check (_STATE/jtbd-graph/check.json,
# gitignored); no rebuild, ~50 ms. Never fails the hook.
python3 "$CLAUDE_PROJECT_DIR/scripts/universe_jtbd_adapter.py" --pulse 2>/dev/null || true
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

# Snapshot: read-only here (2026-10-20). The hook used to rewrite the mechanical git fields of the
# tracked _STATE/snapshot.json every session, which kept every checkout dirty. Only /handoff writes it;
# live git state is one `git status` away.
SNAPFILE="$CLAUDE_PROJECT_DIR/_STATE/snapshot.json"
if [ -f "$SNAPFILE" ]; then
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
    m = re.search(r'(\d{4}-\d{2}-\d{2})(?:-catchup)?\.md$', f)  # catch-ups count (missed until 2026-11-16)
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
    if days >= 8:  # weekly Sunday catch-up digest (2026-11-16); a mid-week gap is expected
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

# ADR/DEWY watcher: count pending decision candidates from the local ledger only (no transcript scan).
# Silent when there is no ledger or nothing pending. Never fails the hook.
if [ -f "$CLAUDE_PROJECT_DIR/scripts/adr_dewy_watch.py" ] && [ -f "$CLAUDE_PROJECT_DIR/_INBOX/adr-dewy-candidates.jsonl" ]; then
  pend=$(cd "$CLAUDE_PROJECT_DIR" && python3 scripts/adr_dewy_watch.py --list 2>/dev/null | head -1 || true)
  case "${pend:-}" in [1-9]*) echo "adr-dewy: $pend (review: python3 scripts/adr_dewy_watch.py --list)";; esac
fi

# Only the dependency bootstrap below is remote-only; the grounding above runs everywhere.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

if [ ! -d node_modules ] || [ ! -x node_modules/.bin/next ]; then
  npm install
fi
