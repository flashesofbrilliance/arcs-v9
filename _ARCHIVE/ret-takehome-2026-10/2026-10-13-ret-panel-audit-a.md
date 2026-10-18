# RET take-home: panel audit, option A (internal, not shipped)

Run 2026-10-12 evening against rc27. Method: deterministic digest (25 requirements from the brief and Sam's email,
10 slides, cited excerpts; ~8k tokens), one Sonnet pass in five panel seats plus a scope skeptic (161k tokens),
Fable synthesis (122k tokens, separate allowance). Claims spot-checked by the orchestrating session.

## Verified by the orchestrator
- presentation/deck.html.orig ships in the ZIP: committed by mistake in c282745 (present-mode flip patch).
- ZIP is 9.62 MB, under the cap (the panel pass's size worry was wrong: it measured 14 MB unzipped).
- "Needs review" is a real board state (live_questions.py:22, :47; README:14), so a review queue exists as a board filter.
- create_update posts the cited answer on every answered item (rfp/sink.py:124).

## Verdict (Fable)
The build has cleared the brief's bar; spend the remaining time on rehearsal and spoken framing, not code.

## Do
1. Value story in RET's units: their target 650 to <=150 h a cycle; slide 7's >=200 h is a D-graded floor; the pilot measures which is right.
2. Amendment beat: the item update shows old and new text; a proactive alert is an automation the free trial lacks; untested.
3. Three cold, timed demo runs with someone else asking the fresh question; keep to the five files.
4. One sentence on Elena's win-rate mandate: hours are the lead indicator; recovered time goes into fewer, better-qualified bids.
5. Remove deck.html.orig (needs Zach's yes: file deletion).

## Don't
Build a notifier; restore Doug's tracker; edit slides 7 or 10 (PDF re-render, ~1 MB of the 0.38 MB headroom);
strip the mistakes log or build diary (AI-use evidence the brief asks for); add code for monday-native AI or polling math.

## Stop saying
3,072 simulated faults, the letter grades, the $86K expansion ARR, the flight recorder and the harness.

## Hard questions with answers
See the session transcript; Q4's "human review queue" means items marked "Needs review" on the Questions board.
