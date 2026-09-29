#!/usr/bin/env bash
# Launcher for the ARCS operator MCP bridge (stdio). Referenced by .mcp.json.
# Bootstraps operators/.venv on first run (Python >= 3.10 required by mcp 2.x).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/.venv"
if [ ! -x "$VENV/bin/python" ]; then
  PY=""
  for c in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then PY="$c"; break; fi
  done
  [ -n "$PY" ] || { echo "mcp-bridge: no Python >= 3.10 found" >&2; exit 1; }
  "$PY" -m venv "$VENV" >&2
  "$VENV/bin/pip" install -q --upgrade pip >&2
  "$VENV/bin/pip" install -q "mcp>=2" "numpy>=2.0" "scipy>=1.13" "pydantic>=2.9" >&2
fi
exec "$VENV/bin/python" "$HERE/arcs_mcp_bridge.py" "$@"
