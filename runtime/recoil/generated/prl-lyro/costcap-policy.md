# Lyro cost-cap policy — PRL Resins (SSOT)
_2026-08-07 · Closes the gauntlet's High-severity cost-bubble finding. Todd's hard constraint: costs must not
balloon after the first crack; he wants a cap he can see, not a routing heuristic. Lyro is billed **per
conversation** (not per message) and quota-metered, so uncontrolled public traffic is a real cost-leak/ruin
vector. This is the hard ceiling._

## The rule
A visible cap beats a hope. Configure so spend **cannot** silently exceed a known ceiling, and Todd is told
before any overage, never after.

## Controls (set in-account when Tidio access lands — verification gate #4)
1. **Overage auto-purchase OFF.** Do not let Lyro auto-buy conversation blocks. When the quota is reached, Lyro
   stops opening new billable conversations rather than spending more.
2. **Graceful floor at quota.** When the Lyro quota is exhausted, visitors fall back to the rule-based Flow +
   human handoff (contact capture still works). The site never goes dark; it just stops spending on AI.
3. **Alert-before-spend.** Set a usage alert at ~80% of the monthly quota that pings Zach/Todd, so any decision
   to raise the cap is a conscious one, made ahead of time.
4. **Gate the billable conversation.** A visitor should pass a cheap qualifying step (a Flow) before a Lyro
   conversation opens, so bots, tire-kickers, and RFQ spam do not each burn a paid conversation. Spend Lyro
   conversations on real questions.

## Blocked-until / to verify in-account
- **Real quota for PRL's plan** — undocumented above Starter; confirm the actual number before quoting Todd.
- **File-import (PDF) tier** — if PDF import is gated to a higher tier, that is a separate plan-cost decision
  (may force paste-as-text instead). Surface as a cost line, not a surprise.

## What Todd hears (his words, not this doc)
"It has a hard ceiling. It can't run up a bill. If it ever gets close, you hear about it first, and the worst
case is it quietly hands people to your team instead of spending more." Never say quota/overage/heuristic to
him — say *capped, predictable, no surprises*.
