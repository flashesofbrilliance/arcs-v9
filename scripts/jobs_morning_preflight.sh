#!/usr/bin/env bash
# jobs_morning_preflight.sh: the morning jobs loop's worktree setup + preflight
# (a) worktree at origin/main, (b) pipeline token + lane 200, (d) model health,
# as ONE command. Why one command: every scheduled run from 2026-10-16 to
# 2026-10-30 stopped at its first Bash call, a multi-line `WT=...; git ...; cd`
# block that no allow rule matches, so it waited on a permission prompt with
# nobody there (one was killed with exit 143). Check (c), the Gmail connector,
# stays with the agent: a shell cannot see MCP tools.
#
#   bash /Users/zharris/arcs-v9/.claude/worktrees/morning-jobs/scripts/jobs_morning_preflight.sh
# Prints PASS/FAIL per check and `MODEL_GATE=<ok|code>`; exits 1 if (a) or (b) fails.
set -u
MAIN=/Users/zharris/arcs-v9
WT=$MAIN/.claude/worktrees/morning-jobs
BASE=${JOBS_BASE:-https://jobs.arcs.care}
fail=0

git -C "$MAIN" fetch -q origin main 2>/dev/null
if [ -d "$WT" ]; then git -C "$WT" checkout -q --detach origin/main 2>/dev/null; else git -C "$MAIN" worktree add -q --detach "$WT" origin/main 2>/dev/null; fi
if [ "$(git -C "$WT" rev-parse HEAD 2>/dev/null)" = "$(git -C "$MAIN" rev-parse origin/main)" ]; then
  echo "PASS (a) worktree $WT at origin/main $(git -C "$WT" rev-parse --short HEAD)"
else echo "FAIL (a) worktree $WT is not at origin/main"; fail=1; fi

if [ -f "$HOME/.arcs/jobs-pipeline.env" ]; then set -a; . "$HOME/.arcs/jobs-pipeline.env"; set +a; fi
if [ -z "${JOBS_PIPELINE_TOKEN:-}" ]; then echo "FAIL (b) JOBS_PIPELINE_TOKEN not set (~/.arcs/jobs-pipeline.env)"; fail=1
else
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 30 -H "x-jobs-token: $JOBS_PIPELINE_TOKEN" "$BASE/api/jobs/lane")
  if [ "$code" = "200" ]; then echo "PASS (b) lane 200"; else echo "FAIL (b) lane returned $code"; fail=1; fi
  body=$(curl -s -m 60 -w '\n%{http_code}' -H "x-jobs-token: $JOBS_PIPELINE_TOKEN" "$BASE/api/jobs/model-health")
  mcode=$(printf '%s' "$body" | tail -n1); mjson=$(printf '%s' "$body" | sed '$d')
  if [ "$mcode" = "404" ]; then echo "PASS-UNVERIFIED (d) model-health not deployed"; echo "MODEL_GATE=ok"
  elif printf '%s' "$mjson" | grep -q '"ok":true'; then echo "PASS (d) model-health ok"; echo "MODEL_GATE=ok"
  else echo "FAIL (d) model-health $mcode: $mjson"; echo "MODEL_GATE=$(printf '%s' "$mjson" | sed -n 's/.*"code":"\([^"]*\)".*/\1/p' | head -1)"; fi
fi
echo "CHECK (c) Gmail connector: the agent must confirm search_threads is present"
exit $fail
