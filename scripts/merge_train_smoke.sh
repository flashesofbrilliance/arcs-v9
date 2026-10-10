#!/bin/sh
# merge_train_smoke.sh: run the Playwright smoke suite against a built worktree, with a throwaway
# Postgres in Docker. Called by merge_train.sh after the build, so the PR-time CI job (fe-smoke)
# does not have to repeat on the push to main (cost cut, 2026-10-07).
#
# Usage: scripts/merge_train_smoke.sh WORKTREE BASE_SHA
#   Exit 0: smoke passed, or nothing in BASE..HEAD can break it (no app code changed).
#   Exit 1: smoke failed, or Docker is not running (fail closed; pass --skip-smoke to merge_train.sh
#           to override on purpose).
# Mirrors the fe-smoke job in .github/workflows/ci.yml: postgres:16, prisma db push, build already
# done by the caller, npm run start, npm run test:smoke. Keep the app-code allowlist below in step
# with the `changes` job there.
set -u
WT="${1:?worktree}"; BASE="${2:?base sha}"
ALLOW='^(src|public|prisma|tests)/|^(package\.json|package-lock\.json|next\.config\.[a-z]+|tsconfig.*\.json|eslint\.config\.mjs|playwright\.config\.[a-z]+|\.github/workflows/ci\.yml)$|^scripts/(classname_guard|purpose_guard|ledger_check|state_sync_check|page_gate)\.py$'

CHANGED=$(git -C "$WT" diff --name-only "$BASE"..HEAD | grep -E "$ALLOW" || true)
if [ -z "$CHANGED" ]; then echo "merge_train_smoke: no app code changed since $BASE, skipping smoke"; exit 0; fi
[ "${MERGE_TRAIN_SMOKE_LIST:-0}" = 1 ] && { echo "$CHANGED"; exit 0; }   # self-test hook

docker info >/dev/null 2>&1 || { echo "merge_train_smoke: Docker is not running (start OrbStack), or pass --skip-smoke to merge_train.sh" >&2; exit 1; }

CID=""; SRV=""
cleanup() {
  [ -n "$SRV" ] && kill "$SRV" 2>/dev/null
  [ -n "$CID" ] && docker rm -f "$CID" >/dev/null 2>&1
  return 0
}
trap cleanup EXIT INT TERM

CID=$(docker run -d -e POSTGRES_PASSWORD=ci -e POSTGRES_DB=arcs -p 127.0.0.1::5432 postgres:16) || { echo "merge_train_smoke: could not start postgres:16" >&2; exit 1; }
DBPORT=$(docker port "$CID" 5432/tcp | head -1 | sed 's/.*://')
i=0; until docker exec "$CID" pg_isready -U postgres >/dev/null 2>&1; do
  i=$((i+1)); [ $i -gt 40 ] && { echo "merge_train_smoke: postgres never became ready" >&2; exit 1; }; sleep 1
done
# A free port for the app so a dev server on :3000 is left alone.
APPPORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])')

export DATABASE_URL="postgresql://postgres:ci@127.0.0.1:$DBPORT/arcs?sslmode=disable"
export ANTHROPIC_API_KEY="sk-ant-ci-placeholder" AUTH_SECRET="ci-placeholder-secret" AUTH_TRUST_HOST=true
export SMOKE_BASE_URL="http://127.0.0.1:$APPPORT"

( cd "$WT" && npx prisma db push --skip-generate ) >/dev/null 2>&1 || ( cd "$WT" && npx prisma db push ) || { echo "merge_train_smoke: prisma db push failed" >&2; exit 1; }
( cd "$WT" && npm run start -- -p "$APPPORT" >"$WT/.smoke-server.log" 2>&1 ) &
SRV=$!
i=0; until curl -sf "$SMOKE_BASE_URL" >/dev/null 2>&1; do
  i=$((i+1)); [ $i -gt 40 ] && { echo "merge_train_smoke: server never came up; log:" >&2; tail -20 "$WT/.smoke-server.log" >&2; exit 1; }; sleep 1
done
echo "merge_train_smoke: app on :$APPPORT, postgres on :$DBPORT, running Playwright smoke"
( cd "$WT" && npm run test:smoke ) || { echo "merge_train_smoke: smoke FAILED" >&2; exit 1; }
echo "merge_train_smoke: smoke passed"
