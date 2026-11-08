<!--
session: claude-myally-primer-terms
branch: claude/myally-primer-terms
head: 54358b19
created_at: 2026-11-08T21:05:16Z
-->
> My Ally Step 1 session (2026-11-06 to 11-08): Step 1 yes handled end to end. Agreement v2 drafted, gauntlet-checked and Option B chosen. Step 1 tab built from the engagement record. Hub debugged with a crawl test. Proposal and Timeline taken off the site.

## Goal
Get My Ally Step 1 ($1,500 light audit and code review) signed and started, with a client site that matches the agreement and can't be shopped for competing bids.

## Changed
- PR 2063 merged (6975b5c2): Step 1 tab on myally.arcs.care rendered from `_ARTIFACTS/engagements/myally-ld/engagement.json` (engagement_render `exports` + `scripts/myally_hub_sync.py`). Receipt 2026-11-08--myally-step1-tab-pr2063--ZH.
- Branch claude/myally-hub-polish (1d101fee), folded into PR 2059 by the rev 27 session: workstream-click and fluid-column fixes, wordmark, glance tiles, `scripts/myally_hub_crawl.py`.
- Draft PR 2070 (stacked on 2059, head 54358b19): Proposal and Timeline content removed from the site; proxy stops serving /myally-proposal.html and /myally.html; Primer jargon sweep (`scripts/myally_primer_terms.py`); a crawl check that fails on any $10,000+ figure.
- Memory project_my_ally_ld_sow_scaffold updated (Nov 6 to 8).

## State
- Agreement rev 27 (Claude Doc https://claude.ai/artifact/5f7Mepg8bY7S4mogR9f4Vt) is current. The engagement record's agreement/reply/Exhibit A renders are still v2: not for sending.
- PRs open, none merged: 2059 (draft; waits on Zach's email and his lawyer's security, data, IP and AI-tools terms), 2070 (draft, after 2059), 2066 (progress band; re-sync after both).
- Nothing sent to My Ally from these sessions.

## Decisions
- Zach: Option B (mutual indemnity, NDA Connecticut courts); office hours mirror the Oct 29 email; Step 1 is five working days, not three weeks; Proposal and Timeline off the site during Step 1 (client-side passcodes rejected as not stopping sharing).

## Open
1. The rev 27 Step 1 row still says "The sprint starts the day after all three are in"; the rev 27 brief said to remove "one-week sprint". Zach to decide.
2. The engagement record's agreement and reply text are at v2; bring them to rev 27 or retire them for this client.
3. Honest proposals design session (local_b635bcfa) is working; the Harrison Wright (Crossbridge Executive) Nov 6 call is the proposed third instance.

## Next action
Zach sends the Step 1 email with agreement rev 27; then merge 2059, then 2070, re-sync 2066.

## Cold-start recipe
- Read memory project_my_ally_ld_sow_scaffold, then PR 2070's body.
