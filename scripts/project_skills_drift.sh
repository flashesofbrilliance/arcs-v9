#!/bin/bash
# project_skills_drift.sh — warn when the skills/commands this session LOADED differ from origin/main.
#
# Usage:  scripts/project_skills_drift.sh [DIR]    check DIR (default: $PWD); prints nothing when clean
#         scripts/project_skills_drift.sh --self-test
#
# Why (2026-10-10): Claude Code resolves project .claude/skills and .claude/commands for a
# worktree session from the MAIN checkout, not the worktree (verified: the /night-moves text
# loaded in a worktree session matched only the main checkout's copy; the worktree-only
# skills echo-scan/page-gate and commands loops/prior-art were absent from the listing).
# When the main checkout is parked on a stale branch, every session silently runs old skills.
# Same class as AGENTS.md gotcha 14 and hookspath_arm.sh. Read-only; never fails the caller.
set -uo pipefail

check() {
  local dir="$1" common main n
  common=$(cd "$dir" && cd "$(git rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd -P) || return 0
  main=$(dirname "$common")
  [ -d "$main/.claude" ] || return 0
  n=$(git -C "$main" diff --name-only origin/main -- .claude/skills .claude/commands .claude/agents 2>/dev/null; \
      git -C "$main" ls-files --others --exclude-standard -- .claude/skills .claude/commands .claude/agents 2>/dev/null)
  n=$(printf '%s\n' "$n" | grep -c . || true)
  [ "$n" -gt 0 ] || return 0
  echo "skills-drift: WARN $n file(s) under $main/.claude/{skills,commands,agents} differ from origin/main"
  echo "skills-drift:   sessions load project skills/commands/agents from the MAIN checkout (branch $(git -C "$main" rev-parse --abbrev-ref HEAD 2>/dev/null))."
  echo "skills-drift:   fix: move the main checkout onto main (preserve dirty work first; never bare stash)."
}

if [ "${1:-}" = "--self-test" ]; then
  unset $(env | sed -n 's/^\(GIT_[A-Z_]*\)=.*/\1/p')  # a pre-commit hook's GIT_DIR would aim the scratch git at the real repo
  t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
  git init -q -b main "$t/o"; mkdir -p "$t/o/.claude/skills/x"; echo a > "$t/o/.claude/skills/x/SKILL.md"
  git -C "$t/o" add -A; git -C "$t/o" -c user.name=t -c user.email=t@t commit -qm i
  git clone -q "$t/o" "$t/m"; git -C "$t/m" worktree add -q "$t/w" -b w 2>/dev/null
  [ -z "$(check "$t/w")" ] || { echo "FAIL: clean flagged"; exit 1; }
  echo b > "$t/m/.claude/skills/x/SKILL.md"
  case "$(check "$t/w")" in *"WARN 1 file"*) ;; *) echo "FAIL: drift missed"; exit 1;; esac
  git -C "$t/m" checkout -q -- .; mkdir -p "$t/m/.claude/agents"; echo c > "$t/m/.claude/agents/new.md"
  case "$(check "$t/w")" in *"WARN 1 file"*) ;; *) echo "FAIL: agents drift missed"; exit 1;; esac
  echo "self-test: PASS (clean silent, drift flagged)"; exit 0
fi
check "${1:-$PWD}" || true
