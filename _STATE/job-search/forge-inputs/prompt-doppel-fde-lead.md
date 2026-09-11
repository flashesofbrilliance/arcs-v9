You are running the LIGHT tier (stages 1, 5, 7, 8, 9) of the counterpart-application forge for ONE posting. Every input is pre-staged below. Do NOT fetch the JD, do NOT re-grade the record, do NOT explore the design system, do NOT call any API or database, do NOT take screenshots beyond the four widths named. Your job is the judgment residue only: the tailor mapping, the resume cut, the red-team, and the page copy.

## The posting
- jobid: 4450636067 · company: Doppel · title: Forward Deployed Engineering Lead
- posting URL: https://www.linkedin.com/jobs/view/4450636067/
- composite 0.694 · band CONSIDER · tier 3
- scorer assessment: 'The mandate is deliberately unfinished, and you'll define it' = high authority. AI is the product but the role's core is enterprise integrations (OAuth/SAML/SCIM/SIEM). No comp disclosed.
- dims (0-3 each): {"role_shape":3,"ai_native":2,"strength_leverage":2,"scope_authority":3,"culture":2,"comp_level":0,"logistics":2,"warm_path":0}
- gates: []
- JD text (already fetched, plain text): _STATE/job-search/forge-inputs/jd-4450636067.txt

## The record of record (Zach Harris)
- _STATE/job-search/forge-inputs/record-of-record.txt  — the ONLY source of claims. Every line in the cut must trace to it. Never invent a title, figure, employer, or date. Never claim "Forward Deployed Engineer" as a past title.

## Reference bundle (copy its SHAPE exactly)
- _ARTIFACTS/forge-citi-fde/  — read: TAILOR-NOTES.md, red-team.md, resume-citi-fde-ats.html, render.sh, page.html, kintsugi.json, cost.json, hiring-manager.json, contact.json. These are the format contract.
- Page base: public/blacksmith.html (the Blacksmith grammar). Not the compass-kit look, not the arcs.care main site.

## Rules (non-negotiable)
1. Resume is TWO pages at Letter, rendered from an HTML file like the reference. Headline under the name names the ARCHETYPE (e.g. "forward-deployed product and AI builder"), NEVER the req title.
2. Plain language. No em-dashes anywhere (use commas or periods). No scoring vocabulary (tier, band, composite, pursue) on page.html.
3. Air-gap: page.html carries no counterpart surnames, no hiring-manager names, no comp talk, no record-of-record link. Hiring manager in hiring-manager.json is explicit / implicit / unknown with evidence quoted from the JD; NEVER a guessed name.
4. Honest-grade every claim in TAILOR-NOTES (documented in record vs self-reported); red-team names the 3 claims most likely to be probed and the defend-or-drop call.
5. Output ONLY into _ARTIFACTS/forge-doppel-fde-lead/ : jd-full.txt (copy of the JD), TAILOR-NOTES.md, red-team.md, resume-doppel-fde-lead.html, resume-doppel-fde-lead.pdf (and -ats variants if you produce them), resume-doppel-fde-lead-page-1.png, resume-doppel-fde-lead-page-2.png, page.html, hiring-manager.json, contact.json, kintsugi.json, cost.json (est_tokens + your actual turn-count estimate), render.sh (adapted copy of the reference).
6. Four-width check of page.html (375, 768, 790, 1280) with Playwright from /Users/zharris/arcs-v9/node_modules exactly as the reference render.sh does; save as forge-shot-<w>.png. Fix any horizontal overflow. That is the only screenshotting.
7. Verify the PDF is exactly 2 pages (pdfinfo or the page PNG count) before you finish. If it is 1 or 3, fix the cut, do not report done.
8. Do not commit, push, deploy, or touch the database. Do not write outside the bundle folder.

Finish with a 6-line report: files written, page count verified, headline used, 3 red-team claims, est/actual tokens, anything you could not do.