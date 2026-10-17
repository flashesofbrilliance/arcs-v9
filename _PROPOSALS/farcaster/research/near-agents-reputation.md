# NEAR agents, verifiability, and onchain reputation (research note)

Date: 2026-10-17. Method: web search only (snippets, no page fetches). Tags: [V-secondary] = stated by search-result summaries of a primary/vendor page, not read in full by me; [INF] = my inference; [GAP] = not found. Nothing here is verified-from-primary by direct page read. Treat all as leads to re-check.

## 1. NEAR AI, private inference, Shade Agents
- NEAR AI Cloud private inference uses Intel TDX confidential VMs plus NVIDIA GPU confidential computing; responses come with a signed attestation. [V-secondary, vendor docs] Vendor claim: NEAR, infra and model providers cannot see data. This is a vendor claim.
- Shade Agents: the agent contract accepts registration only if the agent proves it runs in a TEE with approved code hashes (docker image / app compose hash); optional PPID allowlist of machines; Phala Cloud (dstack) is the default host; local dev skips attestation. [V-secondary, docs.near.org]
- What it guarantees: code identity (hash) and memory confidentiality, on trusted hardware. It does NOT guarantee that an agent's claims are true, or that the operator is honest about inputs. [INF]
- Hardware caveat: TEE.Fail (Oct 2025) and WireTap (Sep 30 2025) showed sub-$1,000 physical interposer attacks that extract attestation keys / forge quotes on SGX, TDX, SEV-SNP; need physical access plus root. [V-secondary, news coverage; verify papers] NEAR's own security page points to "Proof of Cloud" to check facility security. [V-secondary]
- IronClaw agent runtime and confidential GPU marketplace announced NEARCON Feb 2026. [V-secondary]

## 2. Identity / personhood / attestation primitives
- Human Passport (ex Gitcoin Passport): acquired by Holonym Foundation, Dec 2024 / announced Feb 2025; now under human.tech; stamps aggregate to a score; moving credentials to ZK; self-reports 120+ projects, $512M protected (Mar 2026). [V-secondary, vendor]
- Self (self.xyz): ZK proof from passport NFC chip, selective disclosure; Farcaster listed as a partner; EVM/Celo-centric. [V-secondary]
- NEAR-native reputation or personhood primitive: [GAP] none found in this pass. No NEAR integration of Human Passport or Self surfaced.
- ERC-8004 (Draft EIP): Identity, Reputation, Validation registries for agents; feedback is 0-100 score + tags + optional off-chain URI+hash; deployed on several EVM chains incl. Celo; Validation registry still being revised. [V-secondary]

## 3. Comparison anchors
- EAS: offchain attestations cost no gas; you can post only the UID/hash onchain as a timestamp; private-data mode posts a Merkle root only. Base is a supported chain. [V-secondary, SDK/guides] Base fee numbers: [GAP].
- Farcaster: signers are ed25519 keys registered in the Key Registry on Optimism, authorized by the fid custody address; hubs accept only messages from registered keys; removing a key deletes its messages; revoked keys cannot be re-added. [V-secondary, docs.farcaster.xyz] Agents are just fids plus signers; no native "agent" label found. [GAP]
- Ceramic: not researched.

## 4. Known failures of onchain reputation
- Sybil airdrop farming: aPriori (~14k wallets, >60% of claim) and Arbitrum (sybils ~half of distribution) as cited by trade press. [V-secondary]
- Goodhart: visible rewarded scores become targets; tiered rewards invite wallet splitting. [V-secondary; framing mine]
- Gitcoin Passport itself was gamed and re-scored over time; Optimism attestation spam; defamation/right-to-erasure on immutable ledgers. [GAP, from memory only; not verified here]

## Applied opinions (all [INF])
1. Lowest friction anchor for a CLI-first project: EAS offchain attestation signed by the user's key, plus an optional onchain timestamp of the hash on Base. Zero-gas default, hash-only, opt-in fits. Farcaster fid is useful as identity link (verifications) not as the ledger.
2. A hash-only anchor proves existence and time, nothing about truth. The score's value comes from resolution (who resolved the claim, by what rule), so design the resolver, not the chain.
3. Avoid: NEAR/Shade for v0 (TEE proves code identity, not honesty; adds hardware-attack surface and a second ecosystem); a single public numeric score (Goodhart, defamation); anything per-claim onchain with names or content; ERC-8004 until the spec settles; treating any personhood stamp as proof of non-sybil.
4. Keep claims about others hash-only and subject-consent; publish only self-authored claims.

## Sources
- https://docs.near.org/ai/shade-agents/concepts/ai-inference
- https://docs.near.ai/cloud/private-inference
- https://near.ai/blog/building-next-gen-near-ai-infrastructure-with-tees
- https://near.ai/blog/near-ai-launches-ironclaw-confidential-gpu-marketplace-and-multimodal-confidential-inference
- https://docs.near.org/ai/shade-agents/concepts/terminology
- https://docs.near.org/ai/shade-agents/quickstart/components
- https://phala.com/posts/near-shade-agent-template-phala-cloud
- https://thehackernews.com/2025/10/new-teefail-side-channel-attack.html
- https://ethresear.ch/t/physical-integrity-attestation-and-the-state-of-permissionless-tees/24964
- https://passport.human.tech/blog/from-gitcoin-passport-to-human-passport-we-re-now-part-of-human-tech
- https://human.tech/blog/human-tech-launch-acquisition-gitcoin-passport
- https://safefoundation.org/blog/safe-research-zk-passport-where-are-we-now
- https://docs.celo.org/build-on-celo/build-with-self
- https://eips.ethereum.org/EIPS/eip-8004
- https://docs.polygon.technology/payment-services/agentic-payments/agent-integration/erc8004.md
- https://pypi.org/project/eas-sdk/
- https://www.quicknode.com/guides/ethereum-development/smart-contracts/what-is-ethereum-attestation-service-and-how-to-use-it
- https://docs.farcaster.xyz/reference/contracts/reference/key-registry
- https://github.com/farcasterxyz/protocol/discussions/103
- https://cointelegraph.com/news/token-airdrops-targeted-farm-accounts-sybil-attacks
- https://www.coingecko.com/learn/sybil-attack
