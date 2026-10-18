# zachharris.eth: is it already a Farcaster custody address? (read-only, 2026-10-18T02:52Z = 2026-10-17 22:52 ET)
Local note only; the addresses are public chain data but this note is not to be posted anywhere. No key, login, wallet connection, write or transaction was used.

```json
{
  "loop": "zachharris.eth fid lookup",
  "prediction": "None stated in writing before the lookup; I expected the ENS address to be the custody address of an existing FID (user belief), which was wrong.",
  "result": {
    "ens_address": "0xB823E0C2A9AEC21B1Be620AC8990def38cF9395d",
    "fid_for_ens_address": "none (idOf returned 0)",
    "custody_match_for_ens_address": "no",
    "fname_zachharris": "registered 2023-03-06 to FID 10351, owner address 0x0b601c00984ab71a84442b04acf7d5ee7d8ae139",
    "custody_of_fid_10351": "0x0b601c00984ab71a84442b04acf7d5ee7d8ae139 (custodyOf returned it; idOf of that address returns 10351)",
    "is_fid_10351_zachs": "UNVERIFIED (inferred from the matching fname only)",
    "storage_units": "UNVERIFIED (not readable per FID from the registry without event history or a hub; needs a node)"
  },
  "delta": "The ENS name resolves to an address that is not a Farcaster custody address. A different address holds the zachharris fname and FID 10351.",
  "belief_moved": [{"prior": "zachharris.eth wraps Zach's Farcaster custody address", "posterior": "No. The ENS address owns no FID. If Zach has an FID it is 10351 at a different custody address (unverified identity link)", "evidence_kind": "onchain read", "source": "see sources"}],
  "blockers": [{"kind": "human", "who": "Zach", "what": "Confirm whether FID 10351 / the 0x0b60... address is his", "clears_when": "Zach says yes/no", "hard": false}],
  "next": "If 10351 is Zach's, the entry still uses a throwaway (I1). The ENS name can stay a read-only byline.",
  "counts": {"commits": 1, "files": 1, "tests_run": 0, "tests_passed": 0, "tool_calls": 4},
  "budget": {"tool_calls_used": 4, "cap": 60}
}
```

## Facts and sources (all public, no key)
- ENS zachharris.eth resolves to 0xB823...395d. Sources: https://api.ensdata.net/zachharris.eth and https://api.ensideas.com/ens/resolve/zachharris.eth (read 2026-10-17).
- IdRegistry idOf(0xB823...395d) returns 0. Source: JSON-RPC eth_call to https://mainnet.optimism.io, contract 0x00000000Fc6c5F01Fc30151999387Bb99A9f489b, selector d94fe832 computed locally from the keccak256 of idOf(address) (read 2026-10-18T02:52Z). The contract address came from my memory, not from a Farcaster page; I confirmed only that code exists at it (13,600 bytes) and that custodyOf and idOf agree on a second lookup. UNVERIFIED: that this address is the canonical IdRegistry (check against the docs contract list).
- fname zachharris: owner 0x0b601c00984ab71a84442b04acf7d5ee7d8ae139, to FID 10351, timestamp 1678122170 (2023-03-06). Source: https://fnames.farcaster.xyz/transfers/current?name=zachharris (read 2026-10-18T02:52Z). The query for zachharris.eth returned "No transfer found".
- custodyOf(10351) returns 0x0b601c00984ab71a84442b04acf7d5ee7d8ae139. Same RPC and contract as above (read 2026-10-18T02:52Z).
