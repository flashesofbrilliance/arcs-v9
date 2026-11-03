---
paths:
  - "src/**"
  - "scripts/**"
  - "operators/**"
  - "tests/**"
  - "prisma/**"
  - ".claude/hooks/**"
  - ".claude/agents/**"
  - ".claude/skills/**"
  - ".github/**"
---

# Coding discipline (Karpathy guidelines, adapted; Zach 2026-11-03)

Loads when you read, write or edit code. Source: the `agent-protocols:karpathy-guidelines` skill, kept here so every harness
(Claude Code, Hermes) gets it from the repo. Bias is caution over speed; for a trivial change, use judgment.

## 1. Grug first, then think before coding

- Pre-frame before any investment: is this the right first input, given the binding constraint right now? Argue the other side at
  full strength in a line or two, then proceed, redirect or ask (memory `preframe-challenge-the-input-before-investing`).
- Ask whether the thing needs to exist at all. For a new tool, gate, script or process, run the `grug` agent first.
- State assumptions out loud. If a request has two readings, name both; don't pick one silently. If something is unclear, stop and ask.
- If a simpler approach exists, say so and push back.

## 2. Simplicity first

- The least code that solves the asked problem. No features, options or abstractions nobody asked for; no error handling for cases
  that cannot happen.
- If 200 lines could be 50, rewrite it. Test: would a senior engineer call it overcomplicated?
- One sanctioned addition: the Frustration Gate (AGENTS.md gotcha 15). A recurring bug class gets its cheapest failing check in the
  same change; that check is part of the ask, not scope creep.

## 3. Surgical changes

- Touch only what the task needs. Don't reformat, rename or "improve" nearby code. Match the existing style.
- Remove only the orphans your change made. Name other dead code; don't delete it (memory `fix-defect-in-place-dont-delete`).
- Every changed line traces to the request. A file another session owns is theirs (gotcha 22).

## 4. Goal-driven execution

- Turn the task into a check before writing code: a bug gets a failing test or reproduction first, then the fix; a refactor keeps the
  tests green before and after.
- For more than one step, write the plan as `step -> verify: check`.
- Done means verified by the repo's own gates (`npm run build`, `npm test`, the pre-commit hooks), not "looks right". When a test or
  gate turns out to be wrong, fix it in the open and log the seam (memory `kintsugi-seam-when-the-test-was-wrong`).
