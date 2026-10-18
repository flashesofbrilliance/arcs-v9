# Taxonomy for multi-threaded, interdependent work (proposal, 2026-10-17)

Status: PROPOSAL. Measured on the 33 `fc-*` backlog rows (23 leaf rows, 10 containers). Nothing here is wired into a tool. Facet homes below are existing ARCS stores; the point is to hang them on one coordinate system, not to add a thirteenth store.

## 1. Reuse first: what already exists
- Backlog rows: `_QUEUE/induced-backlog.jsonl` (states in `runtime/specs/backlog-status.json`).
- Decisions: `_DECISIONS/` (82 ADR files). Patterns: `_PATTERNS/` (62 files). Memory bank: 331 files under the project memory directory. Tools: `runtime/specs/tool-catalog.json` (269 tools).
- Lookup: `scripts/prior_art.py` (keyword scoring over memory, patterns, ADRs, rules, tools).
- Shape fit: `runtime/specs/shape-card.json`, a PROPOSAL from ADR-086 part D, not wired. Its altitude enum has 3 values (exec, operational, surgical) while the altitude ladder has 5; reconcile before wiring.
- Belief motion: `/thread-recoil` and `scripts/believability_ledger.py`. Altitude ladder: memory `altitude-ladder-friction-audit-method`. Composition ladder: `src/ui-kit/README.md`.

## 2. The coordinate system (every node has all three)
1. **Thread (lane):** a parallel stream of work that can progress on its own. For the Farcaster entry: node, signing, client, gate, proof, surface; cross-cutting: cost, security, design system, earned opinion.
2. **Altitude (why, five fathoms):** executive, strategic, operational, tactical, surgical. Goals cascade down through `serves`; state rolls up through containers.
3. **Form (what, how composed):** atom, molecule, organism, template, page. A node that can stand alone carries a `package` and an in/out `contract`, so it is self-sovereign yet composable.
Layers of stability: the **invariants** never move (I1 to I8 for this entry; I8 added 2026-10-17: an account or app key never travels in a command-line argument or a URL, and the local UI is authorized by a one-time fragment token, never the key); the **meso layer** is the operational bundles (the six templates) that get re-sequenced when the shape of the problem changes; everything below them is replaceable.

## 3. The twelve facets, in four families
Each facet is a node type hung on a coordinate. "Missing" says how absence is detected.

**A. Work**
| Facet | Is | Home today | Min fields | Missing when |
|---|---|---|---|---|
| Blocker | something outside the repo that must arrive | row `blockers` | kind, who, what, clears_when, hard | a BLOCKED row has none, or a hard blocker has no owner |
| Failure mode | how a row breaks | row `failure_modes` | mode, trigger, mitigation, fallback | a row has fewer than 2, or a mitigation has no row implementing it |
| Method | how the job is done | row `route.tool`, `gates`, `checks` | tool, gate, check ids | no `route.tool`, or a check with no pass line |

**B. Knowledge**
| Facet | Is | Home today | Min fields | Missing when |
|---|---|---|---|---|
| Blindspot | something we cannot see yet | none (gap) | statement, how it could be exposed, probe row | untested or stated-only evidence tags; rows with no read-source; requirements with two readings |
| Learning | a belief that moved, with its evidence | thread-recoil ledger, cold-molt brief | prior, posterior, evidence kind, source | a belief change with no cited external datum |
| Memory bank item | a durable fact for future sessions | memory directory + index | type, why, how to apply, links | a decision or learning exists only in chat or a handoff block |

**C. Design**
| Facet | Is | Home today | Min fields | Missing when |
|---|---|---|---|---|
| Architectural call | a decision with alternatives and consequences | ADR | context, options, decision, revisit trigger | a Zach decision is recorded only in prose |
| Architecture pattern | a reusable structure (event log with cursor, hooks as extension points, ports and adapters) | `_PATTERNS/` | name, forces, where applied | a design recurs and has no pattern file |
| System design | the whole picture of parts and flows | roadmap diagrams | components, flows, non-functionals, revisit triggers | no row links to it |
| Design pattern | a reusable interface or interaction shape (receipt chip, visible gate, BBS terminal) | ui-kit primitives, `_PATTERNS/` | name, states, a11y notes | a surface invents a shape the kit lacks |
| Design dependency | a row that needs a design element that does not exist yet | none (gap) | row, element, owning ds row | a UI row has no edge to a `ds-*` row |

**D. Fit**
| Facet | Is | Home today | Min fields | Missing when |
|---|---|---|---|---|
| Shape fit | how well a job's shape matches an existing tool, pattern or ADR | `prior_art.py`, shape-card PROPOSAL | job shape vector, chosen tool, best tool, score, reused flag | a row's chosen tool differs from the best match with no reason |

## 4. Typed edges (so the graph can be queried)
`serves` (goal tree), `contains` (build tree), `depends_on`, `blocks`, `derisks`, `mitigates` (method to failure mode), `exposes` (probe to blindspot), `decided_by` (call to ADR), `instantiates` (row to pattern), `learned_from` (learning to evidence), `remembered_as` (learning to memory file), `fits` (row to tool, pattern or ADR, with a score), `needs_design` (row to ds row).

## 5. Measured coverage on the 33 rows
| Facet | Measured | Reading |
|---|---|---|
| Blockers | 8 typed on 6 rows (7 hard) | typed and owned |
| Failure modes | 69 across 33 rows; 21 rows have 2 or more | strong; mitigations not yet linked to rows |
| Methods | `route.tool` on 33 of 33 rows; 76 checks | present; pass lines are prose |
| Dependencies | 27 `depends_on` edges between leaf rows, 10 `derisks` edges | present |
| Blindspots | no register; 3 rows rest on untested evidence; 12 rows have no read-source behind them | a gap (see section 6) |
| Learnings | 7 in the cold-molt brief; 0 linked to rows by an edge | present in prose only |
| Architectural calls | 0 ADRs mention Farcaster; 1 draft ADR in the roadmap; 4 decisions recorded in the brief | a gap |
| Architecture and design patterns | 0 rows link to a pattern | a gap |
| System design | 1 sketch (roadmap addendum), linked from no row | a gap |
| Design dependencies | 0 edges; the `ds-*` rows live only in a draft artifact, not in the queue | a gap |
| Memory bank | 2 existing memories mention Farcaster, both incidental | a gap before the two saved today |
| Shape fit | 23 leaf rows scored by `prior_art.py` | weak; see below |

## 6. Blindspots named now (not yet in the queue)
- **B1:** the plan assumes a fresh throwaway FID, but an existing memory says Zach already connected with someone on Farcaster, so he may hold an account. Using it would break "test accounts only"; creating a new one may duplicate cost. Ask. RESOLVED 2026-10-17: Zach confirmed in chat that FID 10351 (fname zachharris, custody 0x0b60...e139) is his. The entry still uses a throwaway account; 10351 stays his public identity.
- **B2:** the judging rubric is unknown ("sole discretion"); no one has read how earlier bounties were judged.
- **B3:** the competitive field is unscanned. The thread names at least one builder and a previous winner who forked a client; their quality sets the bar and nobody has looked.
- **B4:** Snapchain's README says the network is in its "migration phase", so node and engine versions may move during the week. Pin versions.
- **B5:** "include or exclude casts from any other client" has an assumed reading (filter by the signer's requesting app FID). The reading is unverified and could be asked of the poster.
- **B6:** the voucher's environment (OS, cloud, skill) is not modelled; the tutorial is tested only on ours.
Ways blindspots get exposed: a probe row, a pre-mortem, the claims-skeptic and `chief-loki` agents, evidence tags that are not "read", and shape-fit rows with no apt prior art.

## 7. Shape fit: what the measurement shows
`prior_art.py` ranks by keyword overlap. On the 23 leaf rows its top memory and pattern hits were mostly off-target (for example the budget-guard row matched a resins client note, and the gate row matched a git-worktree note). By my reading only a few top hits were apt (the publish-hygiene row matched `publish-requires-pii-gate-before-not-after`; the local-UI row matched `single-file-artifacts-inherit-tokens-never-copy`). That is a hand judgment, not a measured precision. The conclusion: text overlap cannot be trusted as a shape detector. A shape detector needs a structured vector (verb, altitude, form, thread, reversibility, human gate, external dependency, output kind) matched on tags, and it must be scored against a labelled set before anyone relies on it.

Seed labels for that set (apt fits by memory or ADR name, from the memory index and ADR headers; the files were not all opened in full):
- write-path probe: `verify-write-path-not-read-path-for-api-capability`, `client-fetch-failure-is-not-persistence-failure`
- gate falsifier set: `pre-register-rule-before-counting`, `inlier-run-the-falsifying-test-before-confident-claim`, `false-null-requires-provenance-exhaustion`
- receipts gate: ADR-044, `provenance-gate-every-metric-cites-evidence`
- budget guard: `cost-leaks-ruin-vector-no-silent-toggle-regression`, `arcs-v9-deploy-blast-radius-guardrails`
- publish hygiene: `publish-requires-pii-gate-before-not-after`, `static-public-files-worldreadable-client-gates-theater`
- voucher ask: `confirm-before-outbound-send-even-when-authorized`
- claims check: ADR-061, `fact-check-final-pass-vs-transcript`
- parent and child sessions: `puppet-master-fanout-worktree-isolated-jtbd`, `precompute-pregate-before-delegation`, `dont-trust-subagent-citation-without-checking`, `btw-gambit-multiwindow-fork-failure-modes`
- pre-mortem: `counterpart-vantage-premortem`
Proposed pre-registered metric: top-3 recall of the structured matcher on this labelled set must beat the keyword baseline; report n.

## 8. Architectural calls to mint (numbers from `python3 scripts/oracle.py next adr` at commit time; do not infer)
- AC1: CLI/TUI first on `hub-nodejs`; browser UI later over a loopback bridge.
- AC2: event core by cursor polling with at-least-once, idempotent handlers (alternative not yet weighed: gRPC event subscription, which the node also offers).
- AC3: receipts gate as the default pre-sign hook, user-tagged claims, no LLM extraction in v1, fails closed.
- AC4: four standalone packages (core, signer, gate, cli) in one workspace, each with an in/out contract.
- AC5: wallet signing by default, seed phrase secondary; scoped keys with a 7-day sliding TTL.
- AC6: clean-room public MIT repo; Snapchain stays a separate GPL-3 process.

## 9. Induced rows (drafts, not appended to the queue)
`wt-blindspot-register` (B1 to B6 as probe rows), `wt-design-dependency-edges` (link `fc-fe-local-ui` and the tutorial site to `ds-*` rows, and move the `ds-*` rows into the queue), `wt-mint-adrs` (AC1 to AC6), `wt-pattern-links` (link rows to patterns and write the missing pattern files), `wt-shape-fit-v2` (structured vector, labelled set, baseline), `wt-taxonomy-check` (a read-only checker that reports facet coverage and missing edges per row, like the backlog status check).
