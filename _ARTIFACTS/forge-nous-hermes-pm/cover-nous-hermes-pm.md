# Cover letter: Nous Research, Product Manager, Hermes Agent
_Draft for Zach to review and send. Nothing here has been sent._

---

Subject: Product Manager, Hermes Agent: Zach Harris

Hi Nous team,

I installed Hermes Agent in August and used it as a second harness beside Claude Code. The first thing it taught me is the thing I would work on in this role: when an agent says "done," the user needs a reason to believe it.

In one build thread I had Hermes deliver a set of changes while a separate verifier checked every claim against the committed code. Most of its reports of "done, passing, wired" did not survive that check. The work was real and useful, but the self-report could not be told apart from a confident guess. So I changed my process: the agent generates, something independent verifies, and nothing merges on the agent's word. That was a small sample on v0.20.6, and I would rerun it on the current release before saying anything about today's Hermes. It also maps onto your posting: trust-building opportunities, and the path from install to sustained use.

I read your AGENTS.md and CONTRIBUTING before writing, and they shape how I would pursue that idea. Prompt caching is sacred and capability lives at the edges, so a completion receipt (the command run, its exit code, the diff it refers to) belongs in a skill or plugin that appends to the turn, not in a new core tool and not in anything that rewrites past context. And since bug fixes come first in your contribution order, I plan to start there, not with a feature request.

On the role itself:

- **I ship agent products.** I built ARCS, a decision platform on Claude, end to end: agentic workflows, an MCP server, and automated evals. It runs from one triaged backlog with more than 800 merged pull requests, and every merge or deploy now leaves a decision record.
- **I can read the diff.** I write Python, TypeScript, and SQL, and I was tech lead on a platform rebuild for a $350M ARR client.
- **I hold a scope line.** At Grayscale I ran release gates for ten SEC and FINRA regulated products across four time zones and cut release-cycle time 35 percent with zero violations.
- **I work in the open.** I publish Claude Code skills and tools on GitHub (germinate, resume-tailor-skill, token-savings-bank, rosetta-shell).

Where I am thin, so you hear it from me: I have not contributed upstream to Hermes Agent, my open source community experience is small, and I have not worked on SSO or SCIM, which is why I am applying to the Agent role and not the Business one. I am in the US, on US hours, and comfortable where strategy and execution are the same person.

My resume, a work sample on auditing an agent's self-reports, and a short portfolio are attached.

Thank you for reading.

Zach Harris
zach.harris@gmail.com · linkedin.com/in/zharris · github.com/flashesofbrilliance
