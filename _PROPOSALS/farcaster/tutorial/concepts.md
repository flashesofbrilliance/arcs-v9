# Concepts (draft, not final)

Status: draft for review. Facts carry a source and the date read. Lines marked UNVERIFIED are not stated as fact. Lines marked RULE are instructions for readers.
Note on sources: links to github.com point at the exact Snapchain repo file at commit fc87f268, which I read. I did not load the rendered snapchain.farcaster.xyz pages.

## 1. FID

- An FID is a Farcaster ID, a number assigned to an Ethereum address when it creates an account through the IdGateway contract. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/accounts (read 2026-10-17)
- UNVERIFIED: An FID is cheap to register. Reason: I did not find a price on the pages I read.

## 2. Custody address and app key

- The custody address owns the account and funds its initial registration and storage. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- The custody private key signs signer requests and fname registrations, and the person registering the account should always hold it. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- An app key, also called a signer, is an Ed25519 key pair that signs the messages you publish. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- If an app publishes for a user, the app holds the private key of that signer. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- Keeping signing keys separate from ownership keys helps keep the account secure. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)
- An account can have a separate key per app. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)

## 3. Messages and how a message becomes merged

- Accounts sign and publish messages. There are five kinds: casts, reactions, links, profile data and verifications. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)
- A valid message must be signed by an authorized account key. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)
- The network rejects a message whose timestamp is more than 15 minutes in the future. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)
- A read node checks that a submitted message is valid and not already merged. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/node-types.mdx (read 2026-10-17)
- A successful response means the message passed validation and was accepted for relay, not that it is in a block. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/node-types.mdx (read 2026-10-17)
- To confirm a message landed, watch for the MERGE_MESSAGE event or query the message back. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/node-types.mdx (read 2026-10-17)
- UNVERIFIED: The exact merge rules for conflicting messages (add and remove). Reason: The messages page only points to the protocol spec, which I did not read.

## 4. Read node and validator

- A read node follows the chain and stores the full state. It serves the HTTP and gRPC APIs, and anyone can run one. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/node-types.mdx (read 2026-10-17)
- A read node has no mempool, so it checks a submitted message, gossips it to validators, and keeps nothing. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/node-types.mdx (read 2026-10-17)
- The message reaches a block only when a validator picks it up from gossip. If the gossip is lost, send the message again. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/node-types.mdx (read 2026-10-17)
- A validator validates submitted messages and includes them in blocks it proposes. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/node-types.mdx (read 2026-10-17)
- A read node is always slightly behind the validators. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/node-types.mdx (read 2026-10-17)
- A read node needs 16 GB of RAM, 4 CPU cores and 2 TB of free storage. Ports 3381 to 3383 must be exposed. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/getting-started.mdx (read 2026-10-17)

## 5. Storage rent

- Accounts pay rent to keep their messages. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)
- When an account passes its limit for a message type, its oldest message of that type is pruned. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)
- After storage expires there is a 30 day grace period, and then the account may lose its messages. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)
- A node reports an FID's limits per message type at /v1/storageLimitsByFid, for example casts, links and reactions. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/reference/httpapi/storagelimits.md (read 2026-10-17)
- The docs page says one unit of storage costs $7 and lasts one year, and lists limits of 5000 casts, 2500 reactions, 2500 links, 50 profile data and 50 verifications. Source: https://docs.farcaster.xyz/learn/what-is-farcaster/messages (read 2026-10-17)
- A Snapchain API example shows much larger limits for one FID: 77000 casts and 38500 links. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/reference/httpapi/storagelimits.md (read 2026-10-17)
- UNVERIFIED: Which limits are current. Reason: the two sources disagree and the docs page may be stale. Check with /v1/storageLimitsByFid on a live node before the tutorial states a number.
- The Snapchain guide says you need about $10 of ETH on Optimism in the custody account for registration and storage. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)

## 6. Gasless KEY_ADD, scopes, TTL and nonces

- Gasless signers are live on mainnet as of engine version V16. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- You register a gasless key by submitting a KEY_ADD message to a node. An EIP-712 signature from the custody address authorizes it. There is no transaction and no gas. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- Every gasless key declares the message types it may sign, so a key scoped to CAST_ADD cannot publish a LINK_ADD. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- KEY_ADD and KEY_REMOVE are never allowed as scopes, so a signer can never mint or revoke another signer. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- Each key has a TTL of at most 90 days. It is refreshed whenever the key signs a merged message. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- Each FID has a nonce counter. Every KEY_ADD must carry a nonce above the current value, so an intercepted authorization cannot be replayed. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- One FID can hold up to 1000 active gasless keys. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)

## 7. Seed phrase safety

- The custody private key controls the account, and the person registering should always hold it. Source: https://github.com/farcasterxyz/snapchain/blob/fc87f2686472598143062a00e1c2b2633b2d87ab/site/docs/pages/guides/writing-messages.mdx (read 2026-10-17)
- RULE (our tutorial's instruction, not a claim about the protocol): Use a test account only. Never use your main wallet or a seed phrase that holds real funds.
- RULE (our tutorial's instruction, not a claim about the protocol): Paste a seed phrase only into software from developers you trust, and prefer authorizing a delegated signer over importing a seed.
- RULE (our tutorial's instruction, not a claim about the protocol): Fund a throwaway account with only what the tutorial needs.
- UNVERIFIED: The contest author's wording on seed phrases. Reason: I have it only second hand from another session's read of the post.
