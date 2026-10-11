<!--
session: atlas bundle observatory spec (follow-up b, supersedes the open items in the earlier fragment)
branch: claude/atlas-handoff-b
head: 735929a5
created_at: 2026-10-11T01:02:07Z
-->
## Changed
- Schema request sent to the take-home writer session ("Continue monday take-home from HANDOFF.md"); it acknowledged and queued the v1 export for after Thu 2026-10-15 17:00 ET. It will replace its older dist/atlas-bundle.json (scripts/catch_net.py) with v1 at the repo root.
- #1158 merged: spec v0.3. Red ruin paths come from a curated list kept in arcs-v9 (seed K35, K40, K42), because KINTSUGI.md has no severity or detected_at columns. A mistake with no detected_at is a point at repaired_at; one with no timestamps goes to an "unplaced" band. Receipt `2026-10-10--atlas-bundle-spec-v03-pr1158--ZH`.

## Open
1. Zach: name any ruin mistakes beyond K35, K40, K42.
2. Take-home session: build atlas-bundle.v1 after submission and send the sha.
3. Then build the admin route per runtime/specs/atlas-bundle-observatory-spec.md (v0.3), npm run build + page gate, PR, receipt.

## Next action
After 2026-10-15 17:00 ET, check for ~/ret-rfp-intelligence/atlas-bundle.json and the sha reply, then build.
