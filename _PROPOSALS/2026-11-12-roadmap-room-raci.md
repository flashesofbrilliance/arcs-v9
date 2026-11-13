# Roadmap room: staff of chiefs, advisor council and RACI (proposal)

Status: PROPOSAL, 2026-11-12 ~22:45 EST, for Zach to rule (R-035). Nothing here runs until ruled.
Scope: the Reading Room's sixth room ("what's next and what's blocked?", `scripts/roadmap_render.py`) and the work it surfaces.
Run model: `/agent-army:agent-army` for fan-out, inside `/ai-native-os:agentic-build-loop` (spec and acceptance tests first, the agent fills logic, a green suite gates the merge).

## Constitutional rule (NOTOMATION)

Zach is **Accountable** for every fate: priority, keep or kill, merge, anything that crosses a one-way door. No chief or council seat may change a ledger row, merge, or publish. Agents propose; the existing gates (backlog_append.py, universe_jtbd_adapter.py --check, page_gate.py, pre-commit hooks) decide what is valid; Zach decides what happens.

## Staff of chiefs (Layer 1 of agent-army)

Each chief is an existing agent type in this environment. Model tier follows agent-army's power level, chosen by Zach at the pre-deploy gate.

| Chief | Job (one line) | Agent type | Writes to |
|---|---|---|---|
| Chief of Staff | Runs the sweep, keeps counts honest, assembles the daily brief | general-purpose | the render only |
| Chief Cartographer | Turns unsequenced items into proposed backlog rows with edges | agent-protocols:spec-analyst | proposals via backlog_append.py, never direct |
| Chief Risk Officer | Prices risk, maintains the funhouse register rules | ai-native-os:devils-advocate (+ risk_underwriter.py) | _PROPOSALS |
| Chief Design Officer | Holds DESIGN.md, impeccable and page_gate on every render | agent-protocols:accessibility-specialist | review notes |
| Chief Engineer | Owns roadmap_render.py, its tests and the HUD seam | agent-protocols:test-engineer + code-reviewer | draft PRs |
| Chief Release Officer | Branches, draft PRs, merge-train readiness, no push to main | agent-protocols:release-engineer | draft PRs |
| Chief Taxonomist | Proposes where folksonomy tags sit in the fathom tree (ADR-058) | idea-librarian (repo agent) | _PROPOSALS |

## Advisor council (review only, never writes)

| Seat | Lens | Agent type |
|---|---|---|
| HEAD | logic, coherence, claim versus source | ai-native-os:safety-judge |
| HEART | focus and wellbeing, income-first priority | ai-native-os:customer-proxy (playing Zach) |
| WALLET | cost versus value; does this displace paid work | ai-native-os:data-flywheel-architect |
| Skeptical evaluator | would a hiring manager trust this | ai-native-os:customer-proxy (hiring manager) |
| Security | connector and data exposure on any page | agent-protocols:security-auditor |

## RACI by workstream

R = responsible, A = accountable, C = consulted, I = informed.

| Workstream | Zach | Chief of Staff | Cartographer | Risk | Design | Engineer | Release | Taxonomist | Council |
|---|---|---|---|---|---|---|---|---|---|
| Sweep all ledgers | A | R | C | I | I | C | I | I | I |
| Sequence: rows and edges for unsequenced items | A | C | R | C | I | I | I | C | C |
| Priority P0 to P4 (fates) | A, R | C | C | C | I | I | I | I | C |
| Risk register (funhouse) | A | C | C | R | I | I | I | I | C |
| Gauntlet (steelman, strawman, personas) | A | C | I | R | C | C | I | I | R |
| Render to DESIGN.md / Field OS | A | I | I | I | R | R | I | I | C |
| HUD seam (route from a job id) | A | I | I | C | C | R | I | I | I |
| Taxonomy placement (fathom tree) | A | I | C | I | I | I | I | R | C |
| Branch, draft PR, merge readiness | A (merge) | I | I | I | I | C | R | I | I |

## Build loop (per change)

1. Spec: one paragraph plus acceptance tests (for example `python3 scripts/roadmap_render.py --self-test`, a count reconciliation test, `python3 scripts/page_gate.py _ARTIFACTS/atlas/roadmap.html`).
2. The chief responsible fills the logic on a branch; the council reviews the diff.
3. Gates run (pre-commit, page_gate, adapter check). Green or it does not ship.
4. Draft PR; Zach rules; a receipt records the decision.

## Open questions for Zach

1. Power level for agent-army (Max Power / Heavy / Balanced / Economy)?
2. Which chief is first? Suggested: Cartographer, because 287 open items cannot be sequenced until they have rows and edges.
3. Does the Taxonomist wait for the Babelfish triage (PARKED #21), or start now on the fathom tree only?
