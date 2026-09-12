---
name: recoil-close
description: T-zero phase (the loop-closing moment). After the call, pull the transcript, score the ex-ante receipt against reality, and fill the Forge / Recoil / War Game / Defensibility tabs. Use right after a call you ran /recoil-prep on.
---

# /recoil-close — score the ex-ante, fill the back four tabs

This is where the loop closes: the pre-call receipt gets scored against what actually happened.
(ADR-068: this is the close-loop print — mandatory once the counterpart has responded, for
every send that filed an ex-ante. An ex-ante left unscored after a response is a drift receipt.)

## Step 1 — pull the transcript
`get_meeting_transcript` for the call (match by attendee + end time). Large transcripts save to a file;
extract via python/shell and read 100% before analyzing. Compute `duration_min` and segment count.

## Step 2 — FORGE (tab 3) — pressure-test the brief's own claims
Before trusting any read, route the load-bearing claims through an **independent skeptic** (you cannot
grade your own output — [[external-artifact-eval-ground-and-skeptic-route]]). Adjudicate each:
GROUNDED (source-forced) / INFERENCE (your read) / STRUCK (overreach). Fill the Forge `table`. Log
omission-drift. This is ROM #6, the Exogenous Forge — a claim stands only if something external forces it.

## Step 3 — RECOIL (tab 4) — close the receipt
- **Receipt closed** (`keyvalue`): predicted (from Ex-Ante) vs actual, which fork hit, load-bearing quote.
- **Belief Log** (`beliefs`): each prior → posterior with **confidence** (credence) and **conviction**
  (how settled), tagged EXP/IMP. NCI stays decision-level only, never per-belief
  ([[confidence-conviction-nci-operational-definitions]]).
- **Belief trajectory** (`kinematic_series`): confidence over segments/calls; `scripts/recoil` computes
  the chart + D1-D3 kinematics.
- Kairos / quiet signals / risk flags (`list`).

## Step 4 — WAR GAME (tab 5)
Kinematic manifold (auto), the gauntlet (BAR ruin edge / LAB Loki-Advisor-Bayesian / COURT), and the
ATG pre-mortem (`table`): assume it's dead in 90 days, walk the critical path, each node gated by THEIR
actual objection; mark the earliest in-your-court node the bottleneck.

## Step 5 — DEFENSIBILITY (tab 6)
Rosetta (translate the method into their native register), the 5-verb × 4-proofing matrix, the
antifragile-core + lossless-translation test.

## Step 6 — render
```bash
./scripts/recoil --data runtime/recoil/generated/<id>.json --audience internal --format html \
    > public/<name>-war.html
```
Commit on main, push, verify live.

## Guardrails
- Honesty over flattery: a falsified prior is the highest-information event — book the correction,
  don't smooth it. Report FORK/DEGRADED where the signal is soft; GREEN only where substrates agree.
- Everything here is `audience: internal`.

## Next
Run **/recoil-ship** to produce the counterpart-safe external twin and draft the note.
