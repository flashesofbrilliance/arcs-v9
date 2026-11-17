#!/bin/bash
# project_mirror.sh: copy the context Claude Code loads in arcs-v9 (CLAUDE.md with the live handoff,
# AGENTS.md, WORLD.md), the newest night-moves digest, and a repo pulse, all from origin/main, into a
# git-excluded folder, so the scheduled night-moves run can upload them to the claude.ai Project
# "Getting Organized" (docs claude/repo/*.md). Zach, 2026-11-17: the Project should have the same
# fresh intel as Claude Code. Read-only on the repo: it never checks out, commits or edits a tracked file.
#
#   scripts/project_mirror.sh            write the five files, print their sizes
#   scripts/project_mirror.sh --self-test  build into a temp dir and check every file is non-empty
set -uo pipefail
REPO="${ARCS_REPO:-/Users/zharris/arcs-v9}"
OUT="${MIRROR_OUT:-$REPO/.claude/worktrees/project-mirror}"   # **/.claude/worktrees/ is in .git/info/exclude
[ "${1:-}" = "--self-test" ] && OUT="$(mktemp -d)"
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:/usr/bin:/bin"
mkdir -p "$OUT"
git -C "$REPO" fetch -q origin || echo "fetch failed; mirroring the last fetched origin/main"
HEAD=$(git -C "$REPO" rev-parse --short origin/main)
STAMP=$(TZ=America/New_York date '+%Y-%m-%d %H:%M %Z')
hdr() { printf '<!-- Mirrored from arcs-v9 origin/main %s at %s by scripts/project_mirror.sh. Read-only copy: edit the repo, not this doc. -->\n\n' "$HEAD" "$STAMP"; }
for f in CLAUDE.md AGENTS.md WORLD.md; do { hdr; git -C "$REPO" show "origin/main:$f"; } > "$OUT/$f"; done
NM=$(git -C "$REPO" ls-tree --name-only origin/main _STATE/night-moves/ | grep -E '/[0-9]{4}-[0-9]{2}-[0-9]{2}(-catchup)?\.md$' | sort | tail -1)
{ hdr; printf 'Newest digest on main: `%s`\n\n' "$NM"; git -C "$REPO" show "origin/main:$NM"; } > "$OUT/NIGHT-MOVES-latest.md"
SINCE=$(date -v-2d +%F 2>/dev/null || date -d '2 days ago' +%F)
{
  hdr
  echo "# Repo pulse"
  echo
  echo "origin/main: \`$HEAD\` ($(git -C "$REPO" log -1 --format='%ci' origin/main))"
  echo
  echo "## Open PRs"
  (cd "$REPO" && gh pr list --state open --limit 40 --json number,title,isDraft,updatedAt \
     --template '{{range .}}- #{{.number}}{{if .isDraft}} (draft){{end}}: {{.title}} (updated {{timefmt "2006-01-02" .updatedAt}}){{"\n"}}{{end}}') || echo "- not checked (gh failed)"
  echo
  echo "## Merged since $SINCE"
  (cd "$REPO" && gh pr list --state merged --limit 60 --search "merged:>=$SINCE" --json number,title \
     --template '{{range .}}- #{{.number}}: {{.title}}{{"\n"}}{{end}}') || echo "- not checked (gh failed)"
  echo
  echo "## Last 15 commits on main"
  git -C "$REPO" log -15 --format='- `%h` %s (%cs)' origin/main
} > "$OUT/REPO-PULSE.md"
if [ "${1:-}" = "--self-test" ]; then
  bad=0; for f in CLAUDE.md AGENTS.md WORLD.md NIGHT-MOVES-latest.md REPO-PULSE.md; do [ -s "$OUT/$f" ] || { echo "empty: $f"; bad=1; }; done
  rm -rf "$OUT"; [ $bad = 0 ] && echo "project_mirror self-test: ok"; exit $bad
fi
for f in CLAUDE.md AGENTS.md WORLD.md NIGHT-MOVES-latest.md REPO-PULSE.md; do printf '%7d %s\n' "$(wc -c < "$OUT/$f")" "$OUT/$f"; done
