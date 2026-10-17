# NEAR x Farcaster project: synthesis (2026-10-17). Opinions are mine; sources are in the three sibling notes.
Evidence quality: keys note = docs.near.org summaries, undated; agents/reputation note = search snippets only (leads, not facts); ecosystem note = news aggregators + search. I re-checked two items with a second search: Farcaster sale to Network School (reported by several outlets, price undisclosed, 2026-10-15/16, one outlet's "Network State Protocol" rename single-sourced) and the NEAR COO (no public "Patrick as COO" found; Chris Donovan listed as "former" COO).

## Belief moves
1. Brief correction #4 moves: Network School (Balaji) acquiring Farcaster from Neynar is now reported by multiple outlets, not one. The bounty poster is plausibly the new owner. Judge preference now matters more than before (opinion).
2. NEAR adds little to a Farcaster CLI: NEAR keys cannot sign Farcaster messages; chain signatures would derive a NEW address (fid would have to move); NEAR Auth/FastAuth-successor is browser/popup + third-party custody; NEAR DA prunes in ~hours. None of it is worth importing for the entry.
3. TEE guarantees are narrower than marketed: they attest code identity, not truth of an agent's claims, and 2025 attacks on attestation were reported (news only).
4. No NEAR-Farcaster interop found (absence of evidence).

## Applied opinions
- Win the bounty with the CLI, the node route, and the tutorial. Do not add NEAR, x402, KYC, or tokens to the entry.
- Judge-aware: demo against a public node AND a self-hosted node; keep a clean machine-readable JSON mode so agents can drive it; MIT; no API keys. Pin facts to Snapchain repo, not to Neynar docs, since ownership is in flux.
- Anchor for the accountability score: EAS-style offchain attestation signed by the user's key, optional hash timestamp on a cheap L2; Farcaster fid is an identity link, not the ledger. Avoid ERC-8004 (draft) and any single public score.
- Key custody ladder: paper + passphrase-encrypted file (ADP only as a second layer) > Touch ID-gated keychain for the disposable app key > hardware wallet for custody. App key is re-issuable, so do not back it up.
- Devices as verifiers of receipts (light check of hashes/signatures), not miners; no token in v1.
- Patrick: unconfirmed as COO. Ask him directly; after the entry, send the repo with an agent-friendly JSON mode. No integration promises.

## Open and unverified
Snapchain maintenance after the sale; bounty deadline (taken from the brief, post not found by research); NEAR finality/storage costs; whether NEAR MPC signatures are accepted by Farcaster contracts; EAS docs and the TEE attack papers were not read at primary.
