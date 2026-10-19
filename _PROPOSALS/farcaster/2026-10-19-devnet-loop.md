# Devnet loop (2026-10-19): finish the write path locally. Prediction written BEFORE running anything.
Predictions (confidence):
- D1 (devnet FID whose custody key we control via a supported route): 55%. I expect the AdminService to accept an arbitrary custody address in an ID_REGISTER on-chain event; the risk is that `fc devnet bootstrap` hard-codes a random custody address and no flag exists. Kill line 15 tool calls.
- D2 (gasless KEY_ADD via makeKeyAddBody appears in /v1/signersByFid): 50%, conditional on D1. Risks: @farcaster/core 0.20.0 helper signatures differ from my probe; EIP-712 domain/network mismatch on devnet; deadline/nonce rules.
- D3 (cast, follow, react via core helpers merged and readable within 60 s, event on shard 1 or 2): 60% conditional on D2. Reaction is the untested path.
- KEY_ADD in /v1/events: 35% that it is visible on any shard 1/2 (my guess: shard 0, which /v1/events rejects).
- D4: devnet limits will differ from mainnet; resolves nothing for 5000 vs 77000 (95%).
- D5: both probes return proven on devnet if D2/D3 pass; canary and argv checks pass (90%).
Local only. No iris.farcaster.xyz, no public node, no mainnet, no cloud. Throwaway keys never written to this note. Disk guard: stop if free disk < 20 GB.

## Results (local devnet only, $0, no external host contacted; throwaway keys kept in mode-0600 files in a scratch dir, never printed here)
```json
{
  "loop": "devnet write path, D1-D5",
  "prediction": "D1 55%, D2 50%, D3 60% conditional, KEY_ADD in /v1/events 35%, D4 resolves nothing 95%, D5 both probes proven 90% (see top of file)",
  "result": {
    "D1": "proven: supported route is AdminService.SubmitOnChainEvent (public gRPC, devnet basic auth). `fc devnet bootstrap` hard-codes a random custody address, but the RPC accepts ID_REGISTER with any `to` address, so a STORAGE_RENT + ID_REGISTER pair for FID 2001 with `to` = address of a throwaway key worked (numFidRegistrations rose). Called with grpcurl inside the node container. No Snapchain patch. Tool calls used: ~6.",
    "D2": "proven: makeKeyAddBody (fid, key, scopes CAST_ADD+REACTION_ADD+LINK_ADD, ttl 604800 = 7 days, nonce 1, deadline +600 s) + makeKeyAdd, submitted to /v1/submitMessage (HTTP 200). /v1/signersByFid lists the key (SIGNER_SOURCE_OFFCHAIN, scopes as requested, ttl 604800, nonce 1, currentUserNonce 1).",
    "D3": "proven: makeCastAdd, makeLinkAdd, makeReactionAdd (LIKE on a devnet cast) all HTTP 200 and readable (castsByFid, linksByFid?link_type=follow, reactionsByCast) about 4 s after submit (poll step 2 s). Matching MERGE_MESSAGE events appeared on shard 2 (not shard 1).",
    "signer_add_visibility_in_events": "UNVERIFIED/not seen: the last 1000 events on shards 1 and 2 held no KEY_ADD; /v1/events?shard_index=0 returned HTTP 400 with from_event_id=0 earlier and an empty list with reverse=true later. KEY_ADD is observable via /v1/signersByFid, which is what the client should use.",
    "D4": "devnet only: FID 2001 with 10 storage units (UnitType2025) shows limits CASTS 1000, LINKS 2000, REACTIONS 2000, USER_DATA 250, VERIFICATIONS 50, USERNAME_PROOFS 20, STORAGE_LENDS 10. These do NOT resolve the mainnet 5000-vs-77000 cast conflict.",
    "D5": "write-path probe: proven (KEY_ADD accepted, key visible after ~4 s, cast readable, merge event seen). Events probe: proven on shards 1 and 2. Canary 0 occurrences; argv canary refused (exit 2). Self-test 12/12."
  },
  "delta": "Better than predicted on D1-D3. Surprises: (1) my write probe called a function that does not exist in @farcaster/core 0.20.0 (getGaslessSignedKeyRequestMetadata); the real API is makeKeyAddBody with the custody signer. (2) KEY_ADD returns 200 before it is merged: casting immediately gets 'signer not authorized'; the key appeared after ~4 s. (3) my merge-event check scanned the oldest 1000 events and missed new ones; reverse=true fixes it. (4) @noble/curves v2 dropped the extensionless ed25519 import.",
  "belief_moved": [
    {"prior": "A devnet FID with a controlled custody key may need a Snapchain patch", "posterior": "No: AdminService.SubmitOnChainEvent accepts any custody address", "evidence_kind": "executed test", "source": "this note, D1"},
    {"prior": "Gasless KEY_ADD plus cast works as one step", "posterior": "Two steps with a wait: KEY_ADD must merge before the key can sign (about 4 s on devnet)", "evidence_kind": "executed test", "source": "write-path-probe run 2026-10-19"}
  ],
  "blockers": [],
  "next": "Fold the 'wait for the key to appear' rule and the real helper names into the tutorial Room 4 and the signer row; mainnet behaviour (EIP-712 domain, timing) is still unproven and needs a real node.",
  "counts": {"commits": 2, "files": 8, "tests_run": 9, "tests_passed": 9, "tool_calls": 27},
  "budget": {"tool_calls_used": 27, "cap": 50}
}
```
Disk: free 71 GiB at end (73 GiB at start); Docker images 11.7 GB, build cache 7.2 GB, containers stopped (not removed). Added dependencies were installed only in a scratch dir outside the repo: @farcaster/core 0.20.0, viem, @noble/curves (npm, --ignore-scripts).
## What this changes
- Tutorial Room 4: use makeKeyAddBody with the custody signer, wait until the key appears in /v1/signersByFid, then sign. Mention that KEY_ADD returns before merge. Import ed25519 from '@noble/curves/ed25519.js'.
- Signer row (fc-signer-bundle): helper names are verified for 0.20.0 (declarations read); behaviour verified on devnet only.
- Reaction path now proven locally (the official `fc` has no reaction command).
