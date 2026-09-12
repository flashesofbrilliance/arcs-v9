# Cover letter — Datadog · Senior Product Manager - Bits Agent Builder
_Draft. Plain text below is paste-ready. Add any personal availability note by hand._

---

Hi Datadog team,

I build the platform, then become the most demanding user of what I built. That is the short version of why this role fits.

Here is the longer one. The Bits Agent Builder role asks for someone who can own the ecosystem that lets customers, partners, and internal Datadog teams build, deploy, and govern AI agents on top of a production-grade observability platform. I have been building exactly that kind of system. ARCS is an AI-native platform on Claude with an agentic pipeline, tool-calling interfaces, an evaluation and outcome-capture framework, and extensibility patterns that let other workflows build on top of it. Not experiments. In production. I own the roadmap, the architecture decisions, the failure-mode handling, and the human-deferral logic for low-confidence outputs. When I read the Bits Agent Builder JD, I did not read it as a candidate. I read it as the person who has been arguing through these exact tradeoffs every week.

A few things I noticed that made me want to write.

Datadog's moat here is not that you have an agent builder. It is that your agent builder sits on top of the richest production-signal substrate in the industry. Logs, traces, metrics, security events, deployment context: the context that makes an agent actually useful in an operational setting is context Datadog already owns. The extensibility model you build is only as valuable as the grounding it gives agents, and no one else has that grounding at your depth. The question I would want to argue with you about is whether the win is the agent canvas or the context layer underneath it. My instinct is the context layer. That is where the defensible moat lives.

The governance and failure-mode problem is the one I find most interesting and the one I think is most underspecified in the market right now. I built human-deferral logic and recalibration loops into ARCS because agents acting on production systems without a principled fallback model are a liability, not a feature. That instinct maps directly to what Datadog needs to get right for enterprise customers who will not deploy agents without audit trails, scope controls, and confidence thresholds.

On me: two decades across tech, data, and commercial operations. I hold my own in technical conversations on LLM architectures, tool-calling design, and API surface tradeoffs, and I prototype with AI tools before committing engineering time. I have shipped regulated products under SEC/FINRA and HIPAA, which describes a meaningful slice of the engineering organizations Datadog serves.

The bundle at the link has the live commit trail and the proof behind the claims. Happy to go deep on any of it.

Zach Harris
zachharris.xyz · github.com/flashesofbrilliance

---

## Short version (form-field, ~180 words)

Hi Datadog team,

I build the platform, then become its most demanding user. ARCS is an AI-native platform on Claude with an agentic pipeline, tool-calling interfaces, an evaluation and outcome-capture framework, and extensibility patterns that let other workflows build on top. Not experiments. In production. When I read the Bits Agent Builder JD, I read it as the person who has been arguing through these exact tradeoffs every week.

Datadog's moat here is not the agent builder. It is that your agent builder sits on the richest production-signal substrate in the industry: logs, traces, metrics, security events, deployment context. The extensibility model is only as valuable as the grounding it gives agents, and no one else has that grounding at your depth. My instinct is the context layer is where the defensible moat lives.

The governance and failure-mode problem is the one I find most underspecified in the market. I built human-deferral logic and recalibration loops into ARCS because agents acting on production systems without a principled fallback model are a liability. That maps directly to what Datadog needs to get right for enterprise customers.

Two decades across tech, data, and commercial operations. I hold my own on LLM architectures, tool-calling design, and API surface tradeoffs, and I prototype before committing engineering time. Receipts, not adjectives: the bundle has the live commit trail.

Zach Harris

---
_Hook: He built an agentic platform with evaluation, tool-calling, and failure-mode governance already in production, and his sharpest instinct, that Datadog's real moat is the context layer under the agent canvas, is the kind of point of view worth a conversation._
