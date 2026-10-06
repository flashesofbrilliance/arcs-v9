#!/usr/bin/env bash
# scripts/vercel-debug.sh — Vercel CLI debugging wrapper
#
# Codifies friction hit while debugging the SAGE Vercel Services deploy
# (2026-06-20): `vercel curl` path/flag syntax, flaky `vercel logs`
# propagation, and the sensitive-env-var masking + git-branch-scoping
# gotchas in `vercel env`. See commit 99dc0b2 / 57f4b95 for the incident.
#
# Usage:
#   bash scripts/vercel-debug.sh curl <deployment-url> <path> [-- curl-args...]
#   bash scripts/vercel-debug.sh logs <deployment-url> [retries]
#   bash scripts/vercel-debug.sh env-check <varname> <environment> [git-branch]

set -euo pipefail

cmd="${1:-}"
shift || true

usage() {
  echo "Usage:"
  echo "  $0 curl <deployment-url> <path> [-- curl-args...]"
  echo "  $0 logs <deployment-url> [retries]"
  echo "  $0 env-check <varname> <environment> [git-branch]"
  exit 1
}

# ── curl: vercel curl wants the PATH as the positional arg, not a full URL.
#          --deployment takes the URL separately. Raw curl flags go after `--`.
cmd_curl() {
  local deployment="${1:-}"
  local path="${2:-}"
  [ -z "$deployment" ] || [ -z "$path" ] && usage
  shift 2
  if [ "${1:-}" = "--" ]; then shift; fi
  echo "→ vercel curl $path --deployment $deployment -- $*"
  vercel curl "$path" --deployment "$deployment" -- "$@"
}

# ── logs: vercel logs propagation is unreliable — empty `logs: []` on a
#          fresh request is common. Retry with --expand before giving up.
cmd_logs() {
  local deployment="${1:-}"
  local retries="${2:-5}"
  [ -z "$deployment" ] && usage
  local i=0
  while [ "$i" -lt "$retries" ]; do
    echo "--- attempt $((i+1))/$retries ---"
    out="$(vercel logs "$deployment" --expand -n 10 2>&1)"
    echo "$out"
    if echo "$out" | grep -qE "Traceback|Error|error"; then
      echo "--- found error detail, stopping ---"
      return 0
    fi
    i=$((i+1))
    sleep 4
  done
  echo "--- no error detail surfaced after $retries attempts ---"
  echo "If you need a guaranteed traceback, temporarily add a debug exception"
  echo "handler gated behind an env var set ONLY on preview (never production)."
  return 1
}

# ── env-check: `vercel env pull` ALWAYS shows sensitive vars (the default on
#               Preview/Production) as empty strings, even when correctly set.
#               This is masking, not failure — don't misread it.
#               Also: CLI `vercel deploy` does not attach git-branch metadata,
#               so a var scoped to a specific git-branch never applies to a
#               CLI-triggered deploy. Scope to "all preview branches"
#               (pass "" as the git-branch positional) unless you are only
#               ever deploying via git push.
cmd_env_check() {
  local varname="${1:-}"
  local environment="${2:-}"
  local branch="${3:-}"
  [ -z "$varname" ] || [ -z "$environment" ] && usage

  echo "Checking $varname in $environment${branch:+ (git-branch: $branch)}..."
  vercel env ls 2>&1 | grep -i "$varname" || echo "  not found in env ls — likely never added"

  echo ""
  echo "NOTE: pulling the value below will show \"\" for sensitive vars"
  echo "(default for Preview/Production) even when correctly set. Presence"
  echo "in 'env ls' above is the real signal, not the pulled value."
  local pull_args=(--environment="$environment" --yes)
  [ -n "$branch" ] && pull_args+=(--git-branch="$branch")
  vercel env pull /tmp/vercel-debug-check.env "${pull_args[@]}" 2>&1 | tail -3
  grep "^$varname=" /tmp/vercel-debug-check.env || echo "  ($varname not in pulled file)"
  rm -f /tmp/vercel-debug-check.env
}

case "$cmd" in
  curl) cmd_curl "$@" ;;
  logs) cmd_logs "$@" ;;
  env-check) cmd_env_check "$@" ;;
  *) usage ;;
esac
