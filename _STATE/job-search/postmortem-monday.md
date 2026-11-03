# Post-mortem: monday.com FDE, Strategic Deployments

2026-11-03. Sibling of `postmortem-fanatics.md`. Sources: Gmail (Sam Turner threads), `_ARTIFACTS/forge-monday-fde/`,
`_STATE/job-search/forge-cost-ledger.jsonl`, `hypothesis-ledger.md`, the 2026-10-26 recoil close, memory
`project_monday_fde_strategic_deployments`.

## Outcome

Closed, rejected. Sam Turner, 2026-11-02 10:36 ET ("Update from monday.com", still unread at the time of writing):
"decided to move forward with other candidates", "a number of positive takeaways", "extremely competitive
process, especially now with the very high volume of applicants". No reason beyond that.

## Timeline

| Date | Event | Who ran it |
|---|---|---|
| ~2026-09-05 | Posting enters jobs.arcs.care from a LinkedIn alert digest, scored, right-swiped | Scheduled loop + Zach (swipe) |
| 2026-09-06 | Forge-light: resume cut + page, 190k tokens, Sonnet. A sister posting (Deployment Architect) forged the same day | Forge |
| ~09-06 to 09-10 | Cold application sent (warm_path 0) | Zach |
| 10-02 | Sam books the recruiter screen ("excited to move forward with your application") | monday |
| 10-07 / 10-08 | Recruiter screen; hiring manager Stefan Karadzic | Zach |
| 10-14 | Take-home rc46 submitted | Zach + many sessions |
| 10-26 | Panel walkthrough; follow-up note + video + monday.arcs.care sent that evening | Zach + sessions |
| 11-02 | Rejection | monday |

Elapsed: about 26 days from application to first human reply, 8 weeks to close.

## What got the screen (the part worth reproducing)

1. **Role shape, not polish.** FDE title, the JD named MCP and agentic tooling, NYC hybrid. Each JD hook was mapped
   to something that runs (the ARCS MCP server). The scorer's own flag was the MCP hit
   (`_ARTIFACTS/forge-monday-fde/TAILOR-NOTES.md`, section 1).
2. **An honest cut.** Archetype headline, never a held "FDE" title, gaps (SCIM/SAML, cloud deploy, n8n) left open
   instead of invented (`TAILOR-NOTES.md`).
3. **A real req.** Posted JD, recruiter-run Ashby loop: req_reality 2 or better from day one. Contrast Fanatics
   (no req, no conversion; `_STATE/job-search/postmortem-fanatics.md`).
4. **Cheap per shot.** One forge-light run per posting, inputs pre-staged (190,306 tokens,
   `_STATE/job-search/forge-cost-ledger.jsonl`, 2026-09-06 `monday-fde`).

Control: the Deployment Architect posting at the same company got the same forge and was rejected without a screen.
So the resume and page alone did not do it; the role-shape match did (`hypothesis-ledger.md`, monday.com Deployment Architect resolved rejected). Base rate: of roughly 30+ cold applications
tracked by mid-September, this was the first human response. n = 1. Treat the recipe as a hypothesis, not a law.

## What lost it (the part worth not repeating)

From the recoil close, verdict FORK/YELLOW, about 0.55 at the time:
- Opened with the bench, not the deck; Jacob redirected at 11:45.
- No code walk, even when Kamran asked for the guardrail code.
- Number slips in front of an eval-minded panel ($0.76 per cycle said as per question; eval attribution).
- Prepared PII and retrieval-at-scale answers went unused.
- Prep built more than it rehearsed: a 134-file catalog and 28 question chains, while the six beats were never said
  out loud on a timer (that check was still open on 10-22).

What landed: "incredibly meticulous", the eval-change answer, the policy/RAG answer. The applicant pool was large;
do not assume the walkthrough alone decided it.

## The cost

Eight weeks, dozens of sessions, a take-home that grew past "a modest build that proves you listened" (R31), a
guide site, two videos. The drain today is part of the bill. A look-alike loop has to cap that spend per stage.

## The recipe: look-alike mondays on cruise control

**Signature to filter for** (all four):
1. FDE, solutions, or deployment-engineer shaped title.
2. The JD names a tool Zach runs today: MCP, Claude, agents, LLM evals.
3. Posted JD with a recruiter-run loop (req_reality 2+).
4. NYC metro or remote.

**What already runs** (checked 2026-11-03):
- `arcs-job-search-loop-retargeted-alerts`, weekdays 7:30: alerts + public boards + Fonzi into jobs.arcs.care,
  score, cheap forges. Last run 2026-11-02 evening; this morning's run does not appear to have fired.
- `daily-reps-picklist`, weekdays 8:00: picks 2 jobs + 2 pitch targets + 1 post into an Apple Note. Enabled; no
  run recorded yet, first fire 2026-11-04.

**Zach's part, about 15 minutes a weekday:**
1. Open the daily-reps note (or jobs.arcs.care sorted by fit, Applied AI / FDE tag).
2. Right-swipe only rows that match all four signature points.
3. Use `_ARTIFACTS/forge-monday-fde/` as the seed for edit-from-seed cuts: it is the only cut with a screen on its
   record.
4. Send. Two a day is the floor the reps task already sets.

**Stage caps when a screen lands:**
- Take-home: time-box to the brief's own scope; ship the modest build.
- Walkthrough: freeze 48 hours before, then rehearse only. Deck first, one code walk drilled, numbers read from a
  card. No new artifacts after the freeze.

## Open

- Record the close: backlog rows `monday-walkthrough-2026-10-26` (RUNNING) and the HOLDING leadership, final and
  offer rows should move to a closed state; a receipt row with the outcome.
- Ask Sam for one line of feedback (optional; draft only, Zach sends).
