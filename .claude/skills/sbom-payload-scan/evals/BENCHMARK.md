# sbom-payload-scan — iteration-1 benchmark (honest)

Run 2026-09-02. 3 eval prompts × {with-skill, baseline-no-skill}, 6 subagent runs. Fixtures:
`evals/fixtures/{evil,benign}`. Every agent was hard-constrained to static inspection (never install,
execute, or contact any host the target references) so nothing detonated the fixture's C2.

## Result

| Config | Assertions | Mean tokens | Mean time |
|--------|-----------|-------------|-----------|
| with-skill | 10/10 (100%) | 105,424 | 87.5s |
| baseline (no skill) | 10/10 (100%) | 100,569 | 90.9s |
| **delta** | **0** | **+4,855** | **−3.4s** |

## Honest read
On these small, blatant fixtures the skill shows **no pass-rate or cost advantage** — a capable model
catches the malware and answers the CI question with or without it. Reporting that straight matters
more than a flattering number. The skill's genuine value is not on the verdict axis these fixtures
test; it is:

1. **Determinism + CI exit code.** The scanner is a machine gate (reproducible, exit-code-driven),
   not a per-invocation model judgment. That is the difference between "an agent looked at it" and "a
   pipeline blocks the merge every time."
2. **Reuse, not reinvention.** In eval-2 the baseline agent *wrote its own ~60-line scanner from
   scratch* to answer the CI question. The skill exists precisely to stop that happening on every
   future invocation. This is the "repeated work across runs" signal, observed live.
3. **Scale.** Fixtures are 3 files; the advantage grows on real repos (thousands of files, one
   high-entropy payload line) where manual reading does not scale. This eval cannot show that.

## Earned improvement (applied)
eval-2 with-skill surfaced that a CI gate must fail on **any non-zero exit (1 or 2)**, not `exit == 2`
alone — a plain install hook is exit 1. Clarified in `SKILL.md`.

## Iteration-2 backlog (to actually discriminate skill value)
- Harder fixtures: a large repo with a single obfuscated payload line buried in thousands; a subtle
  legit-vs-malicious `postinstall` pair; a transitive-dependency plant.
- A qualitative axis for "did it reuse the tool vs. rebuild one" (the real eval-2 signal).
