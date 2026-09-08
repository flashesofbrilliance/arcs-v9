# The Frustration Gate — turn painful bugs into cheap mechanical checks

> Version: 1.0 · 2026-09-08
> "The more painful the learning, the more profound the solution feels once it addresses the root
> cause." A bug that cost real time/effort/frustration is not paid off by fixing the instance. It is
> paid off by a **gate**: the cheapest mechanical check that fails the build on that whole class, so
> the cycle can never spin again. Guidance is ignorable. A gate is not.

## The rule (default, not a favor)

When a bug class is **recurring OR high-frustration** (it burned a session, it shipped more than once,
the user had to flag it more than once), you do not just fix it. In the same change you:

1. **Write the cheapest check that FAILS on the class** (not the one instance). Match cost to the bug:
   - `grep` / regex over source → catch a literal pattern (em-dash, a banned token, a `max-width:NNch`).
   - static lint (stdlib script) → catch a structural relationship (`artifact_wrap_lint.py` MODE 5:
     narrow prose inside a wide container).
   - headless assertion (Playwright/JS) → catch a *rendered* property a static scan can't see
     (a lede pinched to <85% of its lane — invisible to overflow checks because narrow never overflows).
2. **Prove the gate both ways before trusting it:** it FAILS on a sabotaged-bad copy and PASSES on the
   fixed one. A gate you haven't seen fail is not a gate.
3. **Wire it into the always-run path:** `npm test` / pre-commit hook / the repo's own suite — never a
   one-off you have to remember to run. Parameterize it so it covers new files, not just today's.
4. **Verify the instrument is real.** A green gate proves nothing if it's the wrong gate: the stale
   copy, the wrong file, the property you're not actually measuring. Run tools from your worktree, not
   a main-checkout absolute path that drifts to another session's branch (see AGENTS.md gotcha #14).

## The tell that you owe a gate

A symptom that **survives multiple green-gated "fixes"** is the loudest possible signal that the gate
has a blind spot or you're solving the wrong problem. That realization should fire on round 2, not
round 15. When it fires: stop patching, reproduce the user's EXACT condition, grep memory for a
standing preference on that surface, and write the failing case as a test *before* the next fix.

## Anti-laziness clauses (what turns a 1-round fix into a 15-round spin)

- Do not re-assert a convenient diagnosis ("it's your cache") on a repeated complaint — especially
  against contrary evidence the user already gave (they said *incognito*). Reproduce, then speak.
- "Too narrow / too quiet / didn't fire" failures are invisible to overflow/error gates. If a class
  can fail silently, the gate must assert the POSITIVE property (width ≥ X, event fired, row written),
  not just the absence of an error.
- Cheap to add, ruinous to skip. The gate is almost always minutes; the spin is hours and trust.

## Worked example (the pain this pattern is made of)

`zachharris.xyz/scan`, 2026-09-08. A hero lede kept "wrapping too narrow." It took ~15 rounds because:
(a) I ran a **stale** `artifact_wrap_lint.py` (main-checkout copy, no MODE 5) → every "clean" was a
false pass; (b) I verified overflow, but "too narrow" never overflows → the gate was blind; (c) two
doctrines conflicted (narrow shared `--measure` vs `design-full-width-lede-matches-heading`) and I kept
applying the wrong one. The payoff gate: `test/scan-regression-test.mjs` now asserts at 1280px that the
lede spans ≥85% of its lane — proven to FAIL on a 640/1012 lede and PASS on the full-lane fix, wired
into `npm test`. That class cannot ship silently again.

## Related
- Enforcement: AGENTS.md gotchas #13 (artifact CSS measure/lede) and #14 (worktree vs stale checkout).
- Canon CSS: `_PATTERNS/arcs-artifact-css-base.css`.
- Memories: `run-the-repos-own-gates-before-shipping`, `run-repo-tools-from-worktree-not-stale-main-checkout`,
  `design-full-width-lede-matches-heading`, `mechanized-frontend-gate-is-tripwire-not-verdict`.
