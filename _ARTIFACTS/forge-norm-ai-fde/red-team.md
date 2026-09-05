# Red-team · Norm Ai FDE cut · 2026-09-04

Adversarial pass over `resume-norm-ai-fde-ats.html`, run as a constitutional-court read: every sentence checked against `master-resume.txt` and `jd-ashby-fde.txt`. Subtractive fixes only; nothing was added. All fixes below are applied.

## Findings and fixes

| # | Finding | Severity | Fix applied |
|---|---|---|---|
| 1 | Thesis: "then teach their people to run it." JD wants enablement sessions; the record has no training or enablement work, only handoff. Reads as JD echo. | high (reference-check risk) | Removed. Thesis now ends "discovery through handoff." |
| 2 | Thesis: "Twenty years in regulated and high-consequence settings." The record's regulated work starts 2021 (Twill), then Axon 2023, Grayscale 2024. The twenty years are product/data, not regulated. | high | Rewritten: "Two decades building product, the recent years inside regulated, high-consequence settings". |
| 3 | Thesis: "translating a rule into working software was the job." Grayscale record: translated regulatory requirements into product and go-to-market requirements. Role was product lead, not the engineer writing the software. | medium | Softened to "into product requirements". |
| 4 | Thesis: "Built enterprise data layers ... three business units." Plural implies more than one org; record has one (CTF). | low | Singular: "Built an enterprise data layer". |
| 5 | ARCS bullet: "CI gates on every merge." Repo is private; "every merge" is a stronger claim than anyone can check. | low | "CI gates before deploy." |
| 6 | Fit table: label column overlapped values at print width ("CUSTOMER DATA → MODEL" collided with the value text). Caught on the rendered PNG, not in the HTML. | render | Fixed column to `flex:0 0 96px` and shortened labels ("Data → model", "Rule → product"). Re-rendered and re-inspected. |
| 7 | JD terms FastAPI, Dagster, Airflow, "4+ years Python" absent from the cut. Confirmed absent; an ATS keyword pass might tempt adding them. | guard | Left absent. Recorded in defend-or-drop. |
| 8 | "60% reduction in decision noise" is a self-metric on the candidate's own product. | medium | Kept, but labeled "(self-reported)" inline on the résumé and "internal measurement" in the sentence. Not in the thesis, not in the fit table. |
| 9 | Tagline "Forward-Deployed Builder" could read as a held title. | low | Kept: it sits under the name as a descriptor, and every actual title is listed with dates. No job entry is titled FDE. |
| 10 | Master résumé lists Section4 and RBAC claims in sibling cuts; none of it is on the master. | guard | Not inherited. |

## What survived unchanged
Squat NY figures, Grayscale $7B / 10 products, CTF 20%, WTA <120ms / $850K+, consulting summaries, education: all verbatim or tighter than the master.

## Residual risk
- Every dollar figure except Grayscale AUM is self-reported. This is the same exposure as the master résumé, not new exposure.
- The résumé does not cover Python at production depth. That is a real gap versus the JD and is left visible rather than papered over.
