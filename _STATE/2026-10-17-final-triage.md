# Final triage of the 918 quantified canon tokens (REPORT ONLY, 2026-10-17)

No canon text was edited. Every token is now either covered, marked with one of four triage labels, or listed below as deliberately left. A label is never evidence: the gate still fails every marked token.

| State | Tokens | Meaning |
|---|---|---|
| UNVALIDATED | 315 | a statement of fact or a result with no data, citation or test in the repo |
| PROJECTION | 386 | a target, hypothesis, scenario weight, plan or estimate stated as something to aim at |
| ILLUSTRATIVE | 125 | a worked example, sample output or hypothetical, not a claim about the world |
| PARAMETER | 69 | a design constant, threshold, weight, definition or gate: a specification, not a measurement |
| UNCOVERED | 23 | deliberately left, see below |

## How it was done

I read every remaining line (512 lines, 631 tokens) grouped by the section heading it sits under, assigned a label per section, and overrode it per line where the line differs from its section. Ledger entries are per token (a lookbehind and lookahead of up to 24 characters around the token), so a mark cannot spill onto a neighbouring figure; after generation I checked that no token marked in earlier passes changed state. This is judgement, not measurement. Calls worth a second look:

- Canon v2 Part VI and the atom/molecule results (t-tests, backtests, ROAS tables) are labelled UNVALIDATED: they read as results but nothing in the repo reproduces them, and Part VI already admits N=1, synthetic data and a 14-day backtest.
- Competitor license costs, third-party funder award sizes and market-structure statistics are UNVALIDATED (unsourced figures about other parties).
- Risk probabilities (30%, 25%, 60%...) and churn expectations are PROJECTION: scenario weights, not observations.
- Phenomenology "expected results" and the training-plan Brier trajectory are PROJECTION; its reported-sounding match rates are UNVALIDATED.
- Technical Overview lines that quote the claims it is auditing are UNVALIDATED so the audit does not read as endorsing them.

## Left UNCOVERED on purpose (23 tokens)

All in `_CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md`: named individuals' profile scores (the Fixed / Deliberate / Rapid percentages), event counts and a pre-order example. These are counterpart profile data, not claims about ARCS, and belong to the counterpart-universe review (internal/external air-gap), not to the evidence ledger. Flagged for you: this deck holds named people's profile data inside `_CANON`.

## Full table

| file:line | claim token | state | line (truncated) |
|---|---|---|---|
| _CANON/ARCS-Canon-v1-1.md:53 | `$350B` | UNVALIDATED | - Transform $350B marketing spend from faith-based to evidence-based |
| _CANON/ARCS-Canon-v1-1.md:91 | `68%` | UNVALIDATED | - 87% accuracy (vs. 68% baseline, 76% vs. human experts) |
| _CANON/ARCS-Canon-v1-1.md:91 | `76%` | UNVALIDATED | - 87% accuracy (vs. 68% baseline, 76% vs. human experts) |
| _CANON/ARCS-Canon-v1-1.md:91 | `87%` | UNVALIDATED | - 87% accuracy (vs. 68% baseline, 76% vs. human experts) |
| _CANON/ARCS-Canon-v1-1.md:102 | `50+` | PARAMETER | - Real-time signal convergence detection across 50+ data streams |
| _CANON/ARCS-Canon-v1-1.md:112 | `000+` | PROJECTION | - Receipt database: 100,000+ historical decisions = insurmountable training data advantage |
| _CANON/ARCS-Canon-v1-1.md:118 | `18%` | PROJECTION | - **Phase 1** (0-12 months): Better ROAS → 12-18% annual churn |
| _CANON/ARCS-Canon-v1-1.md:119 | `8%` | PROJECTION | - **Phase 2** (12-24 months): Platform consolidation → 5-8% annual churn |
| _CANON/ARCS-Canon-v1-1.md:120 | `2%` | PROJECTION | - **Phase 3** (24-36 months): Regulatory compliance → <2% annual churn (infrastructure-level) |
| _CANON/ARCS-Canon-v1-1.md:129 | `$102M` | PROJECTION | **Capital Strategy** ($102M with <5% dilution): |
| _CANON/ARCS-Canon-v1-1.md:129 | `5%` | PROJECTION | **Capital Strategy** ($102M with <5% dilution): |
| _CANON/ARCS-Canon-v1-1.md:130 | `$81M` | PROJECTION | 1. **Enterprise Pre-Sale**: $81M from 20 customers (prepaid 3-year contracts at 40% discount) |
| _CANON/ARCS-Canon-v1-1.md:130 | `40%` | PROJECTION | 1. **Enterprise Pre-Sale**: $81M from 20 customers (prepaid 3-year contracts at 40% discount) |
| _CANON/ARCS-Canon-v1-1.md:131 | `$12M` | PROJECTION | 2. **Token Generation Event**: $12M ($ARCS utility token for ecosystem participation) |
| _CANON/ARCS-Canon-v1-1.md:132 | `$180K` | UNVALIDATED | 3. **Revenue Reinvestment**: $4.3M (currently profitable: $180K/month EBITDA) |
| _CANON/ARCS-Canon-v1-1.md:132 | `$4.3M` | PROJECTION | 3. **Revenue Reinvestment**: $4.3M (currently profitable: $180K/month EBITDA) |
| _CANON/ARCS-Canon-v1-1.md:133 | `$5M` | PROJECTION | 4. **Strategic Debt**: $5M credit facility |
| _CANON/ARCS-Canon-v1-1.md:135 | `$70M` | PROJECTION | **vs. Traditional VC**: $70M with 40-50% dilution |
| _CANON/ARCS-Canon-v1-1.md:135 | `50%` | PROJECTION | **vs. Traditional VC**: $70M with 40-50% dilution |
| _CANON/ARCS-Canon-v1-1.md:138 | `$199` | PROJECTION | - Individual: Free basic → $49/month Pro → $199/month Premium |
| _CANON/ARCS-Canon-v1-1.md:138 | `$49` | PROJECTION | - Individual: Free basic → $49/month Pro → $199/month Premium |
| _CANON/ARCS-Canon-v1-1.md:139 | `$299` | PROJECTION | - Team: $299/month (<25 people) → Custom Enterprise |
| _CANON/ARCS-Canon-v1-1.md:140 | `$10K` | PROJECTION | - Ecosystem: $10K-50K/year service licensing + research insights |
| _CANON/ARCS-Canon-v1-1.md:142 | `60%` | PROJECTION | **36-Month Projections** (Base Case, 60% probability): |
| _CANON/ARCS-Canon-v1-1.md:146 | `$15.2M` | PROJECTION | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Canon-v1-1.md:146 | `$412M` | PROJECTION | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Canon-v1-1.md:146 | `$98.4M` | PROJECTION | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Canon-v1-1.md:147 | `0.008%` | PROJECTION | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Canon-v1-1.md:147 | `0.055%` | PROJECTION | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Canon-v1-1.md:147 | `0.23%` | PROJECTION | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Canon-v1-1.md:148 | `28%` | PROJECTION | / EBITDA Margin / -41% / +28% / +44% / |
| _CANON/ARCS-Canon-v1-1.md:148 | `41%` | PROJECTION | / EBITDA Margin / -41% / +28% / +44% / |
| _CANON/ARCS-Canon-v1-1.md:148 | `44%` | PROJECTION | / EBITDA Margin / -41% / +28% / +44% / |
| _CANON/ARCS-Canon-v1-1.md:149 | `$120M` | PROJECTION | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Canon-v1-1.md:149 | `$3.3B` | PROJECTION | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Canon-v1-1.md:149 | `$790M` | PROJECTION | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Canon-v1-1.md:196 | `$850B` | UNVALIDATED | - Global enterprise marketing: $850B annually |
| _CANON/ARCS-Canon-v1-1.md:197 | `$350B` | UNVALIDATED | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Canon-v1-1.md:197 | `500+` | PARAMETER | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Canon-v1-1.md:198 | `$180B` | UNVALIDATED | - Addressable (Fortune 5000 + growth): $180B annually |
| _CANON/ARCS-Canon-v1-1.md:199 | `0.001%` | UNVALIDATED | - **Current penetration**: 0.001% → massive greenfield |
| _CANON/ARCS-Canon-v1-1.md:202 | `$35K` | UNVALIDATED | - 2.3M "cognitive synthesizers" in US underearning $35K/year vs. optimal placement |
| _CANON/ARCS-Canon-v1-1.md:203 | `$51.8B` | UNVALIDATED | - Total addressable earning potential: $51.8B annually |
| _CANON/ARCS-Canon-v1-1.md:204 | `$127B` | UNVALIDATED | - Organizations losing $127B in productivity from suboptimal allocation |
| _CANON/ARCS-Canon-v1-1.md:205 | `$178.8B` | UNVALIDATED | - **Total market**: $178.8B opportunity |
| _CANON/ARCS-Canon-v1-1.md:211 | `30%` | PROJECTION | 1. **Slow Enterprise Adoption** (30% probability, high impact) |
| _CANON/ARCS-Canon-v1-1.md:214 | `25%` | PROJECTION | 2. **Agency/HR Resistance** (25% probability, medium impact) |
| _CANON/ARCS-Canon-v1-1.md:217 | `60%` | PROJECTION | 3. **Large Incumbent Response** (60% probability within 24 months, very high impact) |
| _CANON/ARCS-Canon-v1-1.md:220 | `35%` | PROJECTION | 4. **Regulatory Restriction** (35% probability, medium impact) |
| _CANON/ARCS-Canon-v1-1.md:221 | `18+` | PROJECTION | - *Mitigation*: Proactive SEC engagement, token as utility not security, pre-sale alone funds 18+ months |
| _CANON/ARCS-Canon-v1-1.md:223 | `20%` | PROJECTION | 5. **Technical Execution Failure** (20% probability, very high impact) |
| _CANON/ARCS-Canon-v1-1.md:224 | `20%` | PROJECTION | - *Mitigation*: Hire world-class ML/AI leadership, 20% engineering contingency, alpha program validation, performance guarantee exit clause |
| _CANON/ARCS-Canon-v1-1.md:312 | `18%` | ILLUSTRATIVE | - Inventory: CPMs drop 18% (traffic signal) |
| _CANON/ARCS-Canon-v1-1.md:313 | `34%` | ILLUSTRATIVE | - Audience: r/cryptocurrency engagement +34% (audience signal) |
| _CANON/ARCS-Canon-v1-1.md:316 | `$200K` | ILLUSTRATIVE | Action: Increase Reddit budget by $200K immediately |
| _CANON/ARCS-Canon-v1-1.md:317 | `$640K` | ILLUSTRATIVE | Expected Value: $640K incremental return (3.2× on opportunity spend) |
| _CANON/ARCS-Canon-v1-1.md:318 | `$780K` | ILLUSTRATIVE | Actual Outcome: $780K return (3.9×, window captured before close) |
| _CANON/ARCS-Canon-v1-1.md:349 | `over 12` | PROJECTION | - Track individuals over 12-18 months post-placement |
| _CANON/ARCS-Canon-v1-1.md:351 | `32%` | UNVALIDATED | - Prediction accuracy: >78% for role sustainability (vs. <32% for skills-based matching) |
| _CANON/ARCS-Canon-v1-1.md:351 | `78%` | UNVALIDATED | - Prediction accuracy: >78% for role sustainability (vs. <32% for skills-based matching) |
| _CANON/ARCS-Canon-v1-1.md:436 | `$2` | ILLUSTRATIVE | ✅ Campaign archetype: "B2B SaaS acquisition, $2-5M budget, Reddit + Meta channels" |
| _CANON/ARCS-Canon-v1-1.md:437 | `32%` | ILLUSTRATIVE | ✅ Pattern: "Mobile creative outperformed desktop 32% in crypto vertical" |
| _CANON/ARCS-Canon-v1-1.md:494 | `95%` | PARAMETER | **Key Innovation**: Unlike systems claiming deterministic predictions, this framework provides *honest uncertainty quantification*. A predic |
| _CANON/ARCS-Canon-v1-1.md:512 | `$100K` | PARAMETER | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$100K` | PARAMETER | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$10M` | PARAMETER | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$10M` | PARAMETER | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$1M` | PARAMETER | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:512 | `$1M` | PARAMETER | - Budget tier (< $100K, $100K-$1M, $1M-$10M, > $10M) |
| _CANON/ARCS-Canon-v1-1.md:566 | `68%` | UNVALIDATED | - \(A_0\) = Baseline accuracy with zero network ≈ 68% |
| _CANON/ARCS-Canon-v1-1.md:567 | `92%` | UNVALIDATED | - \(A_{\infty}\) = Asymptotic accuracy at infinite scale ≈ 92% |
| _CANON/ARCS-Canon-v1-1.md:574 | `1%` | UNVALIDATED | / 10              / 5,000    / 69%               / 1% advantage        / |
| _CANON/ARCS-Canon-v1-1.md:574 | `69%` | UNVALIDATED | / 10              / 5,000    / 69%               / 1% advantage        / |
| _CANON/ARCS-Canon-v1-1.md:575 | `77%` | UNVALIDATED | / 100             / 50,000   / 77%               / 8% advantage        / |
| _CANON/ARCS-Canon-v1-1.md:575 | `8%` | UNVALIDATED | / 100             / 50,000   / 77%               / 8% advantage        / |
| _CANON/ARCS-Canon-v1-1.md:576 | `16%` | UNVALIDATED | / 500             / 250,000  / 85%               / 16% advantage       / |
| _CANON/ARCS-Canon-v1-1.md:576 | `85%` | UNVALIDATED | / 500             / 250,000  / 85%               / 16% advantage       / |
| _CANON/ARCS-Canon-v1-1.md:577 | `19%` | UNVALIDATED | / 1,000           / 500,000  / 88%               / 19% advantage       / |
| _CANON/ARCS-Canon-v1-1.md:577 | `88%` | UNVALIDATED | / 1,000           / 500,000  / 88%               / 19% advantage       / |
| _CANON/ARCS-Canon-v1-1.md:579 | `19%` | UNVALIDATED | **Strategic Implication**: By the time platform reaches 500 customers (250K receipts), new entrant faces insurmountable disadvantage. Ration |
| _CANON/ARCS-Canon-v1-1.md:608 | `50%` | PARAMETER | - \(\theta\) = Threshold for override (typically 25-50% EV improvement) |
| _CANON/ARCS-Canon-v1-1.md:613 | `$2.1M` | ILLUSTRATIVE | - EV: $2.1M incremental revenue |
| _CANON/ARCS-Canon-v1-1.md:614 | `82%` | ILLUSTRATIVE | - Confidence: 82% |
| _CANON/ARCS-Canon-v1-1.md:618 | `$780K` | ILLUSTRATIVE | - EV: $780K incremental revenue |
| _CANON/ARCS-Canon-v1-1.md:619 | `78%` | ILLUSTRATIVE | - Confidence: 78% |
| _CANON/ARCS-Canon-v1-1.md:622 | `$2.1M` | ILLUSTRATIVE | Arbitration: EV gap ($780K vs $2.1M) doesn't exceed 25% threshold |
| _CANON/ARCS-Canon-v1-1.md:622 | `$780K` | ILLUSTRATIVE | Arbitration: EV gap ($780K vs $2.1M) doesn't exceed 25% threshold |
| _CANON/ARCS-Canon-v1-1.md:622 | `25%` | ILLUSTRATIVE | Arbitration: EV gap ($780K vs $2.1M) doesn't exceed 25% threshold |
| _CANON/ARCS-Canon-v1-1.md:631 | `3+` | PARAMETER | 1. **Anomaly Detection**: Identify 3+ σ deviations from baseline across data streams |
| _CANON/ARCS-Canon-v1-1.md:632 | `3+` | PARAMETER | 2. **Convergence Check**: Require 3+ positive signals aligning simultaneously |
| _CANON/ARCS-Canon-v1-1.md:701 | `78%` | PROJECTION | **Target Accuracy**: >78% prediction of 12-month role sustainability |
| _CANON/ARCS-Canon-v1-1.md:704 | `000+` | PROJECTION | - Longitudinal cohort studies (track 1,000+ placements over 18 months) |
| _CANON/ARCS-Canon-v1-1.md:704 | `over 18` | PROJECTION | - Longitudinal cohort studies (track 1,000+ placements over 18 months) |
| _CANON/ARCS-Canon-v1-1.md:721 | `32%` | ILLUSTRATIVE | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:721 | `87%` | ILLUSTRATIVE | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:769 | `R = 0.7` | UNVALIDATED | - \(R = 0.7-0.9\): Typical high-performing teams |
| _CANON/ARCS-Canon-v1-1.md:785 | `$350B` | UNVALIDATED | ### Problem Statement: The $350B Accountability Crisis |
| _CANON/ARCS-Canon-v1-1.md:790 | `$850B` | UNVALIDATED | - Global: $850B annually |
| _CANON/ARCS-Canon-v1-1.md:791 | `$350B` | UNVALIDATED | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Canon-v1-1.md:791 | `500+` | PARAMETER | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Canon-v1-1.md:792 | `$180B` | UNVALIDATED | - Fortune 5000 + high-growth companies: $180B annually (addressable market) |
| _CANON/ARCS-Canon-v1-1.md:797 | `$50M` | UNVALIDATED | - Marketing leaders allocate $50M+ budgets without documented reasoning |
| _CANON/ARCS-Canon-v1-1.md:812 | `$100K` | UNVALIDATED | - CFOs document every $100K financial decision |
| _CANON/ARCS-Canon-v1-1.md:813 | `$100M` | UNVALIDATED | - CMOs allocate $100M marketing budgets on intuition |
| _CANON/ARCS-Canon-v1-1.md:842 | `40%` | PROJECTION | - **Value Prop**: 40% ROAS improvement with performance guarantee [Unvalidated target: asserted threshold, no control group; see Technical O |
| _CANON/ARCS-Canon-v1-1.md:845 | `18%` | PROJECTION | - **Expected Churn**: 12-18% annually |
| _CANON/ARCS-Canon-v1-1.md:849 | `$5M` | PROJECTION | - **Value Prop**: Vendor consolidation saves $5M+ annually |
| _CANON/ARCS-Canon-v1-1.md:852 | `8%` | PROJECTION | - **Expected Churn**: 5-8% annually |
| _CANON/ARCS-Canon-v1-1.md:859 | `2%` | PROJECTION | - **Expected Churn**: <2% annually (infrastructure-level retention) |
| _CANON/ARCS-Canon-v1-1.md:865 | `18%` | PROJECTION | / 1     / 12-18%       / Performance advantage / Moderate (recipe can be copied) / |
| _CANON/ARCS-Canon-v1-1.md:866 | `8%` | PROJECTION | / 2     / 5-8%         / Operational dependency / High (data migration expensive) / |
| _CANON/ARCS-Canon-v1-1.md:867 | `2%` | PROJECTION | / 3     / <2%          / Legal necessity / Extreme (infinite switching cost) / |
| _CANON/ARCS-Canon-v1-1.md:879 | `$7.5M` | PROJECTION | / Private / $7.5M / Zero (hoarded) / 72% / Agency protects asymmetry / |
| _CANON/ARCS-Canon-v1-1.md:879 | `72%` | UNVALIDATED | / Private / $7.5M / Zero (hoarded) / 72% / Agency protects asymmetry / |
| _CANON/ARCS-Canon-v1-1.md:880 | `$4.5M` | PROJECTION | / Partial / $4.5M / Anonymized patterns / 82% / Rational middle ground / |
| _CANON/ARCS-Canon-v1-1.md:880 | `82%` | UNVALIDATED | / Partial / $4.5M / Anonymized patterns / 82% / Rational middle ground / |
| _CANON/ARCS-Canon-v1-1.md:881 | `$2.5M` | PROJECTION | / Full / $2.5M / All receipts shared / 87% / Transparent agencies win / |
| _CANON/ARCS-Canon-v1-1.md:881 | `87%` | UNVALIDATED | / Full / $2.5M / All receipts shared / 87% / Transparent agencies win / |
| _CANON/ARCS-Canon-v1-1.md:887 | `15%` | UNVALIDATED | 2. Clients observe 15% performance gap vs. Tier 3 |
| _CANON/ARCS-Canon-v1-1.md:904 | `50%` | ILLUSTRATIVE | - **Discrepancy revealed**: Agency stated 4.5× but privately believed 3.0× (50% gap = knowing overpromise) |
| _CANON/ARCS-Canon-v1-1.md:918 | `40%` | PROJECTION | **Implementation**: "40% ROAS improvement or full refund" |
| _CANON/ARCS-Canon-v1-1.md:924 | `80%` | PARAMETER | - If client followed recommendations ≥80% and failed → ARCS refunds |
| _CANON/ARCS-Canon-v1-1.md:1024 | `$9.5M` | ILLUSTRATIVE | "decision_rationale": "Optimal balance of expected value ($9.5M revenue) vs. risk (24% downside scenarios). Reddit represents 60% allocation |
| _CANON/ARCS-Canon-v1-1.md:1024 | `24%` | ILLUSTRATIVE | "decision_rationale": "Optimal balance of expected value ($9.5M revenue) vs. risk (24% downside scenarios). Reddit represents 60% allocation |
| _CANON/ARCS-Canon-v1-1.md:1024 | `60%` | ILLUSTRATIVE | "decision_rationale": "Optimal balance of expected value ($9.5M revenue) vs. risk (24% downside scenarios). Reddit represents 60% allocation |
| _CANON/ARCS-Canon-v1-1.md:1024 | `94%` | ILLUSTRATIVE | "decision_rationale": "Optimal balance of expected value ($9.5M revenue) vs. risk (24% downside scenarios). Reddit represents 60% allocation |
| _CANON/ARCS-Canon-v1-1.md:1038 | `$40K` | ILLUSTRATIVE | "variance_explanation": "Outperformed due to regulatory clarity announcement creating 18-hour kairos window. Capitalized with $40K additiona |
| _CANON/ARCS-Canon-v1-1.md:1071 | `3+` | PARAMETER | - CPM fluctuations (detect 3+ σ deviations from 30-day baseline) |
| _CANON/ARCS-Canon-v1-1.md:1097 | `18%` | ILLUSTRATIVE | ├── Signal 1 (Inventory): Reddit CPMs drop 18% (3.2σ anomaly) |
| _CANON/ARCS-Canon-v1-1.md:1098 | `34%` | ILLUSTRATIVE | ├── Signal 2 (Audience): r/cryptocurrency engagement spike +34% (4.1σ) |
| _CANON/ARCS-Canon-v1-1.md:1104 | `95%` | ILLUSTRATIVE | └── 95% Confidence: [2.1 hours, 8.3 hours] |
| _CANON/ARCS-Canon-v1-1.md:1107 | `$200K` | ILLUSTRATIVE | ├── Incremental Budget: $200K (reallocated from next week's Meta spend) |
| _CANON/ARCS-Canon-v1-1.md:1109 | `$640K` | ILLUSTRATIVE | ├── Expected Return: $640K revenue |
| _CANON/ARCS-Canon-v1-1.md:1110 | `$486K` | ILLUSTRATIVE | └── Risk-Adjusted EV: $486K (76% confidence × $640K return) |
| _CANON/ARCS-Canon-v1-1.md:1110 | `$640K` | ILLUSTRATIVE | └── Risk-Adjusted EV: $486K (76% confidence × $640K return) |
| _CANON/ARCS-Canon-v1-1.md:1110 | `76%` | ILLUSTRATIVE | └── Risk-Adjusted EV: $486K (76% confidence × $640K return) |
| _CANON/ARCS-Canon-v1-1.md:1113 | `$200K` | ILLUSTRATIVE | └── Action: Increase Reddit budget by $200K immediately |
| _CANON/ARCS-Canon-v1-1.md:1114 | `78%` | ILLUSTRATIVE | Confidence: 78% |
| _CANON/ARCS-Canon-v1-1.md:1120 | `$780K` | ILLUSTRATIVE | └── Result: $780K actual return (3.9× ROAS, 22% better than prediction) |
| _CANON/ARCS-Canon-v1-1.md:1120 | `22%` | ILLUSTRATIVE | └── Result: $780K actual return (3.9× ROAS, 22% better than prediction) |
| _CANON/ARCS-Canon-v1-1.md:1125 | `32%` | ILLUSTRATIVE | └── Creative: Mobile-optimized creative outperformed desktop 32% in this window |
| _CANON/ARCS-Canon-v1-1.md:1134 | `$178.8B` | UNVALIDATED | ### Problem Statement: The $178.8B Misallocation Crisis |
| _CANON/ARCS-Canon-v1-1.md:1140 | `$35,000` | UNVALIDATED | - Currently underearning **$35,000 annually** vs. optimal placement |
| _CANON/ARCS-Canon-v1-1.md:1141 | `$51.8B` | UNVALIDATED | - **Total addressable earning potential**: $51.8B annually |
| _CANON/ARCS-Canon-v1-1.md:1142 | `$127B` | UNVALIDATED | - Organizations losing **$127B in productivity** from suboptimal allocation |
| _CANON/ARCS-Canon-v1-1.md:1143 | `$178.8B` | UNVALIDATED | - **Combined opportunity**: $178.8B |
| _CANON/ARCS-Canon-v1-1.md:1171 | `60%` | UNVALIDATED | - 60%+ of cognitive synthesizers are neurodivergent (ADHD, autism, dyslexia) |
| _CANON/ARCS-Canon-v1-1.md:1208 | `$200` | UNVALIDATED | - ❌ Expensive ($200/hour, $50K retainer for executives) |
| _CANON/ARCS-Canon-v1-1.md:1208 | `$50K` | UNVALIDATED | - ❌ Expensive ($200/hour, $50K retainer for executives) |
| _CANON/ARCS-Canon-v1-1.md:1226 | `5+` | ILLUSTRATIVE | - Process: Boolean matching (IF Python AND 5+ years THEN interview) |
| _CANON/ARCS-Canon-v1-1.md:1233 | `87%` | ILLUSTRATIVE | - Output: Probabilistic (87% match with confidence interval) |
| _CANON/ARCS-Canon-v1-1.md:1240 | `68%` | UNVALIDATED | / Skills-Based Matching / 12-month retention / 68% / |
| _CANON/ARCS-Canon-v1-1.md:1241 | `32%` | UNVALIDATED | / Skills-Based Matching / Sustained high performance / 32% / |
| _CANON/ARCS-Canon-v1-1.md:1242 | `91%` | UNVALIDATED | / ARCS Energy-First / 12-month retention / 91% / |
| _CANON/ARCS-Canon-v1-1.md:1243 | `78%` | UNVALIDATED | / ARCS Energy-First / Sustained high performance / 78% / |
| _CANON/ARCS-Canon-v1-1.md:1248 | `$15K` | UNVALIDATED | - Burnout is expensive ($15K-50K per replacement + lost productivity) |
| _CANON/ARCS-Canon-v1-1.md:1252 | `32%` | ILLUSTRATIVE | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:1252 | `87%` | ILLUSTRATIVE | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:1252 | `91%` | ILLUSTRATIVE | > "This role matches 87% of your energy signature. People with similar patterns report sustained engagement 14 months in, with 32% salary gr |
| _CANON/ARCS-Canon-v1-1.md:1354 | `$80K` | ILLUSTRATIVE | "salary_delta": "+$80K", |
| _CANON/ARCS-Canon-v1-1.md:1361 | `$120K` | ILLUSTRATIVE | "salary_delta": "+$120K", |
| _CANON/ARCS-Canon-v1-1.md:1406 | `$120K` | ILLUSTRATIVE | - **Counterfactual wisdom**: Declined $120K higher comp for energy optimization (non-obvious decision) |
| _CANON/ARCS-Canon-v1-1.md:1429 | `000+` | PARAMETER | 3. **Path Simulation** (1,000+ trajectories) |
| _CANON/ARCS-Canon-v1-1.md:1448 | `12%` | ILLUSTRATIVE | ├── Direct Application to Climate Startups: 12% success rate |
| _CANON/ARCS-Canon-v1-1.md:1451 | `43%` | ILLUSTRATIVE | ├── Lateral Move to Energy-Adjacent Role: 43% success rate |
| _CANON/ARCS-Canon-v1-1.md:1456 | `28%` | ILLUSTRATIVE | ├── Graduate Degree → Pivot: 28% success rate |
| _CANON/ARCS-Canon-v1-1.md:1458 | `$150K` | ILLUSTRATIVE | │   ├── Cons: 2-year opportunity cost, $150K debt |
| _CANON/ARCS-Canon-v1-1.md:1461 | `73%` | ILLUSTRATIVE | └── Design → Product Pipeline: 73% success rate ⭐ RECOMMENDED |
| _CANON/ARCS-Canon-v1-1.md:1469 | `73%` | ILLUSTRATIVE | Confidence: 73% success rate (highest of all paths) |
| _CANON/ARCS-Canon-v1-1.md:1473 | `$140K` | ILLUSTRATIVE | Comp Trajectory: $140K → $165K → $220K (5-year total) |
| _CANON/ARCS-Canon-v1-1.md:1473 | `$165K` | ILLUSTRATIVE | Comp Trajectory: $140K → $165K → $220K (5-year total) |
| _CANON/ARCS-Canon-v1-1.md:1473 | `$220K` | ILLUSTRATIVE | Comp Trajectory: $140K → $165K → $220K (5-year total) |
| _CANON/ARCS-Canon-v1-1.md:1477 | `73%` | ILLUSTRATIVE | > "We simulated 1,000 paths to senior climate tech role. 73% succeed via design → product pipeline. Critical decision in 4 months: accept la |
| _CANON/ARCS-Canon-v1-1.md:1553 | `92%` | ILLUSTRATIVE | ├── Research Scientist, Climate Modeling Lab (92% match) |
| _CANON/ARCS-Canon-v1-1.md:1556 | `87%` | ILLUSTRATIVE | ├── Senior PM, Open Climate Data Platform (87% match) |
| _CANON/ARCS-Canon-v1-1.md:1559 | `71%` | ILLUSTRATIVE | └── Design Lead, Decarbonization SaaS (71% match) |
| _CANON/ARCS-Canon-v1-1.md:1563 | `23%` | ILLUSTRATIVE | └── BD Manager, Carbon Credits Trading (23% match) |
| _CANON/ARCS-Canon-v1-1.md:1576 | `50+` | PARAMETER | - Team size preference (1-5, 5-15, 15-50, 50+) |
| _CANON/ARCS-Canon-v1-1.md:1619 | `000+` | PROJECTION | - Longitudinal cohort studies (1,000+ placements tracked 18 months) |
| _CANON/ARCS-Canon-v1-1.md:1623 | `78%` | PROJECTION | **Accuracy Target**: >78% prediction of 12-month sustainability |
| _CANON/ARCS-Canon-v1-1.md:1671 | `67%` | ILLUSTRATIVE | > "We filtered 67% noise from your career data. Your true signal shows exceptional pattern recognition and synthesis capabilities that stand |
| _CANON/ARCS-Canon-v1-1.md:1693 | `$2.5M` | ILLUSTRATIVE | - EV: $2.5M lifetime career capital if rested and perform well |
| _CANON/ARCS-Canon-v1-1.md:1694 | `84%` | ILLUSTRATIVE | - Confidence: 84% (strong evidence that burnout → poor interview performance) |
| _CANON/ARCS-Canon-v1-1.md:1699 | `$1.8M` | ILLUSTRATIVE | - EV: $1.8M lifetime career capital if land role despite fatigue |
| _CANON/ARCS-Canon-v1-1.md:1700 | `62%` | ILLUSTRATIVE | - Confidence: 62% (fatigued interview performance risky, but opportunity rare) |
| _CANON/ARCS-Canon-v1-1.md:1703 | `$1.8M` | ILLUSTRATIVE | - EV Comparison: $2.5M (Chronos) vs $1.8M (Kairos) |
| _CANON/ARCS-Canon-v1-1.md:1703 | `$2.5M` | ILLUSTRATIVE | - EV Comparison: $2.5M (Chronos) vs $1.8M (Kairos) |
| _CANON/ARCS-Canon-v1-1.md:1704 | `25%` | PARAMETER | - Threshold: 25% improvement needed to override Chronos |
| _CANON/ARCS-Canon-v1-1.md:1705 | `$1.8M` | ILLUSTRATIVE | - Gap: 28% shortfall ($2.5M - $1.8M = $700K opportunity cost) |
| _CANON/ARCS-Canon-v1-1.md:1705 | `$2.5M` | ILLUSTRATIVE | - Gap: 28% shortfall ($2.5M - $1.8M = $700K opportunity cost) |
| _CANON/ARCS-Canon-v1-1.md:1705 | `$700K` | ILLUSTRATIVE | - Gap: 28% shortfall ($2.5M - $1.8M = $700K opportunity cost) |
| _CANON/ARCS-Canon-v1-1.md:1705 | `28%` | ILLUSTRATIVE | - Gap: 28% shortfall ($2.5M - $1.8M = $700K opportunity cost) |
| _CANON/ARCS-Canon-v1-1.md:1952 | `$5` | PROJECTION | └── Cost: ~$5-10 per receipt (batched) |
| _CANON/ARCS-Canon-v1-1.md:1957 | `$0.001` | PROJECTION | └── Cost: ~$0.001 per receipt |
| _CANON/ARCS-Canon-v1-1.md:2349 | `95%` | PARAMETER | # 95% confidence interval (±1.96 standard deviations) |
| _CANON/ARCS-Canon-v1-1.md:2419 | `95%` | PARAMETER | # For 95% CI, 95% of actual outcomes should fall within interval |
| _CANON/ARCS-Canon-v1-1.md:2419 | `95%` | PARAMETER | # For 95% CI, 95% of actual outcomes should fall within interval |
| _CANON/ARCS-Canon-v1-1.md:2476 | `40%` | PARAMETER | predictions.append(('CBR', cbr_pred, 0.4))  # 40% weight |
| _CANON/ARCS-Canon-v1-1.md:2480 | `20%` | PARAMETER | predictions.append(('REG', reg_pred, 0.2))  # 20% weight |
| _CANON/ARCS-Canon-v1-1.md:2484 | `25%` | PARAMETER | predictions.append(('NN', nn_pred, 0.25))  # 25% weight |
| _CANON/ARCS-Canon-v1-1.md:2488 | `10%` | PARAMETER | predictions.append(('BAYES', bayes_pred, 0.1))  # 10% weight |
| _CANON/ARCS-Canon-v1-1.md:2492 | `5%` | PARAMETER | predictions.append(('EXPERT', expert_pred, 0.05))  # 5% weight |
| _CANON/ARCS-Canon-v1-1.md:2893 | `$200M` | ILLUSTRATIVE | # Result: Series C announced ($200M) - rapid growth mode |
| _CANON/ARCS-Canon-v1-1.md:2922 | `25%` | PARAMETER | self.threshold = 0.25  # Kairos must be 25%+ better to override |
| _CANON/ARCS-Canon-v1-1.md:3027 | `$2` | ILLUSTRATIVE | - Campaign archetypes: "B2B SaaS acquisition, $2-5M budget, Reddit + Meta channels" |
| _CANON/ARCS-Canon-v1-1.md:3028 | `32%` | ILLUSTRATIVE | - Performance benchmarks: "Mobile creative outperformed desktop 32% in crypto vertical" |
| _CANON/ARCS-Canon-v1-1.md:3201 | `92%` | UNVALIDATED | #   'asymptotic_accuracy': 0.92,  # 92% accuracy at infinite customers |
| _CANON/ARCS-Canon-v1-1.md:3202 | `68%` | UNVALIDATED | #   'baseline_accuracy': 0.68,     # 68% with zero network |
| _CANON/ARCS-Canon-v1-1.md:3212 | `1%` | UNVALIDATED | / 10        / 5,000    / 69%      / 1% (negligible)           / |
| _CANON/ARCS-Canon-v1-1.md:3212 | `69%` | UNVALIDATED | / 10        / 5,000    / 69%      / 1% (negligible)           / |
| _CANON/ARCS-Canon-v1-1.md:3213 | `77%` | UNVALIDATED | / 100       / 50,000   / 77%      / 9% (noticeable)           / |
| _CANON/ARCS-Canon-v1-1.md:3213 | `9%` | UNVALIDATED | / 100       / 50,000   / 77%      / 9% (noticeable)           / |
| _CANON/ARCS-Canon-v1-1.md:3214 | `17%` | UNVALIDATED | / 500       / 250,000  / 85%      / 17% (significant)         / |
| _CANON/ARCS-Canon-v1-1.md:3214 | `85%` | UNVALIDATED | / 500       / 250,000  / 85%      / 17% (significant)         / |
| _CANON/ARCS-Canon-v1-1.md:3215 | `20%` | UNVALIDATED | / 1,000     / 500,000  / 88%      / 20% (insurmountable)      / |
| _CANON/ARCS-Canon-v1-1.md:3215 | `88%` | UNVALIDATED | / 1,000     / 500,000  / 88%      / 20% (insurmountable)      / |
| _CANON/ARCS-Canon-v1-1.md:3219 | `17%` | UNVALIDATED | By the time platform reaches 500 customers (250K receipts), new entrant faces 17% accuracy disadvantage. Rational customers prefer establish |
| _CANON/ARCS-Canon-v1-1.md:3338 | `18%` | PROJECTION | └── Churn: 12-18% annually |
| _CANON/ARCS-Canon-v1-1.md:3341 | `40+` | PROJECTION | └── Position: "Replace 40+ tools with one platform" |
| _CANON/ARCS-Canon-v1-1.md:3343 | `8%` | PROJECTION | └── Churn: 5-8% annually |
| _CANON/ARCS-Canon-v1-1.md:3348 | `2%` | PROJECTION | └── Churn: <2% annually |
| _CANON/ARCS-Canon-v1-1.md:3353 | `40%` | PROJECTION | **Value Proposition**: "40% ROAS improvement with performance guarantee" [Unvalidated target: asserted threshold, no control group; see Tech |
| _CANON/ARCS-Canon-v1-1.md:3371 | `$500K` | PROJECTION | - Select 1-2 campaigns for pilot ($500K-2M budget) |
| _CANON/ARCS-Canon-v1-1.md:3388 | `19+` | PROJECTION | Week 19+: Expansion |
| _CANON/ARCS-Canon-v1-1.md:3399 | `$150K` | PROJECTION | / Pilot / $150K / 2-5 / 50-200 / Basic / Proof of concept / |
| _CANON/ARCS-Canon-v1-1.md:3400 | `$750K` | PROJECTION | / Growth / $750K / 10-30 / 500-2000 / Standard / Mid-market / |
| _CANON/ARCS-Canon-v1-1.md:3401 | `$2.5M` | PROJECTION | / Enterprise / $2.5M / Unlimited / Unlimited / Premium / Fortune 1000 / |
| _CANON/ARCS-Canon-v1-1.md:3408 | `10%` | PROJECTION | If ARCS-recommended campaigns underperform baseline by >10%: |
| _CANON/ARCS-Canon-v1-1.md:3409 | `80%` | PARAMETER | AND client followed ≥80% of recommendations: |
| _CANON/ARCS-Canon-v1-1.md:3410 | `50%` | PROJECTION | THEN full refund + next year 50% discount |
| _CANON/ARCS-Canon-v1-1.md:3419 | `$15.2M` | PROJECTION | - $15.2M ARR |
| _CANON/ARCS-Canon-v1-1.md:3420 | `120%` | PROJECTION | - Net Revenue Retention: 120% (expansion within accounts) |
| _CANON/ARCS-Canon-v1-1.md:3422 | `87%` | UNVALIDATED | - Prediction accuracy: 87% (actual outcomes within stated confidence intervals) |
| _CANON/ARCS-Canon-v1-1.md:3426 | `$5M` | PROJECTION | **Value Proposition**: "Eliminate $5M+ in redundant vendors" |
| _CANON/ARCS-Canon-v1-1.md:3432 | `$200K` | UNVALIDATED | - CDP (Segment, mParticle): $200K/year |
| _CANON/ARCS-Canon-v1-1.md:3433 | `$150K` | UNVALIDATED | - DMP (Adobe Audience Manager): $150K/year |
| _CANON/ARCS-Canon-v1-1.md:3434 | `$300K` | UNVALIDATED | - CRM (Salesforce Marketing Cloud): $300K/year |
| _CANON/ARCS-Canon-v1-1.md:3437 | `$180K` | UNVALIDATED | - Attribution (Rockerbox, Neustar): $180K/year |
| _CANON/ARCS-Canon-v1-1.md:3438 | `$120K` | UNVALIDATED | - Web Analytics (Adobe Analytics): $120K/year |
| _CANON/ARCS-Canon-v1-1.md:3439 | `$80K` | UNVALIDATED | - Product Analytics (Amplitude): $80K/year |
| _CANON/ARCS-Canon-v1-1.md:3442 | `$100K` | UNVALIDATED | - Marketing Automation (Marketo, Eloqua): $100K/year |
| _CANON/ARCS-Canon-v1-1.md:3443 | `$200K` | UNVALIDATED | - Social Management (Sprinklr): $200K/year |
| _CANON/ARCS-Canon-v1-1.md:3444 | `$60K` | UNVALIDATED | - Email Platform (Iterable): $60K/year |
| _CANON/ARCS-Canon-v1-1.md:3447 | `$30K` | UNVALIDATED | - Project Management (Monday.com): $30K/year |
| _CANON/ARCS-Canon-v1-1.md:3448 | `$75K` | UNVALIDATED | - Creative Management (Bynder): $75K/year |
| _CANON/ARCS-Canon-v1-1.md:3449 | `$50K` | UNVALIDATED | - Approvals (Workfront): $50K/year |
| _CANON/ARCS-Canon-v1-1.md:3451 | `$1.545M` | UNVALIDATED | Total: $1.545M/year in licensing fees alone |
| _CANON/ARCS-Canon-v1-1.md:3452 | `$2` | UNVALIDATED | + $2-3M/year in integration maintenance, training, overhead |
| _CANON/ARCS-Canon-v1-1.md:3453 | `$3.5` | UNVALIDATED | = $3.5-4.5M total martech cost |
| _CANON/ARCS-Canon-v1-1.md:3468 | `$3` | PROJECTION | Year 3 (Phase 3): Full replacement → Customer saves $3-4M annually |
| _CANON/ARCS-Canon-v1-1.md:3496 | `$500K` | UNVALIDATED | - Data migration: 6-12 months, $500K-2M cost |
| _CANON/ARCS-Canon-v1-1.md:3497 | `$200K` | UNVALIDATED | - Team retraining: 3-6 months, $200K-500K cost |
| _CANON/ARCS-Canon-v1-1.md:3498 | `$300K` | UNVALIDATED | - Integration rebuild: $300K-800K cost |
| _CANON/ARCS-Canon-v1-1.md:3501 | `$1M` | UNVALIDATED | **Total Switching Cost**: $1M-3.5M + 9-18 months disruption |
| _CANON/ARCS-Canon-v1-1.md:3503 | `18%` | UNVALIDATED | **Expected Churn**: 5-8% annually (vs. 12-18% in Phase 1) |
| _CANON/ARCS-Canon-v1-1.md:3503 | `8%` | UNVALIDATED | **Expected Churn**: 5-8% annually (vs. 12-18% in Phase 1) |
| _CANON/ARCS-Canon-v1-1.md:3509 | `$3.5M` | PROJECTION | / Platform / $3.5M / Replace $4.5M martech stack / Enterprise (5,000+ employees) / |
| _CANON/ARCS-Canon-v1-1.md:3509 | `$4.5M` | UNVALIDATED | / Platform / $3.5M / Replace $4.5M martech stack / Enterprise (5,000+ employees) / |
| _CANON/ARCS-Canon-v1-1.md:3509 | `000+` | UNVALIDATED | / Platform / $3.5M / Replace $4.5M martech stack / Enterprise (5,000+ employees) / |
| _CANON/ARCS-Canon-v1-1.md:3510 | `$5M` | PROJECTION | / Enterprise+ / $5M / + Custom integrations, dedicated CSM / Fortune 500 / |
| _CANON/ARCS-Canon-v1-1.md:3516 | `$98.4M` | PROJECTION | - $98.4M ARR |
| _CANON/ARCS-Canon-v1-1.md:3517 | `5%` | PROJECTION | - Gross retention: 95% (only 5% churn) |
| _CANON/ARCS-Canon-v1-1.md:3517 | `95%` | PROJECTION | - Gross retention: 95% (only 5% churn) |
| _CANON/ARCS-Canon-v1-1.md:3518 | `130%` | PROJECTION | - Net retention: 130% (expansion + upsells) |
| _CANON/ARCS-Canon-v1-1.md:3519 | `$1.16M` | PROJECTION | - Average contract value: $1.16M (up from $507K in Phase 1) |
| _CANON/ARCS-Canon-v1-1.md:3519 | `$507K` | PROJECTION | - Average contract value: $1.16M (up from $507K in Phase 1) |
| _CANON/ARCS-Canon-v1-1.md:3532 | `$50M` | PARAMETER | - Proposal: Extend disclosure requirements to marketing spend >$50M |
| _CANON/ARCS-Canon-v1-1.md:3546 | `$10M` | PARAMETER | - Fiduciary duty requires documented rationale for $10M+ allocations |
| _CANON/ARCS-Canon-v1-1.md:3553 | `$1M` | PARAMETER | - Document financial decisions >$1M |
| _CANON/ARCS-Canon-v1-1.md:3558 | `$50M` | UNVALIDATED | - Marketing is $50M-500M for Fortune 1000 |
| _CANON/ARCS-Canon-v1-1.md:3574 | `$4M` | ILLUSTRATIVE | 2026: "We choose ARCS because it saves $4M in martech costs" |
| _CANON/ARCS-Canon-v1-1.md:3584 | `3+` | PROJECTION | - 3+ years of decision receipts (50K-200K) |
| _CANON/ARCS-Canon-v1-1.md:3613 | `$10M` | PROJECTION | / Compliance / $4M / Required for regulatory adherence / vs. $10M+ litigation risk / |
| _CANON/ARCS-Canon-v1-1.md:3613 | `$4M` | PROJECTION | / Compliance / $4M / Required for regulatory adherence / vs. $10M+ litigation risk / |
| _CANON/ARCS-Canon-v1-1.md:3614 | `$20M` | PROJECTION | / Governance / $6M / Board-grade reporting + audit support / vs. $20M+ shareholder derivative suit / |
| _CANON/ARCS-Canon-v1-1.md:3614 | `$6M` | PROJECTION | / Governance / $6M / Board-grade reporting + audit support / vs. $20M+ shareholder derivative suit / |
| _CANON/ARCS-Canon-v1-1.md:3615 | `$10M` | PROJECTION | / Strategic / $10M+ / Executive decision intelligence + IP licensing / vs. Competitive disadvantage / |
| _CANON/ARCS-Canon-v1-1.md:3620 | `$412M` | PROJECTION | - $412M ARR |
| _CANON/ARCS-Canon-v1-1.md:3621 | `98%` | PROJECTION | - Gross retention: 98% (near-zero voluntary churn) |
| _CANON/ARCS-Canon-v1-1.md:3622 | `140%` | PROJECTION | - Net retention: 140% (expansion despite high base) |
| _CANON/ARCS-Canon-v1-1.md:3623 | `$2.35M` | PROJECTION | - Average contract value: $2.35M |
| _CANON/ARCS-Canon-v1-1.md:3624 | `0.23%` | PROJECTION | - Market share: 0.23% (but growing 120% YoY) |
| _CANON/ARCS-Canon-v1-1.md:3624 | `120%` | PROJECTION | - Market share: 0.23% (but growing 120% YoY) |
| _CANON/ARCS-Canon-v1-1.md:3632 | `$4M` | PROJECTION | - 2 Enterprise AEs (quota: $4M ARR each) |
| _CANON/ARCS-Canon-v1-1.md:3639 | `$6M` | PROJECTION | - 8 Enterprise AEs ($6M quota each) |
| _CANON/ARCS-Canon-v1-1.md:3648 | `$8M` | PROJECTION | - 25 Enterprise AEs ($8M quota each) |
| _CANON/ARCS-Canon-v1-1.md:3659 | `60%` | PROJECTION | **Inbound (60% of pipeline)**: |
| _CANON/ARCS-Canon-v1-1.md:3666 | `40%` | PROJECTION | **Outbound (40% of pipeline)**: |
| _CANON/ARCS-Canon-v1-1.md:3697 | `17%` | UNVALIDATED | - **Strategy**: "Network effects. Our predictions are 17% better because we have more data." |
| _CANON/ARCS-Canon-v1-1.md:3701 | `$1M` | UNVALIDATED | - **Our Advantage**: Scalable software vs. expensive consultants ($1M/year vs. $5M/engagement) |
| _CANON/ARCS-Canon-v1-1.md:3701 | `$5M` | UNVALIDATED | - **Our Advantage**: Scalable software vs. expensive consultants ($1M/year vs. $5M/engagement) |
| _CANON/ARCS-Canon-v1-1.md:3715 | `$5` | PROJECTION | - **Defensive Value**: $5-8M (forces competitors to license or build inferior alternative) |
| _CANON/ARCS-Canon-v1-1.md:3720 | `$12` | PROJECTION | - **Defensive Value**: $12-20M (extremely difficult to design around) |
| _CANON/ARCS-Canon-v1-1.md:3725 | `$3` | PROJECTION | - **Defensive Value**: $3-5M (foundational but many alternatives exist) |
| _CANON/ARCS-Canon-v1-1.md:3730 | `$4` | PROJECTION | - **Defensive Value**: $4-7M (increasingly important with privacy regulations) |
| _CANON/ARCS-Canon-v1-1.md:3735 | `$2` | PROJECTION | - **Defensive Value**: $2-4M (novel but narrow application) |
| _CANON/ARCS-Canon-v1-1.md:3737 | `$26` | PROJECTION | **Total Portfolio Value**: $26-44M (conservative estimates) |
| _CANON/ARCS-Canon-v1-1.md:3746 | `5%` | PROJECTION | - Revenue share model: 5% of gross revenue using patented technology |
| _CANON/ARCS-Canon-v1-1.md:3770 | `1000+` | PROJECTION | - Domain-specific knowledge from 1000+ detected opportunities |
| _CANON/ARCS-Canon-v1-1.md:3790 | `72%` | UNVALIDATED | - Baseline prediction accuracy: 72% |
| _CANON/ARCS-Canon-v1-1.md:3794 | `82%` | UNVALIDATED | - Accuracy: 82% |
| _CANON/ARCS-Canon-v1-1.md:3795 | `10%` | PROJECTION | - Advantage: 10% better than new entrant (significant) |
| _CANON/ARCS-Canon-v1-1.md:3798 | `87%` | UNVALIDATED | - Accuracy: 87% |
| _CANON/ARCS-Canon-v1-1.md:3799 | `15%` | UNVALIDATED | - Advantage: 15% better than Year 1 competitor (customer-visible) |
| _CANON/ARCS-Canon-v1-1.md:3802 | `92%` | UNVALIDATED | - Accuracy: 92% |
| _CANON/ARCS-Canon-v1-1.md:3803 | `20%` | UNVALIDATED | - Advantage: 20% better than Year 3 competitor (insurmountable) |
| _CANON/ARCS-Canon-v1-1.md:3810 | `2+` | UNVALIDATED | 3. **Cold Start Problem**: New entrant starts at 68% accuracy, must convince customers to tolerate inferior predictions for 2+ years |
| _CANON/ARCS-Canon-v1-1.md:3810 | `68%` | UNVALIDATED | 3. **Cold Start Problem**: New entrant starts at 68% accuracy, must convince customers to tolerate inferior predictions for 2+ years |
| _CANON/ARCS-Canon-v1-1.md:3818 | `2029+` | PROJECTION | 2029+: Maintain lead (continuous data accumulation faster than competition) |
| _CANON/ARCS-Canon-v1-1.md:3845 | `2029+` | PROJECTION | **2029+: Market Requirement** |
| _CANON/ARCS-Canon-v1-1.md:3871 | `80%` | PROJECTION | - Search volume: "decision receipts" = 50K/month (80% ARCS-branded content) |
| _CANON/ARCS-Canon-v1-1.md:3875 | `2028+` | PROJECTION | 2028+: Generic trademark risk |
| _CANON/ARCS-Canon-v1-1.md:3881 | `$50` | PROJECTION | **Brand Value**: $50-100M (category ownership drives customer acquisition cost to near-zero) |
| _CANON/ARCS-Canon-v1-1.md:4027 | `80%` | PROJECTION | **Stream 1: Enterprise Software Licensing** (80% of revenue) |
| _CANON/ARCS-Canon-v1-1.md:4030 | `$412M` | PROJECTION | - Target: $412M ARR by Year 3 |
| _CANON/ARCS-Canon-v1-1.md:4032 | `10%` | PROJECTION | **Stream 2: Ecosystem Service Licensing** (10% of revenue) |
| _CANON/ARCS-Canon-v1-1.md:4035 | `$40M` | PROJECTION | - Target: $40M ARR by Year 3 |
| _CANON/ARCS-Canon-v1-1.md:4037 | `5%` | PROJECTION | **Stream 3: Research Partnerships** (5% of revenue) |
| _CANON/ARCS-Canon-v1-1.md:4041 | `$20M` | PROJECTION | - Target: $20M ARR by Year 3 |
| _CANON/ARCS-Canon-v1-1.md:4043 | `5%` | PROJECTION | **Stream 4: Token Ecosystem** (5% of revenue) |
| _CANON/ARCS-Canon-v1-1.md:4045 | `10%` | PROJECTION | - Foundation takes 10% transaction fee |
| _CANON/ARCS-Canon-v1-1.md:4046 | `$20M` | PROJECTION | - Target: $20M ARR by Year 3 |
| _CANON/ARCS-Canon-v1-1.md:4053 | `$164M` | PROJECTION | Engineering (40%): $164M |
| _CANON/ARCS-Canon-v1-1.md:4053 | `40%` | PROJECTION | Engineering (40%): $164M |
| _CANON/ARCS-Canon-v1-1.md:4054 | `$200K` | PROJECTION | - 450 engineers ($200K avg loaded cost) |
| _CANON/ARCS-Canon-v1-1.md:4058 | `$103M` | PROJECTION | Sales & Marketing (25%): $103M |
| _CANON/ARCS-Canon-v1-1.md:4058 | `25%` | PROJECTION | Sales & Marketing (25%): $103M |
| _CANON/ARCS-Canon-v1-1.md:4059 | `$450K` | PROJECTION | - 95 sales team members ($450K avg loaded cost including quotas) |
| _CANON/ARCS-Canon-v1-1.md:4062 | `$41M` | PROJECTION | Customer Success (10%): $41M |
| _CANON/ARCS-Canon-v1-1.md:4062 | `10%` | PROJECTION | Customer Success (10%): $41M |
| _CANON/ARCS-Canon-v1-1.md:4066 | `$41M` | PROJECTION | G&A (10%): $41M |
| _CANON/ARCS-Canon-v1-1.md:4066 | `10%` | PROJECTION | G&A (10%): $41M |
| _CANON/ARCS-Canon-v1-1.md:4070 | `$21M` | PROJECTION | Foundation Operations (5%): $21M |
| _CANON/ARCS-Canon-v1-1.md:4070 | `5%` | PROJECTION | Foundation Operations (5%): $21M |
| _CANON/ARCS-Canon-v1-1.md:4075 | `$10M` | PROJECTION | R&D (Tax Credit): -$10M |
| _CANON/ARCS-Canon-v1-1.md:4076 | `6%` | PROJECTION | - R&D tax credits (~6% of engineering spend) |
| _CANON/ARCS-Canon-v1-1.md:4078 | `$360M` | PROJECTION | Total: $360M |
| _CANON/ARCS-Canon-v1-1.md:4079 | `$52M` | PROJECTION | EBITDA: $52M (13% margin) |
| _CANON/ARCS-Canon-v1-1.md:4079 | `13%` | PROJECTION | EBITDA: $52M (13% margin) |
| _CANON/ARCS-Canon-v1-1.md:4085 | `$6.2M` | PROJECTION | Year 1: -$6.2M EBITDA (-41% margin) - investment phase |
| _CANON/ARCS-Canon-v1-1.md:4085 | `41%` | PROJECTION | Year 1: -$6.2M EBITDA (-41% margin) - investment phase |
| _CANON/ARCS-Canon-v1-1.md:4086 | `$28M` | PROJECTION | Year 2: +$28M EBITDA (+28% margin) - scale efficiency |
| _CANON/ARCS-Canon-v1-1.md:4086 | `28%` | PROJECTION | Year 2: +$28M EBITDA (+28% margin) - scale efficiency |
| _CANON/ARCS-Canon-v1-1.md:4087 | `$180M` | PROJECTION | Year 3: +$180M EBITDA (+44% margin) - platform maturity |
| _CANON/ARCS-Canon-v1-1.md:4087 | `44%` | PROJECTION | Year 3: +$180M EBITDA (+44% margin) - platform maturity |
| _CANON/ARCS-Canon-v1-1.md:4088 | `$800M` | PROJECTION | Year 5: +$800M EBITDA (+55% margin) - infrastructure lock-in |
| _CANON/ARCS-Canon-v1-1.md:4088 | `55%` | PROJECTION | Year 5: +$800M EBITDA (+55% margin) - infrastructure lock-in |
| _CANON/ARCS-Canon-v1-1.md:4096 | `40%` | PROJECTION | (40%) Reinvestment in product |
| _CANON/ARCS-Canon-v1-1.md:4099 | `30%` | PROJECTION | (30%) Foundation endowment |
| _CANON/ARCS-Canon-v1-1.md:4102 | `20%` | PROJECTION | (20%) Employee profit sharing |
| _CANON/ARCS-Canon-v1-1.md:4105 | `10%` | PROJECTION | (10%) Shareholder distributions |
| _CANON/ARCS-Canon-v1-1.md:4121 | `15%` | PROJECTION | Founder voting control: 55% (even with <15% economic ownership) |
| _CANON/ARCS-Canon-v1-1.md:4121 | `55%` | PROJECTION | Founder voting control: 55% (even with <15% economic ownership) |
| _CANON/ARCS-Canon-v1-1.md:4144 | `$100B` | PARAMETER | (b) Has market capitalization >$100B |
| _CANON/ARCS-Canon-v1-1.md:4161 | `$412M` | PROJECTION | - $412M ARR (Year 3) growing 120% YoY → $900M ARR (Year 4) |
| _CANON/ARCS-Canon-v1-1.md:4161 | `$900M` | PROJECTION | - $412M ARR (Year 3) growing 120% YoY → $900M ARR (Year 4) |
| _CANON/ARCS-Canon-v1-1.md:4161 | `120%` | PROJECTION | - $412M ARR (Year 3) growing 120% YoY → $900M ARR (Year 4) |
| _CANON/ARCS-Canon-v1-1.md:4163 | `$9` | PROJECTION | - Valuation: $9-13.5B |
| _CANON/ARCS-Canon-v1-1.md:4166 | `100%` | PROJECTION | - Pre-IPO ownership: 55% (diluted from 100% via pre-sale, debt, token) |
| _CANON/ARCS-Canon-v1-1.md:4166 | `55%` | PROJECTION | - Pre-IPO ownership: 55% (diluted from 100% via pre-sale, debt, token) |
| _CANON/ARCS-Canon-v1-1.md:4167 | `$5` | PROJECTION | - Post-IPO value: $5-7.4B |
| _CANON/ARCS-Canon-v1-1.md:4168 | `10%` | PROJECTION | - Lockup: Standard 180 days, then 10% per year sale limit |
| _CANON/ARCS-Canon-v1-1.md:4229 | `$2M` | PROJECTION | - $2M/year unrestricted research grant |
| _CANON/ARCS-Canon-v1-1.md:4242 | `$500K` | PROJECTION | - $500K/year focused research grants |
| _CANON/ARCS-Canon-v1-1.md:4272 | `95%` | PROJECTION | - Tertiary: Calibration (do 95% CIs actually contain 95% of outcomes?) |
| _CANON/ARCS-Canon-v1-1.md:4272 | `95%` | PROJECTION | - Tertiary: Calibration (do 95% CIs actually contain 95% of outcomes?) |
| _CANON/ARCS-Canon-v1-1.md:4275 | `68%` | PROJECTION | H1: ARCS accuracy > 85% (vs. H0: ≤68% baseline) |
| _CANON/ARCS-Canon-v1-1.md:4275 | `85%` | PROJECTION | H1: ARCS accuracy > 85% (vs. H0: ≤68% baseline) |
| _CANON/ARCS-Canon-v1-1.md:4276 | `15%` | PROJECTION | H2: ARCS MAPE < 15% (vs. H0: ≥22% baseline) |
| _CANON/ARCS-Canon-v1-1.md:4276 | `22%` | PROJECTION | H2: ARCS MAPE < 15% (vs. H0: ≥22% baseline) |
| _CANON/ARCS-Canon-v1-1.md:4277 | `p<0.05` | PROJECTION | H3: ARCS predictions well-calibrated (χ² test, p<0.05) |
| _CANON/ARCS-Canon-v1-1.md:4303 | `32%` | PROJECTION | H1: ARCS energy sustainability prediction >78% (vs. H0: ≤32% skills-based) |
| _CANON/ARCS-Canon-v1-1.md:4303 | `78%` | PROJECTION | H1: ARCS energy sustainability prediction >78% (vs. H0: ≤32% skills-based) |
| _CANON/ARCS-Canon-v1-1.md:4333 | `$400K` | PROJECTION | H2: Average window value $400K-800K incremental return |
| _CANON/ARCS-Canon-v1-1.md:4334 | `85%` | PROJECTION | H3: Competitors miss 85%+ of windows (discovered post-close) |
| _CANON/ARCS-Canon-v1-1.md:4363 | `24%` | PROJECTION | H2: Logarithmic improvement: Acc(N) ≈ 92% - 24% × exp(-0.000012 × N) |
| _CANON/ARCS-Canon-v1-1.md:4363 | `92%` | PROJECTION | H2: Logarithmic improvement: Acc(N) ≈ 92% - 24% × exp(-0.000012 × N) |
| _CANON/ARCS-Canon-v1-1.md:4377 | `$30K` | PROJECTION | Award: $50K/year stipend + $30K research budget + tuition |
| _CANON/ARCS-Canon-v1-1.md:4377 | `$50K` | PROJECTION | Award: $50K/year stipend + $30K research budget + tuition |
| _CANON/ARCS-Canon-v1-1.md:4412 | `$1.5` | UNVALIDATED | - **Award Size**: $1.5-3M over 3-4 years |
| _CANON/ARCS-Canon-v1-1.md:4412 | `over 3` | UNVALIDATED | - **Award Size**: $1.5-3M over 3-4 years |
| _CANON/ARCS-Canon-v1-1.md:4419 | `$500K` | UNVALIDATED | - **Award Size**: $500K-1.5M over 2-3 years |
| _CANON/ARCS-Canon-v1-1.md:4419 | `over 2` | UNVALIDATED | - **Award Size**: $500K-1.5M over 2-3 years |
| _CANON/ARCS-Canon-v1-1.md:4428 | `$2` | UNVALIDATED | - **Award Size**: $2-4M over 4-5 years |
| _CANON/ARCS-Canon-v1-1.md:4428 | `over 4` | UNVALIDATED | - **Award Size**: $2-4M over 4-5 years |
| _CANON/ARCS-Canon-v1-1.md:4437 | `over 3` | UNVALIDATED | - **Award Size**: €3-8M over 3-4 years |
| _CANON/ARCS-Canon-v1-1.md:4453 | `over 18` | UNVALIDATED | - **Award Size**: £500K-2M over 18-36 months |
| _CANON/ARCS-Canon-v1-1.md:4462 | `$2.5M` | UNVALIDATED | - **Award Size**: CAD $2.5M over 4-7 years |
| _CANON/ARCS-Canon-v1-1.md:4462 | `over 4` | UNVALIDATED | - **Award Size**: CAD $2.5M over 4-7 years |
| _CANON/ARCS-Canon-v1-1.md:4468 | `$20` | PROJECTION | **Total Projected Grant Funding (2026-2030)**: $20-35M |
| _CANON/ARCS-Canon-v1-1.md:4475 | `$300K` | UNVALIDATED | - **Award Size**: $300K-1M over 2-3 years |
| _CANON/ARCS-Canon-v1-1.md:4475 | `over 2` | UNVALIDATED | - **Award Size**: $300K-1M over 2-3 years |
| _CANON/ARCS-Canon-v1-1.md:4482 | `$500K` | UNVALIDATED | - **Award Size**: $500K-2M over 3 years |
| _CANON/ARCS-Canon-v1-1.md:4482 | `over 3` | UNVALIDATED | - **Award Size**: $500K-2M over 3 years |
| _CANON/ARCS-Canon-v1-1.md:4489 | `$1` | UNVALIDATED | - **Award Size**: $1-3M over 2-4 years |
| _CANON/ARCS-Canon-v1-1.md:4489 | `over 2` | UNVALIDATED | - **Award Size**: $1-3M over 2-4 years |
| _CANON/ARCS-Canon-v1-1.md:4496 | `$3` | UNVALIDATED | - **Award Size**: $3-5M over 3-5 years |
| _CANON/ARCS-Canon-v1-1.md:4496 | `over 3` | UNVALIDATED | - **Award Size**: $3-5M over 3-5 years |
| _CANON/ARCS-Canon-v1-1.md:4500 | `$10` | PROJECTION | **Total Projected Private Foundation Funding (2026-2030)**: $10-18M |
| _CANON/ARCS-Canon-v1-1.md:4507 | `$2M` | UNVALIDATED | **Structure**: Joint research lab, $2M/year, 3-year commitment |
| _CANON/ARCS-Canon-v1-1.md:4513 | `$1.5M` | UNVALIDATED | **Structure**: Dataset sharing, model co-development, $1.5M/year |
| _CANON/ARCS-Canon-v1-1.md:4522 | `$15` | PROJECTION | **Total Corporate Research Funding (2026-2030)**: $15-25M |
| _CANON/ARCS-Canon-v1-1.md:4744 | `30+` | PROJECTION | 2026: Proven ROI, expanding adoption (30+ customers) |
| _CANON/ARCS-Canon-v1-1.md:4758 | `$100M` | UNVALIDATED | 3. **Fiduciary Duty Evolution**: What boards tolerated in 2020 (undocumented $100M allocations) will be liability in 2030 |
| _CANON/ARCS-Canon-v1-1.md:4777 | `$50K` | UNVALIDATED | Current: $50K/week for advice with no accountability |
| _CANON/ARCS-Canon-v1-1.md:4781 | `30%` | UNVALIDATED | Current: 30% first-year salary for placement (often bad fit) |
| _CANON/ARCS-Canon-v1-1.md:4819 | `$127M` | ILLUSTRATIVE | - Job market sees: 847 decisions, 72% accuracy, $127M value created |
| _CANON/ARCS-Canon-v1-1.md:4819 | `72%` | ILLUSTRATIVE | - Job market sees: 847 decisions, 72% accuracy, $127M value created |
| _CANON/ARCS-Canon-v1-1.md:4836 | `78%` | ILLUSTRATIVE | - Real-time updates ("847 companies tried X this week, 78% failed, here's why") |
| _CANON/ARCS-Canon-v2-0-Complete.md:161 | `90%` | ILLUSTRATIVE | - **High Coherence:** Rowers synchronize strokes, boat cuts straight through water, 90% of energy → forward motion (low entropy, high alignm |
| _CANON/ARCS-Canon-v2-0-Complete.md:272 | `p < 0.0001` | UNVALIDATED | **Statistical Significance:** Paired t-test: \(t = 14.2\), \(p < 0.0001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:333 | `78%` | UNVALIDATED | **Claim:** SecondDerivative detects trend reversals 24-48 hours before they occur, with 78% accuracy. |
| _CANON/ARCS-Canon-v2-0-Complete.md:424 | `15%` | UNVALIDATED | **Claim:** WaveDiffusion predicts saturation point within 15% accuracy, 82% of the time. |
| _CANON/ARCS-Canon-v2-0-Complete.md:424 | `82%` | UNVALIDATED | **Claim:** WaveDiffusion predicts saturation point within 15% accuracy, 82% of the time. |
| _CANON/ARCS-Canon-v2-0-Complete.md:428 | `90%` | PARAMETER | For viral content, define **saturation** as: \(S(t_{sat}) = 0.9 \times S_{max}\) (reached 90% of maximum engagement). |
| _CANON/ARCS-Canon-v2-0-Complete.md:446 | `15%` | UNVALIDATED | - **Within 15% error:** 1,022 threads (82%) |
| _CANON/ARCS-Canon-v2-0-Complete.md:446 | `82%` | UNVALIDATED | - **Within 15% error:** 1,022 threads (82%) |
| _CANON/ARCS-Canon-v2-0-Complete.md:447 | `11%` | UNVALIDATED | - **Median error:** 11% |
| _CANON/ARCS-Canon-v2-0-Complete.md:448 | `p < 0.0001` | UNVALIDATED | - **Correlation:** \(r = 0.87\), \(p < 0.0001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:448 | `r = 0.87` | UNVALIDATED | - **Correlation:** \(r = 0.87\), \(p < 0.0001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:494 | `1+` | PARAMETER | Interference is **energy superposition**. Constructive interference = energy adds (1+1=2). Destructive interference = energy cancels (1+1=0) |
| _CANON/ARCS-Canon-v2-0-Complete.md:494 | `1+` | PARAMETER | Interference is **energy superposition**. Constructive interference = energy adds (1+1=2). Destructive interference = energy cancels (1+1=0) |
| _CANON/ARCS-Canon-v2-0-Complete.md:513 | `35%` | UNVALIDATED | **Claim:** Spacing campaigns by \(T/4\) improves ROAS by 35% compared to uncoordinated launch. |
| _CANON/ARCS-Canon-v2-0-Complete.md:534 | `34%` | UNVALIDATED | / Baseline / 2.17 / 0.42 / 34% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:535 | `8%` | UNVALIDATED | / Optimized / 2.93 / 0.51 / 8% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:540 | `p < 0.001` | UNVALIDATED | - Independent samples t-test: \(t = 7.23\), \(p < 0.001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:541 | `28%` | UNVALIDATED | - 95% CI for improvement: [28%, 42%] |
| _CANON/ARCS-Canon-v2-0-Complete.md:541 | `42%` | UNVALIDATED | - 95% CI for improvement: [28%, 42%] |
| _CANON/ARCS-Canon-v2-0-Complete.md:541 | `95%` | UNVALIDATED | - 95% CI for improvement: [28%, 42%] |
| _CANON/ARCS-Canon-v2-0-Complete.md:609 | `45%` | UNVALIDATED | **Claim:** Detecting deceleration and reallocating budget reduces wasted spend by 45%. |
| _CANON/ARCS-Canon-v2-0-Complete.md:614 | `10%` | PARAMETER | - **Baseline:** Continue spending on all content until engagement drops below 10% of peak |
| _CANON/ARCS-Canon-v2-0-Complete.md:615 | `30%` | PARAMETER | - **Decelerator:** Cut spending when \(D_{severity} > 0.3\) (30% deceleration rate) |
| _CANON/ARCS-Canon-v2-0-Complete.md:622 | `$127K` | UNVALIDATED | - **Wasted spend:** $127K (spent on declining content) |
| _CANON/ARCS-Canon-v2-0-Complete.md:623 | `$890K` | UNVALIDATED | - **Total spend:** $890K |
| _CANON/ARCS-Canon-v2-0-Complete.md:624 | `14.3%` | UNVALIDATED | - **Waste ratio:** 14.3% |
| _CANON/ARCS-Canon-v2-0-Complete.md:627 | `$69K` | UNVALIDATED | - **Wasted spend:** $69K |
| _CANON/ARCS-Canon-v2-0-Complete.md:628 | `$890K` | UNVALIDATED | - **Total spend:** $890K (same budget, reallocated earlier) |
| _CANON/ARCS-Canon-v2-0-Complete.md:629 | `7.8%` | UNVALIDATED | - **Waste ratio:** 7.8% |
| _CANON/ARCS-Canon-v2-0-Complete.md:635 | `10%` | PARAMETER | Most campaigns follow power-law decay: \(S(t) \propto t^{-\alpha}\). By the time engagement drops to 10% of peak, you've already wasted 80%  |
| _CANON/ARCS-Canon-v2-0-Complete.md:635 | `80%` | PARAMETER | Most campaigns follow power-law decay: \(S(t) \propto t^{-\alpha}\). By the time engagement drops to 10% of peak, you've already wasted 80%  |
| _CANON/ARCS-Canon-v2-0-Complete.md:711 | `3%` | PARAMETER | - **Momentum Strategy:** Buy when 1-hour return > 3%, sell when < -3% |
| _CANON/ARCS-Canon-v2-0-Complete.md:711 | `3%` | PARAMETER | - **Momentum Strategy:** Buy when 1-hour return > 3%, sell when < -3% |
| _CANON/ARCS-Canon-v2-0-Complete.md:718 | `83%` | UNVALIDATED | / Sharpe Ratio / 0.73 / 1.34 / 83% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:719 | `15.2%` | UNVALIDATED | / Total Return / 15.2% / 25.8% / 70% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:719 | `25.8%` | UNVALIDATED | / Total Return / 15.2% / 25.8% / 70% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:719 | `70%` | UNVALIDATED | / Total Return / 15.2% / 25.8% / 70% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:720 | `11.8%` | UNVALIDATED | / Max Drawdown / -11.8% / -5.1% / 57% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:720 | `5.1%` | UNVALIDATED | / Max Drawdown / -11.8% / -5.1% / 57% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:720 | `57%` | UNVALIDATED | / Max Drawdown / -11.8% / -5.1% / 57% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:721 | `19%` | UNVALIDATED | / Win Rate / 54% / 64% / 19% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:721 | `54%` | UNVALIDATED | / Win Rate / 54% / 64% / 19% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:721 | `64%` | UNVALIDATED | / Win Rate / 54% / 64% / 19% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:724 | `p < 0.001` | UNVALIDATED | - Bootstrap test (10,000 iterations): \(p < 0.001\) |
| _CANON/ARCS-Canon-v2-0-Complete.md:725 | `95%` | UNVALIDATED | - 95% CI for Sharpe difference: [0.46, 0.76] |
| _CANON/ARCS-Canon-v2-0-Complete.md:789 | `28%` | UNVALIDATED | **Claim:** ContentOrchestration improves cost-per-acquisition by 28% and reach by 42%. |
| _CANON/ARCS-Canon-v2-0-Complete.md:789 | `42%` | UNVALIDATED | **Claim:** ContentOrchestration improves cost-per-acquisition by 28% and reach by 42%. |
| _CANON/ARCS-Canon-v2-0-Complete.md:803 | `35%` | UNVALIDATED | / ROAS / 2.17 / 2.93 / 35% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:804 | `$30` | UNVALIDATED | / Cost per Acquisition / $42 / $30 / 28% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:804 | `$42` | UNVALIDATED | / Cost per Acquisition / $42 / $30 / 28% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:804 | `28%` | UNVALIDATED | / Cost per Acquisition / $42 / $30 / 28% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:805 | `42%` | UNVALIDATED | / Total Reach / 487K / 691K / 42% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:806 | `12%` | UNVALIDATED | / Audience Fatigue (complaints) / 12% / 4% / 67% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:806 | `4%` | UNVALIDATED | / Audience Fatigue (complaints) / 12% / 4% / 67% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:806 | `67%` | UNVALIDATED | / Audience Fatigue (complaints) / 12% / 4% / 67% reduction / |
| _CANON/ARCS-Canon-v2-0-Complete.md:874 | `$67K` | ILLUSTRATIVE | "action": "Enter long position BTC $67K", |
| _CANON/ARCS-Canon-v2-0-Complete.md:938 | `90%` | UNVALIDATED | 2. **Base rate:** "90% of new products fail in Year 1. Why is X different?" |
| _CANON/ARCS-Canon-v2-0-Complete.md:940 | `90%` | UNVALIDATED | 4. **Bayesian:** "We have 2 weeks of data. Is that enough to overcome 90% base failure rate?" |
| _CANON/ARCS-Canon-v2-0-Complete.md:1045 | `$10K` | ILLUSTRATIVE | **Decision (T=0):** "Invest $10K in marketing campaign X. Expected ROI: 2.5x." |
| _CANON/ARCS-Canon-v2-0-Complete.md:1047 | `$18K` | ILLUSTRATIVE | **Outcome (T=3 months):** Actual revenue = $18K. Actual ROI = 1.8x. |
| _CANON/ARCS-Canon-v2-0-Complete.md:1050 | `28%` | ILLUSTRATIVE | - Prediction error: \(/2.5 - 1.8/ = 0.7\) (28% overestimate) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1052 | `15%` | ILLUSTRATIVE | - Update: Reduce FirstDerivative weight by 15% for future campaigns |
| _CANON/ARCS-Canon-v2-0-Complete.md:1108 | `72%` | ILLUSTRATIVE | - Leaf A1: "Early entry, high volatility" (68 decisions, 72% success) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1109 | `52%` | ILLUSTRATIVE | - Leaf A2: "Late entry, low volatility" (34 decisions, 52% success) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1112 | `83%` | ILLUSTRATIVE | - Leaf B1: "High harmony, quick decision" (12 decisions, 83% satisfaction) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1113 | `25%` | ILLUSTRATIVE | - Leaf B2: "Low harmony, delayed decision" (8 decisions, 25% satisfaction) |
| _CANON/ARCS-Canon-v2-0-Complete.md:1160 | `78%` | ILLUSTRATIVE | 5. Recommend: "Similar decisions had 78% success rate. Key factor: X." |
| _CANON/ARCS-Canon-v2-0-Complete.md:1172 | `67%` | ILLUSTRATIVE | - Average offer rate: 67% |
| _CANON/ARCS-Canon-v2-0-Complete.md:1198 | `80%` | UNVALIDATED | Humans are **biological coherence detectors** that complement computational ARCS. When calibrated, intuitive signals achieve 70-80% accuracy |
| _CANON/ARCS-Canon-v2-0-Complete.md:1208 | `72%` | UNVALIDATED | / **Phase Tuning** / Vagus nerve activation / Phase Coherence Index \(PCI > 0.4\) / 8-12 hours / 72% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1209 | `68%` | UNVALIDATED | / **Surge Detection** / Vestibular system (jerk) / Third Derivative \(d^3S/dt^3 > 0\) / 30-90 min / 68% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1210 | `76%` | UNVALIDATED | / **Feels Right** / Whole-body alignment / \(\langle\Psi_{identity}\/\Psi_{option}\rangle > 0.85\) / Instantaneous / 76% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1211 | `72%` | UNVALIDATED | / **That Vibes** / Heart rate coherence / Phase-locked oscillators \(\/\theta_1 - \theta_2\/ < 0.2\) / Real-time / 72% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1212 | `84%` | UNVALIDATED | / **Locked In** / Flow state (high Φ) / Action-gradient alignment \(\cos(\theta) > 0.95\) / Sustained (2-6h) / 84% / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1213 | `80%` | UNVALIDATED | / **Expected vs. Actual** / Prediction error learning / Bayesian updating \(P(\theta\/D)\) / 3-6 months / 80%+ / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1278 | `95%` | UNVALIDATED | / Study / Claim / Confidence / 95% CI / Key Limitation / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1280 | `75%` | UNVALIDATED | / **1. Trading** / Sharpe 1.52 vs. 0.73 / 75% / [1.38, 1.68] / Bull market only, 14-day backtest / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1281 | `85%` | UNVALIDATED | / **2. Twitter** / 11.6h earlier / 85% / [9.2h, 14.3h] / Platform algorithm changes / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1282 | `28%` | UNVALIDATED | / **3. Marketing** / 35% ROAS gain / 70% / [28%, 42%] / Small sample (n=83), industry-specific / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1282 | `35%` | UNVALIDATED | / **3. Marketing** / 35% ROAS gain / 70% / [28%, 42%] / Small sample (n=83), industry-specific / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1282 | `42%` | UNVALIDATED | / **3. Marketing** / 35% ROAS gain / 70% / [28%, 42%] / Small sample (n=83), industry-specific / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1282 | `70%` | UNVALIDATED | / **3. Marketing** / 35% ROAS gain / 70% / [28%, 42%] / Small sample (n=83), industry-specific / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1283 | `19%` | UNVALIDATED | / **4. Career** / 50% offer rate (H>80) / 60% / [19%, 81%] / N=1 study, low power / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1283 | `50%` | UNVALIDATED | / **4. Career** / 50% offer rate (H>80) / 60% / [19%, 81%] / N=1 study, low power / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1283 | `60%` | UNVALIDATED | / **4. Career** / 50% offer rate (H>80) / 60% / [19%, 81%] / N=1 study, low power / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1283 | `81%` | UNVALIDATED | / **4. Career** / 50% offer rate (H>80) / 60% / [19%, 81%] / N=1 study, low power / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1284 | `72%` | UNVALIDATED | / **5. Noise** / 76% accuracy (NSR=1.0) / 90% / [72%, 80%] / Synthetic data only / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1284 | `76%` | UNVALIDATED | / **5. Noise** / 76% accuracy (NSR=1.0) / 90% / [72%, 80%] / Synthetic data only / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1284 | `80%` | UNVALIDATED | / **5. Noise** / 76% accuracy (NSR=1.0) / 90% / [72%, 80%] / Synthetic data only / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1284 | `90%` | UNVALIDATED | / **5. Noise** / 76% accuracy (NSR=1.0) / 90% / [72%, 80%] / Synthetic data only / |
| _CANON/ARCS-Canon-v2-0-Complete.md:1378 | `35%` | UNVALIDATED | 26. **Marketing: 35% ROAS improvement** |
| _CANON/ARCS-Canon-v2-0-Complete.md:1379 | `50%` | UNVALIDATED | 27. **Career: 50% offer rate (high harmony)** |
| _CANON/ARCS-Canon-v2-0-Complete.md:1380 | `76%` | UNVALIDATED | 28. **Noise: 76% accuracy (high NSR)** |
| _CANON/ARCS-Canon-v2-0-Complete.md:1435 | `100+` | UNVALIDATED | **Primary Citations:** 100+ sources |
| _CANON/ARCS-Litepaper.md:21 | `$350B` | UNVALIDATED | Enterprise marketing represents a $350B annual expenditure in the United States alone, yet it remains the least accountable major corporate  |
| _CANON/ARCS-Litepaper.md:25 | `$50M` | UNVALIDATED | 1. **No Decision Documentation**: Marketing leaders allocate $50M+ budgets without documented reasoning, alternatives considered, or risk as |
| _CANON/ARCS-Litepaper.md:53 | `40+` | PROJECTION | 2. **Phase 2**: Expand to Marketing OS (consolidate 40+ tools into unified platform) |
| _CANON/ARCS-Litepaper.md:122 | `87%` | ILLUSTRATIVE | **Key Innovation**: Unlike deductive systems that claim certainty, abductive systems provide **honest uncertainty quantification**. An ARCS  |
| _CANON/ARCS-Litepaper.md:134 | `000+` | PROJECTION | 1. **Receipts Database**: 100,000+ historical campaign decisions with outcomes |
| _CANON/ARCS-Litepaper.md:153 | `87%` | UNVALIDATED | - 87% of predictions fall within stated confidence intervals |
| _CANON/ARCS-Litepaper.md:154 | `15%` | UNVALIDATED | - Mean Absolute Percentage Error (MAPE): 12-15% |
| _CANON/ARCS-Litepaper.md:155 | `76%` | UNVALIDATED | - Outperforms human experts 76% of the time on blind tests |
| _CANON/ARCS-Litepaper.md:240 | `50+` | PARAMETER | 1. Monitor 50+ real-time data streams |
| _CANON/ARCS-Litepaper.md:241 | `3+` | PARAMETER | 2. Detect anomalies (3+ standard deviations from baseline) |
| _CANON/ARCS-Litepaper.md:242 | `3+` | PARAMETER | 3. Check for convergence (3+ positive signals aligning) |
| _CANON/ARCS-Litepaper.md:245 | `75%` | PARAMETER | 6. If EV > threshold + confidence > 75%: Alert team |
| _CANON/ARCS-Litepaper.md:258 | `18%` | ILLUSTRATIVE | Signal 1: Reddit CPMs drop 18% (traffic signal) |
| _CANON/ARCS-Litepaper.md:259 | `34%` | ILLUSTRATIVE | Signal 2: r/cryptocurrency engagement spike +34% (audience signal) |
| _CANON/ARCS-Litepaper.md:263 | `$200K` | ILLUSTRATIVE | Action: Increase Reddit budget by $200K immediately |
| _CANON/ARCS-Litepaper.md:264 | `$640K` | ILLUSTRATIVE | Expected value: $640K incremental return (3.2x on opportunity spend) |
| _CANON/ARCS-Litepaper.md:265 | `$780K` | ILLUSTRATIVE | Actual outcome: $780K return (3.9x, window captured before close) |
| _CANON/ARCS-Litepaper.md:318 | `68%` | UNVALIDATED | / 1,000 / 68% / 2.9x / |
| _CANON/ARCS-Litepaper.md:319 | `78%` | UNVALIDATED | / 10,000 / 78% / 3.4x / |
| _CANON/ARCS-Litepaper.md:320 | `87%` | UNVALIDATED | / 100,000 / 87% / 4.1x / |
| _CANON/ARCS-Litepaper.md:321 | `92%` | UNVALIDATED | / 1,000,000 (projected) / 92% (projected) / 4.8x (projected) / |
| _CANON/ARCS-Litepaper.md:333 | `40%` | PROJECTION | **Value Proposition**: 40% ROAS improvement with performance guarantee [Unvalidated target: asserted threshold, no control group; see Techni |
| _CANON/ARCS-Litepaper.md:348 | `$5M` | PROJECTION | **Value Proposition**: Vendor consolidation saves $5M+ annually |
| _CANON/ARCS-Litepaper.md:394 | `68%` | UNVALIDATED | - Our predictive accuracy (back to 68% from 87%)" |
| _CANON/ARCS-Litepaper.md:394 | `87%` | UNVALIDATED | - Our predictive accuracy (back to 68% from 87%)" |
| _CANON/ARCS-Litepaper.md:397 | `18%` | PROJECTION | - Phase 1 (Ad Server): 12-18% annually (normal SaaS) |
| _CANON/ARCS-Litepaper.md:398 | `8%` | PROJECTION | - Phase 2 (Marketing OS): 5-8% annually (high switching costs) |
| _CANON/ARCS-Litepaper.md:399 | `2%` | PROJECTION | - Phase 3 (Infrastructure): <2% annually (near-zero voluntary churn) |
| _CANON/ARCS-Litepaper.md:411 | `$7.5M` | PROJECTION | - **Tier 1 (Private Mode)**: $7.5M/year—agency hoards client data, gets 72% accuracy |
| _CANON/ARCS-Litepaper.md:411 | `72%` | UNVALIDATED | - **Tier 1 (Private Mode)**: $7.5M/year—agency hoards client data, gets 72% accuracy |
| _CANON/ARCS-Litepaper.md:412 | `$4.5M` | PROJECTION | - **Tier 2 (Partial Contribution)**: $4.5M/year—shares anonymized patterns, gets 82% accuracy |
| _CANON/ARCS-Litepaper.md:412 | `82%` | UNVALIDATED | - **Tier 2 (Partial Contribution)**: $4.5M/year—shares anonymized patterns, gets 82% accuracy |
| _CANON/ARCS-Litepaper.md:413 | `$2.5M` | PROJECTION | - **Tier 3 (Full Contribution)**: $2.5M/year—shares all receipts, gets 87% accuracy |
| _CANON/ARCS-Litepaper.md:413 | `87%` | UNVALIDATED | - **Tier 3 (Full Contribution)**: $2.5M/year—shares all receipts, gets 87% accuracy |
| _CANON/ARCS-Litepaper.md:419 | `15%` | UNVALIDATED | 2. Clients see 15% performance gap vs. Tier 3 |
| _CANON/ARCS-Litepaper.md:457 | `40%` | PROJECTION | **Implementation**: "40% ROAS improvement or full refund" |
| _CANON/ARCS-Litepaper.md:505 | `$70M` | PROJECTION | - Raise $70M in 3 rounds (Seed, A, B) |
| _CANON/ARCS-Litepaper.md:506 | `50%` | PROJECTION | - Give up 40-50% of company |
| _CANON/ARCS-Litepaper.md:519 | `$81M` | PROJECTION | 1. **Enterprise Pre-Sale**: $81M from 20 customers |
| _CANON/ARCS-Litepaper.md:520 | `40%` | PROJECTION | - Customers prepay 3-year contracts at 40% discount |
| _CANON/ARCS-Litepaper.md:521 | `25%` | PROJECTION | - 50% upfront, 25% at 12 months, 25% at 24 months |
| _CANON/ARCS-Litepaper.md:521 | `25%` | PROJECTION | - 50% upfront, 25% at 12 months, 25% at 24 months |
| _CANON/ARCS-Litepaper.md:521 | `50%` | PROJECTION | - 50% upfront, 25% at 12 months, 25% at 24 months |
| _CANON/ARCS-Litepaper.md:523 | `0%` | PROJECTION | - Dilution: 0% (this is revenue, not equity) |
| _CANON/ARCS-Litepaper.md:525 | `$12M` | PROJECTION | 2. **Token Generation Event**: $12M from ecosystem |
| _CANON/ARCS-Litepaper.md:527 | `$0.04` | PROJECTION | - 25% of 1B tokens sold at $0.04 (conservative $40M FDV) |
| _CANON/ARCS-Litepaper.md:527 | `$40M` | PROJECTION | - 25% of 1B tokens sold at $0.04 (conservative $40M FDV) |
| _CANON/ARCS-Litepaper.md:527 | `25%` | PROJECTION | - 25% of 1B tokens sold at $0.04 (conservative $40M FDV) |
| _CANON/ARCS-Litepaper.md:529 | `0%` | PROJECTION | - Dilution: 0% (tokens ≠ equity) |
| _CANON/ARCS-Litepaper.md:531 | `$4.3M` | PROJECTION | 3. **Revenue Reinvestment**: $4.3M from operations |
| _CANON/ARCS-Litepaper.md:532 | `$180K` | UNVALIDATED | - Currently profitable ($180K/month EBITDA) |
| _CANON/ARCS-Litepaper.md:534 | `0%` | PROJECTION | - Dilution: 0% (organic) |
| _CANON/ARCS-Litepaper.md:536 | `$5M` | PROJECTION | 4. **Strategic Debt**: $5M credit facility |
| _CANON/ARCS-Litepaper.md:538 | `2%` | PROJECTION | - Prime + 2% (~8.5% interest rate) |
| _CANON/ARCS-Litepaper.md:538 | `8.5%` | PROJECTION | - Prime + 2% (~8.5% interest rate) |
| _CANON/ARCS-Litepaper.md:539 | `0%` | PROJECTION | - Dilution: 0% (debt, not equity) |
| _CANON/ARCS-Litepaper.md:541 | `$102M` | PROJECTION | **Total Capital**: $102M with <5% dilution vs. $70M with 40-50% dilution |
| _CANON/ARCS-Litepaper.md:541 | `$70M` | PROJECTION | **Total Capital**: $102M with <5% dilution vs. $70M with 40-50% dilution |
| _CANON/ARCS-Litepaper.md:541 | `5%` | PROJECTION | **Total Capital**: $102M with <5% dilution vs. $70M with 40-50% dilution |
| _CANON/ARCS-Litepaper.md:541 | `50%` | PROJECTION | **Total Capital**: $102M with <5% dilution vs. $70M with 40-50% dilution |
| _CANON/ARCS-Litepaper.md:558 | `20%` | PROJECTION | - Public sale (25%): 20% unlocked at TGE, 80% vest over 18 months |
| _CANON/ARCS-Litepaper.md:558 | `25%` | PROJECTION | - Public sale (25%): 20% unlocked at TGE, 80% vest over 18 months |
| _CANON/ARCS-Litepaper.md:558 | `80%` | PROJECTION | - Public sale (25%): 20% unlocked at TGE, 80% vest over 18 months |
| _CANON/ARCS-Litepaper.md:558 | `over 18` | PROJECTION | - Public sale (25%): 20% unlocked at TGE, 80% vest over 18 months |
| _CANON/ARCS-Litepaper.md:559 | `20%` | PROJECTION | - Team (20%): 4-year vest, 1-year cliff |
| _CANON/ARCS-Litepaper.md:560 | `35%` | PROJECTION | - Ecosystem (35%): Released based on network activity over 5 years |
| _CANON/ARCS-Litepaper.md:560 | `over 5` | PROJECTION | - Ecosystem (35%): Released based on network activity over 5 years |
| _CANON/ARCS-Litepaper.md:561 | `15%` | PROJECTION | - Treasury (15%): Strategic reserves |
| _CANON/ARCS-Litepaper.md:562 | `5%` | PROJECTION | - Partners (5%): Early supporters |
| _CANON/ARCS-Litepaper.md:566 | `$2.1M` | UNVALIDATED | - Conservative pricing ($40M FDV for $2.1M ARR company = 19x, reasonable) |
| _CANON/ARCS-Litepaper.md:566 | `$40M` | PROJECTION | - Conservative pricing ($40M FDV for $2.1M ARR company = 19x, reasonable) |
| _CANON/ARCS-Litepaper.md:577 | `$850B` | UNVALIDATED | - Global: $850B annually |
| _CANON/ARCS-Litepaper.md:578 | `$350B` | UNVALIDATED | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Litepaper.md:578 | `500+` | PARAMETER | - US Enterprise (500+ employees): $350B annually |
| _CANON/ARCS-Litepaper.md:579 | `$180B` | UNVALIDATED | - Addressable (Fortune 5000 + growth cos): $180B annually |
| _CANON/ARCS-Litepaper.md:581 | `$180B` | UNVALIDATED | **Current Market Penetration**: 0.001% ($2.1M ARR / $180B TAM) |
| _CANON/ARCS-Litepaper.md:581 | `$2.1M` | UNVALIDATED | **Current Market Penetration**: 0.001% ($2.1M ARR / $180B TAM) |
| _CANON/ARCS-Litepaper.md:581 | `0.001%` | UNVALIDATED | **Current Market Penetration**: 0.001% ($2.1M ARR / $180B TAM) |
| _CANON/ARCS-Litepaper.md:585 | `60%` | PROJECTION | **Base Case (60% probability)**: |
| _CANON/ARCS-Litepaper.md:590 | `$15.2M` | PROJECTION | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Litepaper.md:590 | `$412M` | PROJECTION | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Litepaper.md:590 | `$98.4M` | PROJECTION | / ARR / $15.2M / $98.4M / $412M / |
| _CANON/ARCS-Litepaper.md:591 | `0.008%` | PROJECTION | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Litepaper.md:591 | `0.055%` | PROJECTION | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Litepaper.md:591 | `0.23%` | PROJECTION | / Market Share / 0.008% / 0.055% / 0.23% / |
| _CANON/ARCS-Litepaper.md:592 | `$180M` | PROJECTION | / EBITDA / -$6.2M / +$28M / +$180M / |
| _CANON/ARCS-Litepaper.md:592 | `$28M` | PROJECTION | / EBITDA / -$6.2M / +$28M / +$180M / |
| _CANON/ARCS-Litepaper.md:592 | `$6.2M` | PROJECTION | / EBITDA / -$6.2M / +$28M / +$180M / |
| _CANON/ARCS-Litepaper.md:593 | `28%` | PROJECTION | / EBITDA Margin / -41% / 28% / 44% / |
| _CANON/ARCS-Litepaper.md:593 | `41%` | PROJECTION | / EBITDA Margin / -41% / 28% / 44% / |
| _CANON/ARCS-Litepaper.md:593 | `44%` | PROJECTION | / EBITDA Margin / -41% / 28% / 44% / |
| _CANON/ARCS-Litepaper.md:594 | `$120M` | PROJECTION | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Litepaper.md:594 | `$3.3B` | PROJECTION | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Litepaper.md:594 | `$790M` | PROJECTION | / Valuation / $120M / $790M / $3.3B / |
| _CANON/ARCS-Litepaper.md:597 | `$4.2M` | PROJECTION | - Average contract value: $4.8M → $4.2M (Tier 3 adoption increases) |
| _CANON/ARCS-Litepaper.md:597 | `$4.8M` | PROJECTION | - Average contract value: $4.8M → $4.2M (Tier 3 adoption increases) |
| _CANON/ARCS-Litepaper.md:599 | `94%` | PROJECTION | - Gross margin: 94% maintained (SaaS economics) |
| _CANON/ARCS-Litepaper.md:600 | `8%` | PROJECTION | - Churn: 8% annual (enterprise standard) |
| _CANON/ARCS-Litepaper.md:604 | `0.23%` | PROJECTION | **0.23% market share = Category leader?** |
| _CANON/ARCS-Litepaper.md:607 | `2%` | UNVALIDATED | - No single vendor has >2% of enterprise marketing spend |
| _CANON/ARCS-Litepaper.md:612 | `000+` | PROJECTION | - At 175 customers: 100,000+ receipts in database |
| _CANON/ARCS-Litepaper.md:613 | `000+` | PROJECTION | - At 500 customers: 1,000,000+ receipts (92% accuracy, unbeatable) |
| _CANON/ARCS-Litepaper.md:613 | `92%` | UNVALIDATED | - At 500 customers: 1,000,000+ receipts (92% accuracy, unbeatable) |
| _CANON/ARCS-Litepaper.md:622 | `30%` | PROJECTION | **Probability**: Medium (30%) |
| _CANON/ARCS-Litepaper.md:633 | `25%` | PROJECTION | **Probability**: Low-Medium (25%) |
| _CANON/ARCS-Litepaper.md:644 | `60%` | PROJECTION | **Probability**: High (60% within 24 months) |
| _CANON/ARCS-Litepaper.md:656 | `40%` | PROJECTION | **Probability**: Medium (40%) |
| _CANON/ARCS-Litepaper.md:658 | `$12M` | PROJECTION | **Impact**: Medium (lose $12M funding source) |
| _CANON/ARCS-Litepaper.md:663 | `$81M` | PROJECTION | - Pre-sale alone ($81M) funds 18+ months |
| _CANON/ARCS-Litepaper.md:663 | `18+` | PROJECTION | - Pre-sale alone ($81M) funds 18+ months |
| _CANON/ARCS-Litepaper.md:668 | `25%` | PROJECTION | **Probability**: Low-Medium (25%) |
| _CANON/ARCS-Litepaper.md:674 | `20%` | PROJECTION | - Budget 20% engineering contingency |
| _CANON/ARCS-Litepaper.md:706 | `000+` | PROJECTION | - 100,000+ receipts create prediction advantages |
| _CANON/ARCS-Litepaper.md:719 | `500+` | PROJECTION | - By the time they ship, we have 500+ customers |
| _CANON/ARCS-Litepaper.md:732 | `$350B` | UNVALIDATED | - $350B allocated annually on intuition |
| _CANON/ARCS-Litepaper.md:735 | `87%` | UNVALIDATED | - Marketing becomes evidence-based (predict with 87% accuracy) |
| _CANON/ARCS-Litepaper.md:739 | `$350B` | UNVALIDATED | - $350B allocated annually on documented reasoning |
| _CANON/ARCS-Litepaper.md:747 | `$10B` | PROJECTION | 1. **Best Case**: We build it, capture 0.6% market share, create $10B+ category |
| _CANON/ARCS-Litepaper.md:747 | `0.6%` | PROJECTION | 1. **Best Case**: We build it, capture 0.6% market share, create $10B+ category |
| _CANON/ARCS-Litepaper.md:748 | `$2B` | PROJECTION | 2. **Acceptable**: We build it, competitor copies, we still capture 0.2% = $2B+ company |
| _CANON/ARCS-Litepaper.md:748 | `0.2%` | PROJECTION | 2. **Acceptable**: We build it, competitor copies, we still capture 0.2% = $2B+ company |
| _CANON/ARCS-Litepaper.md:756 | `$2.1M` | UNVALIDATED | - Product-market fit ($2.1M ARR, profitable) |
| _CANON/ARCS-Litepaper.md:758 | `$102M` | PROJECTION | - Capital strategy ($102M non-dilutive path) |
| _CANON/ARCS-Litepaper.md:759 | `$412M` | PROJECTION | - Clear roadmap (36 months to $412M ARR) |
| _CANON/ARCS-Litepaper.md:798 | `$1` | ILLUSTRATIVE | **ROAS (Return on Ad Spend)**: Revenue generated divided by advertising cost (e.g., 4:1 means $4 revenue per $1 spent) |
| _CANON/ARCS-Litepaper.md:798 | `$4` | ILLUSTRATIVE | **ROAS (Return on Ad Spend)**: Revenue generated divided by advertising cost (e.g., 4:1 means $4 revenue per $1 spent) |
| _CANON/ARCS-Litepaper.md:852 | `$7M` | ILLUSTRATIVE | "decision_rationale": "Optimal balance of expected value ($7M) vs risk (24% downside scenarios). Reddit represents 60% allocation due to 94% |
| _CANON/ARCS-Litepaper.md:852 | `24%` | ILLUSTRATIVE | "decision_rationale": "Optimal balance of expected value ($7M) vs risk (24% downside scenarios). Reddit represents 60% allocation due to 94% |
| _CANON/ARCS-Litepaper.md:852 | `60%` | ILLUSTRATIVE | "decision_rationale": "Optimal balance of expected value ($7M) vs risk (24% downside scenarios). Reddit represents 60% allocation due to 94% |
| _CANON/ARCS-Litepaper.md:852 | `94%` | ILLUSTRATIVE | "decision_rationale": "Optimal balance of expected value ($7M) vs risk (24% downside scenarios). Reddit represents 60% allocation due to 94% |
| _CANON/ARCS-Manifesto-Final.md:489 | `21+` | ILLUSTRATIVE | *"Candidate portal showed 'In Review' for 21+ days despite stated 7-day review timeline."* |
| _CANON/ARCS-Manifesto-Final.md:562 | `000+` | PROJECTION | **The Goal:** Reach critical mass (1,000+ attestations across 100+ organizations) where individual contributions become difficult to target  |
| _CANON/ARCS-Manifesto-Final.md:562 | `100+` | PROJECTION | **The Goal:** Reach critical mass (1,000+ attestations across 100+ organizations) where individual contributions become difficult to target  |
| _CANON/ARCS-Manifesto-Final.md:570 | `000+` | PROJECTION | **Our Position:** This risk is real. Mitigation comes through volume and distribution. When 1,000+ workers across 100+ companies contribute, |
| _CANON/ARCS-Manifesto-Final.md:570 | `100+` | PROJECTION | **Our Position:** This risk is real. Mitigation comes through volume and distribution. When 1,000+ workers across 100+ companies contribute, |
| _CANON/ARCS-Manifesto-Final.md:600 | `2026+` | PROJECTION | **Phase 3 (Q4 2026+): Integration** |
| _CANON/ARCS-Phenomenology.md:15 | `85%` | UNVALIDATED | **Core Thesis:** Human intuition is a **high-bandwidth, low-latency coherence detector** that complements (not replaces) computational ARCS. |
| _CANON/ARCS-Phenomenology.md:87 | `95%` | PROJECTION | - 95% CI: [4, 14 hours] |
| _CANON/ARCS-Phenomenology.md:88 | `72%` | PROJECTION | - Accuracy (sensation → PCI>0.4 within 24h): **72%** |
| _CANON/ARCS-Phenomenology.md:160 | `95%` | PROJECTION | - 95% CI: [30 min, 3 hours] |
| _CANON/ARCS-Phenomenology.md:161 | `68%` | PROJECTION | - Accuracy (sensation → jerk>0 within 4h): **68%** |
| _CANON/ARCS-Phenomenology.md:168 | `25%` | PARAMETER | 3. **Small position first:** Enter 25% position immediately, scale up as confirmation arrives |
| _CANON/ARCS-Phenomenology.md:169 | `3%` | PARAMETER | 4. **Set tight stop-loss:** Surge can be false alarm—limit downside to 2-3% |
| _CANON/ARCS-Phenomenology.md:173 | `$67K` | ILLUSTRATIVE | You're watching BTC consolidate around $67K (no clear trend). Suddenly: |
| _CANON/ARCS-Phenomenology.md:205 | `30 seconds` | PARAMETER | - Immediate (within **5-30 seconds** of considering option) |
| _CANON/ARCS-Phenomenology.md:243 | `82%` | UNVALIDATED | - Gut feeling (8-10) → Alignment > 0.85: **82% match** |
| _CANON/ARCS-Phenomenology.md:244 | `76%` | UNVALIDATED | - Gut feeling (8-10) → Good outcome (6mo): **76% success rate** |
| _CANON/ARCS-Phenomenology.md:245 | `79%` | UNVALIDATED | - Gut feeling (1-3) → Alignment < 0.50: **79% match** |
| _CANON/ARCS-Phenomenology.md:246 | `81%` | UNVALIDATED | - Gut feeling (1-3) → Bad outcome (6mo): **81% avoidance** |
| _CANON/ARCS-Phenomenology.md:255 | `20+` | PARAMETER | - ✅ **After you've calibrated** (logged 20+ decisions and validated accuracy) |
| _CANON/ARCS-Phenomenology.md:337 | `85%` | UNVALIDATED | - "That Vibes" moments: HR coherence > 0.7 (**85% of cases**) |
| _CANON/ARCS-Phenomenology.md:339 | `23%` | UNVALIDATED | - Sustained alignment (action taken by both): **72% when vibes detected** vs. 23% without |
| _CANON/ARCS-Phenomenology.md:339 | `72%` | UNVALIDATED | - Sustained alignment (action taken by both): **72% when vibes detected** vs. 23% without |
| _CANON/ARCS-Phenomenology.md:489 | `70%` | UNVALIDATED | - Calibration speed: **20-50 iterations** to achieve 70%+ accuracy |
| _CANON/ARCS-Phenomenology.md:516 | `Brier score < 0.15` | PARAMETER | **Well-calibrated intuition:** Brier score < 0.15 |
| _CANON/ARCS-Phenomenology.md:520 | `50+` | UNVALIDATED | **Claim 6.1:** Without Expected vs. Actual logging, intuition remains at Brier score ≈ 0.25 (random). With systematic logging (50+ decisions |
| _CANON/ARCS-Phenomenology.md:520 | `Brier score improves to 0.10` | UNVALIDATED | **Claim 6.1:** Without Expected vs. Actual logging, intuition remains at Brier score ≈ 0.25 (random). With systematic logging (50+ decisions |
| _CANON/ARCS-Phenomenology.md:520 | `Brier score ≈ 0.25` | UNVALIDATED | **Claim 6.1:** Without Expected vs. Actual logging, intuition remains at Brier score ≈ 0.25 (random). With systematic logging (50+ decisions |
| _CANON/ARCS-Phenomenology.md:533 | `85%` | ILLUSTRATIVE | - Probability of happiness: 85% |
| _CANON/ARCS-Phenomenology.md:534 | `70%` | ILLUSTRATIVE | - Probability of learning: 70% |
| _CANON/ARCS-Phenomenology.md:535 | `40%` | ILLUSTRATIVE | - Probability of promotion: 40% |
| _CANON/ARCS-Phenomenology.md:536 | `10%` | ILLUSTRATIVE | - Probability of regret: 10% |
| _CANON/ARCS-Phenomenology.md:556 | `60%` | ILLUSTRATIVE | - Overestimated happiness (expected 85%, actual 60%) |
| _CANON/ARCS-Phenomenology.md:556 | `85%` | ILLUSTRATIVE | - Overestimated happiness (expected 85%, actual 60%) |
| _CANON/ARCS-Phenomenology.md:557 | `70%` | ILLUSTRATIVE | - Underestimated learning (expected 70%, actual 80%) |
| _CANON/ARCS-Phenomenology.md:557 | `80%` | ILLUSTRATIVE | - Underestimated learning (expected 70%, actual 80%) |
| _CANON/ARCS-Phenomenology.md:563 | `20%` | ILLUSTRATIVE | - I tend to overestimate short-term promotions (update prior to 20% for 3-month window) |
| _CANON/ARCS-Phenomenology.md:571 | `20%` | ILLUSTRATIVE | - Downgrade promotion expectations (40% → 20% for 3-month window) |
| _CANON/ARCS-Phenomenology.md:571 | `40%` | ILLUSTRATIVE | - Downgrade promotion expectations (40% → 20% for 3-month window) |
| _CANON/ARCS-Phenomenology.md:580 | `60%` | ILLUSTRATIVE | - Happiness: [60%, 90%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:580 | `80%` | ILLUSTRATIVE | - Happiness: [60%, 90%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:580 | `90%` | ILLUSTRATIVE | - Happiness: [60%, 90%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:581 | `50%` | ILLUSTRATIVE | - Learning: [50%, 80%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:581 | `80%` | ILLUSTRATIVE | - Learning: [50%, 80%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:581 | `80%` | ILLUSTRATIVE | - Learning: [50%, 80%] with 80% confidence |
| _CANON/ARCS-Phenomenology.md:586 | `80%` | ILLUSTRATIVE | 80% of actual outcomes should fall within your 80% confidence intervals. |
| _CANON/ARCS-Phenomenology.md:586 | `80%` | ILLUSTRATIVE | 80% of actual outcomes should fall within your 80% confidence intervals. |
| _CANON/ARCS-Phenomenology.md:670 | `Brier score: 0.20` | UNVALIDATED | - Brier score: 0.20-0.30 (untrained) |
| _CANON/ARCS-Phenomenology.md:671 | `70%` | UNVALIDATED | - Overconfidence: 60-70% (people typically overestimate accuracy) |
| _CANON/ARCS-Phenomenology.md:681 | `70%` | PROJECTION | - "I predicted X with 70% confidence. Actual was Y. What does this tell me about my intuition?" |
| _CANON/ARCS-Phenomenology.md:685 | `Brier = 0.25` | PROJECTION | - Week 5: Brier = 0.25 |
| _CANON/ARCS-Phenomenology.md:686 | `Brier = 0.18` | PROJECTION | - Week 10: Brier = 0.18 |
| _CANON/ARCS-Phenomenology.md:687 | `Brier = 0.12` | PROJECTION | - Week 16: Brier = 0.12 (well-calibrated) |
| _CANON/ARCS-Phenomenology.md:699 | `Brier = 0.15` | PROJECTION | - If calibration transfers: Brier = 0.15-0.18 (close to trained domains) |
| _CANON/ARCS-Phenomenology.md:700 | `Brier = 0.22` | PROJECTION | - If domain-specific: Brier = 0.22-0.28 (back to baseline) |
| _CANON/ARCS-Phenomenology.md:713 | `80%` | UNVALIDATED | / **Accuracy** / 75-85% (empirical) / 70-80% (calibrated) / |
| _CANON/ARCS-Phenomenology.md:713 | `85%` | UNVALIDATED | / **Accuracy** / 75-85% (empirical) / 70-80% (calibrated) / |
| _CANON/ARCS-Phenomenology.md:793 | `78%` | PROJECTION | / Computational Only / 78% / 2.3 hours / 2.8/10 / 0.14 / |
| _CANON/ARCS-Phenomenology.md:794 | `72%` | PROJECTION | / Somatic Only / 72% / 15 min / 3.4/10 / 0.18 / |
| _CANON/ARCS-Phenomenology.md:795 | `84%` | PROJECTION | / Combined / **84%** / **45 min** / **1.9/10** / **0.11** / |
| _CANON/ARCS-Phenomenology.md:812 | `80%` | UNVALIDATED | **When properly calibrated through Expected vs. Actual feedback loops**, somatic intuition achieves **70-80% accuracy**—competitive with com |
| _CANON/ARCS-YellowPaper.md:11 | `$350B` | UNVALIDATED | We present a novel architectural framework for marketing intelligence systems that fundamentally rethinks decision support through the appli |
| _CANON/ARCS-YellowPaper.md:11 | `60%` | UNVALIDATED | We present a novel architectural framework for marketing intelligence systems that fundamentally rethinks decision support through the appli |
| _CANON/ARCS-YellowPaper.md:11 | `68%` | UNVALIDATED | We present a novel architectural framework for marketing intelligence systems that fundamentally rethinks decision support through the appli |
| _CANON/ARCS-YellowPaper.md:11 | `87%` | UNVALIDATED | We present a novel architectural framework for marketing intelligence systems that fundamentally rethinks decision support through the appli |
| _CANON/ARCS-YellowPaper.md:29 | `$50M` | UNVALIDATED | 1. **Documentation Deficit**: Budget allocations of $50M+ proceed without documented reasoning or alternative evaluation |
| _CANON/ARCS-YellowPaper.md:57 | `40%` | PROJECTION | - Hook: Measurable performance improvement (40%+ ROAS lift) [Unvalidated target: asserted threshold, no control group; see Technical Overvie |
| _CANON/ARCS-YellowPaper.md:62 | `40+` | PROJECTION | - Hook: Complexity reduction (40+ tools → 1 platform) |
| _CANON/ARCS-YellowPaper.md:154 | `95%` | PARAMETER | **Critical Innovation**: Unlike systems claiming deterministic predictions, this framework explicitly quantifies uncertainty. A prediction o |
| _CANON/ARCS-YellowPaper.md:160 | `87%` | UNVALIDATED | - **Accuracy**: 87% of actual outcomes fall within predicted confidence intervals |
| _CANON/ARCS-YellowPaper.md:161 | `15%` | UNVALIDATED | - **Precision**: Mean Absolute Percentage Error (MAPE) of 12-15% |
| _CANON/ARCS-YellowPaper.md:162 | `76%` | UNVALIDATED | - **Comparative Performance**: Outperforms human expert predictions in 76% of cases |
| _CANON/ARCS-YellowPaper.md:163 | `p < 0.01` | UNVALIDATED | - **Calibration**: Predicted confidence levels align with observed outcome distributions (χ² test, p < 0.01) |
| _CANON/ARCS-YellowPaper.md:208 | `22%` | UNVALIDATED | / 1,000 / 68% / 22% / 0.3s / |
| _CANON/ARCS-YellowPaper.md:208 | `68%` | UNVALIDATED | / 1,000 / 68% / 22% / 0.3s / |
| _CANON/ARCS-YellowPaper.md:209 | `17%` | UNVALIDATED | / 10,000 / 78% / 17% / 0.8s / |
| _CANON/ARCS-YellowPaper.md:209 | `78%` | UNVALIDATED | / 10,000 / 78% / 17% / 0.8s / |
| _CANON/ARCS-YellowPaper.md:210 | `12%` | UNVALIDATED | / 100,000 / 87% / 12% / 2.1s / |
| _CANON/ARCS-YellowPaper.md:210 | `87%` | UNVALIDATED | / 100,000 / 87% / 12% / 2.1s / |
| _CANON/ARCS-YellowPaper.md:211 | `8%` | UNVALIDATED | / 1,000,000 (projected) / 92% / 8% / 4.5s / |
| _CANON/ARCS-YellowPaper.md:211 | `92%` | UNVALIDATED | / 1,000,000 (projected) / 92% / 8% / 4.5s / |
| _CANON/ARCS-YellowPaper.md:292 | `3+` | PARAMETER | When multiple signals converge positively (3+ standard deviations from baseline), the system: |
| _CANON/ARCS-YellowPaper.md:303 | `18%` | ILLUSTRATIVE | - CPM decrease: -18% (inventory signal) |
| _CANON/ARCS-YellowPaper.md:304 | `34%` | ILLUSTRATIVE | - Engagement spike: +34% (audience signal) |
| _CANON/ARCS-YellowPaper.md:378 | `000+` | PROJECTION | **Competitive Moat**: A platform with 100,000+ receipts provides materially better predictions than one with 10,000 receipts. This advantage |
| _CANON/ARCS-YellowPaper.md:389 | `40%` | PROJECTION | - 40%+ ROAS improvement over baseline |
| _CANON/ARCS-YellowPaper.md:402 | `68%` | UNVALIDATED | - Loss of prediction accuracy (revert to 68% baseline vs. 87% with system) |
| _CANON/ARCS-YellowPaper.md:402 | `87%` | UNVALIDATED | - Loss of prediction accuracy (revert to 68% baseline vs. 87% with system) |
| _CANON/ARCS-YellowPaper.md:406 | `18%` | PROJECTION | **Expected Churn**: 12-18% annually (typical enterprise SaaS) |
| _CANON/ARCS-YellowPaper.md:413 | `40+` | PROJECTION | - Eliminate 40+ point solutions (single platform) |
| _CANON/ARCS-YellowPaper.md:414 | `$5M` | PROJECTION | - $5M+ annual cost savings (vendor consolidation) |
| _CANON/ARCS-YellowPaper.md:446 | `8%` | PROJECTION | **Expected Churn**: 5-8% annually (high switching cost SaaS) |
| _CANON/ARCS-YellowPaper.md:492 | `2%` | PROJECTION | **Expected Churn**: <2% annually (infrastructure-level retention) |
| _CANON/ARCS-YellowPaper.md:511 | `$7.5M` | PROJECTION | / Private / $7.5M / Zero (siloed) / 72-78% / Agency recommended / |
| _CANON/ARCS-YellowPaper.md:511 | `78%` | UNVALIDATED | / Private / $7.5M / Zero (siloed) / 72-78% / Agency recommended / |
| _CANON/ARCS-YellowPaper.md:512 | `$4.5M` | PROJECTION | / Partial / $4.5M / Anonymized patterns / 82-88% / Rational clients choose / |
| _CANON/ARCS-YellowPaper.md:512 | `88%` | UNVALIDATED | / Partial / $4.5M / Anonymized patterns / 82-88% / Rational clients choose / |
| _CANON/ARCS-YellowPaper.md:513 | `$2.5M` | PROJECTION | / Full / $2.5M / All receipts shared / 87-92% / Optimal performance / |
| _CANON/ARCS-YellowPaper.md:513 | `92%` | UNVALIDATED | / Full / $2.5M / All receipts shared / 87-92% / Optimal performance / |
| _CANON/ARCS-YellowPaper.md:520 | `18%` | UNVALIDATED | 2. Clients observe 15-18% performance gap vs. Full tier |
| _CANON/ARCS-YellowPaper.md:539 | `50%` | ILLUSTRATIVE | Discrepancy: 50% gap between public claim and private belief |
| _CANON/ARCS-YellowPaper.md:595 | `40%` | PROJECTION | Promise: 40% ROAS improvement over baseline within 90 days |
| _CANON/ARCS-YellowPaper.md:599 | `80%` | PROJECTION | Refund: If client followed recommendations ≥80% and missed target → Full refund |
| _CANON/ARCS-YellowPaper.md:663 | `$850B` | UNVALIDATED | - Global enterprise marketing: $850B annually |
| _CANON/ARCS-YellowPaper.md:664 | `$350B` | UNVALIDATED | - US enterprise (500+ employees): $350B annually |
| _CANON/ARCS-YellowPaper.md:664 | `500+` | PARAMETER | - US enterprise (500+ employees): $350B annually |
| _CANON/ARCS-YellowPaper.md:665 | `$180B` | UNVALIDATED | - Addressable segment (Fortune 5000 + growth): $180B annually |
| _CANON/ARCS-YellowPaper.md:667 | `0.01%` | UNVALIDATED | **Current Market Penetration**: <0.01% (greenfield opportunity) |
| _CANON/ARCS-YellowPaper.md:673 | `$2.7B` | PROJECTION | / Aggressive / 1.5% / $2.7B / 600 / 20% / |
| _CANON/ARCS-YellowPaper.md:673 | `1.5%` | PROJECTION | / Aggressive / 1.5% / $2.7B / 600 / 20% / |
| _CANON/ARCS-YellowPaper.md:673 | `20%` | PROJECTION | / Aggressive / 1.5% / $2.7B / 600 / 20% / |
| _CANON/ARCS-YellowPaper.md:674 | `$1.1B` | PROJECTION | / Base / 0.6% / $1.1B / 250 / 60% / |
| _CANON/ARCS-YellowPaper.md:674 | `0.6%` | PROJECTION | / Base / 0.6% / $1.1B / 250 / 60% / |
| _CANON/ARCS-YellowPaper.md:674 | `60%` | PROJECTION | / Base / 0.6% / $1.1B / 250 / 60% / |
| _CANON/ARCS-YellowPaper.md:675 | `$360M` | PROJECTION | / Conservative / 0.2% / $360M / 85 / 20% / |
| _CANON/ARCS-YellowPaper.md:675 | `0.2%` | PROJECTION | / Conservative / 0.2% / $360M / 85 / 20% / |
| _CANON/ARCS-YellowPaper.md:675 | `20%` | PROJECTION | / Conservative / 0.2% / $360M / 85 / 20% / |
| _CANON/ARCS-YellowPaper.md:677 | `$1.2B` | PROJECTION | **Probability-Weighted Expected Value**: 0.67% market share, $1.2B ARR |
| _CANON/ARCS-YellowPaper.md:677 | `0.67%` | PROJECTION | **Probability-Weighted Expected Value**: 0.67% market share, $1.2B ARR |
| _CANON/ARCS-YellowPaper.md:679 | `0.6%` | PROJECTION | **Validation**: 0.6% market share requires 250 customers from 5,000 addressable companies (5% penetration in 36 months). With 40%+ ROAS impr |
| _CANON/ARCS-YellowPaper.md:679 | `40%` | PROJECTION | **Validation**: 0.6% market share requires 250 customers from 5,000 addressable companies (5% penetration in 36 months). With 40%+ ROAS impr |
| _CANON/ARCS-YellowPaper.md:679 | `5%` | PROJECTION | **Validation**: 0.6% market share requires 250 customers from 5,000 addressable companies (5% penetration in 36 months). With 40%+ ROAS impr |
| _CANON/ARCS-YellowPaper.md:679 | `5%` | PROJECTION | **Validation**: 0.6% market share requires 250 customers from 5,000 addressable companies (5% penetration in 36 months). With 40%+ ROAS impr |
| _CANON/ARCS-YellowPaper.md:694 | `68%` | UNVALIDATED | - \( A_0 \) = baseline accuracy with zero network (≈68%) |
| _CANON/ARCS-YellowPaper.md:695 | `92%` | UNVALIDATED | - \( A_{\infty} \) = asymptotic accuracy at infinite scale (≈92%) |
| _CANON/ARCS-YellowPaper.md:702 | `69%` | UNVALIDATED | / 10 / 5,000 / 69% / - / |
| _CANON/ARCS-YellowPaper.md:703 | `77%` | UNVALIDATED | / 100 / 50,000 / 77% / +8% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:703 | `8%` | UNVALIDATED | / 100 / 50,000 / 77% / +8% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:704 | `16%` | UNVALIDATED | / 500 / 250,000 / 85% / +16% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:704 | `85%` | UNVALIDATED | / 500 / 250,000 / 85% / +16% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:705 | `19%` | UNVALIDATED | / 1,000 / 500,000 / 88% / +19% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:705 | `88%` | UNVALIDATED | / 1,000 / 500,000 / 88% / +19% vs. new entrant / |
| _CANON/ARCS-YellowPaper.md:709 | `16%` | UNVALIDATED | Early platform with 500 customers provides 16% better predictions than new entrant starting from zero. Rational customers prefer established |
| _CANON/ARCS-YellowPaper.md:715 | `80%` | UNVALIDATED | **Market Structure Prediction**: Similar to search (Google), e-commerce (Amazon), or CRM (Salesforce)—winner captures 60-80% market share wi |
| _CANON/ARCS-YellowPaper.md:720 | `$200K` | PROJECTION | - Switching Cost: ~$200K (retraining + accuracy loss) |
| _CANON/ARCS-YellowPaper.md:721 | `$4M` | PROJECTION | - Annual Value: ~$4M (ROAS improvement) |
| _CANON/ARCS-YellowPaper.md:725 | `$2M` | PROJECTION | - Switching Cost: ~$2M (data migration + operational disruption) |
| _CANON/ARCS-YellowPaper.md:726 | `$8M` | PROJECTION | - Annual Value: ~$8M (ROAS + cost savings) |
| _CANON/ARCS-YellowPaper.md:731 | `$12M` | PROJECTION | - Annual Value: ~$12M (ROAS + savings + risk mitigation) |
| _CANON/ARCS-YellowPaper.md:738 | `18%` | PROJECTION | / Phase 1 / 12-18% / Normal SaaS (some customers don't see value) / |
| _CANON/ARCS-YellowPaper.md:739 | `8%` | PROJECTION | / Phase 2 / 5-8% / High switching cost (operational dependency) / |
| _CANON/ARCS-YellowPaper.md:740 | `2%` | PROJECTION | / Phase 3 / <2% / Infrastructure-level (legal necessity) / |
| _CANON/ARCS-YellowPaper.md:755 | `30%` | PROJECTION | **Probability**: Medium (30%) |
| _CANON/ARCS-YellowPaper.md:769 | `25%` | PROJECTION | **Probability**: Low-Medium (25%) |
| _CANON/ARCS-YellowPaper.md:775 | `15%` | UNVALIDATED | - Performance data makes resistance untenable (15% gap) |
| _CANON/ARCS-YellowPaper.md:783 | `60%` | PROJECTION | **Probability**: High (60% within 24 months) |
| _CANON/ARCS-YellowPaper.md:788 | `18+` | PROJECTION | - Patent core innovations (18+ months IP protection) |
| _CANON/ARCS-YellowPaper.md:799 | `35%` | PROJECTION | **Probability**: Medium (35%) |
| _CANON/ARCS-YellowPaper.md:813 | `20%` | PROJECTION | **Probability**: Low-Medium (20%) |
| _CANON/ARCS-YellowPaper.md:924 | `$350B` | UNVALIDATED | Enterprise marketing currently represents a $350B annual expenditure with near-zero accountability infrastructure. This paper demonstrates t |
| _CANON/ARCS-YellowPaper.md:958 | `$350B` | UNVALIDATED | Marketing has operated on intuition and incomplete information for decades. The technology now exists to transform this $350B function into  |
| _CANON/ARCS-YellowPaper.md:1043 | `95%` | PARAMETER | / \( \text{CI}_{95\%}(O) \) / 95% confidence interval for outcome / |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:51 | `5%` | UNCOVERED | - Fixed: 5% (very low — prefers fluid, adaptive structures) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:52 | `45%` | UNCOVERED | - Deliberate: 45% (measured, strategic) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:53 | `50%` | UNCOVERED | - Rapid: 50% (iterate quickly, high experimental cadence) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:82 | `20%` | UNCOVERED | - Fixed: 20% (some structural preference but mostly fluid) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:83 | `55%` | UNCOVERED | - Deliberate: 55% (strategic, measured, patient capital mindset) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:84 | `25%` | UNCOVERED | - Rapid: 25% (can move fast when kairos hits) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:116 | `10%` | UNCOVERED | - Fixed: 10% (highly adaptive, willing to experiment) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:117 | `30%` | UNCOVERED | - Deliberate: 30% |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:118 | `60%` | UNCOVERED | - Rapid: 60% (high creative output velocity, momentum-based) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:126 | `$50` | UNCOVERED | - Paints 400-ft mega-murals at $50–75/sq ft with hyper-detailed photoreal work. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:132 | `25+` | UNCOVERED | - 25+ requests/year; needs help sorting and sequencing. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:160 | `40%` | UNCOVERED | - Fixed: 40% (enterprise clients, structured programs) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:161 | `50%` | UNCOVERED | - Deliberate: 50% (methodical, evidence-based) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:162 | `10%` | UNCOVERED | - Rapid: 10% (slow to adopt new tools but high leverage when they do) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:170 | `200+` | UNCOVERED | - 200+ corporate events/year; built-in distribution for pilots. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:199 | `5%` | UNCOVERED | - Fixed: 5% (hyper-adaptive, platform-dependent) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:200 | `20%` | UNCOVERED | - Deliberate: 20% |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:201 | `75%` | UNCOVERED | - Rapid: 75% (content treadmill, rapid iteration, A/B test everything) |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:206 | `200+` | UNCOVERED | - Jeben's wife runs 200+ YouTube creator events/year (top creators, black creators, science creators, entertainment). |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:319 | `25+` | UNCOVERED | - Best year ever (2024), momentum building, 25+ requests in pipeline. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:362 | `$100` | UNCOVERED | - 14-day pre-order window: if fans fund it (500 decks @ $100 = $50K), it gets made. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:362 | `$50K` | UNCOVERED | - 14-day pre-order window: if fans fund it (500 decks @ $100 = $50K), it gets made. |
| _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md:363 | `100%` | UNCOVERED | - Zero inventory risk; 100% creative control with her. |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:20 | `$12B` | PROJECTION | **New Market Opportunities**: $15B+ in content strategy platforms, $8B in trend analytics, $12B in real-time campaign optimization. |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:20 | `$15B` | PROJECTION | **New Market Opportunities**: $15B+ in content strategy platforms, $8B in trend analytics, $12B in real-time campaign optimization. |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:20 | `$8B` | PROJECTION | **New Market Opportunities**: $15B+ in content strategy platforms, $8B in trend analytics, $12B in real-time campaign optimization. |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:36 | `80%` | UNVALIDATED | - Miss 60-80% of optimal entry windows for trending topics |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:37 | `$10M` | UNVALIDATED | - Waste $10M+ annually on late-stage trend participation |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:48 | `70%` | UNVALIDATED | - 70% of content fails to achieve engagement benchmarks |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:60 | `40%` | UNVALIDATED | - Over-provisioning wastes 40% of compute resources |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:73 | `85%` | UNVALIDATED | - Performance: 85% accuracy in identifying trends 6-12 hours early |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:78 | `78%` | UNVALIDATED | - Performance: 78% accuracy in predicting viral cascades 24 hours in advance |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:83 | `15%` | UNVALIDATED | - Performance: 82% accuracy in predicting total reach within 15% |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:83 | `82%` | UNVALIDATED | - Performance: 82% accuracy in predicting total reach within 15% |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:88 | `35%` | UNVALIDATED | - Performance: 35% improvement in multi-campaign ROAS via optimal spacing |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:93 | `45%` | UNVALIDATED | - Performance: Reduces wasted spend on declining content by 45% |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:107 | `65%` | UNVALIDATED | - 65% improvement in engagement rates vs. baseline content |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:108 | `92%` | UNVALIDATED | - 92% of high-resonance predictions achieve >2σ above mean engagement |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:109 | `78%` | UNVALIDATED | - 78% reduction in content iteration cycles (get it right first time) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:131 | `40%` | UNVALIDATED | - 40% reduction in over-provisioning (services activate only when needed) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:132 | `60%` | UNVALIDATED | - 60% faster response to kairos windows (automated triggering) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:133 | `25%` | UNVALIDATED | - 25% cost savings vs. always-on microservice architectures |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:157 | `$2,999` | PROJECTION | **Pricing**: $299/month (individual) → $2,999/month (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:157 | `$299` | PROJECTION | **Pricing**: $299/month (individual) → $2,999/month (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:158 | `$8B` | PROJECTION | **TAM**: $8B (2028) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:163 | `000+` | UNVALIDATED | - Validated on 10,000+ historical viral events |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:177 | `$9,999` | PROJECTION | **Pricing**: $999/month (agency) → $9,999/month (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:177 | `$999` | PROJECTION | **Pricing**: $999/month (agency) → $9,999/month (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:178 | `$15B` | PROJECTION | **TAM**: $15B (2029) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:182 | `65%` | UNVALIDATED | - 65% engagement improvement vs. human copywriters |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:197 | `$1,999` | PROJECTION | **Pricing**: $1,999/month (agency) → Custom (enterprise) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:198 | `$5B` | PROJECTION | **TAM**: $5B (2028) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:202 | `35%` | UNVALIDATED | - 35% ROAS improvement in multi-campaign contexts |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:218 | `$12B` | PROJECTION | **TAM**: $12B (2029) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:222 | `40%` | UNVALIDATED | - 40% cost reduction vs. always-on architectures |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:285 | `$18M` | PROJECTION | / AI Optimizer / $5M / $18M / $45M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:285 | `$45M` | PROJECTION | / AI Optimizer / $5M / $18M / $45M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:285 | `$5M` | PROJECTION | / AI Optimizer / $5M / $18M / $45M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:286 | `$12M` | PROJECTION | / Coherence Monitor / $3M / $12M / $35M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:286 | `$35M` | PROJECTION | / Coherence Monitor / $3M / $12M / $35M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:286 | `$3M` | PROJECTION | / Coherence Monitor / $3M / $12M / $35M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:287 | `$15M` | PROJECTION | / **Trend Surfer (NEW)** / $2M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:287 | `$2M` | PROJECTION | / **Trend Surfer (NEW)** / $2M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:287 | `$40M` | PROJECTION | / **Trend Surfer (NEW)** / $2M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:288 | `$25M` | PROJECTION | / **Rhetorical Compiler (NEW)** / $6M / $25M / $70M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:288 | `$6M` | PROJECTION | / **Rhetorical Compiler (NEW)** / $6M / $25M / $70M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:288 | `$70M` | PROJECTION | / **Rhetorical Compiler (NEW)** / $6M / $25M / $70M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:289 | `$1M` | PROJECTION | / **Phase Scheduler (NEW)** / $1M / $8M / $25M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:289 | `$25M` | PROJECTION | / **Phase Scheduler (NEW)** / $1M / $8M / $25M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:289 | `$8M` | PROJECTION | / **Phase Scheduler (NEW)** / $1M / $8M / $25M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:290 | `$10M` | PROJECTION | / **Service Catalyst (NEW)** / $2M / $10M / $30M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:290 | `$2M` | PROJECTION | / **Service Catalyst (NEW)** / $2M / $10M / $30M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:290 | `$30M` | PROJECTION | / **Service Catalyst (NEW)** / $2M / $10M / $30M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:291 | `$35M` | PROJECTION | / OrgOS / $8M / $35M / $90M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:291 | `$8M` | PROJECTION | / OrgOS / $8M / $35M / $90M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:291 | `$90M` | PROJECTION | / OrgOS / $8M / $35M / $90M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:292 | `$15M` | PROJECTION | / Risk Engine / $3M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:292 | `$3M` | PROJECTION | / Risk Engine / $3M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:292 | `$40M` | PROJECTION | / Risk Engine / $3M / $15M / $40M / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:293 | `$138M` | PROJECTION | / **TOTAL** / **$30M** / **$138M** / **$375M** / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:293 | `$30M` | PROJECTION | / **TOTAL** / **$30M** / **$138M** / **$375M** / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:293 | `$375M` | PROJECTION | / **TOTAL** / **$30M** / **$138M** / **$375M** / |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:295 | `20%` | PROJECTION | **EBITDA Margin**: -20% (Y1) → +35% (Y2) → +48% (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:295 | `35%` | PROJECTION | **EBITDA Margin**: -20% (Y1) → +35% (Y2) → +48% (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:295 | `48%` | PROJECTION | **EBITDA Margin**: -20% (Y1) → +35% (Y2) → +48% (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:297 | `$1.1B` | PROJECTION | **Valuation**: $250M (Y1) → $1.1B (Y2) → $3B (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:297 | `$250M` | PROJECTION | **Valuation**: $250M (Y1) → $1.1B (Y2) → $3B (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:297 | `$3B` | PROJECTION | **Valuation**: $250M (Y1) → $1.1B (Y2) → $3B (Y3) |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:306 | `000+` | UNVALIDATED | - 10,000+ historical trend validation dataset |
| _CANON/arcs-v9-additional/ARCS-WhitePaper-v2-1.md:327 | `$50B` | PROJECTION | - **8 new products** addressing $50B+ in additional TAM |
| _CANON/arcs-v9-additional/ARCS-YellowPaper-v1-2.md:671 | `5+` | PROJECTION | - Patent filings across 5+ novel invention domains |
| _CANON/arcs-v9-additional/ARCS-v9-Chapter-Book-Canon.md:258 | `3+` | PARAMETER | If 3+ turns drift from JTBD without producing an artifact, surface: |
| _CANON/arcs-v9-additional/ARCS-v9-Chapter-Book-Canon.md:319 | `2+` | PARAMETER | - v10: major (architectural change; requires full Deep Shavasana MetaAudit + 2+ pilot receipts) |
| _CANON/arcs-v9-additional/ARCS-v9-Chapter-Book-Canon.md:480 | `2+` | PARAMETER | *Next version bump requires: Deep Shavasana MetaAudit + 2+ pilot receipts* |
| _CANON/book-ii/part-i-firehose-to-compass.md:41 | `50+` | PARAMETER | The other response is to outsource the decision itself. Ask the AI. Get a recommendation. Take the answer and move. This works for low-stake |
| _CANON/book-ii/part-i-firehose-to-compass.md:87 | `85%` | ILLUSTRATIVE | > *"This brief renders at 85% fidelity — conviction gradient is still SHIFTING. The True North is directionally reliable but not crystalline |
| _CANON/book-ii/part-i-firehose-to-compass.md:91 | `80+` | PARAMETER | **Receipt:** `runtime/specs/dewy-receipt-schema-v1.json` — `render_resolution` field; NCI composite thresholds (HOLD at < 40, fidelity heade |
| _CANON/book-ii/part-i-firehose-to-compass.md:140 | `50+` | PARAMETER | / RC-001 / AI recommendation-taking fails for high-conviction-gap decisions / ROM CANDIDATE / Promote after Observatory 50+ session comparis |
| _CANON/index.md:61 | `100+` | PROJECTION | **Implementation gates:** See ADR-023 (100+ receipts) + ADR-013 (30-day Lab inquiry threshold) |
| _CANON/living/ARCS-Codex-v8.5.md:58 | `20%` | ILLUSTRATIVE | *   **Example**: `/ward --protocol stop_loss --threshold 20` (Halts project if confidence drops < 20%) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:13 | `$15M` | PROJECTION | / **White Paper v2.0** / ARCS-WhitePaper-v2-0.md / Investors, C-suite / Commercial thesis, $15M Series A pitch, 5-year revenue projections / |
| _CANON/living/ARCS-Technical-Overview-April2026.md:63 | `5%` | PROJECTION | └── Commercial: 5% gross revenue revenue share |
| _CANON/living/ARCS-Technical-Overview-April2026.md:73 | `$5M` | PROJECTION | 2026 /   $5M      / AI Optimizer early adopters |
| _CANON/living/ARCS-Technical-Overview-April2026.md:74 | `$25M` | PROJECTION | 2027 /  $25M      / Enterprise OrgOS expansion |
| _CANON/living/ARCS-Technical-Overview-April2026.md:75 | `$80M` | PROJECTION | 2028 /  $80M      / Digital Therapeutic launch |
| _CANON/living/ARCS-Technical-Overview-April2026.md:76 | `$200M` | PROJECTION | 2029 / $200M      / Multi-product scaled deployment |
| _CANON/living/ARCS-Technical-Overview-April2026.md:77 | `$450M` | PROJECTION | 2030 / $450M      / Financial services international |
| _CANON/living/ARCS-Technical-Overview-April2026.md:138 | `95%` | PARAMETER | **Confidence Interval (95%):** |
| _CANON/living/ARCS-Technical-Overview-April2026.md:179 | `87%` | UNVALIDATED | Claim: 87% of predictions fall within stated 95% CI |
| _CANON/living/ARCS-Technical-Overview-April2026.md:179 | `95%` | UNVALIDATED | Claim: 87% of predictions fall within stated 95% CI |
| _CANON/living/ARCS-Technical-Overview-April2026.md:185 | `15%` | UNVALIDATED | Claim: MAPE 12–15% (vs 22% baseline) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:185 | `22%` | UNVALIDATED | Claim: MAPE 12–15% (vs 22% baseline) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:199 | `32%` | UNVALIDATED | Claim: Energy sustainability prediction 78% vs 32% (skills-based) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:199 | `78%` | UNVALIDATED | Claim: Energy sustainability prediction 78% vs 32% (skills-based) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:206 | `92%` | UNVALIDATED | Risk: Circular — derived from desired endpoint (92% at 1M receipts) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:209 | `40%` | UNVALIDATED | Claim: 40% ROAS improvement guarantee |
| _CANON/living/ARCS-Technical-Overview-April2026.md:210 | `87%` | UNVALIDATED | Status: Asserted based on 87% accuracy claim |
| _CANON/living/ARCS-Technical-Overview-April2026.md:415 | `$100B` | PARAMETER | b) Market cap > $100B, OR |
| _CANON/living/ARCS-Technical-Overview-April2026.md:566 | `3+` | PARAMETER | When: 3+ positive signal anomalies converge (>3σ from baseline) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:607 | `25%` | PARAMETER | Key parameter: self.threshold = 0.25 (Kairos must be 25% better) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:612 | `25%` | PARAMETER | self.threshold = 0.25  # Initial: 25% EV advantage required |
| _CANON/living/ARCS-Technical-Overview-April2026.md:656 | `50+` | PARAMETER | / **Data source** / Energy cycles, capacity, recovery / 50+ real-time signal streams / Both coaches' EV outputs / |
| _CANON/living/ARCS-Technical-Overview-April2026.md:693 | `$15M` | PROJECTION | → Series A pitch ($15M ask, $75M pre-money) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:693 | `$75M` | PROJECTION | → Series A pitch ($15M ask, $75M pre-money) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:696 | `$450M` | PROJECTION | → Revenue model: $5M → $450M (2026–2030) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:696 | `$5M` | PROJECTION | → Revenue model: $5M → $450M (2026–2030) |
| _CANON/living/ARCS-Technical-Overview-April2026.md:779 | `$49` | PROJECTION | / Over-reliance on enterprise sales (9-month cycle) / Business / MEDIUM / SMB self-serve tier (Canon mentions $49/mo) / |
| _CANON/living/ARCS-v9-Canon-Operational.md:126 | `up to 3` | PARAMETER | / **SIMPLE** / One True North sentence + up to 3 bullets / Default / |
| operators/arcs_primitives.py:187 | `50+` | PARAMETER | 50+ chars scores 1.0. |
| operators/arcs_primitives.py:290 | `r=0.72` | UNVALIDATED | phase_tuning     : Calibration signal (r=0.72 coherence correlation) |
| operators/arcs_primitives.py:292 | `76%` | UNVALIDATED | feels_right      : Gut-level validity check (76% predictive accuracy) |
| operators/arcs_primitives.py:293 | `72%` | UNVALIDATED | that_vibes       : Relational resonance indicator (72% stability predictor) |
| operators/arcs_primitives.py:295 | `Brier score improvement: 0.25→0.12` | UNVALIDATED | expected_vs_actual: Calibration accuracy (Brier score improvement: 0.25→0.12) |
