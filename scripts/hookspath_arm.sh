#!/bin/bash
# hookspath_arm.sh — make a checkout run ITS OWN scripts/git-hooks, never another checkout's.
#
# Usage:  scripts/hookspath_arm.sh [DIR]      arm DIR (default: $PWD); prints one line or nothing
#         scripts/hookspath_arm.sh --self-test
#
# Why (2026-10-05): the Claude desktop app's configureHooksPath reads the base repo's
# core.hooksPath, resolves a relative value against the MAIN checkout, and writes the absolute
# result into every worktree's config.worktree (on creation, and again via setConfigIfChanged on
# reopen). So every worktree ran the main checkout's pre-commit, whatever branch main was parked
# on (AGENTS.md gotcha #14 class; PR #745: kintsugi gate scored 77 vs 95 from the stale hook).
# The relative value `scripts/git-hooks` resolves inside each worktree, so each runs its own gates.
#
# Rules: unset -> arm relative (unchanged behavior). Absolute path equal to the main checkout's
# scripts/git-hooks, in a linked worktree -> repoint per-worktree to relative. Anything else is a
# deliberate value and is left alone. Never fails the caller.
set -uo pipefail

arm() {
  local dir="$1" hp gd cd main
  [ -d "$dir/scripts/git-hooks" ] || return 0
  hp=$(git -C "$dir" config --get core.hooksPath 2>/dev/null || true)
  if [ -z "$hp" ]; then
    git -C "$dir" config core.hooksPath scripts/git-hooks 2>/dev/null \
      && echo "hooks: armed core.hooksPath=scripts/git-hooks (was unset)"
    return 0
  fi
  [ "$hp" = "scripts/git-hooks" ] && return 0
  gd=$(cd "$dir" && cd "$(git rev-parse --git-dir 2>/dev/null)" 2>/dev/null && pwd -P) || return 0
  cd=$(cd "$dir" && cd "$(git rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd -P) || return 0
  main=$(dirname "$cd")
  if [ "$gd" != "$cd" ] && { [ "$hp" = "$main/scripts/git-hooks" ] || [ "$hp" = "$main/.git/hooks" ]; }; then
    git -C "$dir" config extensions.worktreeConfig true 2>/dev/null
    git -C "$dir" config --worktree core.hooksPath scripts/git-hooks 2>/dev/null \
      && echo "hooks: repointed core.hooksPath $hp -> scripts/git-hooks (main checkout's hooks are stale here)"
  else
    echo "hooks: core.hooksPath=$hp (not scripts/git-hooks; left as set)"
  fi
  return 0
}

self_test() {
  local t fail=0 out
  t=$(mktemp -d) && t=$(cd "$t" && pwd -P)
  trap 'rm -rf "$t"' RETURN
  git init -q "$t/main" && mkdir -p "$t/main/scripts/git-hooks" && touch "$t/main/scripts/git-hooks/pre-commit"
  git -C "$t/main" add -A && git -C "$t/main" -c user.name=t -c user.email=t@t commit -qm init
  git -C "$t/main" config core.hooksPath scripts/git-hooks
  git -C "$t/main" config extensions.worktreeConfig true
  git -C "$t/main" worktree add -q "$t/wt" -b wt 2>/dev/null
  chk() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }

  # 1 bad: app-style absolute main path -> repointed, per-worktree, main untouched
  git -C "$t/wt" config --worktree core.hooksPath "$t/main/scripts/git-hooks"
  out=$(arm "$t/wt"); chk "repoint message" "${out%% *}" "hooks:"
  chk "worktree resolves relative" "$(git -C "$t/wt" config --get core.hooksPath)" "scripts/git-hooks"
  chk "written per-worktree" "$(git -C "$t/wt" config --worktree --get core.hooksPath)" "scripts/git-hooks"
  chk "main untouched" "$(git -C "$t/main" config --get core.hooksPath)" "scripts/git-hooks"
  # 2 good: already relative -> silent no-op (idempotent)
  out=$(arm "$t/wt"); chk "idempotent, silent" "$out" ""
  # 3 deliberate: some other absolute path -> left as set
  git -C "$t/wt" config --worktree core.hooksPath /opt/custom-hooks
  arm "$t/wt" >/dev/null; chk "deliberate value kept" "$(git -C "$t/wt" config --get core.hooksPath)" "/opt/custom-hooks"
  # 4 main checkout with its own absolute path is not a linked worktree -> left as set
  git -C "$t/main" config core.hooksPath "$t/main/scripts/git-hooks"
  arm "$t/main" >/dev/null; chk "main checkout not repointed" "$(git -C "$t/main" config --get core.hooksPath)" "$t/main/scripts/git-hooks"
  # 5 unset -> armed relative
  git -C "$t/main" config --unset core.hooksPath; git -C "$t/wt" config --worktree --unset core.hooksPath
  arm "$t/wt" >/dev/null; chk "unset armed" "$(git -C "$t/wt" config --get core.hooksPath)" "scripts/git-hooks"
  # 6 the hook chain actually resolves inside the worktree
  chk "rev-parse --git-path hooks" "$(cd "$t/wt" && git rev-parse --git-path hooks)" "scripts/git-hooks"
  [ $fail = 0 ] && echo "self-test: PASS" || echo "self-test: FAIL"
  return $fail
}

if [ "${1:-}" = "--self-test" ]; then
  unset $(env | sed -n 's/^\(GIT_[A-Z_]*\)=.*/\1/p')  # a pre-commit hook's GIT_DIR would aim the scratch git at the real repo
  self_test; exit $?
fi
arm "${1:-$PWD}"
exit 0
