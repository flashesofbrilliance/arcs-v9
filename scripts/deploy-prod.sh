#!/bin/bash
# deploy-prod.sh — always run this instead of `vercel --prod`
# 1. Enforces deploy from the main worktree
# 2. Pre-flight: ensures every subdomain in next.config.ts is assigned to the project
set -euo pipefail

MAIN_WORKTREE="/Users/zharris/arcs-v9/.claude/worktrees/frosty-kepler-b69f51"
PROJECT_ID="prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9"
TEAM_ID="team_narCbxUgS4eiieJKRv1QMfff"

if [ ! -d "$MAIN_WORKTREE" ]; then
  echo "ERROR: Main worktree not found at $MAIN_WORKTREE"
  exit 1
fi

BRANCH=$(git -C "$MAIN_WORKTREE" branch --show-current 2>/dev/null)
if [ "$BRANCH" != "main" ]; then
  echo "ERROR: $MAIN_WORKTREE is on '$BRANCH', not main"
  exit 1
fi

cd "$MAIN_WORKTREE"

# Pre-flight: verify and add any missing domain assignments
VERCEL_TOKEN=$(python3 -c "import json; print(json.load(open('/Users/zharris/Library/Application Support/com.vercel.cli/auth.json'))['token'])" 2>/dev/null)
if [ -z "$VERCEL_TOKEN" ]; then
  echo "WARNING: Could not read Vercel token — skipping domain pre-flight"
else
  echo "→ Pre-flight: checking domain assignments..."
  CONFIGURED=$(grep -oP '(?<=value: ")[^"]+\.arcs\.care(?=")' next.config.ts 2>/dev/null || true)
  ASSIGNED=$(curl -s "https://api.vercel.com/v9/projects/$PROJECT_ID/domains?teamId=$TEAM_ID&limit=50" \
    -H "Authorization: Bearer $VERCEL_TOKEN" | \
    python3 -c "import sys,json; [print(x['name']) for x in json.load(sys.stdin).get('domains',[])]" 2>/dev/null || true)
  ADDED=0
  while IFS= read -r domain; do
    [ -z "$domain" ] && continue
    if ! echo "$ASSIGNED" | grep -qx "$domain"; then
      echo "  + Adding missing domain: $domain"
      curl -s -X POST "https://api.vercel.com/v9/projects/$PROJECT_ID/domains?teamId=$TEAM_ID" \
        -H "Authorization: Bearer $VERCEL_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$domain\"}" > /dev/null
      ADDED=$((ADDED + 1))
    fi
  done <<< "$CONFIGURED"
  [ "$ADDED" -eq 0 ] && echo "  ✓ All domains assigned" || echo "  ✓ Added $ADDED missing domain(s)"
fi

echo "→ Deploying from main..."
vercel --prod "$@"
echo "✓ Done"
