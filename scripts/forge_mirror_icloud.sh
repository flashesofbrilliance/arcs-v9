#!/usr/bin/env bash
# forge_mirror_icloud.sh — mirror every built forge bundle into iCloud Drive
# (Files app). Per role folder under ARCS/resumes/<slug>/ it saves:
#   - the two resume versions with human names:
#       Zach-Harris-Resume-<slug>.pdf       formatted / human-friendly
#       Zach-Harris-Resume-<slug>-ATS.txt   applicant-tracking plain text
#   - the COMPLETE bundle (staged page, tailor notes, red-team, screenshots,
#     kintsugi/cost/hiring-manager/contact JSON, the HTML source) under _bundle/
# Repo _ARTIFACTS/ stays the source of truth; iCloud is the phone-reachable copy.
# Usage: scripts/forge_mirror_icloud.sh   (idempotent; run after any forge build)
set -euo pipefail
DEST="${ICLOUD_RESUMES:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/ARCS/resumes}"
MAN=runtime/specs/forge-bundles.json
mkdir -p "$DEST"; n=0
while IFS='|' read -r dir slug pdf txt; do
  d=_ARTIFACTS/$dir; [ -d "$d" ] || continue
  out="$DEST/$slug"; mkdir -p "$out/_bundle"
  # friendly-named resumes at the top of the role folder
  [ -n "$pdf" ] && [ -f "$d/$pdf" ] && cp -p "$d/$pdf" "$out/Zach-Harris-Resume-$slug.pdf" && n=$((n+1))
  [ -n "$txt" ] && [ -f "$d/$txt" ] && cp -p "$d/$txt" "$out/Zach-Harris-Resume-$slug-ATS.txt" && n=$((n+1))
  # the complete bundle, verbatim, under _bundle/
  for f in "$d"/*; do [ -f "$f" ] && cp -p "$f" "$out/_bundle/" && n=$((n+1)); done
done < <(python3 -c "import json;[print('|'.join([v['dir'],v['slug'],v.get('resume_pdf') or '',v.get('resume_txt') or ''])) for v in json.load(open('$MAN'))['bundles'].values()]")
echo "mirrored $n files into $DEST"
