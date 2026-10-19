# Zero-cost path: local Snapchain devnet + the official `fc` CLI (read 2026-10-18; nothing run)
Sources: github.com/farcasterxyz/snapchain at commit fc87f268 (cloned via GitHub tarball, read locally): README.md, cli/README.md, Makefile, docker-compose.yml, src/bin/setup_local_testnet.rs, site/docs/pages/getting-started.mdx. docs.farcaster.xyz/reference/contracts/deployments says no testnet deployments (read via summarizing fetch tool, 2026-10-18).

## Facts
- `make dev` runs `docker compose up --watch` and builds a local multi-node devnet from source (4 nodes, 2 shards by default, setup_local_testnet.rs). Needs Docker. Docker, cargo and rustc are installed on this machine (paths found with `which`).
- `fc` (official, ALPHA) ships in the Snapchain image. Subcommands: key-add (gasless KEY_ADD), key-remove, cast-add, cast-remove, link (follow/block), live-at, verification, devnet (devnet-only AdminService helpers that register FIDs on a local node), subscribe (stream HubEvents as JSON). Signer secret is read from the SIGNER_SECRET environment variable. Source: cli/README.md.
- cli/README.md shows `fc subscribe --shard 1 --grpc-node https://iris.farcaster.xyz:3383` as an example against a public testnet node. UNVERIFIED: that this node is up, open, or allowed for our use. Not contacted.
- Snapchain README says a brand-new mainnet node downloads historical snapshots and "can take up to 2 hours" to catch up; getting-started still lists 2 TB free disk. Sync time is therefore not the main cost; disk is.
- Snapchain testnet compose exists (guides/managing-a-node.mdx) but is unstable and may be reset; disk size UNVERIFIED.

## What this means (my opinion)
1. A full flow (register test FID on devnet, gasless key-add, cast, follow, stream events) can be exercised for $0 on a laptop with Docker, without 2 TB and without any wallet funds. UNVERIFIED: whether `make dev` builds cleanly here and how long it takes.
2. The official `fc` CLI already covers submit and subscribe. Our client only adds value as the feed, hooks and receipts gate on top. Earlier research listed other CLIs but missed `fc`; prior-art belief updates accordingly.
3. This does NOT satisfy the contest as written (a real mainnet read node run by a second human); it de-risks our client and probes at zero cost.

## Result of the run (2026-10-18, local only, $0, ~4 minutes build on 6 CPUs; nothing contacted outside this machine)
- Built `snapchain-local:dev` from the cloned repo with `docker compose build` (exit 0) and started 4 nodes with `docker compose up -d`. /v1/info reported version 0.14.3, shards 0, 1, 2, blocks advancing.
- `fc devnet bootstrap --fid N --network devnet --node http://127.0.0.1:3381 --grpc-node http://127.0.0.1:3383 --auth dev:dev` registered devnet FIDs 1001 and 1002 (synthetic on-chain events; custody address is random, so `fc key-add` is NOT exercised: it derives the custody key from a MNEMONIC env var).
- With the printed signer secret passed in the SIGNER_SECRET environment variable inside the container, `fc cast-add` and `fc link add` each returned HTTP 200 and the cast was readable at /v1/castsByFid?fid=1002.
- `events-probe.mjs` run against http://127.0.0.1:3381: verdict "proven" on shards 1 and 2 (no duplicates, per-block totalEvents counts all matched, restart from saved cursor delivered 0). Seen: CAST_ADD and LINK_ADD (both on shard 2), MERGE_ON_CHAIN_EVENT on shards 1 and 2. REACTION_ADD not seen: `fc` has no reaction subcommand, so it was never sent.
## Findings that change the plan
1. `/v1/events?shard_index=0` returns 400 "Shard not found". Message events live on shards 1 and 2 (here, casts and links on shard 2). The probe default is now shards 1,2 (FC_SHARDS to override). Whether KEY_ADD (a shard 0 merge per a comment in setup_local_testnet.rs) is observable through /v1/events is UNVERIFIED.
2. Event IDs are block-based (first IDs 16384, jumps of millions between blocks), confirming the contiguity assumption was wrong. The old "gapIds" report field was meaningless; it is now `idJumpsInfoOnly`.
3. Safety note on the official `fc`: defaults point at the public testnet node iris.farcaster.xyz, so always pass --node and --network. It accepts --signer-secret in argv (also readable from SIGNER_SECRET), and derives custody keys from a MNEMONIC environment variable. Our I8 rule (no key in argv) applies to how we call it.
4. The write-path probe (@farcaster/core helpers) has still not been run: it needs a devnet FID whose custody key we control, which `fc devnet bootstrap` does not give. UNVERIFIED how to get one on devnet.
