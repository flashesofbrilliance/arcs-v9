# red-team · monday.com Deployment Architect bundle (stage 7, subtractive only)

Pass run 2026-09-06 on `resume-monday-deployment-architect-ats.html` and `page.html`, reading as a skeptical Professional Services hiring panel plus a background-check vendor. Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | The posting requires "solutions architect or forward-deployed engineer" title experience; the candidate never held either title. | True. | Resume already avoids both titles (headline is the archetype). Landing page states the gap in the mapping note and STRESS-TEST. No change to the resume. |
| 2 | The posting wants named estimation models, SOW authorship, and estimation-consumption impact, and the record shows go/no-go KPI framework work rather than SOW ownership. | True: this is a real gap, not colour. | Kept the resume narrower than the posting: "KPI frameworks informed go-forward decisions" (Twill/Verizon), never "built the estimation model" or "wrote the SOW." Named as an open gap in TAILOR-NOTES and STRESS-TEST rather than papered over. |
| 3 | The posting names SCIM, SAML 2.0/OAuth 2.0, GraphQL, and webhooks as integration standards; only MCP is genuinely evidenced. | True. | None of the four unevidenced standards were added to the skills line. MCP alone is claimed, and it is the one directly true (ARCS's own MCP server). |
| 4 | "AI quality... evaluation, guardrails, human review, observability" is a named requirement; Twill's KPI-driven viability testing is not the same as production observability of a live AI system. | True, and a real gap. | The Twill bullet is worded as market-viability testing and go-forward decisions, not upgraded to "built evaluation/observability infrastructure." Gap named explicitly in TAILOR-NOTES and on the landing page. |
| 5 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP; none are on the record's skills list. | True, but consistent with the CTF/WTA data-layer roles and the general resume, and carried over unchanged from the prior bundle where it was already graded self-reported. | Kept on the resume; graded self-reported on the landing page and in TAILOR-NOTES; each is on the defend-or-drop list. Would cut on a single "cannot discuss fluently." |
| 6 | "$7B AUM" can read as personal scope. | Partly true. | Resume already binds it to the product suite ("$7B AUM" after "10 SEC/FINRA-regulated ... products"). Landing page grade line adds "the firm's public figure for the period, not a personal P&L." No inflation left. |
| 7 | "Two decades" | Arithmetic from 2006 graduation: 20 years. | No change. |
| 8 | Preferred/required posting elements the candidate cannot show: Cursor/Claude Code named editor use, SCIM/SAML/OAuth/GraphQL, formal SOW authorship. | True. | Not claimed anywhere. Listed as gaps in STRESS-TEST and the mapping note. |
| 9 | Landing-page kicker could read as claiming the req title itself. | Weak. Lowercase, archetype phrasing, and the gap is stated two sections down. | No change, consistent with the reference bundle's disposition on the same pattern. |
| 10 | "In production, not experiments" for ARCS, and the MCP-server claim specifically. | Checkable: live MCP server, public repos. | No change. |
| 11 | The record-of-record URL serves an HTML page, not a PDF (carried-over open question from the prior bundle). | True, and disclosed. | No page change; logged in TAILOR-NOTES as an unresolved open question, same disposition as the prior bundle. |

## Not touched, on purpose

- No claim was rewritten upward to chase the posting's estimation/SOW/observability/protocol requirements. Where the record could not support a match, the gap was named rather than the resume language stretched.
- The scorer's comp-band and tier context (composite 0.778, tier 2, comp_level 1/3) never touched the resume or page.html; it appears only in TAILOR-NOTES §5, which is not an air-gapped surface.
