# Walkthrough narration, read in your voice

Record one file per card. Save as voice/01.m4a to voice/08.m4a (Voice Memos or QuickTime; m4a, wav or mp3 all work). Each card stays on screen as long as your take runs.

## 01

Ask this engine about an RFP, and it either quotes the exact clause behind its answer, or it refuses. It never guesses. The RFP here is a short fictional one, written for this sample. It is standard library Python, with nothing to install.

## 02

It works in three steps. Documents are split into clauses by rules, not a model, and amendments are recorded as superseding what they change. Search finds the candidate clauses. Only then does a model pick clauses and write one sentence, and code checks that sentence before anyone sees it.

## 03

Here it is through the Claude MCP server. Ask for the bid deposit, and it returns thirty five thousand dollars, citing both the original clause and the amendment that replaced it, with a note that the amended value governs. The gate field says which check decided the outcome.

## 04

Six rules keep it honest, and they're enforced in code. It shows its source. Numbers match the text exactly. The latest amendment wins. "Not covered" counts as an answer. Facts, not decisions: it won't write your bid or tell you whether to bid. And no guessing: without a model, you get the clauses, not a summary.

## 05

To test the checks, the mock model can misbehave on purpose. Here it invents eighty thousand dollars and twelve percent. Neither figure is in the cited clause, so the summary is withheld and only the clause text comes back. Eight injected faults were tried, and every one was caught.

## 06

Here is what was measured. Five of five deterministic cases pass through the server, with output identical to calling the engine directly. Then a real model, on twenty-four pre-registered questions: eleven correct, twelve withheld, one wrong. That misses the zero-wrong target.

## 07

The gaps, plainly. There is no confidence score. Retrieval is keyword based. Figures are checked, but meaning is not. It reads plain text in one numbering style. And it was built for RFPs, so contract clause types like indemnity get no special handling yet.

## 08

To try it, add the server to Claude Code with one command, and ask about the bid deposit. Setup and the checks are in the MCP read me.

