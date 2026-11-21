#!/bin/bash
# ADR-039 deploy cost guardrail, versioned (was an un-versioned dashboard field that
# regressed twice — see cost-leaks-ruin-vector-no-silent-toggle-regression memory).
# Wired as vercel.json services.web.ignoreCommand, but as of 2026-11-21 Vercel does NOT run it: every build log
# shows the project's dashboard "Ignored Build Step" (an old git diff with 9 excludes) instead. A top-level
# ignoreCommand is rejected when `services` is used. Until the dashboard field is set to
# `bash scripts/vercel-ignore-build.sh` (or cleared, if Vercel then falls back to the service field), this
# script is the intended rule, not the live one.
# Vercel semantics: exit 0 = skip build, exit 1 = run build. Default is BUILD (fail safe).
# Test without git: `bash scripts/vercel-ignore-build.sh --paths <file> [<file>...]`.
set -euo pipefail

if [ "${1:-}" = "--paths" ]; then
  shift
  CHANGED=$(printf '%s\n' "$@")
else
  CHANGED=$(git diff --name-only HEAD^ HEAD || true)
fi

if [ -z "$CHANGED" ]; then
  exit 1
fi

# Paths confirmed unread by the running app (grepped src/ 2026-08-02): safe to skip a
# build when a commit touches ONLY these. _DECISIONS/ and runtime/ are deliberately
# excluded from this list — both are read at request time (link-search API and the
# /recoil/[reportId] route respectively) and need a fresh deploy to serve new content.
# 2026-09-04: .gitignore added after PR #279 (docs-only + .gitignore) triggered a full production build.
# 2026-11-02 (leak audit): added _QUEUE/ _PROPOSALS/ _HANDOFFS/ _SEEDS/ docs/ tools/ tests/
# .github/ .impeccable/ WORLD.md README.md; src/ names them only in comments and GitHub links.
# Replayed on 60 main commits since 10-30: skips 29 instead of 9.
SAFE_PATTERN='^(CLAUDE\.md|MEMORY\.md|AGENTS\.md|WORLD\.md|README\.md|\.gitignore|\.claude/|\.github/|\.impeccable/|_STATE/|_ARCHIVE/|_PATTERNS/|_MEMORY/|_ARTIFACTS/|_INBOX/|_QUEUE/|_PROPOSALS/|_HANDOFFS/|_SEEDS/|docs/|tools/|tests/|scripts/)'

# Some _ARTIFACTS/ files are served at request time (the /jobs HUDs, forge bundles, the
# reading room), so they need a deploy even though the folder is otherwise safe. The list
# comes from next.config.ts outputFileTracingIncludes so it cannot drift; _ARTIFACTS/atlas/
# is added by hand because the concordance route reads a file that is not traced there.
RUNTIME_GLOBS=$(grep -oE '"\./_ARTIFACTS/[^"]+"' next.config.ts 2>/dev/null | tr -d '"' | sed -e 's#^\./##' || true)
RUNTIME_PATTERN='^_ARTIFACTS/atlas/'
# scripts/ is otherwise safe, but the build itself runs scripts/vercel-migrate-deploy.sh (vercel.json
# buildCommand) and this file is the ignore step, so a change to either must build (2026-11-21).
RUNTIME_PATTERN="$RUNTIME_PATTERN|^scripts/vercel-"
# while-read, not `for g in $RUNTIME_GLOBS`: an unquoted glob like forge-*/** expands
# against the checkout and turned into a pattern too large for grep (2026-11-02).
while IFS= read -r g; do
  [ -n "$g" ] || continue
  re=$(printf '%s' "$g" | sed -e 's/\./\\./g' -e 's/\*\*/@@/g' -e 's/\*/[^\/]*/g' -e 's/@@/.*/g')
  RUNTIME_PATTERN="$RUNTIME_PATTERN|^$re\$"
done <<< "$RUNTIME_GLOBS"

# grep exits 1 for "no match" and 2 for an error. An error must BUILD, never skip.
pick() {
  local out rc=0
  out=$(echo "$CHANGED" | grep "$1" "$2") || rc=$?
  if [ "$rc" -gt 1 ]; then echo "grep failed (exit $rc); building to be safe."; exit 1; fi
  printf '%s' "$out"
}
UNSAFE=$(pick -Ev "$SAFE_PATTERN")
RUNTIME=$(pick -E "$RUNTIME_PATTERN")

if [ -z "$UNSAFE" ] && [ -z "$RUNTIME" ]; then
  echo "All changed files are docs/state-only; skipping build."
  exit 0
fi

echo "Build-relevant files changed:"
printf '%s\n' "$UNSAFE" "$RUNTIME" | grep -v '^$' | sort -u
exit 1
