# Devnet loop (2026-10-19): finish the write path locally. Prediction written BEFORE running anything.
Predictions (confidence):
- D1 (devnet FID whose custody key we control via a supported route): 55%. I expect the AdminService to accept an arbitrary custody address in an ID_REGISTER on-chain event; the risk is that `fc devnet bootstrap` hard-codes a random custody address and no flag exists. Kill line 15 tool calls.
- D2 (gasless KEY_ADD via makeKeyAddBody appears in /v1/signersByFid): 50%, conditional on D1. Risks: @farcaster/core 0.20.0 helper signatures differ from my probe; EIP-712 domain/network mismatch on devnet; deadline/nonce rules.
- D3 (cast, follow, react via core helpers merged and readable within 60 s, event on shard 1 or 2): 60% conditional on D2. Reaction is the untested path.
- KEY_ADD in /v1/events: 35% that it is visible on any shard 1/2 (my guess: shard 0, which /v1/events rejects).
- D4: devnet limits will differ from mainnet; resolves nothing for 5000 vs 77000 (95%).
- D5: both probes return proven on devnet if D2/D3 pass; canary and argv checks pass (90%).
Local only. No iris.farcaster.xyz, no public node, no mainnet, no cloud. Throwaway keys never written to this note. Disk guard: stop if free disk < 20 GB.
