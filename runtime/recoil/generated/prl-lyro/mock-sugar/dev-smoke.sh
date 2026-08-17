#!/usr/bin/env bash
# One-command off-cloud delivery smoke: boot mock-sugar, run the Create-Lead loop, tear down.
#   ./dev-smoke.sh
# Needs only Python 3 (no Docker required). Exits non-zero if any case fails.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8092}"

PORT="$PORT" python3 "$DIR/server.py" >/dev/null 2>&1 &
SRV=$!
trap 'kill "$SRV" 2>/dev/null || true' EXIT

# wait for health (max ~4s)
for _ in $(seq 1 20); do
  curl -sf "http://localhost:$PORT/healthz" >/dev/null 2>&1 && break
  sleep 0.2
done

BASE="http://localhost:$PORT" python3 "$DIR/deliver_smoke.py"
