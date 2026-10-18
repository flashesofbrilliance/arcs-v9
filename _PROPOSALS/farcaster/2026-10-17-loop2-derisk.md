# Farcaster loop 2: derisk rows (draft, nothing sent or spent)

## Loop prediction (written before the work)
- deadline-pin: post time NOT recoverable from page or public API; row ends BLOCKED on Zach reading the hover time. Confidence 85%.
- falsifier set: producible by me now, but check #2 (human-added cases) cannot close. Row stays open.
- budget-guard: README text and teardown commands writable; billing alerts need a cloud account, so BLOCKED on Zach.
- voucher-find: draft only; BLOCKED on Zach naming people.

## Result vs prediction
Matched on all four. Probe: farcaster.xyz page returned 3.7KB shell with no timestamp; client.warpcast.com short-hash lookup 404.

## Deadline (fc-derisk-deadline-pin)
Conservative: 2026-10-24 09:00 EDT = 2026-10-24 13:00 UTC. Treat earlier as binding until Zach reads the exact hover time (screenshot it). Calendar alerts to create once confirmed: D-1 (10-23) 18:00 EDT and D-0 07:00 EDT. Not created: it edits Zach's calendar.

## Budget guard (fc-derisk-budget-guard) README block, to paste before any create
Cap: $150 cash total. Alerts: $25 and $75 (AWS Budgets). Teardown reminder: 2026-10-26.
```bash
# CREATE (only after Zach's go and calculator check) is paired with:
aws ec2 terminate-instances --instance-ids "$IID"
aws ec2 delete-volume --volume-id "$VOL"      # after terminate, if not DeleteOnTermination
aws ec2 describe-instances --query 'Reservations[].Instances[].State.Name'   # expect none running
```
Open: gp3 price for ~2 TB not found; use AWS Pricing Calculator; planning figure 2x to 3x the $100/month claim. Request vCPU quota for m5.xlarge now (needs Zach's account).

## Voucher ask (fc-voucher-find) DRAFT, NOT SENT. Zach picks 1 primary + 2 backups
> Hey [name], I'm entering balajis.eth's Farcaster client bounty. Entries need one other person to run my tutorial cold and vouch publicly on Farcaster (a reply cast quoting the repo URL). It's about 4 to 6 hours mostly waiting on a node to sync, and needs a small cloud VM (16 GB RAM, ~2 TB disk). [VM cost: undecided. Zach has not said whether he covers it; see _PROPOSALS/2026-10-17-farcaster-voucher-ask-zero-spend.md on main, which says the voucher bears their own VM cost.] Use a test account only, never a real seed phrase. You would create your own read node AND your own client (not just endorse), then post publicly about it. I'd need you around [dates, ~10-21 to 10-23]. Up for it? Backups are fine if not.


(2026-10-18) This draft is superseded by the zero-spend ask on main; kept for history. Not sent.
