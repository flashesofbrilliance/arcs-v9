# NEAR accounts, keys, signing: relevance to a Farcaster CLI with delegated app keys

Researched 2026-10-17. Method: WebFetch/WebSearch summaries of docs.near.org pages. Fetch tool returns model-summarized text, so wording is not verbatim; no page carried a publication date. "Verified" = stated on the fetched docs page. "Inferred" = my reasoning or prior knowledge (Farcaster side is from memory, not re-fetched).

## 1. Account model
Verified (docs.near.org/protocol/access-keys, undated, mentions nearcore 2.13 / protocol v86):
- Full-access keys: total control (transfer, delete account, manage keys, deploy, call anything). Never share.
- Function-call keys: signable for ONE contract (receiver_id), optional method list, optional gas `allowance`; no NEAR deposits; omitted allowance = unlimited gas; exhausted allowance = key can no longer sign.
- Keys removed via DeleteKey action; account with zero keys is locked. Gas keys exist (newer; burn-on-delete rule).
- Implicit accounts start with a full-access key; named accounts get one at creation.
Inferred: revocation is an on-chain tx signed by a full-access key (page gives no separate flow); implicit = account id derived from public key (not stated on fetched page).
So what: NEAR's native delegation (scoped key, allowance, revoke) mirrors Farcaster app-key delegation, but a NEAR function-call key only authorizes calls to one NEAR contract; it cannot sign Farcaster messages. Useful only as a pattern, or if receipts are anchored via a contract.

## 2. Chain signatures / MPC
Verified (docs.near.org/chain-abstraction/chain-signatures, undated):
- `v1.signer` contract `sign` supports Secp256k1 (domain_id 0) and Ed25519 (domain_id 1); more domains via vote_add_domains.
- Derivation: NEAR account + path string -> deterministic foreign address (additive key derivation). 8 MPC nodes, threshold signing. One-way only (cannot read foreign state). Replay risk if payload does not bind the network; recommends distinct path per chain.
- Cost, mainnet/testnet status: NOT stated on the page.
Inferred: `sign` takes a prehashed payload, so an EIP-712 digest (keccak256 of typed data) could be signed with secp256k1; an ed25519 domain could sign Farcaster message hashes. The derived key is a NEW address, not an existing Farcaster custody address; to use it you would transfer/register the FID to the derived address (Optimism ID Registry). Unverified: that the MPC returns recoverable (v/r/s) signatures acceptable to the registry contract; test on testnet before believing it. Also, Farcaster Ed25519 uses sha-512-style ed25519 signing over a blake3 hash of the message body; MPC ed25519 compatibility with that exact variant is unverified.
So what: possible but adds an MPC trust assumption, per-signature latency and NEAR gas to a signing path that a local ed25519 app key does today for free. Not recommended for app keys; maybe for a custody-less custody wallet, as a research item only.

## 3. Intents / chain abstraction
Verified (docs.near.org/chain-abstraction/intents/overview, undated): users declare a desired outcome, market makers/solvers compete off-chain, user approves a quote, a Verifier contract on NEAR settles. Page states no status, asset list, API-key rule or fee schedule; links to a 1Click API example.
Inferred: it is a swap/transfer settlement layer, not a messaging or identity layer. Late-2026 maturity and fees not verified here.
So what: irrelevant to casting; at most useful for funding the Optimism/Farcaster storage-rent payment cross-chain. Skip.

## 4. Passkey / social login
Verified via search snippets plus docs.near.org/web3-apps/tutorials/near-auth:
- FastAuth (original) is marked deprecated in docs; a revamp with MPC + Auth0 was in progress.
- NEAR Auth: Google/Apple/email/passkey login via Auth0; keys held by MPC (v1.signer); `fast-auth.near` verifies the Auth0 JWT; each signature triggers an Auth0 approval (popup/redirect); ed25519 default, secp256k1 optional; mainnet needs approved credentials (application form for an Auth0 client id); testnet open.
- Other options named in docs: Privy, Web3Auth, NEAR Connect; Web3Authn is a community passkey SDK (not official).
Custody: key is never held by one party, but access depends on Auth0 (a centralized IdP) and the MPC set; Auth0 account compromise or policy change affects signing. Not self-custody.
So what: needs a browser round-trip per signature and a gated mainnet credential; poor fit for a headless CLI. Local keychain/passkey storage of the app key is simpler.

## 5. Storage / DA to anchor receipt hashes
Verified (search snippet of docs.near.org/chain-abstraction/data-availability; the /tools/near-data-availability URL 404'd): NEAR DA is a rollup-oriented blob store contract + light client + RPC client; docs call integrations proof of concept; one cited cost "at the time of writing" 100 KiB = 1 NEAR flat (undated, stale likely); blob data pruned after at least 3 epochs (about 5 in practice, 12h epochs), then archival nodes/indexers only. A 2023 announcement cited ~$0.0033 per 100 kB (marketing, 2023).
Inferred: for a 32-byte hash, an ordinary NEAR contract call or tx memo is cheaper and permanent in state, and NEAR transactions finalize in seconds (finality time not verified on fetched pages; the transaction-anatomy page 404'd). NEAR DA's pruning makes it wrong for long-lived receipt anchors. API-key requirement: none found; RPC providers may require keys.
So what: if anchoring is wanted, use a tiny NEAR (or Base/OP) tx carrying the hash; do not use NEAR DA. Prefer OpenTimestamps-style or the Farcaster hub itself unless on-chain anchoring is a requirement.

## Gaps and cautions
- No page was dated; "status late 2026" unverified for intents, chain signatures cost, NEAR Auth maturity.
- Multiple NEAR DA / FastAuth pages are renamed or deprecated (docs paths moved: /data-availability/* -> /chain-abstraction/data-availability; fastauth-sdk deprecated).
- Farcaster protocol claims (EIP-712 custody on Optimism, ed25519 app keys) are from prior knowledge; re-verify against docs.farcaster.xyz before relying.

## Sources
- https://docs.near.org/protocol/access-keys
- https://docs.near.org/chain-abstraction/chain-signatures
- https://docs.near.org/chain-abstraction/intents/overview
- https://docs.near.org/chain-abstraction/fastauth-sdk
- https://docs.near.org/web3-apps/tutorials/near-auth
- https://docs.near.org/web3-apps/concepts/web-login
- https://docs.near.org/chain-abstraction/data-availability
- https://github.com/Nuffle-Labs/data-availability
- https://github.com/web3-authn/sdk (community, unofficial)
