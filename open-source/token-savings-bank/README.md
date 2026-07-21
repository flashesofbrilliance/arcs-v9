# token-savings-bank

A [Claude Code](https://claude.com/claude-code) skill that installs a budget-mode operating
discipline for coding agents: spend tokens deliberately instead of by reflex. Pick the right
model tier for the work in front of you, batch instead of drip, do small work inline instead of
spawning subagents, and checkpoint state to a file so nothing gets re-derived.

## Why it exists

Most token waste is not one big mistake – it is a hundred small ones: running the strongest model
to reformat a file, ten sequential reads that could have been one, a subagent spawned to answer a
question a single grep would have settled, and re-deriving project state from scratch at the start
of every session. None of these feel expensive individually. Together they are where the budget
goes.

This skill is a short, explicit checklist that turns those reflexes into deliberate choices. The
goal is not to do less work – it is to stop paying premium rates for cheap work and to stop paying
twice for work already done.

## Install

```bash
git clone https://github.com/flashesofbrilliance/token-savings-bank.git ~/.claude/skills/token-savings-bank
```

Or project-scoped:

```bash
git clone https://github.com/flashesofbrilliance/token-savings-bank.git .claude/skills/token-savings-bank
```

## How to use

Invoke it when a task is large, repetitive, or cost-sensitive, or the moment you notice yourself
burning tokens on low-value motion:

```
/token-savings-bank
```

It walks four levers – model-tier routing, batching, inline-over-subagent, and explicit
checkpointing – and a ten-second pre-task checklist to apply them. Then you work the plan.

## The four levers

- **Model-tier routing** – route mechanical work to a cheaper tier and escalate only on a real
  signal (ambiguity, a failure, cross-system reasoning, an irreversible call); re-escalate the
  moment mechanical work surprises you, and never de-escalate for security-sensitive edits.
  Actionable only where your setup lets you route work (e.g. dispatch a step to a lower-tier
  subagent); a single fixed-model session reads it as which steps to hand off vs. keep.
- **Batch instead of drip** – pay each round-trip's overhead once, but only for read-only or
  provably-disjoint work: read together what you're certain you need, fan out independent reads,
  and confirm a class-wide edit's match set before applying. On diagnostic tasks, gate on one
  probe before batching. Never parallelize writes to shared state.
- **Inline over subagent** – keep small, context-bound work inline; delegate when the work would
  otherwise flood your context with intermediate tool output you only need a conclusion from (a
  broad search is the classic case *for* delegating).
- **Explicit checkpoint** – when a task crosses a context/session boundary, write ground truth to
  a file and read it back instead of reconstructing it. Never checkpoint secrets (references, not
  values); re-verify anything that drifts. Verification after an edit is a check, not waste – never
  skip it to save tokens.

## Use cases

- **Large repetitive edits.** Applying a known change across many files is mechanical – run it on
  a cheap tier in batched passes instead of deliberating file by file on the strongest model.
- **Long multi-step tasks.** Checkpointing what is done and what is next keeps a long task from
  re-deriving its own state every few steps.
- **Cost-sensitive or metered sessions.** When spend matters, the pre-task checklist makes the
  expensive choices visible before you make them by accident.
- **Deciding when to delegate.** A quick test – would doing this inline flood your context with
  intermediate tool output you only need a conclusion from? If yes, delegate; a small briefing
  driving a broad search is the classic case for it.

## What it is not

It is guidance, not automation. It changes how an agent chooses among its existing tools; it does
not modify tools, settings, or model configuration. Correctness always comes first: budget mode
never means skipping a check that matters.

## License

MIT. See [LICENSE](./LICENSE).
