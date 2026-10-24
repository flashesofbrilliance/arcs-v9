# JTBD graph s5 pre-registration: outcome feedback and weekly drift report (2026-10-20)

Backlog row `jtbd-graph-s5-feedback`. ADR-089 ids. Parent rules: `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md`
and amendments 1 to 7. Decided by Zach in session 2026-10-20 (he chose every default below). Committed before any
weighting code was written and before any receipt was counted. Changing any rule or constant here after this commit
needs a dated amendment file saying what was seen.

Gate 1 (receipt schema) is already met: `decision_receipt.job_id` and `tool_id`, nullable, CHECK-shaped
(`runtime/specs/decision-receipt/2026-10-20-job-tool-ids.sql`, receipt `2026-10-20--receipt-job-tool-ids-pr1718--ZH`).

## Decisions

1. **Outcome, no new form.**
   - A **use** is a `decision_receipt` row with a non-null `tool_id`. It feeds an edge only when `job_id` is also set.
   - A use of tool T on job J is a **success** when (a) some receipt with the same `job_id` J has `event_at` strictly
     later than the use, and (b) J is closed and not reopened: for `job:backlog:<id>`, the backlog row's `state` is
     `DONE` at computation time (a reopened row is no longer `DONE`, so it stops counting).
   - It is a **failure** when J's backlog row is `COMPOSTED` or `SUPERSEDED`, or J is `DONE` and the latest receipt
     for J names a different `tool_id` than T (another tool closed it).
   - Otherwise it is **pending** and does not move a weight. Jobs not in the backlog (`job:memory:*`,
     `job:pattern:*`) have no closed state, so their uses stay pending; this is a known limit, not a rule to bend.
2. **Weights.** One weight per (job, tool) edge, default `1.0`.
   - No change until the edge has **at least 3 uses** (`N_MIN = 3`). Below that the weight is exactly `1.0`.
   - At 3 or more, resolved outcomes are folded in `event_at` order with an exponential moving average:
     `w_0 = 1.0`, `w_k = (1 - ALPHA) * w_(k-1) + ALPHA * (0.5 + s_k)`, `ALPHA = 0.1`, `s_k` = 1 success, 0 failure.
     So `w` stays in `[0.5, 1.5]`; one success from 1.0 gives 1.05.
   - Ranking (`operators/jtbd_query.py rank`): the job boost term becomes
     `JOB_BOOST * sum(js[j] * W(j, t))` over the matched jobs adjacent to t. With every `W = 1.0` the ranking is
     byte-identical to s4.
3. **Promote only; first 30 days only.** Only outcomes whose use is dated in `[start, start + 30 days)` move a
   weight. The applied weight is `W = max(1.0, w)`. A computed `w < 1.0` is never applied: it is listed as a
   **demotion flag** in the drift report for Zach's review. Outcomes after day 30 are reported, never folded in.
4. **Weekly drift report.** The s5 drift-report script (built after this file, named in the PR) writes only under `_STATE/jtbd-graph/`
   (already gitignored): `drift-<YYYY-MM-DD>.md`, `drift-latest.md`, and its own history `drift-history.jsonl`.
   It sends nothing, calls no network except the existing read-only receipt export when asked (`--export`), and
   writes no database. Meant for Monday morning; `/loops` (`scripts/open_loops.py`) shows a link line to the latest
   report. Contents: new tools with no job (no `serves` or `needs` edge to any job, new since the last report),
   jobs blocked repeatedly (blocked in this report and at least one earlier one), blockers older than 3 beats
   (1 beat = 1 day, `scripts/pulse.py global_beat`; age from the earlier of its first sighting in the history and the row's
   `added` date), edges whose weights moved since the last report, demotion flags, and the coverage count for test 1.
5. **No backfill.** `start` is the merge time of the s5 PR into main, written into
   an s5 config file under runtime specs by the post-merge follow-up (path named in the PR). While `start` is null nothing is counted and every
   weight is 1.0. Receipts with `event_at < start` are never counted, for weights or for coverage.

## Tests, with kill or adjust rules

Baselines come from `runtime/specs/jtbd-s4/score.json` (graph 16 of 18, mean essential recall 0.89) and the pool
rules in `_PATTERNS/2026-10-20-jtbd-graph-preregistration-amendment-7.md`.


- **Coverage.** Within 14 days of `start`, at least 70% of receipts dated on or after `start` carry both `job_id`
  and `tool_id`. If not, the fix is to make the two fields mandatory for merge receipts, not more weighting.
- **Quality.** After 28 days, rerun the s4 blind judging set: the same 18 jobs, the same pool rules as amendment 7,
  a fresh pool prepared by a session other than the one that built s5. The graph must pass at least 16 of 18 and mean
  essential recall must stay at or above 0.89. If it drops, weights are reset to 1.0 and the rule is revisited by
  amendment.
- **Usefulness.** If 2 consecutive weekly reports produce no action Zach takes, cut the report to monthly.

## Not decided here
- The weekly run is a scheduled task only if Zach approves it in chat; until then the command is documented.
