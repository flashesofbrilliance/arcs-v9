# rca – a root-cause-analysis skill for Claude Code

A small [Claude Code](https://claude.com/claude-code) skill that turns "something broke" into a
disciplined root-cause analysis: triage the effort, reproduce the *real* error, separate symptom
from cause, fix minimally, verify by driving the failure path, and capture the root cause so nobody
re-diagnoses it next month.

It encodes one opinion most debugging advice skips: **decide how much to spend before you start.**
Not every error deserves a full investigation – the skill's first move is a triage gate that routes
a five-minute fix inline and reserves subagent fan-out for the cases that actually need it.

## Why this exists

Most errors get fixed at the symptom (silence the stack trace) rather than the cause, and the fix
gets no durable record – so the same bug gets re-diagnosed from scratch the next time it fires. This
skill makes the cause-not-symptom discipline and the capture-the-gotcha step non-optional, and adds
a triage gate so the process itself does not become the waste.

## Install

Copy the `rca/` directory into your skills location:

```bash
# project-scoped
cp -r rca .claude/skills/rca

# or user-scoped (all projects)
cp -r rca ~/.claude/skills/rca
```

Then invoke it in a Claude Code session:

```
/rca <paste the error, or point at the failing command / build / test>
```

## What it does

1. **Triage gate** – inline fix vs. subagent investigation, decided by reading-to-answer ratio.
2. **Reproduce** the actual error before theorizing.
3. **Symptom vs. cause** – check environment/config, not just application code.
4. **Pre-existing vs. introduced** – reported honestly.
5. **Minimal fix**, with any bonus change named separately.
6. **Verify** by driving the failure path – not "it compiles."
7. **Capture** the root cause as a durable note so it is never re-diagnosed.

See [`SKILL.md`](./SKILL.md) for the full instructions.

## License

MIT – see [LICENSE](./LICENSE).
