# NEAR and Farcaster ecosystem read (2026-10-17)

Method: public web search plus page fetches only. Tags: [P] primary-ish (named outlet or official repo, read directly), [S] secondary/aggregator, [I] inferred. Search-engine summaries were checked against fetched pages where noted. No outreach, no sign-ups.

## 1. NEAR leadership and the COO claim

- NOT FOUND: any public announcement of a COO named Patrick at NEAR Foundation, NEAR One, or NEAR Protocol. Searched several phrasings. Do not name or assume the person; identity is ambiguous and unverified. Ask the friend directly or check near.org / the NEAR Foundation X account. [absence of evidence, not proof]
- Historical COOs [S]: Bill Earner announced as COO Oct 2022 (NEAR Foundation X post); Chris Donovan became COO then CEO after Marieke Flament resigned Sept 2023.
- Oct 15, 2026 [P, The Block, fetched]: Council = Illia Polosukhin, Diogo Monica, Chris Donovan ("former NEAR Foundation COO"), Bowen Wang (NEAR One founder), plus newly appointed Mert Mumtaz (Helius CEO). No current COO named. Mumtaz judges NEAR Hackathon Nov 1-14.
- Oct 2025 [S]: Foundation added five execs (Matt Kummell CBO, a CMO, CPO, CTO). No COO listed.
- A May 2025 piece mentions a new "Executive Director" at NEAR [S, title only, not opened].
- Inference [I]: a COO hire could be very recent (after Oct 15) or at a NEAR-adjacent entity (NEAR One, a business unit). Unconfirmed.

## 2. NEAR priorities (2026)

- [S, paragraph.com fetched, Oct 2026] Chain abstraction (Chain Signatures, Intents), Confidential Intents, NEAR AI + IronClaw agent runtime, dynamic resharding, inflation cut 2.5% to 1.6%, buybacks funded by Intents revenue from Feb 23, 2026; Bitwise spot NEAR ETF Sept 29; SVRN acquired FastNEAR Oct 8.
- [S, BlockEden Mar 2026] agents need programmable payments, cross-chain, privacy; Intents over $10B volume.
- [P, The Block] NEAR Intents had a $3.8M exploit in Oct 2026 (security is a live sore spot).
- [S] Infrastructure Committee 2026 plan: MPC, sharded RPC, privacy infra. Protocol Rewards paid $200K+ to 30+ teams post-hackathon in 2025 (Nansen).
- Hackathon: Nov 1-14, 2026 [P, The Block]. Program terms not read from near.org (not fetched).

## 3. NEAR x Farcaster interop

- NOT FOUND any NEAR-Farcaster integration, NEAR-run Farcaster bounty, or current near.social/BOS status. Only a 2023 NEAR Social cost data point. [absence]
- Related, verified: NEAR is a sponsor on Bankless Farcaster content ("confidential swaps across 35+ chains") [S, ad slot only].
- [I] Natural bridge is Intents/agents, not social: a Farcaster-posting agent paying via Intents.

## 4. Farcaster state (as of Oct 17, 2026)

- Jan 2026 [S, multiple]: Merkle Manufactory sold protocol contracts/repos/apps/Clanker to Neynar; $180M returned to investors; Dan Romero and Varun Srinivasan stepped back (later joined Tempo, Feb).
- Aug 17, 2026 [S]: Neynar's Rish said Neynar sought a new home.
- Oct 15, 2026 [S, CoinMarketCap + KuCoin fetched; The Block-style]: Neynar transferring app, protocol repos and related products to Network School (Balaji). Most Neynar staff join NS; Rish and Manan leave. Terms undisclosed. Balaji: other clients welcome since client and protocol are open source; Farcaster/Warpcast/Neynar names barred from coins/commercial projects. One outlet claims a rename to "Network State Protocol": single-source, treat as unconfirmed.
- Implication [I]: the bounty issuer now owns the platform. A CLI/read-node client is on-message with "build your own client."
- Snapchain [P, farcasterxyz/snapchain README]: read node needs 16GB RAM, 4 cores, 1.5TB, ports 3381-3383; ships an `fc` CLI for submit/stream; `curl localhost:3381/v1/info` health check; repo states migration phase. Neynar docs say 2TB. Post-acquisition repo/maintainer status: not verified.
- Existing entrants/prior art [P/S]: `tofui` (Go TUI, last seen v0.1.5, June 2024, Neynar-backed, stale), `farcaster-snapchain-utils` (andrei0x309 library, read/write), vrypan `fario` CLI (cited in a 2024 balajis bountycaster submission), 2024 artlu99 networkx bounty. No 2026 CLI/TUI or read-node tutorial entrants found. Does not prove none exist.
- Bounty itself: NOT FOUND publicly (the Oct 24 deadline, balajis.eth CLI/Snapchain scope). Take scope from the bounty post, not from this file.
- Mini Apps/agents: only background (datawallet explainer); no 2026 specifics gathered.

## 5. Collaboration angle (does not distract)

- Fit is thin. Do not force NEAR into the submission.
- Credible angle, after submission: a short writeup "reading Farcaster from a Snapchain read node in a terminal" published openly, then one note to Patrick: "shipped X, thought of you, no ask." Social-graph or agent-readable output (JSON/NDJSON) is naturally reusable by NEAR agents. [I]

## 6. Ranked low-cost moves

1. Confirm the COO fact from Patrick himself (one text, no research time) and skip anything public until he says it is public. Cost ~2 minutes.
2. Spend all effort on the bounty; pin read-node facts above (ports, `/v1/info`, `fc`) and design for the new owner (Network School) reading it: demo works against a public node and a self-hosted one. Cost 0 extra.
3. After the Oct 24 submission, send Patrick the repo link plus a 3-line "agent-friendly JSON mode" note and ask nothing. Cost ~10 minutes, post-deadline.

## Sources
- https://coinmarketcap.com/academy/article/network-school-acquires-farcaster-neynar
- https://www.kucoin.com/news/flash/farcaster-changes-hands-for-third-time-in-nine-months
- https://www.theblock.co/news/business/2026-10-15-helius-ceo-mert-mumtaz-joins-near-foundation-council-418656
- https://paragraph.com/@mconnectdaoresearch/near-protocol-in-october-2026-ai-native-blockchain-real
- https://x.com/NEARFoundation/status/1580198982537519106
- https://www.near.org/blog/enter-the-black-dragon-near-co-founder-joins-the-near-foundation-as-ceo
- https://www.mexc.com/news/131408
- https://blockeden.xyz/blog/2026/03/15/near-protocol-invisible-crypto-super-app-ai-first-ux-confidential-intents/
- https://www.raptorgroup.com/news/near-infrastructure-committee-2025-year-in-review-and-the-path-to-2026/
- https://github.com/farcasterxyz/snapchain
- https://docs.neynar.com/snapchain/overview
- https://github.com/andrei0x309/farcaster-snapchain-utils
- https://github.com/artlu99/farcaster-networkx-balajis-bountycaster-20240205
- https://beta.pkg.go.dev/github.com/treethought/tofui
- https://coincodex.com/article/93808/balaji-srinivasans-network-school-acquires-farcaster-starts-banning-users-for-alleged-misconduct
