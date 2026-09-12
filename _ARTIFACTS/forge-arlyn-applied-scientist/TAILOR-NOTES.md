# TAILOR-NOTES · Arlyn AI · Senior Applied Scientist, Agentic AI

Built 2026-09-06 (light tier of the counterpart-application-forge blueprint: stages 1, 5, 7, 8, 9).
Record of record: `_STATE/job-search/forge-inputs/record-of-record.txt` (fetched 2026-09-04 19:29 EDT from resume.arcs.care/resume.pdf, which serves the HTML resume; see that file's own note).
JD: `jd-full.txt` (pre-staged, jobid 4460555968). Resume cut: `resume-arlyn-applied-scientist-ats.html` (2 pages, verified).

Scorer context (pre-staged, not re-graded): composite 0.722, band PURSUE, tier 2. Assessment: "Application layer not model training, passes the AI-native-for-real test. But Applied Scientist framing leans research-adjacent and there is no customer-embed component." That framing gap drives the honest-grade calls below.

## 1. JD hooks and what the resume puts against each

| JD hook | What the resume answers with | Where in the cut | Honest? |
|---|---|---|---|
| Own end-to-end development and deployment of agentic LLM applications, measurable business impact | ARCS: MCP server + agentic orchestration on Claude, running in production; owns the full stack alone. | Pillars, ARCS job | Yes, both in record |
| Design, build, evaluate, ship production-ready AI systems, prototype to production | ARCS build (design/build/ship, in production). Twill Health: market-viability testing informed go-forward on 2 of 3 AI product lines (the "evaluate" half). | Pillars, ARCS, Twill | Yes |
| Partner with founders to define product direction, turn business problems into AI solutions | ARCS: sole founder, every call is founder-facing by construction. Five embedded/advisory engagements (2019-2024) working directly with executive/founder-level stakeholders, not through a PM layer. | Pillars, embedded section | Yes; "founder-facing" framing is honest because ARCS literally has one founder, not because Zach has been an Applied Scientist reporting to founders elsewhere |
| Collaborate with Engineering to build scalable AI infrastructure, system architecture, internal tools | Grayscale: coordinated product/engineering/legal/risk/compliance through regulated release gates. Squat: sole tech partner, discovery through QA and handoff. | Grayscale, Squat | Yes |
| Improve system performance, reliability, UX through rapid experimentation | WTA: <120ms real-time scoring, platform load simulation. CTF: segmentation engine iterated against outcomes. ARCS: outcome-capture framework recalibrates scoring weights. | WTA, CTF, ARCS | Yes (figures self-reported, see grades) |
| 5+ years industry experience in finance, biotech, or tech startups (or PhD quant, 2+ yrs) | Grayscale (finance, SEC/FINRA) and ARCS (tech startup, founder) both qualify on the "or tech startups" branch; twenty years total industry experience. No PhD claimed. | Summary, Grayscale, ARCS | Yes; no biotech/life-science employer in the record, stated as a gap not invented |
| Hands-on AI application building: prompt engineering, advanced analytics, unstructured-to-production | ARCS: MCP server, agentic orchestration, evidence taxonomy that converts unstructured input into a scored outcome. "Prompt engineering" added to the skills line because building the ARCS pipeline requires it; not a separate record entry. | ARCS, skills | Yes, with prompt engineering as a reasonable inference from the documented MCP/agentic build, not a separate documented claim |
| Lead decision-making on system architectures and core operational workflows across Engineering and Data Science | ARCS: sole architectural owner. Grayscale: release-gate coordination across five functions. CTF: designed the data model and segmentation engine that became the org's first intelligence layer. | ARCS, Grayscale, CTF | Yes |
| Transform unstructured data into data ontologies | ARCS evidence taxonomy (closest documented match). CTF: scalable data model and segmentation engine across 3 business units. Neither uses the word "ontology" in the record; framed as the closest honest analog. | ARCS, CTF | Yes, framed carefully; no ontology tooling (e.g. knowledge graphs) is claimed |
| Life science / biotech / drug-launch / patient-access domain | Not claimed. Twill Health (HIPAA digital health) and CTF (clinical operations at a medical research nonprofit) are the closest domain-adjacent work; neither is pharma commercial or drug-launch specific. | Twill, CTF | Gap acknowledged, not papered over |
| Hudson Yards NYC, on site 3 days a week, relocation support offered | "New York City (on site 3 days)" | Header | Yes; already local, relocation support not needed |
| Compensation $175K-$255K + equity | Not on the resume or page (comp talk excluded per air-gap rule). | n/a | n/a |

## 2. Evidence grade per lead claim

Grades: **documented** (verbatim in the record of record, or independently public) · **self-reported** (candidate's own figure, in the record, not independently verified) · **unverifiable** (tacit, never given a figure).

| Claim on the page | Grade | Trace |
|---|---|---|
| ARCS: MCP server + agentic orchestration on Claude, in production, 2025 to present | documented | record ROLES.arcs; public GitHub |
| ARCS: structured evidence taxonomy / gating architecture | documented | record ROLES.arcs bullet ("structured evidence taxonomy and evidence-gating architecture") |
| Grayscale: Product Lead, GTM, 10 SEC/FINRA-regulated products, 2024 to 2025 | documented (title, dates, count) | record ROLES.grayscale |
| $7B AUM | self-reported | record metric "$7B AUM · regulated product suite" |
| Twill Health: 3 AI-enabled digital-health lines, go-forward on 2 of 3, 2021 to 2023 | self-reported | record CONSULTING_CLIENTS.twill |
| Squat: sole technology partner, seven-figure embedded engagement, $350M ARR client, 2019 to 2020 | self-reported | record CONSULTING_CLIENTS.squat |
| Axon: MVP definition for a first-responder OTT platform, 2023 | self-reported | record CONSULTING_CLIENTS.axon |
| Verizon Media: five 5G assessments, go/no-go, 2021 | self-reported | record CONSULTING_CLIENTS.verizon |
| GoPro: EMEA/APAC analytics framework, GDPR, 2020 to 2021 | self-reported | record CONSULTING_CLIENTS.gopro |
| CTF: Sr. Director, Data & Strategy, 2018 to 2019; 20% net-new revenue | documented (title, dates) / self-reported (20%) | record ROLES.ctf |
| WTA: Head of Product & Strategic Partnerships, 2016 to 2018; <120ms; $850K+ | documented (title, dates) / self-reported (figures) | record ROLES.wta |
| Oberlin College, BA Studio Art, 2002 to 2006 | documented | record; general resume |
| Skills: Claude, MCP, agentic pipelines, Glean, SQL, Python, forecasting, data modeling, A/B, attribution, Segment/mParticle, Snowflake, data governance | documented (listed in record SKILLS) | record SKILLS |
| Skills: R, Tableau, Redshift, BigQuery, Salesforce CDP, distributed query systems, prompt engineering, GitHub | self-reported (not on the record SKILLS list; prompt engineering inferred from the ARCS build, not separately documented) | none in record; defend on request |
| "Twenty years" | documented by arithmetic (2006 to 2026) | education dates |

## 3. Defend-or-drop list

**Defend (kept):**
1. "Founder-facing, not committee-facing" as a pillar. Answer: literally true at ARCS (sole founder); the embedded engagements involved direct executive contact, but Zach was never titled "Applied Scientist" reporting into a founder team. If pressed on the JD's specific "partner with founders" framing: the closest direct analog is ARCS itself, where Zach is both.
2. "Prompt engineering" on the skills line. Answer: not a separately documented record entry; inferred from building and running the ARCS MCP/agentic pipeline. Would narrow this to "agentic pipeline design" if pressed hard on the specific term.
3. $7B AUM, $850K+, <120ms, 20%, seven-figure engagement. Same defend posture as the Citi bundle: self-reported figures consistent with the documented role and era, not personal P&L claims.
4. No biotech/life-science employer. Answer: closest adjacent work is Twill Health (HIPAA digital health) and CTF (clinical-adjacent nonprofit); state plainly that neither is pharma commercial.
5. Skills not in the record (R, Tableau, Redshift, BigQuery, Salesforce CDP, distributed query systems). Same posture as prior bundles: used in CTF/WTA data-layer work; drop any one the moment it cannot be discussed fluently.

**Dropped (not on the page):**
1. "~60% decision-noise reduction, 3 to 5x time-to-insight" (internal estimate in the record, no external check). Cut.
2. MIT xPRO / Section4 certificates (general resume only, not in the record of record). Cut until linkable.
3. Any claim of a PhD or a quantitative-field graduate degree. Never held (BA, Studio Art); the posting's PhD branch is not claimed at all, only the "5+ years industry experience" branch.
4. Any life-science, biotech, or drug-launch domain claim beyond Twill/CTF. Not invented.
5. Any "data ontology" tooling claim (e.g. knowledge graphs, formal taxonomy software). The ARCS evidence taxonomy is the honest analog; nothing more specific is claimed.
6. Comp, tier, band, or scoring vocabulary anywhere on page.html (per air-gap rule).

## 4. Headline check

Line under the name: "Agentic AI builder, prototype to production." Archetype, not the req title. The req title appears only in the `<title>` tag and the "Target" line, which is labeled as a target. Passes the rule. "Applied Scientist" is never used as a self-description anywhere on the resume or the page.

## 5. Open question carried from the record

Same as prior bundles: `record-of-record.txt` notes the canonical URL (resume.arcs.care/resume.pdf) serves the HTML resume, not an actual PDF file. Not re-verified this pass (out of scope per the prompt's "do not call any API"); flagged for the human.
