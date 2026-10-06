# Belief log: what moved USDC in January 2026

Question: why did USDC supply fall about $5.7B to $6.6B between Jan 15 and Jan 31, 2026, then recover? Two published pieces (Custody Collateral, Flippening) treated it as forced institutional liquidation after the SEC's Jan 28 statement.

How to read this: a credence is my subjective probability that a factor was a material contributor (more than about 10%) to the January move. Credences do not sum to one, because factors overlap. They are calibration aids, not measurements. Evidence class: **P** primary page or filing, **D** public data series pulled directly (DefiLlama, CoinGecko, FRED), **S** secondary reporting or search summary.

## A. Hypotheses, priors and where they ended

| ID | Hypothesis | Prior | Now | Deciding test | Falsifier | Evidence | Status |
|---|---|---|---|---|---|---|---|
| H1 | Regulation-forced institutional liquidation after the SEC Jan 28 statement | 0.55 | 0.05 | Word search of the statement; agency posture timeline | The statement names wstETH, T-bills or wrappers | P | Premise failed |
| H2 | Same-day deleveraging (Jan 20 and Jan 30 liquidations) | 0.20 | 0.50 | Largest USDC daily drops against liquidation dates | Drops with no liquidation event | S, D | Best fit, inference |
| H3 | Macro risk-off (tariff threats, record JGB yields, yen +3% Jan 20 to 29) | 0.15 | 0.35 | Event dates against drop dates; USD/JPY series | Drop precedes the shocks | S, D | Plausible, overlaps H2 |
| H4 | Rotation into tokenized Treasuries | 0.10 | 0.20 | USDY, USYC, BUIDL supply, Jan 15 to 31 | Tokenized Treasuries flat | D | Real but small (about +$0.8B) |
| H5 | Migration to bank deposit tokens (BNY service launched Jan 9) | 0.10 | 0.15 | BNY and JPM disclosures | Volume shown to be trivial | P, S | Size unknown |
| H6 | Lagged effect of Oct 10 cascade and Q4 DeFi lending collapses | 0.20 | 0.10 | USDC, USDe path Oct to Jan | USDC rose after the shock | D | Mostly rejected |
| H7 | Measurement and issuance mechanics (source disagreement, treasury inventory moves) | 0.05 | 0.15 | CoinGecko vs DefiLlama on the same days | Sources agree to the dollar | D | Live: sources differ by about $1B |
| H8 | Quantum hardening or L2 sequencer risk | 0.05 | 0.02 | Chain breakdown; ETF flows | L2 balances fall | D, S | Rejected |
| H9 | Solana rotation and memecoin exit liquidity | 0.20 | 0.05 | Solana stablecoin totals | Solana stablecoins rise | D | Rejected |
| H10 | Iran war | 0.20 | 0.02 | War start Feb 28 vs drop | Drop after Feb 28 | S | Rejected |
| H11 | Sanctions (OFAC) | 0.10 | 0.03 | Jan 30 designation details | Action targets USDC | P | Rejected |
| H12 | Foreign official retreat, US rating downgrade | 0.15 | 0.04 | Treasury TIC January data | Net foreign selling in January | P | Rejected (net buyers) |
| H13 | Credit or private-credit stress | 0.15 | 0.03 | HY and IG spreads in January | Spreads widen before the drop | D | Rejected (near year lows) |
| H14 | Custodian rehypothecation or gating | 0.15 | 0.05 | Custodian disclosures | A freeze or gating notice | S | No evidence |
| H15 | EU DAC8 reporting-driven redemptions | 0.10 | 0.08 | Mechanics; EU redemption data | n/a | S | Untestable (no data) |
| H16 | Hacks and physical attacks | 0.05 | 0.02 | CertiK January totals | Stolen funds mostly USDC | S | Rejected (scale, mechanics) |
| H17 | Consumer liquidity and confidence | 0.05 | 0.02 | UMich sentiment, saving rate in January | Confidence collapse in January | D | Rejected (best month of year) |
| H20 | Hedge fund shorts or basis trades collateralized in stablecoins | 0.10 | 0.07 | CFTC leveraged-fund positions; margin type; Hyperliquid funding | Shorts hold USDC and redeem it | P, D | CME shorts are cash and bill margined; USDC margin is locked, not burned; funding flip on Jan 20 supports the long-unwind reading of H2 |
| H21 | Rebalance into gold or tokenized gold | 0.10 | 0.04 | Tokenized gold supply, Jan 15 to 31 | Large tokenized gold mints | D | About $0.25B, and gold was at its record, not at a discount |
| H19 | Circle IPO lockup expiry let institutional holders exit | 0.10 | 0.03 | Lockup dates against supply; equity versus stablecoin mechanics | A tie between equity sales and USDC burns | S | Rejected: equity proceeds are dollars, and the date is six weeks early |
| H18 | Rate incentive (bill yield vs 0% on USDC) | 0.20 | 0.08 for January, 0.35 for the drift since March | Weekly yield-change correlation (-0.25, n=47) | Zero relationship | D | Not January; plausible drift |

## B. How my beliefs moved, in the order I tested

| Step | Test | Result | Beliefs that moved |
|---|---|---|---|
| 0 | Starting position: the published thesis | USDC drop read as forced selling after the SEC statement | H1 0.55 |
| 1 | Read the SEC Jan 28 text (two independent reads) | No mention of Treasury bills, liquid staking, wstETH or wrappers | H1 0.55 to 0.15 |
| 2 | DefiLlama series against the "$80B" baseline | December level was $75B to $77B; back to $75.2B by Feb 28; $79.6B on Mar 17 | H1 0.15 to 0.10; the move was transient |
| 3 | Supply by chain | Outflow on Ethereum and Solana; Base, Arbitrum flat or up | H8 0.05 to 0.02 |
| 4 | Iran war dates | War began Feb 28; the largest drops are six weeks earlier; USDC rose in the first weeks | H10 0.20 to 0.02 |
| 5 | Solana stablecoin totals | Solana lost $2.25B of USDC and $1.5B in total | H9 0.20 to 0.05 |
| 6 | OFAC | Jan 30 designation targeted USDT on Tron, the day after the drop | H11 0.10 to 0.03 |
| 7 | Credit spreads, TIC | HY 2.73 and IG 0.75 on Jan 20; foreigners net buyers $63.5B | H13 to 0.03, H12 to 0.04 |
| 8 | Q4 lag test | Oct 10 and Stream hit USDe (14.8B to 6.3B); USDC rose; January liquidations land on the drop days | H6 0.20 to 0.10; H2 0.20 to 0.50 |
| 9 | Rates, FX, BTC correlations | Nothing clears a multiple-comparison bar | H18 0.20 to 0.08 for January |
| 10 | Tokenized Treasuries, BNY | USDY +$0.65B and USYC +$0.12B in the second half of January; BNY launch Jan 9, size unknown | H4 0.10 to 0.20; H5 0.10 to 0.15 |
| 11 | Second data source | CoinGecko and DefiLlama disagree by about $1B on some days (Jan 15: 75.7 vs 76.7) | H7 0.05 to 0.15 |

## C. Leading, lagging and quiet signals

| Type | Signal | Date | Reading |
|---|---|---|---|
| Leading | CLARITY draft (Jan 12), Coinbase withdraws support (Jan 14) | Jan 12 to 14 | Legislative risk rising before the drop; weak link |
| Leading, quiet | USDC, bitcoin and SOL all peaked on Jan 15 to 16 (BTC $96.9K, SOL $146.5K, USDC $76.7B to $77.1B) | Jan 15 to 16 | Supply turned with the crypto cycle at its peak: the strongest clue for H2 and H3 |
| Leading, quiet | USDY began rising (0.74 to 1.39B) from Jan 15, two weeks before the low | Jan 15 to 31 | Early rotation into tokenized Treasuries |
| Coincident | Jan 20 tariff threats, record JGB yields, $1.09B liquidated; USDC -$1.9B (DefiLlama) | Jan 20 | Macro plus deleveraging |
| Coincident | Hyperliquid BTC funding flips from about +11% to -8% annualised on Jan 20; returns to about +10% by Jan 28 | Jan 20 | Long-crowding unwind on the largest USDC drop day (supports H2) |
| Coincident | Bitcoin leads USDC by about one day in January (corr +0.33); January daily corr +0.28 to +0.60 depending on source; reversed in February | Jan | Supply followed leveraged-long appetite in January, then acted as a safe haven |
| Coincident | ETH ETF week of Jan 19 to 23: -$611M | Jan 23 | Risk-off in institutional flow |
| Coincident | Jan 29: gold record, SEC and CFTC joint event, Senate Agriculture vote, USDC -$1.0B | Jan 29 | Clustered events; correlation only |
| Coincident | VIX pulse to 20.1 on Jan 20, back to 16.9 next day; DVOL flat near 40 through January | Jan 20 | Macro pulse in a quiet-volatility, long-crowded regime; USDC dip lasted two weeks |
| Lagging, quiet | DVOL 82.6 on Feb 5, bitcoin $62.8K Feb 6; USDC +$2.0B on Feb 6 and +$2.5B over the next week | Feb 5 to 13 | Inflows came with the volatility spike: supply as safe haven, the reverse of January |
| Lagging | Aave liquidations $429M | Jan 31 to Feb 5 | Deleveraging continued after the supply low |
| Lagging | USDC +$5.2B in February; USDe flat | Feb | Transient, no structural exit |
| Lagging | Circle Q4 call (Feb 25) and 10-K | Feb 25 | Silent on January; 10-K gives year-end only |

## D. Orthogonal echoes (cross-domain shape matches)

DefiLlama USDC supply, peak to trough, then days to regain 95% of the prior peak:

| Episode | Peak to trough | Days down | Days to 95% after trough | Cause class |
|---|---|---|---|---|
| March 2023 (Silicon Valley Bank) | -26.9% | 39 | none in window | Trust and reserve shock |
| November 2025 (Stream collapse) | -2.9% | 10 | 1 | DeFi lending contagion |
| January 2026 | -9.2% | 14 | 12 | Unattributed |
| June to July 2026 | -2.7% | 20 | 1 | War-era drift |

- January's V-shape (sharp, two weeks down, back to 95% within 12 days) looks like a liquidity-demand episode, not a solvency or trust shock like 2023. That favors H2 and H3 over H1 and H14.
- Echoes from other domains, not verified in this pass: the March 2020 "dash for cash" in money funds and gold (assets sold for liquidity, then reversed on a backstop); the April 2025 swap-spread unwind of about $60B (leveraged relative-value unwinding, S); the March 2026 gold sell-off, which one source called liquidity-driven. All three have the same shape: a short cash-raising shock in a leveraged system, with supply restored once the pressure passes.
- VIX and DVOL echo: volatility indices revert half-way in about one day; USDC supply is the slow stock (12 days to 95%). January's pattern (low volatility, crowded longs, pulse, slow rebuild) matches carry-unwind episodes such as August 2024; February's (volatility spike, inflows) is the safe-haven leg.
- Echo in your own record: the Apple "Closing the Loop" piece had one falsifier fire against its own number (the 48.7% margin typo). Here the same class of error is the $80B USDC baseline.

## E. Hard cutoff dates for reporting and disclosure

| Date | What | What it could reveal | Status |
|---|---|---|---|
| Aug 13 and Dec 2, 2025 | Circle IPO lockup: JPMorgan-led early release of 11.5M shares (Aug 13); standard 180-day expiry Dec 2 | Insider and institutional equity selling (tens of millions of dollars in the 90 days before) | Checked: equity flow, not USDC mint or burn |
| Jan 1, 2026 | EU DAC8 applies; platforms must collect tax IDs | Whether EU users were forced to redeem | Dated, effect untested |
| About Mar 1, 2026 | Earliest 60-day block on non-compliant EU accounts | Same | Derived from the rule, S |
| Jan 9, 2026 | BNY tokenized deposit service live | Collateral migration | Volume not disclosed |
| Feb 25, 2026 | Circle Q4 results; 10-K filed about the same time | Intra-quarter circulation | Checked: silent |
| About Feb 14 and May 15 | 13F deadlines (45 days after quarter end) | ETF and fund holders of crypto assets | Not pulled |
| Mid-March (January data), mid-April (February) | Treasury TIC release | Foreign flows | Checked for January and February |
| Early Nov 2026 | Circle Q3 results (date not confirmed) | Q3 composition, redemption commentary | Open |
| Late 2026 | Basel update on the crypto standard | Bank appetite for collateral | Open |
| Jul 18, 2026 (statutory) | GENIUS Act final rules deadline | Reserve and redemption rules | Not confirmed published |
| Jan 18, 2027 | GENIUS effective date (stated as January 2027 by one source) | Compliance cutoff for issuers | S |
| Sep 30, 2027 | First DAC8 reporting exchange | Total reportable EU flows | Future |
| Not published | Circle redeemer counterparties | The direct answer | Does not exist publicly |

## F. What would move beliefs next (cheapest first)

1. Circle's Q3 2026 call: any commentary naming January or an institutional redeemer would raise H5 or H7. Direction: either.
2. Exchange-level USDC balances (CryptoQuant, Glassnode) for Jan 15 to 31: a drop on Binance, OKX or Coinbase would raise H2. A drop in DeFi pools would raise H4.
3. Per-day mint and burn data from Circle's public chain addresses: would settle H7 and show whether the drop was a few large redemptions or many small ones.
4. BNY or JPM disclosures of tokenized deposit volume: would size H5.
5. Jan 26 to 30 ETH ETF flows: would test H2's institutional leg.

## G. Limits

Search summaries stand behind several figures (marked S). Credences are mine. The unattributed finding stands because the decisive data, the identity of redeemers, is not public.
