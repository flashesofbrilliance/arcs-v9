# red-team · Doppel FDE Lead bundle (stage 7, subtractive only)

Pass run 2026-09-06 on `resume-doppel-fde-lead-ats.html` and `page.html`, reading as a skeptical hiring panel (the posting's own author, plus a background-check vendor). Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | The posting's entire integration portfolio (OAuth, SAML, SCIM, IDP sync, SSO, SIEM/SOAR, webhooks, ticketing tools) has zero support in the record. This is the literal job description, not a nice-to-have. | True, and material. | Not claimed anywhere on the resume or the page. Named explicitly as the top gap in TAILOR-NOTES, the mapping table's "gap" row, and the page's stress-test stage. Not softened. |
| 2 | "Lead and grow a team of forward deployed engineers" is the first bullet in the posting. The record shows leading *work* (roadmap, cross-functional coordination) at Squat and Grayscale, never leading *people* or a headcount. | True. | No people-management language added anywhere. Left as a stated gap. |
| 3 | ARCS's "turn one-off analysis into a reusable, compounding system" bullet could read as directly answering the posting's "turn one-off customer builds into product" ask, but the domains differ (decision analysis vs. customer-integration code). | True, risk of implied equivalence. | Bullet wording kept factual to what ARCS actually does; the analogy is flagged as loose in TAILOR-NOTES section 3, with a ready answer if probed rather than an inflated claim on the page. |
| 4 | "6+ years... building production applications" is a hard qualifier in the posting. The record shows twenty years across roles that blend product/GTM/strategy with hands-on build, not a clean multi-year run as an individual production engineer. | True. | The page never claims "6+ years as a software engineer." Thesis says "two decades across tech, data, and commercial operations" and lets the specific engineering artifacts (MCP server, data infra builds) speak for themselves. Flagged as a partial-support item in TAILOR-NOTES. |
| 5 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP; none are on the record's SKILLS list. | True, but consistent with the CTF/WTA data-layer roles (same disposition as the Citi bundle). | Kept on the resume, graded self-reported in TAILOR-NOTES, on the defend-or-drop list. |
| 6 | "$7B AUM" could read as personal scope rather than the firm's product-suite figure. | Partly true. | Resume binds it to "10 SEC/FINRA-regulated ... products" immediately before the figure. No further change needed. |
| 7 | No location is stated anywhere on the resume header, unlike the Citi bundle which named a city. | True — the JD does not state a location and none was fetched (out of scope for this light-tier run). | Header omits a location line rather than inventing one. Noted here so it is not mistaken for an oversight. |
| 8 | Headline "undefined mandates, owned end to end" could be read as implying the FDE Lead title was previously held. | Weak. Lowercase-style framing, archetype language, immediately followed by the explicit "Target · Forward Deployed Engineering Lead" box which marks it as aspirational. | No change. |
| 9 | The page must not use scoring vocabulary (tier, band, composite, pursue). | Checked. | `page.html` grepped clean; TAILOR-NOTES and this file (internal, not air-gapped) are the only places composite/band/tier appear, as required. |
| 10 | Air-gap: page.html must carry no counterpart surnames, no hiring-manager names, no comp talk, no record-of-record link. | Checked. | `hiring-manager.json` records "unknown" with no guessed name; page.html has no comp language and no link to record-of-record.txt. |

## The three claims most likely to be probed (for the report)

1. **"Forward Deployed Engineering Lead" as archetype, never a held title, and the near-total absence of the posting's core integration stack (OAuth/SAML/SCIM/SSO/SIEM/SOAR).** This is the single largest honest gap in the bundle. If asked directly, the answer is: no, I have never built an OAuth/SAML/SCIM integration or owned a SIEM/SOAR connector portfolio; what I bring is the ambiguity-ownership pattern (ARCS) and cross-functional/regulated delivery (Grayscale, Squat), and I would expect a ramp on the specific protocols.
2. **"Turning one-off customer builds into product" mapped from ARCS's decision-compounding framework.** If probed: this is a decision-analysis system recalibrating from prior outcomes, not customer-integration code graduating into a platform. Same underlying discipline (generalize the one-off), different domain. Should be named as an analogy, not a direct precedent.
3. **Self-reported figures ($7B AUM, $850K+, <120ms, 20%, seven-figure Squat engagement).** Same standing answer as every prior bundle: firm-level or internal figures from the era, consistent with the role held, not independently auditable.

## Not touched, on purpose

- No claim was rewritten upward to close the integration-stack gap. Zero additions attempting to make OAuth/SAML/SCIM/SIEM sound closer than it is.
- No people-management language was added to answer "lead and grow a team."
