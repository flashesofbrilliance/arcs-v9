#!/usr/bin/env bash
# forge_mirror_icloud.sh — mirror every built forge bundle into iCloud Drive (Files app).
# Per role, two resume versions with human-readable unique names:
#   Zach-Harris-Resume-<slug>.pdf       formatted / human-friendly (styled)
#   Zach-Harris-Resume-<slug>-ATS.txt   applicant-tracking-friendly plain text
# plus the working files (tailor notes, red-team, page). Repo _ARTIFACTS/ stays SSOT.
set -euo pipefail
DEST="${ICLOUD_RESUMES:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/ARCS/resumes}"
MAN=runtime/specs/forge-bundles.json
mkdir -p "$DEST"; n=0
while IFS='|' read -r dir slug pdf txt; do
  d=_ARTIFACTS/$dir; [ -d "$d" ] || continue
  out="$DEST/$slug"; mkdir -p "$out"
  [ -n "$pdf" ] && [ -f "$d/$pdf" ] && cp -p "$d/$pdf" "$out/Zach-Harris-Resume-$slug.pdf" && n=$((n+1))
  [ -n "$txt" ] && [ -f "$d/$txt" ] && cp -p "$d/$txt" "$out/Zach-Harris-Resume-$slug-ATS.txt" && n=$((n+1))
  for f in "$d"/TAILOR-NOTES.md "$d"/red-team.md; do [ -f "$f" ] && cp -p "$f" "$out/" && n=$((n+1)); done
done < <(python3 -c "import json;[print('|'.join([v['dir'],v['slug'],v.get('resume_pdf') or '',v.get('resume_txt') or ''])) for v in json.load(open('$MAN'))['bundles'].values()]")
echo "mirrored $n files into $DEST"
