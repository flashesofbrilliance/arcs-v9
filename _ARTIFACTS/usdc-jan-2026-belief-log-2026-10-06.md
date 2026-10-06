# Belief log: what moved USDC in January 2026

Question: why did USDC supply fall about $5.7B to $6.6B between Jan 15 and Jan 31, 2026, then recover? Two published pieces (Custody Collateral, Flippening) treated it as forced institutional liquidation after the SEC's Jan 28 statement.

How to read this: a credence is my subjective probability that a factor was a material contributor (more than about 10%) to the January move. Credences do not sum to one, because factors overlap. They are calibration aids, not measurements. Evidence class: **P** primary page or filing, **D** public data series pulled directly (DefiLlama, CoinGecko, FRED), **S** secondary reporting or search summary.

## A. Hypotheses, priors and where they ended

| ID | Hypothesis | Prior | Now | Deciding test | Falsifier | Evidence | Status |
|---|---|---|---|---|---|---|---|
| H1 | Regulation-forced institutional liquidation after the SEC Jan 28 statement | 0.55 | 0.05 | Word search of the statement; agency posture timeline | The statement names wstETH, T-bills or wrappers | P | Premise failed |
| H2 | Same-day deleveraging (Jan 20 and Jan 30 liquidations) | 0.20 | 0.50 | Largest USDC daily drops against liquidation dates | Drops with no liquidation event | S, D | Best fit, inference |
| H3 | Macro risk-off (tariff threats, record JGB yields, yen +3% Jan 20 to 29) | 0.15 | 0.35 | Event dates against drop dates; USD/JPY series | Drop precedes the shocks | S, D | Plausible, overlaps H2. Unusual Whales (X) posted Treasury Secretary Bessent on Jan 20: Japan's ten-year bond had a six-standard-deviation move over two days, and the selloff "has nothing to do with Greenland" |
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
| H22 | Year-end private fund and BDC redemption payouts landing in January | 0.10 | 0.12 | BDC tender caps; crypto fund performance; typical notice and payout lags | A payout schedule that misses mid to late January | S | Plausible, untested: BDC requests ran near or above the 5% cap in Q4 2025, crypto hedge funds fell about 23% in 2025 |
| H23 | Gemini or Genesis ruling and settlement fallout | 0.05 | 0.02 | Case dates | A 2026 adverse ruling | S | Rejected: SEC dismissed its Gemini case on Jan 23, 2026 (pro-industry); Genesis repaid in kind in 2024 |
| H24 | CBDC and e-CNY pushes (digital euro, interest-bearing e-CNY from Jan 1, mBridge) | 0.05 | 0.01 | Timing and scope | A USD-denominated effect | S | Rejected for USDC; matters for EURC and long-run settlement |
| H25 | Reserve-currency diversification away from the dollar | 0.10 | 0.03 | IMF COFER, central bank gold buying | A fall in the dollar share around January | S | Rejected: dollar share about 56.4% (Q4 2025) to about 57% (Q1 2026), diversification favours gold |
| H26 | Collateral repricing (ETH and LST drawdown) forcing repayment or burns of stablecoins borrowed against it | 0.15 | 0.04 | DAI+USDS and USDe supply against ETH daily returns | Collateral-backed stablecoin supply falls with ETH | D | Rejected: DAI+USDS flat at $10.9B from Jan 15 to Jan 31 and +$0.9B in February while ETH fell 19% then 46%; USDe flat; correlations +0.08 and +0.18 full year |
| H27 | Exchange incentive campaign pulling balances from USDC into USD1 (Binance USD1 rewards from Jan 23) | 0.05 | 0.40 | USD1 daily supply against USDC, Jan 22 to 31 | USD1 flat on Jan 23 to 25 | D, S | Strong timing: USD1 +$1.12B on Jan 23 and +$1.76B in three days; USDC -$3.55B (DefiLlama) or -$4.39B (CoinGecko) Jan 22 to 31, so USD1 equals about 43% to 53% of the second leg; the first leg (Jan 15 to 22) still fits H2 and H3. Not shown: that USD1 mints were funded by USDC redemptions |
| H28 | Whale liquidations triggering panic selling | 0.15 | 0.05 | Whale liquidation reports against daily USDC drops | Large long liquidations on the drop days that fed redemptions | S | Mostly short-side or small: a large short whale was liquidated for about $199M on Jan 22 and $120M on Jan 26 (forced buying); a $222.65M ETH long liquidation looks like early February (date not verified); a 200 BTC panic sale ($16.9M) on Jan 29 |
| H29 | Synthetic-dollar depeg contagion (Falcon USDf slipped to $0.9871 on Jan 29) | 0.10 | 0.05 | USDf price deviation against USDC daily change (backtest, 364 days) | A relationship between deviation and USDC supply change | D, S | Backtest: correlation of absolute USDf deviation with USDC daily dollar change -0.00 (n=364), -0.05 in January (n=31). The Jan 29 low was not the deepest: daily-average prices were $0.983 on Jan 1 and $0.9752 on Mar 12. USDf's own supply held at $2.17B through Jan 29 then fell to $2.04B by Feb 3 and $1.64B by Feb 10 (a lead of about four days on USDf's own redemptions, not on USDC). No cause was stated for Jan 29; the LlamaRisk collateral concerns belong to a separate depeg on Jul 8, 2025 (low $0.9783, market cap $540M). No listed options exist on stablecoins; no priced depeg instrument for USDf found (candidate sources: Pendle PT/YT implied yields on sUSDf, on-chain cover pricing, prediction markets) |
| H30 | Early-holder and insider wallet movements (Satoshi-era, Vitalik, Ethereum Foundation, Lubin-linked) | 0.05 | 0.03 | On-chain movement reports against drop dates and sizes | Movements of billions into exchanges or stablecoin redemptions | S | Too small and mostly stablecoin-neutral: a Satoshi-era wallet moved about 2,000 BTC (about $180M) to Coinbase in January; Vitalik sold about $30M of ETH (17,196 ETH, about 7% of holdings) in January and early February via CoW Protocol; Ethereum Foundation sales and a Lubin-linked top-up of 110,000 ETH as Sky collateral came later (April to June) |
| H31 | Tron flows and Justin Sun's dispute with World Liberty | 0.05 | 0.02 | Tron stablecoin supply Jan 15 to 31; dates of Sun's actions | Tron USDC moves or Sun actions in January | D, S | Tron stablecoins rose $1.36B (USDT +$1.24B) from Jan 15 to Jan 31; USDC on Tron is only about $0.04B. Sun's USD1 actions were earlier (May 2025 Tron integration; Sept 2025 WLFI froze his tokens) or later (Apr 12, 2026 public criticism; Apr 21, 2026 lawsuit alleging pressure to mint and promote USD1) |
| H32 | Maturity of Pendle USDf and sUSDf markets on Jan 29 (PT redemption pressure) | 0.05 | 0.10 | Pendle implied APY and TVL history for the two markets that expired on 2026-01-29 | Flat implied APY and stable TVL into expiry | D | Both markets matured on the day of the USDf low. Implied APY rose before expiry: USDf PT 9.2% (Jan 13) to 13.1% (Jan 26) to 17.0% (Jan 27); sUSDf PT 8.3% (Jan 13) to 8.6% (Jan 25) to 13.0% (Jan 26) and 13.3% (Jan 27). TVL tiny ($1.1M to $1.3M and $17M to $20M against USDf supply of $2B). Near-expiry implied APY is hypersensitive to small price moves, so this is weak evidence; a plausible mechanical contributor to the Jan 29 dip in USDf, not to USDC |
| H33 | CLARITY yield-fight escalation (White House threat on Jan 17, Coinbase and bank feud) | 0.10 | 0.15 | Dated policy posts against the Jan 20 drop | No escalation before Jan 20 | S | Unusual Whales (X): Jan 17, the White House considering pulling support for the market-structure bill if Coinbase does not return with a yield agreement; Jan 19, Brian Armstrong says banks are protecting their margins; Jan 30, Jamie Dimon tells Armstrong he is "full of" expletive (Bloomberg). Coincides with the Jan 20 drop but is entangled with the macro pulse |
| H34 | Warsh nomination as a liquidity shock (Jan 30) | 0.05 | 0.10 | Market reaction on Jan 30 to Feb 1 | No reaction | S, D | Trump named Kevin Warsh on Jan 30 (Truth Social, about 11:53 UTC); reports describe silver down about 30% in one session, gold down 9% to 12% from its record, the dollar up and bitcoin under $79,000 by Jan 31. USDC moved little (-$0.24B Jan 30, +$0.07B Jan 31), so it hit risk assets more than the stablecoin float; the Jan 29 drop preceded the announcement |
| H35 | Hardware-wallet attacks and accounting, audit or reporting rule changes | 0.10 | 0.04 | Dated rule changes and incident reports against the drop | Rule changes or incidents that force redemptions in January | S | Hardware wallets: the Jan 10 theft of about $282M (BTC and LTC) came from Trezor-impersonation social engineering, not a device flaw; in late January Ledger's Donjon disclosed a laser-fault-injection weakness in the TROPIC01 secure element used in Trezor Safe 7 (needs physical access and lab equipment); a Coldcard flaw is also reported in a $38M bitcoin theft (date not verified). Rules: Basel crypto standard (effective Jan 1, 2026), EU DAC8 and US 1099-DA reporting (Jan 1, 2026) are in force at the start of the month; FASB tentatively decided on Apr 15 and proposed on Aug 18, 2026 to let stablecoins qualify as cash equivalents if the holder has an on-demand redemption right with the issuer (comments due Nov 19, 2026), which is later and favors USDC; SEC net-capital FAQ of Feb 19 (2% haircut). None forces January redemptions |
| H36 | Coinbase fee or reward changes, gas savings or L2 incentives driving USDC out of Ethereum | 0.10 | 0.04 | Fee and rewards changes; gas levels; USDC by chain | A promotion or fee change in January; USDC rising on L2s | S, D | No Coinbase USDC to USD fee promotion found for January. Coinbase One USDC rewards were cut from 3.75% to 3.5% on Feb 19, after January. Ethereum transfers cost about $0.01 in January and daily transactions hit a record on Jan 16 (2,885,524), so gas was not a motive; bridging to an L2 would conserve total supply, and USDC on Base (about $4.2B to $4.3B) and Arbitrum was flat or up while Ethereum (-$3.6B) and Solana (-$2.0B) fell |
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
| Coincident | Binance announces a USD1 holding-rewards campaign on Jan 23 ($40M WLFI airdrop to USD1 holders on Binance, Jan 23 to Feb 20); USD1 +$1.12B on Jan 23, +$0.43B Jan 24, +$0.21B Jan 25 (3.17B to 4.93B) | Jan 23 to 25 | USDC fell $1.1B to $1.6B over Jan 23 and 24, roughly 1:1 with USD1: the clearest incentive-driven migration clue so far |
| Leading, quiet | Monero: a hardware-wallet social-engineering theft of about $282M (BTC and LTC) on Jan 10 at 23:00 UTC was converted into XMR; XMR rose from $440 (Jan 11) to $706 (Jan 15), its local top (CoinGecko daily; $799.89 intraday high reported Jan 14), then $459 on Jan 29 and $335 by Feb 28; privacy coins rallied broadly and the SEC closed its Zcash Foundation probe in January | Jan 10 to 15 | A froth signature peaking on the same days as BTC (Jan 15), SOL (Jan 15) and USDC (Jan 16); the theft itself is too small to move USDC |
| Leading | Jan 16 Trump threatens tariffs over Greenland; Jan 17 the EU reportedly moves to suspend its trade deal with the US (Bloomberg); Jan 17 White House weighs pulling support for CLARITY unless Coinbase agrees a yield deal; Jan 19 Armstrong's reply (all via Unusual Whales on X) | Jan 16 to 19 | A policy and trade-shock sequence in the four days before the Jan 20 drop |
| Coincident | Jan 20 Bessent attributes the selloff to a six-standard-deviation move in Japan's ten-year bond; Democrats call for the 25th Amendment over Greenland; Jan 21 Davos: Trump rules out force, NATO and US Greenland framework follows on Jan 21 to 22, a 10% credit-card cap is floated, and he says a new Fed chair will be announced and he is working on crypto regulation | Jan 20 to 22 | Macro pulse and reversal: VIX 20.1 on Jan 20, 16.9 on Jan 21; USDC fell $1.9B on Jan 20 and kept drifting |
| Coincident | Jan 29 Trump announces a 50% tariff on Canadian aircraft; Jan 30 Warsh named Fed chair (silver -30% in a session, gold -9% to -12%, dollar up, bitcoin under $79K); Jan 31 Bloomberg: Strategy's full bitcoin position turned negative below $76,000 | Jan 29 to 31 | The second leg overlaps the Warsh liquidity shock and the Binance USD1 campaign |
| Coincident | Unusual Whales (X) posted on Feb 1 that an Abu Dhabi royal backed a secret $500M investment in World Liberty Financial four days before the inauguration, citing the WSJ (not verified against the WSJ); only the first screen of its Jan 14 to Feb 1 posts was read | Jan 31 to Feb 1 | Adds UAE and Abu Dhabi context to the USD1 story (MGX paid $2B to Binance in USD1 in 2025); no direct flow link |
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
| Dec 31, 2025 | Typical annual redemption date for private and crypto funds (notice 30 to 90 days earlier, payouts 30 to 60 days after, so mid-January to early March); not sourced for specific funds | Redemption payouts in the January window | Plausible, untested |
| Jan 1, 2026 | China's e-CNY becomes interest-bearing; Jan 16: mBridge reported above $55B cumulative | Digital yuan push | No USDC link found |
| Jan 23, 2026 | SEC dismisses its Gemini case | Regulatory loosening during the outflow week | Opposite direction |
| Mar 19, Jun 23 and Jul 9, 2026; end of 2026 | Digital euro: Council position, ECON vote, plenary mandate, legislation target | EURC exposure | Open |
| Late 2026 | Bank of England digital pound decision | Sterling rail | Open |
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

## H. Additions after the first commit

- 12-month net issuance (DefiLlama, month-end): USDC +$0.7B over 12 months, January -$5.2B its worst month; 13 major coins -$3.5B in January but -$7.3B in June and -$4.2B in July; USDe -$9.8B; USDT +$9.3B. January was a sharp USDC event; the larger contractions were slower and later.
- rwa.xyz (page and charts read directly; history and longer periods are login-gated): tokenized Treasuries $14.88B (-6.3% in 30 days), 30-day net flows USDC -$871M, BUIDL -$569M, USYC -$224M against USDe +$617M and USDS +$432M; custodians (BitGo, Anchorage, Paxos) now issue about $7B of stablecoins; pockets of stress in municipal credit and specialty finance. Relevant to H4 (rotation into tokenized Treasuries did not hold for September) and to the institutional-contraction reading of H18.
- Tokenized gold (H21): $0.25B in the Jan 15 to 31 window; short positioning (H20): CME leveraged-fund shorts rose about 3.1K contracts into Jan 20, a basis trade; Hyperliquid BTC funding flipped from about +11% to -8% on Jan 20.
- Bitcoin and volatility: January daily correlation of bitcoin returns with USDC change +0.28 to +0.60 depending on source; VIX pulse Jan 20; DVOL about 40 in January and 82.6 on Feb 5 with USDC +$2.0B on Feb 6.
- China and reserves (H24, H25): e-CNY interest-bearing from Jan 1, 2026; 3.4B transactions worth about 16.7T yuan; mBridge cumulative above $55B with the digital yuan above 95%; Shanghai international operations center since Sept 2025 and 26 institutions signed Jun 16. IMF COFER dollar share about 56.4% (Q4 2025), about 57.1% (Q1 2026, about half valuation), about 56.7% (Q2 2026). Central banks bought gold: Poland 82t, Uzbekistan 41t, China 40t, Kazakhstan 27t in H1; 74% of surveyed central banks expect a lower dollar share in five years. Diversification favours gold more than the renminbi.
- China as a Treasury seller (Feb to Jul 2026, -$77B) is a separate, later event from January.

- Accounting and reporting cutoffs (H35): Jan 1, 2026 Basel crypto standard, EU DAC8 and US 1099-DA reporting apply; Feb 19 SEC broker-dealer net-capital FAQ; Apr 15 FASB tentative decision and Aug 18 proposed ASU on stablecoins as cash equivalents, comments due Nov 19, 2026 (a later tailwind for USDC as a corporate treasury asset).
- Whales and wallets (H28 to H30, search-sourced): a short whale ("Air Force Commander", nearly $500M of shorts) liquidated for about $199M on Jan 22 and $120M on Jan 26; Falcon USDf at $0.9871 on Jan 29; a Satoshi-era wallet moved 2,000 BTC (about $180M) to Coinbase in January (other Satoshi-era wallets moved 20 BTC in May and 600 BTC in September; Galaxy Research says the May wallet is not Satoshi's); Vitalik Buterin sold about $30M of ETH (17,196 ETH) in January and early February; the Ethereum Foundation sold ETH in April to July; a Joseph Lubin-linked wallet moved 110,000 ETH ($170.8M) as extra Sky collateral on about Jun 6, with ETH under $1,600, to defend a $259M DAI debt, and another wallet moved 133,298 ETH ($356M) at an undated point. The Lubin-linked top-up is a live example of a borrower posting more collateral instead of selling. Background only: the Bybit hack was on Feb 21, 2025, about $1.4B to $1.5B of ETH (Lazarus Group); a Bybit keynote on Jan 29, 2026 was a roadmap talk with no linked market event.

## F. What would move beliefs next (cheapest first)

1. Circle's Q3 2026 call: any commentary naming January or an institutional redeemer would raise H5 or H7. Direction: either.
2. Exchange-level USDC balances (CryptoQuant, Glassnode) for Jan 15 to 31: a drop on Binance, OKX or Coinbase would raise H2. A drop in DeFi pools would raise H4.
3. Per-day mint and burn data from Circle's public chain addresses: would settle H7 and show whether the drop was a few large redemptions or many small ones.
4. BNY or JPM disclosures of tokenized deposit volume: would size H5.
5. Jan 26 to 30 ETH ETF flows: would test H2's institutional leg.

## G. Limits

Search summaries stand behind several figures (marked S). Credences are mine. The unattributed finding stands because the decisive data, the identity of redeemers, is not public.
