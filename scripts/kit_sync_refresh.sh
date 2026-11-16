#!/bin/sh
# kit_sync_refresh.sh: the recipe safe_merge.sh rule 3b names, as one command.
#
# Why (dreaming pass 13 T2, Zach's go 2026-11-16): rule 3b refuses a kit PR while main has kit-input
# commits it lacks, because the kit manifest and periodic table are built from the whole kit. Sessions
# were typing the fix by hand. This runs it on the current branch: merge origin/main (a merge, not a
# rebase, so the push stays a normal fast-forward and never needs force: AGENTS.md gotcha 22),
# regenerate the two kit files, commit them if they changed, push, and print the new head for
# safe_merge.sh.
#
# Run it only on a PR branch your session owns (gotcha 22). It refuses on main and on a dirty tree.
#   scripts/kit_sync_refresh.sh [--no-push]
set -e

PUSH=1
[ "$1" = "--no-push" ] && PUSH=0

BRANCH=$(git rev-parse --abbrev-ref HEAD)
[ "$BRANCH" = "main" ] || [ "$BRANCH" = "HEAD" ] && { echo "kit_sync_refresh: refusing on main or a detached HEAD; check out your PR branch" >&2; exit 1; }
# hook-written state files (session-start pulse, snapshot) do not count as uncommitted work
DIRTY=$(git status --porcelain --untracked-files=no | grep -vE '_STATE/pulse.json|_STATE/snapshot.json|public/family-roster.json' || true)
[ -n "$DIRTY" ] && { echo "kit_sync_refresh: tracked changes are uncommitted; commit them first:" >&2; echo "$DIRTY" >&2; exit 1; }

git fetch -q origin main
if ! git merge -q --no-edit origin/main; then
  echo "kit_sync_refresh: merging origin/main hit conflicts; resolve them (generated kit files: take either side, the next step regenerates them), commit, then re-run" >&2
  exit 1
fi

python3 scripts/kit_pull.py manifest
python3 scripts/kit_periodic_table.py

if [ -n "$(git status --porcelain --untracked-files=no -- src/ui-kit/kit-manifest.json _ARTIFACTS/kit-periodic-table.html src/ui-kit/kit-catalysts.jsonl)" ]; then
  git add src/ui-kit/kit-manifest.json _ARTIFACTS/kit-periodic-table.html src/ui-kit/kit-catalysts.jsonl
  git commit -q -m 'chore(kit): refresh generated kit files after merging main [NCI:SKIP kit]'
  echo "kit_sync_refresh: regenerated kit files committed"
else
  echo "kit_sync_refresh: generated kit files already current"
fi

[ "$PUSH" = 1 ] && GIT_TERMINAL_PROMPT=0 git push -q
HEAD_SHA=$(git rev-parse HEAD)
echo "kit_sync_refresh: head $HEAD_SHA"
echo "next: scripts/safe_merge.sh <pr> $HEAD_SHA"
