# Due diligence: Nous Research, Product Manager, Hermes Agent
Researched 2026-10-06 by web search, page fetches, and the local Hermes clone. The Perplexity MCP was not loaded in this session. Press figures are secondary sources; confirm before quoting them to Nous.

## The company
- Frontier open-source AI lab, founded 2023 by Jeffrey Quesnelle (CEO), Karan Malhotra (Head of Behavior), Teknium (Head of Post Training), and Shivani Mitra. [TechCrunch, 2026-07-13](https://techcrunch.com/2026/07/13/hermes-agent-maker-nous-research-in-talks-for-new-funding-at-1-5b-valuation/): in talks for at least $75M at a $1.5B valuation, Robot Ventures leading; paid hosted tiers reported at $20 to $200 a month; Hermes reported near 214K stars and 40K forks.
- Mission line on [the careers page](https://nousresearch.com/careers): powerful AI "in the hands of the many." 13 open roles, 11 remote.

## The product
- Hermes Agent: MIT-licensed, self-improving agent with a learning loop (skills, memory, cron, subagents), run through CLI, TUI, a messaging gateway, and a desktop app. Desktop went to public preview 2026-06-02. [Startup Fortune](https://startupfortune.com/nous-research-brings-hermes-agent-out-of-the-terminal/) names the open risk: whether it becomes "part of daily work or another interesting tool installed for a weekend." That is the posting's "installation through sustained engagement."
- Hermes Business launched 2026-09-15 (team credits with per-member caps, shared skills, spend intelligence), with an Enterprise tier (SSO, on-prem). [Tao Media](https://www.tao.media/nous-research-launches-hermes-business-for-team-based-ai-agent-workflows/).
- A sibling role, [Product Manager, Hermes Business](https://nousresearch.com/careers/product-manager-hermes-business), requires hands-on SSO, SCIM, RBAC, audit logs and admin consoles. Zach has regulated-release depth but no SSO or SCIM, so it is a weaker fit. Decision: apply to the Agent role only, and say why in the letter.

## How they work (from the repo, snapshot 2026-08-28)
- Commit authorship is concentrated: about 1,600 commits from Teknium since August, then a long tail. A small core plus heavy community flow. Issue and PR numbers are past 133,000, so duplicates are common.
- `AGENTS.md`: per-conversation prompt caching is "sacred"; the core is a narrow waist and capability lives at the edges as plugins and skills.
- `CONTRIBUTING.md`: priority order is bug fixes, cross-platform compatibility, security, robustness, then skills, then tools. Search open and merged issues and PRs before filing.
- Culture line on the careers page: "high-agency and mission focused," "long months of complete focus." Interview with Quesnelle ([TWiT, 2026-06-11](https://twit.tv/posts/tech/what-makes-hermes-agent-stand-out-open-source-innovation-nous-researchs-jeffrey)): community features shipped "often within hours," local-first and model-agnostic.

## Reverse-lookup results
- **Head of Product: not publicly named** in any source found. No named hiring manager, so no one to address by name. Do not guess.
- **Warm path:** none in the 2025-11 LinkedIn export (searched "nous research"). Still worth asking mutual contacts; found none automatically.
- **Public Hermes record for Zach:** a fork (flashesofbrilliance/hermes-agent), zero upstream PRs or issues.

## Honest read on fit
- Strong: agent products shipped, agent-reliability instinct, reads code, regulated release discipline, written communication, US hours.
- Thin: no upstream contribution, small open-source community footprint, no SSO/SCIM, and usage depth. His local install is v0.20.6 (2026-08-27), about six weeks behind, and its session log shows little recent use. The role lists "daily usage of Hermes Agent" as a duty, so the application is only credible if he becomes a current daily user first.

## Implications applied to the bundle
1. Letter and resume say "used" and "since August," not "run daily."
2. The letter ties the trust idea to their own contribution rules (a skill or plugin, not a core tool, no cache invalidation), and commits to a bug fix as the first contribution.
3. The letter states the gaps, including why not the Business role.
4. Next steps below are ordered so the contribution and a current-release rerun happen before the email goes out.
