# Strategist or FDE? Internal decision note (2026-10-15)
> Markdown copy of the substance of the local-only `role-choice.html` (the HTML fails the design gates; regenerate or restyle it before committing). Internal. Grades are manual, on the deployed anchors, plus or minus 0.03.

## Grades (see grades.json)
| | Fit, target-role-scan (of 81) | Winnability, bridge-scan (of 87) |
|---|---|---|
| Forward Deployed Engineer | 0.790 PURSUE | not scored: the bridge lens defers FDE titles, so odds are unmeasured |
| Deployment Strategist | 0.778 PURSUE | 0.701 PURSUE at the threshold, competition HIGH |

FDE wins on role shape (3 vs 2) and scope and authority (3 vs 2). Strategist wins on rare combination (3 vs 2) and regulated breadth (3 vs 2).

## What would actually disqualify
- FDE "5+ years building software or solving complex technical problems": SOFT, the JD wording allows it.
- FDE architecture and system design: PERFORMANCE GATE, decided in the technical interview. ARCS is solo, the repo is private; public build history at status.arcs.care; no on-call or scale record.
- FDE APIs, integrations, distributed systems: PARTIAL.
- Big-tech or Palantir pedigree: not in either JD; George said they are not set on it. Not a paper gate.
- Strategist requirements (deployment, ambiguity, stakeholders, APIs and MCP): met. Hands-on engineering is a nice-to-have.

## What George already said on the call (Granola 2026-10-13)
| Question | Answer | Status |
|---|---|---|
| Do Strategists write or ship code? | No: tech savvy but "not the actual doers, not the engineers"; they define and scope, manage stakeholders, work with FDEs; many come from consulting | ANSWERED |
| What does the FDE do? | "Super technical, very hands-on"; AI/ML or software backgrounds, or self-taught at a strong enough level; plus commercial skill | ANSWERED |
| Pre-sales? | Both do deployment and delivery; Strategist a bit more at the start | ANSWERED |
| Seats | About 10 FDEs, 5 to 6 Strategists | ANSWERED |
| Process | 5 stages, possibly under 2 weeks: talent call (Itay), technical interview, decomposition case study (prep-based role play), 2 more; George not privy to session content | PARTIAL |
| Strategist to FDE path? | Not discussed | OPEN |
| Does a live code walkthrough count? | Not discussed; he said he would look at the OpenTelemetry link | OPEN |

## Revised read
George's description settles the biggest question: the Strategist does not build. With the fit tie and no hard paper disqualifier, lead with FDE (Zach's first pick, conditional on meeting the engineering standard) and keep Strategist as the alternative. FDE's two real risks: the system-design bar in the technical interview, and unmeasured winnability. If getting onto the founding team at all outweighs what Zach wants to be doing, flip it: a values call, not a data one.

## Open
1. Ask George: is there a Strategist to FDE path, and what does the FDE technical interview cover, including whether a walkthrough of Zach's own system counts?
2. Rehearse 45 minutes: decompose an enterprise agent deployment out loud (see hyperstition-ledger.md). Log which half is energizing, build or discovery.
