# ADR-090: The public RFP engine repo's main is the clean work sample only

> **Status:** PROPOSED (2026-10-31). Not decided. Zach accepts or rejects; nothing here is wired.
> **Date:** 2026-10-31
> **Author:** Claude Opus 5.5 (decision-record reconciliation sweep, 2026-10-14 to 2026-10-31)
> **Oracle:** number allocated via `python3 scripts/oracle.py next adr` (90); `_SEEDS/_oracle.json` committed with this file.
> **Cross-repo note:** tracked here like ADR-010; the change executes in the ret-rfp-intelligence repo, not in arcs-v9.

## D: The decision

**Sharp question:** When the RFP engine goes public, which history and which code does the public repo's main carry?

**Decision (as recorded by Zach in his Project receipts, 2026-10-31; not read from a primary source by this session):**
- The public repo's main is the content of the ret-rfp-intelligence branch `claude/dioptra-work-sample-clean` only.
- The agentalent runner stays private for now. It lives on `claude/agentalent-public`, which is not the public main.
- The walkthrough video is held. It does not ship with the first public main.

## E: Entity / system

- ret-rfp-intelligence (private on GitHub, checked 2026-10-31 with `gh repo view`: PRIVATE, default branch main).
- Branch heads, copied from `git rev-parse` in the ret-rfp-intelligence clone on 2026-10-31:
  - ret-rfp-intelligence `claude/dioptra-work-sample-clean` at 0e0e25fd6c89, root commit 87865b27b, 49 tracked files, 0 paths matching "agentalent".
  - ret-rfp-intelligence `claude/agentalent-public` at cf2001be2660, same root 87865b27b, carries the agentalent runner and its test.
  - ret-rfp-intelligence `claude/dioptra-work-sample` at d12a3590ade5, root 90402118f, which is full RET history.
- Newest commit on the clean branch: ret-rfp-intelligence 0e0e25f, 2026-10-31 05:38, "docs(sample): README states the real-model run (11/12/1, target missed; 14/24 by hand)".
- The arcs-v9 landing page for the engine shipped in PR #1876 (merged 2026-10-31T20:02:51Z as d63f992a0d04).

## W: Window

**Horizon:** QUARTER
**Revisit trigger:** Zach decides the agentalent runner is ready to publish; the walkthrough video is cut and approved; or a leak check on the clean branch fails.

## Context

Two candidate branches share a fresh root, so neither drags RET history. The backlog row `rfp-ship-public-leak-gate` (landing in open PR #1893) records the corrected check: both `claude/agentalent-public` and `claude/dioptra-work-sample-clean` share root 87865b27b and pass, while `claude/dioptra-work-sample` and `claude/claude-mcp-agent-81c7a6` carry full RET history and must never be the public main. The open question was scope, not history: ship the runner too, or the work sample alone.

## Options considered

### Option A: clean work sample only (chosen)
- Smallest public surface; one claim to defend (the README's measured run).
- Runner and video can follow as additive pushes without rewriting public history.
- Cost: the public repo shows the result, not the agent that produced it.

### Option B: agentalent-public as main
- Shows the runner. Same clean root.
- Cost: more code under public scrutiny before Zach has chosen to stand behind it; harder to pull back once public.

### Option C: wait and ship everything together
- One launch.
- Cost: holds the work sample hostage to the slowest piece (the video).

## Decision

**Chosen:** Option A.
**Rationale:** publishing is one-way; start with the smallest artifact whose claims are already measured and stated in its README, and add the rest later.
**Trade-offs accepted:** a thinner first impression; the runner's value is told, not shown, until it is published.

## Y: Conviction

**Polarity:** YELLOW
**Conviction:** MEDIUM
**Stability:** PROVISIONAL (the "for now" and "held" parts are explicit)

**Loki test:** the README's own run missed its target (11/12/1, "target missed"). A public repo whose headline result is a miss, with the runner hidden, may read as a demo with nothing behind it.

## Consequences

- Whoever creates the public repo pushes only the clean branch's tree as main. Any other branch is a separate, later decision.
- The leak gate row stays the guard on what may become public main.

**Implementation pointer:** ret-rfp-intelligence `claude/dioptra-work-sample-clean`; arcs-v9 PR #1893 (backlog rows); arcs-v9 PR #1876 (landing page).

## Linked receipts / ADRs

- ADR-036: split the repo, public app and private sensitive (relates to: same public and private boundary, other repo).
- ADR-084: reliance, not trust, on public surfaces (relates to).
