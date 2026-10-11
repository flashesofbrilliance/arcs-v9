<!--
session: correction to the 2026-10-10 train handoff
branch: claude/handoff-fragment-correction
head: 064d29b9
created_at: 2026-10-11T01:49:43Z
-->
## Changed
- Corrects the 2026-10-10 handoff block "merge train, neighbor scan, adr-queue fix" (fragment from #1155, now folded into CLAUDE.md). That block said #1107 and #1101 were held and needed a decision. Both had already merged on 2026-10-09: #1107 at 16:23Z as 70bd0de5 and #1101 at 18:33Z as d9c31a7a.
- #1107's fe-smoke failure (`depth slider missing` at 375, 790 and 1280) was on earlier commits of its branch; the final commit b15f5c87 passed CI and is what merged. The cause and the fix were not opened.
- #1101 needs no rebase: its branch is 0 commits ahead of main, and a trial merge of origin/main into it had no conflicts.

## Decisions
- Drop from the active handoff: "Zach: merge each PR on green CI; do not touch #1107 or #1101 yet", the open decision "decide #1107 and whether #1101 gets a rebase", and Open items 1 and 2 of the train fragment. Nothing replaces them.

## Open
1. The CLAUDE.md handoff block still carries those stale lines until the next molt. Editing CLAUDE.md directly was blocked by the integrity gate: it fails on five commit cites (44ed0c88, 5022f9b2, b5c41786, dbc9dbe1, f41067ec) and the path scripts/catch_net.py, all from other sessions' older text and not from this correction. The gate was not bypassed.

## Next action
Next molt: fold this fragment so the stale #1107 and #1101 lines drop out of the CLAUDE.md block.
