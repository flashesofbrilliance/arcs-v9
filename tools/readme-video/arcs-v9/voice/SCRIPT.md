# arcs-v9 README walkthrough narration

One section per card. Each must equal that card's `v` in build.cjs (rule R0). Read in Zach's voice; "Arcs" is said "arks".

## 01

Arcs helps you think through one hard decision. You type the question. It gives back one next step, the reasons for it, three follow-up questions, and a label for how settled the answer is. It does not make the decision for you. The final call stays yours.

## 02

Each question gets one Claude call, with a prompt that walks six steps. Is this a real decision, and what are the strongest objections? What evidence bears on it? Is it built on a false premise? An honest confidence score, from zero to one hundred. Then one next step, and up to three reasons.

## 03

Plain code, not the model, then labels how settled the answer is. Green means no warning fired, and confidence is sixty five or more. Yellow means a caution, or confidence under sixty five. Fork means two or more workable paths. Paradox means exactly two paths, with confidence under sixty. The table has the rest.

## 04

Here is what you can check. All seventeen tests on the labeling code pass. The app is live. A reader with no memory rebuilt seventeen of nineteen parts of one incident from the repo history alone, about ninety percent. That is one incident, not the whole repo. And this read me was itself read cold, and checked claim by claim.

## 05

Some things are not what they may sound like. The canon describes eight layers, and the app runs six. The Observatory is a demo that replays a fixed dataset about this build, not your decisions. The operators folder is a reference library, not wired into the live compass. And the Python command line needs your own scan files.

## 06

Open app dot arcs dot care, and choose open the compass. No account is needed. Anonymous answers live only in your browser tab, and are not stored. If you are signed in, each run is saved as a receipt. Wider access opens in stages, through a waitlist. To run it locally, you need Node and a Postgres database.
