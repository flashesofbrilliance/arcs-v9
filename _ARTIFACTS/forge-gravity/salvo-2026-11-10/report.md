# Gravity Call and Put: ballistic salvo, 2026-11-10

A simulation only shows what its assumptions imply. Every prior is judgment unless a source is named; none was fitted to data. Operator verdicts come from the repo's code (SAGE, LAB, BAR, COURT); the inputs that code needs (a time series, axiom marks, somatic scores, irreversibility) are also judgment and were varied across 16 runs. Run by a subagent; files here: mc.py, lenses.py, results.json.

## Classes
| Class | Lenses | Verdict | Weakest joint | Fix (applied on the page) |
|---|---|---|---|---|
| Bomb | BAR, Funhouse Q2, KKL Kairos Lock | holds | Ruin only if irreversibility > 0.7 (Put read as a build commitment) | Stake is the post; build time-boxed |
| Fire | COURT evidence test, LAB Loki lens | leaked | No resolution rule: median P 0.24 / 0.30 / 0.62 by reading | Resolution rule pre-registered on the Call |
| Water | LAB advisors and Bayesian lens, MC sensitivity, KKL | leaks | base_network drives the variance; no decay schedule | Re-mark P at each network rules release |
| Air-gap | Funhouse Q3, COURT identity test | leaked | Author sells the remedy and self-grades; Put overstated the ARCS record | Interest stated, Gravity resolves, Put reworded |

## Monte Carlo (30,000 forward, 30,000 reverse; uniform priors, all judgment)
| Prior | Range |
|---|---|
| p_standard (AP2, recalled) | 0.35-0.70 |
| p_fraud | 0.25-0.55 |
| p_regulator (OCC rule not counted) | 0.05-0.25 |
| base_network | 0.04-0.15 |
| base_issuer | 0.02-0.08 |
| lift_standard | 1.5-3.0x |
| lift_fraud | 1.3-2.5x |
| lift_regulator | 1.5-3.0x |
| p_existing_counts (loose only) | 0.30-0.60 |

| Reading | p05 | median | p95 | Runs at or above 1/3 |
|---|---|---|---|---|
| Network rule only | 0.11 | 0.24 | 0.41 | 0.20 |
| As written (network or issuer) | 0.17 | 0.30 | 0.46 | 0.37 |
| Loose | 0.48 | 0.62 | 0.74 | 1.00 |

Tornado: base_network 0.25, lift_standard 0.10, lift_fraud 0.09, base_issuer 0.07. Reverse: 82% of yes-runs fire through a network rule, 18% through an issuer alone; likelihood ratios regulator 2.6, fraud 1.6, standard 1.4.

Put: expected loss 2.7 weeks (p05 1.6, p95 4.2); 26% sits in the branch where the rule arrives and the ARCS record does not meet its format. The decision_receipt table is append-only by trigger but has no signature, mandate or transaction-binding field.

## Seams found in the operator code (not fixed here)
- SAGE labels a smooth rising 13-point series "noise" and a straight line "mixed", so the auto-generated Loki fires at 0.95 and returns RUIN_RISK whatever the claim.
- The court_permit_threshold comment in arcs_rom.py points the opposite way to the Court's code; 8 of 16 COURT runs land on the 0.35 boundary.

## Not run
probe_kkl and probe_funhouse (need config files), Funhouse Q4 and Q6, web re-verification of AP2, Agent Pay and Visa status. Somatic and HCI inputs are placeholders.
