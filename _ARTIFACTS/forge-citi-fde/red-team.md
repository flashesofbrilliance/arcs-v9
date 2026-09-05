# red-team · Citi FDE bundle (stage 7, subtractive only)

Pass run 2026-09-04 on `resume-citi-fde-ats.html` and `public/forge-citi-fde.html`, reading as a skeptical hiring panel plus a background-check vendor. Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | "Direct experience as a Forward Deployed Engineer" is a required qualification; the candidate never held the title. | True. | Resume already avoids the title (headline is the archetype). Landing page states the gap in plain words in the mapping note and in STRESS-TEST. No change to the resume. |
| 2 | Squat mapping row on the landing page said "engineering, clinical, and operations in one room." Figurative; the record says "partnered across engineering, marketing, design, clinical, and operations to align stakeholders and ship on schedule." | True: colour beyond the record. | Narrowed to the record's wording: "aligned engineering, clinical, and operations to ship on schedule." |
| 3 | A CSS comment in the landing page referenced the source page of another application bundle by company name. Air-gap rule: no other companies. | True. | Comment stripped. Grep for the name returns 0. |
| 4 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP, distributed query systems, GitHub; none are on the record's skills list. | True, but consistent with the CTF/WTA data-layer roles and the general resume. | Kept on the resume; graded self-reported on the landing page and in TAILOR-NOTES; each is on the defend-or-drop list. Would cut on a single "cannot discuss fluently." |
| 5 | "$7B AUM" can read as personal scope. | Partly true. | Resume already binds it to the product suite ("$7B AUM" after "10 SEC/FINRA-regulated ... products"). Landing page grade line adds "the firm's public figure for the period, not a personal P&L." No inflation left. |
| 6 | "Two decades" | Arithmetic from 2006 graduation: 20 years. | No change. |
| 7 | Preferred skills the posting names and the candidate cannot show: NLP, model training, AWS/GCP/Azure, payments. | True. | Not claimed anywhere. Listed as gaps in STRESS-TEST and the mapping note. |
| 8 | Landing page kicker says "forward-deployed · AI transformation". Could be read as a held title. | Weak. Lowercase, archetype plus the posting's own program name, and the gap is stated two sections down. | No change. |
| 9 | "In production, not experiments" for ARCS. | Checkable: live MCP server, public repos. | No change. |
| 10 | The GRADED ticker in the hero says every claim is "traced to a record of record." The record URL serves an HTML page, not a PDF. | True, and disclosed. | No page change; the discrepancy is logged in TAILOR-NOTES and record-of-record.txt as an open question for the human. |

## Not touched, on purpose

- Resume HTML unchanged this pass, so no re-render was needed; PDF, PNGs, and ATS text on disk remain current (verified same mtime as the HTML).
- No claim was rewritten upward. Two removals on the landing page (hits 2 and 3), zero on the resume.
