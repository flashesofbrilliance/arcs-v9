# Ahmed call, Sep 3: what he said, and the plan to change how we share

Source: raw Granola transcript `363c13a2` (Sep 3, 1:30 PM), pulled as transcript, not summary.
Every line in quotes is verbatim. Everything else is labeled as a read.

## The one-line verdict, his words

"I think you're thinking about this process of like kind of adversarial and testing is a really good
idea. I just think that honestly, your delivery mechanisms are just not great."

He said the value is real and the presentation loses it: "it's lost on at least me because of the
way it's presented." He asked at the end, "is there anything I can do to help or anything we can do?"
The partnership is still open. The blocker is consumption, full stop.

## What he said, grouped, with the quote that carries it

### 1. The problem is hierarchy, not volume of value
- "it's so hard to follow what is important, what is not, and what are the layers."
- "where's my hierarchy of information that's important?"
- "I have to go through each one of these things and like really try to read it to know what is
  this even telling me."
- "I feel like I'm giving it less credit because I'm having a hard time quickly figuring out what it
  is, but I think it really seems like really valuable."

### 2. The shape he wants: takeaway up front, then evidence, then depth on demand
- "here is my goal. Here are the things that I missed. And then like, here's how I fix it. Then
  supporting evidence and other interesting things that I should know."
- "if you had to narrow it down to 3 reasons why I should care. Okay, great. And then ... what are
  the first 3 questions I'm gonna have and what are those first 3 simple answers? And then I'll
  drill down into that."
- "You kind of give like 4 or 5 steps. So I think it would be good to have like 2 steps into it
  versus just one step."
- "takeaway up front, supporting evidence, takeaway ... maximum one plot, one big number."
- "if maybe I need to know more information and there's like a little eye and I can click on it."

### 3. Depth is wanted, but never first
- "nobody wants depth front. You want depth once you know, like you have the ability to know how to
  scan it because you built it."
- "you're not giving the person the reason to want to continue."
- "you have to get my interest piqued so that I can go into the depth."

### 4. The consumption-cost rule
- "if it takes the system like a day to create it, it should take me an hour to consume it ... it
  should be faster to consume it than to create it. And if it's created just really roughly, then
  like you put the work on the consumer."
- "zero mental math basically" (Zach's summary, Ahmed agreed).

### 5. Format: less text, more structure, possibly a deck
- "it could be more like a deck versus like a long PDF ... all of it is just like intense amount of
  text, and it's also hard to read."
- "I would honestly recommend just asking like the system to create a PowerPoint for executive, for
  like a VC telling them the story ... you need someone to give a shit first."
- "a VC doesn't care, can't tell them about your innovation before they care about the problem."

### 6. The live A/B he ran on Saul's brief
He pasted the Saul inputs into ChatGPT and read its output next to saul.arcs.care. His read of the
ChatGPT version: "This feels a lot easier for me to consume this than the initial one." What worked
in it, in his words: "the decision ... the whole takeaway point I need to know ... if I know nothing,
I'll take this." Then "the role, here's some basic information." Then "what is proven and what is
not." Then "before the call, bring 3 proofs. Okay, this is my task." Then "5 useful questions here."
His read of ours: "I looked at yours and I skimmed through it ... tried to read different pieces like
multiple times and I have no idea, like what I'm trying to do."

Honest note: saul.arcs.care already contains every element he praised (decision line, three things
to land, ask two, watch-outs). He could not find them. That is the finding. The content is right and
the order, density, and visual weight hide it.

### 7. Reference designs he named
- His own tool's default report: "executive read is always up front, like takeaway points ... maximum
  one plot, one big number ... takeaway up front, supporting evidence, takeaway."
- Co-Star: "they help you understand what's important ... they kind of built you up in steps and then
  you're like literally paying to get more information." Headline, lede, then the math underneath.
- Myers-Briggs style test results: same pattern, plain verdict first, detail on request.
- Dashboards are different: "big numbers up front on top, then your charts as you tell a story."

### 8. What he thinks ARCS is (his one-sentence version, keep it)
"if you were having a conversation with Claude, and you wanted Claude to like battle test something
for you ... combining both the ability to battle test it and the way we would normally eval it to
treat it like kind of like a metric. So you're doing the benefits of battle testing and evaluations
in one for real-world problems."

### 9. His one suggestion for the fix mechanism
"you have a good eval system that can just fight with like a person ... how do you make this more
digestible? Have your system fight and try to like battle test it itself."

### 10. Standing offer
"is there anything I can do to help or anything we can do? ... I had some notes on the call and
discuss potentially doing stuff together."

## Where today's pages already land and where they still miss (read against his rules)

| His rule | ahmed-start | one-table | loop | atlas | saul |
|---|---|---|---|---|---|
| Takeaway first, one line | yes (preframe + offer) | partial (preframe, no verdict line) | no (title, then table) | no (title, then 3-paragraph preframe) | partial (headline, buried under eyebrow) |
| 3 reasons to care, then 3 questions | no | no | no | no | no |
| One plot or one number per step | n/a | one table | one table per stop | 19 cards | dense |
| Depth behind a click | no (all inline) | no | no | no (all cards open) | no |
| Consume faster than create | ~2 min, ok | ~90s, ok | ~3 min | ~5+ min, fails | fails per his A/B |
| Deck-shaped steps | no | no | yes (4 stops) | no | no |

## The plan: change the delivery layer, not the engine

### A. Adopt one document grammar for every counterpart surface (the "Ahmed order")
Fixed, in this sequence, every time:
1. **The verdict.** One sentence. "If I know nothing, I'll take this."
2. **Three reasons to care.** Three lines, no sub-bullets.
3. **Three questions you will have, three short answers.** The first drill-down.
4. **Your tasks.** "Before the call, bring 3 proofs." Numbered, imperative, cut at 60 seconds each.
5. **Evidence, behind a disclosure.** The quotes, the numbers, the rows. Collapsed by default, one
   plot or one number per expanded step.
6. **The full record, linked.** The atlas, the SSOT-derived tables, for the reader who wants depth.

This is the saul PREP schema re-ordered and gated, not a new template. The content survives; the
order and the disclosure change.

### B. Stamp it as a data-driven template, then re-render the existing surfaces
- Add a `verdict`, `reasons[3]`, `questions[3]` block to the PREP data object; renderer emits
  section 1 to 4 open, 5 collapsed (`<details>`), 6 as links.
- Re-render saul.arcs.care from the same data in the new order. This is the A/B he already ran; it
  is the acceptance test. Send him both versions and ask which one he can act on.
- Re-render ahmed-start as the verdict-first version of the same content.

### C. Density budget, enforced mechanically
- Sections 1 to 4 together: under 250 words, under one screen at 375px.
- One plot or one number per expanded evidence step. The renderer refuses two.
- Consumption-cost stamp at the top of every artifact: "Read time: N minutes." If N exceeds a tenth
  of the build time, it does not ship. His rule, made into a gate.

### D. Make the gauntlet fight for digestibility, not just truth
His suggestion, and it fits the existing tooling. Add a facet to `counterpart-gauntlet`: a cold
reader with two minutes who must answer, from the page alone, "what is this, why should I care, what
do I do." If the facet cannot answer all three from sections 1 to 4, the page fails. Truth gates
stay; a legibility gate joins them.

### E. Steal the two reference patterns he named
- **Co-Star pattern**: headline, lede, math underneath. Maps exactly to sections 1, 2, 5.
- **His own report default**: takeaway, evidence, takeaway. Maps to the evidence steps in section 5:
  each expanded step opens with its takeaway line, shows one thing, closes with what it means.

### F. Sequence
1. Today: this plan, plus a reply to him (draft only, he sends nothing, you send by hand): thank him,
   tell him the fix is the order and the gate, and that he will get the Saul page both ways to judge.
2. This week: PREP schema change + renderer; re-render saul and ahmed-start; run the new legibility
   facet; send him the A/B.
3. After his read: if he can act on the new version in two minutes, promote the grammar to the
   forge and re-render the counterpart family. If not, the grammar is wrong, not the density; go
   back to his six quotes in section 2 above.

## Falsifier
He reads the re-rendered Saul page and either says what it is and what to do inside two minutes, or
does not. That is the whole test. Nothing else about ARCS changes until it passes.
