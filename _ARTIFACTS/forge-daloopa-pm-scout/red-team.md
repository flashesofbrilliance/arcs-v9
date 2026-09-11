# red-team · Daloopa PM Scout bundle (stage 7, subtractive only)

Pass run 2026-09-07 on `resume-daloopa-pm-scout-ats.html` and `page.html`, reading as a skeptical hiring panel plus a background-check vendor. Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | "Financial workflows" claim could read as direct equity-research/analyst-desk experience, which the candidate has never had. | True; the scorer's own assessment flags this ("financial workflows are adjacent"). | Grayscale is scoped explicitly to "regulated digital-asset investment products," never to comps, modeling, or analyst tooling. The mapping table and STRESS-TEST stage on the page both name the gap in plain words. No resume change needed; it was written scoped from the start. |
| 2 | WTA bullet frames <120ms scoring as "tuned to a live, cyclical usage window," echoing Scout's earnings-cycle cadence. Could read as if the candidate has direct earnings-cycle / fintech-cadence experience. | Partly true: a framing choice, not a new fact. | Kept, because the underlying fact (real-time scoring, live events, 2016-2018) is unchanged from the record; TAILOR-NOTES defend-or-drop item 2 states plainly this is an analogy, not a claim of prior fintech-cadence work. |
| 3 | JD explicitly asks for "the hardest problem you hit shipping an LLM-powered product... walk through it in detail" (evals, tool design, retrieval, prompting). Resume claims the evaluation/outcome-capture mechanism but no specific technical failure mode. | True: the record does not carry that level of detail. | Not fabricated. Left at the altitude the record supports (evaluation framework, agentic orchestration, in production); the specific war story is explicitly deferred to the interview in TAILOR-NOTES rather than invented here. |
| 4 | "Success looks like" section wants retention/engagement metrics moved and traced to product decisions. Resume makes no such claim for ARCS. | True; no metric exists in the record for ARCS user counts or retention. | No claim added. Confirmed as an open gap in TAILOR-NOTES defend-or-drop, item 4 under "Dropped." |
| 5 | CTF title is "Sr. Director, Data & Strategy," not a product title, but sits in the "Experience" section alongside genuine PM roles, which could blur the "owned a product end to end, not as a contributor" framing. | Weak but worth stating. | Not counted toward the PM-ownership claim in TAILOR-NOTES section 1 ("CTF kept for the data-layer proof, not counted toward the 'PM title' claim"); resume itself never labels CTF as a product role. |
| 6 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP; none are on the record's skills list. | True, but consistent with the CTF/WTA data-layer roles (same call made for the Citi bundle). | Kept, graded self-reported in TAILOR-NOTES, each on the defend-or-drop list; would cut on a single "cannot discuss fluently." |
| 7 | "$7B AUM" can read as personal scope. | Partly true. | Resume already binds it to the product suite ("$7B AUM" after "10 SEC/FINRA-regulated ... products"). No change needed. |
| 8 | Landing-page kicker/hero language must not use scoring vocabulary (tier, band, composite, pursue) per the rules for this bundle. | Checked. | Grep for those terms on page.html returns 0 (excluding the internal grading legend's own words "documented / self-reported / unverifiable," which are not the forbidden scoring vocabulary). |
| 9 | Air-gap: page.html must carry no counterpart surnames, no hiring-manager name, no comp talk, no record-of-record link. | Checked. | No names beyond "Zach Harris" / "Daloopa" (company name only, required for context); no comp figures; no link to record-of-record.txt or resume.arcs.care. |
| 10 | "In production, not experiments" for ARCS. | Checkable: live MCP server, public repos. | No change. |

## Not touched, on purpose

- No claim was rewritten upward. The gap named in hit #1 (financial-workflow adjacency, matching the scorer's own dims note) is the single most important honest disclosure in this bundle and is stated in three places: TAILOR-NOTES section 5, the resume's own scoping language ("regulated digital-asset investment products," never "financial analyst" or "equity research"), and the page's mapping-table gap line.
- No resume text changed as a result of this pass; every hit above was already scoped correctly at first draft.
