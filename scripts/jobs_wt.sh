#!/usr/bin/env bash
# jobs_wt.sh: run one morning-jobs step from the dedicated worktree, as ONE command.
# Scheduled runs start in the main checkout and every pipeline script uses
# repo-relative paths and $JOBS_PIPELINE_TOKEN; the old prompt bridged that with
# `cd "$WT"; set -a; . env; set +a` chains, which no allow rule matches, so runs
# stalled on a permission prompt. This wrapper does the cd and the env load.
#
#   bash /Users/zharris/arcs-v9/.claude/worktrees/morning-jobs/scripts/jobs_wt.sh node ./scripts/jobs_score_sweep.mjs
#   bash .../jobs_wt.sh api GET  /api/jobs/lane
#   bash .../jobs_wt.sh api POST /api/jobs/lane '{"sourceKey":"linkedin_alert_digest","fromDate":"2026-10-08","toDate":"2026-11-03"}'
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -z "${JOBS_PIPELINE_TOKEN:-}" ] && [ -f "$HOME/.arcs/jobs-pipeline.env" ]; then set -a; . "$HOME/.arcs/jobs-pipeline.env"; set +a; fi
: "${JOBS_PIPELINE_TOKEN:?JOBS_PIPELINE_TOKEN not set (~/.arcs/jobs-pipeline.env)}"
if [ "${1:-}" = "api" ]; then
  method=${2:?method}; p=${3:?path}; body=${4:-}
  base=${JOBS_BASE:-https://jobs.arcs.care}
  if [ -n "$body" ]; then exec curl -s -m 60 -X "$method" -H "x-jobs-token: $JOBS_PIPELINE_TOKEN" -H "content-type: application/json" -d "$body" "$base$p"
  else exec curl -s -m 60 -X "$method" -H "x-jobs-token: $JOBS_PIPELINE_TOKEN" "$base$p"; fi
fi
exec "$@"
