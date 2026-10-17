# Cold-molt brief: Farcaster CLI client entry, loop 2

You are a fresh session with no memory of any earlier conversation. Everything you need is in this brief and the committed files it names. Start from the repo branch `claude/farcaster-receipts-client-1506aa` (its tip carries everything this brief names; nothing is pushed or merged to main).

## Ground truth (checked 2026-10-17; tags: read = source was read, stated = taken from a message and unchecked, untested = needs a live probe)
- The bounty (read): balajis.eth posted https://farcaster.xyz/balajis.eth/0x50184b62. Prizes $2,048 first, $512 second, $128 honorable mentions. Required: three commands (provision compute, run a Snapchain read node, run a client that reads from that node), no API keys. The client imports an existing seed phrase, issues itself an app key, reads the feed, posts, follows, reacts, and includes or excludes casts from other clients. An entry needs a microsite with quickstart and tutorial, a public MIT GitHub repo, and a second human who completes the tutorial and vouches publicly on Farcaster. The reply with three URLs is due seven days after the post.
- The post time is not recoverable from the page (it shows relative times only). Conservative deadline: 2026-10-24 09:00 US Eastern. Pin the exact time first.
- The poster's clarifications in the thread (stated): read nodes do accept writes and relay them to validators; app keys are gasless; the tutorial must treat seed phrases as dangerous (test accounts only, delegated signers where possible). "Mobile- and desktop-friendly" applies to the tutorial, not the client.
- Docs and source (read): a Snapchain read node needs 16 GB RAM, 4 vCPU, about 2 TB disk, and hours to sync. HTTP API on port 3381 serves /v1/events (parameters from_event_id, shard_index, stop_id, pageSize) and POST /v1/submitMessage. Gasless signers use a KEY_ADD message (engine V16). Storage costs $7 per unit per year.
- Package check (read, not executed): npm `@farcaster/core` 0.20.0 exports makeKeyAddBody, makeKeyAdd, getGaslessSignedKeyRequestMetadata, NobleEd25519Signer, ViemLocalEip712Signer, makeCastAdd, makeLinkAdd and makeReactionAdd.
- Cost (partly untested): EC2 m5.xlarge is about $0.192 per hour (aggregator page, July 2026). The gp3 price was not found. Snapchain's own AWS guide says roughly $100 per month, which is probably low. Treat real cost as 2x to 3x until the AWS calculator says otherwise.
- Untested joints, prove these first: the events endpoint covers every message type we need; gasless KEY_ADD plus a relayed cast merges on mainnet; the real monthly cost.

## Decisions by Zach (final unless Zach reverses)
- CLI/TUI first, BBS style, works over SSH. A local browser UI comes later over a 127.0.0.1 bridge. Same event model: poll node events with a saved per-shard cursor; hooks (pre-sign, post-merge, on-mention) are scripts that receive one event as JSON on stdin. The receipts gate is the default pre-sign hook.
- Design-system work is parked. The `ds-*` rows in the design-system backlog artifact on that branch are drafts only.
- Stop-loss: cash cap $150, about 40 hours, checkpoints at end of day 2 (node synced, one signed write merged) and day 4 (CLI posts, follows, reacts).
- North star is an earned opinion score (hypothesis, unmeasured; see `runtime/specs/lore.jsonl`, entry lore-008). Version 1 scores only our own tutorial claims. Grading other people stays held.
- Nothing public, sent, or spent without Zach's explicit go.

## SSOT
- 33 `fc-*` rows in `_QUEUE/induced-backlog.jsonl` with fields altitude, form, serves, depends_on, derisks, blockers, failure_modes, invariants (I1 to I7). Allowed states are in `runtime/specs/backlog-status.json`.
- Notes: `_PROPOSALS/2026-10-17-farcaster-receipts-pwa.md` (research) and `_PROPOSALS/2026-10-17-farcaster-roadmap-idea-loop.md` (roadmap, costs, taxonomy, pre-mortem).

## Routes (first action is an action, not a re-read)
1. Do the READY rows, smallest first: `fc-derisk-deadline-pin`, `fc-derisk-budget-guard`, `fc-derisk-gate-falsifier-set`, and a draft-only `fc-voucher-find` message for Zach to send. Mark each row's state in the queue as it moves.
2. After Zach approves spend and funds a throwaway wallet: `fc-node-spike`, then the two probes (`fc-derisk-events-probe`, `fc-derisk-write-path-probe`). These can kill the plan; run them before building the client.
3. Then build in this order: `fc-core-events`, `fc-signer-bundle`, `fc-cli-client`, `fc-receipts-gate-v1`, `fc-tutorial-draft`.

## Gates
- After any queue edit run `python3 scripts/backlog_status_check.py --check`.
- Merge only with `gh pr merge --merge`. Allocate any ADR or receipt number with `python3 scripts/oracle.py next <namespace>`; never infer one.
- Run repo scripts from your own worktree, not the main checkout.
- Any HTML added under `_ARTIFACTS/` must pass the repo pre-commit gates (wrap lint, lane edge, token and component source, design findings).
- Never use a main wallet or real seed phrase. Never send a message or open a public repo without Zach's go.

## Corrections: belief updates from the prior loop (prior -> posterior, evidence)
1. PWA is the client -> CLI first. USER-CHALLENGE plus the bounty text, re-read.
2. A seed import costs an Optimism transaction and read nodes refuse writes -> app keys are gasless and read nodes relay writes. EXTERNAL-SOURCE: poster's thread and the Snapchain docs.
3. Browser writes to a node are fine because CORS defaults to `*` -> the node has no OPTIONS handler, so browser POSTs likely fail. CORPUS-READ: `http_server.rs`; untested live; moot while the client is a CLI.
4. A Farcaster client called Super was acquired by Farcaster -> unconfirmed. EXTERNAL-SOURCE: searches found only Neynar acquiring Farcaster (January 2026) and one unverified report of Network School acquiring it (October 2026).
5. The backlog was deep enough -> it was shallow; it now carries failure modes, typed blockers, derisking rows, a five-altitude by five-form taxonomy and seven invariants. USER-CHALLENGE. Ground: the `fc-*` rows in `_QUEUE/induced-backlog.jsonl`, method from ADR-058.
6. Gates I had run were the gates that apply -> the repo's pre-commit design gates rejected three rounds of the artifact. CORPUS: the gates themselves. Run all pre-commit gates before calling an artifact ready. Ground: `scripts/component_source_gate.py` passed while the kintsugi design gate in `scripts/git-hooks/pre-commit` still failed.
7. The earned-opinion idea is new -> a one-line ancestor exists as lore-008 ("Trust is an outcome of a successful earned opinion"). CORPUS-READ. Ground: `runtime/specs/lore.jsonl`.
- Not counted as revisions: the "2x to 3x cost" figure and the deadline estimate. Both are my estimates, still unverified.

## Close protocol
- Work in small loops. Each loop: state the smallest shippable improvement and how it will be validated (written before doing it); do it; compare the result to the prediction; record the belief that moved and the evidence (kind and source); change one thing about how you work; then close with a Shavasana cap.
- A mid-turn message from Zach (a "btw") is a small loop inside the running one. Classify it as a correction, a new task, or a consequential instruction slipped in casually. A consequential instruction (spend, send, publish, mint, commit to shared canon) needs an explicit confirm. If it takes more than a few tool calls, move it to its own session. Close it with a one-line cap: what changed, which claim moved, what remains.
- Shavasana cap (no new claims): counts of commits, merges and outward actions; counts of external data that moved a belief; counts of challenges accepted and pushbacks made; each claim re-read cold, released if it does not survive; Zach's felt certainty now versus at the start; then release the act or return it to the queue. Spec: `runtime/specs/operator-25-shavasana-v0.md` (candidate, unbuilt; the cap is a manual checklist, not a tool).
- Reuse the weekly token kaizen routine for cost; do not build another loop.

## Open items for Zach
- Who the voucher is, and whether to cover their VM.
- Fund a throwaway wallet with about $10 to $15 of ETH on Optimism.
- Which cloud account and budget to use for the node.
- The exact post time, if Zach can read it on a device.
