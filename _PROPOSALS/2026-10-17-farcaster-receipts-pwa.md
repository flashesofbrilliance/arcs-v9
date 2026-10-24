# Farcaster "receipts or it didn't happen" PWA client: research notes (2026-10-17)

Status: research only. Nothing built, nothing published. Source claims marked [doc], [src] (read in code), or [unverified].

## The bounty (balajis.eth, farcaster.xyz/balajis.eth/0x50184b62, posted ~2026-10-17)
- $2,048 / $512 / $128 honorable mentions. Deadline: 7 days from post (about 2026-10-24).
- Deliver: microsite quickstart + tutorial, MIT GitHub repo, a human voucher's public endorsement on Farcaster.
- Flow: provision compute by script -> Snapchain read node -> client reading from that node. No third-party API keys.
- Client: import seed phrase, issue itself an app key, read feed, post, follow, react, include/exclude casts from other clients.
- Clarified in-thread: read nodes DO take writes; app keys are gasless; tutorial must treat seed phrases like `rm -rf` (test account only, prefer delegated signers).

## Correction (2026-10-17, Zach)
The bounty's "mobile- and desktop-friendly" requirement applies to the tutorial, not the client. A CLI/TUI client is allowed and sidesteps findings 1 and 2 below (CORS, TLS) because a Node process has no browser restrictions. The original post text also says read nodes do not accept writes and app keys cost an Optimism transaction; both were superseded by Balaji's in-thread clarifications (read nodes relay writes; gasless app keys). Treat the PWA sections as the stretch option, CLI/TUI as the lead.

## Protocol facts that matter
- Read node: follows chain, serves HTTP :3381 and gRPC :3383. Needs 16 GB RAM, 4 vCPU, ~2 TB disk, public IP; snapshot is hundreds of GB, hours to sync [doc: snapchain getting-started].
- Writes via a read node: validated, then gossiped to validators; node keeps nothing. A success response means accepted for relay, NOT in a block. Gossip loss means resubmit. Confirm by querying the message back or watching MERGE_MESSAGE [doc: node-types].
- Gasless signer: submit a KEY_ADD message. Needs (a) an EIP-712 KeyAdd signature from the FID custody address covering scopes, TTL (max 90 days, sliding), nonce, and (b) an EIP-712 SignedKeyRequest from the requesting app's FID (requestFid), and the envelope signed by the new Ed25519 key. Do not use getSignedKeyRequestMetadata (onchain domain); use makeKeyAddBody / getGaslessSignedKeyRequestMetadata [doc: writing-messages]. Helpers landed in hub-monorepo 2026-07-29 (FIP-272).
- Scoped keys: a key can be limited to message types (CAST_ADD only, etc.). KEY_ADD/KEY_REMOVE can never be scoped in. Up to 1000 active gasless keys per FID [doc].
- HTTP API has no feed, search, or aggregate counts. Primitives: castsByFid, castsByParent, castsByMention, reactionsByCast/Fid/Target, linksByFid/TargetFid, userDataByFid, signersByFid, storageLimitsByFid, events, submitMessage (POST protobuf bytes) [src: http_server.rs routes].
- Username lookup: fnames.farcaster.xyz returns `access-control-allow-origin: *` [tested live].
- Libraries: @farcaster/core 0.20.0 (noble curves/hashes, viem), @farcaster/hub-web 0.13.0, MIT, active as of 2026-07-29.

## Findings that change the plan
1. CORS gap on writes [src, UNTESTED against a live node]: http_server.rs sets `Access-Control-Allow-Origin` (default `*`) on responses only. No OPTIONS handler and no Allow-Headers/Methods anywhere in the file. A browser POST of protobuf bytes (non-simple content-type) triggers a preflight that the node likely fails. Reads (simple GET) are fine. Fix options: TLS/CORS reverse proxy in front of the node (Caddy), or an upstream PR adding OPTIONS handling (which the bounty explicitly rewards). Verify on a real node before building around it.
2. HTTPS requirement: an installed PWA is served over HTTPS and cannot fetch a plain-http node (mixed content). The node needs TLS anyway: Caddy with a domain, or a Cloudflare/Tailscale tunnel. This belongs in command 1 of the quickstart.
3. The official `farcasterxyz/client` (MIT, Neynar copyright) points at Farcaster's production API, not your own node. Forking it means replacing farcaster-client-data/hooks; not obviously cheaper than a small fresh PWA on hub-web.
4. Licenses: Snapchain is GPL-3 (run as a separate process, talk over HTTP; fine). herocast is AGPL-3 (read for ideas, never copy into the MIT repo).
5. Client attribution is verifiable: each app key's KEY_ADD names a requestFid, readable via /v1/signersByFid. "Include/exclude casts from other clients" = filter by the signer's requestFid.

## PWA feasibility: yes, cheap
- Static site (Vite + small framework, no backend). Hosting free (GitHub Pages / Cloudflare Pages). The only real cost is the node VM (2 TB disk, 16 GB RAM); I have not priced current providers.
- Reads: fetch the user's node. Home feed is built client-side: linksByFid -> castsByFid per followee -> merge by timestamp, cache in IndexedDB. Thread view = castsByParent. Counts = reactionsByCast.
- Writes: build + sign messages in the browser with @farcaster/core (noble Ed25519), POST bytes to the node. App key lives in IndexedDB (tradeoff: noble-held keys are extractable; non-extractable WebCrypto Ed25519 depends on browser support [unverified]).
- Account import without pasting a seed: prefer wallet `signTypedData` (EIP-712) for the one-time KEY_ADD authorization. Support seed import too (the bounty asks), derive in-memory, use once, discard, with loud test-account warnings.
- Not feasible without a server: web push notifications, search, algorithmic ranking. Cut them; polling /v1/events + castsByMention covers basic mentions while the app is open.
- iOS: installable via Add to Home Screen; background sync unreliable. Fine for a tutorial client.

## Receipts-or-it-didn't-happen: where it lives
Protocol cannot enforce it; signing is the only choke point, and the client holds the signer. So the gate is a composer rule: no signature until every assertion is covered.
- Receipt manifest: small JSON, content-addressed (path or fragment carries its sha256), attached to the cast as an embed URL. Other clients just show a link, so it degrades gracefully; this client fetches it, re-hashes, re-resolves, and shows a verified badge.
- Resolvers that need no API key and run in-browser or against the user's own node:
  - cast reference (cited cast hash exists on your node; author and timestamp match)
  - git commit/PR (public GitHub API, CORS-enabled for unauthenticated reads [unverified])
  - URL + content hash (user supplies snapshot hash; verifier re-fetches if CORS allows, else marks "unverifiable from browser")
  - later: EAS attestation, tx hash, zkTLS.
- Honest limit: "receipt resolves and matches" is mechanical; "claim is true" is not. Badge text must say what was checked (coherence is not correctness).
- Scoped signer fits: issue a CAST_ADD-only key for the gated composer; a second, ungated key is a visible choice, and its casts carry no badge.
- Reuse from ARCS (private repo, so rewrite rather than copy into the MIT repo): provenance_lint coverage idea (every quantified claim needs a ledger entry), ADR-044 NOW/NEXT/ASPIRATIONAL tags.

## Risks for the bounty
- Needs a real second human to run the whole tutorial and vouch publicly. Slowest step; start now.
- Sync takes hours; test the quickstart on a fresh VM early.
- Public repo + public reply are publishing actions: need explicit go from Zach, plus the PII gate.
- Seed-phrase handling must be exemplary, since the judge called it out.

## Suggested path (7 days)
D1 provision + node + TLS/CORS proxy on a fresh VM, confirm write path works (settles finding 1). D2 read-only PWA. D3 key issue + post/follow/react. D4 receipts gate v1 (cast-ref + git resolvers). D5 tutorial site + 3-command quickstart. D6 recruit voucher, fix doc drift (PR upstream). D7 submit.
