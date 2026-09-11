#!/bin/bash
# ADR-039 deploy cost guardrail, versioned (was an un-versioned dashboard field that
# regressed twice — see cost-leaks-ruin-vector-no-silent-toggle-regression memory).
# Vercel semantics: exit 0 = skip build, exit 1 = run build. Default is BUILD (fail safe).
set -euo pipefail

CHANGED=$(git diff --name-only HEAD^ HEAD || true)

if [ -z "$CHANGED" ]; then
  exit 1
fi

# Paths confirmed unread by the running app (grepped src/ 2026-08-02): safe to skip a
# build when a commit touches ONLY these. _DECISIONS/ and runtime/ are deliberately
# excluded from this list — both are read at request time (link-search API and the
# /recoil/[reportId] route respectively) and need a fresh deploy to serve new content.
# 2026-09-04: .gitignore added after PR #279 (docs-only + .gitignore) triggered a full production build.
SAFE_PATTERN='^(CLAUDE\.md|MEMORY\.md|AGENTS\.md|\.gitignore|\.claude/|_STATE/|_ARCHIVE/|_PATTERNS/|_MEMORY/|_ARTIFACTS/|_INBOX/|scripts/)'

UNSAFE=$(echo "$CHANGED" | grep -Ev "$SAFE_PATTERN" || true)

if [ -z "$UNSAFE" ]; then
  echo "All changed files are docs/state-only; skipping build."
  exit 0
fi

echo "Build-relevant files changed:"
echo "$UNSAFE"
exit 1
