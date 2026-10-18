# Farcaster probes (written, NOT run)

Nothing here has been executed. Both need a live Snapchain read node; the write probe also needs Zach's go and a funded throwaway account.

## events-probe.mjs  (read-only; needs `FC_NODE_URL`)
Proves: `/v1/events` answers per shard with `from_event_id`; which event types and message types appear on shards 0, 1, 2 in a bounded sample; that restarting from a saved cursor yields no duplicate and no gap IDs inside the sample.
Cannot prove: that every message type we need (reaction, link, cast) occurs (it reports missing ones, a short sample may simply not contain them); correctness at chain tip under reorg; behaviour over days; that event ID field names match (the probe guesses `id|event_id|eventId` and prints keys if none fit); that a node that is still syncing returns complete data.

## write-path-probe.mjs  (WRITES to mainnet; needs the key guard env)
Proves (if it passes): `@farcaster/core` 0.20.0 builds a gasless KEY_ADD, the node accepts it via `POST /v1/submitMessage`, a cast signed by the new app key is accepted and readable via `castById`.
Cannot prove: that the message was relayed to validators and merged network-wide (only that this node serves it; the events cross-check is separate); anything about delegated signers beyond this one key; cost; rate limits; that helper signatures are right (they are from documentation, unverified: a throw at import or call is itself the result).
Guard (`guard.mjs`): refuses a seed phrase, anything not 0x+64 hex, a missing exact acknowledgement string, a missing FID, or a FID on `FC_DENY_FIDS`. It cannot know a wallet's balance without a network call, so "under about $15" rests on the acknowledgement, not on a check.

Install (not done): `npm i @farcaster/core@0.20.0 @farcaster/hub-nodejs@0.17.0 viem @noble/curves`.

## Known assumptions (reviewer finding 9; not yet checked against a real node)
- Event IDs are block-based and not contiguous across blocks (example IDs in the Snapchain events API doc: 151622205440, then 151622205441 within one block). So gap detection no longer uses +1 steps: order must be strictly increasing, and completeness is checked against BLOCK_CONFIRMED.totalEvents when supplied. Wiring `blocks` from live pages is still TODO in events-probe.mjs. Source: snapchain site/docs/pages/reference/httpapi/events.md @ fc87f268 (read 2026-10-17).
- Hubs prune events older than 3 days (same page), so a cursor older than that cannot be replayed.
- An empty page after data means the node is at head and is accepted; an empty page before or between data, or no data at all, is `fallback` (inconclusive).
- The restart-from-cursor check uses an in-process cursor (max id + 1), so it can only detect server-side overlap, not a cursor file corrupted between runs.
- The offline self-test shows the classifier is consistent with these rules, not correct against real Snapchain output.
