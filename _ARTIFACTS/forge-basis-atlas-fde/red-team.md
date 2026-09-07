# red-team · Basis Atlas FDE bundle (stage 7, subtractive only)

Pass run 2026-09-07 on `resume-basis-atlas-fde-ats.html` and `page.html`, reading as a skeptical hiring panel plus a background-check vendor. Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | "Member of Technical Staff" and "Atlas FDE" are the actual req titles; the candidate never held either. | True. | Resume headline names the archetype, never the title. Landing page states the gap in plain words in the mapping note and the STRESS-TEST stage. No change needed beyond the copy already written this way. |
| 2 | Posting's regulated context is specifically accounting firms; resume's regulated claims are SEC/FINRA (finance) and HIPAA (health), not accounting. | True: adjacent, not identical. | Landing page mapping note states the gap explicitly: "regulated finance and health, not accounting" rather than implying accounting-domain depth. |
| 3 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP, distributed query systems, GitHub; none are on the record's skills list. | True, but consistent with the CTF/WTA data-layer roles. | Kept on the resume; graded self-reported on the landing page and in TAILOR-NOTES; each is on the defend-or-drop list. Would cut on a single "cannot discuss fluently." |
| 4 | "$7B AUM" can read as personal scope. | Partly true. | Resume already binds it to the product suite ("$7B AUM" after "10 SEC/FINRA-regulated ... products"). Landing page grade line adds "the firm's public figure for the period, not a personal P&L." |
| 5 | "In office 5 days a week" on the resume matches the posting's non-negotiable but is a statement of agreement, not a fact about a past employer. | True. | Kept as a location/availability line, not framed as a claim about prior work arrangement. |
| 6 | "Two decades" | Arithmetic from 2006 graduation: 20 years. | No change. |
| 7 | Preferred/implied skills the posting rewards that the candidate cannot show: no prior employment at an AI-native or agent-first company, no accounting/audit domain depth. | True. | Not claimed anywhere; listed as gaps on the landing page and in TAILOR-NOTES. |
| 8 | "Zero-human loops" and "AI-native company at scale" are the posting's own phrases; using them verbatim on the resume could read as mirroring the posting rather than describing real work. | True risk. | Avoided; resume and page use the candidate's own language (agent-native systems, AI-native pipeline) rather than lifting the posting's phrasing. |
| 9 | "In production, not experiments" for ARCS. | Checkable: live MCP server, public repos. | No change. |
| 10 | Air-gap: page must carry no counterpart surnames, no comp talk, no link to the record-of-record file itself. | Checked. | hiring-manager.json marks status "unknown" with no guessed name; contact.json names no individual; page.html links only to public GitHub/status/build/good surfaces, never to the record-of-record.txt file. |

## Not touched, on purpose

- No claim was rewritten upward. Two gaps stated plainly on the landing page (accounting-domain depth, prior AI-native employment) rather than papered over.
- The resume's regulated-industry framing was left as SEC/FINRA and HIPAA, not softened toward "regulated" in a way that would imply accounting familiarity.
