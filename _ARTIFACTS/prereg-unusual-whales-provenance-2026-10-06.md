# Pre-registration: do the Unusual Whales trading claims for Jan 14 to Feb 1, 2026 trace to primary records?

Registered 2026-10-06 as a git commit on `claude/prereg-unusual-whales-provenance` (the commit timestamp is the registration time). Question from Zach. Drafted with Claude. Docs only. Not published. Companion to the Brier pre-registration (`brier-preregistration-calls-and-priors-2026-10-06.md`).

## 0. Read this first

- **Not blind.** The belief log already cites this account as a dated news source (rows H3 and H33, and the leading-signals timeline) and records that only the first screen of its Jan 14 to Feb 1 posts was read. Nothing has been captured or graded yet.
- **What this can show:** whether each trading claim traces to a primary record, and whether traced activity precedes dated announcements by more than a pre-set threshold. **What it cannot show:** that anyone traded on nonpublic information. That is a legal finding. This test measures provenance and timing only.
- **Language rule.** Results say "traced", "partly traced", "not traceable" or "contradicted". They never say "insider" about a person. Any claim about a named person is reported as the account's allegation, with the primary record beside it, or marked untraced.
- **Not legal advice, not investment advice.**

## 1. Questions

- **Q1 (provenance):** Of the account's posts in the window that assert a trade, position or flow tied to an event, what share traces to a primary record?
- **Q2 (timing):** For the traced trades, is activity in the instrument unusually high before the matching announcement, compared with a matched baseline?
- **Q3 (link to USDC):** Does any traced, unusual trade sit in an instrument tied to the USDC move (USDC itself, Circle's stock, Coinbase's stock, USD1, the WLFI token)? If not, the belief log is unchanged.

## 2. Capture, fixed before any post is read

1. **Full capture, not a screen.** Every post by the account from 2026-01-14 00:00 to 2026-02-01 23:59 UTC. Method: X advanced search (`from:<account> since:2026-01-14 until:2026-02-02`) in a logged-in browser session, paged to the end, one query per day to keep each page complete. Record the exact query strings, the capture time, the post count per day and a hash of the saved text. Completeness check: X search can silently omit posts, so the per-day counts are compared against a second pass with the `filter:replies` and `filter:links` variants, and any day where the counts disagree is flagged and re-run, not smoothed over.
2. **If full capture fails,** the test is declared "not run", with the reason. A partial capture is not a substitute and is not analyzed.
3. **Unit of analysis (a claim):** a post that asserts a specific trade, position, flow or market move tied to a specific event or announcement. Commentary, news relays with no trade claim, and replies without a claim are excluded and counted.

## 3. Provenance grading (Q1), fixed now

For each claim, record the instrument, timestamp, size and the event it is tied to. Then assign one grade:

- **P1:** a primary record confirms it (filing, exchange or clearing data, a congressional disclosure, a court document, the issuer's own release).
- **P2:** a reputable secondary source cites a primary record that I then locate and read.
- **P3:** the account's own data, not independently reproducible by me.
- **P4:** no source stated and none found.

A claim is **traced** if P1 or P2, **partly traced** if some fields match and others do not, **not traceable** if P3 or P4, and **contradicted** if a primary record shows otherwise. Grades are assigned by one pass, then re-checked cold by a second pass; disagreements are listed, not averaged.

## 4. The denominator problem (selection bias), fixed now

An account that posts suspicious cases will look more suspicious than the market is. To control for that:

1. **Event list frozen in this commit.** The comparison set is every dated event in the belief log's Jan 14 to Feb 1 timeline, not only events the account flagged: the Jan 16 tariff threats, the Jan 17 White House threat over the market-structure bill, Jan 19 Armstrong's reply, the Jan 20 Bessent remarks and bond move, the Jan 23 Binance USD1 campaign, the Jan 28 SEC statement, the Jan 29 events, and the Jan 30 Warsh nomination.
2. **Matched baseline.** For each (instrument, event) pair, activity in the 20 trading days before the event, excluding the 2 trading days immediately before it.
3. **Null events count.** Events with no flagged trading are tallied. The share of events with a flagged trade is reported against the share of all events.

## 5. Timing test (Q2), fixed now

- **Metric.** Volume (or open interest for options) in the 2 trading days before the announcement, as a z-score against the matched baseline. "Unusual" means a z-score of 3 or more.
- **Multiple comparisons.** The number of (instrument, event) pairs tested is stated first. Results are reported with a false discovery rate adjustment across all pairs. A single outlier is an anecdote, not a finding.
- **Required-disclosure rule.** Silence counts as evidence only for required, routine disclosures (for example a congressional periodic transaction report or a Form 4 due by its deadline). An absent post, or silence in reply to a letter, is not evidence.

## 6. Link to USDC (Q3) and the belief-log rule, fixed now

New row **H37** in the belief log if any claim is traced: "Trading ahead of announcements contributed materially to the January USDC move." **Prior: 0.03**, set here before capture. The row stays below 0.10 unless a traced, primary-sourced, unusual trade sits in a USDC-linked instrument and its reported notional is compared with the USDC daily change in the same units. Otherwise the final is reported at or below the prior, with the reason.

## 7. Chain of custody and limits

- Posts are captured once, hashed, and graded from the captured copy, not from live pages.
- The account's posts are secondary. A claim the account attributes to a newspaper is graded P2 only after I locate the original. The WSJ report cited for the Abu Dhabi item is currently unverified.
- Options and flow data may sit behind paid sources. If a pair cannot be tested for lack of data, it is listed as untestable, not scored zero.
- Personal data stays out of any result. A privacy and PII gate runs before anything from this study is published.

## 8. Not computed in this commit

No post has been captured, no claim graded, no z-score computed, and no row added to the belief log. The first computation lands in a later commit that cites this file's hash, with any deviation listed under "Deviations" and a reason.

## 9. What would change my mind

- If Q1 shows most claims P3 or P4, the account is a lead generator, not evidence, and I stop citing it for trade claims.
- If Q2 finds no pair at z of 3 or more after the false discovery adjustment, "no unusual pre-announcement activity found in this sample" is the result, stated as such, with the sample limits.
- If any pair does clear the bar, I report it as a timing anomaly with its primary record, not as a finding about intent, and Q3 decides whether the belief log moves.
