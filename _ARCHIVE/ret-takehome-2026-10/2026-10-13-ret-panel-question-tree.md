# RET take-home: panel lines of reasoning (internal, not shipped)

Each line is a heading: where the panelist is driving. Every step reads "if your answer holds, the next question
follows". Rehearse the whole line, not single questions: the panel is testing whether your answers stay consistent as
they cascade. "Answer" is what is true in the build; "Lives in" is where to point. Tests in golden_wave3.json (X1-X10)
check the system side of these lines; X4 fails today on purpose (see the Doug line).

## Doug, heading: "Will this ever let an amendment slip past us again?"
1. Amendment Two arrives worded oddly. What happens?
   Answer: rules it can read are applied by code; wording it cannot read goes to the board as Needs review, never a guess.
2. If it goes to Needs review, who sees it, and how fast?
   Answer: it sits on the Key Facts board as Needs review; a push alert is a monday.com automation the free trial lacks (untested).
3. If nobody looks for two days, does the board still show the old deposit as current?
   Answer (VERIFIED 2026-10-12, test_unreadable_amendment_flags_the_fact_and_the_answer): no. The deposit row turns
   "Needs review" while still showing Amendment One's $100,000; the Solicitations board names "§A2.1 unresolved §7";
   anyone asking the deposit gets "needs review: a person must check the amendment". The gap: no push alert (free plan).
4. If the board is right, can I trust the deadline on the morning of submission? ("5:01 PM CT: are we on time?")
   Answer: §3.4: late is never accepted, the portal timestamp decides. The system's own test of this (X4) shows word search
   missed §3.4 when the question never says "late"; the figure check withheld the answer instead of guessing.
Lives in: K55, K17, D-NOTIFY, D-PLAN, X4.

## Doug, heading: "Does this cut my 650 hours or just move them?"
1. You skipped my tracker. Why?  Answer: to prove intake first; the tracker is board work, phase 2, first item.
2. If intake is proven, what does the tracker do on day one?  Answer: milestones from the clauses that name dates and owners; untested.
3. If clauses don't name owners, who fills them?  Answer: Doug's team, and the pilot measures how many rows they still type.
Lives in: D-NOTBUILT, slide 8.

## Nina, heading: "Can a wrong number ever reach our bid?"
1. Where does $100,000 come from?  Answer: §A1.2, word for word; the proof page traces it.
2. If you cite A1.2, what about the $75,000 still in §7.1?  Answer: both texts cited; the amendment governs and the answer says so (X5).
3. If both figures sit in cited clauses, how does a reader know which one is current?  Answer: the governing note names the amendment; code decides, not the model.
4. If the model paraphrases a figure, what stops it?  Answer: the figure check withholds the summary and shows the clauses (X4 is a live example).
Lives in: proof-of-one-answer, answer.py, slide 4.

## Nina, heading: "Where is the line on drafting?"
1. "Draft our executive summary."  Answer: refused (T4).
2. If that is refused, what about "two sentences for our cover letter"?  Answer: also refused (X6).
3. If it refuses, does the refusal leak anything?  Answer: it says it does not draft bid language; the attack tests cover leaks.
Lives in: T4, X6, wargame.

## Sam, heading: "What can leave, and who controls it?"
1. What leaves on one question?  Answer: fixed instructions, the question and a few clauses; logged in full.
2. If the question is itself strategy, why send it out?  Answer: you choose; the local model keeps the AI step on RET's machine (14 of 18 vs 18 of 18).
3. If we choose local, what do we lose?  Answer: accuracy on the hardest questions; a person reviews its answers before a bid.
4. If the token leaks, what can an attacker write?  Answer: only the four named boards (sink allowlist); the token is never logged.
Lives in: glossary.json, slide 5, provider.py, sink.py.

## Sam, heading: "What do we have to run after you leave?"
1. How many moving parts?  Answer: one Python folder, no installs, one poller on one machine.
2. If it runs on one machine, what about weekends and sleep?  Answer: questions wait until it wakes; one poller per computer, ./rfp status shows it (K61).
3. If two copies run, do answers double?  Answer: no; the second refuses, by lock.
Lives in: README "Run it for real", K61.

## Elena, heading: "Is this worth my budget, and how will I know?"
1. Why fund this?  Answer: RET's own target, 650 to 150 hours a cycle; my floor 200 hours, graded D.
2. If the floor is 200, which number goes in my plan?  Answer: neither yet; the pilot measures it on Maple Creek.
3. If it misses, what tells me to stop?  Answer: your three tests; miss them on your staff's questions and my premise was wrong.
4. If hours drop, does win rate move?  Answer: a hypothesis, not evidence: recovered time goes into fewer, better-qualified bids.
5. If we bid fewer, should we bid this one? (X10)  Answer: the system never gives a verdict; that is RET's call.
Lives in: slide 7, slide 8, README:157, DEMO two unprompted lines.

## The monday.com engineer, heading: "Did you use the platform well, and know its limits?"
1. Why polling, not webhooks?  Answer: a webhook needs a public endpoint into RET; polling costs about 60 calls an hour.
2. If you poll, how do you stay under 1,000 calls a day?  Answer: shared daily count, poller stops at 100 left (K61).
3. If state is local SQLite, what is the source of truth?  Answer: the RFP files; the boards are written idempotently from them.
4. If someone renames a column?  Answer: the sync finds columns by title; named in "not tested", fix is keying by id.
5. If you had enterprise, what changes?  Answer: monday.com's own models, one automation, API analytics; none tested (D-PLAN).
Lives in: README architecture, monday.py, D-SDK, D-MCP, D-PLAN.
