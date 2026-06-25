# Toolbar comment pass — open items (2026-06-25)

> Source: Vercel Toolbar comments on PR #22 (`claude/sleepy-booth-889373`). 19 threads
> reviewed; 14 resolved (fixes shipped across `d2b4182`, `000b552`, `825e8d3`). These 5
> are genuinely open — either need Zach's call or are blocked on unbuilt infrastructure
> (the Profile Scan generation pipeline, ADR-028). Not bugs; don't resolve by guessing.

| # | Thread | What's open | Blocked on |
|---|--------|-------------|------------|
| 1 | [Wfcaehw-mbia](https://vercel.com/zachharris-3439s-projects/arcs-v9/c/Wfcaehw-mbia) | Pull non-obvious insights into the scan (e.g. "you're applying to PM roles but there are 10x more forward-deployed-PM/Applied-AI-engineer roles — that's your edge") | ADR-028 generation pipeline — can't fake this convincingly as static content |
| 2 | [y8wN7M9MaH_K](https://vercel.com/zachharris-3439s-projects/arcs-v9/c/y8wN7M9MaH_K) | Progressive disclosure (Simple→Rich→Deep) should actively "pull people in" at each fathom, like the Harry Wilson scan does | Same — audience-aware register + real per-tier insight density is a pipeline capability, not a depth-truncation prop |
| 3 | [4AGQVPr_92If](https://vercel.com/zachharris-3439s-projects/arcs-v9/c/4AGQVPr_92If) | Is `TwoColumn` really the best layout for the headline-vs-export comparison? | Needs a specific alternative from Zach — didn't want to swap for something equally arbitrary |
| 4 | [BuE6qSMbEuYE](https://vercel.com/zachharris-3439s-projects/arcs-v9/c/BuE6qSMbEuYE) | "Toast isn't working, competing CTAs" on `/dashboard` | Couldn't reproduce after the carousel removal (000b552) — asked Zach to recheck the live page; no toast component found in this flow |
| 5 | [WG5sdXx0B6XB](https://vercel.com/zachharris-3439s-projects/arcs-v9/c/WG5sdXx0B6XB) | "Add context" button font looked regressed/not-smaller on `/dashboard` | Source already has the correct 0.6875rem size — likely a stale-deploy render; asked Zach to recheck on the fresh deploy |

## Also flagged, not this branch's scope

Two more threads are real but live on `main`/production (not this PR):
- [fG8QC3j7dJC4](https://vercel.com/zachharris-3439s-projects/arcs-v9/c/fG8QC3j7dJC4) — one CTA above the fold > two, on the production homepage
- [JqKzfbYZdK1-](https://vercel.com/zachharris-3439s-projects/arcs-v9/c/JqKzfbYZdK1-) — flash of wrong receipt on initial load, production homepage

## Note on the "Vercel Preview Comments" CI check

This check counts unresolved Toolbar comments across the whole team's Vercel projects, not
scoped to this PR's branch/deployment — it picked up comments on `main` and even a different
project (`arcs-care`). No branch-protection rule on `main` requires it (confirmed via
`gh api repos/.../branches/main/protection` → 404, not protected), so it does **not** block
merging this PR. No scoping setting found in Vercel's docs or CLI; it'll stay red until every
unresolved comment everywhere is cleared, which isn't a realistic target for one PR.
