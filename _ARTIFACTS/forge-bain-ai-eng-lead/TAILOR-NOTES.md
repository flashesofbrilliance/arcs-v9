# TAILOR-NOTES · Bain & Company · Lead, AI Engineering (AI, Insights & Solutions)

Built 2026-09-06 (light tier of the counterpart-application-forge blueprint: stages 1, 5, 7, 8, 9). Inputs pre-staged: JD (`jd-4441207605.txt`, copied here as `jd-full.txt`), record of record (`record-of-record.txt`, resume.arcs.care content), scorer output (composite 0.792, band PURSUE, tier 2), reference bundle `_ARTIFACTS/forge-citi-fde/` for shape.

Scorer's own note: "Ships genAI end-to-end incl. agentic patterns. Docked on scope (IC 'with growing influence') and 3-5yr leveling well under his 20." That framing drives most of the honest gaps below.

## 1. JD hooks and what the resume puts against each

| JD hook | What the resume answers with | Where in the cut | Honest? |
|---|---|---|---|
| Ship end-to-end genAI systems, prototype through production | ARCS: MCP server + agentic orchestration on Claude, in production, not a prototype. | Summary, ARCS bullet 1, pillar 1 | Yes |
| Multi-agent workflows; reasoning, tool use, function calling, orchestration | ARCS pipeline described as agentic orchestration handling capture automatically. Skills line adds "tool use and function calling." | ARCS bullets, Skills | Yes, at the level the record supports; no framework names claimed |
| RAG, fine-tuning, embeddings, hybrid retrieval (vector/graph/keyword) | Not claimed anywhere. The record does not name any of these. | n/a | Gap, stated below |
| Evaluation frameworks: hallucination rate, precision/recall, latency, cost tracking; GenAIOps (automated testing, regression eval) | Not claimed as LLM-specific eval work. The resume instead leans on general KPI/measurement-framework building (CTF, Twill, Verizon, Squat) as the closest honest analog. | Pillar 3 ("evaluation-minded"), CTF/Twill/Verizon bullets | Yes, but explicitly a different kind of evaluation than the JD means; flagged as a gap |
| Guardrails, fallbacks, red-teaming, HITL, Responsible AI | Not claimed. No record support. | n/a | Gap, stated below |
| APIs, microservices, CI/CD, cloud-native deployment, observability | Not claimed. The record shows product/GTM/data-layer building, not backend-service engineering. | n/a | Gap, stated below |
| Technical liaison between engineering, product, data science, ethics; explain concepts to non-technical stakeholders | Grayscale: coordinated product, engineering, legal, risk, compliance. Squat: aligned engineering, clinical, operations. | Pillar 4, Grayscale, Squat | Yes |
| Client-facing consulting or enterprise-transformation experience (stated as "a strong plus") | Squat: sole product-and-tech partner, embedded discovery through QA and handoff, inside a $350M-ARR client. Four other embedded/advisory engagements (Twill, Axon, Verizon, GoPro). | Embedded section | Yes |
| Mentoring junior peers; growing into technical leadership | Not claimed. The record shows individual and embedded-lead work, not people-management or formal mentoring. | n/a | Gap, not invented |
| 3-5+ years hands-on software/ML/applied-AI engineering | Two decades total, but the record's AI-native building (ARCS) is 2025-present, roughly one year. This is the leveling mismatch the scorer flagged. | n/a (headline avoids a years claim) | Named directly in the mapping note and red-team, not smoothed over |
| Hybrid, 3 days/week, travel required | "New York City (hybrid, 3 days on site)" | Header | Yes; travel not separately addressed since no record data on it |

## 2. Evidence grade per lead claim

Grades: **documented** (public/checkable or verbatim in the record) · **self-reported** (candidate's own figure, in the record, not independently verified) · **unverifiable** (tacit, cannot be shown).

| Claim on the page | Grade | Trace |
|---|---|---|
| ARCS: MCP server + agentic orchestration on Claude, in production, 2025 to present | documented | record ROLES.arcs; public GitHub |
| Grayscale: Product Lead, GTM, 10 SEC/FINRA-regulated products, 2024 to 2025 | documented (title, dates, count) | record ROLES.grayscale |
| $7B AUM | self-reported | record metric "$7B AUM · regulated product suite" |
| Squat: sole technology partner, seven-figure embedded engagement, $350M ARR client, 2019 to 2020 | self-reported | record CONSULTING_CLIENTS.squat |
| Twill: 3 AI-enabled lines, go-forward on 2 of 3, 2021 to 2023 | self-reported | record CONSULTING_CLIENTS.twill |
| Axon: MVP definition for a first-responder OTT platform, 2023 | self-reported | record CONSULTING_CLIENTS.axon |
| Verizon Media: five 5G assessments, go/no-go, 2021 | self-reported | record CONSULTING_CLIENTS.verizon |
| GoPro: EMEA/APAC analytics framework, GDPR, 2020 to 2021 | self-reported | record CONSULTING_CLIENTS.gopro |
| CTF: Sr. Director, Data & Strategy, 2018 to 2019; 20% net-new revenue | documented (title, dates) / self-reported (20%) | record ROLES.ctf |
| WTA: Head of Product & Strategic Partnerships, 2016 to 2018; <120ms; $850K+ | documented (title, dates) / self-reported (figures) | record ROLES.wta |
| Oberlin College, BA Studio Art, 2002 to 2006 | documented | record; general resume |
| Skills: Claude, MCP, agentic pipelines, Glean, SQL, Python, forecasting, data modeling, A/B, attribution, Segment/mParticle, Snowflake, data governance | documented (listed in record SKILLS) | record SKILLS |
| Skills: R, Tableau, Redshift, BigQuery, Salesforce CDP, distributed query systems, GitHub | self-reported (not in record SKILLS list; consistent with CTF/WTA roles) | none in record; defend on request |
| "Tool use and function calling" on the Skills line | self-reported extrapolation from the ARCS MCP/agentic build | record ROLES.arcs describes an agentic orchestration layer; the phrase "tool use and function calling" is added phrasing, not a record-verbatim term |
| "Two decades" | documented by arithmetic (2006 to 2026) | education dates |

## 3. Defend-or-drop list

**Defend (kept):**
1. "AI-native builder, forward-deployed with clients" headline. Never held the title "Lead, AI Engineering" or any "AI Engineer" title. Answer if asked: the archetype is proven by ARCS (built, shipped, running) and by the embedded engagements, not by a job title.
2. $7B AUM. Answer: the suite of 10 products the GTM covered; Grayscale's public AUM figure for the period, not a personal P&L.
3. $850K+ and <120ms (WTA), 20% net-new (CTF). Answer: internal figures from those builds, consistent with the role and era, not externally auditable.
4. Skills not in the record (R, Tableau, Redshift, BigQuery, Salesforce CDP). Answer: used in the CTF/WTA data-layer work; drop any one the moment it cannot be discussed fluently.
5. "Tool use and function calling" phrasing on the skills line. Answer: this describes what the MCP/agentic orchestration layer does mechanically; if pressed on a specific framework (LangChain, LangGraph, a particular function-calling API), the honest answer is "built directly against Claude's tool-use API, no third-party orchestration framework."

**Dropped (not on the page):**
1. Any RAG, fine-tuning, embeddings, or hybrid-retrieval claim. Not in the record, not built. This is the single largest technical gap against the JD's "What You'll Do" list.
2. Any evaluation-framework claim in the JD's specific sense (hallucination rate, factual consistency, precision/recall, latency/throughput, cost tracking, GenAIOps regression testing). The resume's "KPI frameworks" language is a genuinely different (business-metric) kind of evaluation and is labeled as such, not conflated.
3. Any guardrails, red-teaming (the JD's AI-safety sense), or HITL-workflow claim.
4. Any claim of building or maintaining APIs, microservices, CI/CD pipelines, or cloud-native deployments.
5. Any people-management or formal-mentoring claim.
6. "~60% decision-noise reduction, 3 to 5x time-to-insight" (in the record as an internal ARCS estimate). Softest number, not carried onto a two-page cut competing on technical depth.
7. Any years-of-hands-on-AI-engineering figure. The record supports roughly one year (ARCS, 2025-present) of hands-on Claude/agentic building; twenty years is true only for the broader tech/data/commercial-ops career, and stating it near the AI claims would blur the leveling issue rather than surface it.

## 4. Headline check

Line under the name: "AI-native builder, forward-deployed with clients." Archetype plus method, not the req title ("Lead, AI Engineering"). The req title appears only in the `<title>` tag and the "Target" line, labeled as a target. Passes the rule.

## 5. The leveling mismatch (read this before sending)

The posting is written for 3-5+ years in software/ML/applied-AI engineering, as a hands-on IC "with growing influence" who may begin informally mentoring. The record shows a candidate with two decades in tech/data/commercial roles at Director-and-above scope (Sr. Director, Product Lead, Head of Product, Founder), but only about one year (2025-present) of hands-on building on an LLM stack. Composite 0.792 / PURSUE reflects strong genAI-shipping signal; the scorer's own dock is exactly this scope/leveling gap. This resume does not resolve that tension; it states the AI-native work honestly (recent, real, in production) and lets the seniority read as what it is. Worth a human gut-check before applying: this may be a considerable pay/scope step down given the base $179.5-203.5K range against two decades of Director-level experience, or it may be the right on-ramp into AI-native technical work. That call belongs to the human, not the resume.
