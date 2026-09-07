# red-team · Codesearch AI FDE (Founding) bundle (stage 7, subtractive only)

Pass run 2026-09-06 on `resume-codesearch-fde-founding.html` and `page.html`, reading as a skeptical hiring panel plus a background-check vendor. Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | The posting requires a minimum of 2 years in a role explicitly in the FDE / Customer-Facing SWE / Solution-Sales Engineering family. The candidate never held any of those titles. | True. | Resume already avoids the title (headline names the seam, not the req title). Landing page states the gap in plain words in the mapping note and in STRESS-TEST. No change to the resume. |
| 2 | The role is 5 days a week in person plus ~20% travel. The record shows embedded engagements at client sites but not a standing 5-day-onsite cadence at any single employer. | True. | Not claimed on the resume or page as prior experience; named as an open gap on the page (mapnote, STRESS-TEST) rather than smoothed over. |
| 3 | "Forward-deployed" language on the page could read as the candidate implying the title was held. | Weak, but worth checking: the kicker reads "forward-deployed · founder-operator" (lowercase, archetype language) and the gap is stated two sections down. | No change; same construction the reference bundle used and cleared. |
| 4 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP, distributed query systems, GitHub; none are on the record's skills list. | True, but consistent with the CTF/WTA data-layer roles and the general resume. | Kept on the resume; graded self-reported on the landing page and in TAILOR-NOTES; each is on the defend-or-drop list. Would cut on a single "cannot discuss fluently." |
| 5 | "$7B AUM" can read as personal scope. | Partly true. | Resume already binds it to the product suite ("$7B AUM" after "10 SEC/FINRA-regulated ... products"). Landing page grade line adds "the firm's public figure for the period, not a personal P&L." No inflation left. |
| 6 | The JD's "software engineer moving toward customer-facing" bonus signal does not match the record's actual trajectory (commercial/product-first, increasing build depth over time). | True. | Not claimed either way on the page; left silent rather than forced into a shape the record does not support. |
| 7 | Preferred/bonus qualifiers the posting names and the candidate cannot show as directly documented: NLP or model-training depth, an ex-founder streak framed as the posting means it (the candidate is a current, active founder, not "ex"). | Mostly true; ARCS founder status is current, which is actually a stronger fit than "ex-founder," but is not the literal bonus phrase. | Framing kept as "founder-operator" (accurate, current) rather than forcing the posting's "ex-founder" language onto the page. |
| 8 | The mapping table's "Hands-on Python, REST / HTTP APIs" row cites the MCP server as proof of API integration; the record does not explicitly say "REST/HTTP APIs" for that build. | True: a reasonable inference from an MCP server (which is API-shaped), not a verbatim record claim. | Left as is; MCP-server-and-agentic-orchestration is the documented claim, and "Python and SQL across every data-layer build" is the separately documented skills claim. No wording implies REST/HTTP was verbatim in the record. |
| 9 | "Two decades" | Arithmetic from 2006 graduation: 20 years. | No change. |
| 10 | US work authorization requirement (no new-visa sponsorship) is not addressed anywhere in the bundle. | True, and correctly out of scope. | Not added; this is an application-form fact, not a resume/page claim, and inventing a status here would be worse than silence. |

## Not touched, on purpose

- No claim was rewritten upward. All new content this pass (the founding-startup framing, the "operate without a structured path" pillar, the FDE-titling gap) was added at the same evidence grade the record already supports; nothing was invented to close the leveling gap.
- The page's air-gap terms (no other company's name, no scoring vocabulary, no comp talk, no record-of-record hyperlink) verified clean by grep before this pass and after.
