#!/usr/bin/env bash
# scripts/watchdog.sh — Default stop-rule for any long-running task (J21).
#
# We hand-wrote a stop-rule for the recoil run AFTER it hung ~60min. J21 makes
# the watchdog a default, not an afterthought: wrap ANY long-running command
# (workflow, agent driver, deploy-wait, scan) and it is guaranteed to terminate.
# A background task without a timeout is an unbounded-blast-radius operation
# (ADR-032) — this is the bound.
#
# Properties (ADR-032 conformance):
#   - Terminating: the timeout is the terminating guard. The wrapped command
#     CANNOT run forever; on breach it is SIGTERM'd, then SIGKILL'd after grace.
#   - Fail-safe: a missing/zero/non-numeric timeout is rejected (exit 2) rather
#     than defaulting to "no limit". No timeout is never silently "unlimited".
#   - Named signal: on breach it emits SIGNAL_WATCHDOG_TIMEOUT (greppable, like
#     smoke.sh's SIGNAL_* trips) and exits 124, distinct from the command's own
#     non-zero exits, so a caller can tell "it failed" from "it ran too long".
#   - Portable: uses coreutils `timeout` when present; falls back to a pure-bash
#     monitor+kill so it works where `timeout` is absent.
#
# Exit codes: <command's own code> on normal completion ·
#             124 = watchdog fired (SIGNAL_WATCHDOG_TIMEOUT) ·
#             2   = misuse (bad/zero timeout, or no command given).
#
# Usage:
#   bash scripts/watchdog.sh <seconds> <command> [args...]
#   WATCHDOG_TIMEOUT=1800 bash scripts/watchdog.sh -- <command> [args...]
#   WATCHDOG_GRACE=10 (seconds between SIGTERM and SIGKILL; default 10)
set -euo pipefail

GRACE="${WATCHDOG_GRACE:-10}"

# ── Parse timeout (positional first arg, or WATCHDOG_TIMEOUT with `--`) ───────
if [ "${1:-}" = "--" ]; then
  TIMEOUT="${WATCHDOG_TIMEOUT:-0}"
  shift
else
  TIMEOUT="${1:-0}"
  shift || true
fi

# Fail-safe: reject anything that isn't a positive integer. "No limit" is a bug.
case "$TIMEOUT" in
  ''|*[!0-9]*) echo "⚠ watchdog: timeout must be a positive integer of seconds (got '${TIMEOUT}'). Refusing to run unbounded." >&2; exit 2 ;;
esac
[ "$TIMEOUT" -gt 0 ] || { echo "⚠ watchdog: timeout must be > 0. Refusing to run unbounded." >&2; exit 2; }
[ "$#" -gt 0 ]      || { echo "⚠ watchdog: no command given." >&2; exit 2; }

echo "watchdog: cap=${TIMEOUT}s grace=${GRACE}s — $*" >&2

# ── Preferred path: coreutils timeout ────────────────────────────────────────
if command -v timeout >/dev/null 2>&1; then
  set +e
  timeout --kill-after="${GRACE}s" "${TIMEOUT}s" "$@"
  rc=$?
  set -e
  if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
    echo "SIGNAL_WATCHDOG_TIMEOUT: '$*' exceeded ${TIMEOUT}s — terminated." >&2
    exit 124
  fi
  exit "$rc"
fi

# ── Fallback: pure-bash monitor + kill (no coreutils timeout) ────────────────
"$@" &
cmd_pid=$!

(
  # Monitor: sleep the cap, then escalate SIGTERM -> SIGKILL if still alive.
  sleep "$TIMEOUT"
  if kill -0 "$cmd_pid" 2>/dev/null; then
    kill -TERM "$cmd_pid" 2>/dev/null || true
    sleep "$GRACE"
    kill -KILL "$cmd_pid" 2>/dev/null || true
  fi
) &
mon_pid=$!

set +e
wait "$cmd_pid"
rc=$?
set -e

# Stop the monitor if the command finished first.
kill "$mon_pid" 2>/dev/null || true
wait "$mon_pid" 2>/dev/null || true

# 143 = 128+SIGTERM, 137 = 128+SIGKILL — both mean the watchdog fired.
if [ "$rc" -eq 143 ] || [ "$rc" -eq 137 ]; then
  echo "SIGNAL_WATCHDOG_TIMEOUT: '$*' exceeded ${TIMEOUT}s — terminated." >&2
  exit 124
fi
exit "$rc"
