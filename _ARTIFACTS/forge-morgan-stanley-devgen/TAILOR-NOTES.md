# Tailor notes: DevGen.AI Lead Product Engineer, Executive Director · Morgan Stanley

**Source:** Workday req PT-JR042405 (jd-full.txt, jd-workday.json), fetched 2026-09-04. New York, $195,000 to $275,000 base. ATS: Workday (PDF upload; ATS .txt as paste fallback).
**Record of record:** resume.arcs.care (public/resume.html ROLES + CONSULTING_CLIENTS + education block). Every claim below traces to it or to a public repo.
**Reference length:** two pages (per _ARTIFACTS/resume-trinity-fdgenai). The first cut was one page; restored to two, see "Seams repaired".

## Role shape

Co-leader of an internal AI development platform. Multi-agent orchestration and RAG at the core. Connective tissue across product, engineering, governance, InnerSource contributors, divisional stakeholders. Platform enablement, not customer embed. The resume leads with the platform-builder archetype, then product-and-engineering breadth, then governance, then reuse.

## JD hooks -> what the resume puts against each (honest mappings only)

| JD hook | Resume answer | Grade of the lead claim |
|---|---|---|
| "reusable agents, prompts, patterns, accelerators, APIs" · "MCP, multi-agent orchestration" | ARCS: custom MCP server, agentic orchestration layer, Claude tool use, human-in-the-loop control | documented (public repos, commit trail) |
| "Innovate to Incubate to Implement lifecycle ... governance gates, production readiness" | Grayscale regulated release gates (legal, risk, compliance in the loop); CI gates on ARCS (lint, build, leak-check as test, security scan, auto-rollback) | Grayscale: documented title/dates, self-reported figures · ARCS CI: documented |
| "Champion InnerSource ... firmwide capabilities rather than one-off solutions" | Open-source section: germinate, token-savings-bank, rosetta-shell, arcs-field-scan, each MIT-licensed with a conformance or regression suite; CTF first shared data layer across 3 BUs | OSS: documented (good.arcs.care, GitHub) · CTF: self-reported |
| "Translate customer demand, usage data ... into prioritized product backlog themes" | Pillar "Product and engineering in one head"; Squat roadmap/backlog/sprint ownership | self-reported (record of record) |
| "Track ... adoption, productivity, ROI, contribution ... metrics" | Skills block "Measurement and adoption"; WTA attribution and $850K+; CTF 20% | self-reported |
| "regulated ... enterprise technology environments" | SEC/FINRA (Grayscale), HIPAA (Twill), GDPR (GoPro) | documented context, self-reported outcomes |
| "Strong technical fluency in APIs, cloud-native engineering ... access control" | Engineering stack block: TypeScript, Node, Next.js, Python, Postgres, Vercel, Supabase; RBAC and identity/auth | documented (public repos) |
| "10+ years ... product engineering ... enterprise technology delivery" | 2016 to present in named product-leadership roles; "two decades" per record of record | documented titles/dates |
| "prototypes, reference implementations, technical documentation" | ARCS platform + OSS tools with docs | documented |

## Evidence grades per lead claim

- documented: MCP server, agentic orchestration, HITL control; OSS tools with conformance suites; titles and dates for ARCS, Grayscale, Squat, CTF, WTA, Twill, Axon, GoPro, Verizon; engineering stack; Oberlin BA; MIT xPRO certificate (one).
- self-reported: $7B AUM, 10 products (Grayscale); seven-figure engagement, $350M ARR client (Squat); 20% net-new revenue (CTF); $850K+ year one, under 120ms scoring (WTA); 3 product lines / 2 of 3 (Twill); five 5G ventures (Verizon).
- unverifiable (not on the page): 60% decision-noise reduction, 3 to 5x time-to-insight.

## Defend-or-drop list (what the resume does NOT claim)

1. **RAG pipeline / vector search.** JD names RAG. ARCS does structured context assembly from prior decision receipts (lineage), not vector retrieval. Resume says "context management"; no RAG keyword. Defend in interview by describing the receipt-lineage design and what a RAG layer would add.
2. **Azure OpenAI / Bedrock / Vertex / internal AI gateway.** No claim. Record is Claude API direct on Vercel + Supabase. Say so if asked.
3. **Managing engineering teams.** Record supports cross-functional delivery and sole-technology-partner ownership, not engineer head-count management. Resume says "cross-functional delivery".
4. **CS / Engineering degree.** JD lists it. Record is BA Studio Art (Honors) + MIT xPRO certificate. Not addressed on the page; honest answer is two decades of shipped systems and public code.
5. **60% / 3 to 5x figures.** Cut from the page (self-measured on own platform). Defend only if asked how ARCS is measured.
6. **35% release-cycle reduction, RBAC "policy-at-the-glass" at Grayscale.** Present on the trinity render; not in the record of record (resume.arcs.care). Not used here.
7. **Section4 certificate, second MIT certificate.** Not in the record of record. Not used.

## Seams repaired this session

- Headline under the name was the requisition title nearly verbatim. Rewritten to "AI-native product engineer · builds the platform, runs the product". Document title keeps the role.
- One page -> two pages. Restored: advisory engagements as their own section (Twill, Axon, GoPro, Verizon each with a line), Open Source section (four tools), engineering-stack and enablement skill blocks, extra ARCS/Grayscale/WTA bullets. Each is on the record of record or a public repo.
- 60% / 3 to 5x removed from the ARCS bullet; mechanism described instead.

## Render

`./render.sh resume-morgan-stanley-devgen-ats.html` -> 2-page PDF + page PNGs. Both pages viewed: page 1 full, no orphan header; page 2 ends after Education and footer with clean white space. ATS .txt regenerated from the HTML (tag strip), not from pdftotext (which letter-spaced the target chip).
