You are running the LIGHT tier (stages 1, 5, 7, 8, 9) of the counterpart-application forge for ONE posting. Every input is pre-staged below. Do NOT fetch the JD, do NOT re-grade the record, do NOT explore the design system, do NOT call any API or database, do NOT take screenshots beyond the four widths named. Your job is the judgment residue only: the tailor mapping, the resume cut, the red-team, and the page copy.

## The posting
- jobid: 4441105462 · company: Basis · title: Member of Technical Staff - Atlas FDE
- posting URL: https://www.linkedin.com/jobs/view/4441105462/
- composite 0.944 · band PURSUE · tier 1
- scorer assessment: Exceptional: agents in production, FDE embed model, regulated (accounting), NYC 5d/week, strong culture. Comp not stated; weak warm path (Basis is known but no intro).
- dims (0-3 each): {"role_shape":3,"ai_native":3,"strength_leverage":3,"scope_authority":3,"culture":3,"comp_level":2,"logistics":3,"warm_path":1}
- gates: []
- JD text (already fetched, plain text): _STATE/job-search/forge-inputs/jd-4441105462.txt

## The record of record (Zach Harris)
- _STATE/job-search/forge-inputs/record-of-record.txt  — the ONLY source of claims. Every line traces to it. Never invent a title, figure, employer, or date. Never claim "Forward Deployed Engineer" as a past title.

## Reference bundle (copy its SHAPE exactly)
- _ARTIFACTS/forge-citi-fde/  — read: TAILOR-NOTES.md, red-team.md, resume-citi-fde-ats.html, render.sh, page.html, kintsugi.json, cost.json, hiring-manager.json, contact.json. These are the format contract.
- Page base: public/blacksmith.html (Blacksmith grammar). Not the compass-kit look, not the arcs.care main site.

## Rules (non-negotiable)
1. Resume is TWO pages at Letter, rendered from an HTML file like the reference. Headline under the name names the ARCHETYPE (e.g. "forward-deployed product and AI builder"), NEVER the req title.
2. Plain language. No em-dashes. No scoring vocabulary (tier, band, composite, pursue) on page.html.
3. Air-gap: page.html carries no counterpart surnames, no hiring-manager names, no comp talk, no record-of-record link. hiring-manager.json is explicit/implicit/unknown with evidence quoted from the JD; NEVER a guessed name.
4. Honest-grade every claim in TAILOR-NOTES (documented in record vs self-reported); red-team names the 3 claims most likely to be probed and the defend-or-drop call.
5. Output ONLY into _ARTIFACTS/forge-basis-atlas-fde/ : jd-full.txt, TAILOR-NOTES.md, red-team.md, resume-basis-atlas-fde.html, resume-basis-atlas-fde.pdf (+ -ats variants if produced), resume-basis-atlas-fde-page-1.png, resume-basis-atlas-fde-page-2.png, page.html, hiring-manager.json, contact.json, kintsugi.json, cost.json, render.sh.
6. Four-width check of page.html (375,768,790,1280) with Playwright from /Users/zharris/arcs-v9/node_modules exactly as the reference render.sh; save forge-shot-<w>.png. Fix any horizontal overflow.
7. Verify the PDF is EXACTLY 2 pages (pdfinfo) before finishing. If 1 or 3, fix the cut.
8. Do not commit, push, deploy, or touch the database. Do not write outside the bundle folder.

Finish with a 6-line report: files written, page count verified, headline used, 3 red-team claims, est/actual tokens, anything you could not do.