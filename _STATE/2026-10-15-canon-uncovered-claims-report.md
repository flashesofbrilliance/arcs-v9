# Canon uncovered quantified claims (REPORT ONLY, 2026-10-15)

No canon text was edited or deleted. Zach decides keep (add ledger entry with source), cite, or strike.

- Gate: `scripts/provenance_lint.py` (opt-in). Enrolled via empty sibling ledgers `_CANON/evidence.jsonl` and `operators/arcs_primitives.evidence.jsonl`. The pre-commit hook only lints `public/**` and `_ARTIFACTS/**` html, so enrolment blocks nothing.
- Generator: `scripts/canon_claims_report.py` (stdlib; reuses the gate's METRIC plus r=, p<, Brier, chi-square). Regenerate: `python3 scripts/canon_claims_report.py`.
- Rows: **918** uncovered tokens across _CANON/**/*.md and arcs_primitives.py docstrings. Counts are tokens, not distinct claims; many are illustrations, projections or targets, which the table does not distinguish.
- Does data exist? No outcome dataset backs any row. Closed-outcome counts in the repo: Accountant report `_STATE/2026-09-27-accountant-scoreboard.json` shows 3 outcomes of 254 receipts (3 founder, 0 external, 0 anonymous); AGENTS.md records 2/247 on 2026-09-02. Calibration needs n>=30 closed per cohort. So accuracy, calibration, MAPE, r, Brier and "vs human experts" figures (e.g. YellowPaper:160-163, primitives:290-295) have no source in the repo. A "Compendium, Volume II" cited at primitives:289 was not found by grep in this repo (not searched outside it). A grep match of a number in some unrelated data file is coincidence, not evidence, so no such column is given.
- Highest-risk rows (empirical-sounding): ARCS-YellowPaper.md:11, :160, :161, :162, :163, :208-211 (scaling table; :211 is labelled projected); ARCS-Canon-v1-1.md:91; operators/arcs_primitives.py:290, :292, :293, :295 (and :315-319 weights comments).
- Not covered by the regex: definitional drift (primitives NCI formula vs product NCI) and the acronym mismatch in the Litepaper; those are not numeric claims. Listed as open questions in the spec, not here.

| file:line | claim token | line (truncated) |
|---|---|---|
| _CANON/ARCS-Canon-v1-1.md:53 | `$350B` | - Transform $350B marketing spend from faith-based to evidence-based |
| _CANON/ARCS-Canon-v1-1.md:91 | `68%` | - 87% accuracy (vs. 68% baseline, 76% vs. human experts) |
| _CANON/ARCS-Canon-v1-1.md:91 | `76%` | - 87% accuracy (vs. 68% baseline, 76% vs. human experts) |
| _CANON/ARCS-Canon-v1-1.md:91 | `87%` | - 87% accuracy (vs. 68% baseline, 76% vs. human experts) |
| _CANON/ARCS-Canon-v1-1.md:102 | `50+` | - Real-time signal convergence detection across 50+ data streams |
| _CANON/ARCS-Canon-v1-1.md:112 | `000+` | - Receipt database: 100,000+ historical decisions = insurmountable training data advantage |
| _CANON/ARCS-Canon-v1-1.md:118 | `18%` | - **Phase 1** (0-12 months): Better ROAS → 12-18% annual churn |
| _CANON/ARCS-Canon-v1-1.md:119 | `8%` | - **Phase 2** (12-24 months): Platform consolidation → 5-8% annual churn |
| _CANON/ARCS-Canon-v1-1.md:120 | `2%` | - **Phase 3** (24-36 months): Regulatory compliance → <2% annual churn (infrastructure-level) |
| _CANON/ARCS-Canon-v1-1.md:129 | `$102M` | **Capital Strategy** ($102M with <5% dilution): |
| _CANON/ARCS-Canon-v1-1.md:129 | `5%` | **Capital Strategy** ($102M with <5% dilution): |
| _CANON/ARCS-Canon-v1-1.md:130 | `$81M` | 1. **Enterprise Pre-Sale**: $81M from 20 customers (prepaid 3-year contracts at 40% discount) |
| _CANON/ARCS-Canon-v1-1.md:130 | `40%` | 1. **Enterprise Pre-Sale**: $81M from 20 customers (prepaid 3-year contracts at 40% discount) |
| _CANON/ARCS-Canon-v1-1.md:131 | `$12M` | 2. **Token Generation Event**: $12M ($ARCS utility token for ecosystem participation) |
| _CANON/ARCS-Canon-v1-1.md:132 | `$180K` | 3. **Revenue Reinvestment**: $4.3M (currently profitable: $180K/month EBITDA) |
| _CANON/ARCS-Canon-v1-1.md:132 | `$4.3M` | 3. **Revenue Reinvestment**: $4.3M (currently profitable: $180K/month EBITDA) |
| _CANON/ARCS-Canon-v1-1.md:133 | `$5M` | 4. **Strategic Debt**: $5M credit facility |
| _CANON/ARCS-Canon-v1-1.md:135 | `$70M` | **vs. Traditional VC**: $70M with 40-50% dilution |
| _CANON/ARCS-Canon-v1-1.md:135 | `50%` | **vs. Traditional VC**: $70M with 40-50% dilution |
| _CANON/ARCS-Canon-v1-1.md:138 | `$199` | - Individual: Free basic → $49/month Pro → $199/month Premium |
| _CANON/ARCS-Canon-v1-1.md:138 | `$49` | - Individual: Free basic → $49/month Pro → $199/month Premium |
| _CANON/ARCS-Canon-v1-1.md:139 | `$299` | - Team: $299/month (<25 people) → Custom Enterprise |
| _CANON/ARCS-Canon-v1-1.md:140 | `$10K` | - Ecosystem: $10K-50K/year service licensing + research insights |
| _CANON/ARCS-Canon-v1-1.md:142 | `60%` | **36-Month Projections** (Base Case, 60% probability): |
| _CANON/ARCS-Canon-v1-1.md:146 | `$15.2M` | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Canon-v1-1.md:146 | `$412M` | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Canon-v1-1.md:146 | `$98.4M` | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Canon-v1-1.md:147 | `0.008%` | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Canon-v1-1.md:147 | `0.055%` | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Canon-v1-1.md:147 | `0.23%` | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Canon-v1-1.md:148 | `28%` | / EBITDA Margin / -41% / +28% / +44% / |
| _CANON/ARCS-Canon-v1-1.md:148 | `41%` | / EBITDA Margin / -41% / +28% / +44% / |
| _CANON/ARCS-Canon-v1-1.md:148 | `44%` | / EBITDA Margin / -41% / +28% / +44% / |
| _CANON/ARCS-Canon-v1-1.md:149 | `$120M` | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Canon-v1-1.md:149 | `$3.3B` | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Canon-v1-1.md:149 | `$790M` | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Canon-v1-1.md:196 | `$850B` | - Global enterprise marketing: $850B annually |
| _CANON/ARCS-Canon-v1-1.md:197 | `$350B` | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Canon-v1-1.md:197 | `500+` | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Canon-v1-1.md:198 | `$180B` | - Addressable (Fortune 5000 + growth): $180B annually |
| _CANON/ARCS-Canon-v1-1.md:199 | `0.001%` | - **Current penetration**: 0.001% → massive greenfield |
| _CANON/ARCS-Canon-v1-1.md:202 | `$35K` | - 2.3M "cognitive synthesizers" in US underearning $35K/year vs. optimal placement |
| _CANON/ARCS-Canon-v1-1.md:203 | `$51.8B` | - Total addressable earning potential: $51.8B annually |
| _CANON/ARCS-Canon-v1-1.md:204 | `$127B` | - Organizations losing $127B in productivity from suboptimal allocation |
| _CANON/ARCS-Canon-v1-1.md:205 | `$178.8B` | - **Total market**: $178.8B opportunity |
| _CANON/ARCS-Canon-v1-1.md:211 | `30%` | 1. **Slow Enterprise Adoption** (30% probability, high impact) |
| _CANON/ARCS-Canon-v1-1.md:214 | `25%` | 2. **Agency/HR Resistance** (25% probability, medium impact) |
| _CANON/ARCS-Canon-v1-1.md:217 | `60%` | 3. **Large Incumbent Response** (60% probability within 24 months, very high impact) |
| _CANON/ARCS-Canon-v1-1.md:220 | `35%` | 4. **Regulatory Restriction** (35% probability, medium impact) |
| _CANON/ARCS-Canon-v1-1.md:221 | `18+` | - *Mitigation*: Proactive SEC engagement, token as utility not security, pre-sale alone funds 18+ months |
| _CANON/ARCS-Canon-v1-1.md:223 | `20%` | 5. **Technical Execution Failure** (20% probability, very high impact) |
| _CANON/ARCS-Canon-v1-1.md:224 | `20%` | - *Mitigation*: Hire world-class ML/AI leadership, 20% engineering contingency, alpha program validation, performance guarantee exit clause |
| _CANON/ARCS-Canon-v1-1.md:312 | `18%` | - Inventory: CPMs drop 18% (traffic signal) |
| _CANON/ARCS-Canon-v1-1.md:313 | `34%` | - Audience: r/cryptocurrency engagement +34% (audience signal) |
| _CANON/ARCS-Canon-v1-1.md:316 | `$200K` | Action: Increase Reddit budget by $200K immediately |
| _CANON/ARCS-Canon-v1-1.md:317 | `$640K` | Expected Value: $640K incremental return (3.2× on opportunity spend) |
| _CANON/ARCS-Canon-v1-1.md:318 | `$780K` | Actual Outcome: $780K return (3.9×, window captured before close) |
| _CANON/ARCS-Canon-v1-1.md:349 | `over 12` | - Track individuals over 12-18 months post-placement |
| _CANON/ARCS-Canon-v1-1.md:351 | `32%` | - Prediction accuracy: >78% for role sustainability (vs. <32% for skills-based matching) |
| _CANON/ARCS-Canon-v1-1.md:351 | `78%` | - Prediction accuracy: >78% for role sustainability (vs. <32% for skills-based matching) |
| _CANON/ARCS-Canon-v1-1.md:436 | `$2` | ✅ Campaign archetype: "B2B SaaS acquisition, $2-5M budget, Reddit + Meta channels" |
| _CANON/ARCS-Canon-v1-1.md:437 | `32%` | ✅ Pattern: "Mobile creative outperformed desktop 32% in crypto vertical" |
| _CANON/ARCS-Canon-v1-1.md:494 | `95%` | **Key Innovation**: Unlike systems claiming deterministic predictions, this framework provides *honest uncertainty quantification*. A predic |
| _CANON/ARCS-Canon-v1-1.md:512 | `$100K` | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$100K` | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$10M` | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$10M` | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$1M` | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$1M` | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:566 | `68%` | - \(A_0\) = Baseline accuracy with zero network ≈ 68% |
| _CANON/ARCS-Canon-v1-1.md:567 | `92%` | - \(A_{\infty}\) = Asymptotic accuracy at infinite scale ≈ 92% |
| _CANON/ARCS-Canon-v1-1.md:574 | `1%` | / 10              / 5,000    / 69%               / 1% advantage        / |
| _CANON/ARCS-Canon-v1-1.md:574 | `69%` | / 10              / 5,000    / 69%               / 1% advantage        / |
| _CANON/ARCS-Canon-v1-1.md:575 | `77%` | / 100             / 50,000   / 77%               / 8% advantage        / |
| _CANON/ARCS-Canon-v1-1.md:575 | `8%` | / 100             / 50,000   / 77%               / 8% advantage        / |
| _CANON/ARCS-Canon-v1-1.md:576 | `16%` | / 500             / 250,000  / 85%               / 16% advantage       / |
| _CANON/ARCS-Canon-v1-1.md:576 | `85%` | / 500             / 250,000  / 85%               / 16% advantage       / |
| _CANON/ARCS-Canon-v1-1.md:577 | `19%` | / 1,000           / 500,000  / 88%               / 19% advantage       / |
| _CANON/ARCS-Canon-v1-1.md:577 | `88%` | / 1,000           / 500,000  / 88%               / 19% advantage       / |
| _CANON/ARCS-Canon-v1-1.md:579 | `19%` | **Strategic Implication**: By the time platform reaches 500 customers (250K receipts), new entrant faces insurmountable disadvantage. Ration |
| _CANON/ARCS-Canon-v1-1.md:608 | `50%` | - \(\theta\) = Threshold for override (typically 25-50% EV improvement) |
| _CANON/ARCS-Canon-v1-1.md:613 | `$2.1M` | - EV: $2.1M incremental revenue |
| _CANON/ARCS-Canon-v1-1.md:614 | `82%` | - Confidence: 82% |
| _CANON/ARCS-Canon-v1-1.md:618 | `$780K` | - EV: $780K incremental revenue |
| _CANON/ARCS-Canon-v1-1.md:619 | `78%` | - Confidence: 78% |
| _CANON/ARCS-Canon-v1-1.md:622 | `$2.1M` | Arbitration: EV gap ($780K vs $2.1M) doesn't exceed 25% threshold |
| _CANON/ARCS-Canon-v1-1.md:622 | `$780K` | Arbitration: EV gap ($780K vs $2.1M) doesn't exceed 25% threshold |
| _CANON/ARCS-Canon-v1-1.md:622 | `25%` | Arbitration: EV gap ($780K vs $2.1M) doesn't exceed 25% threshold |
| _CANON/ARCS-Canon-v1-1.md:631 | `3+` | 1. **Anomaly Detection**: Identify 3+ σ deviations from baseline across data streams |
| _CANON/ARCS-Canon-v1-1.md:632 | `3+` | 2. **Convergence Check**: Require 3+ positive signals aligning simultaneously |
| _CANON/ARCS-Canon-v1-1.md:701 | `78%` | **Target Accuracy**: >78% prediction of 12-month role sustainability |
| _CANON/ARCS-Canon-v1-1.md:704 | `000+` | - Longitudinal cohort studies (track 1,000+ placements over 18 months) |
| _CANON/ARCS-Canon-v1-1.md:704 | `over 18` | - Longitudinal cohort studies (track 1,000+ placements over 18 months) |
| _CANON/ARCS-Canon-v1-1.md:721 | `32%` | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:721 | `87%` | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:769 | `R = 0.7` | - \(R = 0.7-0.9\): Typical high-performing teams |
| _CANON/ARCS-Canon-v1-1.md:785 | `$350B` | ### Problem Statement: The $350B Accountability Crisis |
| _CANON/ARCS-Canon-v1-1.md:790 | `$850B` | - Global: $850B annually |
| _CANON/ARCS-Canon-v1-1.md:791 | `$350B` | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Canon-v1-1.md:791 | `500+` | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Canon-v1-1.md:792 | `$180B` | - Fortune 5000 + high-growth companies: $180B annually (addressable market) |
| _CANON/ARCS-Canon-v1-1.md:797 | `$50M` | - Marketing leaders allocate $50M+ budgets without documented reasoning |
| _CANON/ARCS-Canon-v1-1.md:812 | `$100K` | - CFOs document every $100K financial decision |
| _CANON/ARCS-Canon-v1-1.md:813 | `$100M` | - CMOs allocate $100M marketing budgets on intuition |
| _CANON/ARCS-Canon-v1-1.md:842 | `40%` | - **Value Prop**: 40% ROAS improvement with performance guarantee |
| _CANON/ARCS-Canon-v1-1.md:845 | `18%` | - **Expected Churn**: 12-18% annually |
| _CANON/ARCS-Canon-v1-1.md:849 | `$5M` | - **Value Prop**: Vendor consolidation saves $5M+ annually |
| _CANON/ARCS-Canon-v1-1.md:852 | `8%` | - **Expected Churn**: 5-8% annually |
| _CANON/ARCS-Canon-v1-1.md:859 | `2%` | - **Expected Churn**: <2% annually (infrastructure-level retention) |
| _CANON/ARCS-Canon-v1-1.md:865 | `18%` | / 1     / 12-18%       / Performance advantage / Moderate (recipe can be copied) / |
| _CANON/ARCS-Canon-v1-1.md:866 | `8%` | / 2     / 5-8%         / Operational dependency / High (data migration expensive) / |
| _CANON/ARCS-Canon-v1-1.md:867 | `2%` | / 3     / <2%          / Legal necessity / Extreme (infinite switching cost) / |
| _CANON/ARCS-Canon-v1-1.md:879 | `$7.5M` | / Private / $7.5M / Zero (hoarded) / 72% / Agency protects asymmetry / |
| _CANON/ARCS-Canon-v1-1.md:879 | `72%` | / Private / $7.5M / Zero (hoarded) / 72% / Agency protects asymmetry / |
| _CANON/ARCS-Canon-v1-1.md:880 | `$4.5M` | / Partial / $4.5M / Anonymized patterns / 82% / Rational middle ground / |
| _CANON/ARCS-Canon-v1-1.md:880 | `82%` | / Partial / $4.5M / Anonymized patterns / 82% / Rational middle ground / |
| _CANON/ARCS-Canon-v1-1.md:881 | `$2.5M` | / Full / $2.5M / All receipts shared / 87% / Transparent agencies win / |
| _CANON/ARCS-Canon-v1-1.md:881 | `87%` | / Full / $2.5M / All receipts shared / 87% / Transparent agencies win / |
| _CANON/ARCS-Canon-v1-1.md:885 | `15%` | 2. Clients observe 15% performance gap vs. Tier 3 |
| _CANON/ARCS-Canon-v1-1.md:902 | `50%` | - **Discrepancy revealed**: Agency stated 4.5× but privately believed 3.0× (50% gap = knowing overpromise) |
| _CANON/ARCS-Canon-v1-1.md:916 | `40%` | **Implementation**: "40% ROAS improvement or full refund" |
| _CANON/ARCS-Canon-v1-1.md:920 | `80%` | - If client followed recommendations ≥80% and failed → ARCS refunds |
| _CANON/ARCS-Canon-v1-1.md:1020 | `$9.5M` | "decision_rationale": "Optimal balance of expected value ($9.5M revenue) vs. risk (24% downside scenarios). Reddit represents 60% allocation |
| _CANON/ARCS-Canon-v1-1.md:1020 | `24%` | "decision_rationale": "Optimal balance of expected value ($9.5M revenue) vs. risk (24% downside scenarios). Reddit represents 60% allocation |
| _CANON/ARCS-Canon-v1-1.md:1020 | `60%` | "decision_rationale": "Optimal balance of expected value ($9.5M revenue) vs. risk (24% downside scenarios). Reddit represents 60% allocation |
| _CANON/ARCS-Canon-v1-1.md:1020 | `94%` | "decision_rationale": "Optimal balance of expected value ($9.5M revenue) vs. risk (24% downside scenarios). Reddit represents 60% allocation |
| _CANON/ARCS-Canon-v1-1.md:1034 | `$40K` | "variance_explanation": "Outperformed due to regulatory clarity announcement creating 18-hour kairos window. Capitalized with $40K additiona |
| _CANON/ARCS-Canon-v1-1.md:1067 | `3+` | - CPM fluctuations (detect 3+ σ deviations from 30-day baseline) |
| _CANON/ARCS-Canon-v1-1.md:1093 | `18%` | ├── Signal 1 (Inventory): Reddit CPMs drop 18% (3.2σ anomaly) |
| _CANON/ARCS-Canon-v1-1.md:1094 | `34%` | ├── Signal 2 (Audience): r/cryptocurrency engagement spike +34% (4.1σ) |
| _CANON/ARCS-Canon-v1-1.md:1100 | `95%` | └── 95% Confidence: [2.1 hours, 8.3 hours] |
| _CANON/ARCS-Canon-v1-1.md:1103 | `$200K` | ├── Incremental Budget: $200K (reallocated from next week's Meta spend) |
| _CANON/ARCS-Canon-v1-1.md:1105 | `$640K` | ├── Expected Return: $640K revenue |
| _CANON/ARCS-Canon-v1-1.md:1106 | `$486K` | └── Risk-Adjusted EV: $486K (76% confidence × $640K return) |
| _CANON/ARCS-Canon-v1-1.md:1106 | `$640K` | └── Risk-Adjusted EV: $486K (76% confidence × $640K return) |
| _CANON/ARCS-Canon-v1-1.md:1106 | `76%` | └── Risk-Adjusted EV: $486K (76% confidence × $640K return) |
| _CANON/ARCS-Canon-v1-1.md:1109 | `$200K` | └── Action: Increase Reddit budget by $200K immediately |
| _CANON/ARCS-Canon-v1-1.md:1110 | `78%` | Confidence: 78% |
| _CANON/ARCS-Canon-v1-1.md:1116 | `$780K` | └── Result: $780K actual return (3.9× ROAS, 22% better than prediction) |
| _CANON/ARCS-Canon-v1-1.md:1116 | `22%` | └── Result: $780K actual return (3.9× ROAS, 22% better than prediction) |
| _CANON/ARCS-Canon-v1-1.md:1121 | `32%` | └── Creative: Mobile-optimized creative outperformed desktop 32% in this window |
| _CANON/ARCS-Canon-v1-1.md:1130 | `$178.8B` | ### Problem Statement: The $178.8B Misallocation Crisis |
| _CANON/ARCS-Canon-v1-1.md:1136 | `$35,000` | - Currently underearning **$35,000 annually** vs. optimal placement |
| _CANON/ARCS-Canon-v1-1.md:1137 | `$51.8B` | - **Total addressable earning potential**: $51.8B annually |
| _CANON/ARCS-Canon-v1-1.md:1138 | `$127B` | - Organizations losing **$127B in productivity** from suboptimal allocation |
| _CANON/ARCS-Canon-v1-1.md:1139 | `$178.8B` | - **Combined opportunity**: $178.8B |
| _CANON/ARCS-Canon-v1-1.md:1167 | `60%` | - 60%+ of cognitive synthesizers are neurodivergent (ADHD, autism, dyslexia) |
| _CANON/ARCS-Canon-v1-1.md:1204 | `$200` | - ❌ Expensive ($200/hour, $50K retainer for executives) |
| _CANON/ARCS-Canon-v1-1.md:1204 | `$50K` | - ❌ Expensive ($200/hour, $50K retainer for executives) |
| _CANON/ARCS-Canon-v1-1.md:1222 | `5+` | - Process: Boolean matching (IF Python AND 5+ years THEN interview) |
| _CANON/ARCS-Canon-v1-1.md:1229 | `87%` | - Output: Probabilistic (87% match with confidence interval) |
| _CANON/ARCS-Canon-v1-1.md:1236 | `68%` | / Skills-Based Matching / 12-month retention / 68% / |
| _CANON/ARCS-Canon-v1-1.md:1237 | `32%` | / Skills-Based Matching / Sustained high performance / 32% / |
| _CANON/ARCS-Canon-v1-1.md:1238 | `91%` | / ARCS Energy-First / 12-month retention / 91% / |
| _CANON/ARCS-Canon-v1-1.md:1239 | `78%` | / ARCS Energy-First / Sustained high performance / 78% / |
| _CANON/ARCS-Canon-v1-1.md:1244 | `$15K` | - Burnout is expensive ($15K-50K per replacement + lost productivity) |
| _CANON/ARCS-Canon-v1-1.md:1248 | `32%` | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:1248 | `87%` | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:1248 | `91%` | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:1350 | `$80K` | "salary_delta": "+$80K", |
| _CANON/ARCS-Canon-v1-1.md:1357 | `$120K` | "salary_delta": "+$120K", |
| _CANON/ARCS-Canon-v1-1.md:1402 | `$120K` | - **Counterfactual wisdom**: Declined $120K higher comp for energy optimization (non-obvious decision) |
| _CANON/ARCS-Canon-v1-1.md:1425 | `000+` | 3. **Path Simulation** (1,000+ trajectories) |
| _CANON/ARCS-Canon-v1-1.md:1444 | `12%` | ├── Direct Application to Climate Startups: 12% success rate |
| _CANON/ARCS-Canon-v1-1.md:1447 | `43%` | ├── Lateral Move to Energy-Adjacent Role: 43% success rate |
| _CANON/ARCS-Canon-v1-1.md:1452 | `28%` | ├── Graduate Degree → Pivot: 28% success rate |
| _CANON/ARCS-Canon-v1-1.md:1454 | `$150K` | │   ├── Cons: 2-year opportunity cost, $150K debt |
| _CANON/ARCS-Canon-v1-1.md:1457 | `73%` | └── Design → Product Pipeline: 73% success rate ⭐ RECOMMENDED |
| _CANON/ARCS-Canon-v1-1.md:1465 | `73%` | Confidence: 73% success rate (highest of all paths) |
| _CANON/ARCS-Canon-v1-1.md:1469 | `$140K` | Comp Trajectory: $140K → $165K → $220K (5-year total) |
| _CANON/ARCS-Canon-v1-1.md:1469 | `$165K` | Comp Trajectory: $140K → $165K → $220K (5-year total) |
| _CANON/ARCS-Canon-v1-1.md:1469 | `$220K` | Comp Trajectory: $140K → $165K → $220K (5-year total) |
| _CANON/ARCS-Canon-v1-1.md:1473 | `73%` | > "We simulated 1,000 paths to senior climate tech role. 73% succeed via design → product pipeline. Critical decision in 4 months: accept la |
| _CANON/ARCS-Canon-v1-1.md:1549 | `92%` | ├── Research Scientist, Climate Modeling Lab (92% match) |
| _CANON/ARCS-Canon-v1-1.md:1552 | `87%` | ├── Senior PM, Open Climate Data Platform (87% match) |
| _CANON/ARCS-Canon-v1-1.md:1555 | `71%` | └── Design Lead, Decarbonization SaaS (71% match) |
| _CANON/ARCS-Canon-v1-1.md:1559 | `23%` | └── BD Manager, Carbon Credits Trading (23% match) |
| _CANON/ARCS-Canon-v1-1.md:1572 | `50+` | - Team size preference (1-5, 5-15, 15-50, 50+) |
| _CANON/ARCS-Canon-v1-1.md:1615 | `000+` | - Longitudinal cohort studies (1,000+ placements tracked 18 months) |
| _CANON/ARCS-Canon-v1-1.md:1619 | `78%` | **Accuracy Target**: >78% prediction of 12-month sustainability |
| _CANON/ARCS-Canon-v1-1.md:1667 | `67%` | > "We filtered 67% noise from your career data. Your true signal shows exceptional pattern recognition and synthesis capabilities that stand |
| _CANON/ARCS-Canon-v1-1.md:1689 | `$2.5M` | - EV: $2.5M lifetime career capital if rested and perform well |
| _CANON/ARCS-Canon-v1-1.md:1690 | `84%` | - Confidence: 84% (strong evidence that burnout → poor interview performance) |
| _CANON/ARCS-Canon-v1-1.md:1695 | `$1.8M` | - EV: $1.8M lifetime career capital if land role despite fatigue |
| _CANON/ARCS-Canon-v1-1.md:1696 | `62%` | - Confidence: 62% (fatigued interview performance risky, but opportunity rare) |
| _CANON/ARCS-Canon-v1-1.md:1699 | `$1.8M` | - EV Comparison: $2.5M (Chronos) vs $1.8M (Kairos) |
| _CANON/ARCS-Canon-v1-1.md:1699 | `$2.5M` | - EV Comparison: $2.5M (Chronos) vs $1.8M (Kairos) |
| _CANON/ARCS-Canon-v1-1.md:1700 | `25%` | - Threshold: 25% improvement needed to override Chronos |
| _CANON/ARCS-Canon-v1-1.md:1701 | `$1.8M` | - Gap: 28% shortfall ($2.5M - $1.8M = $700K opportunity cost) |
| _CANON/ARCS-Canon-v1-1.md:1701 | `$2.5M` | - Gap: 28% shortfall ($2.5M - $1.8M = $700K opportunity cost) |
| _CANON/ARCS-Canon-v1-1.md:1701 | `$700K` | - Gap: 28% shortfall ($2.5M - $1.8M = $700K opportunity cost) |
| _CANON/ARCS-Canon-v1-1.md:1701 | `28%` | - Gap: 28% shortfall ($2.5M - $1.8M = $700K opportunity cost) |
| _CANON/ARCS-Canon-v1-1.md:1948 | `$5` | └── Cost: ~$5-10 per receipt (batched) |
| _CANON/ARCS-Canon-v1-1.md:1953 | `$0.001` | └── Cost: ~$0.001 per receipt |
| _CANON/ARCS-Canon-v1-1.md:2345 | `95%` | # 95% confidence interval (±1.96 standard deviations) |
| _CANON/ARCS-Canon-v1-1.md:2415 | `95%` | # For 95% CI, 95% of actual outcomes should fall within interval |
| _CANON/ARCS-Canon-v1-1.md:2415 | `95%` | # For 95% CI, 95% of actual outcomes should fall within interval |
| _CANON/ARCS-Canon-v1-1.md:2472 | `40%` | predictions.append(('CBR', cbr_pred, 0.4))  # 40% weight |
| _CANON/ARCS-Canon-v1-1.md:2476 | `20%` | predictions.append(('REG', reg_pred, 0.2))  # 20% weight |
| _CANON/ARCS-Canon-v1-1.md:2480 | `25%` | predictions.append(('NN', nn_pred, 0.25))  # 25% weight |
| _CANON/ARCS-Canon-v1-1.md:2484 | `10%` | predictions.append(('BAYES', bayes_pred, 0.1))  # 10% weight |
| _CANON/ARCS-Canon-v1-1.md:2488 | `5%` | predictions.append(('EXPERT', expert_pred, 0.05))  # 5% weight |
| _CANON/ARCS-Canon-v1-1.md:2889 | `$200M` | # Result: Series C announced ($200M) - rapid growth mode |
| _CANON/ARCS-Canon-v1-1.md:2918 | `25%` | self.threshold = 0.25  # Kairos must be 25%+ better to override |
| _CANON/ARCS-Canon-v1-1.md:3023 | `$2` | - Campaign archetypes: "B2B SaaS acquisition, $2-5M budget, Reddit + Meta channels" |
| _CANON/ARCS-Canon-v1-1.md:3024 | `32%` | - Performance benchmarks: "Mobile creative outperformed desktop 32% in crypto vertical" |
| _CANON/ARCS-Canon-v1-1.md:3197 | `92%` | #   'asymptotic_accuracy': 0.92,  # 92% accuracy at infinite customers |
| _CANON/ARCS-Canon-v1-1.md:3198 | `68%` | #   'baseline_accuracy': 0.68,     # 68% with zero network |
| _CANON/ARCS-Canon-v1-1.md:3208 | `1%` | / 10        / 5,000    / 69%      / 1% (negligible)           / |
| _CANON/ARCS-Canon-v1-1.md:3208 | `69%` | / 10        / 5,000    / 69%      / 1% (negligible)           / |
| _CANON/ARCS-Canon-v1-1.md:3209 | `77%` | / 100       / 50,000   / 77%      / 9% (noticeable)           / |
| _CANON/ARCS-Canon-v1-1.md:3209 | `9%` | / 100       / 50,000   / 77%      / 9% (noticeable)           / |
| _CANON/ARCS-Canon-v1-1.md:3210 | `17%` | / 500       / 250,000  / 85%      / 17% (significant)         / |
| _CANON/ARCS-Canon-v1-1.md:3210 | `85%` | / 500       / 250,000  / 85%      / 17% (significant)         / |
| _CANON/ARCS-Canon-v1-1.md:3211 | `20%` | / 1,000     / 500,000  / 88%      / 20% (insurmountable)      / |
| _CANON/ARCS-Canon-v1-1.md:3211 | `88%` | / 1,000     / 500,000  / 88%      / 20% (insurmountable)      / |
| _CANON/ARCS-Canon-v1-1.md:3215 | `17%` | By the time platform reaches 500 customers (250K receipts), new entrant faces 17% accuracy disadvantage. Rational customers prefer establish |
| _CANON/ARCS-Canon-v1-1.md:3334 | `18%` | └── Churn: 12-18% annually |
| _CANON/ARCS-Canon-v1-1.md:3337 | `40+` | └── Position: "Replace 40+ tools with one platform" |
| _CANON/ARCS-Canon-v1-1.md:3339 | `8%` | └── Churn: 5-8% annually |
| _CANON/ARCS-Canon-v1-1.md:3344 | `2%` | └── Churn: <2% annually |
| _CANON/ARCS-Canon-v1-1.md:3349 | `40%` | **Value Proposition**: "40% ROAS improvement with performance guarantee" |
| _CANON/ARCS-Canon-v1-1.md:3367 | `$500K` | - Select 1-2 campaigns for pilot ($500K-2M budget) |
| _CANON/ARCS-Canon-v1-1.md:3384 | `19+` | Week 19+: Expansion |
| _CANON/ARCS-Canon-v1-1.md:3395 | `$150K` | / Pilot / $150K / 2-5 / 50-200 / Basic / Proof of concept / |
| _CANON/ARCS-Canon-v1-1.md:3396 | `$750K` | / Growth / $750K / 10-30 / 500-2000 / Standard / Mid-market / |
| _CANON/ARCS-Canon-v1-1.md:3397 | `$2.5M` | / Enterprise / $2.5M / Unlimited / Unlimited / Premium / Fortune 1000 / |
| _CANON/ARCS-Canon-v1-1.md:3402 | `10%` | If ARCS-recommended campaigns underperform baseline by >10%: |
| _CANON/ARCS-Canon-v1-1.md:3403 | `80%` | AND client followed ≥80% of recommendations: |
| _CANON/ARCS-Canon-v1-1.md:3404 | `50%` | THEN full refund + next year 50% discount |
| _CANON/ARCS-Canon-v1-1.md:3413 | `$15.2M` | - $15.2M ARR |
| _CANON/ARCS-Canon-v1-1.md:3414 | `120%` | - Net Revenue Retention: 120% (expansion within accounts) |
| _CANON/ARCS-Canon-v1-1.md:3416 | `87%` | - Prediction accuracy: 87% (actual outcomes within stated confidence intervals) |
| _CANON/ARCS-Canon-v1-1.md:3420 | `$5M` | **Value Proposition**: "Eliminate $5M+ in redundant vendors" |
| _CANON/ARCS-Canon-v1-1.md:3426 | `$200K` | - CDP (Segment, mParticle): $200K/year |
| _CANON/ARCS-Canon-v1-1.md:3427 | `$150K` | - DMP (Adobe Audience Manager): $150K/year |
| _CANON/ARCS-Canon-v1-1.md:3428 | `$300K` | - CRM (Salesforce Marketing Cloud): $300K/year |
| _CANON/ARCS-Canon-v1-1.md:3431 | `$180K` | - Attribution (Rockerbox, Neustar): $180K/year |
| _CANON/ARCS-Canon-v1-1.md:3432 | `$120K` | - Web Analytics (Adobe Analytics): $120K/year |
| _CANON/ARCS-Canon-v1-1.md:3433 | `$80K` | - Product Analytics (Amplitude): $80K/year |
| _CANON/ARCS-Canon-v1-1.md:3436 | `$100K` | - Marketing Automation (Marketo, Eloqua): $100K/year |
| _CANON/ARCS-Canon-v1-1.md:3437 | `$200K` | - Social Management (Sprinklr): $200K/year |
| _CANON/ARCS-Canon-v1-1.md:3438 | `$60K` | - Email Platform (Iterable): $60K/year |
| _CANON/ARCS-Canon-v1-1.md:3441 | `$30K` | - Project Management (Monday.com): $30K/year |
| _CANON/ARCS-Canon-v1-1.md:3442 | `$75K` | - Creative Management (Bynder): $75K/year |
| _CANON/ARCS-Canon-v1-1.md:3443 | `$50K` | - Approvals (Workfront): $50K/year |
| _CANON/ARCS-Canon-v1-1.md:3445 | `$1.545M` | Total: $1.545M/year in licensing fees alone |
| _CANON/ARCS-Canon-v1-1.md:3446 | `$2` | + $2-3M/year in integration maintenance, training, overhead |
| _CANON/ARCS-Canon-v1-1.md:3447 | `$3.5` | = $3.5-4.5M total martech cost |
| _CANON/ARCS-Canon-v1-1.md:3462 | `$3` | Year 3 (Phase 3): Full replacement → Customer saves $3-4M annually |
| _CANON/ARCS-Canon-v1-1.md:3490 | `$500K` | - Data migration: 6-12 months, $500K-2M cost |
| _CANON/ARCS-Canon-v1-1.md:3491 | `$200K` | - Team retraining: 3-6 months, $200K-500K cost |
| _CANON/ARCS-Canon-v1-1.md:3492 | `$300K` | - Integration rebuild: $300K-800K cost |
| _CANON/ARCS-Canon-v1-1.md:3495 | `$1M` | **Total Switching Cost**: $1M-3.5M + 9-18 months disruption |
| _CANON/ARCS-Canon-v1-1.md:3497 | `18%` | **Expected Churn**: 5-8% annually (vs. 12-18% in Phase 1) |
| _CANON/ARCS-Canon-v1-1.md:3497 | `8%` | **Expected Churn**: 5-8% annually (vs. 12-18% in Phase 1) |
| _CANON/ARCS-Canon-v1-1.md:3503 | `$3.5M` | / Platform / $3.5M / Replace $4.5M martech stack / Enterprise (5,000+ employees) / |
| _CANON/ARCS-Canon-v1-1.md:3503 | `$4.5M` | / Platform / $3.5M / Replace $4.5M martech stack / Enterprise (5,000+ employees) / |
| _CANON/ARCS-Canon-v1-1.md:3503 | `000+` | / Platform / $3.5M / Replace $4.5M martech stack / Enterprise (5,000+ employees) / |
| _CANON/ARCS-Canon-v1-1.md:3504 | `$5M` | / Enterprise+ / $5M / + Custom integrations, dedicated CSM / Fortune 500 / |
| _CANON/ARCS-Canon-v1-1.md:3510 | `$98.4M` | - $98.4M ARR |
| _CANON/ARCS-Canon-v1-1.md:3511 | `5%` | - Gross retention: 95% (only 5% churn) |
| _CANON/ARCS-Canon-v1-1.md:3511 | `95%` | - Gross retention: 95% (only 5% churn) |
| _CANON/ARCS-Canon-v1-1.md:3512 | `130%` | - Net retention: 130% (expansion + upsells) |
| _CANON/ARCS-Canon-v1-1.md:3513 | `$1.16M` | - Average contract value: $1.16M (up from $507K in Phase 1) |
| _CANON/ARCS-Canon-v1-1.md:3513 | `$507K` | - Average contract value: $1.16M (up from $507K in Phase 1) |
| _CANON/ARCS-Canon-v1-1.md:3526 | `$50M` | - Proposal: Extend disclosure requirements to marketing spend >$50M |
| _CANON/ARCS-Canon-v1-1.md:3540 | `$10M` | - Fiduciary duty requires documented rationale for $10M+ allocations |
| _CANON/ARCS-Canon-v1-1.md:3547 | `$1M` | - Document financial decisions >$1M |
| _CANON/ARCS-Canon-v1-1.md:3552 | `$50M` | - Marketing is $50M-500M for Fortune 1000 |
| _CANON/ARCS-Canon-v1-1.md:3568 | `$4M` | 2026: "We choose ARCS because it saves $4M in martech costs" |
| _CANON/ARCS-Canon-v1-1.md:3578 | `3+` | - 3+ years of decision receipts (50K-200K) |
| _CANON/ARCS-Canon-v1-1.md:3607 | `$10M` | / Compliance / $4M / Required for regulatory adherence / vs. $10M+ litigation risk / |
| _CANON/ARCS-Canon-v1-1.md:3607 | `$4M` | / Compliance / $4M / Required for regulatory adherence / vs. $10M+ litigation risk / |
| _CANON/ARCS-Canon-v1-1.md:3608 | `$20M` | / Governance / $6M / Board-grade reporting + audit support / vs. $20M+ shareholder derivative suit / |
| _CANON/ARCS-Canon-v1-1.md:3608 | `$6M` | / Governance / $6M / Board-grade reporting + audit support / vs. $20M+ shareholder derivative suit / |
| _CANON/ARCS-Canon-v1-1.md:3609 | `$10M` | / Strategic / $10M+ / Executive decision intelligence + IP licensing / vs. Competitive disadvantage / |
| _CANON/ARCS-Canon-v1-1.md:3614 | `$412M` | - $412M ARR |
| _CANON/ARCS-Canon-v1-1.md:3615 | `98%` | - Gross retention: 98% (near-zero voluntary churn) |
| _CANON/ARCS-Canon-v1-1.md:3616 | `140%` | - Net retention: 140% (expansion despite high base) |
| _CANON/ARCS-Canon-v1-1.md:3617 | `$2.35M` | - Average contract value: $2.35M |
| _CANON/ARCS-Canon-v1-1.md:3618 | `0.23%` | - Market share: 0.23% (but growing 120% YoY) |
| _CANON/ARCS-Canon-v1-1.md:3618 | `120%` | - Market share: 0.23% (but growing 120% YoY) |
| _CANON/ARCS-Canon-v1-1.md:3626 | `$4M` | - 2 Enterprise AEs (quota: $4M ARR each) |
| _CANON/ARCS-Canon-v1-1.md:3633 | `$6M` | - 8 Enterprise AEs ($6M quota each) |
| _CANON/ARCS-Canon-v1-1.md:3642 | `$8M` | - 25 Enterprise AEs ($8M quota each) |
| _CANON/ARCS-Canon-v1-1.md:3653 | `60%` | **Inbound (60% of pipeline)**: |
| _CANON/ARCS-Canon-v1-1.md:3660 | `40%` | **Outbound (40% of pipeline)**: |
| _CANON/ARCS-Canon-v1-1.md:3691 | `17%` | - **Strategy**: "Network effects. Our predictions are 17% better because we have more data." |
| _CANON/ARCS-Canon-v1-1.md:3695 | `$1M` | - **Our Advantage**: Scalable software vs. expensive consultants ($1M/year vs. $5M/engagement) |
| _CANON/ARCS-Canon-v1-1.md:3695 | `$5M` | - **Our Advantage**: Scalable software vs. expensive consultants ($1M/year vs. $5M/engagement) |
| _CANON/ARCS-Canon-v1-1.md:3709 | `$5` | - **Defensive Value**: $5-8M (forces competitors to license or build inferior alternative) |
| _CANON/ARCS-Canon-v1-1.md:3714 | `$12` | - **Defensive Value**: $12-20M (extremely difficult to design around) |
| _CANON/ARCS-Canon-v1-1.md:3719 | `$3` | - **Defensive Value**: $3-5M (foundational but many alternatives exist) |
| _CANON/ARCS-Canon-v1-1.md:3724 | `$4` | - **Defensive Value**: $4-7M (increasingly important with privacy regulations) |
| _CANON/ARCS-Canon-v1-1.md:3729 | `$2` | - **Defensive Value**: $2-4M (novel but narrow application) |
| _CANON/ARCS-Canon-v1-1.md:3731 | `$26` | **Total Portfolio Value**: $26-44M (conservative estimates) |
| _CANON/ARCS-Canon-v1-1.md:3740 | `5%` | - Revenue share model: 5% of gross revenue using patented technology |
| _CANON/ARCS-Canon-v1-1.md:3764 | `1000+` | - Domain-specific knowledge from 1000+ detected opportunities |
| _CANON/ARCS-Canon-v1-1.md:3784 | `72%` | - Baseline prediction accuracy: 72% |
| _CANON/ARCS-Canon-v1-1.md:3788 | `82%` | - Accuracy: 82% |
| _CANON/ARCS-Canon-v1-1.md:3789 | `10%` | - Advantage: 10% better than new entrant (significant) |
| _CANON/ARCS-Canon-v1-1.md:3792 | `87%` | - Accuracy: 87% |
| _CANON/ARCS-Canon-v1-1.md:3793 | `15%` | - Advantage: 15% better than Year 1 competitor (customer-visible) |
| _CANON/ARCS-Canon-v1-1.md:3796 | `92%` | - Accuracy: 92% |
| _CANON/ARCS-Canon-v1-1.md:3797 | `20%` | - Advantage: 20% better than Year 3 competitor (insurmountable) |
| _CANON/ARCS-Canon-v1-1.md:3804 | `2+` | 3. **Cold Start Problem**: New entrant starts at 68% accuracy, must convince customers to tolerate inferior predictions for 2+ years |
| _CANON/ARCS-Canon-v1-1.md:3804 | `68%` | 3. **Cold Start Problem**: New entrant starts at 68% accuracy, must convince customers to tolerate inferior predictions for 2+ years |
| _CANON/ARCS-Canon-v1-1.md:3812 | `2029+` | 2029+: Maintain lead (continuous data accumulation faster than competition) |
| _CANON/ARCS-Canon-v1-1.md:3839 | `2029+` | **2029+: Market Requirement** |
| _CANON/ARCS-Canon-v1-1.md:3865 | `80%` | - Search volume: "decision receipts" = 50K/month (80% ARCS-branded content) |
| _CANON/ARCS-Canon-v1-1.md:3869 | `2028+` | 2028+: Generic trademark risk |
| _CANON/ARCS-Canon-v1-1.md:3875 | `$50` | **Brand Value**: $50-100M (category ownership drives customer acquisition cost to near-zero) |
| _CANON/ARCS-Canon-v1-1.md:4021 | `80%` | **Stream 1: Enterprise Software Licensing** (80% of revenue) |
| _CANON/ARCS-Canon-v1-1.md:4024 | `$412M` | - Target: $412M ARR by Year 3 |
| _CANON/ARCS-Canon-v1-1.md:4026 | `10%` | **Stream 2: Ecosystem Service Licensing** (10% of revenue) |
| _CANON/ARCS-Canon-v1-1.md:4029 | `$40M` | - Target: $40M ARR by Year 3 |
| _CANON/ARCS-Canon-v1-1.md:4031 | `5%` | **Stream 3: Research Partnerships** (5% of revenue) |
| _CANON/ARCS-Canon-v1-1.md:4035 | `$20M` | - Target: $20M ARR by Year 3 |
| _CANON/ARCS-Canon-v1-1.md:4037 | `5%` | **Stream 4: Token Ecosystem** (5% of revenue) |
| _CANON/ARCS-Canon-v1-1.md:4039 | `10%` | - Foundation takes 10% transaction fee |
| _CANON/ARCS-Canon-v1-1.md:4040 | `$20M` | - Target: $20M ARR by Year 3 |
| _CANON/ARCS-Canon-v1-1.md:4047 | `$164M` | Engineering (40%): $164M |
| _CANON/ARCS-Canon-v1-1.md:4047 | `40%` | Engineering (40%): $164M |
| _CANON/ARCS-Canon-v1-1.md:4048 | `$200K` | - 450 engineers ($200K avg loaded cost) |
| _CANON/ARCS-Canon-v1-1.md:4052 | `$103M` | Sales & Marketing (25%): $103M |
| _CANON/ARCS-Canon-v1-1.md:4052 | `25%` | Sales & Marketing (25%): $103M |
| _CANON/ARCS-Canon-v1-1.md:4053 | `$450K` | - 95 sales team members ($450K avg loaded cost including quotas) |
| _CANON/ARCS-Canon-v1-1.md:4056 | `$41M` | Customer Success (10%): $41M |
| _CANON/ARCS-Canon-v1-1.md:4056 | `10%` | Customer Success (10%): $41M |
| _CANON/ARCS-Canon-v1-1.md:4060 | `$41M` | G&A (10%): $41M |
| _CANON/ARCS-Canon-v1-1.md:4060 | `10%` | G&A (10%): $41M |
| _CANON/ARCS-Canon-v1-1.md:4064 | `$21M` | Foundation Operations (5%): $21M |
| _CANON/ARCS-Canon-v1-1.md:4064 | `5%` | Foundation Operations (5%): $21M |
| _CANON/ARCS-Canon-v1-1.md:4069 | `$10M` | R&D (Tax Credit): -$10M |
| _CANON/ARCS-Canon-v1-1.md:4070 | `6%` | - R&D tax credits (~6% of engineering spend) |
| _CANON/ARCS-Canon-v1-1.md:4072 | `$360M` | Total: $360M |
| _CANON/ARCS-Canon-v1-1.md:4073 | `$52M` | EBITDA: $52M (13% margin) |
| _CANON/ARCS-Canon-v1-1.md:4073 | `13%` | EBITDA: $52M (13% margin) |
| _CANON/ARCS-Canon-v1-1.md:4079 | `$6.2M` | Year 1: -$6.2M EBITDA (-41% margin) - investment phase |
| _CANON/ARCS-Canon-v1-1.md:4079 | `41%` | Year 1: -$6.2M EBITDA (-41% margin) - investment phase |
| _CANON/ARCS-Canon-v1-1.md:4080 | `$28M` | Year 2: +$28M EBITDA (+28% margin) - scale efficiency |
| _CANON/ARCS-Canon-v1-1.md:4080 | `28%` | Year 2: +$28M EBITDA (+28% margin) - scale efficiency |
| _CANON/ARCS-Canon-v1-1.md:4081 | `$180M` | Year 3: +$180M EBITDA (+44% margin) - platform maturity |
| _CANON/ARCS-Canon-v1-1.md:4081 | `44%` | Year 3: +$180M EBITDA (+44% margin) - platform maturity |
| _CANON/ARCS-Canon-v1-1.md:4082 | `$800M` | Year 5: +$800M EBITDA (+55% margin) - infrastructure lock-in |
| _CANON/ARCS-Canon-v1-1.md:4082 | `55%` | Year 5: +$800M EBITDA (+55% margin) - infrastructure lock-in |
| _CANON/ARCS-Canon-v1-1.md:4090 | `40%` | (40%) Reinvestment in product |
| _CANON/ARCS-Canon-v1-1.md:4093 | `30%` | (30%) Foundation endowment |
| _CANON/ARCS-Canon-v1-1.md:4096 | `20%` | (20%) Employee profit sharing |
| _CANON/ARCS-Canon-v1-1.md:4099 | `10%` | (10%) Shareholder distributions |
| _CANON/ARCS-Canon-v1-1.md:4115 | `15%` | Founder voting control: 55% (even with <15% economic ownership) |
| _CANON/ARCS-Canon-v1-1.md:4115 | `55%` | Founder voting control: 55% (even with <15% economic ownership) |
| _CANON/ARCS-Canon-v1-1.md:4138 | `$100B` | (b) Has market capitalization >$100B |
| _CANON/ARCS-Canon-v1-1.md:4155 | `$412M` | - $412M ARR (Year 3) growing 120% YoY → $900M ARR (Year 4) |
| _CANON/ARCS-Canon-v1-1.md:4155 | `$900M` | - $412M ARR (Year 3) growing 120% YoY → $900M ARR (Year 4) |
| _CANON/ARCS-Canon-v1-1.md:4155 | `120%` | - $412M ARR (Year 3) growing 120% YoY → $900M ARR (Year 4) |
| _CANON/ARCS-Canon-v1-1.md:4157 | `$9` | - Valuation: $9-13.5B |
| _CANON/ARCS-Canon-v1-1.md:4160 | `100%` | - Pre-IPO ownership: 55% (diluted from 100% via pre-sale, debt, token) |
| _CANON/ARCS-Canon-v1-1.md:4160 | `55%` | - Pre-IPO ownership: 55% (diluted from 100% via pre-sale, debt, token) |
| _CANON/ARCS-Canon-v1-1.md:4161 | `$5` | - Post-IPO value: $5-7.4B |
| _CANON/ARCS-Canon-v1-1.md:4162 | `10%` | - Lockup: Standard 180 days, then 10% per year sale limit |
| _CANON/ARCS-Canon-v1-1.md:4223 | `$2M` | - $2M/year unrestricted research grant |
| _CANON/ARCS-Canon-v1-1.md:4236 | `$500K` | - $500K/year focused research grants |
| _CANON/ARCS-Canon-v1-1.md:4266 | `95%` | - Tertiary: Calibration (do 95% CIs actually contain 95% of outcomes?) |
| _CANON/ARCS-Canon-v1-1.md:4266 | `95%` | - Tertiary: Calibration (do 95% CIs actually contain 95% of outcomes?) |
| _CANON/ARCS-Canon-v1-1.md:4269 | `68%` | H1: ARCS accuracy > 85% (vs. H0: ≤68% baseline) |
| _CANON/ARCS-Canon-v1-1.md:4269 | `85%` | H1: ARCS accuracy > 85% (vs. H0: ≤68% baseline) |
| _CANON/ARCS-Canon-v1-1.md:4270 | `15%` | H2: ARCS MAPE < 15% (vs. H0: ≥22% baseline) |
| _CANON/ARCS-Canon-v1-1.md:4270 | `22%` | H2: ARCS MAPE < 15% (vs. H0: ≥22% baseline) |
| _CANON/ARCS-Canon-v1-1.md:4271 | `p<0.05` | H3: ARCS predictions well-calibrated (χ² test, p<0.05) |
| _CANON/ARCS-Canon-v1-1.md:4297 | `32%` | H1: ARCS energy sustainability prediction >78% (vs. H0: ≤32% skills-based) |
| _CANON/ARCS-Canon-v1-1.md:4297 | `78%` | H1: ARCS energy sustainability prediction >78% (vs. H0: ≤32% skills-based) |
| _CANON/ARCS-Canon-v1-1.md:4327 | `$400K` | H2: Average window value $400K-800K incremental return |
| _CANON/ARCS-Canon-v1-1.md:4328 | `85%` | H3: Competitors miss 85%+ of windows (discovered post-close) |
| _CANON/ARCS-Canon-v1-1.md:4357 | `24%` | H2: Logarithmic improvement: Acc(N) ≈ 92% - 24% × exp(-0.000012 × N) |
| _CANON/ARCS-Canon-v1-1.md:4357 | `92%` | H2: Logarithmic improvement: Acc(N) ≈ 92% - 24% × exp(-0.000012 × N) |
| _CANON/ARCS-Canon-v1-1.md:4371 | `$30K` | Award: $50K/year stipend + $30K research budget + tuition |
| _CANON/ARCS-Canon-v1-1.md:4371 | `$50K` | Award: $50K/year stipend + $30K research budget + tuition |
| _CANON/ARCS-Canon-v1-1.md:4406 | `$1.5` | - **Award Size**: $1.5-3M over 3-4 years |
| _CANON/ARCS-Canon-v1-1.md:4406 | `over 3` | - **Award Size**: $1.5-3M over 3-4 years |
| _CANON/ARCS-Canon-v1-1.md:4413 | `$500K` | - **Award Size**: $500K-1.5M over 2-3 years |
| _CANON/ARCS-Canon-v1-1.md:4413 | `over 2` | - **Award Size**: $500K-1.5M over 2-3 years |
| _CANON/ARCS-Canon-v1-1.md:4422 | `$2` | - **Award Size**: $2-4M over 4-5 years |
| _CANON/ARCS-Canon-v1-1.md:4422 | `over 4` | - **Award Size**: $2-4M over 4-5 years |
| _CANON/ARCS-Canon-v1-1.md:4431 | `over 3` | - **Award Size**: €3-8M over 3-4 years |
| _CANON/ARCS-Canon-v1-1.md:4447 | `over 18` | - **Award Size**: £500K-2M over 18-36 months |
| _CANON/ARCS-Canon-v1-1.md:4456 | `$2.5M` | - **Award Size**: CAD $2.5M over 4-7 years |
| _CANON/ARCS-Canon-v1-1.md:4456 | `over 4` | - **Award Size**: CAD $2.5M over 4-7 years |
| _CANON/ARCS-Canon-v1-1.md:4462 | `$20` | **Total Projected Grant Funding (2026-2030)**: $20-35M |
| _CANON/ARCS-Canon-v1-1.md:4469 | `$300K` | - **Award Size**: $300K-1M over 2-3 years |
| _CANON/ARCS-Canon-v1-1.md:4469 | `over 2` | - **Award Size**: $300K-1M over 2-3 years |
| _CANON/ARCS-Canon-v1-1.md:4476 | `$500K` | - **Award Size**: $500K-2M over 3 years |
| _CANON/ARCS-Canon-v1-1.md:4476 | `over 3` | - **Award Size**: $500K-2M over 3 years |
| _CANON/ARCS-Canon-v1-1.md:4483 | `$1` | - **Award Size**: $1-3M over 2-4 years |
| _CANON/ARCS-Canon-v1-1.md:4483 | `over 2` | - **Award Size**: $1-3M over 2-4 years |
| _CANON/ARCS-Canon-v1-1.md:4490 | `$3` | - **Award Size**: $3-5M over 3-5 years |
| _CANON/ARCS-Canon-v1-1.md:4490 | `over 3` | - **Award Size**: $3-5M over 3-5 years |
| _CANON/ARCS-Canon-v1-1.md:4494 | `$10` | **Total Projected Private Foundation Funding (2026-2030)**: $10-18M |
| _CANON/ARCS-Canon-v1-1.md:4501 | `$2M` | **Structure**: Joint research lab, $2M/year, 3-year commitment |
| _CANON/ARCS-Canon-v1-1.md:4507 | `$1.5M` | **Structure**: Dataset sharing, model co-development, $1.5M/year |
| _CANON/ARCS-Canon-v1-1.md:4516 | `$15` | **Total Corporate Research Funding (2026-2030)**: $15-25M |
| _CANON/ARCS-Canon-v1-1.md:4738 | `30+` | 2026: Proven ROI, expanding adoption (30+ customers) |
| _CANON/ARCS-Canon-v1-1.md:4752 | `$100M` | 3. **Fiduciary Duty Evolution**: What boards tolerated in 2020 (undocumented $100M allocations) will be liability in 2030 |
| _CANON/ARCS-Canon-v1-1.md:4771 | `$50K` | Current: $50K/week for advice with no accountability |
| _CANON/ARCS-Canon-v1-1.md:4775 | `30%` | Current: 30% first-year salary for placement (often bad fit) |
| _CANON/ARCS-Canon-v1-1.md:4813 | `$127M` | - Job market sees: 847 decisions, 72% accuracy, $127M value created |
| _CANON/ARCS-Canon-v1-1.md:4813 | `72%` | - Job market sees: 847 decisions, 72% accuracy, $127M value created |
| _CANON/ARCS-Canon-v1-1.md:4830 | `78%` | - Real-time updates ("847 companies tried X this week, 78% failed, here's why") |
| _CANON/ARCS-Canon-v2-0-Complete.md:161 | `90%` | - **High Coherence:** Rowers synchronize strokes, boat cuts straight through water, 90% of energy → forward motion (low entropy, high alignm |
| _CANON/ARCS-Canon-v2-0-Complete.md:272 | `p < 0.0001` | **Statistical Significance:** Paired t-test: \(t = 14.2\), \(p < 0.0001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:333 | `78%` | **Claim:** SecondDerivative detects trend reversals 24-48 hours before they occur, with 78% accuracy. |
| _CANON/ARCS-Canon-v2-0-Complete.md:424 | `15%` | **Claim:** WaveDiffusion predicts saturation point within 15% accuracy, 82% of the time. |
| _CANON/ARCS-Canon-v2-0-Complete.md:424 | `82%` | **Claim:** WaveDiffusion predicts saturation point within 15% accuracy, 82% of the time. |
| _CANON/ARCS-Canon-v2-0-Complete.md:428 | `90%` | For viral content, define **saturation** as: \(S(t_{sat}) = 0.9 \times S_{max}\) (reached 90% of maximum engagement). |
| _CANON/ARCS-Canon-v2-0-Complete.md:446 | `15%` | - **Within 15% error:** 1,022 threads (82%) |
| _CANON/ARCS-Canon-v2-0-Complete.md:446 | `82%` | - **Within 15% error:** 1,022 threads (82%) |
| _CANON/ARCS-Canon-v2-0-Complete.md:447 | `11%` | - **Median error:** 11% |
| _CANON/ARCS-Canon-v2-0-Complete.md:448 | `p < 0.0001` | - **Correlation:** \(r = 0.87\), \(p < 0.0001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:448 | `r = 0.87` | - **Correlation:** \(r = 0.87\), \(p < 0.0001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:494 | `1+` | Interference is **energy superposition**. Constructive interference = energy adds (1+1=2). Destructive interference = energy cancels (1+1=0) |
| _CANON/ARCS-Canon-v2-0-Complete.md:494 | `1+` | Interference is **energy superposition**. Constructive interference = energy adds (1+1=2). Destructive interference = energy cancels (1+1=0) |
| _CANON/ARCS-Canon-v2-0-Complete.md:513 | `35%` | **Claim:** Spacing campaigns by \(T/4\) improves ROAS by 35% compared to uncoordinated launch. |
| _CANON/ARCS-Canon-v2-0-Complete.md:534 | `34%` | / Baseline / 2.17 / 0.42 / 34% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:535 | `8%` | / Optimized / 2.93 / 0.51 / 8% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:540 | `p < 0.001` | - Independent samples t-test: \(t = 7.23\), \(p < 0.001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:541 | `28%` | - 95% CI for improvement: [28%, 42%] |
| _CANON/ARCS-Canon-v2-0-Complete.md:541 | `42%` | - 95% CI for improvement: [28%, 42%] |
| _CANON/ARCS-Canon-v2-0-Complete.md:541 | `95%` | - 95% CI for improvement: [28%, 42%] |
| _CANON/ARCS-Canon-v2-0-Complete.md:609 | `45%` | **Claim:** Detecting deceleration and reallocating budget reduces wasted spend by 45%. |
| _CANON/ARCS-Canon-v2-0-Complete.md:614 | `10%` | - **Baseline:** Continue spending on all content until engagement drops below 10% of peak |
| _CANON/ARCS-Canon-v2-0-Complete.md:615 | `30%` | - **Decelerator:** Cut spending when \(D_{severity} > 0.3\) (30% deceleration rate) |
| _CANON/ARCS-Canon-v2-0-Complete.md:622 | `$127K` | - **Wasted spend:** $127K (spent on declining content) |
| _CANON/ARCS-Canon-v2-0-Complete.md:623 | `$890K` | - **Total spend:** $890K |
| _CANON/ARCS-Canon-v2-0-Complete.md:624 | `14.3%` | - **Waste ratio:** 14.3% |
| _CANON/ARCS-Canon-v2-0-Complete.md:627 | `$69K` | - **Wasted spend:** $69K |
| _CANON/ARCS-Canon-v2-0-Complete.md:628 | `$890K` | - **Total spend:** $890K (same budget, reallocated earlier) |
| _CANON/ARCS-Canon-v2-0-Complete.md:629 | `7.8%` | - **Waste ratio:** 7.8% |
| _CANON/ARCS-Canon-v2-0-Complete.md:635 | `10%` | Most campaigns follow power-law decay: \(S(t) \propto t^{-\alpha}\). By the time engagement drops to 10% of peak, you've already wasted 80%  |
| _CANON/ARCS-Canon-v2-0-Complete.md:635 | `80%` | Most campaigns follow power-law decay: \(S(t) \propto t^{-\alpha}\). By the time engagement drops to 10% of peak, you've already wasted 80%  |
| _CANON/ARCS-Canon-v2-0-Complete.md:711 | `3%` | - **Momentum Strategy:** Buy when 1-hour return > 3%, sell when < -3% |
| _CANON/ARCS-Canon-v2-0-Complete.md:711 | `3%` | - **Momentum Strategy:** Buy when 1-hour return > 3%, sell when < -3% |
| _CANON/ARCS-Canon-v2-0-Complete.md:718 | `83%` | / Sharpe Ratio / 0.73 / 1.34 / 83% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:719 | `15.2%` | / Total Return / 15.2% / 25.8% / 70% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:719 | `25.8%` | / Total Return / 15.2% / 25.8% / 70% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:719 | `70%` | / Total Return / 15.2% / 25.8% / 70% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:720 | `11.8%` | / Max Drawdown / -11.8% / -5.1% / 57% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:720 | `5.1%` | / Max Drawdown / -11.8% / -5.1% / 57% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:720 | `57%` | / Max Drawdown / -11.8% / -5.1% / 57% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:721 | `19%` | / Win Rate / 54% / 64% / 19% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:721 | `54%` | / Win Rate / 54% / 64% / 19% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:721 | `64%` | / Win Rate / 54% / 64% / 19% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:724 | `p < 0.001` | - Bootstrap test (10,000 iterations): \(p < 0.001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:725 | `95%` | - 95% CI for Sharpe difference: [0.46, 0.76] |
| _CANON/ARCS-Canon-v2-0-Complete.md:789 | `28%` | **Claim:** ContentOrchestration improves cost-per-acquisition by 28% and reach by 42%. |
| _CANON/ARCS-Canon-v2-0-Complete.md:789 | `42%` | **Claim:** ContentOrchestration improves cost-per-acquisition by 28% and reach by 42%. |
| _CANON/ARCS-Canon-v2-0-Complete.md:803 | `35%` | / ROAS / 2.17 / 2.93 / 35% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:804 | `$30` | / Cost per Acquisition / $42 / $30 / 28% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:804 | `$42` | / Cost per Acquisition / $42 / $30 / 28% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:804 | `28%` | / Cost per Acquisition / $42 / $30 / 28% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:805 | `42%` | / Total Reach / 487K / 691K / 42% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:806 | `12%` | / Audience Fatigue (complaints) / 12% / 4% / 67% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:806 | `4%` | / Audience Fatigue (complaints) / 12% / 4% / 67% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:806 | `67%` | / Audience Fatigue (complaints) / 12% / 4% / 67% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:874 | `$67K` | "action": "Enter long position BTC $67K", |
| _CANON/ARCS-Canon-v2-0-Complete.md:938 | `90%` | 2. **Base rate:** "90% of new products fail in Year 1. Why is X different?" |
| _CANON/ARCS-Canon-v2-0-Complete.md:940 | `90%` | 4. **Bayesian:** "We have 2 weeks of data. Is that enough to overcome 90% base failure rate?" |
| _CANON/ARCS-Canon-v2-0-Complete.md:1045 | `$10K` | **Decision (T=0):** "Invest $10K in marketing campaign X. Expected ROI: 2.5x." |
| _CANON/ARCS-Canon-v2-0-Complete.md:1047 | `$18K` | **Outcome (T=3 months):** Actual revenue = $18K. Actual ROI = 1.8x. |
| _CANON/ARCS-Canon-v2-0-Complete.md:1050 | `28%` | - Prediction error: \(/2.5 - 1.8/ = 0.7\) (28% overestimate) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1052 | `15%` | - Update: Reduce FirstDerivative weight by 15% for future campaigns |
| _CANON/ARCS-Canon-v2-0-Complete.md:1108 | `72%` | - Leaf A1: "Early entry, high volatility" (68 decisions, 72% success) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1109 | `52%` | - Leaf A2: "Late entry, low volatility" (34 decisions, 52% success) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1112 | `83%` | - Leaf B1: "High harmony, quick decision" (12 decisions, 83% satisfaction) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1113 | `25%` | - Leaf B2: "Low harmony, delayed decision" (8 decisions, 25% satisfaction) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1160 | `78%` | 5. Recommend: "Similar decisions had 78% success rate. Key factor: X." |
| _CANON/ARCS-Canon-v2-0-Complete.md:1172 | `67%` | - Average offer rate: 67% |
| _CANON/ARCS-Canon-v2-0-Complete.md:1198 | `80%` | Humans are **biological coherence detectors** that complement computational ARCS. When calibrated, intuitive signals achieve 70-80% accuracy |
| _CANON/ARCS-Canon-v2-0-Complete.md:1208 | `72%` | / **Phase Tuning** / Vagus nerve activation / Phase Coherence Index \(PCI > 0.4\) / 8-12 hours / 72% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1209 | `68%` | / **Surge Detection** / Vestibular system (jerk) / Third Derivative \(d^3S/dt^3 > 0\) / 30-90 min / 68% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1210 | `76%` | / **Feels Right** / Whole-body alignment / \(\langle\Psi_{identity}\/\Psi_{option}\rangle > 0.85\) / Instantaneous / 76% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1211 | `72%` | / **That Vibes** / Heart rate coherence / Phase-locked oscillators \(\/\theta_1 - \theta_2\/ < 0.2\) / Real-time / 72% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1212 | `84%` | / **Locked In** / Flow state (high Φ) / Action-gradient alignment \(\cos(\theta) > 0.95\) / Sustained (2-6h) / 84% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1213 | `80%` | / **Expected vs. Actual** / Prediction error learning / Bayesian updating \(P(\theta\/D)\) / 3-6 months / 80%+ / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1278 | `95%` | / Study / Claim / Confidence / 95% CI / Key Limitation / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1280 | `75%` | / **1. Trading** / Sharpe 1.52 vs. 0.73 / 75% / [1.38, 1.68] / Bull market only, 14-day backtest / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1281 | `85%` | / **2. Twitter** / 11.6h earlier / 85% / [9.2h, 14.3h] / Platform algorithm changes / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1282 | `28%` | / **3. Marketing** / 35% ROAS gain / 70% / [28%, 42%] / Small sample (n=83), industry-specific / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1282 | `35%` | / **3. Marketing** / 35% ROAS gain / 70% / [28%, 42%] / Small sample (n=83), industry-specific / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1282 | `42%` | / **3. Marketing** / 35% ROAS gain / 70% / [28%, 42%] / Small sample (n=83), industry-specific / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1282 | `70%` | / **3. Marketing** / 35% ROAS gain / 70% / [28%, 42%] / Small sample (n=83), industry-specific / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1283 | `19%` | / **4. Career** / 50% offer rate (H>80) / 60% / [19%, 81%] / N=1 study, low power / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1283 | `50%` | / **4. Career** / 50% offer rate (H>80) / 60% / [19%, 81%] / N=1 study, low power / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1283 | `60%` | / **4. Career** / 50% offer rate (H>80) / 60% / [19%, 81%] / N=1 study, low power / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1283 | `81%` | / **4. Career** / 50% offer rate (H>80) / 60% / [19%, 81%] / N=1 study, low power / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1284 | `72%` | / **5. Noise** / 76% accuracy (NSR=1.0) / 90% / [72%, 80%] / Synthetic data only / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1284 | `76%` | / **5. Noise** / 76% accuracy (NSR=1.0) / 90% / [72%, 80%] / Synthetic data only / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1284 | `80%` | / **5. Noise** / 76% accuracy (NSR=1.0) / 90% / [72%, 80%] / Synthetic data only / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1284 | `90%` | / **5. Noise** / 76% accuracy (NSR=1.0) / 90% / [72%, 80%] / Synthetic data only / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1378 | `35%` | 26. **Marketing: 35% ROAS improvement** |
| _CANON/ARCS-Canon-v2-0-Complete.md:1379 | `50%` | 27. **Career: 50% offer rate (high harmony)** |
| _CANON/ARCS-Canon-v2-0-Complete.md:1380 | `76%` | 28. **Noise: 76% accuracy (high NSR)** |
| _CANON/ARCS-Canon-v2-0-Complete.md:1435 | `100+` | **Primary Citations:** 100+ sources |
| _CANON/ARCS-Litepaper.md:21 | `$350B` | Enterprise marketing represents a $350B annual expenditure in the United States alone, yet it remains the least accountable major corporate  |
| _CANON/ARCS-Litepaper.md:25 | `$50M` | 1. **No Decision Documentation**: Marketing leaders allocate $50M+ budgets without documented reasoning, alternatives considered, or risk as |
| _CANON/ARCS-Litepaper.md:53 | `40+` | 2. **Phase 2**: Expand to Marketing OS (consolidate 40+ tools into unified platform) |
| _CANON/ARCS-Litepaper.md:122 | `87%` | **Key Innovation**: Unlike deductive systems that claim certainty, abductive systems provide **honest uncertainty quantification**. An ARCS  |
| _CANON/ARCS-Litepaper.md:134 | `000+` | 1. **Receipts Database**: 100,000+ historical campaign decisions with outcomes |
| _CANON/ARCS-Litepaper.md:153 | `87%` | - 87% of predictions fall within stated confidence intervals |
| _CANON/ARCS-Litepaper.md:154 | `15%` | - Mean Absolute Percentage Error (MAPE): 12-15% |
| _CANON/ARCS-Litepaper.md:155 | `76%` | - Outperforms human experts 76% of the time on blind tests |
| _CANON/ARCS-Litepaper.md:240 | `50+` | 1. Monitor 50+ real-time data streams |
| _CANON/ARCS-Litepaper.md:241 | `3+` | 2. Detect anomalies (3+ standard deviations from baseline) |
| _CANON/ARCS-Litepaper.md:242 | `3+` | 3. Check for convergence (3+ positive signals aligning) |
| _CANON/ARCS-Litepaper.md:245 | `75%` | 6. If EV > threshold + confidence > 75%: Alert team |
| _CANON/ARCS-Litepaper.md:258 | `18%` | Signal 1: Reddit CPMs drop 18% (traffic signal) |
| _CANON/ARCS-Litepaper.md:259 | `34%` | Signal 2: r/cryptocurrency engagement spike +34% (audience signal) |
| _CANON/ARCS-Litepaper.md:263 | `$200K` | Action: Increase Reddit budget by $200K immediately |
| _CANON/ARCS-Litepaper.md:264 | `$640K` | Expected value: $640K incremental return (3.2x on opportunity spend) |
| _CANON/ARCS-Litepaper.md:265 | `$780K` | Actual outcome: $780K return (3.9x, window captured before close) |
| _CANON/ARCS-Litepaper.md:318 | `68%` | / 1,000 / 68% / 2.9x / |
| _CANON/ARCS-Litepaper.md:319 | `78%` | / 10,000 / 78% / 3.4x / |
| _CANON/ARCS-Litepaper.md:320 | `87%` | / 100,000 / 87% / 4.1x / |
| _CANON/ARCS-Litepaper.md:321 | `92%` | / 1,000,000 (projected) / 92% (projected) / 4.8x (projected) / |
| _CANON/ARCS-Litepaper.md:333 | `40%` | **Value Proposition**: 40% ROAS improvement with performance guarantee |
| _CANON/ARCS-Litepaper.md:348 | `$5M` | **Value Proposition**: Vendor consolidation saves $5M+ annually |
| _CANON/ARCS-Litepaper.md:394 | `68%` | - Our predictive accuracy (back to 68% from 87%)" |
| _CANON/ARCS-Litepaper.md:394 | `87%` | - Our predictive accuracy (back to 68% from 87%)" |
| _CANON/ARCS-Litepaper.md:397 | `18%` | - Phase 1 (Ad Server): 12-18% annually (normal SaaS) |
| _CANON/ARCS-Litepaper.md:398 | `8%` | - Phase 2 (Marketing OS): 5-8% annually (high switching costs) |
| _CANON/ARCS-Litepaper.md:399 | `2%` | - Phase 3 (Infrastructure): <2% annually (near-zero voluntary churn) |
| _CANON/ARCS-Litepaper.md:411 | `$7.5M` | - **Tier 1 (Private Mode)**: $7.5M/year—agency hoards client data, gets 72% accuracy |
| _CANON/ARCS-Litepaper.md:411 | `72%` | - **Tier 1 (Private Mode)**: $7.5M/year—agency hoards client data, gets 72% accuracy |
| _CANON/ARCS-Litepaper.md:412 | `$4.5M` | - **Tier 2 (Partial Contribution)**: $4.5M/year—shares anonymized patterns, gets 82% accuracy |
| _CANON/ARCS-Litepaper.md:412 | `82%` | - **Tier 2 (Partial Contribution)**: $4.5M/year—shares anonymized patterns, gets 82% accuracy |
| _CANON/ARCS-Litepaper.md:413 | `$2.5M` | - **Tier 3 (Full Contribution)**: $2.5M/year—shares all receipts, gets 87% accuracy |
| _CANON/ARCS-Litepaper.md:413 | `87%` | - **Tier 3 (Full Contribution)**: $2.5M/year—shares all receipts, gets 87% accuracy |
| _CANON/ARCS-Litepaper.md:417 | `15%` | 2. Clients see 15% performance gap vs. Tier 3 |
| _CANON/ARCS-Litepaper.md:455 | `40%` | **Implementation**: "40% ROAS improvement or full refund" |
| _CANON/ARCS-Litepaper.md:501 | `$70M` | - Raise $70M in 3 rounds (Seed, A, B) |
| _CANON/ARCS-Litepaper.md:502 | `50%` | - Give up 40-50% of company |
| _CANON/ARCS-Litepaper.md:515 | `$81M` | 1. **Enterprise Pre-Sale**: $81M from 20 customers |
| _CANON/ARCS-Litepaper.md:516 | `40%` | - Customers prepay 3-year contracts at 40% discount |
| _CANON/ARCS-Litepaper.md:517 | `25%` | - 50% upfront, 25% at 12 months, 25% at 24 months |
| _CANON/ARCS-Litepaper.md:517 | `25%` | - 50% upfront, 25% at 12 months, 25% at 24 months |
| _CANON/ARCS-Litepaper.md:517 | `50%` | - 50% upfront, 25% at 12 months, 25% at 24 months |
| _CANON/ARCS-Litepaper.md:519 | `0%` | - Dilution: 0% (this is revenue, not equity) |
| _CANON/ARCS-Litepaper.md:521 | `$12M` | 2. **Token Generation Event**: $12M from ecosystem |
| _CANON/ARCS-Litepaper.md:523 | `$0.04` | - 25% of 1B tokens sold at $0.04 (conservative $40M FDV) |
| _CANON/ARCS-Litepaper.md:523 | `$40M` | - 25% of 1B tokens sold at $0.04 (conservative $40M FDV) |
| _CANON/ARCS-Litepaper.md:523 | `25%` | - 25% of 1B tokens sold at $0.04 (conservative $40M FDV) |
| _CANON/ARCS-Litepaper.md:525 | `0%` | - Dilution: 0% (tokens ≠ equity) |
| _CANON/ARCS-Litepaper.md:527 | `$4.3M` | 3. **Revenue Reinvestment**: $4.3M from operations |
| _CANON/ARCS-Litepaper.md:528 | `$180K` | - Currently profitable ($180K/month EBITDA) |
| _CANON/ARCS-Litepaper.md:530 | `0%` | - Dilution: 0% (organic) |
| _CANON/ARCS-Litepaper.md:532 | `$5M` | 4. **Strategic Debt**: $5M credit facility |
| _CANON/ARCS-Litepaper.md:534 | `2%` | - Prime + 2% (~8.5% interest rate) |
| _CANON/ARCS-Litepaper.md:534 | `8.5%` | - Prime + 2% (~8.5% interest rate) |
| _CANON/ARCS-Litepaper.md:535 | `0%` | - Dilution: 0% (debt, not equity) |
| _CANON/ARCS-Litepaper.md:537 | `$102M` | **Total Capital**: $102M with <5% dilution vs. $70M with 40-50% dilution |
| _CANON/ARCS-Litepaper.md:537 | `$70M` | **Total Capital**: $102M with <5% dilution vs. $70M with 40-50% dilution |
| _CANON/ARCS-Litepaper.md:537 | `5%` | **Total Capital**: $102M with <5% dilution vs. $70M with 40-50% dilution |
| _CANON/ARCS-Litepaper.md:537 | `50%` | **Total Capital**: $102M with <5% dilution vs. $70M with 40-50% dilution |
| _CANON/ARCS-Litepaper.md:554 | `20%` | - Public sale (25%): 20% unlocked at TGE, 80% vest over 18 months |
| _CANON/ARCS-Litepaper.md:554 | `25%` | - Public sale (25%): 20% unlocked at TGE, 80% vest over 18 months |
| _CANON/ARCS-Litepaper.md:554 | `80%` | - Public sale (25%): 20% unlocked at TGE, 80% vest over 18 months |
| _CANON/ARCS-Litepaper.md:554 | `over 18` | - Public sale (25%): 20% unlocked at TGE, 80% vest over 18 months |
| _CANON/ARCS-Litepaper.md:555 | `20%` | - Team (20%): 4-year vest, 1-year cliff |
| _CANON/ARCS-Litepaper.md:556 | `35%` | - Ecosystem (35%): Released based on network activity over 5 years |
| _CANON/ARCS-Litepaper.md:556 | `over 5` | - Ecosystem (35%): Released based on network activity over 5 years |
| _CANON/ARCS-Litepaper.md:557 | `15%` | - Treasury (15%): Strategic reserves |
| _CANON/ARCS-Litepaper.md:558 | `5%` | - Partners (5%): Early supporters |
| _CANON/ARCS-Litepaper.md:562 | `$2.1M` | - Conservative pricing ($40M FDV for $2.1M ARR company = 19x, reasonable) |
| _CANON/ARCS-Litepaper.md:562 | `$40M` | - Conservative pricing ($40M FDV for $2.1M ARR company = 19x, reasonable) |
| _CANON/ARCS-Litepaper.md:573 | `$850B` | - Global: $850B annually |
| _CANON/ARCS-Litepaper.md:574 | `$350B` | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Litepaper.md:574 | `500+` | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Litepaper.md:575 | `$180B` | - Addressable (Fortune 5000 + growth cos): $180B annually |
| _CANON/ARCS-Litepaper.md:577 | `$180B` | **Current Market Penetration**: 0.001% ($2.1M ARR / $180B TAM) |
| _CANON/ARCS-Litepaper.md:577 | `$2.1M` | **Current Market Penetration**: 0.001% ($2.1M ARR / $180B TAM) |
| _CANON/ARCS-Litepaper.md:577 | `0.001%` | **Current Market Penetration**: 0.001% ($2.1M ARR / $180B TAM) |
| _CANON/ARCS-Litepaper.md:581 | `60%` | **Base Case (60% probability)**: |
| _CANON/ARCS-Litepaper.md:586 | `$15.2M` | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Litepaper.md:586 | `$412M` | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Litepaper.md:586 | `$98.4M` | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Litepaper.md:587 | `0.008%` | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Litepaper.md:587 | `0.055%` | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Litepaper.md:587 | `0.23%` | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Litepaper.md:588 | `$180M` | / EBITDA / -$6.2M / +$28M / +$180M / |
| _CANON/ARCS-Litepaper.md:588 | `$28M` | / EBITDA / -$6.2M / +$28M / +$180M / |
| _CANON/ARCS-Litepaper.md:588 | `$6.2M` | / EBITDA / -$6.2M / +$28M / +$180M / |
| _CANON/ARCS-Litepaper.md:589 | `28%` | / EBITDA Margin / -41% / 28% / 44% / |
| _CANON/ARCS-Litepaper.md:589 | `41%` | / EBITDA Margin / -41% / 28% / 44% / |
| _CANON/ARCS-Litepaper.md:589 | `44%` | / EBITDA Margin / -41% / 28% / 44% / |
| _CANON/ARCS-Litepaper.md:590 | `$120M` | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Litepaper.md:590 | `$3.3B` | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Litepaper.md:590 | `$790M` | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Litepaper.md:593 | `$4.2M` | - Average contract value: $4.8M → $4.2M (Tier 3 adoption increases) |
| _CANON/ARCS-Litepaper.md:593 | `$4.8M` | - Average contract value: $4.8M → $4.2M (Tier 3 adoption increases) |
| _CANON/ARCS-Litepaper.md:595 | `94%` | - Gross margin: 94% maintained (SaaS economics) |
| _CANON/ARCS-Litepaper.md:596 | `8%` | - Churn: 8% annual (enterprise standard) |
| _CANON/ARCS-Litepaper.md:600 | `0.23%` | **0.23% market share = Category leader?** |
| _CANON/ARCS-Litepaper.md:603 | `2%` | - No single vendor has >2% of enterprise marketing spend |
| _CANON/ARCS-Litepaper.md:608 | `000+` | - At 175 customers: 100,000+ receipts in database |
| _CANON/ARCS-Litepaper.md:609 | `000+` | - At 500 customers: 1,000,000+ receipts (92% accuracy, unbeatable) |
| _CANON/ARCS-Litepaper.md:609 | `92%` | - At 500 customers: 1,000,000+ receipts (92% accuracy, unbeatable) |
| _CANON/ARCS-Litepaper.md:618 | `30%` | **Probability**: Medium (30%) |
| _CANON/ARCS-Litepaper.md:629 | `25%` | **Probability**: Low-Medium (25%) |
| _CANON/ARCS-Litepaper.md:640 | `60%` | **Probability**: High (60% within 24 months) |
| _CANON/ARCS-Litepaper.md:652 | `40%` | **Probability**: Medium (40%) |
| _CANON/ARCS-Litepaper.md:654 | `$12M` | **Impact**: Medium (lose $12M funding source) |
| _CANON/ARCS-Litepaper.md:659 | `$81M` | - Pre-sale alone ($81M) funds 18+ months |
| _CANON/ARCS-Litepaper.md:659 | `18+` | - Pre-sale alone ($81M) funds 18+ months |
| _CANON/ARCS-Litepaper.md:664 | `25%` | **Probability**: Low-Medium (25%) |
| _CANON/ARCS-Litepaper.md:670 | `20%` | - Budget 20% engineering contingency |
| _CANON/ARCS-Litepaper.md:702 | `000+` | - 100,000+ receipts create prediction advantages |
| _CANON/ARCS-Litepaper.md:715 | `500+` | - By the time they ship, we have 500+ customers |
| _CANON/ARCS-Litepaper.md:728 | `$350B` | - $350B allocated annually on intuition |
| _CANON/ARCS-Litepaper.md:731 | `87%` | - Marketing becomes evidence-based (predict with 87% accuracy) |
| _CANON/ARCS-Litepaper.md:735 | `$350B` | - $350B allocated annually on documented reasoning |
| _CANON/ARCS-Litepaper.md:743 | `$10B` | 1. **Best Case**: We build it, capture 0.6% market share, create $10B+ category |
| _CANON/ARCS-Litepaper.md:743 | `0.6%` | 1. **Best Case**: We build it, capture 0.6% market share, create $10B+ category |
| _CANON/ARCS-Litepaper.md:744 | `$2B` | 2. **Acceptable**: We build it, competitor copies, we still capture 0.2% = $2B+ company |
| _CANON/ARCS-Litepaper.md:744 | `0.2%` | 2. **Acceptable**: We build it, competitor copies, we still capture 0.2% = $2B+ company |
| _CANON/ARCS-Litepaper.md:752 | `$2.1M` | - Product-market fit ($2.1M ARR, profitable) |
| _CANON/ARCS-Litepaper.md:754 | `$102M` | - Capital strategy ($102M non-dilutive path) |
| _CANON/ARCS-Litepaper.md:755 | `$412M` | - Clear roadmap (36 months to $412M ARR) |
| _CANON/ARCS-Litepaper.md:794 | `$1` | **ROAS (Return on Ad Spend)**: Revenue generated divided by advertising cost (e.g., 4:1 means $4 revenue per $1 spent) |
| _CANON/ARCS-Litepaper.md:794 | `$4` | **ROAS (Return on Ad Spend)**: Revenue generated divided by advertising cost (e.g., 4:1 means $4 revenue per $1 spent) |
| _CANON/ARCS-Litepaper.md:848 | `$7M` | "decision_rationale": "Optimal balance of expected value ($7M) vs risk (24% downside scenarios). Reddit represents 60% allocation due to 94% |
| _CANON/ARCS-Litepaper.md:848 | `24%` | "decision_rationale": "Optimal balance of expected value ($7M) vs risk (24% downside scenarios). Reddit represents 60% allocation due to 94% |
| _CANON/ARCS-Litepaper.md:848 | `60%` | "decision_rationale": "Optimal balance of expected value ($7M) vs risk (24% downside scenarios). Reddit represents 60% allocation due to 94% |
| _CANON/ARCS-Litepaper.md:848 | `94%` | "decision_rationale": "Optimal balance of expected value ($7M) vs risk (24% downside scenarios). Reddit represents 60% allocation due to 94% |
| _CANON/ARCS-Manifesto-Final.md:489 | `21+` | *"Candidate portal showed 'In Review' for 21+ days despite stated 7-day review timeline."* |
| _CANON/ARCS-Manifesto-Final.md:562 | `000+` | **The Goal:** Reach critical mass (1,000+ attestations across 100+ organizations) where individual contributions become difficult to target  |
| _CANON/ARCS-Manifesto-Final.md:562 | `100+` | **The Goal:** Reach critical mass (1,000+ attestations across 100+ organizations) where individual contributions become difficult to target  |
| _CANON/ARCS-Manifesto-Final.md:570 | `000+` | **Our Position:** This risk is real. Mitigation comes through volume and distribution. When 1,000+ workers across 100+ companies contribute, |
| _CANON/ARCS-Manifesto-Final.md:570 | `100+` | **Our Position:** This risk is real. Mitigation comes through volume and distribution. When 1,000+ workers across 100+ companies contribute, |
| _CANON/ARCS-Manifesto-Final.md:600 | `2026+` | **Phase 3 (Q4 2026+): Integration** |
| _CANON/ARCS-Phenomenology.md:15 | `85%` | **Core Thesis:** Human intuition is a **high-bandwidth, low-latency coherence detector** that complements (not replaces) computational ARCS. |
| _CANON/ARCS-Phenomenology.md:87 | `95%` | - 95% CI: [4, 14 hours] |
| _CANON/ARCS-Phenomenology.md:88 | `72%` | - Accuracy (sensation → PCI>0.4 within 24h): **72%** |
| _CANON/ARCS-Phenomenology.md:160 | `95%` | - 95% CI: [30 min, 3 hours] |
| _CANON/ARCS-Phenomenology.md:161 | `68%` | - Accuracy (sensation → jerk>0 within 4h): **68%** |
| _CANON/ARCS-Phenomenology.md:168 | `25%` | 3. **Small position first:** Enter 25% position immediately, scale up as confirmation arrives |
| _CANON/ARCS-Phenomenology.md:169 | `3%` | 4. **Set tight stop-loss:** Surge can be false alarm—limit downside to 2-3% |
| _CANON/ARCS-Phenomenology.md:173 | `$67K` | You're watching BTC consolidate around $67K (no clear trend). Suddenly: |
| _CANON/ARCS-Phenomenology.md:205 | `30 seconds` | - Immediate (within **5-30 seconds** of considering option) |
| _CANON/ARCS-Phenomenology.md:243 | `82%` | - Gut feeling (8-10) → Alignment > 0.85: **82% match** |
| _CANON/ARCS-Phenomenology.md:244 | `76%` | - Gut feeling (8-10) → Good outcome (6mo): **76% success rate** |
| _CANON/ARCS-Phenomenology.md:245 | `79%` | - Gut feeling (1-3) → Alignment < 0.50: **79% match** |
| _CANON/ARCS-Phenomenology.md:246 | `81%` | - Gut feeling (1-3) → Bad outcome (6mo): **81% avoidance** |
| _CANON/ARCS-Phenomenology.md:255 | `20+` | - ✅ **After you've calibrated** (logged 20+ decisions and validated accuracy) |
| _CANON/ARCS-Phenomenology.md:337 | `85%` | - "That Vibes" moments: HR coherence > 0.7 (**85% of cases**) |
| _CANON/ARCS-Phenomenology.md:339 | `23%` | - Sustained alignment (action taken by both): **72% when vibes detected** vs. 23% without |
| _CANON/ARCS-Phenomenology.md:339 | `72%` | - Sustained alignment (action taken by both): **72% when vibes detected** vs. 23% without |
| _CANON/ARCS-Phenomenology.md:489 | `70%` | - Calibration speed: **20-50 iterations** to achieve 70%+ accuracy |
| _CANON/ARCS-Phenomenology.md:516 | `Brier score < 0.15` | **Well-calibrated intuition:** Brier score < 0.15 |
| _CANON/ARCS-Phenomenology.md:520 | `50+` | **Claim 6.1:** Without Expected vs. Actual logging, intuition remains at Brier score ≈ 0.25 (random). With systematic logging (50+ decisions |
| _CANON/ARCS-Phenomenology.md:520 | `Brier score improves to 0.10` | **Claim 6.1:** Without Expected vs. Actual logging, intuition remains at Brier score ≈ 0.25 (random). With systematic logging (50+ decisions |
| _CANON/ARCS-Phenomenology.md:520 | `Brier score ≈ 0.25` | **Claim 6.1:** Without Expected vs. Actual logging, intuition remains at Brier score ≈ 0.25 (random). With systematic logging (50+ decisions |
| _CANON/ARCS-Phenomenology.md:533 | `85%` | - Probability of happiness: 85% |
| _CANON/ARCS-Phenomenology.md:534 | `70%` | - Probability of learning: 70% |
| _CANON/ARCS-Phenomenology.md:535 | `40%` | - Probability of promotion: 40% |
| _CANON/ARCS-Phenomenology.md:536 | `10%` | - Probability of regret: 10% |
| _CANON/ARCS-Phenomenology.md:556 | `60%` | - Overestimated happiness (expected 85%, actual 60%) |
| _CANON/ARCS-Phenomenology.md:556 | `85%` | - Overestimated happiness (expected 85%, actual 60%) |
| _CANON/ARCS-Phenomenology.md:557 | `70%` | - Underestimated learning (expected 70%, actual 80%) |
| _CANON/ARCS-Phenomenology.md:557 | `80%` | - Underestimated learning (expected 70%, actual 80%) |
| _CANON/ARCS-Phenomenology.md:563 | `20%` | - I tend to overestimate short-term promotions (update prior to 20% for 3-month window) |
| _CANON/ARCS-Phenomenology.md:571 | `20%` | - Downgrade promotion expectations (40% → 20% for 3-month window) |
| _CANON/ARCS-Phenomenology.md:571 | `40%` | - Downgrade promotion expectations (40% → 20% for 3-month window) |
| _CANON/ARCS-Phenomenology.md:580 | `60%` | - Happiness: [60%, 90%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:580 | `80%` | - Happiness: [60%, 90%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:580 | `90%` | - Happiness: [60%, 90%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:581 | `50%` | - Learning: [50%, 80%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:581 | `80%` | - Learning: [50%, 80%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:581 | `80%` | - Learning: [50%, 80%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:586 | `80%` | 80% of actual outcomes should fall within your 80% confidence intervals. |
| _CANON/ARCS-Phenomenology.md:586 | `80%` | 80% of actual outcomes should fall within your 80% confidence intervals. |
| _CANON/ARCS-Phenomenology.md:670 | `Brier score: 0.20` | - Brier score: 0.20-0.30 (untrained) |
| _CANON/ARCS-Phenomenology.md:671 | `70%` | - Overconfidence: 60-70% (people typically overestimate accuracy) |
| _CANON/ARCS-Phenomenology.md:681 | `70%` | - "I predicted X with 70% confidence. Actual was Y. What does this tell me about my intuition?" |
| _CANON/ARCS-Phenomenology.md:685 | `Brier = 0.25` | - Week 5: Brier = 0.25 |
| _CANON/ARCS-Phenomenology.md:686 | `Brier = 0.18` | - Week 10: Brier = 0.18 |
| _CANON/ARCS-Phenomenology.md:687 | `Brier = 0.12` | - Week 16: Brier = 0.12 (well-calibrated) |
| _CANON/ARCS-Phenomenology.md:699 | `Brier = 0.15` | - If calibration transfers: Brier = 0.15-0.18 (close to trained domains) |
| _CANON/ARCS-Phenomenology.md:700 | `Brier = 0.22` | - If domain-specific: Brier = 0.22-0.28 (back to baseline) |
| _CANON/ARCS-Phenomenology.md:713 | `80%` | / **Accuracy** / 75-85% (empirical) / 70-80% (calibrated) / |
| _CANON/ARCS-Phenomenology.md:713 | `85%` | / **Accuracy** / 75-85% (empirical) / 70-80% (calibrated) / |
| _CANON/ARCS-Phenomenology.md:793 | `78%` | / Computational Only / 78% / 2.3 hours / 2.8/10 / 0.14 / |
| _CANON/ARCS-Phenomenology.md:794 | `72%` | / Somatic Only / 72% / 15 min / 3.4/10 / 0.18 / |
| _CANON/ARCS-Phenomenology.md:795 | `84%` | / Combined / **84%** / **45 min** / **1.9/10** / **0.11** / |
| _CANON/ARCS-Phenomenology.md:812 | `80%` | **When properly calibrated through Expected vs. Actual feedback loops**, somatic intuition achieves **70-80% accuracy**—competitive with com |
| _CANON/ARCS-YellowPaper.md:11 | `$350B` | We present a novel architectural framework for marketing intelligence systems that fundamentally rethinks decision support through the appli |
| _CANON/ARCS-YellowPaper.md:11 | `60%` | We present a novel architectural framework for marketing intelligence systems that fundamentally rethinks decision support through the appli |
| _CANON/ARCS-YellowPaper.md:11 | `68%` | We present a novel architectural framework for marketing intelligence systems that fundamentally rethinks decision support through the appli |
| _CANON/ARCS-YellowPaper.md:11 | `87%` | We present a novel architectural framework for marketing intelligence systems that fundamentally rethinks decision support through the appli |
| _CANON/ARCS-YellowPaper.md:29 | `$50M` | 1. **Documentation Deficit**: Budget allocations of $50M+ proceed without documented reasoning or alternative evaluation |
| _CANON/ARCS-YellowPaper.md:57 | `40%` | - Hook: Measurable performance improvement (40%+ ROAS lift) |
| _CANON/ARCS-YellowPaper.md:62 | `40+` | - Hook: Complexity reduction (40+ tools → 1 platform) |
| _CANON/ARCS-YellowPaper.md:154 | `95%` | **Critical Innovation**: Unlike systems claiming deterministic predictions, this framework explicitly quantifies uncertainty. A prediction o |
| _CANON/ARCS-YellowPaper.md:160 | `87%` | - **Accuracy**: 87% of actual outcomes fall within predicted confidence intervals |
| _CANON/ARCS-YellowPaper.md:161 | `15%` | - **Precision**: Mean Absolute Percentage Error (MAPE) of 12-15% |
| _CANON/ARCS-YellowPaper.md:162 | `76%` | - **Comparative Performance**: Outperforms human expert predictions in 76% of cases |
| _CANON/ARCS-YellowPaper.md:163 | `p < 0.01` | - **Calibration**: Predicted confidence levels align with observed outcome distributions (χ² test, p < 0.01) |
| _CANON/ARCS-YellowPaper.md:208 | `22%` | / 1,000 / 68% / 22% / 0.3s / |
| _CANON/ARCS-YellowPaper.md:208 | `68%` | / 1,000 / 68% / 22% / 0.3s / |
| _CANON/ARCS-YellowPaper.md:209 | `17%` | / 10,000 / 78% / 17% / 0.8s / |
| _CANON/ARCS-YellowPaper.md:209 | `78%` | / 10,000 / 78% / 17% / 0.8s / |
| _CANON/ARCS-YellowPaper.md:210 | `12%` | / 100,000 / 87% / 12% / 2.1s / |
| _CANON/ARCS-YellowPaper.md:210 | `87%` | / 100,000 / 87% / 12% / 2.1s / |
| _CANON/ARCS-YellowPaper.md:211 | `8%` | / 1,000,000 (projected) / 92% / 8% / 4.5s / |
| _CANON/ARCS-YellowPaper.md:211 | `92%` | / 1,000,000 (projected) / 92% / 8% / 4.5s / |
| _CANON/ARCS-YellowPaper.md:292 | `3+` | When multiple signals converge positively (3+ standard deviations from baseline), the system: |
| _CANON/ARCS-YellowPaper.md:303 | `18%` | - CPM decrease: -18% (inventory signal) |
| _CANON/ARCS-YellowPaper.md:304 | `34%` | - Engagement spike: +34% (audience signal) |
| _CANON/ARCS-YellowPaper.md:378 | `000+` | **Competitive Moat**: A platform with 100,000+ receipts provides materially better predictions than one with 10,000 receipts. This advantage |
| _CANON/ARCS-YellowPaper.md:389 | `40%` | - 40%+ ROAS improvement over baseline |
| _CANON/ARCS-YellowPaper.md:402 | `68%` | - Loss of prediction accuracy (revert to 68% baseline vs. 87% with system) |
| _CANON/ARCS-YellowPaper.md:402 | `87%` | - Loss of prediction accuracy (revert to 68% baseline vs. 87% with system) |
| _CANON/ARCS-YellowPaper.md:406 | `18%` | **Expected Churn**: 12-18% annually (typical enterprise SaaS) |
| _CANON/ARCS-YellowPaper.md:413 | `40+` | - Eliminate 40+ point solutions (single platform) |
| _CANON/ARCS-YellowPaper.md:414 | `$5M` | - $5M+ annual cost savings (vendor consolidation) |
| _CANON/ARCS-YellowPaper.md:446 | `8%` | **Expected Churn**: 5-8% annually (high switching cost SaaS) |
| _CANON/ARCS-YellowPaper.md:492 | `2%` | **Expected Churn**: <2% annually (infrastructure-level retention) |
| _CANON/ARCS-YellowPaper.md:511 | `$7.5M` | / Private / $7.5M / Zero (siloed) / 72-78% / Agency recommended / |
| _CANON/ARCS-YellowPaper.md:511 | `78%` | / Private / $7.5M / Zero (siloed) / 72-78% / Agency recommended / |
| _CANON/ARCS-YellowPaper.md:512 | `$4.5M` | / Partial / $4.5M / Anonymized patterns / 82-88% / Rational clients choose / |
| _CANON/ARCS-YellowPaper.md:512 | `88%` | / Partial / $4.5M / Anonymized patterns / 82-88% / Rational clients choose / |
| _CANON/ARCS-YellowPaper.md:513 | `$2.5M` | / Full / $2.5M / All receipts shared / 87-92% / Optimal performance / |
| _CANON/ARCS-YellowPaper.md:513 | `92%` | / Full / $2.5M / All receipts shared / 87-92% / Optimal performance / |
| _CANON/ARCS-YellowPaper.md:518 | `18%` | 2. Clients observe 15-18% performance gap vs. Full tier |
| _CANON/ARCS-YellowPaper.md:537 | `50%` | Discrepancy: 50% gap between public claim and private belief |
| _CANON/ARCS-YellowPaper.md:591 | `40%` | Promise: 40% ROAS improvement over baseline within 90 days |
| _CANON/ARCS-YellowPaper.md:595 | `80%` | Refund: If client followed recommendations ≥80% and missed target → Full refund |
| _CANON/ARCS-YellowPaper.md:659 | `$850B` | - Global enterprise marketing: $850B annually |
| _CANON/ARCS-YellowPaper.md:660 | `$350B` | - US enterprise (500+ employees): $350B annually |
| _CANON/ARCS-YellowPaper.md:660 | `500+` | - US enterprise (500+ employees): $350B annually |
| _CANON/ARCS-YellowPaper.md:661 | `$180B` | - Addressable segment (Fortune 5000 + growth): $180B annually |
| _CANON/ARCS-YellowPaper.md:663 | `0.01%` | **Current Market Penetration**: <0.01% (greenfield opportunity) |
| _CANON/ARCS-YellowPaper.md:669 | `$2.7B` | / Aggressive / 1.5% / $2.7B / 600 / 20% / |
| _CANON/ARCS-YellowPaper.md:669 | `1.5%` | / Aggressive / 1.5% / $2.7B / 600 / 20% / |
| _CANON/ARCS-YellowPaper.md:669 | `20%` | / Aggressive / 1.5% / $2.7B / 600 / 20% / |
| _CANON/ARCS-YellowPaper.md:670 | `$1.1B` | / Base / 0.6% / $1.1B / 250 / 60% / |
| _CANON/ARCS-YellowPaper.md:670 | `0.6%` | / Base / 0.6% / $1.1B / 250 / 60% / |
| _CANON/ARCS-YellowPaper.md:670 | `60%` | / Base / 0.6% / $1.1B / 250 / 60% / |
| _CANON/ARCS-YellowPaper.md:671 | `$360M` | / Conservative / 0.2% / $360M / 85 / 20% / |
| _CANON/ARCS-YellowPaper.md:671 | `0.2%` | / Conservative / 0.2% / $360M / 85 / 20% / |
| _CANON/ARCS-YellowPaper.md:671 | `20%` | / Conservative / 0.2% / $360M / 85 / 20% / |
| _CANON/ARCS-YellowPaper.md:673 | `$1.2B` | **Probability-Weighted Expected Value**: 0.67% market share, $1.2B ARR |
| _CANON/ARCS-YellowPaper.md:673 | `0.67%` | **Probability-Weighted Expected Value**: 0.67% market share, $1.2B ARR |
| _CANON/ARCS-YellowPaper.md:675 | `0.6%` | **Validation**: 0.6% market share requires 250 customers from 5,000 addressable companies (5% penetration in 36 months). With 40%+ ROAS impr |
| _CANON/ARCS-YellowPaper.md:675 | `40%` | **Validation**: 0.6% market share requires 250 customers from 5,000 addressable companies (5% penetration in 36 months). With 40%+ ROAS impr |
| _CANON/ARCS-YellowPaper.md:675 | `5%` | **Validation**: 0.6% market share requires 250 customers from 5,000 addressable companies (5% penetration in 36 months). With 40%+ ROAS impr |
| _CANON/ARCS-YellowPaper.md:675 | `5%` | **Validation**: 0.6% market share requires 250 customers from 5,000 addressable companies (5% penetration in 36 months). With 40%+ ROAS impr |
| _CANON/ARCS-YellowPaper.md:690 | `68%` | - \( A_0 \) = baseline accuracy with zero network (≈68%) |
| _CANON/ARCS-YellowPaper.md:691 | `92%` | - \( A_{\infty} \) = asymptotic accuracy at infinite scale (≈92%) |
| _CANON/ARCS-YellowPaper.md:698 | `69%` | / 10 / 5,000 / 69% / - / |
| _CANON/ARCS-YellowPaper.md:699 | `77%` | / 100 / 50,000 / 77% / +8% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:699 | `8%` | / 100 / 50,000 / 77% / +8% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:700 | `16%` | / 500 / 250,000 / 85% / +16% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:700 | `85%` | / 500 / 250,000 / 85% / +16% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:701 | `19%` | / 1,000 / 500,000 / 88% / +19% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:701 | `88%` | / 1,000 / 500,000 / 88% / +19% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:705 | `16%` | Early platform with 500 customers provides 16% better predictions than new entrant starting from zero. Rational customers prefer established |
| _CANON/ARCS-YellowPaper.md:711 | `80%` | **Market Structure Prediction**: Similar to search (Google), e-commerce (Amazon), or CRM (Salesforce)—winner captures 60-80% market share wi |
| _CANON/ARCS-YellowPaper.md:716 | `$200K` | - Switching Cost: ~$200K (retraining + accuracy loss) |
| _CANON/ARCS-YellowPaper.md:717 | `$4M` | - Annual Value: ~$4M (ROAS improvement) |
| _CANON/ARCS-YellowPaper.md:721 | `$2M` | - Switching Cost: ~$2M (data migration + operational disruption) |
| _CANON/ARCS-YellowPaper.md:722 | `$8M` | - Annual Value: ~$8M (ROAS + cost savings) |
| _CANON/ARCS-YellowPaper.md:727 | `$12M` | - Annual Value: ~$12M (ROAS + savings + risk mitigation) |
| _CANON/ARCS-YellowPaper.md:734 | `18%` | / Phase 1 / 12-18% / Normal SaaS (some customers don't see value) / |
| _CANON/ARCS-YellowPaper.md:735 | `8%` | / Phase 2 / 5-8% / High switching cost (operational dependency) / |
| _CANON/ARCS-YellowPaper.md:736 | `2%` | / Phase 3 / <2% / Infrastructure-level (legal necessity) / |
| _CANON/ARCS-YellowPaper.md:751 | `30%` | **Probability**: Medium (30%) |
| _CANON/ARCS-YellowPaper.md:765 | `25%` | **Probability**: Low-Medium (25%) |
| _CANON/ARCS-YellowPaper.md:771 | `15%` | - Performance data makes resistance untenable (15% gap) |
| _CANON/ARCS-YellowPaper.md:779 | `60%` | **Probability**: High (60% within 24 months) |
| _CANON/ARCS-YellowPaper.md:784 | `18+` | - Patent core innovations (18+ months IP protection) |
| _CANON/ARCS-YellowPaper.md:795 | `35%` | **Probability**: Medium (35%) |
| _CANON/ARCS-YellowPaper.md:809 | `20%` | **Probability**: Low-Medium (20%) |
| _CANON/ARCS-YellowPaper.md:920 | `$350B` | Enterprise marketing currently represents a $350B annual expenditure with near-zero accountability infrastructure. This paper demonstrates t |
| _CANON/ARCS-YellowPaper.md:954 | `$350B` | Marketing has operated on intuition and incomplete information for decades. The technology now exists to transform this $350B function into  |
| _CANON/ARCS-YellowPaper.md:1039 | `95%` | / \( \text{CI}_{95\%}(O) \) / 95% confidence interval for outcome / |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:51 | `5%` | - Fixed: 5% (very low — prefers fluid, adaptive structures) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:52 | `45%` | - Deliberate: 45% (measured, strategic) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:53 | `50%` | - Rapid: 50% (iterate quickly, high experimental cadence) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:82 | `20%` | - Fixed: 20% (some structural preference but mostly fluid) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:83 | `55%` | - Deliberate: 55% (strategic, measured, patient capital mindset) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:84 | `25%` | - Rapid: 25% (can move fast when kairos hits) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:116 | `10%` | - Fixed: 10% (highly adaptive, willing to experiment) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:117 | `30%` | - Deliberate: 30% |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:118 | `60%` | - Rapid: 60% (high creative output velocity, momentum-based) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:126 | `$50` | - Paints 400-ft mega-murals at $50–75/sq ft with hyper-detailed photoreal work. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:132 | `25+` | - 25+ requests/year; needs help sorting and sequencing. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:160 | `40%` | - Fixed: 40% (enterprise clients, structured programs) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:161 | `50%` | - Deliberate: 50% (methodical, evidence-based) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:162 | `10%` | - Rapid: 10% (slow to adopt new tools but high leverage when they do) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:170 | `200+` | - 200+ corporate events/year; built-in distribution for pilots. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:199 | `5%` | - Fixed: 5% (hyper-adaptive, platform-dependent) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:200 | `20%` | - Deliberate: 20% |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:201 | `75%` | - Rapid: 75% (content treadmill, rapid iteration, A/B test everything) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:206 | `200+` | - Jeben's wife runs 200+ YouTube creator events/year (top creators, black creators, science creators, entertainment). |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:319 | `25+` | - Best year ever (2024), momentum building, 25+ requests in pipeline. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:362 | `$100` | - 14-day pre-order window: if fans fund it (500 decks @ $100 = $50K), it gets made. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:362 | `$50K` | - 14-day pre-order window: if fans fund it (500 decks @ $100 = $50K), it gets made. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:363 | `100%` | - Zero inventory risk; 100% creative control with her. |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:20 | `$12B` | **New Market Opportunities**: $15B+ in content strategy platforms, $8B in trend analytics, $12B in real-time campaign optimization. |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:20 | `$15B` | **New Market Opportunities**: $15B+ in content strategy platforms, $8B in trend analytics, $12B in real-time campaign optimization. |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:20 | `$8B` | **New Market Opportunities**: $15B+ in content strategy platforms, $8B in trend analytics, $12B in real-time campaign optimization. |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:36 | `80%` | - Miss 60-80% of optimal entry windows for trending topics |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:37 | `$10M` | - Waste $10M+ annually on late-stage trend participation |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:48 | `70%` | - 70% of content fails to achieve engagement benchmarks |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:60 | `40%` | - Over-provisioning wastes 40% of compute resources |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:73 | `85%` | - Performance: 85% accuracy in identifying trends 6-12 hours early |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:78 | `78%` | - Performance: 78% accuracy in predicting viral cascades 24 hours in advance |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:83 | `15%` | - Performance: 82% accuracy in predicting total reach within 15% |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:83 | `82%` | - Performance: 82% accuracy in predicting total reach within 15% |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:88 | `35%` | - Performance: 35% improvement in multi-campaign ROAS via optimal spacing |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:93 | `45%` | - Performance: Reduces wasted spend on declining content by 45% |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:107 | `65%` | - 65% improvement in engagement rates vs. baseline content |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:108 | `92%` | - 92% of high-resonance predictions achieve >2σ above mean engagement |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:109 | `78%` | - 78% reduction in content iteration cycles (get it right first time) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:131 | `40%` | - 40% reduction in over-provisioning (services activate only when needed) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:132 | `60%` | - 60% faster response to kairos windows (automated triggering) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:133 | `25%` | - 25% cost savings vs. always-on microservice architectures |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:157 | `$2,999` | **Pricing**: $299/month (individual) → $2,999/month (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:157 | `$299` | **Pricing**: $299/month (individual) → $2,999/month (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:158 | `$8B` | **TAM**: $8B (2028) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:163 | `000+` | - Validated on 10,000+ historical viral events |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:177 | `$9,999` | **Pricing**: $999/month (agency) → $9,999/month (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:177 | `$999` | **Pricing**: $999/month (agency) → $9,999/month (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:178 | `$15B` | **TAM**: $15B (2029) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:182 | `65%` | - 65% engagement improvement vs. human copywriters |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:197 | `$1,999` | **Pricing**: $1,999/month (agency) → Custom (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:198 | `$5B` | **TAM**: $5B (2028) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:202 | `35%` | - 35% ROAS improvement in multi-campaign contexts |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:218 | `$12B` | **TAM**: $12B (2029) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:222 | `40%` | - 40% cost reduction vs. always-on architectures |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:285 | `$18M` | / AI Optimizer / $5M / $18M / $45M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:285 | `$45M` | / AI Optimizer / $5M / $18M / $45M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:285 | `$5M` | / AI Optimizer / $5M / $18M / $45M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:286 | `$12M` | / Coherence Monitor / $3M / $12M / $35M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:286 | `$35M` | / Coherence Monitor / $3M / $12M / $35M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:286 | `$3M` | / Coherence Monitor / $3M / $12M / $35M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:287 | `$15M` | / **Trend Surfer (NEW)** / $2M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:287 | `$2M` | / **Trend Surfer (NEW)** / $2M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:287 | `$40M` | / **Trend Surfer (NEW)** / $2M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:288 | `$25M` | / **Rhetorical Compiler (NEW)** / $6M / $25M / $70M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:288 | `$6M` | / **Rhetorical Compiler (NEW)** / $6M / $25M / $70M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:288 | `$70M` | / **Rhetorical Compiler (NEW)** / $6M / $25M / $70M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:289 | `$1M` | / **Phase Scheduler (NEW)** / $1M / $8M / $25M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:289 | `$25M` | / **Phase Scheduler (NEW)** / $1M / $8M / $25M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:289 | `$8M` | / **Phase Scheduler (NEW)** / $1M / $8M / $25M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:290 | `$10M` | / **Service Catalyst (NEW)** / $2M / $10M / $30M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:290 | `$2M` | / **Service Catalyst (NEW)** / $2M / $10M / $30M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:290 | `$30M` | / **Service Catalyst (NEW)** / $2M / $10M / $30M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:291 | `$35M` | / OrgOS / $8M / $35M / $90M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:291 | `$8M` | / OrgOS / $8M / $35M / $90M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:291 | `$90M` | / OrgOS / $8M / $35M / $90M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:292 | `$15M` | / Risk Engine / $3M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:292 | `$3M` | / Risk Engine / $3M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:292 | `$40M` | / Risk Engine / $3M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:293 | `$138M` | / **TOTAL** / **$30M** / **$138M** / **$375M** / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:293 | `$30M` | / **TOTAL** / **$30M** / **$138M** / **$375M** / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:293 | `$375M` | / **TOTAL** / **$30M** / **$138M** / **$375M** / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:295 | `20%` | **EBITDA Margin**: -20% (Y1) → +35% (Y2) → +48% (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:295 | `35%` | **EBITDA Margin**: -20% (Y1) → +35% (Y2) → +48% (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:295 | `48%` | **EBITDA Margin**: -20% (Y1) → +35% (Y2) → +48% (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:297 | `$1.1B` | **Valuation**: $250M (Y1) → $1.1B (Y2) → $3B (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:297 | `$250M` | **Valuation**: $250M (Y1) → $1.1B (Y2) → $3B (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:297 | `$3B` | **Valuation**: $250M (Y1) → $1.1B (Y2) → $3B (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:306 | `000+` | - 10,000+ historical trend validation dataset |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:327 | `$50B` | - **8 new products** addressing $50B+ in additional TAM |
| _CANON/arcs-v9-additional/ARCS-YellowPaper-v1-2.md:671 | `5+` | - Patent filings across 5+ novel invention domains |
| _CANON/arcs-v9-additional/ARCS-v9-Chapter-Book-Canon.md:258 | `3+` | If 3+ turns drift from JTBD without producing an artifact, surface: |
| _CANON/arcs-v9-additional/ARCS-v9-Chapter-Book-Canon.md:319 | `2+` | - v10: major (architectural change; requires full Deep Shavasana MetaAudit + 2+ pilot receipts) |
| _CANON/arcs-v9-additional/ARCS-v9-Chapter-Book-Canon.md:480 | `2+` | *Next version bump requires: Deep Shavasana MetaAudit + 2+ pilot receipts* |
| _CANON/book-ii/part-i-firehose-to-compass.md:41 | `50+` | The other response is to outsource the decision itself. Ask the AI. Get a recommendation. Take the answer and move. This works for low-stake |
| _CANON/book-ii/part-i-firehose-to-compass.md:87 | `85%` | > *"This brief renders at 85% fidelity — conviction gradient is still SHIFTING. The True North is directionally reliable but not crystalline |
| _CANON/book-ii/part-i-firehose-to-compass.md:91 | `80+` | **Receipt:** `runtime/specs/dewy-receipt-schema-v1.json` — `render_resolution` field; NCI composite thresholds (HOLD at < 40, fidelity heade |
| _CANON/book-ii/part-i-firehose-to-compass.md:140 | `50+` | / RC-001 / AI recommendation-taking fails for high-conviction-gap decisions / ROM CANDIDATE / Promote after Observatory 50+ session comparis |
| _CANON/index.md:61 | `100+` | **Implementation gates:** See ADR-023 (100+ receipts) + ADR-013 (30-day Lab inquiry threshold) |
| _CANON/living/ARCS-Codex-v8.5.md:58 | `20%` | *   **Example**: `/ward --protocol stop_loss --threshold 20` (Halts project if confidence drops < 20%) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:13 | `$15M` | / **White Paper v2.0** / ARCS-WhitePaper-v2-0.md / Investors, C-suite / Commercial thesis, $15M Series A pitch, 5-year revenue projections / |
| _CANON/living/ARCS-Technical-Overview-April2026.md:63 | `5%` | └── Commercial: 5% gross revenue revenue share |
| _CANON/living/ARCS-Technical-Overview-April2026.md:73 | `$5M` | 2026 /   $5M      / AI Optimizer early adopters |
| _CANON/living/ARCS-Technical-Overview-April2026.md:74 | `$25M` | 2027 /  $25M      / Enterprise OrgOS expansion |
| _CANON/living/ARCS-Technical-Overview-April2026.md:75 | `$80M` | 2028 /  $80M      / Digital Therapeutic launch |
| _CANON/living/ARCS-Technical-Overview-April2026.md:76 | `$200M` | 2029 / $200M      / Multi-product scaled deployment |
| _CANON/living/ARCS-Technical-Overview-April2026.md:77 | `$450M` | 2030 / $450M      / Financial services international |
| _CANON/living/ARCS-Technical-Overview-April2026.md:138 | `95%` | **Confidence Interval (95%):** |
| _CANON/living/ARCS-Technical-Overview-April2026.md:179 | `87%` | Claim: 87% of predictions fall within stated 95% CI |
| _CANON/living/ARCS-Technical-Overview-April2026.md:179 | `95%` | Claim: 87% of predictions fall within stated 95% CI |
| _CANON/living/ARCS-Technical-Overview-April2026.md:185 | `15%` | Claim: MAPE 12–15% (vs 22% baseline) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:185 | `22%` | Claim: MAPE 12–15% (vs 22% baseline) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:199 | `32%` | Claim: Energy sustainability prediction 78% vs 32% (skills-based) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:199 | `78%` | Claim: Energy sustainability prediction 78% vs 32% (skills-based) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:206 | `92%` | Risk: Circular — derived from desired endpoint (92% at 1M receipts) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:209 | `40%` | Claim: 40% ROAS improvement guarantee |
| _CANON/living/ARCS-Technical-Overview-April2026.md:210 | `87%` | Status: Asserted based on 87% accuracy claim |
| _CANON/living/ARCS-Technical-Overview-April2026.md:415 | `$100B` | b) Market cap > $100B, OR |
| _CANON/living/ARCS-Technical-Overview-April2026.md:566 | `3+` | When: 3+ positive signal anomalies converge (>3σ from baseline) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:607 | `25%` | Key parameter: self.threshold = 0.25 (Kairos must be 25% better) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:612 | `25%` | self.threshold = 0.25  # Initial: 25% EV advantage required |
| _CANON/living/ARCS-Technical-Overview-April2026.md:656 | `50+` | / **Data source** / Energy cycles, capacity, recovery / 50+ real-time signal streams / Both coaches' EV outputs / |
| _CANON/living/ARCS-Technical-Overview-April2026.md:693 | `$15M` | → Series A pitch ($15M ask, $75M pre-money) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:693 | `$75M` | → Series A pitch ($15M ask, $75M pre-money) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:696 | `$450M` | → Revenue model: $5M → $450M (2026–2030) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:696 | `$5M` | → Revenue model: $5M → $450M (2026–2030) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:779 | `$49` | / Over-reliance on enterprise sales (9-month cycle) / Business / MEDIUM / SMB self-serve tier (Canon mentions $49/mo) / |
| _CANON/living/ARCS-v9-Canon-Operational.md:126 | `up to 3` | / **SIMPLE** / One True North sentence + up to 3 bullets / Default / |
| operators/arcs_primitives.py:187 | `50+` | 50+ chars scores 1.0. |
| operators/arcs_primitives.py:290 | `r=0.72` | phase_tuning     : Calibration signal (r=0.72 coherence correlation) |
| operators/arcs_primitives.py:292 | `76%` | feels_right      : Gut-level validity check (76% predictive accuracy) |
| operators/arcs_primitives.py:293 | `72%` | that_vibes       : Relational resonance indicator (72% stability predictor) |
| operators/arcs_primitives.py:295 | `Brier score improvement: 0.25→0.12` | expected_vs_actual: Calibration accuracy (Brier score improvement: 0.25→0.12) |
