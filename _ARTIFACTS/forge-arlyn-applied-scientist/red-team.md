# red-team · Arlyn AI Applied Scientist bundle (stage 7, subtractive only)

Pass run 2026-09-06 on `resume-arlyn-applied-scientist-ats.html` and `page.html`, reading as a skeptical hiring panel (an Applied Scientist / ML lead at a stealth AI startup) plus a background-check vendor. Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Top 3 claims most likely to be probed

1. **"Applied Scientist" framing gap.** The posting's title implies research-adjacent rigor (its own PhD-or-5-years-quant framing); the record shows a generalist product/GTM/data builder, not a research scientist with a publication or model-training record. Defend-or-drop call: **defend, narrowly.** The resume never claims the title or research credentials; the headline is "Agentic AI builder, prototype to production," and the pillars lead with the ARCS build (MCP server, agentic orchestration, in production) as the closest honest match to "applied," not "scientist." If pressed on model training or research methodology specifically: none claimed, none invented.

2. **No biotech/life-science domain experience.** The posting is explicitly a life-science commercial-intelligence company (drug launch, patient access, pharma). The record's closest domain adjacency is Twill Health (HIPAA digital health, not pharma commercial) and Children's Tumor Foundation (a medical research nonprofit's data/CRM layer, not drug-launch strategy). Defend-or-drop call: **defend by stating the gap plainly**, not by stretching Twill or CTF into something they are not. TAILOR-NOTES and page.html both name this as an open gap.

3. **"Founder-facing" pillar risks reading as more embedded-with-founders experience than the record supports.** The strongest literal support is ARCS itself (Zach is the founder), which is circular if read uncharitably. Defend-or-drop call: **defend with the circularity named up front.** The pillar text says "operate the full stack at ARCS as a single founder" first, then separately credits the five embedded engagements for executive-level (not founder-level, except where the client was founder-led, e.g. Axon's incubation) stakeholder work. Not claiming direct reports-to-founder history at an outside company beyond what the record shows.

## Other hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 4 | "Prompt engineering" added to the skills line is not a separate line item in the record's SKILLS list. | True, but a reasonable inference from the documented MCP/agentic-orchestration build (you cannot build that pipeline without it). | Kept, graded self-reported in TAILOR-NOTES; on the defend-or-drop list. Would narrow to "agentic pipeline design" if challenged on the specific term. |
| 5 | "Unstructured data into structured decisions" pillar uses the word "ontologies" nowhere, while the JD specifically asks for "data ontologies." | Deliberate. The record does not use ontology language or claim ontology tooling. | Kept the softer "evidence taxonomy and gating architecture" phrasing rather than echoing "ontology," to avoid implying tooling that was never built. |
| 6 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP, distributed query systems; none are on the record's skills list. | True, but consistent with the CTF/WTA data-layer roles (same posture as the Citi bundle). | Kept on the resume; graded self-reported in TAILOR-NOTES; each is on the defend-or-drop list. |
| 7 | "$7B AUM" could read as personal scope rather than the product suite's AUM. | Partly true. | Resume already binds it to the product suite ("$7B AUM" directly after "10 SEC/FINRA-regulated ... products"). No change needed. |
| 8 | Posting explicitly wants PhD-in-quant-field OR 5+ years in finance/biotech/tech; the record shows neither a PhD nor biotech, but does show finance (Grayscale) and tech startup (ARCS). | True; the "5+ years, finance or tech startups" branch is honestly satisfiable, the PhD and biotech branches are not. | page.html and TAILOR-NOTES state this branch-by-branch rather than implying blanket qualification. |
| 9 | "Twenty years" arithmetic from 2006 graduation. | Correct (2006 to 2026). | No change. |
| 10 | Air-gap check: page.html and this bundle name no other counterpart, no hiring-manager name, no comp figures, no record-of-record link. | Verified by grep (see below). | No change needed. |

## Air-gap grep audit

Checked `page.html` for: comp figures ("$175", "$255", "255,000"), the words "tier", "band", "composite", "pursue", any other company's bundle name (citi, forge-citi), and a hiring-manager name. All zero hits. See verification note in kintsugi.json.

## Not touched, on purpose

- No claim was rewritten upward. Removals only where the panel's hit was true (none required a resume text change this pass; two of the three top claims were already stated honestly on first draft and needed no rewrite, only confirmation).
- The record's "platform load simulation and reliability engineering" bullet for WTA was left off the two-page cut for space, not because it failed the evidence bar; it is still traceable to the record if the page needs to expand.
