# Pre-registration: do early explanations run overconfident? A Brier score test on my calls and priors

Registered 2026-10-06, as a git commit on `claude/brier-preregistration` (the commit timestamp is the registration time). Author of the question: Zach. Drafted with Claude. Docs only. Not published.

## 0. Read this first: what this registration can and cannot do

- **It is not blind.** The January belief log (priors and finals for H1 to H36) and the calls scorecard already exist, and the registrant has read them. This document fixes the scoring rules before anything is computed, so the analysis cannot fork after the fact. It does not hide outcomes. A result here is descriptive, not a clean confirmation.
- **No score is computed in this commit.** Section 6 lists what is deliberately left uncomputed.
- **Not investment advice, and no Sharpe claim.** A Sharpe ratio (return per unit of volatility) needs a defined strategy and a return series. Neither exists here, so nothing below predicts one.
- **Out of scope: insider trading.** Nothing here tests trading on nonpublic information. Hypothesis H30 in the belief log covers early-holder and insider wallet movements (Satoshi-era, Vitalik, Ethereum Foundation, Lubin-linked), which is a different question.

## 1. The question

If an explanation is written down early, before its test, is it more likely to be too confident? Brier score: the mean squared gap between a stated probability and what happened (0 is perfect; a constant 0.5 forecast scores 0.25). Lower is better.

## 2. Test A: the seven published calls (retrospective, rule-locked)

**Inclusion rule.** A claim is scored only if the published text states a numeric probability for it. Nothing is inferred or back-filled.

**Expected result of the rule, stated now:** very few items qualify. The Jan 24 piece states 85 percent for an SEC bulletin by Jan 31 and 75 percent for visible custodian freezes by Feb 28. The 62 percent figure is a share of a market, not a probability of an event, so it is excluded. The other calls state falsifiers but no probabilities. So Test A is expected to have a very small n, and it will be reported as an anecdote, never as a calibration curve.

**Outcome coding.** Binary, taken from the scorecard verdict: 1 if the stated event happened as published, 0 otherwise. A PREMISE ERROR or MISSED verdict codes 0 for an item the verdict covers. If the scorecard verdict is PARTIAL or OPEN, the item is excluded and counted.

**Reporting.** The Brier score per item and the mean, the count excluded and why, and no interval at this n.

## 3. Test B: the belief-log priors (retrospective, rule-locked)

**Unit.** Each hypothesis row in `usdc-jan-2026-belief-log-2026-10-06.md` with a numeric prior and a numeric final credence.

**Forecast.** The prior as recorded.

**Outcome.** 1 if the final credence is at least 0.10, which is the log's own threshold for "a material contributor"; 0 otherwise.

**Exclusions, fixed in advance.**
1. H15 (DAC8): marked untestable, so its final is not a result.
2. H18 uses its January value (0.08), not the drift value.
3. Any row without a numeric prior or final.
Excluded rows are listed by ID in the report.

**Metrics, computed once.**
1. Brier score of the priors.
2. Brier score of a constant forecast equal to the observed base rate of outcome 1 (the climatology baseline).
3. Brier skill score: 1 minus (prior Brier divided by baseline Brier). Positive means the priors beat the baseline.
4. Mean prior against the fraction of outcome 1, to show the direction of any miscalibration.
5. A bootstrap interval for the skill score at 0.90 coverage, 10,000 resamples of rows, fixed seed 20261006.

**Descriptive only, because the rows are not independent** (credences overlap by design) and **because the final is itself my judgment**, so a good score can reflect consistency with myself, not with the world.

**Secondary, descriptive:** rank the priors. Report where H1, the thesis I published, sits among them and its prior-to-final gap.

## 4. Chain-of-custody limit that governs both tests

The log's priors are recorded in git, but git cannot show that each prior was written before its test ran. The log was built in a single working window on 2026-10-06 across many commits, and some rows were added after the evidence that motivated them surfaced. For example, H27 (the Binance USD1 campaign) carries a prior of 0.05 but was added after the clue was found. So Test B scores "priors as recorded", not "priors as held in advance". Any result is reported with this sentence attached. Only Test C removes the limit.

## 5. Test C: the prospective protocol (the real test)

For every new call or episode from the commit date forward:

1. **Before testing:** write the prediction, a numeric probability, a falsifier and a resolution date in one dated entry, and commit it.
2. **Log the delay:** the hours between the event and the first written explanation.
3. **Prior before test:** record each explanation's prior before running its deciding test, in a separate commit from the result.
4. **Outcome:** per explanation, final credence of at least 0.10 counts as surviving, as in Test B. Per call, the falsifier verdict.

**Hypothesis.** A longer delay before the first written explanation goes with a smaller gap between its prior and its final credence. In other words, early explanations run more overconfident.

**Statistic.** Spearman rank correlation between the delay (in hours, logged) and the prior-minus-final gap, over episodes.

**Decision rule, fixed now.**
- Below 30 episodes: report descriptively. No claim either way.
- At 30 or more episodes: the hypothesis is **supported** if the correlation is negative and its bootstrap interval at 0.90 coverage excludes zero. It is **not supported** if the correlation is zero or positive, or the interval spans zero.
- A result of "not supported" is reported with the same prominence as "supported".

**Also scored in Test C:** the Brier score of the stated call probabilities, with the same baseline and skill score as Test B.

## 6. Deliberately not computed in this commit

No Brier score, no skill score, no correlation and no row count for any test. The first computation happens in a later commit that cites this file's commit hash, and any deviation from this document is listed there under "Deviations" with a reason.

## 7. What would change my mind

- If Test B's skill score is positive with an interval that excludes zero, the recorded priors were not systematically overconfident, and the "explained too early" worry is weakened for this episode, subject to Section 4.
- If Test C reaches 30 episodes and the correlation is not negative, the delay story is not supported, and I drop it.
- If Test A ends with fewer than five scorable items, I say it cannot calibrate me, and I stop citing it for that.
