# The Plain-English Version

*A companion to [the essay](notomation-gradient-ascent.md) and [its hardening ledger](notomation-gradient-ascent.hardening.md),
with the jargon removed. The other two files are written in "ARCS speak." This one is not. It explains
the idea in normal words, and then shows how the document rewrote itself, version by version, getting
plainer and more honest each time.*

---

## The idea, in one breath

You sit with an AI and improve something over a couple of hours, saying "yes, keep that" and "no, cut
that" over and over. It feels like you're *training* the AI. You're not. The AI never changes. **You**
are doing the improving, and your yes/no reactions are the steering wheel. The improvements get saved
in ordinary files (a notes file, some examples), so the work isn't lost when the chat closes.

That's the whole thing. The rest is being careful about how you say it.

---

## The idea, in a few more sentences

- **It looks like "reinforcement learning" (RL), but it isn't.** RL actually rewires the AI's internals.
  None of that happens here. The AI is frozen the whole time. Calling it RL would be borrowing a fancy
  term you didn't earn, so we don't.
- **What it actually is:** you climbing a hill, where each "keep this / cut that" is a step in a
  direction. You are the judge of what "better" means, the whole time. The AI just hands you options.
- **The one rule that keeps it honest:** the AI is allowed to *organize* the work and *suggest* the next
  option, but it is never allowed to quietly decide what "good" means for you and slip its taste in for
  yours. (In ARCS that rule has a name, "NOTOMATION." In plain words: *don't let the tool replace your
  judgment; let it only tee things up.*)
- **Where the improvement is stored:** not inside the AI, but in plain files you can open and read. That's
  why the work survives to the next session instead of starting from zero.
- **The one useful tip:** save the ideas you *rejected*, not just the ones you kept. Dead ends cost the
  same effort to find, and nobody writes them down, so you keep rediscovering them. Jot the reject and a
  one-line reason next to the thing you kept. Costs nothing, saves you re-doing dead ends later.

---

## The honest catch (added late, and it matters)

This only clearly matters when it's **one person improving one thing.** At that tiny scale there's
nothing to automate anyway, so "we never automate your judgment" isn't really a brave choice, it's just
the only option. It's a real *difference* from the big-AI approach, but it is **not** proof that it's
*better*. Say it any bigger than that and you're overselling.

---

## How the document rewrote itself (the version history)

The essay was put through waves of hostile review. Each wave is a version bump. Here's the same core
sentence, rewritten each time, so you can watch it get sharper and more honest. (This is the thing the
ARCS files call "render fidelity" going from blurry to sharp. Plain version: the claim starts vague and
gets pinned down.)

### v0.1 — first draft ("sounds impressive")
> *"Refining a skill with an AI is a kind of gradient ascent where your preferences are the gradient,
> and the improvements are the literal weights the process writes to."*

Confident, quotable, and leaning hard on machine-learning words. Problem: it half-claims to be the very
thing (RL) it also says it isn't, and it states one "fact" about how the ARCS product works.

### v0.2 — after the fact-check and honesty pass ("stop borrowing words you can't back")
> *"It's not literally reinforcement learning. It's more like climbing a hill where your yes/no choices
> point the direction, and the improvements are saved as ordinary files, not as anything inside the AI."*

What changed and why:
- **A "fact" about the product turned out to be false.** The draft claimed the ARCS app does a specific
  thing when you disagree with it. We checked the actual code: it doesn't. That whole sentence was cut.
  (Notably, three of the reviewers had *wanted* to feature that sentence more prominently. The one
  reviewer who checked the code proved it false. Checking beat sounding-good.)
- **"Literal weights" was downgraded to "like weights."** Calling a text file a "weight" is borrowing
  math the file doesn't actually do. The honest version: it's a *record*, not a weight.

### v0.3 — after the "what's actually new here?" pass ("say the real thing, admit the borrowed thing")
> *"The hill-climbing part is just 'active learning,' an old and known idea. The new part is narrower:
> your judgment is never boiled down into a shortcut the AI uses instead of you, and the results stay
> as plain files a person can read."*

What changed and why:
- **A skeptical expert reader would have shrugged.** "This is just active learning with saved notes."
  Fair. So the essay now *concedes* that outright and points at the genuinely new sliver instead of
  dressing up the old part.
- **Another false product claim caught, of the same type as before.** The essay had said the ARCS tool
  always phrases its output as a suggestion, never a command, "by design." Checked the code: it doesn't
  enforce that. It even asks for direct, concrete answers. So the essay now admits this out loud: the
  "it's a suggestion, not an order" feeling comes from labels and wording around the answer, not from a
  rule inside the software. Admitting that is more honest than hiding it.

### v0.4 — after the formal debate ("is the idea even real, or just clever?")
> *"When it's one person on one thing, this genuinely differs in kind from the big-AI approach, because
> your judgment is never turned into a stand-in and the results stay readable. It's a real difference,
> not a proven improvement, and it only holds at that tiny one-person scale."*

What changed and why:
- **A staged debate** (a defender, a ruthless critic, and a panel acting as judge) put the *idea itself*
  on trial, not just the wording.
- The critic's best hits landed and were fixed: the essay now says plainly that this only matters at the
  one-person scale, gives the "save your rejects" tip an actual how-to, and stops implying it beats the
  big approach.
- **The scoring sheet had to fix itself, too.** The behind-the-scenes tracker had been rating its own
  confidence to two decimal places (like "0.72") when those numbers were just guesses. That's the same
  fake-precision sin the essay criticizes. So the tracker switched to plain "low / medium / high." The
  honesty tool had to take its own medicine.

### v0.5 — the final test ("hand it to a stranger and see if it breaks")
> *"The real difference isn't that your judgment is never turned into a shortcut — it can be. The
> difference is that the shortcut is never allowed to overrule you, and the results stay as readable
> files. That's a useful, practical edge, not a deep difference in kind."*

We handed the finished files to a *fresh* AI with no memory of any of this, five times over, cheaply,
and asked: can a stranger pick these up and use them without the author in the room?

**Three of the five checks passed cleanly.** A stranger AI could run the "save your rejects" tip from the
text alone, could recover the idea *and* its limits without help (the writing "actively punishes
overstatement," it said), and found no new mistakes in the latest round of edits.

**But one check broke the main claim — and this is the important part.** The essay had been leaning on the
line "at one-person scale there's no data to build a shortcut from." A stranger AI pointed out that this
is simply false: every yes/no you give *is* data. You could absolutely build a shortcut (a small
preference model) from it. So the grand claim ("this is fundamentally a different kind of thing than big
AI") collapsed. What survives is smaller and true: the point isn't that you *can't* build a shortcut, it's
that you never let the shortcut **overrule you**, and the results stay readable. A real, practical edge.
Not a different universe.

So the document did **not** get the top grade ("CRYSTAL"). It failed its own final exam on purpose, and
that is the best thing that happened to it. The whole method exists to catch exactly this kind of
too-big claim, and here it caught its own — even catching a mistake that an *earlier* fix had introduced.
A process that can prove its own headline wrong is the opposite of a sales pitch.

*(How it was done, plainly: instead of one expensive AI, we used five cheap ones to poke at the files in
parallel and one expensive one to weigh the results — the budget way to stress-test something.)*

---

## Why go to all this trouble?

Because the essay's whole point is *honesty*, so it would be embarrassing to publish it with a false
claim inside. The elaborate review process is just: attack your own work hard, from many angles, fix
what breaks, and keep a visible log of every change so nobody has to take your word for it. The scars
are left showing on purpose. (ARCS calls that "kintsugi," after the Japanese craft of repairing pottery
with visible gold seams instead of hiding the crack. Plain version: *show your repairs; don't sand them
off.*)

The surprising part is what the process actually caught: not the fancy claims, but two small, factual
"the product does X" statements that turned out to be false, both quietly inherited from the project's
own internal documents. The lesson, in plain words: **when a claim comes from your own paperwork, go
check the actual thing, because your paperwork can be wrong too.**

---

## The jargon, translated

| ARCS word | Plain meaning |
|---|---|
| **NOTOMATION** | "Don't let the tool replace your judgment; let it only set things up." |
| **gauntlet** | A hostile review pass. Send the work through a critic whose job is to break it. |
| **kintsugi** | Repair the work and leave the repair visible, like gold seams in mended pottery. |
| **render fidelity** (GRAIN → SHARP → CRYSTAL) | How pinned-down the claim is: blurry first draft → sharp → proven. |
| **belief ledger** | A running scorecard of how confident the doc is in each claim, and how that moved. |
| **pathogen** | A false claim caught from a trusted source (here, the project's own docs) that spreads. |
| **Constitutional Court** | A final judge panel that rules whether the idea holds up against the project's own rules. |
| **the spine / the trunk** | The one core claim everything else rests on. |
| **falsifier** | The specific test that, if it failed, would prove the core claim wrong. |
| **DEWY / Y-gate / compass** | ARCS's internal product machinery. Not needed to understand the idea here. |

---

*This plain version tracks the ARCS files. When the final test (v0.5) returns, both this file and the
ledger get the result, so the two stay in sync.*
