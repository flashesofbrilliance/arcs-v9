# Bench video script

## 1. The model proposes. Code checks.

This engine answers questions about a short, fictional R F P and its amendment, written just for this sample. A model helps write the answers, but it never gets the last word. The code does. And a bench of test cases and injected faults checks that those safeguards actually hold.

## 2. Where the model stops

First, the code parses the R F P and finds the clauses that might answer the question. For four fixed questions, it skips the model entirely, and just quotes the governing text. Otherwise, the model proposes an answer: it picks the clauses, and writes one sentence.

## 3. What code checks

Then the code checks that answer. Every cited clause has to exist, and every figure has to appear in them. If it passes, you get the answer, with citations. If it fails, the model's sentence is held back.

## 4. Eight cases, one command

Eight test cases run through the M C P server. With the mock model, which is a stand-in for testing the plumbing and the safety checks, not real answers, all five of five pass. The other three traps need a real model, so the mock skips them. The real-model run is a separate result. And the server returns exactly what the engine returns when you call it directly.

## 5. Faults the check catches

Here's the fun part, the mock model can also fail on purpose! Say it invents a figure? The check names it, and holds the sentence back. Change a single dollar figure, and the check catches that too. And if it cites a clause that doesn't exist? No answer. At all.

## 6. Faults that fail safe

Ask it to draft a whole proposal, or hand down a bid verdict? That's withheld. If the model times out, returns garbage, or flat-out refuses, the engine fails safe, with no answer. Eight faults in. Eight caught.

## 7. A second bench

I used the same discipline on a provenance search engine. I wrote the rules down first, and then ran it exactly once. A shingle index missed edited quotes, so I cut it. A quick pre-check, a Bloom filter, dropped thirty-seven true files, so I cut that too. Hash checks caught every tampered file, so they stayed.

## 8. A claim you can rerun

A bench turns a claim into something you can rerun. It tells you what to cut, and what to keep. On that bench, two layers were cut, and one check was kept.
