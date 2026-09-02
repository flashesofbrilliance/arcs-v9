# SAGE Firing — Diagnosis & Solution Spec

> Root-cause diagnosis + treatment plan for the write-time coverage gap surfaced by the real-receipt
> audit (`operators/audit_service/run_real_receipts.py`). Grounded in prod `SageTrace.failureReason`
> evidence (read-only), 2026-09-01. Differential-diagnosis discipline: symptom → candidate pathogens →
> discriminating test → confirmed pathogen → treatment. Do NOT prescribe before triangulating.

## Symptom
SAGE fired on **45 of 247** decisions (18%). The real-receipt scorecard is therefore mostly `null`
(202 unscored), and — the sharper cost — **70 of 88 one-way (irreversible) doors are unscored.**

## Differential → triangulated (basis: `SageTrace` GROUP BY `fired, failureReason`)

| Candidate pathogen | Verdict | Evidence |
|---|---|---|
| SAGE_URL unset / not deployed | **RULED OUT** | 0 "unset" failures; 45 fired at avg 131ms — service was **reachable from the compass route in a window** (Jun 21–Aug 11). NB: "reachable" ≠ "robustly deployed" — the 22 timeouts suggest a *fragile/dev* endpoint, not prod-grade infra. Deploy *quality* is un-verified. |
| Selective / manual on critical (80/20) | **RULED OUT** | fire-rate flat across door class (one-way 20.5% vs two-way 17.0%); fired on MORE two-way (27) than one-way (18) in absolute count |
| Latency / timeout | **CONFIRMED** | 22 aborts at avg 3005ms (the 3s `AbortSignal.timeout`), window Jun 21–Jul 1 |
| Contract / validation | **CONFIRMED** | 4× `non-200:422`, Jun 30–Jul 19 |
| Pre-feature absence | **CONFIRMED (structural)** | 176/247 have no `SageTrace` row — SAGE machinery didn't exist yet |

**Corrected framing:** since SAGE existed, success is **45/71 = 63%**, not 18%. The 18% is drowned by the
pre-feature bulk. The lever was never *deploy* (SAGE was deployed) — it's **latency + a payload bug.**

> Limit (couched): door-class fire-rate is confounded by time (SAGE only fired in a health window).
> The flat rate gives no selectivity signal to explain, so isolating door-class effects (needs per-
> receipt `createdAt`) is unlikely to change the headline, but is not fully controlled.

## Treatment (solution half — the fix)
1. **Latency — kill the 22 timeouts.** SAGE is 131ms when warm; the aborts are cold-start/overload in a
   window. Keep the SAGE service warm (min-instance / ping) and/or raise the compass 3s abort. Cheapest
   high-yield fix.
2. **Contract — fix the 422.** A payload validation mismatch between compass's `{question, horizon,
   stakes}` and `arcs_api.sage_score`'s `SageScoreRequest`. Small, deterministic.
3. **Prioritize by irreversibility (refuted-hypothesis-turned-rule).** Gate firing so **every one-way
   door always fires** SAGE. Covers the free-solo topology (a missing check on an irreversible decision
   is unrecoverable) AND is cheaper than firing on every reversible two-way door.
4. **History — accept the 176 as pre-feature.** Unrecoverable retroactively (no re-run without original
   context). A backfill (re-derive from stored `rawResponse`) is a separate, low-value decision.

## The deep core (separate, bigger — a product change, not an ops fix)
Even at 100% firing, **fidelity stays proxy — and worse than proxy.** SAGE's somatic/axioms output is
not just derived, it is **DEGENERATE**: across all 45 fired traces there is **exactly 1 distinct value**
for somatic AND for axioms (every receipt: axioms `YES/YES/YES/YES`; somatic byte-identical
`{phase_tuning:0.72, surge_detection:False, feels_right:True, that_vibes:True, locked_in:True,
expected_vs_actual:0.72}`). Present-but-constant = **zero per-decision information** — an inlier that
passed every per-row presence check; only a corpus-level distinct-value pass caught it. So informative
somatic/axioms coverage is **0/247**, not 45. (Symptom triangulated; mechanism — pipeline stub vs
input-insensitivity in `arcs_api.sage_score` → operators — NOT yet confirmed; needs reading the SAGE
pipeline. Do not claim the cause.)

**Broader than SAGE (verified 2026-09-01, genetic-frame audit).** The persistence gap is not limited to
somatic/axioms. Across the 247, `dewyVector` (the D/E/W/Y state vector) is **null 247/247**, and
`nciByLens` is **null 240/247** — verified real in the DB, not a query artifact. So the runner's
`signalProxy` (derived from DEWY Y) and `hci` (from nciByLens) also default corpus-wide. Receipts persist
the *outputs* (trueNorth, nci, fated, court) but not the *state vector* they encode. "Unexpressed gene,"
not "absent from the genome" — but for the audit's purposes, currently unavailable either way.

Therefore: **0/247 decisions carry user-grounded evidence, and 0/247 carry even informative derived
signal.** No amount of reliable firing changes that. Evidence-grade fidelity requires **eliciting the 6
somatic dimensions from the user at decision time** (a compass UX change) AND fixing SAGE to emit
per-decision (non-constant) somatic/axioms. This is the real constraint on the instrument ever producing
trust — the ops fixes (latency/422/gating) only restore *coverage of a signal that is currently empty.*

## Verify (the third loop-half — future, on measurement not assertion)
After 1–3 ship: re-run `run_real_receipts` on a fresh export; forward success-rate should climb 63% → ~100%
and one-way-door coverage should approach full. **Evidence-grade (`somatic real`) stays 0** until the deep
core (elicitation) ships — track it separately so the two are never conflated again.
