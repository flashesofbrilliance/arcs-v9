# Cover letter — Datadog · Senior Product Manager - Data Agent
_Draft. Plain text below is paste-ready. Add any personal availability note by hand._

---

Hi Datadog team,

I build AI-native data products for technical users who need governed, trustworthy answers. That is the short version of why this role fits.

Here is the longer one. The problem you are describing at the top of this posting is the exact problem I built ARCS to solve: every answer is a one-off, no governance, no consistency, no visibility for the people responsible for data quality. I did not read that sentence as a candidate. I read it as someone who has lived inside that failure mode and built the instrumentation to fix it. ARCS runs an evaluation framework, confidence scoring, and a self-improvement loop that recalibrates from real outcomes, on Claude, in production. The governance and quality architecture you are describing for the Data Agent is the same architecture, applied to a much larger surface.

A few things I noticed that made me want to write.

The dual-persona problem here is genuinely hard. Data teams need to govern and curate. Data consumers, your PMs, SREs, and executives, need fast, trustworthy answers without caring how the plumbing works. I have built for both sides of that seam. At Twill Health I defined governance controls and quality loops for three AI-enabled product lines while also scoping the API instrumentation and data-access contracts that developer-facing consumers depended on. At the WTA I built real-time fan-behavior scoring at under 120ms, serving personalized outputs inside a live usage window where a wrong answer had an immediate cost. Trustworthy and fast are not opposites if the context layer is built right.

The observability-plus-business-data angle is the part of your product I find most interesting and most defensible. Datadog already owns the infrastructure signal. The question is whether you can make that signal legible to the data consumer who has never touched a trace. That is a product design problem as much as a data problem, and it is the kind I like to own: hard interior, clean surface.

On me: I write SQL and Python in daily use for product decisions, I hold my own in technical tradeoff conversations with engineering, and I prototype with AI tools before committing engineering time. Two decades across finance, health, sports, and consumer, always on the data-intensive side. I do not just write the deck.

The bundle at datadog.arcs.care has the live commit trail and the director's cut of how ARCS was built. Happy to go deep on any of it.

Zach Harris
zachharris.xyz · github.com/flashesofbrilliance

---

## Short version (form-field, ~180 words)

Hi Datadog team,

I build AI-native data products for technical users who need governed, trustworthy answers. The problem at the top of this posting, every answer a one-off, no governance, no consistency, is the exact problem I built ARCS to solve. I did not read it as a candidate. I read it as someone who has lived inside that failure mode. ARCS runs an evaluation framework, confidence scoring, and a self-improvement loop that recalibrates from real outcomes, on Claude, in production.

The dual-persona problem here is genuinely hard. At Twill Health I defined governance controls and quality loops for three AI-enabled product lines while scoping the API instrumentation that data consumers depended on. At the WTA I built real-time fan-behavior scoring at under 120ms, where a wrong answer had an immediate cost. Trustworthy and fast are not opposites if the context layer is built right.

The observability-plus-business-data angle is the most defensible part of your moat. Making infrastructure signal legible to a data consumer who has never touched a trace is a product design problem as much as a data problem. That is the kind I like to own.

SQL and Python in daily use. Two decades on the data-intensive side. I do not just write the deck.

Zach Harris
zachharris.xyz · github.com/flashesofbrilliance

---
_Hook: He built the governance-and-eval architecture Datadog is describing, on a live product, as a solo founder, and he reads the dual-persona problem from both sides of the seam._
