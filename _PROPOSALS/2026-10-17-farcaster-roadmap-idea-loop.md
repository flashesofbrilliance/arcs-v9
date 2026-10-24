# Farcaster receipts client: roadmap via the I.D.E.A. loop (2026-10-17)

Prior art: `scripts/prior_art.py` run on this job. Applicable hits: AGENTS.md "Receipts or it didn't happen", ADR-044 (temporal provenance gate), ADR-058 (I.D.E.A. construction), memory `tool-fit-marker-convention`, `met-at-your-level-onramp-design-principle`, `drift-receipt-loop-and-inchworm`. Research base: `_PROPOSALS/2026-10-17-farcaster-receipts-pwa.md`.
Catalog cross-referenced: `runtime/specs/tool-catalog.json` = 269 tools (178 scripts, 48 operators, 21 skills, 15 commands, 3 packages, 2 workflows, 2 hooks). Fit calls below come from each tool's catalog `jtbd` line, not from running it.
Status: PLAN. No code, no queue rows written, nothing published.

## I.D.E.A. pass (run inline; 9-agent fan-out judged not worth the tokens for a 7-day plan)

- **Alchemist (claim a cheap test can kill):** "A stranger can go from nothing to a node-backed Farcaster PWA that refuses to sign an unreceipted claim, in three commands, by 2026-10-24." MECHANISM: node, signer, resolvers, composer gate. METAPHOR: "hyperstition", "diamond cut".
- **Detective (the joint most likely to break):** the browser-to-node write path (CORS preflight on POST, TLS). Cheapest test: a 20-line `fetch` POST from an HTTPS page to a freshly synced node. Kill line, fixed now: if no working write path in 6 hours of work, switch to the proxy (Caddy) fallback; if the proxy path also fails by end of day 2, the PWA plan is dead and we ship a Node CLI composer instead.
- **Curator (one orthogonal reframe):** the stated question is "how do we build a better client?" The prize is a tutorial a stranger can follow. The receipts gate is the differentiator, but the cold-run is the product. Humans decide whether to adopt this reframe.
- **Loki test (before building):** falsifier = a second human completes the quickstart cold and vouches publicly. Anything that does not move that is cut.

## Jobs to be done, ranked (risk-kill value x bounty necessity / cost)

| # | Job | Why now | Kill line | Cost prior |
|---|-----|---------|-----------|-----------|
| 1 | Find the voucher | Long pole; needs a human, cannot be compressed | none by D3 -> widen ask | 1 h/day, async |
| 2 | Provision + node + TLS/CORS proxy (one script) | Settles the biggest unknown; sync takes hours so start first | see Detective | 4-6 h + sync wait |
| 3 | Signer: wallet-sign EIP-712 KEY_ADD, scoped + short TTL; seed import as secondary | Required by the bounty; security-critical | KEY_ADD rejected on mainnet after 4 h | 6 h |
| 4 | Read-only PWA: feed fan-out, thread, profile, requestFid filter | Cheap once the node answers | feed >3 s on local node | 8 h |
| 5 | Write: cast, react, follow, pending->merged state | Needs 3 and 4 | message accepted but never merges (gossip loss) -> resubmit logic | 6 h |
| 6 | Receipts gate v1 (cast-ref + git resolvers + manifest) | The differentiator | resolver adds no signal beyond "link present" on a 10-claim test set | 8 h |
| 7 | Tutorial + 59 s video + quickstart page | What judges score | cold-run fails at any step | 8 h |
| 8 | Upstream doc PRs for drift found on the way | Explicitly rewarded | none | 2 h |
| 9 | Publish repo + reply | Outward-facing; needs Zach's go + PII gate | n/a | 1 h |

Cut for now: push notifications, search, ranking, Chinese translation (nice extra; only if days remain).

## Sequence, bundle, nest

- **Bundle A, Node** = jobs 2. One script: provision, snapchain-bootstrap, Caddy TLS + CORS. Command 1 and 2 of the quickstart.
- **Bundle B, Signer** = job 3. Wallet path default; seed path warned, in-memory only; scoped key (CAST/REACTION/LINK), 7-day sliding TTL, visible self-revoke.
- **Bundle C, Client core** = jobs 4 and 5. Static PWA on `@farcaster/core` + `hub-web`.
  - **Nested in C:** Bundle D, Receipts gate (job 6), inside the composer. Gate is a pure function `canSign(draft, receipts) -> {ok, unmet[]}` so it is testable without UI.
- **Bundle E, Proof and publish** = jobs 1, 7, 8, 9. Wraps everything; runs last except job 1.
- Order: A -> B -> C -> D -> E, with job 1 running in parallel from day 1.

## System design (condensed)

```
Browser PWA (static, HTTPS) --GET/POST--> Caddy (TLS, CORS) --> Snapchain read node :3381
   | IndexedDB: app key, feed cache, manifests                        | gossip -> validators
   | @farcaster/core: build + sign messages (Ed25519)
   | gate.canSign(): resolvers (cast-ref -> node; git -> GitHub API; url+hash -> user-supplied)
   | wallet: EIP-712 signTypedData for KEY_ADD (one time)
Receipt manifest: JSON, sha256 in its URL, attached as cast embed; other clients see a link.
```
Non-functional: one user per deployment; node is the only stateful dependency; cost = one VM. Revisit if: multi-user hosting, push notifications, or feed latency on large follow graphs.

## ADR draft (number from `python3 scripts/oracle.py next adr` at commit time; do not infer)

- **Decision:** static PWA on `@farcaster/core` + `hub-web`; gate lives in the client composer; node fronted by Caddy.
- **Rejected A, fork `farcasterxyz/client`:** points at Farcaster's production API, so the data layer must be replaced anyway; larger surface to learn in 7 days.
- **Rejected B, herocast:** AGPL-3 cannot enter an MIT repo.
- **CORRECTION 2026-10-17 (Zach):** the bounty text puts "mobile- and desktop-friendly" on the TUTORIAL, not the client. A CLI/TUI client (BBS-board style, run over a terminal or SSH) is allowed. A Node client also has no browser CORS or mixed-content limits, which removes the two biggest risks found in the research notes. New leading option: **CLI/TUI first** on `hub-nodejs`, with the PWA as a stretch that reuses the same core library (signer, resolvers, gate). The earlier "Rejected C" reasoning was wrong and is withdrawn.
- **Consequences:** easier: zero backend, cheap hosting, auditable. Harder: key custody in browser storage; CORS depends on the proxy; no push.
- **Revisit:** if upstream node adds OPTIONS handling (then drop the proxy's CORS role).

## Plan review (/code-review lens; there is no code yet, so this reviews the design)

Critical
1. App key in IndexedDB is readable by any script on the origin. Strict CSP, zero third-party scripts, scoped key, 7-day TTL, self-revoke button. Treat as the top security item.
2. Seed phrase: JS strings cannot be reliably zeroed. Say so in the tutorial; default to wallet signing; test account only.
3. Write path unverified (CORS preflight, TLS). Do job 2 first.
Important
4. "Accepted" is not "merged". UI must show pending, merged, failed; resubmit on timeout.
5. Render receipt manifests as text only; never inject manifest HTML.
6. Verify gasless-signer engine version on the live node (`/v1/info`) before relying on it; docs say live as of V16.
7. Feed fan-out is N+1: cap followees fetched, concurrency ~6, cache in IndexedDB.
8. Dependency licenses must all be MIT-compatible before publishing; Snapchain stays a separate GPL process.
Nice to have
9. Badge text says what was checked ("2 of 2 receipts resolve"), never "true". Coherence is not correctness.

## UI direction (/impeccable shape, planning only; mode Operate for the client, Read for the tutorial)

Assumed answers, flagged for Zach: audience = developers and curious Farcaster users; tone = calm instrument, not crypto-neon; one signature object = the receipt chip.
- Receipt chip: compact, monospaced hash fragment, resolver icon, state (resolved / unresolved / not checkable here). Tap expands to what was fetched and compared.
- Composer: the gate is visible, not a modal. Unmet claims are underlined inline with a "needs receipt" slot; Sign stays disabled with the reason in words.
- Feed: dense, readable, two states only for casts (receipts-verified or plain); no engagement-bait counters.
- Tutorial: Read mode, three numbered commands at the top, concepts explained as you go (FID, custody, app key, read node vs validator, storage), mobile-first, one measure for body text.
- Open questions for Zach: (a) ARCS visual world or a neutral one for the public repo? (b) name for the client; (c) light/dark default.
- Rules to carry in: no Tailwind-style utility sprawl is an ARCS rule, but this repo is separate; decide its styling approach (plain CSS tokens) before day 3. Run `impeccable` craft-floor read before the first UI edit. Verify in one batched pass, not a loop.

## Tool map (catalog -> job). "Method" = idea reused, code stays private; this repo is public MIT.

| Job | Tool | Kind | Note |
|-----|------|------|------|
| plan | `/prior-art`, `/catalog`, `scripts/oracle.py`, `scripts/backlog_status_check.py` | cmd/script | numbering and queue hygiene |
| gate design | `scripts/provenance_lint.py` (claim -> ledger coverage), ADR-044 (NOW/NEXT/ASPIRATIONAL), `scripts/blog_provenance.py` (manifest emit/verify), `scripts/case_evidence_lint.py` (every number traces to a source) | method | fit for the manifest format unverified; read before borrowing |
| security | `ciso-review` agent, `privacy-review` agent | agent | run on key storage and manifest rendering |
| verify claims | `claims-skeptic` agent against the live docs; `chief-loki` agent for small falsifiers | agent | tutorial claims must match docs as of that day |
| cold-run | adapt `counterpart-gauntlet` workflow to simulate a stranger; real voucher is the actual test | workflow | simulation does not replace the human |
| page QA | `page-gate`, `scripts/artifact_wrap_lint.py` | skill/script | for the tutorial site, run from the worktree, not main |
| ship | `scripts/merge_train.sh`, `/nci-commit`, Decision Receipt row via Supabase `execute_sql` | script/cmd | receipt per merge/publish (AGENTS.md) |
| memory | `/witness`, `/handoff` | cmd | attest insights live; fold the arc at the end |

## SUPERSEDED: first draft backlog rows (replaced by the 33 `fc-*` rows now in `_QUEUE/induced-backlog.jsonl`; see the Taxonomy section at the end)

```jsonl
{"id":"fc-voucher-find","jtbd":"Recruit one human to cold-run the quickstart and vouch publicly on Farcaster.","state":"READY","outlet":"shared","status_note":"Long pole. Draft outreach for Zach to send; never send for him.","needs":[],"ruin":"high","reach":5,"cost_prior":"author estimate: 1 h/day async"}
{"id":"fc-node-write-spike","jtbd":"Provision a VM, sync a read node, front with Caddy TLS+CORS, prove a browser POST of a signed message merges.","state":"READY","outlet":"shared","status_note":"Kill line: no working write path in 6 h, switch to proxy; fails day 2 -> CLI composer.","needs":[],"ruin":"high","reach":5,"cost_prior":"author estimate: 4-6 h + sync wait"}
{"id":"fc-signer-bundle","jtbd":"Wallet EIP-712 KEY_ADD, scoped CAST/REACTION/LINK key, 7-day TTL, self-revoke; seed import secondary with warnings.","state":"HOLDING","outlet":"shared","status_note":"Waits for the node spike.","needs":["fc-node-write-spike"],"ruin":"high","reach":5,"cost_prior":"author estimate: 6 h"}
{"id":"fc-client-core","jtbd":"Static PWA: feed fan-out, thread, profile, requestFid filter, cast/react/follow with pending->merged states.","state":"HOLDING","outlet":"shared","status_note":"Needs node and signer.","needs":["fc-signer-bundle"],"ruin":"medium","reach":5,"cost_prior":"author estimate: 14 h"}
{"id":"fc-receipts-gate-v1","jtbd":"canSign(draft, receipts) with cast-ref and git resolvers, content-addressed manifest embed, honest badge text.","state":"HOLDING","outlet":"shared","status_note":"Kill line: no signal beyond link-present on a 10-claim set.","needs":["fc-client-core"],"ruin":"medium","reach":4,"cost_prior":"author estimate: 8 h"}
{"id":"fc-tutorial-site","jtbd":"Three-command quickstart + tutorial + 59 s video; concepts explained inline; seed-phrase safety section.","state":"HOLDING","outlet":"shared","status_note":"Cold-run is the acceptance test.","needs":["fc-client-core"],"ruin":"high","reach":5,"cost_prior":"author estimate: 8 h"}
{"id":"fc-upstream-doc-prs","jtbd":"PR any outdated docs found in farcasterxyz repos while building.","state":"OPEN","outlet":"shared","status_note":"Rewarded by the bounty; no AI slop.","needs":[],"ruin":"low","reach":3,"cost_prior":"author estimate: 2 h"}
{"id":"fc-publish","jtbd":"Create public MIT repo, deploy microsite, post reply with 3 URLs.","state":"HELD","outlet":"shared","status_note":"Needs Zach's explicit go and the PII gate; outward-facing.","needs":["fc-tutorial-site","fc-voucher-find"],"ruin":"high","reach":5,"cost_prior":"author estimate: 1 h"}
```

## Day plan (today is Saturday 2026-10-17; deadline about 2026-10-24)

D1 voucher outreach drafted; VM provisioned, node syncing; spike script. D2 write-path proven or fallback chosen. D3 signer. D4 read PWA. D5 write + gate v1. D6 tutorial + video + cold-run by voucher. D7 fix, upstream PRs, publish only on Zach's go.

## Decision 2026-10-17 (Zach): CLI core first, front end later

Build one solid CLI/TUI client on `hub-nodejs` (signer, node reads, writes, gate as a pure function). Any web or design-system layer sits on top of the same core afterward. Consequences: no CORS or TLS work on the critical path; the `ds-*` rows in `_ARTIFACTS/ds-backlog-inducer.html` stay parked (they are not on the bounty path); the gate takes user-tagged claims in v1 (no LLM extraction, so no API key in the client).

## Cost and exposure (estimates, not quotes; verify prices before spending)

| Item | Cash | Time | Note |
|------|------|------|------|
| Read node VM, build + cold-run test | roughly $30 to $120 | 3 h | Snapchain's AWS guide says "roughly $100/month" (m5.xlarge, 2 TB gp3). My own arithmetic from remembered list prices gives about 3x that; check the AWS calculator. Prorated to ~10 days. |
| Voucher's own node | their cost, roughly the same | their ~4 to 6 h incl. sync wait | The voucher must also stand up a node. Ask early; offer to cover their VM. |
| Test FID + storage on Optimism | about $7 to $10 | 0.5 h | Docs: $7 per storage unit per year; registration bundles one unit. Use a throwaway wallet. |
| Microsite + repo | $0 | 2 h | GitHub Pages or an existing arcs.care subdomain. |
| 59 s video (optional) | $0 to $30 | 3 h | |
| CLI build (reads, signer, writes, gate v1) | $0 | ~20 to 25 h | Author estimate; CLI-first removes the PWA/CORS work. |
| Tutorial + quickstart script + cold-run fixes | $0 | ~8 to 10 h | The judged artifact. |
| Zach's own time (voucher, review, go/no-go, wallet steps) | $0 | ~8 to 12 h | |
| Claude subscription usage | unknown | n/a | Weekly cap can stall other jobs; keep fan-out low. |

Stop-loss: cash cap $150; time cap ~40 h; checkpoint 1 (end of day 2) node synced and one signed write merged; checkpoint 2 (day 4) CLI posts, follows, reacts. Miss a checkpoint: stop or cut scope, do not extend.

Biggest surprises to pre-empt: a forgotten VM (set a teardown reminder and a billing alert the day it is created); a main wallet used by mistake (throwaway only); anything private committed to a public repo (PII gate and a clean-room repo); an unpaid or unconfirmed voucher; prize is not guaranteed ("subject to enough good submissions", and judging is at their sole discretion). USDC prizes may be taxable income; check with a tax professional.

## Architecture addendum 2026-10-17 (Zach): one event core, CLI first, local browser UI on top

```
Snapchain read node :3381
   ^ poll GET /v1/events?from_event_id=<cursor>&shard_index=N&pageSize=K   (cursor persisted on disk)
   |
fc-core (Node, no UI)   -- emits typed events: merged, pending, failed, mention, reply, follow
   |  hooks: pre-sign (the receipts gate), post-merge, on-mention (user scripts, same shape as Claude Code hooks)
   +-- TUI / BBS-style client (stdin/stdout, also works over SSH)
   +-- 127.0.0.1 HTTP + SSE bridge  --> local browser UI (design-system layer, later)
```
- Polling is real: the node's `/v1/events` takes `from_event_id` (0 = from the start), `shard_index`, `stop_id` and `pageSize`, so a client can keep a cursor and resume after a crash [doc: Events API]. "Accepted" becomes "merged" when the matching MERGE_MESSAGE event arrives (node-types doc), which gives the pending to merged state for free.
- Local browser UI talks to the CLI's own localhost bridge, not to the node, so the CORS and TLS problems from the PWA path do not apply. Same-origin or an explicit localhost origin allowlist; the app key never leaves the CLI process.
- Hooks: a hook is a script that receives the event as JSON on stdin and may veto (pre-sign) or react (post-merge). The receipts gate is simply the default pre-sign hook, so users can read, replace or add to it.
- Design system: the local UI inherits the kit tokens and primitives (the `ds-*` rows become the FE layer's backlog, after the CLI works). Not on the bounty critical path.
- Open check: confirm the events endpoint on a live node returns MERGE_MESSAGE for casts and links before depending on it for mentions.

## Taxonomy, invariants and pre-mortem (2026-10-17)

Two orthogonal five-step ladders, both already ARCS vocabulary:
- **Altitude (why, top down):** executive, strategic, operational, tactical, surgical (the altitude ladder, memory `altitude-ladder-friction-audit-method`). Every row has `altitude` and a `serves` parent exactly one or more altitudes up (checked). Goals cascade down; state rolls up (a container row's `depends_on` is its children).
- **Form (what, bottom up):** atom, molecule, organism, template, page (atomic design, `src/ui-kit/README.md`). Every row has a `form`. Molecules and organisms that stand alone carry a `package` and a `contract` (in/out) so each can run as a self-sovereign module and be recombined: `fc-core`, `fc-signer`, `fc-gate`, `fc-cli`, later `fc-ui`. For the 7-day bounty these ship as one workspace; the contracts keep them separable.
- Rows by altitude x form: executive 1 page; strategic 3 templates; operational 6 templates; tactical 5 molecules, 3 organisms, 3 pages; surgical 12 atoms. Empty cells are information: no cheap atoms sit under the tactical molecules yet, and nothing at the template level below operational.
- **Invariants** (the layer that never changes while everything else moves): I1 test-only, I2 private-stays-private, I3 honest wording, I4 human gates outward, I5 stop-loss, I6 deadline, I7 fail-closed. Declared at the executive row, inherited by all descendants, and the generator fails if any invariant has no enforcing non-container row (current enforcers: 6, 3, 9, 6, 4, 2, 5 rows).
- **Meso layer** = the six operational bundles (node, signing, client, gate, proof, surface). They are the units to sequence, bundle, nest and re-cluster when the problem changes shape.
- Each row also carries `checks` (the fifth step, surgical atoms inside a row, with ids like `fc-node-spike#2`), `failure_modes` (mode, trigger, mitigation, fallback), typed `blockers`, and `derisks` pointers. Counts: 33 rows, 69 failure modes, 8 typed blockers, 10 derisking rows, longest chain 13 rows deep.

### North star: earned opinion score (hypothesis, unmeasured)
For a source on a topic: claims that held / claims resolved, where each claim is resolved by an external check, claims are chosen by a rule fixed before sampling, and the result is shown as k of n with an interval; "insufficient" below n=30 (borrowed from the Accountant operator, not validated). It generalises `scripts/believability_ledger.py` (stated confidence vs externally resolved outcome). v1 scores only our own tutorial and gate claims (`fc-eos-own-claims`). Grading other people (`fc-eos-source-grader`) is HELD: it is a public statement about named people, so it needs counts and sources shown, a right of reply, a sampling rule fixed first, and Zach's go.

### Pre-mortem (it is 2026-10-25 and we failed; three causes, each with a falsifier)
1. **The gate was theatre.** Falsifier: the 10-claim set (5 false with a resolving receipt) is passed by the gate. Row: `fc-derisk-gate-falsifier-set`, written before gate code. Response: downgrade the badge to "receipt exists".
2. **No qualifying voucher.** Falsifier: no named yes by D3 or no node started by D5. Rows: `fc-voucher-find` (three candidates), `fc-derisk-stranger-sim`. Response: public call for a volunteer; submit nothing without the endorsement.
3. **The write path never worked on mainnet.** Falsifier: no merged cast by end of day 2. Row: `fc-derisk-write-path-probe`. Response: onchain-signer fallback, then a stop-loss review that cuts scope.
- Also watched: cost overrun (`fc-derisk-budget-guard`), a leak into the public repo (`fc-derisk-publish-hygiene`), a missed deadline (`fc-derisk-deadline-pin`).
- Post-mortem, imagined: we shipped on D7, a stranger followed the tutorial, the node needed nine hours to sync, they gave up before posting, and the vouch never came. Root cause: the tutorial did not set the sync-time expectation and the voucher started too late. Fix already in the rows: expected-time text, a progress check, voucher start by D5.
