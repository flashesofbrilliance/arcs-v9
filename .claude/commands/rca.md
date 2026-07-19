# /rca

> On-demand root-cause analysis for a specific error. Invoke this ONLY when an error is worth the
> structured treatment — not for every error (a blanket RCA-per-error burns tokens; most errors are a
> one-line inline fix). Billing tier: SUBSCRIPTION (interactive).

Usage: `/rca <paste the error, or point at the failing command/build/test>`

## The triage gate (decide BEFORE diagnosing)

Judge the **reading-to-answer ratio**:
- **Low** (you can likely root-cause in a handful of tool calls — a known signature, a config/env issue, a
  single obvious file) → **diagnose inline.** Do NOT spawn a subagent; the overhead would exceed the work.
- **High** (diagnosis needs reading a lot of code, or several independent hypotheses can be checked in
  parallel) → **spawn a subagent** (or several) to investigate in isolated context and report back only the
  conclusion. The messy read stays out of the main session — that is the token win.

State which tier you picked and why, in one line, before proceeding.

## Steps

1. **Reproduce first.** Get the *actual* error, not the reported one — run the failing command/build/test
   and capture the real output. If it doesn't reproduce, say so and stop (you're chasing a ghost).
2. **Separate symptom from cause.** The stack-trace location is usually the symptom. Ask: *what makes this
   fire?* Check the layers most people skip — **environment and config** (env vars like `NODE_ENV`, build
   flags, versions, duplicate deps), not just application code. (Real example: a `/_global-error`
   `useContext`-null build crash was `NODE_ENV=development` in the shell, not a code bug.)
3. **Establish pre-existing vs introduced.** Does it fail on a clean tree / before the suspected change?
   Report this honestly — "pre-existing and unrelated" is a valid, important finding.
4. **Fix minimally.** Smallest change that addresses the *cause*. Don't bundle unrelated cleanup; if you add
   a "while I'm here" improvement, name it separately from the fix.
5. **Verify by driving the failure path** — reproduce the original trigger and confirm it's gone. Not "it
   compiles" — actually exercise the thing that broke. (Consider the `verify` skill for runtime surfaces.)
6. **Capture the root cause as a durable gotcha** — THE compounding step. Add a one-liner to
   `AGENTS.md` → Gotchas (if it's a repo-wide trap people will re-hit) or `_PATTERNS/durable-gotchas.md`
   (deeper/on-demand). This is what stops the same error from ever being re-diagnosed.
7. **Optional — ADR** if the cause is systemic/architectural (a recurring class, a design decision, a
   cross-repo issue). Write it to `_DECISIONS/` and register it in `index.json`.
8. **Commit** with `/nci-commit` (score it — an error fix changes runtime behavior, so not SKIP unless it's
   docs-only). Push only if asked.

## Output

- Tier chosen (inline vs subagent) + one-line why.
- Symptom → root cause (the actual mechanism, not the trace location).
- Pre-existing vs introduced.
- The fix (+ any bonus, named separately).
- Verification: what failure path you drove, and that it's resolved.
- The gotcha you captured (file + line), and whether an ADR was warranted.

## Anti-patterns (do NOT)

- Spawn a subagent for a 5-tool-call fix "to be thorough" — that's the token waste this command exists to avoid.
- Claim "fixed" from a green compile without driving the actual failure.
- Fix the symptom (silence the error) instead of the cause.
- Skip step 6 — an RCA without a captured gotcha is a fix you'll pay for again.
