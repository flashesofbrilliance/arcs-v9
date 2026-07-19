# Workflow Cost Ledger

**Tributary:** J4 (ATG, ratified 2026-07-19)

Records each real workflow run's **actual** token spend against the **projected**
budget in `jtbd-orchestration-map.md`, so the projections stay honest and future
runs are costed from evidence, not guesses. Append one row per run; when actuals
drift >25% from projection, update the map's budget for that job and note it here.

## Ledger

| Date | Run ID | Job | Subject | Projected | Actual (output tok) | Δ | Notes |
|------|--------|-----|---------|-----------|---------------------|---|-------|
| 2026-07-19 | `wf_31635888-3f6` | recoil-report | Chan Suh (validation) | ~350k | **exceeded — stopped at 48/93 verify** | **▲ over** | 60 agents started / 58 returned; ~60 min wall; watchdog-stopped mid-verify. See lessons. |

### Run notes — `wf_31635888-3f6` (validation, pre-tightening script)

**Coverage reached:** gather 5/5 (only granola + git productive — Gmail/Calendar/LinkedIn
returned thin/empty, likely MCP not connected) → profile ✓ → 4 lenses ✓ (31 claims: LAB 9,
SAGE 9, CURATOR 8, BAR 5) → verify **48 of 93** verdicts before the watchdog stopped it →
synthesis **never reached.**

**Headline (design working):** the adversarial verify **refuted 43 of 48** claims (~90%).
The input was thin (2 real sources), so most claims were single-source/affect-driven — and
the skeptic correctly killed them. Only ~5 survived. The stage does exactly its job.

**Lessons (feed back into the map + workflow):**
1. **Verify fan-out is the cost driver.** 31 claims × 3 skeptics = **93 Opus agents** — this
   blew the ~350k projection and the wall-clock. Fix: cap claims/lens (top-N by confidence),
   or Sonnet first-pass with Opus only on survivors, or batch (one judge per N claims).
   Update the recoil-report budget upward and the shape to bounded.
2. **Reasoning agents wandered into other people's dossiers.** On the broad-permission
   script the CURATOR lens used filesystem access to pull in *other named individuals'*
   precall files (Cassandra Riley, Ayesha, Danny Quick) into Chan's report — empirically the
   cross-person data-bleed we theorized. Even the tightened `recoil-reason` still has `Read`;
   recommend dropping it to truly no-tools so lenses can't leave their prompt.
3. **MCP gather was thin** — confirm Gmail/Granola/Calendar connectivity before a real run,
   or the report is built on 2 sources, not 5.

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
