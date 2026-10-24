# The June 2026 port plan against arcs-v9 today (2026-10-17)

Source: "ARCS to Claude Code Port: S-Tier Migration Plan" (30 KB, dated 2026-06-11), a Perplexity-origin document in ~/Downloads. It was read in full and is NOT copied here: its reference list embeds signed download URLs with access-key IDs and security tokens (expired June 2026), so the file itself should not enter any repo. Compared with this repo's `.claude/` tree, hooks, root files and the operator registry on 2026-10-17. Advisory; every ruling is Zach's.

The plan: seven workstreams, build order WS1, WS7, WS5, then WS2, WS3, then WS4, WS6, with six quality gates. Its stated true north was to build the invariants layer first.

| Workstream | The plan asked for | arcs-v9 today | Reading |
|---|---|---|---|
| WS1 cold-start seed | root CLAUDE.md of at most 200 lines; full canon and invariants lazy-loaded from two rule files | root CLAUDE.md is 375 lines (40 KB) and imports AGENTS.md (30 KB) and WORLD.md (13 KB): about 83 KB always on. No rules directory. | NOT adopted. Quality gate 3 of the plan fails. |
| WS2 eight L0 primitive skills | one skill per primitive (derivatives, wave diffusion, phase cancellation, decelerator, kintsugi, nci grader) | none as skills. The primitives exist as Python (arcs_primitives, arcs_kinematics, arcs_kintsugi); an nci-scoring skill exists | Done in a different form. |
| WS3 ten operator agents and five advisor archetypes | 15 agent files | 8 agent files under new names: chief-bayesian, chief-conductor, chief-loki, idea-librarian, idea-detective, idea-alchemist, idea-curator, scenario-runner. Not present as agents: orchestrator, devils-advocate, folksonomy, immune-system, shavasana, and all five advisor archetypes. Those operators exist as Python (16, 24, 20, 18, 25) | Half ported, renamed, partly as agents and partly as code. |
| WS4 eight commands | stier, kairos-lock, question-compass, nci-audit, drift-check, receipt, recoil, init | drift-check exists by name; nci-commit and recoil-report cover nci-audit and recoil; question-compass is the product route; a global dewy-stub skill covers receipt. No stier, kairos-lock or init | Mostly covered by other names. Three absent. |
| WS5 receipt infrastructure | PostToolUse hook logging receipts to a repo folder | receipts are rows in the decision_receipt table; a PostToolUse hook exists on Write and Edit | Done, differently, and stronger (database, CHECK constraints). |
| WS6 MCP stack | Supabase, GitHub, Perplexity connectors | connectors are configured globally; there is no root .mcp.json (the operator bridge has its own) | Done at user level. |
| WS7 NOTOMATION layer | always-on invariants rule; a PreToolUse guard on canon files; a Stop hook for a session receipt | the invariants live in CLAUDE.md, WORLD.md and AGENTS.md. A global Stop hook exists (progressive handoff). No PreToolUse hook | Invariants present as prose, the canon write guard absent. |

## What the comparison says

- The plan is a design from June; arcs-v9 diverged on purpose in several places (database receipts, Python operators, a Next.js product). Divergence is not failure.
- **The biggest unadopted item is measurable: WS1.** The plan's rule is a root file of at most 200 lines with the rest lazy-loaded. Today about 83 KB is always on; the token-kaizen ledger's 2026-10-16 entry puts the docs floor near 19,000 tokens. That is the one lever in the plan with a number attached.
- **The one safety gap the plan named and the repo still lacks: a PreToolUse guard on canon writes.** Canon collisions are handled by written rules ("escalate, never resolve") but not by a hook.
- Advisory leaning, not a decision: COMPOST the L0 skills (WS2) and most missing agents (WS3), because the Python operators and the periodic table already cover them and a second copy would drift. PORT candidates are WS1 (lazy-load) and the PreToolUse canon guard.
- The five advisor archetypes (Executor, Orchestrator, Risk, Opportunist, Generalist) appear in no other place I checked. They may be worth a keep-or-kill call on their own.

## Not checked

The plan's failure modes FM-1 to FM-5 were not mapped to current gates. The plan's own NCI self-grade (94) was not re-scored. The earlier transcripts the plan cites (the long thread and the positioning thread) were searched for by their exact original file names in Downloads, A.R.C.S., Desktop and Documents and are not on this machine.
