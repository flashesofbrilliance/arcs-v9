# The one dated receipt — search run and result
Run: 2026-08-28, session claude/happy-cori-d4faaf. Prescribed by war-game panel wf_3ac81615-7e1.

## Question
Does any commit message, ADR, session note, DEWY receipt, or handoff **dated before a feature
landed** cite a vision film? One hit upgrades candidate-hyperstition to demonstrated causation.

## Method (exact, reproducible)
- `git log --all --grep=<term> -i` for each of: NotebookLM, vision film, explainer, First Wave,
  Phase Locked / Phase-Locked, Bicycle for the Mind, Force Multiplier, For All Brains,
  OS for Clarity, Decision Physics, hyperstition.
- `grep -rniE` for the same terms over `_DECISIONS/ _STATE/ _ARCHIVE/ _SEEDS/ _PATTERNS/
  MEMORY.md SKILL.md` (excluding the atlas family itself and gauntlet-runs.jsonl).

## Result: NULL — zero qualifying hits.
- Every commit citing a film title or "NotebookLM"/"vision film" is dated **2026-08-28**, the
  atlas session itself (8edc0a5a, 42fc6da4, 3ce06ec9) or later.
- The one earlier "explainer" hit (d833187f, 2026-08-05) is the unrelated Yuri meta-cognitive
  explainer, not a vision film.
- "hyperstition" appears earlier (2026-07-02 Kelly SIGNAL, 2026-07-23 Yuri champion-kit) as the
  concept applied to *other* subjects — none cite a film or precede a film-named feature.
- Repo-text grep: only the ADR-033 "force multiplier" idiom (generic phrase, not the film).

## Verdict
No dated evidence exists that any film was consulted mid-build. The causal arrow
(film → feature) is now **searched-and-not-found**, not merely unproven. The common-cause null
(corpus → films, corpus → product, independently) stands as the best-supported reading. The
family's honest claim remains the naming lag: the corpus described itself twice, eight months
apart, and the second description ran.
