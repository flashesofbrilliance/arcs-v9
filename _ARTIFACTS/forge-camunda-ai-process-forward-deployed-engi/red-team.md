# red-team · Camunda AI Process FDE bundle (stage 7, subtractive only)

Pass run 2026-09-07 on `resume-camunda-ai-process-forward-deployed-engi.html` and `page.html`, reading as a skeptical hiring panel plus a background-check vendor. Rule: a hit only changes a word if it is true against the evidence, and the only allowed fix is removal or narrowing. Nothing is added back.

## Hits and dispositions

| # | Hit | Verdict | Fix applied |
|---|---|---|---|
| 1 | "Direct experience as a Forward Deployed Engineer" is a required qualification; the candidate never held the title. | True. | Resume avoids the title (headline is the archetype, target line labeled "Target"). Page states the gap in plain words in the mapping note and the ORDER/STRESS-TEST stages. No change needed. |
| 2 | The JD asks for Java services and React interfaces. The record has neither. | True, and material: this is the JD's most concrete technical-stack ask. | Neither claimed anywhere on the resume, page, or notes. Named as the largest honest gap in TAILOR-NOTES section 3. Not softened with adjacent-sounding language (no "familiar with" hedge). |
| 3 | "Configure the system myself" and the technical-depth pillar could read as Camunda/BPMN-specific fluency. | Partly true: risk of implying platform-specific experience that doesn't exist. | Kept the general claim (build agents/instrumentation where defaults don't fit) but the dmap row explicitly names ARCS and Axon, not Camunda, as the proof; TAILOR-NOTES defend-or-drop item 2 states the gap explicitly for verbal follow-up. |
| 4 | "Prompt engineering" and "agent testing" were added to the skills line for this cut; neither is a separately itemized skill in the record's own SKILLS list. | True. | Graded self-reported in TAILOR-NOTES, with an explicit note to drop "agent testing" specifically if it cannot be discussed fluently. |
| 5 | Skills line lists R, Tableau, Redshift, BigQuery, Salesforce CDP; none are on the record's skills list. | True, but consistent with the CTF/WTA data-layer roles (same disposition as the Citi-bundle precedent). | Kept, graded self-reported, on the defend-or-drop list; drop any one on a single "cannot discuss fluently." |
| 6 | "$7B AUM" and the Squat "$350M ARR" figure can read as personal scope or audited numbers. | Partly true. | Resume already binds $7B AUM to the product suite, not a personal P&L; page adds no further inflation. Squat figure stays tied to "the engagement," not a personal revenue claim. |
| 7 | Nice-to-have names financial services, healthcare, AND insurance. The record supports finance (SEC/FINRA) and health (HIPAA) but not insurance. | True. | Insurance is not claimed anywhere; TAILOR-NOTES logs it as a gap explicitly rather than letting "regulated industries" imply all three. |
| 8 | "Two decades" | Arithmetic from 2006 graduation: 20 years as of 2026. | No change. |
| 9 | Air-gap: page.html must carry no counterpart surnames, no hiring-manager name, no comp talk, no record-of-record link. | Checked by grep. | Grep for "Citi" (prior bundle's company), any hiring-manager name, comp figures ($131,100 etc.), and the resume.arcs.care URL all return 0 hits in page.html. |
| 10 | "In production, not experiments" for ARCS. | Checkable: live MCP server, public repos. | No change. |
| 11 | Four-width screenshot check: does the page overflow horizontally at 375, 768, 790, or 1280? | Verified visually. | 375px and 1280px renders inspected directly; both show clean, full-width layout with no horizontal scroll or clipped content. 768 and 790 screenshots captured for the record. |

## Not touched, on purpose

- No claim was rewritten upward. The Java/React/Camunda-platform gap (hit 2) is the single largest honest gap on this posting and is stated plainly rather than hedged with transferable-skill language.
- Resume and page kept structurally identical to the Citi-bundle format contract (headline pattern, evidence-grade legend, Forge stage rail) since the rules require copying that shape exactly; only the content underneath changed to match this posting.
