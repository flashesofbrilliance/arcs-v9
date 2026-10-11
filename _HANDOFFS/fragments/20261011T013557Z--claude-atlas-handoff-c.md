<!--
session: atlas bundle observatory spec (follow-up c, supersedes open items in fragments a and b)
branch: claude/atlas-handoff-c
head: d494d6b3
created_at: 2026-10-11T01:35:57Z
-->
## Changed
- #1163 merged: ruin list is K35, K37, K40, K42, K44 (Zach 2026-10-10), spec v0.3.1. Told the take-home writer FYI only: keep severity null where KINTSUGI.md is silent.
- #1229 merged: spec v0.4. The build-replay booth (take-home repo, its own generator, kickoff task replay-booth-kickoff at 2026-10-15 17:30 ET) is the single source for its three flightlog lines. The observatory adds one local-only link to the booth output; no embed, no shared code. Absent output = disabled link. Receipt `2026-10-10--atlas-spec-v04-booth-link-pr1229--ZH`.
- The booth session closed before I could confirm v0.4 to it; no action needed on its side.

## Decisions
- Zach confirmed link-out in this session (a peer's relay of the same decision was not treated as his answer until he said it here).

## Open
1. Take-home writer: atlas-bundle.v1 export after 2026-10-15 17:00 ET; sends the sha.
2. Find the booth's output path once it is built.
3. Build the admin route per runtime/specs/atlas-bundle-observatory-spec.md v0.4, npm run build + page gate, PR, receipt.

## Next action
After 2026-10-15 17:00 ET, check for ~/ret-rfp-intelligence/atlas-bundle.json, then build.
