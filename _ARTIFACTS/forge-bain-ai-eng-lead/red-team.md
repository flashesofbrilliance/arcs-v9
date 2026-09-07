# red-team · Bain AI Eng Lead bundle (stage 7, subtractive only)

Pass run 2026-09-06 on `resume-bain-ai-eng-lead-ats.html` and `page.html`, reading as a skeptical hiring panel (Bain AIS engineers) plus a background-check vendor. Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | The JD's core technical list (RAG, fine-tuning, embeddings, hybrid retrieval, evaluation frameworks with hallucination/precision-recall/latency/cost metrics, GenAIOps, guardrails/red-teaming, HITL, APIs/microservices/CI/CD) is mostly absent from the resume. | True, and this is the biggest single risk in the bundle. | Not papered over. Named explicitly in TAILOR-NOTES section 3 (Dropped) and in the page's "honest gaps" note. Nothing invented to cover it. |
| 2 | "3-5+ years hands-on" required; candidate has roughly one year of hands-on LLM/agentic building (ARCS, 2025-present), inside a 20-year career at Director-and-above scope. | True. Scorer flagged the same gap. | Resume does not state a years-of-AI-experience figure at all (avoids implying either "one year" undersells or "twenty years" oversells). TAILOR-NOTES section 5 states the mismatch plainly for the human to weigh. |
| 3 | "AI-native builder, forward-deployed with clients" could read as implying the "Forward Deployed Engineer"-style title Bain does not use for this req (the req is "Lead, AI Engineer," an IC role). | Weak but worth a look. | Headline uses "forward-deployed" as a description of working style (embedded, client-facing), not a claimed title; no title is claimed anywhere on the page or resume. Left as is, since dropping "forward-deployed" would lose the one genuinely differentiated, checkable claim (the Squat embed). |
| 4 | "Tool use and function calling" on the skills line is a JD-mirroring phrase, not verbatim from the record. | True. | Kept, but graded self-reported in TAILOR-NOTES with a specific defend answer (built directly against Claude's API, no named orchestration framework). If asked to name a framework (LangChain, LangGraph, CrewAI, etc.) and it cannot be discussed fluently, drop the phrase. |
| 5 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP; none are on the record's skills list. | True, but consistent with the CTF/WTA data-layer roles and the general resume (same treatment as the Citi bundle). | Kept, graded self-reported, each is on the defend-or-drop list. |
| 6 | "$7B AUM" can read as personal scope. | Partly true. | Resume already binds it to the product suite ("$7B AUM" directly after "10 SEC/FINRA-regulated ... products"). No inflation left. |
| 7 | No mentoring or people-management claim, though the JD explicitly names "support or informally mentoring peers" and "eagerness to grow into a technical leadership role" as desired. | True, and left as a gap rather than invented. | Named in TAILOR-NOTES as dropped (not claimed); no resume change. |
| 8 | Comp: JD lists $179.5K-$203.5K by state. No comp talk anywhere in the resume or page.html (air-gap rule). | Confirmed clean. | Grep for "$179" / "$203" / "comp" against page.html and resume returns 0 outside this file. |
| 9 | "Client-facing translator" pillar leans on Grayscale/Squat coordination bullets already used elsewhere on the page; some repetition of the same two engagements across pillars. | True, minor. | Left as is; the reference bundle (Citi) has the same pattern (Squat and ARCS anchor multiple pillars) and repetition across a short pillar list is a known, accepted shape here, not a new problem. |
| 10 | Air-gap: no other company's bundle name, no hiring-manager name, no comp figure, no scoring vocabulary (tier/band/composite/pursue) anywhere in page.html. | Checked. | Confirmed clean by grep (see kintsugi.json). |

## Not touched, on purpose

- No claim was rewritten upward. The largest gap (technical depth against the JD's genAI-engineering list) is stated, not minimized, in both TAILOR-NOTES and the page's honest-gaps note.
- The leveling/seniority tension (hit #2) is surfaced for the human, not resolved by the resume; a resume cannot honestly resolve a scope mismatch, only avoid pretending it isn't there.
