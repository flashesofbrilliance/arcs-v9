# 04 Cost-baseline template (one page, INTERNAL DRAFT, 2026-10-08)

Every cell is a placeholder. No price, rate, term or budget has been agreed or sourced. Fill a cell only with a number that carries a source and a date; otherwise leave `TBD`. Read-only on the client's financial data: this sheet records inputs they give us and never approves or pays anything. Cost driver codes match `02-sow-scaffold.md`: T time, V vendor or subscription, K model tokens, L legal or counsel, O other.

**Inputs to collect (each with owner and source):**
`rate_zach` = EXAMPLE, set by Zach after the NDA materials are read. `hours_<item>` = from the sequenced backlog (F.1). `price_per_token_<model>` = vendor price page, fetch date recorded. `users_<persona>` = from the founders' token-cost model (light, typical, heavy; long-term user counts as they stated). `docs_per_user`, `tokens_per_doc` = from the build spec and a measured sample of synthetic documents. `counsel_hours` = counsel's own estimate, not ours.

## Fixed, variable and hidden under three cases

| Line | Code | Best | Base | Worst | Formula or source | Owner | Status |
|---|---|---|---|---|---|---|---|
| **FIXED** | | | | | | | |
| Phase 0 (audit, light discovery) | T | EXAMPLE | EXAMPLE | EXAMPLE | hours_P0 × rate_zach | Z | TBD |
| Phase 1 (shareback, roadmap co-design, fork workshop) | T | EXAMPLE | EXAMPLE | EXAMPLE | hours_P1 × rate_zach | Z | TBD |
| Environment setup (B.1) | T | EXAMPLE | EXAMPLE | EXAMPLE | hours_B1 × rate | Z | TBD |
| Counsel review (L.1 to L.6, L.9) | L | EXAMPLE | EXAMPLE | EXAMPLE | counsel_hours × counsel_rate | founders | TBD |
| Platform subscriptions (build tool, database, hosting) | V | EXAMPLE | EXAMPLE | EXAMPLE | plan price × months, from vendor pages | C | TBD |
| Vendor compliance tier, if counsel requires one (L.4) | V | EXAMPLE | EXAMPLE | EXAMPLE | vendor quote; not assumed to exist | C | TBD |
| **VARIABLE** | | | | | | | |
| Model tokens per persona | K | EXAMPLE | EXAMPLE | EXAMPLE | users × sessions × (input tokens + output tokens) × price_per_token | Z with C | TBD |
| Vault documents as input tokens | K | EXAMPLE | EXAMPLE | EXAMPLE | docs_per_user × tokens_per_doc × reads per month × price | Z with C | TBD |
| Open-web search and file processing calls | V | EXAMPLE | EXAMPLE | EXAMPLE | per-call price × calls (not tokens) | C | TBD |
| Fractional or advisory hours after Phase 1 | T | EXAMPLE | EXAMPLE | EXAMPLE | hours per sprint × sprints × rate | Z | TBD |
| **HIDDEN** | | | | | | | |
| Rework after counsel answers arrive late or differ | T | EXAMPLE | EXAMPLE | EXAMPLE | share of B.3 and B.4 hours redone | Co | TBD |
| Redaction review burden on parents (B.4) | O | EXAMPLE | EXAMPLE | EXAMPLE | support hours per user cohort | C | TBD |
| Accessibility remediation (F.6) | T | EXAMPLE | EXAMPLE | EXAMPLE | depends on the standard counsel confirms | Co | TBD |
| Vendor migration if the model vendor must change (switch cost) | T | EXAMPLE | EXAMPLE | EXAMPLE | measured by the B.2 swap test, not guessed | Z | TBD |
| Founder time (four people, other work) | O | EXAMPLE | EXAMPLE | EXAMPLE | hours per week × weeks; opportunity cost, not cash | Co | TBD |
| Unowned subscriptions and orphaned accounts (H.3) | V | EXAMPLE | EXAMPLE | EXAMPLE | accounts inventory | C | TBD |

## Case definitions (set before filling, not after)

- **Best:** counsel answers arrive before B.3 starts; synthetic redaction recall is high enough that review is a spot check; the lightest persona dominates.
- **Base:** the founders' typical-user assumption; counsel answers arrive mid-build; one vendor change is not needed.
- **Worst:** the heaviest persona dominates; a vendor change or a counsel-required architecture change lands after B.3.

Benchmarks, if any are used, are quoted as percentiles with a source, a date and an incentive note. "Industry average" is not a base case.

## Variance column for later

When real spend starts, add actual vs projected beside each line, as `_PATTERNS/workflow-cost-ledger.md` does for workflow runs; revisit a line when it drifts by more than the tolerance agreed at P0.A3.

## Visibility (open question 3)

If cost visibility is an engagement outcome, add: per-user cost dashboard, spend alerts, cap tests (F.4, B.6). If not, they stay recommendations.
