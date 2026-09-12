# red-team · Aircall · Director, Forward Deployed Engineering & AI GTM

Adversarial pass, 2026-09-04. Subtractive fixes only. Every hit was checked against the record of record (`public/resume.html`, served at resume.arcs.care) before a word changed.

## Hits that changed the resume

| # | Objection | Check | Fix applied |
|---|---|---|---|
| 1 | "Built the first intelligence layer at three organizations that had none." Which three? | Record names WTA ("first fan behavior intelligence layer") and CTF ("first intelligence layer any of these teams had"). No third. | Rewritten to "Built the first intelligence layer, twice, for organizations that had none." Re-rendered; still two pages, no orphans. |

## Hits checked and left as-is (each traces verbatim to the record)

| Objection | Where it traces |
|---|---|
| "Extended thinking" in Skills looks like padding | Master resume: "ARCS runs Claude (API, tool use, extended thinking), a custom MCP server, and agentic pipelines". Kept. |
| "Ran platform load simulation ... ahead of the Finals" | Master: "Platform load simulation and reliability engineering ahead of Women's Finals". Kept. |
| "made time-to-interaction the primary conversion KPI" | Master: "accelerated time-to-interaction as primary conversion KPI". Kept. |
| "self-updating models recalibrate scoring weights" | Master, verbatim. Kept. |
| Twill "two of three" | Master: "KPI frameworks informed go-forward decisions on 2 of 3". Kept. |
| Summary is long for a director cut | Five sentences, each a graded claim; the two-hires line is the argument. Kept. |

## Hits that are gaps, not overclaims (nothing to cut, flagged in TAILOR-NOTES defend-or-drop)

- No people-management claim against a 6-to-20 team-scaling mandate.
- No conversational AI or voice agent claim.
- No overlay-GTM claim.
- No help desk integration claim.

The resume does not pretend to any of these. The page mentions none of them. The gap is named before the interviewer names it.

## Landing page (public/forge-aircall-fde.html) air-gap sweep

- No counterpart surnames, no recruiter names, no internal scoring words, no other target companies. Verified by grep before finishing (see kintsugi.json).
- Employer names on the page (Grayscale, Squat New York, Children's Tumor Foundation, WTA) are the candidate's own record and appear on the resume itself.
- No time-to-ship claim on the page (nothing like the "1h 22m" clock), because no git-true measurement exists for this bundle.
