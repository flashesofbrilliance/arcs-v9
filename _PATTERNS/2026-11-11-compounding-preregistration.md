# Compounding pre-registration: does the induced backlog lower the cost of the next job? (2026-11-11)

Backlog row `compounding-model-prereg`. Written before any fit is run. The rules change only by a dated
amendment appended below; an amendment written after a count names the count it saw.

## Why
The Posted Rate (good.arcs.care/blog/nftt/the-posted-rate) priced one video at about $7.72 of marginal compute
and noted that the low figure rests on tooling paid for earlier. The claim to test: tools built for one backlog row
lower the cost of later rows, by reuse and by recombination, so the cost of the next job falls as closed work piles up.
The stronger claim, that it falls exponentially, is tested separately and is not assumed.

## Prior, stated now
The usual finding for cumulative-output cost curves is a power law (Wright's law): a fixed percent cut per doubling of
cumulative output, which flattens. Exponential decline in time is the less likely shape. Basis: judgment from the
learning-curve literature, not a measurement of this repo.

## Unit and window
- **Unit:** a backlog row in `_QUEUE/induced-backlog.jsonl` that reached `DONE` with a merged PR or receipt named in its
  `status_note`.
- **Window:** rows closed 2026-10-20 (the first day receipts required `job_id`) through 2026-12-15.
- **Read date:** 2026-12-15, reported in that week's drift report. If the plan cap stalls work, that is reported as a
  result, not a missing value.

## Measures (fixed now)
Sources: `public.decision_receipt` (job_id, tool_id, refs, event_at; AGENTS.md "Receipts or it didn't happen"),
`_QUEUE/induced-backlog.jsonl`, session transcripts, `git log`. Shape follows
`_PATTERNS/2026-10-20-throughput-preregistration.md`.

1. **Cost per row, c.** Sum the token usage of every session transcript (`~/.claude/projects/*/*.jsonl`, replies
   deduplicated by message id) whose `gitBranch` equals the head branch of a PR cited by a receipt with
   `job_id = job:backlog:<row>`. Price it at Claude list rates per model (the rates in The Posted Rate; Opus 5.5 at
   $4 in, $20 out, $0.20 cache read, $5 cache write per million). This is a shadow cost, labelled as such.
   Rows with no matching transcript are dropped and their count is reported.
2. **Human attention, h.** The count of user turns in the same transcripts. A proxy, not hours; labelled as a proxy.
3. **Experience, X.** Cumulative count of rows closed before this row's close date (ordered by receipt `event_at`).
4. **Reuse share, r.** The share of tool paths the row's sessions ran (scripts and skills named in Bash or Skill calls)
   whose file already existed in git on the row's `added` date. Dated by git history, not by first receipt, because
   `tool_id` logging began 2026-10-20 and first-receipt dating inflates later reuse by construction.
5. **Recomposition, k.** The count of distinct pre-existing tools a row's sessions ran. Reuse of one tool scores 1;
   chaining several scores higher.
6. **Upkeep share, u.** The share of rows closed per week whose `id` or `jtbd` contains any of: fix, repair, drift,
   stale, gate, hygiene, refresh, regen, reconcile. A crude keyword rule, fixed now so it cannot be tuned later.
7. **Controls.** Model mix (share of output tokens from the top tier), row size (log of lines changed across the
   row's PRs), priority.

## Models
- **M0, no compounding:** ln c = a + controls.
- **M1, power law (Wright):** ln c = a - b ln X + controls.
- **M2, exponential in time:** ln c = a - g t + controls, t = days since 2026-10-20.
- **M3, recomposition:** M1 plus terms in r and ln k.

## Verdict rules (fixed now)
The thresholds below are judgment, set now (memory `pre-register-rule-before-counting`); the 4-AIC margin is a
conventional cut, not derived from this repo.

- **Sample floor:** at least 30 rows with a cost. Below that the report says "too few to say", prints n, and renders at
  grain fidelity. No verdict.
- **Compounding supported:** b > 0 with a 90% interval that excludes 0, and M1 beats M0 by at least 4 AIC.
- **Exponential supported:** M2 beats M1 by at least 4 AIC, and in M3 the coefficient on ln k is negative with a 90%
  interval that excludes 0. Otherwise the shape is reported as a power law, or as no detectable trend.
- **Compounding falsified:** the 90% interval for b includes 0 or sits below it; or upkeep share u exceeds 50% of
  closed rows in the last two weeks of the window (the stock of tools costing more to keep than it saves).
- **Attention check:** the same M0/M1 comparison is run on h. Compute can fall while attention does not; if so, the
  report says so, because attention is the cost The Posted Rate left unpriced.

## Known confounds, named before counting
- Rows that close early may be easier (selection). Row size is controlled; the residual is stated, not removed.
- Model and price changes inside the window shift c without any compounding. Model mix is controlled.
- Rows with no transcript match are not missing at random (cloud sessions, other harnesses).
- **Seen before this file was written:** on 2026-11-11 a receipts query showed weekly first-seen tool reuse of 81, 89,
  92 and 96% (weeks of 2026-10-19 to 2026-11-09). That figure uses first-receipt dating, which this file rejects, so it
  counts as neither evidence for nor against the claim.

## What this file does not do
It does not build the fit script. That is the next step on the row, written after this file merges, so the counting
tool cannot shape the rule.

## Amendments
(none)
