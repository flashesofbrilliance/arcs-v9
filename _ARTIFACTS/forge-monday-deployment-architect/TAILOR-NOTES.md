# TAILOR-NOTES · monday.com · Deployment Architect

Built 2026-09-06 (light tier of the counterpart-application-forge blueprint: stages 1, 5, 7, 8, 9). All inputs were pre-staged; no JD fetch, no re-grading, no design-system exploration was performed per the light-tier rule.

Record of record: `_STATE/job-search/forge-inputs/record-of-record.txt` (fetched 2026-09-04 19:29 EDT, itself the extracted content of `resume.arcs.care/resume.pdf`, which serves the HTML resume, not a PDF file, carried forward from the prior bundle's open question, unresolved here). JD: `jd-full.txt`. Resume cut: `resume-monday-deployment-architect-ats.html` (2 pages, print-verified). Format and section shape copied from `_ARTIFACTS/forge-citi-fde/` (the format contract for this light-tier run).

## 1. JD hooks and what the resume puts against each

| JD hook | What the resume answers with | Where in the cut | Honest? |
|---|---|---|---|
| Lead technical discovery, surface AI/integration/data requirements before scope and price are committed | Squat: sole tech partner, discovery through QA and handoff, owned roadmap/backlog/sprint planning. | Embedded section | Yes |
| Design AI architecture spanning agents, context, and data layers | ARCS: MCP server, agentic orchestration layer, Claude, in production. | Summary, ARCS, pillars | Yes |
| Architect scope beyond native platform (integrations, data mobility/migrations, custom apps) | CTF: CDP evaluation, Salesforce Lightning modernization, lifecycle segmentation across 3 BUs. WTA: CDP evaluation/selection, real-time scoring build. | CTF, WTA | Yes |
| Estimate effort and consumption impact of scoped work | Twill: KPI frameworks drove go-forward on 2 of 3 lines. Verizon: five opportunity assessments with go/no-go calls. No formal SOW-line-item estimating claim is made; the record does not carry one. | Twill, Verizon; gap named below | Partly, estimation-adjacent (viability/go-no-go), not SOW-line-item costing |
| Sell forward-deployed engineering services; credibility with architects, security reviewers, executives | Grayscale: coordinated product/engineering/legal/risk/compliance through regulated release gates. Squat: cross-functional alignment inside a $350M ARR company. | Grayscale, Squat | Yes |
| Produce solution-design docs, architecture diagrams, technical SOW content | Not directly claimed; the record shows the outputs of scoping (roadmap, backlog, MVP feature/instrumentation definitions at Axon) rather than named deliverable artifacts. | Axon bullet; gap named below | Yes, by omission rather than invention |
| Carry design into delivery, brief engineers, technical oversight on complex engagements | Squat: sole technology partner, discovery through QA and handoff, carried the design the whole way, not just scoped it. | Embedded section | Yes |
| Own delivery standards: architecture, security, governance, scalability | Grayscale: SEC/FINRA release-gate coordination. Twill: HIPAA-regulated market testing. GoPro: GDPR data-sovereignty navigation. | Grayscale, Twill, GoPro | Yes |
| Build estimation models, discovery questionnaires, reusable skill libraries | Not claimed as a named artifact; the KPI-framework language (Twill, Verizon, WTA) is the closest analog and is kept, not overstated into "built an estimation model." | Gap named below | Yes, gap acknowledged |
| 7+ years solutions architect / forward-deployed engineer, recent AI solution design for external customers | Never held either title. Archetype claimed ("forward-deployed product and AI builder"); proven via Squat (embedded, external customer, discovery-to-handoff) and ARCS (AI solution built and run). Two decades total, most recent AI work 2025 to present. | Headline, summary | Yes, and this is the claim most likely to be probed |
| Agentic systems, LLM-based workflows, tool use, context/retrieval design | ARCS: MCP server (the same protocol the posting names explicitly) plus agentic orchestration on Claude. | ARCS, pillars | Yes |
| Defining how AI quality is measured: evaluation, guardrails, human review, observability | Twill's KPI framework decided go-forward on AI product lines; this is evaluation of AI product viability, not live-system observability or guardrails. Named as a partial match. | Twill; gap named below | Partial, named honestly |
| Enterprise data architecture, ETL/migrations/conversions, data readiness for AI | CTF: CDP evaluation, CRM modernization, lifecycle segmentation, "first intelligence layer" for 3 BUs. WTA: CDP selection, real-time behavior scoring at <120ms. | CTF, WTA | Yes |
| Integration standards: REST, GraphQL, webhooks, SCIM, SAML 2.0/OAuth 2.0, MCP | MCP is explicit and genuine (ARCS's own MCP server). SCIM/SAML/OAuth/GraphQL/webhooks are not claimed as named protocols on the record; kept off the page rather than listed to pattern-match the posting. | ARCS bullet; gap named below | Yes, no invented protocol claims |
| Python or TypeScript, AI-assisted editors (Cursor, Claude Code) | Python is on the record's skills list. Claude Code / Cursor usage is not separately claimed as a distinct line; the ARCS build itself (on Claude) stands as the evidence instead of naming a specific editor. | Skills | Partial, no editor-brand claim added |
| Enterprise security, compliance, governance for AI systems handling customer data | Grayscale (SEC/FINRA), Twill (HIPAA), GoPro (GDPR). | Grayscale, Twill, GoPro | Yes |
| Estimating delivery effort, SOWs for AI/data/integration/custom app work | See estimation gap above; no named SOW-authorship claim. | Gap named below | Gap acknowledged |
| Commercial acumen, run discovery in front of a customer, support sale of technical services | Grayscale GTM leadership; Squat embedded sale-adjacent cross-functional work. | Grayscale, Squat | Yes |
| Strong customer-facing, presentation, written/verbal communication | Not claimed as a separate line; carried by the shape of every embedded/advisory engagement (discovery, translation, cross-functional alignment). | Implicit across bullets | Yes, by demonstration rather than assertion |
| Hybrid, 3 days/week New York office | "New York City (hybrid, 3 days on site)" | Header | Yes |
| BA/BS preferred | Oberlin College, BA Studio Art, 2002 to 2006 | Education | Yes |
| Comp $140K-170K | Not referenced on the resume or page (scoring/comp language excluded from all air-gapped surfaces per rule 2/3). | n/a | n/a |

## 2. Evidence grade per lead claim

Grades: **documented** (public and checkable, or verbatim in the record of record) · **self-reported** (the candidate's own figure, in the record, not independently verified) · **unverifiable** (tacit, cannot be shown).

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
| "Two decades" | documented by arithmetic (2006 to 2026) | education dates |

## 3. Defend-or-drop list

**Defend (kept):**
1. "Forward-deployed" as archetype, never as a held title, and never as "solutions architect" either. Answer: the Squat embed (sole product and tech partner, external $350M ARR company, discovery through handoff) and ARCS (built on contact with the real problem, no inherited spec). If asked "were you ever titled Solutions Architect or FDE": no, and the resume does not say so.
2. $7B AUM. Answer: the suite of 10 products the GTM covered; it is Grayscale's public AUM figure for the period, not a personal P&L.
3. $850K+ and <120ms (WTA). Answer: first-year partnership revenue and scoring latency from the 2016 to 2018 build; consistent with the role, not externally auditable.
4. 20% net-new revenue (CTF). Answer: measured against the prior year after the segmentation and personalization rollout; internal figure.
5. Skills not in the record (R, Tableau, Redshift, BigQuery, Salesforce CDP). Answer: used in the CTF and WTA data-layer work; drop any one of them the moment it cannot be discussed fluently.
6. "In production, not experiments" for ARCS, and the MCP-server claim specifically. Answer: live MCP server, live app, public commit trail, the same protocol named in the posting's own integration-standards list.

**Dropped (not on the page):**
1. Any claim of holding the title "Solutions Architect" or "Forward Deployed Engineer." Never held; not invented.
2. Any named SOW-authorship or formal estimation-model-building claim. The record shows go/no-go KPI framework work (Twill, Verizon), which is estimation-adjacent, not the same as owning a delivery-organization estimation model. Kept narrower than the posting asks.
3. Any claim of SCIM, SAML 2.0/OAuth 2.0, GraphQL, or webhook standards fluency. Not in the record. MCP is the one integration standard genuinely evidenced and is the only one claimed.
4. Any named AI-evaluation/guardrails/observability framework for a live production AI system. Twill's KPI-driven go/no-go work is the closest analog and is described as what it is, not upgraded into an evaluation/observability claim.
5. Any Cursor or Claude Code editor-brand claim. Not separately claimed; the ARCS build itself is the evidence offered instead.
6. "~60% decision-noise reduction, 3 to 5x time-to-insight" (in the record as an internal estimate). Softest numbers; cut, consistent with the prior bundle's precedent.
7. "35% release-cycle reduction" at Grayscale (general resume only, not in the record of record). Cut.
8. MIT xPRO certificates and Section4 Certified Product Strategist (general resume only, not in the record). Cut until linkable.
9. Any payments-domain claim. Finance depth is regulated digital assets, not payments; monday's JD does not ask for payments specifically, so this was a non-issue but is noted for consistency with the format contract.

## 4. Headline check

Line under the name: "Forward-deployed product and AI builder · regulated domains" (unchanged from the reference bundle; the archetype is generic to the candidate, not the posting, and remains accurate here). The req title "Deployment Architect" appears only in the document `<title>` and in the "Target" line, labeled as a target. Passes the rule.

## 5. Comp and scope note (not on any air-gapped surface)

Scorer context: composite 0.778, band PURSUE, tier 2, comp_level dim 1 of 3 (posting range $140K-170K, below senior/staff target). This context shaped nothing on the page or resume; it is recorded here only because TAILOR-NOTES is the internal working file, not an air-gapped one.
