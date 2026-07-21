---
name: token-savings-bank
description: Use before or during any large, repetitive, multi-step, or cost-metered coding task – bulk edits across many files, long resumable work, or a session where token spend matters. Also invoke on observable waste: sequential reads that could be parallel, re-deriving project state every session, running a top-tier model on mechanical work, or spawning a subagent to answer a one-line question. It helps you choose model tier, batching, inline-vs-subagent, and checkpointing deliberately – without ever trading away correctness.
---

# token-savings-bank

A discipline for spending tokens like a budget, not a faucet. The goal is not to do less work –
it is to stop paying premium rates for cheap work and to stop paying twice for work already done.

**Correctness outranks budget, always.** Every lever below is subordinate to getting the right
answer. Budget mode never means skipping a check that matters, shipping a guess to save a call, or
trusting stale state. Where a lever and correctness conflict, correctness wins – the levers below
say so at each point where the temptation is real.

Four levers. Apply the ones that fit; they compose.

## Lever 1 – Model-tier routing

Match the model tier to the difficulty of the *current step*, not the hardest step in the task.

**Applicability first.** A running agent usually cannot change its own model mid-task – tier is
set by the caller or chosen when a subagent is spawned. So this lever is actionable only when your
setup lets you route: you (or an orchestrator) can dispatch a step to a subagent with a lower- or
higher-tier model. If you run as a single fixed model, read this as *which steps to hand off vs.
keep*, and skip the rest.

- **Route mechanical work to a cheaper tier**: applying a pre-stated edit, formatting, extracting
  fields, straightforward lookups. Test: if you can state the step as a rule ("change every X to
  Y"), a cheaper tier can execute it.
- **Escalate on a signal, not by default.** Escalate when: requirements are genuinely ambiguous, a
  first attempt failed, the reasoning spans several files or systems at once, or the action is hard
  to reverse.
- **Re-escalate the moment "mechanical" work surprises you** – an edit that will not apply
  cleanly, a test that fails, or a step that turns out to touch auth, crypto, money, or migrations.
  Do not de-escalate for anything security-sensitive or irreversible, even if it looks like typing.

Beware false-mechanical work: a cross-file rename *looks* like a rule ("rename every getUser") but
hides shadowed locals, comment/string matches, and look-alike symbols (getUserId). Verify the
match set before treating it as mechanical (see Lever 2).

## Lever 2 – Batch instead of drip

Every round trip has fixed overhead. Group work so you pay that overhead once – but only when the
work is safe to group.

- **Read together what you are already certain you need.** If you know you need three files,
  request them in one step. Fan out independent, **read-only** calls in parallel.
- **Batch only read-only or provably-disjoint operations.** Never parallelize writes to shared
  state (same file, ordered migrations, dependency installs) – hidden ordering and write conflicts
  are silent-corruption bugs, not token savings.
- **A class-wide edit requires you to confirm the pattern first.** "One edit that fixes the class"
  is powerful and dangerous: verify the full match set has no false positives *before* applying it.
- **On diagnostic or exploratory tasks, gate before you batch.** When you do not yet know which
  files matter (debugging a failure, tracing unfamiliar code), take one cheap probe first, then
  batch the reads the probe reveals. Speculative up-front reading is the "surveying options you
  will not take" waste in disguise.

## Lever 3 – Inline over subagent

Subagents cost a context setup and discard their intermediate work – but they also keep that
intermediate work *out of your context*. Choose on where the bulk actually lands.

The test: **would doing this inline flood my context with tool output I do not need to keep?**

- **Do it inline** when the task is small, you already hold the context, or you will need the
  details afterward (inline results stay in your working context; a subagent's do not).
- **Delegate to a subagent** when the work would otherwise accumulate a large volume of
  intermediate tool output you only need a conclusion from – a broad multi-file search, a wide
  sweep where you want the answer, not the hits. A tiny briefing that triggers a large search is
  the *strongest* case for delegating, not against it: the briefing is cheap, the discarded reads
  are the real cost, and the subagent absorbs them (often on a cheaper tier too).
- **Do not nest reflexively.** A subagent that spawns a subagent to do a one-line lookup pays three
  context setups for one answer.

## Lever 4 – Explicit checkpoint

Re-deriving state you already established is a quiet, recurring leak. Writing ground truth down
once and reading it back is cheaper – *when the task is long enough to re-derive at all.*

- **Only checkpoint when the task will cross a boundary**: a context-window compaction, a session
  end, or a handoff to someone else. Below that, your working context already is the checkpoint –
  writing a file is pure overhead and unrequested clutter. Use a scratch/gitignored location, not
  the user's tracked tree, unless a durable committed note is explicitly wanted.
- **Never checkpoint secrets.** Do not write credentials, API keys, tokens, connection strings,
  `.env` contents, or personal data into a state file. Checkpoint *references* – env var names,
  file paths – never values. Never `git commit` a state note without scanning it first.
- **A checkpoint records state as of when it was written.** Anything that drifts (deploy targets,
  live credentials, external service state) must be re-verified before you act on it – checkpoint
  the *verification method*, not just the conclusion.
- **Verification is not re-derivation.** Stop re-confirming facts you already established and stop
  re-reading a file just to admire an edit. But running the build, tests, or a targeted re-read to
  confirm a change actually landed – especially after a batched or mechanical edit – is a check,
  and a check that matters is never optional to save tokens.

## Applying this to a task

Before a non-trivial task, decide four things:

1. **Route** – is this mechanical (hand to a cheaper tier / subagent) or does it need judgment
   (keep at the strong tier)? Where might it flip mid-way?
2. **Batch** – which reads am I *certain* I need and can safely group now, and what should I gate
   on a probe first?
3. **Inline vs subagent** – would any piece flood my context with output I do not need to keep?
4. **Checkpoint** – will this task cross a boundary? If so, where do I write state (safely, no
   secrets)? If not, skip it.

Then work the plan, re-escalating the moment mechanical work surprises you.

## Anti-patterns this prevents

- Running the strongest model to reformat JSON, or dropping to the cheapest tier to apply a
  security fix.
- Ten sequential single-file reads that could have been one batched read – or a broad class-wide
  edit applied without checking its false positives first.
- Spawning a subagent to answer a question a single grep would settle – or grinding a huge search
  inline and flooding your own context with hits.
- Re-deriving project state from git history every session because nobody wrote it down – or
  writing scratch files for a task that ends in three steps.
- Skipping the post-edit build/test because "the answer was in hand."
- Checkpointing a database URL or API key into a file.
