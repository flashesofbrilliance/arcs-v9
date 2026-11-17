#!/usr/bin/env bash
# Build the counterpart-safe twin of a war-room report: public/recoil-ext/<id>.html.
# Non-admin visitors to /recoil/<id> are redirected there (src/app/recoil/[reportId]/page.tsx),
# so a war-room link that was sent to a counterpart still opens, without a sign-in.
# Only audience:"both" content survives; scripts/recoil_brief.py does the redaction.
# Header overrides for the external page live in the SSOT at meta.external_sets.
# Run the leak scan in .claude/skills/recoil-ship/SKILL.md (step 3) on the output before merging.
set -euo pipefail
id="$1"
cd "$(dirname "$0")/.."
src="runtime/recoil/generated/$id.json"
args=()
while IFS= read -r s; do [ -n "$s" ] && args+=(--set "$s"); done < <(python3 -c "import json,sys;[print(s) for s in json.load(open(sys.argv[1]))['meta'].get('external_sets',[])]" "$src")
./scripts/recoil --data "$src" --audience external --format html "${args[@]}" > "public/recoil-ext/$id.html"
echo "wrote public/recoil-ext/$id.html"
