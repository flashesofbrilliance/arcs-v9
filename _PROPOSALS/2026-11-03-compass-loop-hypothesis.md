# Compass loop hypothesis, pre-registration draft (2026-11-03)

Status: DRAFT. The bar below is not pre-registered until Zach approves it; after that it does not move.
Step 1 of the idea-to-MVA flow. Step 3 (the system inventory) is `_PROPOSALS/2026-11-03-compass-system-inventory.md`.
Designed inside /trust v1.7, /privacy v1.5, /terms v1.0 (memory `design-inside-the-trust-contract`).

## 1. The problem, in the navigator's words

Someone at a fork with stakes and a deadline ("take the offer or wait", "ship now or fix first") can't see the terrain clearly enough to
choose, and later can't tell whether they chose well or got lucky. Today they cope by asking a friend, writing a pros and cons list, or
deciding on gut and never looking back. The hurt is per decision, a few times a quarter for most people; the second half (never
learning from how it landed) is invisible until the same mistake repeats.

Labelled assumption, not evidence: this framing comes from WORLD.md and the arcs.care copy. No interview has confirmed it; the ICP is
described as a state (stuck at a fork), not a segment (memory `icp-is-a-state-not-a-segment-catch-in-caught-breath`).

## 2. The assumption stack

| # | Belief | Uncertainty (1-3) | Fatality (1-3) | Score | Evidence today |
|---|---|:-:|:-:|:-:|---|
| A | Strangers bring a real decision to the compass | 2 | 3 | 6 | 5 signed-in non-Zach users, 11 receipts, Jun 21 to Oct 13; 48 anonymous runs Jun to Jul |
| B | The bearing is useful enough to act on, not just novel | 2 | 3 | 6 | No external rating collected |
| **C** | **A navigator comes back at the horizon and logs how it landed, with no extra nudge** | **3** | **3** | **9** | **3 users got their first debrief email, 0 opted in to more, 0 outcomes on 11 receipts** (query in section 5) |
| D | Someone pays for the brief | 3 | 2 | 6 | 0 paid receipts (`paidAt`) |
| E | Their own outcomes measurably sharpen their next bearing | 3 | 2 | 6 | Not built; 5 real outcomes exist, all Zach's |

C is the riskiest by score. But section 5's query shows A blocks the test of C: 1 outside receipt in the last 8 weeks. Organic traffic
cannot answer C before 2026-12-31.  It is the loop: without it there is no ledger, no calibration, nothing that compounds, and the contract rules out
the usual fix (more reminders). A, B and D matter, but a compass that people use once and never close is a one-shot tool, a different
product with a different price.

## 3. The falsifiable hypothesis

**We believe** a signed-in navigator who brought a real decision will come back after its horizon and log how it landed, prompted only
by what the contract allows: the one unasked debrief email, plus an outcome prompt on pages they already open (receipt page, /history).

**We'll know we're wrong if** 0 of the first **6** qualifying navigators log an outcome within **14 days** of their first receipt's
horizon. **Pass** at 2 or more of 6. (Revised after the devils-advocate pass: count per navigator, not per receipt, because the contract
emails only a navigator's first receipt. At a true rate of 30%, "0 of 6" happens by chance about 12% of the time; at 10%, "2 or more of
6" happens about 11% of the time. 1 of 6 is inconclusive: run 6 more, once.)

- Qualifying navigator: signed-in, not Zach (excluded by `userId`), first receipt created after the outcome prompt ships, first
  debrief email actually sent (`firstDebriefSentAt` set).
- Logged stage by stage so a failure points at a cause: debrief sent, link clicked (a `via` tag on the email link), form opened, outcome
  saved. The form requires `matched` and `regretScore`; time three people filling it before the test, so friction is not mistaken for
  a broken loop.
- Window: until 10 qualifying receipts have passed horizon + 14 days, or 2026-12-31, whichever comes first. If fewer than 10 qualify by
  then, the result is "not enough traffic", which is a finding about A, not a pass on C.
- Counted by `scripts/outcome_funnel.py` (read-only) or one SQL count, written into this file with the query.

**Decision rule, fixed before looking:**
- 2 or more of 6: build A in the inventory (show their own closed outcomes beside the next bearing).
- 1 of 6: run 6 more, same bar, no changes. Only once.
- 0 of 6: stop loop work. Treat the compass as a one-shot tool and price and pitch it that way (the paid brief), not as a ledger.

## 4. Cheaper ways to run it (Zach's call)

The test above waits on horizons and on traffic, so it can take weeks. Two cheaper variants, each with a cost:

| Variant | Speed | Cost or bias | Contract check |
|---|---|---|---|
| Recruit 10 people Zach knows to bring a this-week decision | about 2 weeks | Friends close loops more than strangers: a pass is weaker evidence | Fine: they sign up knowingly |
| Write to the 5 existing outside users and ask how their decision landed | days | 5 is a small sample; personal outreach is itself a nudge | /privacy allows email "only if you provided an address" for the service; a research email may need its own wording. Check first |

## 5. Refutations (devils-advocate pass, 2026-11-03) and the first check

1. **Traffic blocks the test.** CONFIRMED by query below: 1 outside receipt in 8 weeks.
2. **Unequal treatment:** only a navigator's first receipt is emailed. CONFIRMED: 6 of 11 receipts have `debriefSentAt` (some predate
   the first-only rule), 3 of 5 users have `firstDebriefSentAt`, 0 opted in. So the real evidence is "3 emailed navigators, 0 outcomes":
   weak (at a true 30% rate, 0 of 3 happens about 34% of the time), not nothing.
3. **Short horizons get selected:** only near-term receipts finish inside a window. Average reminder lag today is 34.2 days. Not fixed;
   named as a limit.
4. **The count can't explain itself:** no record of which path brought someone back, and required fields may block the form. Addressed
   by the stage logging and the form timing in section 3.
5. **n = 10 per receipt was noise.** Addressed by the per-navigator bar.

Query (Supabase, 2026-11-03), excluding Zach by `userId` (the account with the most receipts):
11 receipts, 5 users, 11 with a reminder date, 10 past it, 6 debriefs sent, 3 users with a first debrief, 0 opted in, 0 outcomes,
average 34.2 days from receipt to reminder, 1 receipt in the last 8 weeks.

## 6. Next

Checkpoint 1 (Zach): C stays the bet, but it can't be tested on organic traffic. Pick one:
- Run it on a recruited cohort (section 4, first variant) of at least 6 people with this-week decisions, knowing a pass is weaker evidence.
- Or move upstream: A (getting strangers to bring a decision at all) is the bet to frame first, and C waits.
Then pre-register the chosen bar, then map-the-terrain (Step 2), then design-the-mva (Step 4).
