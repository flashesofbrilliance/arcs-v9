# red-team · monday.com FDE bundle (stage 7, subtractive only)

Pass run 2026-09-06 on `resume-monday-fde.html` and `page.html`, reading as a skeptical hiring panel
and a technical screener. Rule: a hit only changes a word if it is true against the evidence, and the
only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | "3+ years of experience as a forward deployed engineer, software engineer, or technical consultant" is a required qualification; the candidate never held any of those three titles. | True. | Headline stays the archetype, never the title. Page states the gap in plain words in the mapping note. No resume change (title was never claimed). |
| 2 | The new "TypeScript and JavaScript, Next.js" skill line is not in the record of record's own SKILLS array; it is inferred from the public GitHub repo, not from anything Zach wrote in the record. | True, and it is the single highest-risk new claim this pass. | Narrowed the phrasing to name the repo directly ("ARCS platform, public repo") so the claim points at checkable evidence rather than asserting general fluency; graded "documented (public, checkable)" not "self-reported" in TAILOR-NOTES; kept on the defend-or-drop list with the honest answer that depth in React vs. Node specifically is not separately claimed. |
| 3 | "Fluency in Generative and Agentic AI development... with AI-assisted editors such as Cursor or Claude Code in daily use", the resume does not name a specific editor. | True, and correct as-is. | No change: naming a specific tool without a checkable trace would be an overclaim; the agentic-pipeline and MCP claims already carry the substance. |
| 4 | SCIM, SAML 2.0/OAuth 2.0, GraphQL, n8n/Workato, AWS/GCP/Azure are all named in the JD requirements and none appear on the resume. | True. | Confirmed absent from the page (grep clean); listed as open gaps in TAILOR-NOTES rather than papered over. |
| 5 | "$7B AUM" can read as personal scope rather than the firm's regulated product suite. | Partly true. | Resume binds it to "10 SEC/FINRA-regulated ... products" immediately before the figure; page.html's claims ledger row for this figure adds "the firm's public figure for the period, not a personal P&L." No inflation left in either surface. |
| 6 | "Two decades" | Arithmetic from 2006 graduation: 20 years as of 2026. | No change. |
| 7 | Air-gap: does the page or resume name any monday.com employee, hiring manager, or comp figure? | Checked: no. `hiring-manager.json` records "unknown" with JD-quoted evidence only; no name anywhere. Comp ($140-160K) is not printed on any bundle file except this red-team note and TAILOR-NOTES, both internal. | No change needed. |
| 8 | Does the resume claim the literal title "Forward Deployed Engineer" anywhere as a past role? | Checked via grep across resume-monday-fde.html and page.html for the exact phrase outside the "Target" line and page `<title>`. | Clean; only appears in the labeled target/title contexts. |

## Not touched, on purpose

- No claim was rewritten upward. One narrowing this pass (hit #2), consistent with the citi-fde
  precedent of "only removal or narrowing."
- The comp gap ($140-160K vs. target, per the scorer's own comp_level:1 dim) is not addressed anywhere
  on the candidate-facing bundle; comp is not resume or landing-page content per the forge blueprint.
