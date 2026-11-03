# Recoil close: monday FDE team walkthrough, 2026-10-26 (internal)

Source: Granola transcript 492e8cc7-5ea7-44ef-b9f8-5327d58ed253, 61:44 long, 273 segments, read in full.
Panel: Jacob Green (ran the meeting), Kamran Uddin, Robert Dixon. Zach went off camera to present.

## Receipt closed: predicted vs actual

| Predicted (Call Sheet plan) | What happened | Evidence |
|---|---|---|
| Sam's agenda: slides first, then demo and code | Zach opened with the front page, the drill-down view and the bench. Jacob stopped him at 11:45 to ask for the stakeholder presentation first | 0:51 Jacob lays out the agenda; 11:45 "before we go into the demo, is there a presentation that you have for the stakeholders?" |
| Slides in about 10 minutes | The deck ran from 12:19 to 25:19 (13 minutes), with a pilot-timeline question at 19:09 | timestamps |
| Live question on the board | Done: "Is there a cutoff date… can I submit past it?" got a cited answer. The second question was expected to be "not addressed" but was answered (the 150-page limit); Zach said "I tricked myself" | 26:29 to 28:40 |
| Code review: file, rule, test, gap | **Partly done, at the scope Kamran set.** He asked for the guardrail code, then narrowed it at 33:00 ("not all of them, just one or 2"). Zach walked one or two through the eval layer (golden case, its test, append-only K11 tests, grader check), then gave the liability posture. Not shown: answer.py and resolve.py, governance and change control (Zach stopped the share at 36:17) | 32:31 to 36:17 (corrected 2026-10-26) |
| Name the three unproven items | Partly: named the PDF limit, the unpinned temperature, polling vs webhooks and the API cap, in answer to "where would it fail" | 22:51, 38:12 to 40:08 |
| Your question 1: "what would you push on harder?" | Not asked. He asked whether the case is a real engagement, about first 30/60/90-day surprises, and about a shared harness library | 51:00, 56:37, 60:16 |
| End on time; his questions start by minute 50 | His questions started at 50:58; the call ended at 61:44 with his last question unasked | |

## What landed (grounded in their words)

- Jacob on the eval-change answer (append-only, superseding eval): "I think that answers it very well."
- Jacob on the questions: "I think you did a very good job with answering questions around that" (policy and eval change versus naive RAG).
- Jacob's close: "It's clear that you put a lot of effort and attention into this. Incredibly meticulous. It was a pleasure to chat to you and hope we get to catch up soon."
- Robert confirmed the case mirrors a real engagement they are pursuing. Jacob described their motion ("stacking those up into a library… pushing back into the product"), which matches Zach's harness thesis.

## Corrections to book: claims said live that the record contradicts

| Said | Record (rc46) |
|---|---|
| "$0.76 per run, per question" | $0.76 per **cycle**; about $0.004 per question (slide 7, bench) |
| "about 0.004 **cents** per question" | about $0.004 (dollars) |
| "3 RFPs that have been missed" | 3 bid windows missed **or nearly missed** in 24 months (slide 1) |
| "covered about 16 of the 20 evaluations" for the local models | 16/20 and 17/20 were the **blind sets before fixes**; the local model scored 14 of 18 on the first set |
| "the AI column cite-source feature they already have" | slide 10 **recommends** AI columns that cite; the feature does not exist yet |
| "architectural decision receipts" | ADR = architecture decision **record** |
| "Oak Ridge" | the ISO is Heartland ISO |
| "7 adversarial passes" | not verified in the record |

## Missed prepared answers (in the Call Sheet, not used)

- **PII to models (Kamran):** proposed a new redaction or hash middleware. The existing posture went unmentioned: only the question plus about 8 clauses leave (about 3,400 characters), every call is logged, and the local model keeps the AI step on RET's machine.
- **Retrieval at scale (Robert):** answered with caching, RBAC and CRM. The prepared D-600 answer went unmentioned: search, then select, never the whole document; add local embeddings as a second retriever; Docling for PDFs.
- **The code walk itself**, the part the brief calls "not optional".

## Risk flags

- Agenda misread at the start (about 6 minutes, and the first impression).
- Long answers: the "smarter over time" answer ran about 4 minutes, and Zach said so himself.
- "a really hardcore Israeli CISO person": a national generalization about the employer's people on a recorded call; low but nonzero risk.

## Belief log

| Prior | Posterior | Confidence | Conviction |
|---|---|---|---|
| The panel grades code first | The panel ran it as stakeholder presentation, then demo, then judgment questions; the code walk was only probed once (Kamran) | 0.7 | medium |
| Gaps named up front read as strength | Held: the failure-mode answer drew no pushback | 0.6 | medium |
| Fit with the team's motion | Strong: real-engagement case, harness/library thesis, "goalposts move" | 0.7 | medium |

## Verdict

**FORK / YELLOW.** The rapport and closing signals are warm and specific ("incredibly meticulous", praise for the questions). The scorer-facing gaps are real: no code walk, an agenda slip, number slips. Advance probability is about 0.55 (judgment, not data).

## Next (the leave-behind is the repair channel)

The draft goes to Sam for the team, and Zach sends it. It should be a short note that:
1. corrects the cost and eval numbers;
2. links the guardrail code (answer.py figure check, resolve.py rules) as the walk Kamran asked for;
3. gives the two-line PII posture and the D-600 retrieval-at-scale path;
4. answers his unasked question.

Then file the ex-ante receipt (row receipt-monday-fde-offer), update memory, and draft the thank-you.

## Reverse pass and cross-reference (added 2026-10-26)

**Cause of the 11:45 redirect.** It traces to 6:14-6:38. Zach asked "has anybody seen the submission?", heard "yes", and skipped the deck. But Jacob had stated the agenda at 0:51: intros, presentation, then demo. The stated agenda should beat an inferred shortcut.

**The forward pass under-credited 43:03-46:12.** At 54:00 Jacob praised a "scorecard pulling things from the CRM" and "what happens when policy changes". That praise came from Zach's 37:01 and 43:03 answers. The retrieval-at-scale answer landed as judgment, even without the D-600 detail.

**The cost of the long answer.** The 46:47-50:45 answer (4 minutes) cut Zach's question time from 10 minutes to 8, and his last question was cut at 61:29.

**Shape of the call.** Credibility dipped in the first 26 minutes (agenda slip, number slips) and climbed from 37:00 on. The candidate-questions segment was the high point. The call ended stronger than its middle. Probability of advancing, revised: about 0.6.

## Revised read: open by default (added 2026-10-26, Zach's challenge)

Zach's read: the panel asked few code questions because the glass-box opening (front page, drill-down view, bench, all before anyone asked) answered "how does it work" up front. The panel backgrounds support it: all three have shipped systems themselves (Jacob: risk controls and approval flows at ION; Kamran: AWS architecture and guardrails; Robert: deterministic benchmark checkers), so visible internals settle their mechanics questions. The question time went to judgment (policy change, evals, scale, 30/60/90).
What still holds: Kamran asked explicitly at 32:31 for the guardrail code and got eval cases and DECISIONS.md, not answer.py or resolve.py. Being that open shrank the gap; it did not close it.
Repair: the follow-up links a 2:18 video of the guardrails running (title card re-cut to "On the running build"), framed "in case it's useful", which answers the ask without admitting a miss.
Probability of advancing, revised: about 0.62 to 0.65 (judgment, not data).

## Under-credited: the liability posture (added 2026-10-26, Zach's recall)

The transcript does capture it, in two places; the forward and reverse passes both under-weighted it.
- 35:07, directly after Kamran's guardrail ask: "from a burden of proof standpoint... due diligence, due care, and due process, assuming that each of the different stakeholders was kind of on the hook... a product-level way to limit exposure or liability."
- 55:00: "change controls, release management, global relay, and then all of the audit requirements for any publicly traded company."
- Corroboration: at 58:44 Jacob echoes it unprompted ("legal and compliance, what they'll actually allow, how those are changing"). Jacob built risk controls for trading operations at ION, so this register is his native language.
- Zach reports all three smiled at the posture line. Video is not in the transcript, so this is UNCONFIRMED by the record, but the 58:44 echo is consistent with it.
Effect on the read: Kamran's guardrail ask was answered at the level of architectural posture (why the guardrails exist, who is on the hook), not at the level of files. For this panel that may have landed better than a file walk would have. The video plus the ZIP-path guide supply the file level. Odds unchanged at about 0.62 to 0.65; this strengthens the rapport and fit side, not the evidence side.

## Correction: the guardrail ask was met at Kamran's scope (added 2026-10-26)

Re-read of 32:31 to 36:33. Kamran scoped his own ask down at 33:00 ("not all of them, of course, just one or 2. Go for it."). Zach delivered one or two through the eval code and tests, then the posture line at 35:07, and ended the share himself at 36:17. Jacob's 36:33 question (wants that turn out to be needs, and how the evals absorb them) builds on that walkthrough. The earlier "biggest miss: no code walk" overstated it: this is a completeness gap (answer.py, resolve.py, governance and change-control tabs not reached), not an unanswered ask. Zach's read: the panel saw prepared answers behind the observability and explainability questions and moved on. Probability of advancing, revised: about 0.65 to 0.68 (judgment, not data). The follow-up video and the guide's Governance and Change control lists cover the unreached part.
