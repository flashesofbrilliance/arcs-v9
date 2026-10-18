# Farcaster entry: what only Zach can unblock (dependency doc, 2026-10-17)

Parent session (this branch) owns this list and talks to Zach. The child session `fc-cli-loop2` (branch `claude/fc-cli-loop2-d953c2`) does the work that needs no Zach input and never chases these items. Downstream counts are computed from `depends_on` in the 33 `fc-*` rows (non-container rows only). Conservative bounty deadline: 2026-10-24 09:00 US Eastern; the exact post time is still unknown (Z1).

| # | Zach does | Unblocks (rows, count) | Needed by | Zach time | If no answer |
|---|-----------|------------------------|-----------|-----------|--------------|
| Z4 (NOT APPROVED as of 2026-10-17 ~21:30 ET: Zach said "I dont wanna spent 150 right now"; scope unknown: not tonight, a smaller cap, or stop) | Pick a cloud account, approve the $150 / ~40 h stop-loss as spend authority, and request quota for a 16 GB / 4 vCPU / 2 TB instance | `fc-derisk-budget-guard`, then `fc-node-spike` and everything after it (17 rows incl. both probes, core, signer path, CLI, tutorial, publish) | tonight 2026-10-17 (sync takes hours; checkpoint 1 is end of 10-18) | 20 min | Nothing starts. Checkpoint 1 is missed; the stop-loss says cut scope or stop. |
| Z5 | Fund a throwaway wallet with about $10 to $15 of ETH on Optimism and register a test FID | `fc-derisk-wallet-funding`, then `fc-derisk-write-path-probe`, signer, CLI, gate, tutorial (14 rows) | 2026-10-18 | 20 min | Write-path probe cannot run; no signed cast, no entry. |
| Z1 | Read the exact post time (hover the timestamp on the cast, screenshot it) | `fc-derisk-deadline-pin`, then `fc-publish` and `fc-teardown` (2 rows) | today | 1 min | Treat 2026-10-24 09:00 EDT as binding. |
| Z2 | Name one primary and two backup voucher candidates; send the ask yourself (draft exists in `_PROPOSALS/farcaster/2026-10-17-loop2-derisk.md` on the child branch) | `fc-voucher-find`, `fc-voucher-cold-run`, then publish and teardown (3 rows) | a yes by 2026-10-19; voucher starts by 2026-10-21 | 30 min plus replies | No voucher means no qualifying entry. |
| Z3 | Confirm you will cover the voucher's VM cost (the draft says "I'll cover the VM cost") | the ask cannot go out as written | with Z2 | 1 min | Remove the sentence; expect more declines. |
| Z6 | Add three hard cases to the gate test set, or delegate to the `chief-loki` agent | `fc-derisk-gate-falsifier-set`, then gate v1, tutorial, voucher run, publish (10 rows) | 2026-10-19 | 30 min | Agent-authored cases only; the set is labelled weaker. |
| Z8 | Voice edit pass on the tutorial | `fc-tutorial-draft` quality (judged at the poster's sole discretion) | 2026-10-22 | 1 h | Ships unedited; slop risk rises. |
| Z7 | Say go to publish: public MIT repo, microsite, reply with three URLs | `fc-publish`, `fc-teardown` | evening of 2026-10-23 | 10 min | No entry. |
| Z9 | Decide whether other people's casts may ever be graded (earned opinion score) | `fc-eos-source-grader` only; not on the bounty path | not needed | 5 min | Stays HELD. |

Order by leverage: Z4 and Z5 each gate more than ten rows, so they come first; Z1 is the cheapest and settles the deadline; Z2 and Z3 are the long pole because a human has to finish a multi-hour run before the deadline.

Hard rule across all of these: nothing public, sent or spent until Zach says so.

## Z4 status and the zero-spend path (added 2026-10-17 night)
- Relayed from another session at Zach's request; no file, row or plan was changed on that basis beyond this note. It is not a stop decision. Zach still needs to choose: not tonight, a smaller alert-gated cap, or stop.
- Still blocked until Z4 moves: `fc-derisk-budget-guard`, `fc-node-spike`, the probes, and every row behind them (checkpoint 1 slips).
- Not blocked by Z4 (zero spend): Z1 (post time), Z2 and Z3 (voucher names and the ask, which Zach sends himself), tutorial and microsite drafting, the child session's fixtures and offline tests, doc-fix PR research.
- Recommended order while Z4 is open: recruit and confirm the voucher first, spend only after a named commitment (this was the top-ranked path in the seed-agent conductor run in another session; advice, not a decision).
- Home compute check (read-only, 2026-10-17): this Mac has 16 GB RAM, 8 CPUs and 88 GB free of 926 GB, no external volume, and no Docker daemon running. Snapchain's docs ask for about 2 TB of disk, so it cannot run here without added storage; an external 2 TB drive would be a purchase of its own (price not checked).
- Rough size of a smaller cap, from unverified inputs: EC2 m5.xlarge at about $0.192 per hour is about $32 for 7 days; 2 TB gp3 storage for a week is unpriced (about $37 if the remembered $0.08 per GB-month holds). That points to roughly $70 for our node for a week, before the voucher's own node. Verify in the AWS calculator before acting.

## Decision (Zach, 2026-10-17 night, in chat): zero-spend first
- Z4 stays HELD: the $150 is not approved tonight. Spending is decided only after a voucher has committed. This replaces the open "not tonight, smaller cap, or stop" question above; the entry is not stopped.
- Proceed now, zero spend: voucher recruiting (Zach names people and sends the ask himself), tutorial concept drafting from public docs, offline tests and fixtures, doc-fix PR research.
- Hold: `fc-derisk-budget-guard`, `fc-node-spike`, both probes against a live node, anything that provisions or pays. Still unanswered: Z1, Z2, Z3, Z5.
- Consequence: checkpoint 1 (node synced, one signed write by end of 10-18) is missed. Per the stop-loss rule, next step is to re-plan the dates once a voucher commits; the later the commit, the less room for a multi-hour node sync before the deadline of about 2026-10-24 09:00 ET.
