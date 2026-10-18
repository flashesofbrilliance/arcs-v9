# Role lenses: clusters of the scored jobs.arcs.care board (2026-10-14)
Source: prod `JobOpportunity`, PURSUE + CONSIDER rows with dims (633). Read-only pull via Supabase CLI. Title-regex clustering (crude: first match wins; "other" is a residue). Data: `role-lenses-2026-10-14.json`.

## Read this first
The board holds TWO scoring lenses. Rows scored on `target-role-scan` v1.3 (217) and on `bridge-scan` v1.1 (416) have different dimensions and cannot be averaged together, and the bridge lens mechanically defers FDE-lane titles to target-role-scan. So the clusters below are per lens. Scores are model-assigned (Haiku, temp 0); treat differences under ~0.03 as noise.

## Target-role-scan (fit, 217 rows)
| Lens | n | PURSUE | mean composite | strongest dims | weakest |
|---|---|---|---|---|---|
| forward-deployed | 90 | 69 | 0.780 | role_shape 2.93, scope 2.78, ai_native 2.51 | warm_path 0.09, domain_breadth 1.22 |
| applied-ai-engineer | 44 | 34 | 0.756 | ai_native 2.89, role_shape 2.70, scope 2.55 | warm_path 0.05, domain_breadth 1.16 |
| embedded-product | 34 | 21 | 0.741 | scope 2.76, role_shape 2.65, ai_native 2.62 | warm_path 0.06, domain_breadth 1.15 |
| deployment-solutions | 15 | 5 | 0.676 | scope 2.47, comp 2.47, culture 2.40 | warm_path 0.20 |
| transformation-strategy-ops | 15 | 7 | 0.708 | comp 2.60, scope 2.53, culture 2.40 | warm_path 0.20 |
| gtm-systems | 4 | 4 | 0.784 | role_shape 3.0, ai_native 3.0 | domain_breadth 0.0 (n too small) |

## Bridge-scan (winnability, 416 rows)
| Lens | n | PURSUE | mean composite | weakest |
|---|---|---|---|---|
| gtm-systems | 53 | 43 | 0.781 | warm_path 0.0, competition_density 1.70 |
| transformation-strategy-ops | 114 | 72 | 0.719 | warm_path 0.0, edge_rewarded 1.33 |
| deployment-solutions | 82 | 39 | 0.689 | warm_path 0.0, competition_density 1.39 |
| embedded-product | 114 | 37 | 0.668 | warm_path 0.0, competition_density 0.61 (stampede) |
| applied-ai-engineer | 6 | 2 | 0.713 | n too small |

## What the clusters say (descriptive, not causal)
1. **Where mass is:** forward-deployed (most PURSUE rows at the highest fit mean), then applied-AI engineer, then embedded product. On winnability, gtm-systems is the best and embedded product the worst (stampede).
2. **The universal bottleneck is not fit, it is warm_path.** Mean warm_path is about 0 in every cluster in both lenses. Fit is already high; no intro or referral is attached to almost any row. This is the cheapest lever.
3. **The regulated-breadth moat is under-rewarded by the market, not by the rubric:** mean domain_breadth is about 1.2 in the fit lens, so roles rarely ask for multi-regulated fluency (the Wonderful JD does not either). Position it as a bonus, not the headline.
4. **Deployment-strategist is thin in fit-lens data (15 rows)** and lives mostly in bridge-scan (82). That matches the Wonderful grade: Strategist clears on fit and only just on winnability.
5. **Lens overlap:** forward-deployed and applied-AI engineer have nearly the same dimensional shape in the fit lens, so one resume facet can serve both with a title swap; embedded product and deployment-solutions differ more.

## Method limits
Title-regex clustering misfiles roles (a "Product Operations" title may be a GTM-systems role). The "other" bucket and the 375 unscored rows are excluded. Dimension means are over LLM-assigned integers 0-3. No outcome data (replies, interviews) is joined, so nothing here predicts which lens converts; the kaizen row below adds that join.
