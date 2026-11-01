# arcs-v9 README walkthrough narration

One section per card. Each must equal that card's `v` in build.cjs (rule R0). Read in Zach's voice; "Arcs" is said "arks". Written for the ear (2026-11-01 rewrite after the post-mortem): README order, proof on card 1.

## 01

Arcs helps you think through one hard decision. You ask. It answers with one next step, and a label for how settled that answer is. And you can check it. Seventeen of seventeen tests pass on the code that sets the label. The final call stays yours.

## 02

Try it now. Open app dot arcs dot care, and choose open the compass. No account is needed. Anonymous answers live only in your browser tab, and are not stored. Sign in, and each run is saved as a receipt. To run it yourself, you need Node and a Postgres database.

## 03

Behind each answer is one Claude call. Its prompt walks six steps. Is this a real decision? What are the strongest objections? What evidence bears on it? Is the premise false? Then an honest confidence score. And finally, one next step.

## 04

Then plain code, not the model, labels how settled the answer is. Green, when it holds up. Yellow, when a caution fires. Fork, paradox, delta and scratch name the other ways it can be unsettled. The exact rules are on screen.

## 05

So what can you check? All seventeen tests on the labeling code pass. The app is live. And a reader with no memory rebuilt seventeen of nineteen parts of one incident, from the repo history alone. About ninety percent. One incident, not the whole repo.

## 06

Some things are not what they may sound like. The app runs six of the eight layers the canon describes. The Observatory replays the history of this build, not your decisions. The operators folder is a reference library, not wired in. And the final call stays yours.
