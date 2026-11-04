# Agent marketplaces for near-term income: decision brief (2026-11-03)

Status: PROPOSED. Read-only research. Nothing was listed, applied for, signed up for or published.
Builds on PR 1987 (`_PROPOSALS/2026-11-03-first-product-decision.md`, branch `claude/first-product-decision`): sell the
Agent Receipts Audit for cash now, and test the MCP probe under its kill rule. This brief does not change that plan.

## Bottom line

Listing an agent and waiting is not near-term income. On Agentalent, 1 of the 19 jobs posted since the launch month
shows a hire (counts below). The only route worth a few hours is to **apply to two open jobs that already match what ARCS
does**, under a kill rule. It is not passive: you host the agent, set up delivery for each buyer, and refund in full on
request for two weeks. The audit outreach in PR 1987 stays the first move for cash.

## What the market shows (read 2026-11-03)

**Agentalent.ai** (monday.com, launched 2026-03-23 with 17 agents, built with AWS and Anthropic; [Constellation][c]).
- Buyers: small and mid-size companies. The 30 open jobs come from monday.com, Wix, Mesh, a law firm, a cleaning company and similar ([jobs][j]).
- Pay: listing is free. You set a monthly rate or a fixed-price gig, and the platform adds 20% on top, paid by the buyer. You get your full rate through Stripe Connect. Retainers pay when the first payment clears and at each renewal. Gigs pay on acceptance, or 3 days after delivery ([Builder FAQ][f]).
- To qualify: the agent runs on your own servers and is reachable over HTTP. It must pass the "Handshake", a 30-minute automated test (up to 3 tries) scored 0 to 100 by an LLM judge, where any failed safety task fails the agent. Then an admin approves it, with "no fixed timeline, currently selective" ([Builder FAQ][f]). Each application to a job gets its own evaluation and score ([Builder API][a]).
- Supply: 177 agents listed. One builder has 7 of the 12 top-scored agents. Listed rates include $3,000/mo for a recruiting coordinator, $4,000/mo for an IT helpdesk agent and $6,000/mo for an underwriting assistant ([browse][b]).
- Demand (all 30 cards on the jobs page, counted by hand):

| Jobs | Count | Show HIRED |
|---|---|---|
| Posted in the launch month (7 months ago) | 11 | 9, all posted by Agentalent, monday.com, Mesh or Wix (the platform, its parent and two launch partners) |
| Posted since then (6 months ago to 1 week ago) | 19 | **1** (NanoCo, $3k/mo) |

  Of the 19 newer jobs, 13 show a monthly budget: median **$2,000**, range $100 to $7,000. Four say "Negotiable". The newer jobs have 0 to 10 applicants each.
- Upkeep: no SLA is published. In practice, how work reaches the agent is agreed with each buyer, so every hire is a small integration. Refunds are case by case, with a full refund inside the first two weeks. Model costs come out of your rate.

**Other markets, for comparison**

| Market | Builder share | What earnings are public | Fit for near-term cash |
|---|---|---|---|
| Apify Store | About 80% of revenue minus costs, paid monthly ([Apify docs][ap1]) | Apify says it paid "over $1M" to developers in one month; the year is not shown ([Apify blog][ap2]) | Poor. Our job-board adapters already exist there several times over, priced $1 to $5 per 1,000 jobs ([search][ap3]) |
| GPT Store | US only, engagement-based pilot | None published ([OpenAI forum][g]) | None |
| AWS Marketplace, AI agents category | Revenue share on paid listings; fee not confirmed here | None | No. Seller registration and enterprise sales, months not weeks ([AWS][aws]) |
| Upwork / Fiverr (human services) | Upwork takes 0 to 15% per contract ([Upwork][u]); Fiverr takes 20% ([fee guide][fv]) | Not checked | Real buyers, but this is freelancing, not an agent listing |

Vendor blogs put marketplace shares at 70 to 85% to the builder ([Pickaxe][p]). They give no checked earnings, so this brief does not use them.

## The two agents to put forward (fastest from what exists)

Picked by matching open Agentalent jobs to ARCS parts that already run. Resume-tailor and job scoring were checked and
left out. Their buyer is a job seeker, not a company. The company-side versions (Slate at $3k/mo; "Job Hunter" and
"Hiring & Matching" jobs) are already filled.

| | 1. Tools and frameworks evaluator | 2. AI roadmap with a go/no-go |
|---|---|---|
| Open job it answers | "AI Tools & Frameworks Evaluator", $1k/mo, posted 2 months ago, 1 applicant | "AI Strategy Consultant, Internal Learning & HR Enablement", posted 9 days ago by an account named "monday" (company type "Startup", joined October 2026, no person named; not the "monday.com" account behind the launch jobs), $3k per project over 3 months, 0 applicants |
| ARCS parts it reuses | `scripts/research_render.py`, `scripts/prior_art.py`, Perplexity MCP (mcp.arcs.care), receipts that list what is confirmed and what is not | Compass L0 to L5 with the Loki counter-argument, the ex-ante receipt, the brief's confirmed/unconfirmed split |
| Why it fits | Their ask is the receipt grammar: "clear trade-offs, a recommendation, and the reasoning" | Their ask includes "a no-go if content access constraints make that the honest answer", which is the brand promise |
| Build to qualify | One HTTP endpoint that takes a task and returns a scorecard, enough to pass the Handshake. About half a day (estimate) | Same endpoint, roadmap template. Zach does the scoping himself |
| Earnings if won | $1,000/mo, minus model costs | $3,000 for the project; payout timing for a project job is not stated |
| Honest caveat | Thin: one $1k/mo buyer, and the post may be stale | monday.com rejected Zach for the FDE role on 2026-11-02. Applying is his call alone. It is consulting work wearing an agent label |

**Expected earnings, first 60 days: $0 base case; $1,000 to $4,000 if one or both are won.** Odds of any Agentalent
dollar inside 30 days: about 1 in 10. That is my judgment, not a measurement. It rests on 1 hire among the 19 newer
jobs and an approval step with no timeline.

**Time to first dollar:** at least 2 to 3 weeks if everything goes right (Handshake, then approval with no fixed timeline,
then selection, then delivery, then payout on acceptance). It could be never.

## Kill rule (set before anything is built or submitted)

- Budget: at most 6 hours of Zach's time and $25 of model spend, counted from the first line of code to the first dollar.
- Stop if any of these happens: the agent fails the Handshake 3 times; admin approval is not granted within 10 business days of submission; or neither application gets a buyer reply within 15 business days of approval.
- On a stop: file a falsified receipt for "Agentalent is a near-term income channel" and do no more marketplace work. Fold the endpoint into the MCP probe only if PR 1987's precision test has passed.
- Applicant counts, agent views and badges do not count. Only a buyer reply or a payment does.

## What Zach must do himself (Claude will not)

1. Decide: apply to job 2 (monday) or not.
2. Create the Agentalent builder account and accept its terms.
3. Complete Stripe Connect onboarding (bank and tax details).
4. Submit the agent, start the Handshake, and send each application. Sign any NDA a buyer asks for.

With a go, Claude can: build the one endpoint on a branch, dry-run it on sample evaluator tasks, draft both applications
for Zach to edit and send, and file the ex-ante receipt (ADR-068) before the send.

## Decisions for Zach

1. Go on job 1 only, jobs 1 and 2, or no marketplace work (the audit outreach in PR 1987 continues either way).
2. If go: approve the kill rule above as written.

[c]: https://www.constellationr.com/insights/news/monday-launches-ai-agent-marketplace
[j]: https://agentalent.ai/jobs
[f]: https://agentalent.ai/builder-faq
[a]: https://agentalent.ai/builder-api
[b]: https://agentalent.ai/hire/browse?tab=full-time
[ap1]: https://pr-2484.preview.docs.apify.com/platform/actors/publishing/monetize
[ap2]: https://blog.apify.com/programmer-passive-income-web-scraping/
[ap3]: https://apify.com/quietloop-labs/ashby-greenhouse-lever-job-scraper
[g]: https://community.openai.com/t/what-is-the-status-with-gpt-store-revenue-share/839172
[aws]: https://aws.amazon.com/about-aws/whats-new/2025/07/ai-agents-tools-aws-marketplace
[u]: https://www.upwork.com/resources/is-upwork-free
[fv]: https://www.websiterating.com/productivity/fiverr-fees-explained/
[p]: https://pickaxe.co/post/monetize-ai-agents-2026
