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
