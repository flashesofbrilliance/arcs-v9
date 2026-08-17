---
title: "The Loop That Never Stops Asking"
subtitle: "What looks like reinforcement learning is a person climbing their own hill, one honest step at a time, with the machine bound not to move the summit."
status: DRAFT — for Zach's review. Do not publish.
hardening: "Epoch 4 · fidelity SHARP · 4 epochs / 18 gauntlets. A cold CRYSTAL falsifier drew real blood on the spine (a proxy CAN be trained on the accept/reject trace), so the claim retreated from difference-in-kind to no-substitution + a pragmatic legibility edge. CRYSTAL denied, honestly. See notomation-gradient-ascent.hardening.md."
date: 2026-08-17
canon_anchors:
  - CLAUDE.md / AGENTS.md — ROM Primitive 1 (NOTOMATION), quoted verbatim
  - memory: throwaway-context-not-throwaway-learning, prepaid-reflexes-tier-descent,
    context-manifold-as-model-agnostic-attractor-basin, brand-promise-refusal-to-overclaim
  - WORLD.md — render scale (applied to this doc's own hardening ledger)
working_titles:
  - "The Loop That Never Stops Asking" (current — names the thesis, no jargon)
  - "Never Amortize the Human"
  - "Gradient Ascent Without the Gradient" (retired — over-leans the ML analogy the body disciplines)
---

# The Loop That Never Stops Asking

*What looks like reinforcement learning is a person climbing their own hill, one honest step at a
time, with the machine bound not to move the summit.*

---

## The one difference that matters

Spend a few hours refining a skill with a model, one accept-or-reject at a time, and you will want
to call it reinforcement learning. The surface rhymes: try, score, adjust, try again, get better.
Everyone reaches for the word.

Here is why the word is wrong, and why the wrongness is the whole point. RLHF exists to *stop asking*.
It spends human labels to train a reward model precisely so it can turn the human off and optimize
against the proxy. This loop is the opposite. It never stops asking, because the objective is one
specific person on one specific artifact, and there is nothing to hand the asking off to. A reward
model would be a worse copy of the only thing that matters.

So the honest question is not *"was that RL?"* It was not. The honest question is *"then what was it,
exactly?"* This is an answer, and it comes from ARCS, a decision instrument whose whole discipline is
to hand you a bearing and refuse to hand you a verdict.

## The overclaim, named

There was no reinforcement learning in that session. Say precisely what the RL story would need: a
parameter update on the model, computed from a reward signal, moving a policy. None of it happened.
The model's weights were frozen the entire time. Nothing backpropagated. No policy moved.

Borrowing *reinforcement learning* for what actually happened would be an overclaim, and ARCS has one
house rule it turns on everything, including its own most flattering descriptions of itself: **refuse
to overclaim.** Do not borrow a term of art the artifact cannot back. A system that dresses a
hill-climb as RL is doing what a system does when it sells immunity while it can only offer
survivability. It manufactures a confidence it did not earn.

## The honest frame, and its one concession

It was **gradient ascent where the person's revealed preference stands in for the gradient.** The
objective is their taste, observed live through their reactions, never distilled into a stand-in that
gets consulted instead. Each accept or reject is a signed step: *keep this* points a direction, *cut
this* points the other way, *colder* carries a rough magnitude. The optimizer is the person and the
model coupled, the model proposing positions and the person supplying the direction.

Now the concession that has to come first, because a knowing reader is already reaching for it. **The
loop itself is active learning.** Proposing the most informative candidate next and spending the
human's attention where it moves the objective most is decades old, and calling it "gradient ascent
on revealed preference" adds no acquisition function and no stopping rule. If that were the claim, it
would be a naming ceremony.

The claim is what the loop is *for*. Active learning selects queries to train a model that will
eventually stop needing the human. Here the human is never handed off. Its output is not an opaque
policy but **portable, human-legible artifacts** a later model can read: a skill file, a set of
exemplars, a few memory notes. Active learning is instrumental to a model; this is instrumental to a
person.

Now the correction that a hard test forced, because the first version of this section overclaimed and
the honest version is narrower still. I wanted to say the objective is *never distilled into a proxy
at all*, because at N=1 "there is no sample to train one on." That is false, and the falsifier that
found it was right: the accept/reject trace **is** a sample, a small preference dataset, and you could
train a proxy on it. So the real distinction is not *no representation*. It is **no substitution**: the
person stays the final judge on every step, and a representation is never consulted *in place of* them.
An opaque model queried under continuous human judgment would honor that same principle. Which means the
edge this essay actually defends is the smaller, plainer one: the gains come out as a **legible record
you can read** rather than a policy you cannot. That is a real and useful difference, but a *pragmatic*
one, not a difference in kind. Everything here holds at N=1 and claims nothing at any scale where
training the proxy would pay.

## One real step

Watch a single step, because the claim "the reaction is the gradient" should be shown, not asserted.
This essay was hardened by the loop it describes, so the specimen is honest and close at hand.

A draft sentence read: *"The weights are real. Those artifacts are the literal weights this ascent
wrote to."* A reviewer's reaction, the signed step: *that negates your own hedge; you spent three
sections saying this is an analogy, and here you call it literal.* The revision: *"The gains are real.
They are the weights, in the analogy's terms, and the analogy stops at the arithmetic."* One reaction,
one direction, one artifact moved. No reward model computed that. A person did, and the improvement
now lives in the file you are reading, not in anyone's weights.

## The practice: keep the rejected directions

One practice falls out of all this. It is not a discovery, it is an old and under-followed discipline,
and active-learning tooling routinely throws it away.

**Capture the directions you rejected, not only the ones you kept.** A dead end costs the same to
discover as a good step, and it is almost never written down, so the next same-shaped job re-buys
every one from zero. The reason nobody does it is not that they disagree; it is that logging negatives
is dull and the payoff is deferred. So make it a single-line cost: when you cut a direction, append the
cut and its one-line reason to the same file, on the line beside the step you kept. It is not free, it
is one decision and one line per cut, and it only pays off if you actually re-read the file before the
next attempt. But that is a small, bounded cost against re-buying the same dead end from zero. The skill
file already records where you arrived; this makes it also record where you turned back. ARCS has a name
for the leak it closes: *throwaway context, not throwaway learning.* The window is disposable. The
learning inside it must not be.

The hoped-for payoff is that a cheaper model could later read the grooves the expensive climb already
cut instead of re-cutting them: pay for the ascent once, then roll in it. Hold that loosely. It is the
design intent behind writing gains to a portable substrate, not a measured result. No cheap model has
re-run these artifacts and matched; until one has, the reason to keep the negatives is the cheap,
proven one (you stop re-buying dead ends), not the unproven one.

## NOTOMATION, and where it actually bites

The first ROM primitive, quoted verbatim from CLAUDE.md:

> **NOTOMATION** — scaffold/sequence cognition only; never compress/replace/overrule revealed
> preference.

Read as a constraint on the loop it is exact: the scaffold may sequence the climb, but it may never
substitute its own guess about what "good" means for the person's judgment of it. It may order the
work, surface the next candidate, hold the state, propose the step. It may not swap the hill.

That is a stated constraint, not a lock, and the honest version has to admit two limits. The first:
the failure it names, a fluent model quietly optimizing for its own sense of a good answer so smoothly
the swap goes unnoticed, is a failure NOTOMATION *forbids* but does not *prevent*. It is the rule the
model is bound to, not a mechanism that makes the drift impossible. The second is sharper. NOTOMATION
governs whether your choice is overruled. It says nothing about **which candidates you were shown.**
The model still shapes the choice set, and a preference expressed over three options the model picked
is only as honest as that selection. The consent is governed; the framing upstream of it is not.

An honest note on the product, since this is where the essay could most easily cheat. ARCS frames its
output as a bearing, not an answer: the result carries a *True North* label and the positioning copy
says plainly that the tool does not decide for you. That framing is real and it renders. But it is a
frame around the answer, not a guard on the answer's words. The system does not forbid the model from
writing *you should*, and in fact it asks for one concrete sentence rather than a hedge. So the
bearing-not-command discipline lives in the label and the copy today, not in an enforced rule on the
generated text. Saying that out loud is the same refusal to overclaim the rest of the piece runs on.

## The honest edges

Where the analogy earns its keep is also where it stops:

- **It is gradient ascent by analogy, not by mathematics.** No differentiable objective, no computed
  gradient, no convergence guarantee. Every optimization word here, gradient, step, weights, is
  borrowed as a lens, never claimed as mechanism.
- **The gradient is noisy and non-stationary.** People are inconsistent, and their taste moves while
  they climb. Some of the ascent is the objective itself shifting, which no optimizer handles cleanly.
- **Artifacts capture the climb, not the climber.** The skill file holds where you ended up, not the
  person. Re-run the loop with a different objective and you get a different hill, correctly. The
  record is portable; the taste that wrote it is not.
- **A stale artifact is a proxy too.** The whole distinction from RLHF is that the objective is never
  distilled into a stand-in. But a skill file consulted *instead of* the person, long after their taste
  has moved, is a stand-in. A legible one, which is better than an opaque one, but the substitution the
  essay warns about creeps back the moment the record is trusted in place of the judge. Legibility is
  not freshness. The artifact defers to the person; it does not replace them.
- **The distinction is regime-bound.** Everything here holds at N=1, one person and one artifact. It is
  not a claim that this beats amortization anywhere amortization would pay. Read wider than that and the
  essay is overclaiming.

## The one line

RLHF spends the human to buy the right to stop asking. This loop refuses the trade: the person stays
the objective, the machine is bound not to move the summit, and what the climb leaves behind is a file
you can read, not a weight you cannot.

---

*Draft. ARCS voice, honest-by-default. Every mechanism is either verbatim canon (NOTOMATION) or a
plain, source-checked description of the product and the session that produced the idea. The
optimization vocabulary is deliberate analogy, flagged as such. Nothing is asserted as live system
behavior that the code does not do, including the admission that the bearing-not-command convention
is carried by the interface, not enforced on the generated sentence. This draft was hardened over two
gauntlet epochs; the scar-log is a companion file.*
