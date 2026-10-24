# RET take-home: enterprise access test plan (internal, not shipped)

Ground rule: the submission stays rc25, built and measured on the free trial account the brief asks for.
Enterprise work happens in a copy, against new boards in the enterprise workspace, with its own token
(`MONDAY_API_TOKEN_ENT` in the copy's .env). It becomes, at most, one interview beat and one README line.

## The idea: subtract, don't add
Keep what is ours and defensible: amendment rules, the word-for-word figure check, citations, refusals.
Hand monday.com only what it does better than our code. Four swaps, each one switch or one setting:

| Today (free plan) | With enterprise | Who it helps | Change |
|---|---|---|---|
| Answers via Claude | monday.com's own models (`--provider monday`, already in the code; 403 on free) | Sam: no new AI vendor to review | one flag |
| Amendment notice dropped (no automations) | Automation: Key Facts row changes, notify Doug | Doug: the November 13 incident can't repeat silently | one automation, no code |
| API cost visible only in our log | monday.com API analytics | Elena, Sam: usage visible in the product | none; open the page |
| Questions typed as board items | unchanged | everyone | keep the board; it already works |

Not doing: AI columns or Sidekick answering RFP questions (they would skip the figure check: Nina's
non-negotiable), Vibe app, agent workforce, notetaker. Name them in Q&A as deliberate choices.

## Part A: technical testing (CLI)
1. `./rfp doctor` with the enterprise token: plan reads enterprise; calls-left line still sane.
2. `./rfp sync` into the enterprise workspace twice: second run creates nothing.
3. `./rfp ask --provider monday "When are proposals due?"`: December 4, cites §A1.1; payload logged.
4. Eval set on `--provider monday`: 18 questions; record the score next to Claude's 18/18, whatever it is.
5. Traps on `--provider monday`: union labor = not addressed; "draft our executive summary" = refused.
6. Fault: bad enterprise token, then rate limit: falls back or says "AI unavailable", poller survives.
Pass: 1-3, 5, 6 all pass; 4 recorded honestly (a lower score is a finding, not a failure).

## Part B: non-technical testing (in monday.com, no terminal)
1. Ask on RET · Questions as a colleague would; answer and citation appear within a minute.
2. Edit the deadline row on Key Facts: Doug's notification arrives (the automation).
3. Ask the two awkward questions on the board; same outcomes as the CLI.
4. Open API analytics: today's calls are visible.
5. A second person (anyone) repeats 1 and 3 without help, timed.
Pass: 1-4 work; the second person needs no explanation.

## Gates before any of it touches the submission
Zach decides. Default: nothing changes in rc25; the README gains one line only if Part A step 3 passed.
