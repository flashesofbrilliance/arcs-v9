# TAILOR-NOTES · Norm Ai · Forward Deployed Engineer

Forged 2026-09-04 (light tier: gather, honest-grade, red-team, render, kintsugi).
Record of record: `https://resume.arcs.care` (serves `public/resume.html`; there is no separate PDF, the URL `/resume.pdf` returns the same HTML). Text extracted to `master-resume.txt`.
Posting of record: Ashby board JSON (`ashby-board.json`), FDE posting `366d4079-4842-469d-a5e0-3cc891a136b4`, published 2025-07-15, department Engineering, team "Deployment Team". Full JD in `jd-ashby-fde.txt`. LinkedIn 4266778287 matches it.

## Positioning knob (from `_ARTIFACTS/resume-applied-ai/positioning.md`)
FDE archetype: lead differentiator #2 (embed) then #1 (build). Squat NY is the headline; ARCS is the AI-fluency proof; Grayscale is the regulatory-translation proof; CTF is the data-modeling proof.

## JD hooks → what the résumé puts against each

| JD hook | Résumé answer | Evidence grade |
|---|---|---|
| Lead technical implementation and integration with enterprise clients | Squat NY: sole product and technology partner, seven-figure embedded engagement, $350M-ARR client, discovery through QA and handoff | self-reported (figures are the candidate's; the engagement itself is on the master résumé) |
| Work with client technical teams on infrastructure, security, compliance | Grayscale: coordinated product, eng, legal, risk, compliance through regulated release gates; GoPro: GDPR data sovereignty | self-reported |
| Design and implement scalable ETL pipelines into the platform | CTF: enterprise data infrastructure end to end (CDP evaluation, Salesforce Lightning, lifecycle segmentation); WTA: CDP selection + real-time scoring pipeline | self-reported |
| Map ambiguous business data into a structured data model with SMEs | CTF: one scalable data model across marketing, fundraising, clinical (3 BUs); ARCS: evidence taxonomy; WTA: behavioral taxonomy | self-reported |
| Client-specific customizations to convert and upsell | Squat NY roadmap/CX overhaul against a conversion KPI; CTF 20% net-new revenue | self-reported |
| Enablement sessions for client end-users | Not claimed. Record supports stakeholder alignment and handoff, not training sessions. See defend-or-drop. | n/a |
| Technical documentation | good.arcs.care OSS tools, each with docs + conformance suite | documented (public repos) |
| Translate regulatory requirements with legal engineering | Grayscale: "translated regulatory requirements into product and go-to-market requirements" (master, verbatim); Twill HIPAA | self-reported |
| 4+ years production Python | Python listed under Analytics & DS on the master; ARCS Python operator library. The year-count is NOT asserted. | self-reported (library is in a private repo; unverifiable from outside) |
| 1+ years enterprise technical client-facing | Squat NY 2019 to 2020 + embedded consulting 2020 to 2023 | self-reported |
| APIs, FastAPI | Next.js route handlers in ARCS (TypeScript). FastAPI not claimed. | documented that ARCS is live; FastAPI n/a |
| Postgres or similar | ARCS on Postgres (Prisma); Snowflake/Redshift/BigQuery on master | self-reported |
| Excited to iterate with customers | thesis line + Squat bullets | n/a |
| Nice: React/TypeScript, Next.js | ARCS is Next.js + TypeScript (live at arcs.care) | documented |
| Nice: Dagster / Airflow | Not claimed | n/a |
| Nice: startup ambiguity | ARCS founder 2025 to present | documented |
| AI fluency, concrete tools and workflows | ARCS on Claude, custom MCP server, agentic pipelines; "coding agents in daily use"; public commit trail at status.arcs.care | documented (live product, public trail) |

## Evidence grade per lead claim on the cut

| Claim | Grade | Basis |
|---|---|---|
| ARCS runs on Claude with a custom MCP server and agentic pipelines | documented | live app; master résumé; public OSS |
| Next.js/TypeScript on Postgres (Prisma), Python operator library, CI gates | self-reported | repo is private; stack is real but not inspectable from outside |
| 60% decision-noise reduction | self-reported, labeled as such on the page | internal measurement of own product |
| Grayscale: 10 SEC/FINRA-regulated products, $7B AUM | documented (AUM is public), role self-reported | master résumé |
| Squat NY: seven-figure engagement, $350M ARR client | self-reported | master résumé |
| CTF: 20% net-new revenue lift | self-reported | master résumé |
| WTA: <120ms scoring, $850K+ year one | self-reported | master résumé |
| Twill 3 lines / 2 of 3, Axon OTT MVP, GoPro GDPR, Verizon 5 ventures | self-reported | master résumé |
| Oberlin BA Studio Art (Honors), MIT xPRO certificate | documented | master résumé; verifiable credentials |

Nothing on the cut is graded "unverifiable" after the red-team pass; the two candidates for that grade (Python year-count, teaching/enablement) were dropped.

## Defend-or-drop (removed or never added)

| Item | Decision | Reason |
|---|---|---|
| FastAPI | drop (never added) | not in the record |
| Dagster / Apache Airflow | drop (never added) | not in the record |
| "4+ years of Python" as a number | drop | Python is on the record as a skill; a year-count is not, and a wrong count fails a reference check |
| "then teach their people to run it" (thesis) | drop | enablement sessions are in the JD, not the record; record says handoff |
| "Twenty years in regulated settings" | rewrite | two decades of product; regulated work is 2021 onward |
| "translating a rule into working software" | soften to "product requirements" | that is the verbatim record at Grayscale |
| "CI gates on every merge" | soften to "before deploy" | not independently checkable; the weaker claim is true and enough |
| 3 to 5x time-to-insight (master) | drop | compounding self-metric; adds nothing the 60% line does not already say, and it is the weaker of the two |
| RBAC / "policy-at-the-glass" / 35% release-cycle cut (from the earlier MCP-platform cut) | drop | not on the master résumé; do not inherit claims from sibling cuts |
| Section4 certification (earlier cuts) | drop | not on the master résumé |
| Email address | omit | not on the master; consistent with the most recent public cut (GitHub + LinkedIn + metro) |

## Notes for the human
- Compensation on the posting: Senior $190K to $250K, Staff $240K to $280K, equity, hybrid 3 to 4 days in NYC office. Fairfield County commute is plausible; relocation support is offered but not needed.
- The interview will ask for concrete AI workflows. status.arcs.care and the MCP server are the exhibits.
- The FastAPI / Dagster gap is real. If asked, the honest answer is Python data tooling plus Next.js APIs, and a willingness to be evaluated on it.
