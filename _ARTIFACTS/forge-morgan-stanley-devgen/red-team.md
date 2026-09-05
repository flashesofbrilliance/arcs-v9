# Red-team: Morgan Stanley DevGen.AI bundle (subtractive fixes only)

Pass run 2026-09-04 against the resume HTML, ATS text, and public/forge-morgan-stanley-devgen.html, reading as the hiring panel and as a background-check vendor.

| # | Hit | True? | Fix applied |
|---|---|---|---|
| 1 | Headline under the name echoes the req title ("Lead Product Engineer · AI Development Platforms"). Reads as keyword stuffing. | Yes | Rewritten to a positioning line naming the archetype. Title tag keeps the role. |
| 2 | Softest numbers on the page (60%, 3 to 5x) sit in the first bullet, self-measured on the candidate's own platform. | Yes | Figures removed; bullet now states the mechanism (evidence taxonomy, confidence state, lineage). Moved to defend-or-drop. |
| 3 | One-page cut dropped the open-source tools and the advisory work, which are the strongest InnerSource / reuse evidence for this specific JD. | Yes | Restored to two pages; Open Source and Advisory sections added from the record of record. |
| 4 | Any RAG or vector-search claim to match the JD keyword? | Checked; none present | No change. Kept "context management" only. Noted on the defend-or-drop list. |
| 5 | Any cloud AI gateway (Azure OpenAI, Bedrock, Vertex) claim? | None present | No change. |
| 6 | "Led engineering teams" language? | Not present; "cross-functional delivery" and "sole technology partner" only | No change. |
| 7 | Education: second MIT certificate or Section4 credential? | Not present | No change. |
| 8 | ATS text had letter-spaced uppercase from pdftotext ("E XEC U TIV E") and "in/ zharris" spacing. | Yes | Regenerated from HTML with a tag-strip; spacing fixed. |
| 9 | Forge page ticker said "Three were cut" while the cut list had four entries. | Yes | Changed to "Four". |
| 10 | Forge page CSS comment named another company's surface. | Yes | Comment reworded; grep for company names other than the target returns zero. |
| 11 | Air-gap: counterpart surnames, recruiter names, internal scoring words (PURSUE, composite, rubric, tier, Y-gate), other target companies on the public page? | Grep clean | No change. |
| 12 | Em-dashes or en-dashes anywhere in the bundle? | Grep clean on resume HTML, ATS text, forge page | No change. |
| 13 | Forge page at 790 px: third pillar and sixth stage orphaned on their own row. | Yes | auto-fit minimums tightened (200px pillars, 112px stages); re-verified at 1280 / 790 / 768 / 375, zero horizontal overflow. |

Nothing was added to make a claim stronger. Every change above removes, corrects, or restores from the record.
