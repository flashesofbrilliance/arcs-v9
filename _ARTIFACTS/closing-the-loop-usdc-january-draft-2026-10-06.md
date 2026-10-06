# Closing the Loop, Part 2: What Moved USDC in January 2026

USD Coin (USDC), Circle's dollar stablecoin, lost about $5.7B to $6.6B of supply between Jan 15 and Jan 31, 2026. Two of my earlier pieces called it forced institutional liquidation. Here is every test I ran on public data, what each hypothesis scored, and which tests came back empty.

> **Field Account · LinkedRecord: Part 2 · Open on purpose**
> *Draft for review, not published · Tests pre-registered before the data was pulled · Priors written down before they moved · Corrections owned in full*

---

### I · Where Part 1 left this

Part 1 graded seven dated calls against their published falsifiers. One thread stayed open: why USDC supply fell in January. Two of my pieces said the cause was forced selling after the Securities and Exchange Commission (SEC) staff statement of Jan 28. I could not confirm that, and I said so. This post is the full accounting of the attempt, with the numbers it rests on.

The short version: the thesis I published scored lowest of anything I tested. The best-supported reading is two overlapping legs, and the decisive test needs data that is not public.

---

### II · The method

Three rules, set before the data came in.

1. **Pre-registered tests.** Each hypothesis got a deciding test and a falsifier, written down before I pulled the series. If the falsifier showed up, the hypothesis dropped.
2. **A belief log with priors.** A credence is my subjective probability that a factor contributed more than about 10% of the January move. Credences overlap, so they do not sum to one. They are calibration aids, not measurements. Every row records the prior, the final value and the evidence class: primary page or filing (P), public data series pulled directly (D), or secondary reporting (S).
3. **Silence counts as evidence only for required routine disclosures.** If a filing must mention something, mentioning nothing is information. If the party is under inquiry or legally advised, silence is close to no information. Circle's 10-K, for example, reports year-end only, so its silence on January tells me nothing.

---

### III · The calls

**Feb 1 and Feb 2, 2026.** "Flippening, Not Gonna Happen" and "Custody Collateral" read the January outflow as institutions dumping stablecoins after the SEC statement. The Flippening piece set a falsifier: USDC supply returns to its December level.

Nothing below was rewritten after the fact.

---

### IV · What each hypothesis scored

Prior is what I believed before testing. Final is where it ended. Only the hypotheses that moved most, or that carry the story, are in this table; the full log has more rows.

| ID | Hypothesis | Prior | Final | Deciding test | Evidence | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| H1 | Regulation-forced liquidation after the SEC Jan 28 statement | 0.55 | 0.05 | Word search of the statement | P | **Premise failed** |
| H2 | Same-day deleveraging of crowded longs (Jan 20, Jan 30) | 0.20 | 0.50 | Largest USDC daily drops against liquidation dates | S, D | **Best fit, inference** |
| H27 | Binance rewards campaign pulling balances from USDC into USD1 | 0.05 | 0.40 | USD1 daily supply against USDC, Jan 22 to 31 | D, S | **Strong timing, mechanism unshown** |
| H3 | Macro risk-off (tariff threats, record Japanese bond yields, yen) | 0.15 | 0.35 | Event dates against drop dates; USD/JPY series | S, D | Plausible, overlaps H2 |
| H4 | Rotation into tokenized Treasuries | 0.10 | 0.20 | USDY, USYC, BUIDL supply | D | Real but small |
| H5 | Migration to bank deposit tokens | 0.10 | 0.15 | BNY and JPMorgan disclosures | P, S | Size unknown |
| H7 | Measurement and issuance mechanics | 0.05 | 0.15 | CoinGecko against DefiLlama, same days | D | Live: the sources differ |
| H22 | Year-end fund redemption payouts landing in January | 0.10 | 0.12 | Payout schedules, tender caps | S | Plausible, untested |
| H6 | Lagged fallout from the Oct 10 cascade and Q4 DeFi lending collapses | 0.20 | 0.10 | USDC and USDe paths, Oct to Jan | D | Mostly rejected |
| H9 | Solana rotation and memecoin exit liquidity | 0.20 | 0.05 | Solana stablecoin totals | D | Rejected |
| H10 | The Iran war | 0.20 | 0.02 | War start date against drop dates | S | Rejected |
| H18 | Rate incentive (bill yield against 0% on USDC) | 0.20 | 0.08 for January | Weekly yield-change correlation | D | Not January; plausible drift since March |

**How the first number moved.** Step one was reading the SEC text twice. It names no Treasury bills, no liquid staking tokens and no wrappers. H1 went from 0.55 to 0.15 on that alone, then to 0.05 once the December baseline and the recovery were measured. The published thesis lost most of its weight in the first test.

---

### V · The two-leg reading

This is the best-supported story. It is still inference.

**Leg one, Jan 15 to 22 (about -$3.1B).** USDC, bitcoin and Solana all peaked on Jan 15 to 16, so supply turned with the crypto cycle at its high. Then came a cluster on Jan 20: Greenland tariff threats, record Japanese government bond yields, about $1.09B of liquidations (secondary reporting), and USDC down $1.9B on the day, one of its two largest daily drops in the DefiLlama series. Hyperliquid's bitcoin funding rate flipped from about +11% to -8% annualized that day, which reads as crowded longs unwinding. USD/JPY fell about 3% between Jan 20 and Jan 29. On the policy side, the Senate CLARITY Act draft appeared on Jan 12 and Coinbase withdrew its support on Jan 14, before the drop. That is a weak link, not a trigger.

Bitcoin led USDC supply by about one day in January and the relationship reversed in February, when the Feb 5 volatility spike came with USDC inflows. January supply followed crowded-long appetite. February supply behaved like a safe haven.

**Leg two, Jan 22 to 31.** On Jan 23 Binance launched a holding-rewards campaign for World Liberty Financial's USD1 stablecoin: $40M of WLFI tokens to USD1 holders on Binance, Jan 23 to Feb 20 (secondary reporting). USD1 supply went from $3.17B to $4.93B in three days, with $1.12B on Jan 23 alone. From Jan 22 to Jan 31 USD1 gained $1.89B while USDC fell $3.55B (DefiLlama) or $4.39B (CoinGecko). That is about 43% to 53% of the second leg. The Jan 30 liquidation day (about $1.71B, secondary) and the Warsh Fed chair nomination, also Jan 30, sit inside this window. I did not score the nomination: no hypothesis row exists for it, and I have not re-verified the date outside my own session notes, so treat it as a co-occurring event, not a tested cause.

**The V-shape.** Peak to trough, January 2026 was -9.2% over 14 days, and USDC regained 95% of its prior peak 12 days after the trough. Other episodes in the same series:

| Episode | Peak to trough | Days down | Days to 95% after trough | Cause class |
| :--- | :--- | :--- | :--- | :--- |
| March 2023, Silicon Valley Bank | -26.9% | 39 | none in window | Trust and reserve shock |
| November 2025, Stream collapse | -2.9% | 10 | 1 | DeFi lending contagion |
| January 2026 | -9.2% | 14 | 12 | Unattributed |

A fast V is how a liquidity-demand episode looks. A trust shock, like 2023, does not rebound that way. That favors H2 and H3 over H1.

---

### VI · What would settle it

The decisive question is whether the USD1 mints were funded by USDC redemptions. Public data cannot answer it. Two things could:

1. **Entity-level USDC burns.** Circle does not publish who redeemed. A coin in a cold wallet, a frozen vault or a hacked address is still in circulation, so supply falls only when someone redeems with the issuer. A list of burns by entity (from a paid on-chain analytics vendor) would show whether the drop was a few large redemptions or many small ones.
2. **Binance conversion data.** Exchange-level USDC balances for Jan 15 to 31, or the Binance conversion record for the campaign window, would show whether holders swapped USDC into USD1. A fall in USDC on Binance, OKX or Coinbase raises H2. A fall in DeFi pools raises H4.

Cheaper signals, in order: Circle's Q3 2026 call, if it names January or a redeemer; per-day mint and burn data from Circle's public chain addresses; BNY and JPMorgan tokenized-deposit volume disclosures.

---

### VII · The tests that came back empty

Each of these had a falsifier. Each failed to find its effect. Empty is a result, and it is how the list of live causes got short.

- **SEC statement names the assets (H1).** It names none.
- **Delayed October cascade (H6).** That event hit USDe, not USDC, and USDC rose afterward.
- **Solana rotation (H9).** Solana lost USDC too: about $2.25B of USDC.
- **The Iran war (H10).** It began Feb 28, six weeks after the largest drops.
- **Sanctions (H11).** The Jan 30 designation targeted USDT on Tron, a day after the drop.
- **Foreign official selling of Treasuries (H12).** Foreigners were net buyers in January: $63.5B.
- **Credit stress (H13).** Spreads sat near year lows.
- **Custodian gating (H14).** No freeze or gating notice found.
- **Hacks (H16).** About $370M stolen in January, and most of it not in USDC.
- **Consumer confidence (H17).** Sentiment was at its best month of the year.
- **Collateral repricing (H26).** DAI plus USDS stayed flat at $10.9B from Jan 15 to Jan 31 while ether fell.
- **Tokenized gold (H21).** About $0.25B, and gold was at a record, not a discount.
- **Hedge fund shorts (H20).** Cash and bill margined. USDC margin is locked, not burned.
- **Circle IPO lockup (H19).** Equity proceeds are dollars, and the expiry was six weeks early.
- **Gemini and Genesis fallout (H23).** The SEC dismissed its Gemini case Jan 23, which points the wrong way.
- **Reserve diversification (H25).** The dollar share of reserves did not fall around January.
- **Weekly correlations.** Supply against bitcoin, bill yields, spreads, the dollar, yen and curve slope never cleared a multiple-comparison bar. I ran more than a dozen of these, so a couple of borderline hits are what chance supplies.

Untestable, not empty: the European Union's DAC8 tax-reporting rules (H15). There is no redemption data to test against.

---

### VIII · Corrections owned

**The December baseline.** My Flippening piece set the falsifier at about $80B. The real December level was $75B to $77B. USDC closed 2025 at $75.3B and was back to $75.2B by Feb 28, so my own falsifier fired. My first draft of Part 1 missed it by reading a September snapshot.

**The SEC premise.** The central premise of two pieces failed on a read of the primary text. H1 is the row that records it.

**Two sources, one move.** DefiLlama and CoinGecko disagree by about $1B on some days, and CoinGecko's daily points are 00:00 UTC snapshots, one day offset from events. Part of the size of the move may be measurement. That is why the headline range is $5.7B to $6.6B and not one number.

---

### IX · What I kept out of the causal story

Several stories about political and commercial conflicts of interest touch this period: a pardon connected to a Binance founder, a loan connected to a cabinet official and Tether, the holdings of a White House adviser, and a lawsuit against the Internal Revenue Service. I tested what could be tested. They are alleged or disputed, and for each one I found no flow link to USDC supply. I list the sourced facts and the open claims separately in the scorecard, and none of them is a cause in the account above. The test I will use if new filings arrive: the required disclosures (Circle and Cantor filings, Tether's quarterly attestation, public financial disclosures) matter more than silence in response to letters.

---

### X · Pre-mortem: the convex skeptic

| Skeptic objection | Record audit |
| :--- | :--- |
| "You are fitting a story to a V-shape." | Two legs fit the timing, and both are still inference. Neither is stated as cause. The decisive data is not public. |
| "A rewards campaign is not a redemption." | Correct. That is the one thing I could not show. The 43% to 53% is an overlap in size, not a funding trace. |
| "Your credences are made up." | They are subjective, and the log says so. What is checkable is the order of tests and the written falsifiers. Priors were set before the data. |
| "Secondary sources carry key figures." | True for liquidation totals, the Binance campaign details and the Tether attestation. Each is marked secondary, and the supply series are pulled directly. |
| "You rejected a dozen causes on thin evidence." | Rejections rest on dated primary or direct series where possible. Where they do not, the row says untested, not rejected. |

---

### XI · What this is for

The first call scored lowest and moved fastest once I read the primary text. The method did the work: pre-registered tests, priors written down, silence counted only where a disclosure was required. The next January-sized question gets the same rule: name the falsifier first, record the prior, read the primary text twice, and correct in public.

*This is analysis, not investment advice. Nothing here was checked by the author alone. Draft for review: not published, and nothing here is cleared to post.*

---

### Sources and reference record

**Primary:** [SEC staff statement on tokenized securities, Jan 28, 2026](https://www.sec.gov/newsroom/speeches-statements/corp-fin-statement-tokenized-securities-012826) · [Treasury TIC data, January 2026](https://home.treasury.gov/news/press-releases/sb0418) · [Circle Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000246/augustepr-circle_q22026f.htm) · FRED series (rates, spreads, dollar, yen, sentiment).

**Data:** [DefiLlama stablecoin supply](https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=2) · CoinGecko daily USDC and bitcoin series · [rwa.xyz](https://app.rwa.xyz/).

**Secondary, marked as such:** Binance USD1 campaign reports · January liquidation totals · CertiK January 2026 report via Cointelegraph · Tether attestation coverage.

**Companion records in the repo:** the scorecard `crypto-defi-predictions-closing-the-loop-2026-10-06.md` and the belief log `usdc-jan-2026-belief-log-2026-10-06.md` (H1 to H27).

*Field account, 2026. One question, two legs, one test that cannot be run yet.*
