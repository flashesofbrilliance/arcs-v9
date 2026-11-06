#!/bin/bash
# deploy-prod.sh — always run this instead of `vercel --prod`
# 1. Enforces deploy from a clean checkout whose HEAD is origin/main (any worktree or the
#    main checkout; run it from inside the checkout you want to deploy)
# 2. Pre-flight: ensures every subdomain in next.config.ts is assigned to the project
# Usage: scripts/deploy-prod.sh [--dry-run] [extra vercel args]
#   --dry-run  run the guards and list missing domains, change nothing, exit before vercel
set -euo pipefail

PROJECT_ID="prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9"
TEAM_ID="team_narCbxUgS4eiieJKRv1QMfff"

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then DRY_RUN=1; shift; fi

CHECKOUT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "ERROR: not inside a git checkout of arcs-v9"
  exit 1
}
cd "$CHECKOUT"

git fetch -q origin main
HEAD_SHA=$(git rev-parse HEAD)
MAIN_SHA=$(git rev-parse origin/main)
if [ "$HEAD_SHA" != "$MAIN_SHA" ]; then
  echo "ERROR: $CHECKOUT is at ${HEAD_SHA:0:8}, not origin/main (${MAIN_SHA:0:8})"
  echo "       deploy from a checkout of origin/main, e.g. git switch --detach origin/main"
  exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: $CHECKOUT has uncommitted or untracked files; vercel would upload them"
  git status --short | head -10
  exit 1
fi
echo "→ Checkout $CHECKOUT is clean at origin/main (${MAIN_SHA:0:8})"

# Pin the project so a worktree without .vercel/project.json deploys to the right place
export VERCEL_ORG_ID="$TEAM_ID" VERCEL_PROJECT_ID="$PROJECT_ID"

# Pre-flight: verify and add any missing domain assignments
vercel whoami >/dev/null 2>&1 || true  # refreshes the CLI token in auth.json if it has expired
VERCEL_TOKEN=$(python3 -c "import json; print(json.load(open('/Users/zharris/Library/Application Support/com.vercel.cli/auth.json'))['token'])" 2>/dev/null || true)
if [ -z "$VERCEL_TOKEN" ]; then
  echo "WARNING: Could not read Vercel token — skipping domain pre-flight"
else
  echo "→ Pre-flight: checking domain assignments..."
  VERCEL_TOKEN="$VERCEL_TOKEN" PROJECT_ID="$PROJECT_ID" TEAM_ID="$TEAM_ID" DRY_RUN="$DRY_RUN" python3 - <<'PY'
import json, os, re, urllib.request

tok, pid, tid = os.environ["VERCEL_TOKEN"], os.environ["PROJECT_ID"], os.environ["TEAM_ID"]
dry = os.environ["DRY_RUN"] == "1"
base = f"https://api.vercel.com/v9/projects/{pid}/domains?teamId={tid}"
hdr = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}

def call(url, body=None):
    req = urllib.request.Request(url, data=body, headers=hdr, method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

configured = sorted(set(re.findall(r'value: "([^"]+\.arcs\.care)"', open("next.config.ts").read())))
assigned, until = set(), None
while True:  # paginate; the project carries more domains than one page
    try:
        page = call(base + "&limit=100" + (f"&until={until}" if until else ""))
    except urllib.error.HTTPError as e:
        print(f"  WARNING: could not list domains (HTTP {e.code}); skipping pre-flight")
        raise SystemExit(0)
    assigned |= {d["name"] for d in page.get("domains", [])}
    until = (page.get("pagination") or {}).get("next")
    if not until:
        break

missing = [d for d in configured if d not in assigned]
print(f"  {len(configured)} configured, {len(assigned)} assigned, {len(missing)} missing")
for d in missing:
    if dry:
        print(f"  (dry run) would add: {d}")
        continue
    try:
        call(base, json.dumps({"name": d}).encode())
        print(f"  + Added missing domain: {d}")
    except urllib.error.HTTPError as e:
        print(f"  ! Failed to add {d}: HTTP {e.code} {e.read().decode()[:200]}")
PY
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "✓ Dry run: guards passed; stopping before vercel --prod"
  exit 0
fi

echo "→ Deploying from origin/main..."
vercel --prod "$@"
echo "✓ Done"
