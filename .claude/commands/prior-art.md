---
description: Pre-plan lookup. Rank existing memories, patterns, ADRs and tools against a job before planning it
---

# /prior-art — read what we already learned before planning

> The retrieval half of "capture what you learned." Lessons get written to memory,
> `_PATTERNS/` and `_DECISIONS/`; this makes sure the next plan reads them first.

1. Run `python3 scripts/prior_art.py "$ARGUMENTS"` from your own worktree (AGENTS.md gotcha 14).
   If no job was given, ask one question: "What's the job?"
   The first section, `## tool assembly (jtbd graph)`, is the graph's answer to "which tool for
   this job" (best tool, open blockers, what it needs, last receipts; under 1,000 tokens). Its
   first line says whether the graph answered or the keyword `## tool` section is the fallback;
   say which in the plan. The memory, pattern, ADR and rules ranking below it is unchanged.
2. Open only the top hits that plausibly apply (usually 1 to 3). Do not read every hit.
3. Start the plan with a **Prior art** line: each hit you used and what it changes about the
   plan, or `Prior art: none applied` if nothing fit. A matching tool wins over building one
   (memory `jtbd-reuse-existing-tool-before-inventing`).

Read-only and keyword-ranked: a miss does not prove no prior art exists. If the plan later
hits a lesson the lookup missed, note it so its description can be sharpened.
