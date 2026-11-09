---
title: Engagement compounding (design, not built)
date: 2026-11-08
status: WAITING on Zach's go; nothing built
artifact: https://claude.ai/artifact/G8v6s8QTwK1HptYn39zwPN (private)
rendered: _PROPOSALS/rendered/2026-11-08-engagement-compounding.html
owner: Zach Harris
prior_art: scripts/engagement_render.py (progress + gifts, PR 2066), scripts/myally_hub_sync.py, PR 2072 honest-proposals (engagement-record-v1, proposal_lint.py), memories avoid-front-loaded-unpaid-discovery, myally-progress-log-is-claudes-job, zero-event-futures-measure-the-prior-use-rule-of-three, label-every-probability-with-its-basis, payment-terms-new-vs-existing-clients
---

# Engagement compounding

**Why.** Each client engagement so far was built by hand and kept nothing for the next one. My Ally shows the
cost: about 30 to 45 unpaid hours (calls measured; work sessions estimated from 249 commits; emails at an assumed 15
minutes each) before a $1,500 first step. Counting Step 1's 12 hours, that is roughly $25 to $35 an hour. The number
only exists because one agent dug it up once. PRL showed the same pattern earlier ($6,200 mostly on discovery). A
lesson that lives in memory and not in a check repeats.

**What.** Five additions to the engagement record so that every engagement leaves three things behind: a measured
cost of winning it, a measured gap between what I planned and what happened, and reusable parts (gift skills, a
client page, a morning check) that the next client gets for free.

**Why now.** The pieces just landed or are in review: one record per engagement (merged), the honest-proposals
v1 record format (PR 2072), and progress plus payment-released gifts (PR 2066). My Ally Step 1 starts within days,
so its actual hours can be captured from the first one instead of reconstructed. The next engagement (Louisville or
another) would otherwise copy My Ally's one-off scripts.

**How.**
- Before (now): this design. Nothing built.
- During (after your go): merge 2072, 2059, 2066 in that order, then build Move 1 and Move 2 during My Ally Step 1.
- After: Moves 3 to 5 start when a second engagement signs, not before. A claim that the calibration means
  anything waits for three finished steps.

**How to read this page.** Section 1 is the five moves in one table. Sections 2 to 6 are one move each. Section 7
is order and cost. Section 8 is what it will not do. Section 9 is the case against. Section 10 is what I need from
you.

---

## 1. The five moves

| # | Move | What it builds | What it compounds into | When |
|---|---|---|---|---|
| 1 | Hours ledger | `investment` block in the record + `scripts/engagement_hours.py` | Cost of winning each client, a discovery cap that warns before more free work | Now |
| 2 | Planned vs actual | actual hours on progress entries + `scripts/engagement_calibrate.py` | Better ranges in the next proposal, by kind of work | Now (collects), report after 3 steps |
| 3 | Gift library | `_ARTIFACTS/gift-skills/catalog.json`, rows reference a gift id | Every skill written becomes offerable to every client | Second engagement |
| 4 | One sync for every client page | `scripts/engagement_sync.py`, the record names its page | A new client is a record, a page and one routing line | Second engagement |
| 5 | Morning evidence sweep | a section in the existing morning open-loops note | Progress and payment releases proposed before anyone asks | After Move 4 |

## 2. Move 1: hours ledger

- **Record.** An `investment` block, append-only like `progress`:
  - `calls[]`: `{date, minutes, source, basis}` where basis is `measured` (Granola or calendar duration) or `estimated`.
  - `work_paths[]`: the repo paths that belong to this engagement (for My Ally: the hub, the record folder, the
    scaffold folder). Sessions are computed, not typed.
  - `emails`: `{sent, minutes_each, basis: "assumed"}`.
  - `paid_from`: the date the first paid step started. Hours before it are unpaid discovery.
- **Script.** `engagement_hours.py --dir <engagement>` prints calls, sessions (commit clusters on `work_paths`, a gap
  over 90 minutes starts a new session, plus 30 minutes lead-in), emails, and a low/high total with each part's
  basis. It is the method the agent used on 2026-11-08, made repeatable. Stdlib, read-only.
- **Tripwire.** A `discovery_cap_hours` field (you set it; I suggest 10). When unpaid hours pass it, the script
  exits non-zero, `proposal_lint.py` (PR 2072) warns on any new client-facing draft, and the session-start sentry
  names the engagement. It warns; it does not block, since sometimes free work is a choice.
- **Never client-facing by default.** The number can go on a client page only by an explicit field, and then only
  as a range ("roughly 30 to 45 hours").

## 3. Move 2: planned vs actual

- Progress entries already carry the date a row finished. Add an optional `actual_hours` to `done` entries. The
  session that does the work logs it (the standing rule already says sessions log progress).
- `engagement_calibrate.py` reads every engagement and reports, by row kind (task, report, cost range, call):
  planned hours vs actual, planned day vs finished day, and how often a client gate (access, payment) was the delay.
- **No claim before three finished steps** (rule of three). Until then the report prints counts and says "not
  enough data". After that, honest-proposals v1 ranges can cite it as their source instead of judgment.
- Private always: calibration never renders into a client page.

## 4. Move 3: gift library

- `_ARTIFACTS/gift-skills/catalog.json`: one entry per skill with `id`, `repo`, `pinned_sha`, `path`, `license`,
  `fit` tags (non-technical team, builder, founder, finance), and a one-line plain-language "what it does for you".
- Rows in a record name `gift: "<id>"` instead of copying a file; the unlock rule from PR 2066 stays per row.
- The copy served to a client is fetched at the pinned commit, and a `--check` fails if it drifts, so a fix in the
  public repo is a deliberate re-pin, not a silent change on a client page.
- honest-proposals can then suggest gifts by `fit` when drafting the "included at no charge" section.

## 5. Move 4: one sync for every client page

- Each record gets a `hub` block: page file, the marker block name, the download folder, the host.
- `scripts/engagement_sync.py` does what `myally_hub_sync.py` does today for any record with a `hub` block.
  `myally_hub_sync.py` stays as a two-line wrapper so nothing that calls it breaks (house rule: never overwrite a
  script in place for a breaking change).
- Routing stays one explicit line per host in `src/proxy.ts`, so the surface catalog check keeps seeing every host.

## 6. Move 5: morning evidence sweep

- The existing weekday morning note (`arcs-open-loops-morning-note`) gains one section: for each engagement with an
  active step, new evidence since yesterday (a reply in the thread, a GitHub or Lovable invite, a payment notice),
  and the progress entries I propose from it, with the client-facing note already drafted.
- It only proposes. Client-facing notes and payment releases go live when you say yes, in the session where you do.

## 7. Order, dependencies and cost

| Step | Depends on | My estimate (judgment) |
|---|---|---|
| Merge 2072, then 2059, then 2066 (rebased, the six remaining voice-gate lines fixed) | your go on each | 1 to 2 hours of rebase and gates |
| Move 1 | 2072 merged | half a day |
| Move 2 | Move 1, 2066 merged | 2 hours to build; data accrues during Step 1 |
| Move 3 | a second engagement signs | half a day |
| Move 4 | a second engagement signs | half a day |
| Move 5 | Move 4 | 2 to 3 hours |

Moves 1 and 2 are independent of each other in code but Move 2's report is only useful with Move 1's paid/unpaid
split, so they ship together.

## 8. What it will not do

- Send, publish or bill anything. No invoicing system.
- Put calibration or unpaid hours on a client page without an explicit field set by you.
- Pool one client's data into another client's page.
- Claim the estimates got better before three finished steps.

## 9. The case against

Building infrastructure for 1.5 clients is the same front-loading this design warns about. The answer is the
trigger column: only Moves 1 and 2 are built now, because they cost a day, they start paying during My Ally Step 1,
and they turn the unpaid-discovery lesson into a check that runs. Moves 3 to 5 wait for a second signed engagement;
if none comes, they are never built, and nothing is lost.

## 10. What I need from you

1. Go or no-go on the design.
2. The discovery cap in hours (my suggestion: 10).
3. Whether sessions should log actual hours per finished row (needed for Move 2).
4. Confirm the merge order: 2072, then 2059, then 2066.
