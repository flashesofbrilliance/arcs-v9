# TAILOR-NOTES · monday.com · Forward Deployed Engineer

Built 2026-09-06 (LIGHT tier of the counterpart-application forge: stages 1, 5, 7, 8, 9). All inputs
pre-staged; no JD fetch, no re-grade, no design-system exploration, no API/DB call this pass.
Record of record: `_STATE/job-search/forge-inputs/record-of-record.txt` (the ROLES / TRAJ / CONSULTING_CLIENTS
/ TRUE_NORTH / SKILLS content served at resume.arcs.care/resume.pdf, per the prior forge-citi-fde pass).
JD: `jd-full.txt`. Resume cut: `resume-monday-fde.html` (2 pages, verified; headline is the archetype, not
the req title).

## 1. JD hooks and what the resume puts against each

| JD hook | What the resume answers with | Where in the cut | Honest? |
|---|---|---|---|
| MCP named explicitly (developer tools incl. "the monday.com API, MCP, and apps framework") | ARCS: built and operate a live MCP server + agentic orchestration layer on Claude, in production. This is the scorer's own flagged direct hit. | Pillars (primary), ARCS job | Yes, documented via public GitHub |
| Fluency in Generative and Agentic AI, LLM workflows, agent orchestration, tool use | ARCS: AI-native analysis pipeline on Claude, agentic orchestration layer, in production not experiments. | Summary, ARCS job, skills | Yes |
| AI-assisted editors (Cursor, Claude Code) in daily use | Not claimed as a named tool. This session and its predecessor are built inside Claude Code, which is circumstantial but not a resume-line claim; left off rather than asserted without a checkable trace. | (not on page) | Gap acknowledged, not invented |
| Evaluation harnesses, guardrails, human-in-the-loop, tracing, production AI failure modes | Not claimed directly. ARCS's "experimentation and outcome-capture framework" and "in production, not experiments" gesture at operational rigor without asserting eval-harness or guardrail work specifically. | ARCS job (soft) | Yes, no overclaim |
| APIs (REST, GraphQL), webhooks, MCP, SCIM, SAML/OAuth | MCP: yes, hands-on. REST/webhooks: implied by "MCP server" build but not separately claimed. GraphQL, SCIM, SAML/OAuth: not claimed, not in record. | Skills (MCP only) | Partial; real gap on SCIM/SAML/OAuth, left open |
| TypeScript and JavaScript, React or Node.js, full-stack preferred | New skill line added this pass: "TypeScript and JavaScript, Next.js (ARCS platform, public repo)." The record of record does not list a programming language under SKILLS, but ARCS is publicly built and shipped as a Next.js/TypeScript app on GitHub (flashesofbrilliance/arcs-v9), so the claim is checkable, not invented. React vs. Node depth is not separately claimed. | Skills, new "Application layer" group | Documented (public, checkable), narrower than the JD's ask |
| n8n or Workato automations, SQL/scripts for data migration | SQL is in the record. n8n/Workato: not claimed, not in record. | Skills (SQL only) | Gap acknowledged |
| CI/CD, version control, deploy to AWS/GCP/Azure | Not claimed. GitHub is claimed (version control, public). Cloud deploy platforms: not in record. | (not on page) | Gap acknowledged |
| 3+ years as FDE, software engineer, or technical consultant delivering hands-on work for external customers in complex enterprise environments | Never held the title "Forward Deployed Engineer." The cut proves the shape instead: Squat (sole tech partner, discovery through QA and handoff, 2019-2020), the four other embedded/advisory engagements 2019-2024, and ARCS (2025-present, hands-on build). Headline names the archetype. | Headline, pillars, embedded section | Yes; title never claimed, shape substantiated |
| Consultative range: frame a business problem, communicate to non-technical audience | Grayscale (cross-functional coordination through regulated gates), Squat (cross-functional across engineering, marketing, design, clinical, operations), CTF/WTA/Twill (translated business problems into KPI frameworks). | Grayscale, Squat, CTF/WTA | Yes |
| Adaptability across customers, tech stacks, unfamiliar domains | Five embedded engagements across health, gov, consumer, telecom, plus finance (Grayscale) and sports (WTA). Named explicitly as breadth in the record's own TRUE_NORTH copy. | Embedded section | Yes |
| Project-management comfort, standalone engagements, several projects at once | Squat: "sole technology partner," owned roadmap/backlog/sprint planning. ARCS: "operate the full stack... standalone, end to end." | Squat, ARCS | Yes |
| BS/BA CS or equivalent professional experience | Oberlin College BA, Studio Art (not CS); the JD explicitly allows "equivalent professional experience," which the two-decade record carries. | Education | Yes, disclosed as-is |
| Hybrid, 3 days/week, New York office | "New York City (hybrid, 3 days on site)" | Header | Yes |
| $140,000-160,000 base | Not on the resume (comp is never resume content); scorer already flagged this sits under target, see red-team and the scorer's own dim (comp_level:1). No page content changes based on comp. | (not on page) | N/A |

## 2. Evidence grade per lead claim

Grades: **documented** (public and checkable, or verbatim in the record of record) · **self-reported**
(the candidate's own figure, in the record, not independently verified) · **unverifiable** (tacit, cannot
be shown).

| Claim on the page | Grade | Trace |
|---|---|---|
| ARCS: MCP server + agentic orchestration on Claude, in production, 2025 to present | documented | record ROLES.arcs; public GitHub (flashesofbrilliance/arcs-v9) |
| TypeScript/JavaScript, Next.js on ARCS | documented (public repo, not in record's own SKILLS list) | inferred from public GitHub, not from record text, see defend-or-drop |
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
| "Two decades" | documented by arithmetic (2006 to 2026) | education dates |

## 3. Defend-or-drop list

**Defend (kept):**
1. "Forward-deployed" as archetype, never as a held title. Answer: the Squat embed (sole product and
   tech partner, discovery through handoff) and ARCS (built on contact with the real problem, no
   inherited spec). If asked "were you ever titled FDE": no, and the resume does not say so.
2. TypeScript/JavaScript/Next.js skill line. Answer: not in the record's own SKILLS list, but the ARCS
   platform is publicly built and shipped in TypeScript/Next.js on GitHub; point to the repo, do not
   claim deep React or Node.js authorship beyond what the repo shows. This is the single claim most
   likely to be probed technically (see red-team #1).
3. $7B AUM. Answer: the suite of 10 products the GTM covered; Grayscale's public AUM figure for the
   period, not a personal P&L.
4. $850K+ and <120ms (WTA); 20% net-new revenue (CTF). Answer: internal figures from the 2016-2019
   builds, consistent with the roles, not externally auditable.
5. "In production, not experiments" for ARCS. Answer: live MCP server, live app, public commit trail.

**Dropped (not on the page):**
1. SCIM, SAML 2.0/OAuth 2.0, GraphQL as named protocols. Never claimed as hands-on; only MCP is claimed
   with confidence.
2. n8n, Workato, AWS/GCP/Azure deploy experience. Not in the record; not invented.
3. Named AI-assisted editors (Cursor, Claude Code) as a resume line. True in practice but not a
   checkable, record-backed claim distinct from the ARCS build itself; left off rather than asserted.
4. Eval harnesses / guardrails / HITL review as a named competency. ARCS gestures at this softly
   ("experimentation and outcome-capture framework") but no separate line claims production-AI-ops
   experience at the depth the JD implies.
5. Any claim of a held "Forward Deployed Engineer" or "software engineer" title. Never held; not
   invented.
6. Any project-management certification or formal PM title. The JD asks for "some project management
   experience," which the Squat backlog/sprint-planning line already carries; nothing further claimed.

## 4. Headline check

Line under the name: "Forward-deployed product and AI builder." Archetype only, no domain qualifier
needed this time (the citi-fde version added "regulated domains"; monday.com's posting is not
regulated-industry specific, so the domain qualifier is dropped rather than left in a way that doesn't
serve this posting). The req title appears only in the `<title>` tag and in the "Target" line, labeled
as a target. Passes the rule.
