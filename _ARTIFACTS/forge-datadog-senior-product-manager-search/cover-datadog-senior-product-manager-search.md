# Cover letter — Datadog · Senior Product Manager - Search
_Draft. Plain text below is paste-ready. Add any personal availability note by hand._

---

Hi Datadog team,

I build systems that surface the right answer at the right moment, for users who cannot afford to wait or guess. That is the short version of why this role fits.

Here is the longer one. I built ARCS end to end on Claude: natural-language query staging, an agentic pipeline with MCP-style tool orchestration, and a compounding quality loop that recalibrates from real usage. When I read about Bits AI using MCP tools to respond to natural-language prompts, I did not read it as a candidate. I read it as someone who has already argued through the same design decisions: when does the agent call a tool versus synthesize from context, how do you score retrieval quality when the user never tells you they got the wrong answer, and what does a failure mode look like when the stakes are a production incident at 2am. Those are the conversations I want to have with your Applied AI and Search teams.

A few things I noticed that made me want to write.

Datadog's search surface is genuinely unusual. Most search problems are one user, one query, one result set. Yours spans cmd+k navigation for a human moving fast, query editors for an engineer building a dashboard, and MCP tool calls from an agent that has no patience for ambiguity and no ability to ask a clarifying question. The ranking and personalization model that works for one of those users is wrong for the other two. I built the WTA's real-time fan-behavior scoring engine at sub-120ms latency, serving personalized offers inside a live usage window, and the hardest part was not the speed. It was that the signal you have in the moment is almost nothing, and the model has to be right anyway. Agentic search at Datadog has the same shape: low-latency, sparse signal, high cost of a wrong answer.

The KPI problem here is also interesting. Search quality is easy to measure when users click. It is hard to measure when an agent consumes a result silently and moves on. At Twill Health I built evaluation frameworks and outcome-capture loops for AI-enabled product lines where the feedback signal was delayed and indirect. That is the instrumentation design I would bring to your search quality metrics.

I do not just write the deck. I hold technical tradeoff conversations with engineering, prototype with AI tools before committing engineering time, and have shipped agentic orchestration in production, not experiments. The bundle at the link below has the live commit trail and the open-source tools.

Zach Harris
zachharris.xyz · github.com/flashesofbrilliance

---

## Short version (form-field, ~180 words)

Hi Datadog team,

I build systems that surface the right answer at the right moment, for users who cannot afford to wait or guess. I built ARCS end to end on Claude: natural-language query staging, an agentic pipeline with MCP-style tool orchestration, and a quality loop that recalibrates from real usage. When I read about Bits AI using MCP tools to respond to natural-language prompts, I read it as someone who has already argued through the same design decisions.

Datadog's search surface is genuinely unusual: cmd+k for a human moving fast, query editors for an engineer building a dashboard, and MCP tool calls from an agent with no patience for ambiguity. The ranking model that works for one is wrong for the other two. I built the WTA's real-time fan-behavior scoring engine at sub-120ms, serving personalized offers inside a live usage window, where the signal is sparse and the cost of a wrong answer is high. Agentic search at Datadog has the same shape.

The KPI problem is also interesting. Search quality is easy to measure when users click. It is hard when an agent consumes a result silently and moves on. At Twill Health I built evaluation frameworks for AI product lines where feedback was delayed and indirect. That is the instrumentation design I would bring here.

I do not just write the deck. I hold technical tradeoff conversations with engineering and have shipped agentic orchestration in production, not experiments.

Zach Harris
github.com/flashesofbrilliance

---
_Hook: He has already shipped MCP-style agentic orchestration in production and built a real-time ranking engine at sub-120ms, which means he arrives knowing exactly where Datadog's human-versus-agent search split gets hard._
