# Workflow Cost Ledger

**Tributary:** J4 (ATG, ratified 2026-07-19)

Records each real workflow run's **actual** token spend against the **projected**
budget in `jtbd-orchestration-map.md`, so the projections stay honest and future
runs are costed from evidence, not guesses. Append one row per run; when actuals
drift >25% from projection, update the map's budget for that job and note it here.

## Ledger

| Date | Run ID | Job | Subject | Projected | Actual (output tok) | Δ | Notes |
|------|--------|-----|---------|-----------|---------------------|---|-------|
| 2026-07-19 | `wf_31635888-3f6` | recoil-report | Chan Suh (validation) | ~350k | _pending — fill from run journal_ | — | first real run of the orchestrated recoil; validating vs hand-built `chan.html` |

## How to fill "actual"

The workflow's transcript dir holds `journal.jsonl` (per-agent returns) and
`agent-*.jsonl`. Sum the output tokens across the run, or read the run summary's
`subagent_tokens`. Record output tokens (the budgeted quantity), not input.

## Calibration rule

- Δ within ±25% → projection stands.
- Δ > +25% (over budget) → either the job's scope grew or a tier was mis-assigned;
  bump the map row and note which stage overran.
- Δ < −25% (under) → a stage is cheaper than modeled (often: a Judge task that
  Sonnet could have done) — consider down-tiering and re-cost.
