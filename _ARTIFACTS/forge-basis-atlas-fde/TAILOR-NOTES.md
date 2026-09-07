# TAILOR-NOTES · Basis · Member of Technical Staff, Atlas FDE

Built 2026-09-07 (light tier of the counterpart-application-forge blueprint: stages 1, 5, 7, 8, 9), copying the shape of `_ARTIFACTS/forge-citi-fde/`.
Record of record: `_STATE/job-search/forge-inputs/record-of-record.txt` (the content data behind resume.arcs.care/resume.pdf, fetched 2026-09-04, saved by an earlier session). JD: `_STATE/job-search/forge-inputs/jd-4441105462.txt`, copied here as `jd-full.txt`. Resume cut: `resume-basis-atlas-fde-ats.html` (2 pages, print-verified).

## 1. JD hooks and what the resume puts against each

| JD hook | What the resume answers with | Where in the cut | Honest? |
|---|---|---|---|
| Embed with teams, learn workflows inside and out, build agents to offload the work | Squat: sole product-and-tech partner, discovery through QA and handoff, embedded inside a $350M-ARR company. ARCS: built the agentic pipeline itself, end to end. | Summary, pillars, Squat bullet | Yes, both in record |
| No established playbook; decompose novel problems from first principles | CTF and WTA: "the first intelligence layer those teams had," built from scratch with no inherited spec. Axon: MVP defined with no established playbook. | Summary, CTF, WTA, Axon | Yes |
| Excited about working with coding agents; unlimited token budget | ARCS: MCP server + agentic orchestration on Claude, in production, public commit trail. | Summary, ARCS, skills | Yes |
| Future founders: agency, customer obsession, product taste, technical skill, communication | ARCS: "operate the full stack, single-threaded" (product, GTM, growth, commercial). Grayscale and Squat: cross-functional translation between non-technical stakeholders and engineering. | ARCS, Grayscale, Squat | Yes |
| Regulated context (Basis serves accounting firms) | Grayscale: SEC/FINRA-regulated digital-asset products, $7B AUM, translated regulatory requirements into buildable ones. Twill: HIPAA-regulated digital health. | Grayscale, Twill | Directionally yes (finance/health regulation, not accounting specifically; named as a gap below) |
| Passionate about outcomes; success of the embedded team is your success | Squat: aligned engineering, clinical, and operations to ship on schedule. Twill: KPI frameworks drove go-forward on 2 of 3 lines. | Squat, Twill | Yes |
| In person, Flatiron NYC, 5 days a week | "New York City (in office, 5 days a week)" | Header | Yes, matches candidate's stated location; the posting's non-negotiable is stated as agreed, not independently verified |
| Systems thinkers who design things that compound | ARCS: "models recalibrate scoring weights from prior decisions, compounding institutional memory." | ARCS | Yes |
| "Member of Technical Staff" as a literal title | Never held. The headline names the archetype ("forward-deployed product and AI builder, agent-native systems"), never the req title. | Headline, target line | Yes, and this is the claim most likely to be probed (see red-team) |

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
| Oberlin College, BA Studio Art, 2002 to 2006 | documented | record |
| Skills: Claude, MCP, agentic pipelines, Glean, SQL, Python, forecasting, data modeling, A/B, attribution, Segment/mParticle, Snowflake, data governance | documented (listed in record SKILLS) | record SKILLS |
| Skills: R, Tableau, Redshift, BigQuery, Salesforce CDP, distributed query systems, GitHub | self-reported (not in record SKILLS list; consistent with CTF/WTA roles) | none in record; defend on request |
| "Two decades" | documented by arithmetic (2006 to 2026) | education dates |

## 3. Defend-or-drop list

**Defend (kept):**
1. "Forward-deployed" as archetype, never as a held title, and never as "Member of Technical Staff." Answer: the Squat embed (sole product and tech partner, discovery through handoff) and ARCS (built on contact with the real problem, no inherited spec). If asked "were you ever titled MTS or FDE": no, and the resume does not say so.
2. $7B AUM. Answer: the suite of 10 products the GTM covered; it is Grayscale's public AUM figure for the period, not a personal P&L.
3. $850K+ and <120ms (WTA). Answer: first-year partnership revenue and scoring latency from the 2016 to 2018 build; consistent with the role, not externally auditable.
4. 20% net-new revenue (CTF). Answer: measured against the prior year after the segmentation and personalization rollout; internal figure.
5. Skills not in the record (R, Tableau, Redshift, BigQuery, Salesforce CDP). Answer: used in the CTF and WTA data-layer work; drop any one the moment it cannot be discussed fluently.
6. "In production, not experiments" for ARCS. Answer: live MCP server, live app, public commit trail.
7. Regulated-industry fluency framed against Basis's accounting-firm customer base. Answer: SEC/FINRA and HIPAA are the actual regulated environments worked in; accounting/audit specifically is not claimed as domain experience, only the muscle of shipping inside compliance gates.

**Dropped (not on the page):**
1. "~60% decision-noise reduction, 3 to 5x time-to-insight" (in the record as an internal estimate). Softest numbers; cut.
2. "35% release-cycle reduction" at Grayscale (general resume only, not in the record of record). Cut.
3. MIT xPRO certificates and Section4 Certified Product Strategist (general resume only, not in the record). Cut until linkable.
4. Any claim of prior accounting, audit, or finance-ops domain depth. Never held; not invented.
5. Any claim of having worked at an AI-native, agent-first company before. ARCS is the candidate's own build, not employment at one.
6. Any team-size or people-management claim. The record shows individual and embedded-lead work; no headcount figure is claimed.

## 4. Open question carried from the prior forge run

The record-of-record URL (resume.arcs.care/resume.pdf) serves an HTML resume, not a PDF file. Content was extracted from the HTML page source and treated as the record; flagged here again since this bundle inherits that same record.

## 5. Headline check

Line under the name: "Forward-deployed product and AI builder · agent-native systems." Archetype plus domain, never the req title "Member of Technical Staff" or "Atlas FDE." The req title appears only in the document `<title>` and the "Target" line, which is labeled as a target. Passes the rule.
