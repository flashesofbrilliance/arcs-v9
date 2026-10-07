# Outcome of the Unusual Whales provenance and timing pre-registration: NOT RUN

Written 2026-10-06. Cites the registration commit `bf8c92e4` (2026-10-06 14:49:50 -0400) and merge `e8502447` of `prereg-unusual-whales-provenance-2026-10-06.md`. Docs only.

## 1. Result

**The test was not run.** The pre-registration says a partial capture is not analyzed and the test is then declared "not run" with the reason. That is what happened. No claim was graded, no z-score was computed, no row was added to the belief log, and H37 (prior 0.03) stays reserved and unscored. Nothing in this note is a finding about any account, instrument, announcement or person.

## 2. What was captured

| Window (X query, `from:` the account) | Posts seen | Status |
|---|---|---|
| since 2026-01-14 until 2026-01-15 | 101, spanning 2026-01-14 06:45 UTC to 2026-01-16 04:58 UTC | **Saved.** File `uw-capture-2026-01-14_to_2026-01-15.jsonl`, 101 lines, SHA-256 `d1abf767a6b38b532aa6a2bf223489c58c9c87e69717817f587e685f421b8abc`, kept by Zach in `~/Downloads` (not committed) |
| since 2026-01-13 until 2026-01-14 | 100, spanning 2026-01-13 05:31 UTC to 2026-01-15 04:58 UTC | Captured in the page, **not saved** (the browser blocked the second automatic download); lost on navigation |
| since 2026-01-16 until 2026-01-17 | 68, spanning 2026-01-16 11:44 UTC to 2026-01-18 04:33 UTC | Captured in the page, **not saved** (same reason); lost on navigation |
| since 2026-01-18 until 2026-01-19 | 10 | **Invalid:** the tab was hidden, so X stopped loading older posts. Discarded |
| since 2026-01-20 until 2026-01-21 | 8 | **Invalid:** same reason. Discarded |
| The remaining windows through 2026-02-02 | none | Not attempted |

Coverage: one saved window of roughly ten needed for 2026-01-14 through 2026-02-01 UTC. The saved window is not enough to answer Q1, Q2 or Q3.

## 3. Why it stopped

1. **Hidden tab.** X loads older posts only while the tab is visible and focused. The tab reported itself hidden for most of the run, and scripted scrolling then stalls. Real scrolling works but returns an image per step. The captures that were valid ran only while the browser window was in front.
2. **Blocked downloads.** The browser allowed one automatic download from the page and blocked later ones, so two good windows were lost.
3. **Output limit.** The script tool truncates its output near 1,000 characters, so reading posts back through it was not possible. Reading through the page-text tool worked but cost roughly 25,000 tokens for two days of posts.
4. **Stopped by Zach.** After repeated attempts to bring the tab to the front, Zach ended the run.

## 4. Deviations from the pre-registration, recorded before any rerun

- **Date windows.** X's `until:` includes the end date, so one query covers about two local days, cut in the browser's local timezone, not UTC. The planned fix was two-day windows from 2026-01-13 to 2026-02-02, de-duplicated by post ID and filtered to the registered UTC range by timestamp.
- **Completeness check.** The pre-registered check (compare `filter:replies` and `filter:links` variants) was replaced, before use, by a stricter one: originals plus replies must sum to the window total, and adjacent windows must agree on any shared posts. This check was not reached.
- **Capture rule kept.** A window is valid only if the tab stayed visible through the whole scroll. Invalid windows were discarded, not smoothed over.

## 5. What this note does not say

Zach was shown two post topics from the first window while the capture ran (a spouse-of-a-congressmember stock purchase claim and a Polymarket bet on a territorial acquisition). Neither was graded, traced or interpreted, and mentioning them is not a finding. Under the pre-registered rules they would be graded only after a complete capture.

## 6. If the test is rerun

1. Foreground tab confirmed visible before and after every window, with the check built into the script.
2. Browser downloads allowed for the site first, or each window written to a single file at the end.
3. Windows as in section 4, then the two checks, then grading under the original sections 3 to 6.
4. The rerun cites this file and commit `bf8c92e4`, and any further change is listed as a deviation before any post is graded.
