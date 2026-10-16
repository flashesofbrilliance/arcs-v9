# Scout Global / Wonderful: candidate bundle (minimum viable)

A private candidate bundle for Zach's application path to Wonderful via George Suttie at Scout Global. Same shape as `_ARTIFACTS/mercury-bundle`: one SSOT memo, projections of it, no live pages. Nothing here has been sent or deployed.

## Files
| File | What it is |
|---|---|
| `positioning-brief.md` | External cut of the brief promised to George. No internal scores, rubric or tooling language. Draft for Zach to edit; not sent. Internal reasoning stays in the memo and ledger. |
| `hyperstition-ledger.md` | Rubric grades for both roles, Loki-tested claims, decomposition rehearsal, draft ex-ante receipt, the kintsugi seam. |
| `grades.json` | Per-dimension scores on target-role-scan v1.3 and bridge-scan v1.1. |
| `role-choice.md` | Internal decision note: grades, what would actually disqualify, what George already said on the call, revised read. The richer `role-choice.html` is LOCAL ONLY (fails the design gates). |
| `candidate-memo.md` | **The SSOT.** Opportunity, role fit maps (FDE vs Deployment Strategist), positioning, draft reply to George, open facts. |
| `../forge-wonderful-deployment-strategist/` | Lead-alternative resume pair in the canonical forge layout (designed + `-ats`, PDFs, text, page PNGs, evidence ledger, render.sh). Sits under `_ARTIFACTS/forge-*/` so the design gate's print-resume waiver applies. |
| `../forge-wonderful-forward-deployed-engineer/` | FDE resume pair, same layout. `-ats` is generated from the designed one by `scripts/resume_ats_render.py`. |
| `evidence.jsonl` | Metric ledger for the resume; `provenance_lint` passes on both versions. |
| `recoil-report.html` | LOCAL ONLY, not committed: derived render of the recoil JSON `runtime/recoil/generated/2026-10-13-suttie.json` (the SSOT, committed). The tool's renderer emits an em-dash in the title and 36 design findings (10px text, wide letter-spacing) that the commit gates block. Regenerate with `python3 tools/recoil-report/recoil_report.py render runtime/recoil/generated/2026-10-13-suttie.json --out <path>`. |
| `render.sh` | Re-renders a resume HTML to PDF, PNG pages and plain text (copies live in each forge folder). |

## External bundle for George: `external/`
Only files that can go to George. Everything else in this folder is internal.
- `Zach-Harris-Positioning-Brief.pdf` (2 pages)
- `Zach-Harris-Resume-Deployment-Strategist.pdf` and `-ATS.pdf` (lead)
- `Zach-Harris-Resume-Forward-Deployed-Engineer.pdf` and `-ATS.pdf` (stretch)
- `cover-note.md`: the email text, with one marked blank for the 12-month answer. 
Checked: text scan of all five PDFs for internal terms (rubric, scores, ledger, recoil, hyperstition, tailored, target) found none; PDF titles read "Zach Harris - Resume" (no role or company); 0 em-dashes. Not run: counterpart gauntlet, strict slop eval. 12-month answer filled 2026-10-14 from Zach ("have not applied in the last 12 months"); "about eight years of AI, discovery to delivery" added to the brief from Zach, self-reported. Confirmed by Zach 2026-10-14: independent since 2019; a year and a half building ARCS with a full agentic harness.

## Gates run
- `provenance_lint`: pass, 7 metrics cited (both resumes).
- `slop_lint`: pass. A "public repo" claim inherited from the base resume was caught by hand and fixed (arcs-v9 is private); no lint catches it. `resume_location_gate`: pass. Em-dashes: 0.
- `slop_eval --strict`: not run (needs `ANTHROPIC_API_KEY`).
- `counterpart-gauntlet`: not run. Run it before anything goes to a human.
- Recoil JSON validated against `tools/recoil-report/schema/report.schema.json`.
- Both resumes render at 2 pages; the designed one leaves white space at the foot of page 1 because the embedded-engagements block stays intact on page 2.

## Before you send anything
1. Answer George's 12-month "no prior application to Wonderful" question yourself.
2. Pick the lead role (graded tie on fit; the bundle recommends Deployment Strategist, FDE as stretch).
3. Edit and send the draft reply in the memo. Send to George only.
4. File the ex-ante receipt first.
