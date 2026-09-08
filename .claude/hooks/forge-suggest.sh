#!/usr/bin/env bash
# PostToolUse(Write) hook: when a new *-enriched-profile.json lands in runtime/recoil/generated/,
# suggest forging the 4-surface counterpart family from it. Advisory only (exit 0, no block).
file=$(printf '%s' "$CLAUDE_TOOL_INPUT" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('file_path',''))" 2>/dev/null)

case "$file" in
  *runtime/recoil/generated/*-enriched-profile.json)
    name=$(basename "$file" | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}-//; s/-enriched-profile\.json$//')
    echo "[counterpart-forge] New enriched profile detected (${name}). This is seed #1 of the recoil"
    echo "[counterpart-forge] seed. To stand up the 4-surface family (landing/recoil/codex/demo), run"
    echo "[counterpart-forge] the counterpart-forge skill: synthesize runtime/recoil/generated/<name>-forge.json"
    echo "[counterpart-forge] from this profile + the call transcript, then /forge <name>."
    ;;
esac
exit 0
