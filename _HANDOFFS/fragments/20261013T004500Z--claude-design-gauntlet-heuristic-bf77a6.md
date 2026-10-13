<!--
session: claude-design-gauntlet-heuristic-bf77a6
branch: claude/design-gauntlet-heuristic-bf77a6
head: 5f3d0b17
created_at: 2026-10-13T00:45:00Z
-->
> Design gauntlet and Ahmed-heuristic review of the monday take-home (127.0.0.1:8765, repo ~/ret-rfp-intelligence), read-only, relaying every finding to the take-home session as single writer; plus the explainer video v1 to v7.1, then handed the cards rig to the explainer session.

## Goal
Ship the monday.com take-home by Thu 2026-10-15 17:00 ET with every claim traceable to its log.

## Changed
- No arcs-v9 PRs from this session; all work was read-only against ~/ret-rfp-intelligence and relayed by SendMessage.
- Take-home commits that landed from this session's relays and were verified here: fbc6639/b7d6d63 (crawl fixes), 66dcd6e (P0 claims: slide 6 denominator, blind sets, hours), 0514821 (present-mode rail gutter), 7be2993 (bench fault samples reach the model), c28a5ec (Withheld label on a failed figure check), 7587f1b (slide 4 images served), ab5a276 (grade tooltips open on tap), 2c591f8 (present-mode legend band), 1302ab3 (slide 10 graded C), c282745 (present-mode rolodex).
- Explainer videos v1 to v7.1 built in the session scratchpad; the cards rig was handed to the session "Rebuild explainer as capture of deck present mode", now canonical at ~/ret-rfp-explainer-rig/cards-rig/.

## State
- Take-home submission is rc25 (ZIP = source/ + presentation/ only); final videos are in ~/ret-rfp-intelligence/dist/videos/ (rendered from rc24), old explainers moved to dist/videos/superseded/.
- Zach skipped three phone items for submission: present-mode tap targets (3-7 px letters), the landscape-preferred overlay, the phone bottom bar.
- Watchers and the port-8766 copy server are stopped.

## Decisions
- Run every check read-only against a copy of the take-home repo (port 8766) because bench runs append to its flightlog and that session is the single writer.
- Correct own errors in a new message rather than silently: the "about 3 s" flag was retracted after the e2e log showed a 3.2 s median; the v8 staleness flags were withdrawn once dist held v4.

## Open
1. After submission: the three skipped phone items, and K-numbers still visible in the Beliefs and Evals tabs.
2. Zach: a real-iPhone tap check of the grade tooltips (verified only under Chromium touch emulation).

## Next action
Zach submits rc25 by Thu 2026-10-15 17:00 ET.

## Cold
- /handoff-pickup; `git -C ~/ret-rfp-intelligence log --oneline -5`; videos in ~/ret-rfp-intelligence/dist/videos/MANIFEST.md.

### Lessons
- Verify a subagent's NOT FOUND against the repo's evidence index before relaying it (the e2e log held the "3 s" figure).
- A video that quotes the deck drifts whenever the deck changes; generate its text from the deck's own data ids.

### Notes: Shavasana

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/design-gauntlet-heuristic-bf77a6), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 3 / dissent 0 (ratio 3.0) → OK: dissent present.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Attachment release: kept all claims; each Changed sha was read in git log on ~/ret-rfp-intelligence this session. Somatic: not asked. Disposition: release.
