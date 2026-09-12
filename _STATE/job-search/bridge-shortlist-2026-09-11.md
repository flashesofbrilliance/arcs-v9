# Bridge lane shortlist — 2026-09-11 (bridge-scan v1.0)

> Lens: shoot-to-win = fit x win-probability, NOT FDE fit. Spec: `runtime/specs/bridge-scan.json`.
> Scorer: `POST /api/jobs/score` with `spec:"bridge-scan"` (Haiku, temp 0, strict gate allowlist); driver `scripts/jobs_bridge_sweep.mjs`.
> Score rows keyed `targetVersion=bridge-1.0`; FDE v1.3 rows untouched. Re-runnable: `node scripts/jobs_bridge_sweep.mjs` drains any new UNSCORED bridge row.
> Read tiers, not ranks: 0-3 integer dims on 8-row batches give coarse composites; a 0.02 gap is noise.

Scored: 75 bridge rows · bands: PURSUE 24 · PASS 30 · CONSIDER 21

## Dims and weights (max 87)
- **req_reality** (w5) — Req reality
- **competition_density** (w5) — Winnability vs applicant pool (inverse of competition density)
- **level_fit** (w4) — Level fit
- **shape_fit** (w4) — Role-shape fit (operator x regulated x product/AI/ops)
- **stability_parent_signal** (w3) — Stability of the parent
- **edge_rewarded** (w3) — Is the AI-builder edge a differentiator (not the bar)?
- **logistics** (w2) — Logistics
- **comp_floor** (w2) — Comp floor
- **warm_path** (w1) — Warm path

Gates (strict allowlist, auto-PASS): `evergreen / talent-community / no live req`, `junior/entry leveling`, `VP+ / C-level leveling`, `on-site outside NY-metro with no remote`, `AI-lab or research-scientist hiring bar`, `pure quota-carrying sales rep`

## Ranked (competition read: LOW = thin pool · MED · HIGH · STAMPEDE)

| # | comp | band | tier | compete | req | lvl | shape | stab | edge | company — title | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.885 | PURSUE | T1 | MED | 3 | 3 | 3 | 3 | 3 | Justworks — Product Operations Manager, AI & Systems |  |
| 2 | 0.874 | PURSUE | T1 | MED | 3 | 3 | 3 | 3 | 2 | Ramp — GTM Senior Business Systems Analyst, Pre-Sales |  |
| 3 | 0.874 | PURSUE | T1 | MED | 3 | 3 | 3 | 3 | 2 | Ramp — GTM Senior Business Systems Analyst – Channel Sales |  |
| 4 | 0.862 | PURSUE | T1 | MED | 3 | 2 | 3 | 3 | 3 | Squarespace — Business Development Manager, AI Discoverability and Scheduling Partnerships |  |
| 5 | 0.851 | PURSUE | T1 | MED | 3 | 3 | 3 | 3 | 2 | Betterment — Business Systems Architect, GTM Systems |  |
| 6 | 0.828 | PURSUE | T1 | HIGH | 3 | 3 | 3 | 3 | 3 | Datadog — Director, GTM Enablement Operations |  |
| 7 | 0.805 | PURSUE | T1 | MED | 3 | 2 | 3 | 3 | 2 | Ramp — GTM Business Systems Analyst – Post Sales |  |
| 8 | 0.805 | PURSUE | T1 | HIGH | 3 | 3 | 2 | 3 | 3 | Ramp — AI Solutions Strategist |  |
| 9 | 0.782 | PURSUE | T2 | HIGH | 3 | 3 | 2 | 3 | 3 | Datadog — Senior Product Manager - Search |  |
| 10 | 0.759 | PURSUE | T2 | MED | 3 | 3 | 3 | 3 | 0 | Betterment — Sr. Manager, Revenue Operations - Deal Desk & GTM Process Improvement |  |
| 11 | 0.759 | PURSUE | T2 | HIGH | 3 | 2 | 3 | 3 | 3 | Ramp — Product Operations \| AI Revenue Systems |  |
| 12 | 0.747 | PURSUE | T2 | MED | 3 | 2 | 3 | 3 | 1 | Squarespace — GTM Marketing Programs Manager |  |
| 13 | 0.747 | PURSUE | T2 | HIGH | 3 | 3 | 2 | 3 | 2 | Oscar Health — Senior Product Manager, Marketplace |  |
| 14 | 0.747 | PURSUE | T2 | MED | 3 | 2 | 2 | 3 | 1 | Oscar Health — Group Product Manager, Lucie Platform |  |
| 15 | 0.747 | PURSUE | T2 | HIGH | 3 | 3 | 2 | 3 | 2 | Datadog — Senior Product Solutions Architect - AI Agent |  |
| 16 | 0.747 | PURSUE | T2 | STAMPEDE | 3 | 3 | 2 | 3 | 3 | Datadog — Senior Product Manager - Data Agent |  |
| 17 | 0.736 | PURSUE | T2 | HIGH | 3 | 3 | 2 | 2 | 2 | Peloton — Lead Product Manager |  |
| 18 | 0.713 | PURSUE | T2 | HIGH | 3 | 3 | 2 | 3 | 1 | MongoDB — Senior Product Manager, Post Sales |  |
| 19 | 0.713 | PURSUE | T2 | STAMPEDE | 3 | 3 | 2 | 3 | 2 | Datadog — Senior Product Manager - Fleet and Lifecycle Management |  |
| 20 | 0.713 | PURSUE | T2 | STAMPEDE | 3 | 3 | 2 | 3 | 2 | Datadog — Senior Product Manager - Bits Agent Builder |  |
| 21 | 0.701 | PURSUE | T2 | HIGH | 3 | 3 | 2 | 3 | 0 | Squarespace — Enterprise Transformation, Senior Lead |  |
| 22 | 0.701 | PURSUE | T2 | STAMPEDE | 3 | 3 | 1 | 3 | 3 | Ramp — Product Manager \| Tax |  |
| 23 | 0.701 | PASS | T2 | MED | 3 | 0 | 3 | 3 | 3 | Datadog — GTM Strategy and Operations Associate | junior/entry leveling |
| 24 | 0.701 | PURSUE | T2 | HIGH | 3 | 3 | 2 | 3 | 0 | Justworks — Senior Product Manager, Time |  |
| 25 | 0.701 | PURSUE | T2 | HIGH | 3 | 3 | 2 | 3 | 0 | Justworks — Senior Product Manager, Contractor Managment |  |
| 26 | 0.678 | PASS | T3 | HIGH | 3 | 0 | 3 | 3 | 2 | MongoDB — Senior Director, Global AI Native & POD Program | VP+ / C-level leveling |
| 27 | 0.667 | PASS | T3 | HIGH | 3 | 1 | 1 | 3 | 3 | Ramp — Applied AI Engineer | AI-lab or research-scientist hiring bar |
| 28 | 0.667 | CONSIDER | T3 | STAMPEDE | 3 | 3 | 1 | 3 | 2 | Datadog — Senior Product Manager - Journey Monitoring |  |
| 29 | 0.667 | CONSIDER | T3 | STAMPEDE | 3 | 3 | 1 | 3 | 2 | Datadog — Senior Platform Product Manager - AI SDLC Trusted Throughput |  |
| 30 | 0.667 | CONSIDER | T3 | STAMPEDE | 3 | 3 | 1 | 3 | 2 | Justworks — Senior Product Manager, Product Foundations |  |
| 31 | 0.655 | CONSIDER | T3 | STAMPEDE | 3 | 2 | 1 | 3 | 3 | Ramp — Product Manager \| Vendor Intelligence & Marketplace |  |
| 32 | 0.655 | CONSIDER | T3 | HIGH | 3 | 3 | 1 | 2 | 1 | Peloton — Senior Product Manager |  |
| 33 | 0.644 | CONSIDER | T3 | HIGH | 3 | 2 | 1 | 3 | 1 | Ramp — GTM Business Systems Engineer, Quote-to-Cash |  |
| 34 | 0.644 | CONSIDER | T3 | HIGH | 3 | 2 | 1 | 3 | 1 | Ramp — GTM Business Systems Engineer – Post Sales |  |
| 35 | 0.644 | PASS | T3 | HIGH | 3 | 1 | 1 | 3 | 3 | Oscar Health — Staff AI Engineer | AI-lab or research-scientist hiring bar |
| 36 | 0.632 | CONSIDER | T3 | STAMPEDE | 3 | 3 | 1 | 3 | 1 | Datadog — Senior Product Manager - Observability Data Platform |  |
| 37 | 0.632 | CONSIDER | T3 | HIGH | 3 | 2 | 1 | 3 | 2 | Datadog — Product Manager II, AI & Data Security |  |
| 38 | 0.632 | CONSIDER | T3 | MED | 3 | 1 | 1 | 3 | 1 | Datadog — Partner Technology Solutions Engineer |  |
| 39 | 0.621 | PASS | T3 | MED | 3 | 2 | 0 | 3 | 0 | Datadog — Senior Forward Deployed Engineer, Feature Flags | pure quota-carrying sales rep |
| 40 | 0.621 | PASS | T3 | HIGH | 3 | 2 | 1 | 3 | 3 | Datadog — Senior AI Engineer – Notebooks | on-site outside NY-metro with no remote |
| 41 | 0.621 | PASS | T3 | HIGH | 3 | 2 | 1 | 3 | 3 | Datadog — Senior AI Engineer – Notebooks | on-site outside NY-metro with no remote |
| 42 | 0.609 | CONSIDER | T3 | MED | 3 | 2 | 1 | 2 | 0 | Peloton — Sr. Hardware Product Manager |  |
| 43 | 0.609 | CONSIDER | T3 | STAMPEDE | 3 | 2 | 2 | 3 | 1 | Oscar Health — Group Product Manager, Member Coverage & Support Platform |  |
| 44 | 0.609 | CONSIDER | T3 | STAMPEDE | 2 | 3 | 1 | 3 | 2 | Datadog — Staff Product Manager - Bits Release |  |
| 45 | 0.609 | PASS | T3 | STAMPEDE | 3 | 3 | 1 | 3 | 1 | Datadog — Senior Product Manager - Serverless | generic PM title at prestige brand = stampede applicant pool |
| 46 | 0.598 | CONSIDER | T3 | MED | 3 | 1 | 1 | 3 | 0 | Oscar Health — Manager, Insurance Product Innovation & Emerging Solutions |  |
| 47 | 0.598 | CONSIDER | T3 | STAMPEDE | 3 | 3 | 1 | 3 | 0 | Datadog — Senior Product Manager - Network Path |  |
| 48 | 0.598 | CONSIDER | T3 | HIGH | 3 | 2 | 2 | 2 | 0 | Justworks — Product Manager, Benefits |  |
| 49 | 0.586 | CONSIDER | T3 | STAMPEDE | 3 | 3 | 1 | 3 | 1 | MongoDB — Senior Data Product Manager, Product Telemetry |  |
| 50 | 0.586 | PASS | T3 | HIGH | 3 | 1 | 0 | 3 | 2 | Datadog — Senior Applied Scientist | AI-lab or research-scientist hiring bar |
| 51 | 0.586 | CONSIDER | T3 | HIGH | 3 | 2 | 1 | 3 | 0 | Justworks — Group Product Manager, Product Foundations |  |
| 52 | 0.586 | CONSIDER | T3 | HIGH | 3 | 2 | 1 | 3 | 0 | Justworks — Group Product Manager, Advisor Channel |  |
| 53 | 0.575 | PASS | T3 | HIGH | 3 | 0 | 2 | 3 | 1 | MongoDB — Lead Forward Deployed Engineer | VP+ / C-level leveling |
| 54 | 0.563 | PASS | T3 | HIGH | 3 | 0 | 2 | 3 | 2 | Datadog — GTM Operations Associate | junior/entry leveling |
| 55 | 0.563 | CONSIDER | T3 | HIGH | 3 | 1 | 2 | 3 | 0 | Justworks — Product Manager, Time Global |  |
| 56 | 0.552 | CONSIDER | T3 | STAMPEDE | 3 | 2 | 1 | 3 | 0 | Datadog — Product Manager II - SQL & Sheets Growth |  |
| 57 | 0.540 | PASS | T- | STAMPEDE | 3 | 2 | 0 | 3 | 1 | Ramp — AI Solutions Engineer | pure quota-carrying sales rep |
| 58 | 0.540 | PASS | T- | HIGH | 2 | 1 | 1 | 3 | 1 | Datadog — Product Strategy and Corporate Development Lead, AI | AI-lab or research-scientist hiring bar |
| 59 | 0.540 | PASS | T- | STAMPEDE | 3 | 0 | 2 | 3 | 1 | Datadog — Director, Product Management - Platforms | VP+ / C-level leveling |
| 60 | 0.494 | PASS | T- | STAMPEDE | 2 | 1 | 1 | 3 | 2 | Datadog — Product Manager II - Application Performance Monitoring |  |
| 61 | 0.494 | PASS | T- | HIGH | 3 | 0 | 2 | 3 | 0 | Datadog — GTM Strategy/Operations Associate - New York | junior/entry leveling |
| 62 | 0.494 | PASS | T- | HIGH | 3 | 0 | 2 | 3 | 0 | Datadog — GTM Strategy/Operations Associate | junior/entry leveling |
| 63 | 0.483 | PASS | T- | STAMPEDE | 3 | 0 | 0 | 3 | 2 | Ramp — Director, Product Design | VP+ / C-level leveling |
| 64 | 0.471 | PASS | T- | HIGH | 3 | 0 | 2 | 3 | 0 | Oscar Health — Associate, Insurance Product and Emerging Product Innovation | junior/entry leveling |
| 65 | 0.460 | PASS | T- | STAMPEDE | 3 | 1 | 0 | 3 | 0 | Datadog — Staff GenAI Engineer - Application Performance Monitoring (APM) | AI-lab / research-scientist hiring bar: BS/MS/PhD required, 10+ ML/GenAI eng, model training/eval/deployment focus |
| 66 | 0.460 | PASS | T- | STAMPEDE | 3 | 1 | 0 | 3 | 0 | Datadog — Staff Applied Scientist - Dashboards | AI-lab / research-scientist hiring bar: BS/MS/PhD required, 10+ applied science, eval/measurement/ML systems focus |
| 67 | 0.460 | PASS | T- | STAMPEDE | 3 | 1 | 0 | 3 | 0 | Datadog — Senior Staff GenAI Engineer - Application Performance Monitoring (APM) | AI-lab / research-scientist hiring bar: BS/MS/PhD required, 10+ ML/GenAI eng + 4+ cross-team technical lead, model development/deployment/eval focus |
| 68 | 0.437 | PASS | T- | STAMPEDE | 2 | 0 | 1 | 3 | 1 | Datadog — Staff Product Manager, Observability Data Platforms | VP+ / C-level leveling |
| 69 | 0.437 | PASS | T- | STAMPEDE | 2 | 0 | 1 | 3 | 1 | Datadog — Group Product Manager - Bring Your Own Cloud | VP+ / C-level leveling |
| 70 | 0.437 | PASS | T- | STAMPEDE | 3 | 1 | 0 | 3 | 0 | Datadog — Distinguished Architect, AI | AI-lab or research-scientist hiring bar |
| 71 | 0.425 | PASS | T- | STAMPEDE | 3 | 1 | 0 | 2 | 0 | Peloton — Machine Learning Engineer III | AI-lab or research-scientist hiring bar |
| 72 | 0.414 | PASS | T- | STAMPEDE | 3 | 0 | 0 | 3 | 0 | Datadog — AI Research Scientist - Datadog AI Research (DAIR) | AI-lab or research-scientist hiring bar |
| 73 | 0.402 | PASS | T- | STAMPEDE | 2 | 0 | 1 | 3 | 0 | Datadog — Group Product Manager - Code Security | VP+ / C-level leveling |
| 74 | 0.391 | PASS | T- | STAMPEDE | 3 | 1 | 0 | 3 | 0 | Datadog — Staff Applied Scientist - Agentic Interfaces | AI-lab / research-scientist hiring bar: BS/MS/PhD required, 10+ applied science, eval/measurement/ML systems focus; on-site only: #LI-Onsite, no remote option stated |
| 75 | 0.356 | PASS | T- | STAMPEDE | 2 | 0 | 0 | 3 | 0 | Datadog — Manager I, Engineering - Applied AI - Natural Language & Conversational Interfaces | AI-lab or research-scientist hiring bar |

## Top 20 — assessments

1. **Justworks — Product Operations Manager, AI & Systems** · 0.885 PURSUE T1 · compete MED · comp $131,000–$169,000
   Perfect shape fit: product ops + AI systems + regulated domain. Live req, NYC hybrid. Comp at lower end; competition moderate for niche role.
   https://boards.greenhouse.io/justworks/jobs/7839622?gh_jid=7839622

2. **Ramp — GTM Senior Business Systems Analyst, Pre-Sales** · 0.874 PURSUE T1 · compete MED · comp $145,800–$182,200
   Live senior analyst role, HubSpot/Salesforce GTM systems. Excellent shape fit (RevOps, automation, AI tooling). High-growth fintech, NYC remote. Comp at floor.
   https://jobs.ashbyhq.com/ramp/aa433e44-f095-484b-a46a-a330583d84b0

3. **Ramp — GTM Senior Business Systems Analyst – Channel Sales** · 0.874 PURSUE T1 · compete MED · comp $145,800–$182,200
   Channel/partner GTM systems analyst. Salesforce, integrations, attribution. Niche shape (partner ops) filters applicants. Same comp band, NYC remote, stable fintech.
   https://jobs.ashbyhq.com/ramp/2d2c336c-16e7-4f27-b0cd-5bb6055cdf21

4. **Squarespace — Business Development Manager, AI Discoverability and Scheduling Partnerships** · 0.862 PURSUE T1 · compete MED · comp $148,500 - $215,000
   Strong fit: BizDev x AI ecosystem x partnerships. Reports to AD, NYC hybrid. AI adoption is core. Comp floor solid. Competition moderate for title.
   http://www.squarespace.com/about/careers?gh_jid=8101310

5. **Betterment — Business Systems Architect, GTM Systems** · 0.851 PURSUE T1 · compete MED · comp $155,000–$175,000
   Live staff-level GTM systems role at stable fintech. Strong shape fit (Salesforce, integrations, architecture). AI mentioned but not core. Comp slightly below senior operator floor.
   https://www.betterment.com/careers/current-openings/job?gh_jid=8074484&gh_jid=8074484

6. **Datadog — Director, GTM Enablement Operations** · 0.828 PURSUE T1 · compete HIGH · comp $198,000–$264,000
   Director GTM Enablement Ops at public company. Operator-level (10+ yrs ops/RevOps). AI/automation explicitly rewarded. Hybrid NYC. Comp strong. Logistics: hybrid, not full remote.
   https://careers.datadoghq.com/detail/8137579/?gh_jid=8137579

7. **Ramp — GTM Business Systems Analyst – Post Sales** · 0.805 PURSUE T1 · compete MED · comp $145,800–$182,200
   GTM systems + Salesforce automation + AI tooling. Excellent shape fit, NYC remote. Level slightly junior (analyst vs manager); comp mid-range.
   https://jobs.ashbyhq.com/ramp/196e4e25-c452-430d-8b2f-36a40f88a2ae

8. **Ramp — AI Solutions Strategist** · 0.805 PURSUE T1 · compete HIGH · comp $176,000–$240,000
   AI solutions + finance workflows + customer discovery. Strong comp, NYC hybrid. Shape fit good but solutions/consulting lane, not ops-native operator.
   https://jobs.ashbyhq.com/ramp/cbdf2857-1675-4b68-8cb5-2f92a20faa75

9. **Datadog — Senior Product Manager - Search** · 0.782 PURSUE T2 · compete HIGH · comp $192,000–$240,000
   Senior PM Search: niche shape (search + ranking + agentic UX + MCP). Thin pool for PM who understands agent-human UX duality. Candidate's AI builder edge + ops systems background differentiates. NYC/Boston hybrid. Comp borderline.
   https://careers.datadoghq.com/detail/7974481/?gh_jid=7974481

10. **Betterment — Sr. Manager, Revenue Operations - Deal Desk & GTM Process Improvement** · 0.759 PURSUE T2 · compete MED · comp $135,000–$160,000
   Deal desk + RevOps + commercial ops at fintech. Perfect shape fit, NYC hybrid, stable. Comp floor weak; AI not rewarded. Strong operator role.
   https://www.betterment.com/careers/current-openings/job?gh_jid=8075138&gh_jid=8075138

11. **Ramp — Product Operations \| AI Revenue Systems** · 0.759 PURSUE T2 · compete HIGH · comp $128,000–$180,000
   Product ops + AI agents + GTM data platform. Excellent shape fit, AI-native build required. Level junior (1–3 yrs PM); comp floor weak for senior operator.
   https://jobs.ashbyhq.com/ramp/4e9886c1-134b-4cc7-9bcf-eb56bd0ca71f

12. **Squarespace — GTM Marketing Programs Manager** · 0.747 PURSUE T2 · compete MED · comp $85,500 - $138,000
   GTM Programs Manager (ops/systems shape, strong fit). NYC hybrid. Comp floor well below senior-operator. AI familiarity mentioned but not core. Level junior.
   http://www.squarespace.com/about/careers?gh_jid=8144850

13. **Oscar Health — Senior Product Manager, Marketplace** · 0.747 PURSUE T2 · compete HIGH · comp $163,944–$215,176.50
   Specific, live req at stable health-tech unicorn. Senior PM title attracts broad applicant pool. Marketplace/ecommerce shape is adjacent but not core operator lane. AI mentioned but not a hiring differentiator.
   http://www.hioscar.com/careers/7977877?gh_jid=7977877

14. **Oscar Health — Group Product Manager, Lucie Platform** · 0.747 PURSUE T2 · compete MED · comp $180,504–$236,911.50
   Group PM = people-management step up. Candidate has 20yr ops, not PM ladder. Stable company, good comp. Marketplace/enrollment platform is niche but PM-centric, not ops-systems-AI bridge. Leveling mismatch.
   http://www.hioscar.com/careers/8070624?gh_jid=8070624

15. **Datadog — Senior Product Solutions Architect - AI Agent** · 0.747 PURSUE T2 · compete HIGH · comp $185,000–$246,000
   Senior PSA, AI Agent Observability. Niche shape (solutions architect + AI observability + field). Thin pool for this cross-functional role. Candidate's ops/GTM/systems background + AI builder edge fits. 40% travel, NYC/Boston/Denver/SF hybrid. Comp borderline.
   https://careers.datadoghq.com/detail/7627531/?gh_jid=7627531

16. **Datadog — Senior Product Manager - Data Agent** · 0.747 PURSUE T2 · compete STAMPEDE · comp $192,000–$240,000
   Elite-eng stampede (Senior PM at Datadog). AI-native product bar. Thin operator fit despite AI interest.
   https://careers.datadoghq.com/detail/7785350/?gh_jid=7785350

17. **Peloton — Lead Product Manager** · 0.736 PURSUE T2 · compete HIGH · comp $215,029–$265,202
   Live req, named team, strong comp. But Lead PM at public company attracts stampede of PM applicants. AI/automation mentioned but not core differentiator. Operator fit is moderate (product ops, not GTM/RevOps).
   https://careers.onepeloton.com/en/all-jobs/?gh_jid=8093029

18. **MongoDB — Senior Product Manager, Post Sales** · 0.713 PURSUE T2 · compete HIGH · comp $136,000–$266,000
   Senior PM, post-sales GTM ops. Strong shape fit (support/CS platforms, workflow automation). AI secondary. Multi-city hybrid.
   https://www.mongodb.com/careers/job/?gh_jid=7975695

19. **Datadog — Senior Product Manager - Fleet and Lifecycle Management** · 0.713 PURSUE T2 · compete STAMPEDE · comp $192,000 - $240,000
   Senior PM at elite-eng stampede (Datadog). Fleet/lifecycle mgmt is infrastructure, not operator lane. AI-agent use case mentioned but not core hiring bar.
   https://careers.datadoghq.com/detail/8077142/?gh_jid=8077142

20. **Datadog — Senior Product Manager - Bits Agent Builder** · 0.713 PURSUE T2 · compete STAMPEDE · comp $192,000–$240,000
   Datadog prestige PM role. Agent platform is AI-native product engineering, not operator bridge. Stampede.
   https://careers.datadoghq.com/detail/8092004/?gh_jid=8092004


## Known scorer misfires (v1.0, not corrected by hand)
- Haiku over-fires the AI-lab gate on any "AI Engineer" title; those are FDE-lane roles anyway, so a bridge PASS is the right fate for the wrong reason.
- "Senior Director" was read as VP+ (MongoDB Global AI Native & POD Program). Senior Director is inside the level target; treat that row as CONSIDER by hand.
- One Datadog FDE role was gated as quota-carrying sales; again FDE-lane, PASS is the right fate here.
- Batch composition moves composites by ~0.05 between runs at temp 0; tiers are stable, ranks inside a tier are not.

