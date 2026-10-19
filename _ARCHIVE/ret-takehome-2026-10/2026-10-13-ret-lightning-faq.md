# RET take-home: lightning-round FAQ, model answers with sources (internal, not shipped)

Each answer is retrieved from the build, not remembered: the "Source" line is where it was checked on 2026-10-12.
Two sentences, under 20 seconds. Answer first, then one beat: the mechanism, the number or the "because".

## Doug (operations, amendments)
1. **Will it catch the next amendment?** Drop the file in data/ and the next sync reads it, no code change; rules apply
   what they can read, and anything they cannot is flagged Needs review on the fact, never guessed.
   Source: K55, test_unreadable_amendment_flags_the_fact_and_the_answer, sync_boards.py:110.
2. **Who gets told?** Today nobody is pushed an alert: the free trial has no automations. The fact turns Needs review
   and every answer about it says a person must check; the alert is the first enterprise automation, untested.
   Source: D-NOTIFY, D-PLAN.
3. **Upload the same RFP twice?** Nothing new is created: items are written by their own Key, so a re-run updates in
   place. A live sync tonight: 16 unchanged, 0 created. Source: sink.py upsert, README:81.
4. **Where's my tracker?** Phase 2, first item: phase 1 proves intake hours first. Source: D-NOTBUILT, slide 8.

## Nina (compliance, citations)
1. **Where does a figure come from?** Word for word from a cited clause, or the answer is withheld and the clauses are
   shown instead. Source: answer.py figure check, proof-of-one-answer.
2. **How accurate is it?** 18 of 18 on RET's sample questions and traps; blind sets 16 and 17 of 20 before fixes;
   one known borderline case flips about 1 run in 10. Source: slide 6, evidence/blind, K62.
3. **Will it draft for us?** No: it refuses bid language in any form, including "two sentences for the cover letter".
   Source: T4, X6.
4. **What about the old $75,000?** Given only with the amendment that replaced it, both clauses cited.
   Source: X5 (passes).
5. **Disclaimers and carve-outs?** Answers keep their conditions (force majeure, negligence-only indemnity, the ISO's
   "no representation"), and the README states the system's own limits in one section. Source: X11-X13, README
   "Limits and disclaimers".

## Sam Ito (security, data)
1. **What leaves?** Fixed instructions, the question and a few clauses, about 3,400 characters, every call logged in
   full. Source: slide 5, glossary.json what_leaves, flightlog/model_calls.jsonl.
2. **Can nothing leave?** Yes: the local model keeps the AI step on RET's machine; it scored 14 of 18 in one run, and its
   misses were "not addressed" where the RFP does answer, including prohibited ISO contact, so a person reviews it.
   Source: E-local-eval, eval_runs (local, 2026-10-10).
3. **What does a leaked token allow?** Writing only the four named boards; the token is never printed or logged.
   Source: sink.py ALLOWED_BOARDS, monday.py header.
4. **What do we run?** One Python folder, no installs, one poller per computer; ./rfp status shows it.
   Source: README "Run it for real", K61.

## Elena Marsh (sponsor, value)
1. **Why fund it?** Phase one proves same-day facts and cited answers in minutes, for under a dollar of AI a cycle,
   judged by your three tests. Source: slide 1, slide 7 ($0.74 a cycle).
2. **How many hours?** Your target is 650 to 150 a cycle; my floor is 200 saved, graded D at 50% confidence; the pilot
   measures it. Source: README:157, slide 7.
3. **What would make you stop?** Missing your three tests on your staff's own questions. Source: slide 1, slide 8.
4. **Win rate?** A hypothesis, not evidence: recovered time goes into fewer, better-qualified bids. Source: none built;
   say so.

## monday.com engineer (platform)
1. **Why polling?** A webhook needs a public endpoint into RET; all-day polling is 1,440 calls, over 1,000, so it stops
   when idle and keeps 100 in reserve. Source: README not-tested table, K61.
2. **Source of truth?** The RFP files: the database is a rebuildable cache and the boards are the view.
   Source: sync_boards.load, README architecture.
3. **Column renamed?** Found by recorded id, so harmless; a deleted column stops the sync before writing. Source: K65.
4. **Over budget?** Paced below 100,000 points, retried on the server's wait, and a failed run re-runs safely because
   writes are keyed. Source: monday.py gql.
5. **Enterprise tomorrow?** monday.com's own models first (re-test the 18 before switching), an alert automation
   second; no AI columns answering RFP questions, because they would skip the figure check. Source: D-PLAN.
